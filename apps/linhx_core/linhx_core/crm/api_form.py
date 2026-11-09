"""API nhận form liên hệ (C2) và kết quả T1 Khám (D2) từ Trang BU (allow_guest=True, giới hạn tần suất qua rate_limit)."""
from __future__ import annotations

from contextlib import ExitStack, contextmanager
import ipaddress
import json
import logging
from pathlib import Path
import threading
import time

import frappe
from frappe.rate_limiter import rate_limit

from linhx_core import co_module
from linhx_core.crm import dong_y, form, gop_trung, t1, xac_minh_marketing

logger = logging.getLogger(__name__)

GIOI_HAN_MOI_PHUT = 10
GIOI_HAN_THEO_KHOA_MOI_PHUT = 5
CUA_SO_GIAY = 60
CUA_SO_PHAT_OTP_GIAY = 3600
GIOI_HAN_BODY_BYTES = 16 * 1024
GIOI_HAN_TRUY_VAN_NGUOI = 20
TOI_DA_KHOA_BO_NHO = 1000
TRUONG_LIEN_HE_FORM = ("ho_ten", "dien_thoai", "email")
TRUONG_NGUOI_T1 = (
    "ho_ten",
    "dien_thoai",
    "email",
    "zalo",
    "nguon",
    "tang_pheu",
    "t1_tong",
    "t1_muc",
    "lich_su_t1",
)
TRUONG_CAM_TU_CLIENT = ("nguon", "tang_pheu", "bang_muc", "cau", "phuong_thuc")
LOI_XAC_MINH_CHUNG = "xac_minh_that_bai"

_BO_DEM_KHOA_DU_PHONG: dict[str, list[float]] = {}
_LICH_SU_PHAT_OTP_THEO_KENH: dict[str, list[str]] = {}
_KHOA_BO_NHO_GUARD = threading.Lock()
_KHOA_BO_NHO_THEO_LIEN_HE: dict[str, threading.Lock] = {}
_CACHE_KHAM_JSON: dict | None = None


def _che_kenh(gia_tri: object) -> str:
    """Che thông tin nhạy cảm (email dạng `a***@domain`, SĐT/khoá dạng `xx***yy`) trước khi ghi log."""
    chu = str(gia_tri or "").strip()
    if not chu:
        return "***"
    if "@" in chu:
        phan_truoc, phan_sau = chu.split("@", 1)
        tien_to = ""
        if ":" in phan_truoc:
            goc, local = phan_truoc.rsplit(":", 1)
            tien_to = f"{goc}:"
        else:
            local = phan_truoc
        ky_tu_dau = local[0] if local else ""
        return f"{tien_to}{ky_tu_dau}***@{phan_sau}"
    if len(chu) <= 4:
        return "***"
    return f"{chu[:2]}***{chu[-2:]}"


def _la_dong_y_true(gia_tri: object) -> bool:
    return form._la_dong_y_true(gia_tri)


def _tra_loi_http(thong_diep: str, ma_http: int, loai_loi=None) -> None:
    if hasattr(frappe, "local") and isinstance(getattr(frappe.local, "response", None), dict):
        frappe.local.response["http_status_code"] = ma_http
    exc_cls = loai_loi or getattr(frappe, "ValidationError", ValueError)
    frappe.throw(thong_diep, exc_cls)


def _lay_cache():
    cache_fn = getattr(frappe, "cache", None)
    if callable(cache_fn):
        try:
            return cache_fn()
        except Exception as exc:
            logger.warning("Không kết nối được frappe.cache(): %s", type(exc).__name__)
            return None
    return None


def _la_ip_proxy_tin_cay(ip_str: str) -> bool:
    ds_tin_cay = getattr(getattr(frappe, "conf", None), "get", lambda *_: None)("trusted_proxies")
    if isinstance(ds_tin_cay, (list, tuple, set)) and ip_str in ds_tin_cay:
        return True
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        return bool(ip_obj.is_loopback or ip_obj.is_private)
    except ValueError:
        return False


def _lay_ip_khach() -> str:
    local_obj = getattr(frappe, "local", None)
    ip_ket_noi = str(getattr(local_obj, "request_ip", None) or "127.0.0.1").strip()
    req = getattr(local_obj, "request", None) or getattr(frappe, "request", None)
    headers = getattr(req, "headers", None) if req else None
    if headers and _la_ip_proxy_tin_cay(ip_ket_noi):
        xff = str(headers.get("X-Forwarded-For") or "").strip()
        if xff:
            cac_ip = [phan.strip() for phan in xff.split(",") if phan.strip()]
            for ung_vien in reversed(cac_ip):
                try:
                    ipaddress.ip_address(ung_vien)
                except ValueError:
                    continue
                if not _la_ip_proxy_tin_cay(ung_vien) or ung_vien == cac_ip[0]:
                    return ung_vien
        x_real = str(headers.get("X-Real-IP") or "").strip()
        if x_real:
            try:
                ipaddress.ip_address(x_real)
                return x_real
            except ValueError:
                pass
    return ip_ket_noi or "127.0.0.1"


def _trich_du_lieu_request(kwargs: dict) -> dict:
    du_lieu: dict = {}
    local_obj = getattr(frappe, "local", None)
    req = getattr(local_obj, "request", None)
    if req is not None:
        content_length = getattr(req, "content_length", None)
        if isinstance(content_length, int) and content_length > GIOI_HAN_BODY_BYTES:
            raise ValueError("Kích thước dữ liệu gửi lên vượt quá giới hạn cho phép")
        if hasattr(req, "get_data"):
            try:
                raw_bytes = req.get_data(cache=True, as_text=False)
                if isinstance(raw_bytes, (bytes, bytearray)) and len(raw_bytes) > GIOI_HAN_BODY_BYTES:
                    raise ValueError("Kích thước dữ liệu gửi lên vượt quá giới hạn cho phép")
            except ValueError:
                raise
            except Exception as exc:
                logger.warning("Lỗi đọc raw request body: %s", type(exc).__name__)
        if hasattr(req, "get_json"):
            try:
                body_json = req.get_json(silent=True)
                if isinstance(body_json, dict):
                    du_lieu.update(body_json)
            except Exception as exc:
                logger.warning("Lỗi phân tích JSON request body: %s", type(exc).__name__)

    form_dict = getattr(local_obj, "form_dict", None)
    if isinstance(form_dict, dict):
        for k, v in form_dict.items():
            if k not in ("cmd", "data") and k not in du_lieu:
                du_lieu[k] = v
        if isinstance(form_dict.get("data"), str):
            raw_data_str = form_dict["data"]
            if len(raw_data_str.encode("utf-8", errors="ignore")) > GIOI_HAN_BODY_BYTES:
                raise ValueError("Kích thước dữ liệu gửi lên vượt quá giới hạn cho phép")
            try:
                parsed = json.loads(raw_data_str)
                if isinstance(parsed, dict):
                    for k, v in parsed.items():
                        du_lieu.setdefault(k, v)
            except Exception as exc:
                logger.warning("Lỗi phân tích form_dict['data']: %s", type(exc).__name__)

    for k, v in (kwargs or {}).items():
        if v is not None or k not in du_lieu:
            du_lieu[k] = v
    if isinstance(du_lieu.get("du_lieu"), dict):
        goc = dict(du_lieu["du_lieu"])
        goc.update({k: v for k, v in du_lieu.items() if k != "du_lieu"})
        du_lieu = goc

    for tr_cam in TRUONG_CAM_TU_CLIENT:
        du_lieu.pop(tr_cam, None)
    return du_lieu


def _kiem_module_crm_bat() -> None:
    cau_hinh = co_module._doc_cau_hinh_frappe()
    if co_module.doctype_bi_an("LX Nguoi", cau_hinh):
        _tra_loi_http("Module CRM đang tắt", 403, getattr(frappe, "PermissionError", PermissionError))


def _dem_trong_bo_nho(khoa: str, bay_gio_ts: float, gioi_han: int = GIOI_HAN_THEO_KHOA_MOI_PHUT) -> bool:
    """Bộ đếm dự phòng trong bộ nhớ có dọn TTL và giới hạn kích thước khi Redis cache lỗi."""
    with _KHOA_BO_NHO_GUARD:
        khoa_het_han = [
            k
            for k, ds in _BO_DEM_KHOA_DU_PHONG.items()
            if not ds or all(bay_gio_ts - ts >= CUA_SO_GIAY for ts in ds)
        ]
        for k in khoa_het_han:
            _BO_DEM_KHOA_DU_PHONG.pop(k, None)

        ds_ts = [x for x in _BO_DEM_KHOA_DU_PHONG.get(khoa, []) if bay_gio_ts - x < CUA_SO_GIAY]
        if len(ds_ts) >= gioi_han:
            _BO_DEM_KHOA_DU_PHONG[khoa] = ds_ts
            return True

        if khoa not in _BO_DEM_KHOA_DU_PHONG and len(_BO_DEM_KHOA_DU_PHONG) >= TOI_DA_KHOA_BO_NHO:
            khoa_cu_nhat = min(
                _BO_DEM_KHOA_DU_PHONG,
                key=lambda k: max(_BO_DEM_KHOA_DU_PHONG[k]) if _BO_DEM_KHOA_DU_PHONG[k] else 0.0,
            )
            _BO_DEM_KHOA_DU_PHONG.pop(khoa_cu_nhat, None)

        ds_ts.append(bay_gio_ts)
        _BO_DEM_KHOA_DU_PHONG[khoa] = ds_ts
        return False


def _kiem_gioi_han_theo_khoa(
    em_chuan: str = "",
    zl_chuan: str = "",
    dt_chuan: str = "",
    *,
    tien_to: str = "linhx_form_rl",
) -> None:
    """Giới hạn tần suất theo IP khách và từng khoá liên hệ (email/Zalo/SĐT) chuẩn hoá."""
    ip_khach = _lay_ip_khach()
    cac_khoa: list[tuple[str, int]] = [(f"{tien_to}:ip:{ip_khach}", GIOI_HAN_MOI_PHUT)]
    if dt_chuan:
        cac_khoa.append((f"{tien_to}:dt:{dt_chuan}", GIOI_HAN_THEO_KHOA_MOI_PHUT))
    if em_chuan:
        cac_khoa.append((f"{tien_to}:email:{em_chuan}", GIOI_HAN_THEO_KHOA_MOI_PHUT))
    if zl_chuan:
        cac_khoa.append((f"{tien_to}:zalo:{zl_chuan}", GIOI_HAN_THEO_KHOA_MOI_PHUT))

    cache = _lay_cache()
    bay_gio_ts = time.time()
    for khoa, gioi_han in cac_khoa:
        da_vuot = False
        da_kiem_cache = False
        if cache is not None and hasattr(cache, "get_value") and hasattr(cache, "set_value"):
            try:
                ds_ts = cache.get_value(khoa) or []
                if not isinstance(ds_ts, list):
                    ds_ts = []
                ds_ts = [float(x) for x in ds_ts if bay_gio_ts - float(x) < CUA_SO_GIAY]
                if len(ds_ts) >= gioi_han:
                    da_vuot = True
                else:
                    ds_ts.append(bay_gio_ts)
                    cache.set_value(khoa, ds_ts, expires_in_sec=CUA_SO_GIAY)
                da_kiem_cache = True
            except Exception as exc:
                logger.warning(
                    "Lỗi đọc/ghi cache giới hạn tần suất (%s), chuyển sang bộ đếm dự phòng: %s",
                    _che_kenh(khoa),
                    type(exc).__name__,
                )

        if not da_kiem_cache:
            da_vuot = _dem_trong_bo_nho(khoa, bay_gio_ts, gioi_han)

        if da_vuot:
            _tra_loi_http(
                "Quá nhiều yêu cầu trong thời gian ngắn, vui lòng thử lại sau.",
                429,
            )


def _lay_lock_bo_nho(khoa_lock: str) -> threading.Lock:
    with _KHOA_BO_NHO_GUARD:
        lock_obj = _KHOA_BO_NHO_THEO_LIEN_HE.get(khoa_lock)
        if lock_obj is None:
            if len(_KHOA_BO_NHO_THEO_LIEN_HE) >= TOI_DA_KHOA_BO_NHO:
                for k_cu, lk_cu in list(_KHOA_BO_NHO_THEO_LIEN_HE.items()):
                    if not lk_cu.locked():
                        _KHOA_BO_NHO_THEO_LIEN_HE.pop(k_cu, None)
                        break
            lock_obj = threading.Lock()
            _KHOA_BO_NHO_THEO_LIEN_HE[khoa_lock] = lock_obj
        return lock_obj


@contextmanager
def _khoa_theo_lien_he(em_chuan: str = "", zl_chuan: str = "", dt_chuan: str = ""):
    """Khoá phân tán qua `frappe.cache().lock` kèm khoá luồng nội bộ `threading.Lock`."""
    cac_khoa_lock = sorted(
        {
            *([f"linhx_form_lock:email:{em_chuan}"] if em_chuan else []),
            *([f"linhx_form_lock:zalo:{zl_chuan}"] if zl_chuan else []),
            *([f"linhx_form_lock:dt:{dt_chuan}"] if dt_chuan else []),
        }
    )
    cache = _lay_cache()
    with ExitStack() as stack:
        for k_lock in cac_khoa_lock:
            stack.enter_context(_lay_lock_bo_nho(k_lock))
            if cache is not None and hasattr(cache, "lock"):
                try:
                    stack.enter_context(cache.lock(k_lock, timeout=15))
                except Exception as exc:
                    logger.warning(
                        "Không lấy được khoá cache %s, dùng khoá bộ nhớ dự phòng: %s",
                        _che_kenh(k_lock),
                        type(exc).__name__,
                    )
        yield


def _doc_cau_hinh_kham() -> dict:
    """Đọc cấu hình câu hỏi và bảng mức chuẩn từ `sites/ifagent/kham.json` (hoặc bản chuẩn mặc định)."""
    global _CACHE_KHAM_JSON
    if _CACHE_KHAM_JSON is not None:
        return _CACHE_KHAM_JSON

    goc_repo = Path(__file__).resolve().parents[4]
    duong_dan = goc_repo / "sites" / "ifagent" / "kham.json"
    if duong_dan.is_file():
        try:
            du_lieu = json.loads(duong_dan.read_text(encoding="utf-8"))
            if isinstance(du_lieu, dict) and du_lieu.get("muc"):
                _CACHE_KHAM_JSON = du_lieu
                return _CACHE_KHAM_JSON
        except (OSError, ValueError) as exc:
            logger.warning("Không đọc được cấu hình khám từ file, dùng mặc định: %s", type(exc).__name__)

    _CACHE_KHAM_JSON = dict(t1.CAU_HINH_KHAM_MAC_DINH)
    return _CACHE_KHAM_JSON


def _cac_dang_dien_thoai(dien_thoai_raw: str, dt_chuan: str) -> list[str]:
    """Sinh các dạng biểu diễn SĐT (chuẩn hoá, nội địa 0..., quốc tế +84..., và các dạng có ngoặc/dấu cách/gạch/chấm)."""
    if not dt_chuan:
        return []
    cac_dang = {dt_chuan, f"+{dt_chuan}"}
    if dien_thoai_raw:
        cac_dang.add(dien_thoai_raw)
    if dt_chuan.startswith("84") and len(dt_chuan) > 2:
        so_noi_dia = dt_chuan[2:]
        so_0 = "0" + so_noi_dia
        cac_dang.add(so_0)
        cac_dang.add("0084" + so_noi_dia)
        if len(so_noi_dia) == 9:
            cac_dang.add(so_noi_dia)
            for sep in (" ", "-", "."):
                cac_dang.add(f"{so_0[:4]}{sep}{so_0[4:7]}{sep}{so_0[7:]}")
                cac_dang.add(f"{so_0[:3]}{sep}{so_0[3:6]}{sep}{so_0[6:]}")
                cac_dang.add(f"({so_0[:4]}){sep}{so_0[4:7]}{sep}{so_0[7:]}")
                cac_dang.add(f"({so_0[:3]}){sep}{so_0[3:6]}{sep}{so_0[6:]}")
                cac_dang.add(f"+84{sep}{so_noi_dia[:3]}{sep}{so_noi_dia[3:6]}{sep}{so_noi_dia[6:]}")
                cac_dang.add(f"(+84){sep}{so_noi_dia[:3]}{sep}{so_noi_dia[3:6]}{sep}{so_noi_dia[6:]}")
                cac_dang.add(f"84{sep}{so_noi_dia[:3]}{sep}{so_noi_dia[3:6]}{sep}{so_noi_dia[6:]}")
    return sorted(cac_dang)


def _chuan_ban_ghi_nguoi(u: dict) -> dict:
    ban_sao = dict(u)
    raw_ls = ban_sao.get("lich_su_t1")
    if isinstance(raw_ls, str) and raw_ls.strip():
        try:
            da_parse = json.loads(raw_ls)
            ban_sao["lich_su_t1"] = da_parse if isinstance(da_parse, list) else []
        except ValueError:
            ban_sao["lich_su_t1"] = []
    elif not isinstance(raw_ls, list):
        ban_sao["lich_su_t1"] = []
    return ban_sao


def _tim_nguoi_trung(du_lieu: dict) -> list[dict]:
    """Truy vấn các bản ghi LX Nguoi khớp khoá email, Zalo hoặc điện thoại đã chuẩn hoá.

    Giới hạn `limit=GIOI_HAN_TRUY_VAN_NGUOI` (20) và `order_by="creation asc"` để giữ truy vấn nhẹ
    và luôn ưu tiên gộp vào hồ sơ gốc tạo sớm nhất. Nếu chưa khớp ứng viên theo SĐT chuẩn (do DB cũ
    lưu định dạng lạ), thực hiện thêm truy vấn giới hạn theo 3 chữ số cuối rồi lọc qua `gop_trung.khoa_gop`.
    """
    if not isinstance(du_lieu, dict):
        return []
    dt_raw = str(du_lieu.get("dien_thoai") or "").strip()
    em_raw = str(du_lieu.get("email") or "").strip()
    zl_raw = str(du_lieu.get("zalo") or "").strip()
    dt_chuan = gop_trung.chuan_hoa_dien_thoai(dt_raw)
    em_chuan = gop_trung.chuan_hoa_email(em_raw)
    zl_chuan = gop_trung.chuan_hoa_zalo(zl_raw)
    if not dt_chuan and not em_chuan and not zl_chuan:
        return []

    or_filters: list = []
    cac_dt = _cac_dang_dien_thoai(dt_raw, dt_chuan)
    if cac_dt:
        or_filters.append(["LX Nguoi", "dien_thoai", "in", cac_dt])
    if em_chuan:
        cac_em = sorted({em_chuan, em_raw} if em_raw else {em_chuan})
        or_filters.append(["LX Nguoi", "email", "in", cac_em])
    if zl_chuan:
        cac_zl = sorted({zl_chuan, zl_raw} if zl_raw else {zl_chuan})
        or_filters.append(["LX Nguoi", "zalo", "in", cac_zl])

    ds_ung_vien = frappe.get_all(
        "LX Nguoi",
        fields=["name", "creation", *TRUONG_NGUOI_T1],
        or_filters=or_filters,
        order_by="creation asc",
        limit=GIOI_HAN_TRUY_VAN_NGUOI,
    )
    khoa_tim: set[str] = set()
    if dt_chuan:
        khoa_tim.add(f"dt:{dt_chuan}")
    if em_chuan:
        khoa_tim.add(f"email:{em_chuan}")
    if zl_chuan:
        khoa_tim.add(f"zalo:{zl_chuan}")

    ket_qua: list[dict] = []
    da_co_ten: set[str] = set()
    co_khop_dt = False
    for u in ds_ung_vien or []:
        if isinstance(u, dict):
            khop = gop_trung.khoa_gop(u) & khoa_tim
            if khop:
                ket_qua.append(_chuan_ban_ghi_nguoi(u))
                ten_u = str(u.get("name") or "").strip()
                if ten_u:
                    da_co_ten.add(ten_u)
                if f"dt:{dt_chuan}" in khop:
                    co_khop_dt = True

    if dt_chuan and len(dt_chuan) >= 3 and not co_khop_dt:
        duoi_3 = dt_chuan[-3:]
        ds_phu = frappe.get_all(
            "LX Nguoi",
            fields=["name", "creation", *TRUONG_NGUOI_T1],
            or_filters=[["LX Nguoi", "dien_thoai", "like", f"%{duoi_3}%"]],
            order_by="creation asc",
            limit=GIOI_HAN_TRUY_VAN_NGUOI,
        )
        co_them_phu = False
        for u in ds_phu or []:
            if isinstance(u, dict):
                ten_u = str(u.get("name") or "").strip()
                if ten_u and ten_u in da_co_ten:
                    continue
                if gop_trung.khoa_gop(u) & khoa_tim:
                    ket_qua.append(_chuan_ban_ghi_nguoi(u))
                    co_them_phu = True
                    if ten_u:
                        da_co_ten.add(ten_u)
        if co_them_phu:
            ket_qua.sort(key=lambda d: str(d.get("creation") or ""))
    return ket_qua


def _tim_nguoi_da_co(nguoi_dict: dict, ds_nguoi_cu: list[dict]) -> dict | None:
    khoa_nguoi = gop_trung.khoa_gop(nguoi_dict)
    ten_nguoi = str(nguoi_dict.get("name") or "").strip()
    for cu in ds_nguoi_cu:
        if not isinstance(cu, dict):
            continue
        ten_cu = str(cu.get("name") or "").strip()
        if not ten_cu:
            continue
        if ten_cu == ten_nguoi or (khoa_nguoi and (gop_trung.khoa_gop(cu) & khoa_nguoi)):
            return cu
    return None


def _nguoi_so_huu_kenh(nguoi_dict: dict | None, kenh_chuan: str) -> bool:
    """Kiểm tra hồ sơ LX Nguoi có thực sự sở hữu kênh liên hệ `kenh_chuan` hay không."""
    if not isinstance(nguoi_dict, dict):
        return False
    kenh = xac_minh_marketing._chuan_kenh(kenh_chuan)
    if not kenh:
        return False
    em_db = gop_trung.chuan_hoa_email(nguoi_dict.get("email"))
    dt_db = gop_trung.chuan_hoa_dien_thoai(nguoi_dict.get("dien_thoai"))
    zl_db = gop_trung.chuan_hoa_zalo(nguoi_dict.get("zalo"))
    if "@" in kenh:
        return bool(em_db and kenh == em_db)
    if dt_db and kenh == dt_db:
        return True
    if zl_db and kenh == zl_db:
        return True
    return False


def _chon_kenh_otp_cho_nguoi(
    nguoi_db: dict | None,
    *,
    em_chuan: str = "",
    dt_chuan: str = "",
    zl_chuan: str = "",
) -> str:
    """Chọn kênh phát OTP xác minh marketing cho `nguoi_db`.

    Chỉ cho phép phát OTP khi mọi kênh liên hệ gửi lên trong form đều khớp đúng kênh đã lưu trên
    `nguoi_db` (chống kẻ tấn công ghép SĐT/Zalo của nạn nhân với email của kẻ tấn công để chiếm quyền
    xác nhận double opt-in cho hồ sơ của nạn nhân).
    """
    if not isinstance(nguoi_db, dict):
        return ""
    for kenh_gui in (em_chuan, dt_chuan, zl_chuan):
        if kenh_gui and not _nguoi_so_huu_kenh(nguoi_db, kenh_gui):
            return ""
    kenh_ung_vien = em_chuan or dt_chuan or zl_chuan
    if not kenh_ung_vien or not _nguoi_so_huu_kenh(nguoi_db, kenh_ung_vien):
        return ""
    return kenh_ung_vien


def _doc_nguoi_db(ma_nguoi: str) -> dict | None:
    ma = str(ma_nguoi or "").strip()
    if not ma:
        return None
    try:
        doc = frappe.get_doc("LX Nguoi", ma)
        return {
            "name": str(getattr(doc, "name", "") or ma),
            "email": getattr(doc, "email", None),
            "dien_thoai": getattr(doc, "dien_thoai", None),
            "zalo": getattr(doc, "zalo", None),
        }
    except Exception:
        pass
    try:
        ds = frappe.get_all(
            "LX Nguoi",
            fields=["name", "email", "dien_thoai", "zalo"],
            or_filters=[["LX Nguoi", "name", "=", ma]],
            limit=GIOI_HAN_TRUY_VAN_NGUOI,
        )
        if ds and isinstance(ds[0], dict):
            return ds[0]
    except Exception as exc:
        logger.warning("Không truy vấn được LX Nguoi (%s): %s", _che_kenh(ma), type(exc).__name__)
    return None


def _kiem_nguoi_so_huu_kenh_db(ma_nguoi: str, kenh_chuan: str) -> bool:
    """Xác minh trực tiếp trên DB rằng bản ghi `LX Nguoi` (`ma_nguoi`) thực sự sở hữu `kenh_chuan`."""
    nguoi_db = _doc_nguoi_db(ma_nguoi)
    if nguoi_db is None:
        return False
    return _nguoi_so_huu_kenh(nguoi_db, kenh_chuan)


def _ghi_chu_lien_he_khac(du_lieu: dict, nguoi_da_co: dict | None) -> str:
    """Ghi nhận thông tin liên hệ mới/khác gửi kèm form vào ghi_chu của LX Co Hoi
    để không ghi đè dữ liệu cũ trên LX Nguoi mà vẫn giữ đầy đủ thông tin khách gửi.
    """
    if nguoi_da_co is None:
        return ""
    khac_biet: list[str] = []
    for truong in TRUONG_LIEN_HE_FORM:
        moi_val = str(du_lieu.get(truong) or "").strip()
        if not moi_val:
            continue
        cu_val = str(nguoi_da_co.get(truong) or "").strip()
        if not cu_val:
            khac_biet.append(f"{truong}(mới)={moi_val}")
        elif truong == "dien_thoai":
            if gop_trung.chuan_hoa_dien_thoai(cu_val) != gop_trung.chuan_hoa_dien_thoai(moi_val):
                khac_biet.append(f"dien_thoai(khác)={moi_val}")
        elif truong == "email":
            if gop_trung.chuan_hoa_email(cu_val) != gop_trung.chuan_hoa_email(moi_val):
                khac_biet.append(f"email(khác)={moi_val}")
        elif cu_val != moi_val:
            khac_biet.append(f"{truong}(khác)={moi_val}")
    if not khac_biet:
        return ""
    return "Thông tin gửi kèm form: " + "; ".join(khac_biet)


def _luu_hoac_lay_nguoi(
    nguoi_dict: dict,
    ds_nguoi_cu: list[dict],
    *,
    du_lieu_goc: dict | None = None,
) -> str:
    """Nếu Người đã có trong DB thì dùng lại mã `name` và KHÔNG ghi đè dữ liệu cũ bằng dữ liệu form;
    chỉ insert LX Nguoi mới khi chưa có.
    """
    nguoi_da_co = _tim_nguoi_da_co(nguoi_dict, ds_nguoi_cu)
    if nguoi_da_co is not None:
        return str(nguoi_da_co["name"]).strip()

    em_luu = gop_trung.chuan_hoa_email(nguoi_dict.get("email")) or nguoi_dict.get("email")
    doc_nguoi = frappe.get_doc(
        {
            "doctype": "LX Nguoi",
            "ho_ten": nguoi_dict.get("ho_ten"),
            "dien_thoai": nguoi_dict.get("dien_thoai"),
            "email": em_luu,
        }
    )
    dup_err = getattr(frappe, "DuplicateEntryError", None)
    loai_loi_trung = (dup_err,) if isinstance(dup_err, type) and issubclass(dup_err, Exception) else ()
    doc_nguoi.flags.ignore_permissions = True
    try:
        doc_nguoi.insert(ignore_permissions=True)
        return str(doc_nguoi.name)
    except loai_loi_trung:
        if du_lieu_goc:
            ds_lai = _tim_nguoi_trung(du_lieu_goc)
            if ds_lai and ds_lai[0].get("name"):
                return str(ds_lai[0]["name"]).strip()
        raise


def _lay_so_dong_y_hien_co(ds_nguoi_cu: list[dict] | str) -> list[dict]:
    """Đọc toàn bộ sổ đồng ý của các bản ghi LX Nguoi khớp khoá liên hệ.

    Nếu SĐT và email khớp hai bản ghi LX Nguoi khác nhau trong DB, gộp sổ của tất cả
    các bản ghi đó (quy về mã `name` của bản ghi chính đầu tiên theo thứ tự thời gian `luc`)
    để dòng rút đồng ý (`dong_y=0`) trên bất kỳ bản ghi khớp nào cũng được tôn trọng.
    """
    if isinstance(ds_nguoi_cu, str):
        cac_ma = [ds_nguoi_cu.strip()] if ds_nguoi_cu.strip() else []
    else:
        cac_ma = []
        for u in ds_nguoi_cu or []:
            if isinstance(u, dict):
                m = str(u.get("name") or "").strip()
                if m and m not in cac_ma:
                    cac_ma.append(m)
    if not cac_ma:
        return []
    ma_chinh = cac_ma[0]
    ket_qua: list[dict] = []
    for ma in cac_ma:
        try:
            ds = frappe.get_all(
                "LX Dong Y",
                filters={"nguoi": ma},
                fields=["name", "nguoi", "muc_dich", "dong_y", "trang_thai", "luc", "nguon"],
                order_by="luc asc, creation asc",
            )
            for x in ds or []:
                if isinstance(x, dict):
                    ban_sao = dict(x)
                    ban_sao["nguoi"] = ma_chinh
                    ket_qua.append(ban_sao)
        except Exception as exc:
            logger.warning(
                "Không đọc được sổ đồng ý hiện có của %s: %s",
                _che_kenh(ma),
                type(exc).__name__,
            )
    ket_qua.sort(key=lambda d: str(d.get("luc") or ""))
    return ket_qua


def _luu_hoac_lay_nguoi_t1(
    nguoi_moi: dict,
    ds_nguoi_cu: list[dict],
    *,
    du_lieu_goc: dict,
) -> str:
    """Lưu LX Nguoi mới hoặc cập nhật an toàn hồ sơ đã có mà không ghi đè dữ liệu cũ bằng dữ liệu form."""
    nguoi_da_co = ds_nguoi_cu[0] if ds_nguoi_cu else None
    if nguoi_da_co is not None and nguoi_da_co.get("name"):
        ten_nguoi = str(nguoi_da_co["name"]).strip()
        doc_nguoi = frappe.get_doc("LX Nguoi", ten_nguoi)
        co_thay_doi = False

        if not getattr(doc_nguoi, "nguon", None) and nguoi_moi.get("nguon"):
            doc_nguoi.nguon = nguoi_moi["nguon"]
            co_thay_doi = True
        if not getattr(doc_nguoi, "tang_pheu", None) and nguoi_moi.get("tang_pheu"):
            doc_nguoi.tang_pheu = nguoi_moi["tang_pheu"]
            co_thay_doi = True

        da_co_diem_db = (
            getattr(doc_nguoi, "t1_tong", None) not in (None, "", 0)
            or bool(str(getattr(doc_nguoi, "t1_muc", None) or "").strip())
        )
        if not da_co_diem_db:
            doc_nguoi.t1_tong = nguoi_moi.get("t1_tong")
            doc_nguoi.t1_muc = nguoi_moi.get("t1_muc")
            co_thay_doi = True
        elif nguoi_moi.get("lich_su_t1"):
            doc_nguoi.lich_su_t1 = json.dumps(nguoi_moi["lich_su_t1"], ensure_ascii=False)
            co_thay_doi = True

        if co_thay_doi:
            doc_nguoi.flags.ignore_permissions = True
            doc_nguoi.save(ignore_permissions=True)
        return ten_nguoi

    em_luu = gop_trung.chuan_hoa_email(nguoi_moi.get("email")) or nguoi_moi.get("email")
    zl_luu = gop_trung.chuan_hoa_zalo(nguoi_moi.get("zalo")) or nguoi_moi.get("zalo")
    doc_nguoi = frappe.get_doc(
        {
            "doctype": "LX Nguoi",
            "ho_ten": nguoi_moi.get("ho_ten"),
            "dien_thoai": nguoi_moi.get("dien_thoai"),
            "email": em_luu,
            "zalo": zl_luu,
            "nguon": t1.NGUON_T1,
            "tang_pheu": t1.TANG_PHEU_MOI,
            "t1_tong": nguoi_moi.get("t1_tong"),
            "t1_muc": nguoi_moi.get("t1_muc"),
        }
    )
    dup_err = getattr(frappe, "DuplicateEntryError", None)
    loai_loi_trung = (dup_err,) if isinstance(dup_err, type) and issubclass(dup_err, Exception) else ()
    doc_nguoi.flags.ignore_permissions = True
    try:
        doc_nguoi.insert(ignore_permissions=True)
        return str(doc_nguoi.name)
    except loai_loi_trung:
        ds_lai = _tim_nguoi_trung(du_lieu_goc)
        if ds_lai and ds_lai[0].get("name"):
            return str(ds_lai[0]["name"]).strip()
        raise


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=GIOI_HAN_MOI_PHUT, seconds=CUA_SO_GIAY)
def nhan_form(
    ho_ten: str | None = None,
    dien_thoai: str | None = None,
    email: str | None = None,
    nhu_cau: str | None = None,
    dong_y_lien_he: bool | int | str | None = None,
    dong_y_marketing: bool | int | str | None = None,
    **kwargs,
) -> dict:
    """Nhận form liên hệ từ Trang BU, kiểm tra hợp lệ và ghi LX Nguoi + LX Co Hoi + LX Dong Y."""
    _kiem_module_crm_bat()

    tham_so = dict(kwargs)
    for k, v in (
        ("ho_ten", ho_ten),
        ("dien_thoai", dien_thoai),
        ("email", email),
        ("nhu_cau", nhu_cau),
        ("dong_y_lien_he", dong_y_lien_he),
        ("dong_y_marketing", dong_y_marketing),
    ):
        if v is not None:
            tham_so[k] = v

    try:
        du_lieu = _trich_du_lieu_request(tham_so)
        form._kiem_tra_dau_vao(du_lieu)
    except ValueError as exc:
        _tra_loi_http(str(exc), 400)

    if not form._la_dong_y_true(du_lieu.get("dong_y_lien_he")):
        _tra_loi_http("Khách hàng phải đồng ý liên hệ trước khi gửi form", 400)

    dt_chuan = gop_trung.chuan_hoa_dien_thoai(du_lieu.get("dien_thoai"))
    em_chuan = gop_trung.chuan_hoa_email(du_lieu.get("email"))
    if not dt_chuan and not em_chuan:
        _tra_loi_http("Phải cung cấp ít nhất số điện thoại hoặc email", 400)

    _kiem_gioi_han_theo_khoa(em_chuan, "", dt_chuan, tien_to="linhx_form_rl")

    ten_site = str(getattr(getattr(frappe, "local", None), "site", "") or "").strip()
    nguon_ghi = f"trang-{ten_site}" if ten_site else "trang-bu"
    luc_ghi = dong_y.bay_gio()

    with _khoa_theo_lien_he(em_chuan, "", dt_chuan):
        ds_nguoi_cu = _tim_nguoi_trung(du_lieu)
        nguoi_da_co = ds_nguoi_cu[0] if ds_nguoi_cu else None
        so_dong_y_cu = _lay_so_dong_y_hien_co(ds_nguoi_cu) if ds_nguoi_cu else []
        so_luong_dy_cu = len(so_dong_y_cu)

        try:
            ket_qua = form.xu_ly(du_lieu, ds_nguoi_cu, so_dong_y_cu, luc_ghi, nguon_ghi)
        except ValueError as exc:
            _tra_loi_http(str(exc), 400)

        ma_nguoi = _luu_hoac_lay_nguoi(
            ket_qua["nguoi"],
            ds_nguoi_cu,
            du_lieu_goc=du_lieu,
        )
        nguoi_db = nguoi_da_co if nguoi_da_co is not None else (_doc_nguoi_db(ma_nguoi) or ket_qua["nguoi"])
        kenh_xm = _chon_kenh_otp_cho_nguoi(
            nguoi_db,
            em_chuan=em_chuan,
            dt_chuan=dt_chuan,
        )

        ch_dict = ket_qua["co_hoi"]
        ghi_chu_ch = _ghi_chu_lien_he_khac(du_lieu, nguoi_da_co)
        du_lieu_co_hoi = {
            "doctype": "LX Co Hoi",
            "nguoi": ma_nguoi,
            "nhu_cau": ch_dict.get("nhu_cau"),
            "nguon": nguon_ghi,
            "trang_thai": ch_dict.get("trang_thai") or "moi",
        }
        if ghi_chu_ch:
            du_lieu_co_hoi["ghi_chu"] = ghi_chu_ch
        doc_co_hoi = frappe.get_doc(du_lieu_co_hoi)
        doc_co_hoi.flags.ignore_permissions = True
        doc_co_hoi.insert(ignore_permissions=True)

        cac_dong_dy_moi = ket_qua["so_dong_y"][so_luong_dy_cu:]
        for dy in cac_dong_dy_moi:
            muc_dich = dy["muc_dich"]
            if nguoi_da_co is not None and form.da_rut_dong_y(so_dong_y_cu, ma_nguoi, muc_dich):
                continue
            if muc_dich == "marketing":
                if dong_y.hieu_luc(so_dong_y_cu, ma_nguoi, "marketing"):
                    continue
                if not kenh_xm:
                    continue
            trang_thai_dy = str(dy.get("trang_thai") or "").strip()
            dong_y_db = 0 if trang_thai_dy == "cho_xac_minh" else (1 if dy.get("dong_y") else 0)
            du_lieu_dy = {
                "doctype": "LX Dong Y",
                "nguoi": ma_nguoi,
                "muc_dich": muc_dich,
                "dong_y": dong_y_db,
                "luc": dy.get("luc") or luc_ghi,
                "nguon": nguon_ghi,
            }
            if trang_thai_dy:
                du_lieu_dy["trang_thai"] = trang_thai_dy
            doc_dy = frappe.get_doc(du_lieu_dy)
            doc_dy.flags.ignore_permissions = True
            doc_dy.insert(ignore_permissions=True)

            if muc_dich == "marketing" and trang_thai_dy == "cho_xac_minh" and kenh_xm:
                _luu_yeu_cau_otp_marketing_db(
                    kenh_xm,
                    ma_nguoi,
                    ket_qua["so_dong_y"],
                    luc_ghi,
                    nguon_ghi,
                )

    return {
        "ok": True,
        "nguoi": ma_nguoi,
        "co_hoi": str(doc_co_hoi.name),
        "ban_cai": ten_site,
    }


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=GIOI_HAN_MOI_PHUT, seconds=CUA_SO_GIAY)
def nhan_ket_qua_t1(
    email: str | None = None,
    zalo: str | None = None,
    ho_ten: str | None = None,
    tong: int | str | None = None,
    muc: str | None = None,
    dong_y_lien_he: bool | int | str | None = None,
    dong_y_marketing: bool | int | str | None = None,
    **kwargs,
) -> dict:
    """Tiếp nhận yêu cầu mở khoá kết quả đầy đủ T1 Khám đổi lấy email/Zalo (đồng ý một bước)."""
    _kiem_module_crm_bat()

    tham_so = dict(kwargs)
    for k, v in (
        ("email", email),
        ("zalo", zalo),
        ("ho_ten", ho_ten),
        ("tong", tong),
        ("muc", muc),
        ("dong_y_lien_he", dong_y_lien_he),
        ("dong_y_marketing", dong_y_marketing),
    ):
        if v is not None:
            tham_so[k] = v

    try:
        du_lieu = _trich_du_lieu_request(tham_so)
        t1._kiem_tra_dau_vao(du_lieu)
    except ValueError as exc:
        _tra_loi_http(str(exc), 400)

    if not _la_dong_y_true(du_lieu.get("dong_y_lien_he")):
        _tra_loi_http("Phải đồng ý liên hệ để nhận kết quả T1 đầy đủ", 400)

    em_chuan = gop_trung.chuan_hoa_email(du_lieu.get("email"))
    zl_chuan = gop_trung.chuan_hoa_zalo(du_lieu.get("zalo"))
    dt_chuan = gop_trung.chuan_hoa_dien_thoai(du_lieu.get("dien_thoai"))
    if not em_chuan and not zl_chuan:
        _tra_loi_http("Phải cung cấp ít nhất email hoặc Zalo", 400)

    _kiem_gioi_han_theo_khoa(em_chuan, zl_chuan, dt_chuan, tien_to="linhx_t1_rl")

    cau_hinh_kham = _doc_cau_hinh_kham()
    du_lieu_chuan = dict(du_lieu)
    du_lieu_chuan["dong_y_lien_he"] = True
    du_lieu_chuan["dong_y_marketing"] = _la_dong_y_true(du_lieu.get("dong_y_marketing"))
    du_lieu_chuan["bang_muc"] = cau_hinh_kham.get("muc") or []
    du_lieu_chuan["cau"] = cau_hinh_kham.get("cau") or []

    ten_site = str(getattr(getattr(frappe, "local", None), "site", "") or "").strip()
    luc_ghi = dong_y.bay_gio()

    with _khoa_theo_lien_he(em_chuan, zl_chuan, dt_chuan):
        ds_nguoi_cu = _tim_nguoi_trung(du_lieu_chuan)
        nguoi_da_co = ds_nguoi_cu[0] if ds_nguoi_cu else None
        so_dong_y_cu = _lay_so_dong_y_hien_co(ds_nguoi_cu) if ds_nguoi_cu else []
        so_luong_dy_cu = len(so_dong_y_cu)

        try:
            ket_qua = t1.ghi_ket_qua(du_lieu_chuan, ds_nguoi_cu, so_dong_y_cu, luc_ghi)
        except ValueError as exc:
            _tra_loi_http(str(exc), 400)

        ma_nguoi = _luu_hoac_lay_nguoi_t1(
            ket_qua["nguoi"],
            ds_nguoi_cu,
            du_lieu_goc=du_lieu_chuan,
        )
        nguoi_db = nguoi_da_co if nguoi_da_co is not None else (_doc_nguoi_db(ma_nguoi) or ket_qua["nguoi"])
        kenh_xm = _chon_kenh_otp_cho_nguoi(
            nguoi_db,
            em_chuan=em_chuan,
            dt_chuan=dt_chuan,
            zl_chuan=zl_chuan,
        )

        cac_dong_dy_moi = ket_qua["so_dong_y"][so_luong_dy_cu:]
        for dy in cac_dong_dy_moi:
            muc_dich = dy["muc_dich"]
            if nguoi_da_co is not None and t1.da_rut_dong_y(so_dong_y_cu, ma_nguoi, muc_dich):
                continue
            if muc_dich == "marketing":
                if dong_y.hieu_luc(so_dong_y_cu, ma_nguoi, "marketing"):
                    continue
                if not kenh_xm:
                    continue
            trang_thai_dy = str(dy.get("trang_thai") or "").strip()
            dong_y_db = 0 if trang_thai_dy == "cho_xac_minh" else (1 if dy.get("dong_y") else 0)
            du_lieu_dy = {
                "doctype": "LX Dong Y",
                "nguoi": ma_nguoi,
                "muc_dich": muc_dich,
                "dong_y": dong_y_db,
                "luc": dy.get("luc") or luc_ghi,
                "nguon": t1.NGUON_T1,
            }
            if trang_thai_dy:
                du_lieu_dy["trang_thai"] = trang_thai_dy
            doc_dy = frappe.get_doc(du_lieu_dy)
            doc_dy.flags.ignore_permissions = True
            doc_dy.insert(ignore_permissions=True)

            if muc_dich == "marketing" and trang_thai_dy == "cho_xac_minh" and kenh_xm:
                _luu_yeu_cau_otp_marketing_db(
                    kenh_xm,
                    ma_nguoi,
                    ket_qua["so_dong_y"],
                    luc_ghi,
                    t1.NGUON_T1,
                )

    t1_tong_gui = int(du_lieu_chuan["tong"])
    t1_muc_gui = str(du_lieu_chuan["muc"]).strip()
    ket_qua_day_du = t1.tao_ket_qua_day_du(
        t1_tong_gui,
        t1_muc_gui,
        du_lieu_chuan["bang_muc"],
        du_lieu_chuan["cau"],
        du_lieu_chuan.get("chon") if isinstance(du_lieu_chuan.get("chon"), dict) else None,
    )

    return {
        "ok": True,
        "nguoi": ma_nguoi,
        "ban_cai": ten_site,
        "ket_qua_day_du": ket_qua_day_du,
    }


def _gui_mail_xac_minh_marketing(email_nhan: str, ma_otp: str, muc_dich: str) -> None:
    """Gửi thông báo mã OTP xác nhận đồng ý marketing trực tiếp (`now=True`) để không lưu OTP trần vào Email Queue.

    Giới hạn hiện tại: chỉ gửi tự động qua kênh email (`@`); nếu khách chỉ cung cấp SĐT/Zalo thì
    đồng ý marketing giữ ở trạng thái `cho_xac_minh` cho tới khi xác minh kênh.
    """
    if "@" not in str(email_nhan or ""):
        return
    sendmail_fn = getattr(frappe, "sendmail", None)
    if not callable(sendmail_fn):
        return
    try:
        sendmail_fn(
            recipients=[email_nhan],
            subject="Xác nhận đăng ký nhận bản tin & tài liệu (Double Opt-in)",
            message=(
                f"<p>Mã xác nhận đồng ý nhận thông tin ({muc_dich}) của bạn là: "
                f"<strong>{ma_otp}</strong> (hiệu lực 10 phút, dùng 1 lần).</p>"
                "<p>Vui lòng nhập mã và bấm nút Xác nhận (POST) trên trang để kích hoạt đồng ý.</p>"
            ),
            now=True,
        )
    except Exception as exc:
        logger.warning(
            "Không gửi được email OTP xác minh marketing cho %s: %s",
            _che_kenh(email_nhan),
            type(exc).__name__,
        )


def _lay_lich_su_phat_otp_1_gio(khoa_kenh: str) -> list[str]:
    khoa_cache = f"linhx_otp_phat_1h:{khoa_kenh}"
    cache = _lay_cache()
    if cache is not None and hasattr(cache, "get_value"):
        try:
            ds = cache.get_value(khoa_cache)
            if isinstance(ds, list):
                return [str(x) for x in ds if x]
        except Exception as exc:
            logger.warning(
                "Lỗi đọc cache lịch sử phát OTP (%s): %s",
                _che_kenh(khoa_kenh),
                type(exc).__name__,
            )
    with _KHOA_BO_NHO_GUARD:
        return list(_LICH_SU_PHAT_OTP_THEO_KENH.get(khoa_kenh, []))


def _luu_lich_su_phat_otp_1_gio(khoa_kenh: str, lich_su: list[str]) -> None:
    ds_chuan = [str(x) for x in (lich_su or []) if x]
    with _KHOA_BO_NHO_GUARD:
        if len(_LICH_SU_PHAT_OTP_THEO_KENH) >= TOI_DA_KHOA_BO_NHO and khoa_kenh not in _LICH_SU_PHAT_OTP_THEO_KENH:
            _LICH_SU_PHAT_OTP_THEO_KENH.pop(next(iter(_LICH_SU_PHAT_OTP_THEO_KENH)), None)
        _LICH_SU_PHAT_OTP_THEO_KENH[khoa_kenh] = ds_chuan
    khoa_cache = f"linhx_otp_phat_1h:{khoa_kenh}"
    cache = _lay_cache()
    if cache is not None and hasattr(cache, "set_value"):
        try:
            cache.set_value(khoa_cache, ds_chuan, expires_in_sec=CUA_SO_PHAT_OTP_GIAY)
        except Exception as exc:
            logger.warning(
                "Lỗi ghi cache lịch sử phát OTP (%s): %s",
                _che_kenh(khoa_kenh),
                type(exc).__name__,
            )


def _doc_otp_db_for_update(khoa_kenh: str) -> tuple[object | None, dict]:
    """Đọc bản ghi LX Xac Minh Marketing từ DB (kèm khoá dòng FOR UPDATE khi có SQL) và chuyển sang kho_otp."""
    db_obj = getattr(frappe, "db", None)
    ten_doc = ""
    if db_obj is not None and hasattr(db_obj, "sql"):
        try:
            rows = db_obj.sql(
                "SELECT `name` FROM `tabLX Xac Minh Marketing` WHERE `khoa_kenh` = %s FOR UPDATE",
                (khoa_kenh,),
            )
            if rows and rows[0] and rows[0][0]:
                ten_doc = str(rows[0][0]).strip()
        except Exception as exc:
            logger.warning(
                "Không khoá dòng FOR UPDATE cho LX Xac Minh Marketing (%s): %s",
                _che_kenh(khoa_kenh),
                type(exc).__name__,
            )

    if not ten_doc:
        try:
            ds = frappe.get_all(
                "LX Xac Minh Marketing",
                filters={"khoa_kenh": khoa_kenh},
                fields=[
                    "name",
                    "khoa_kenh",
                    "email",
                    "nguoi",
                    "muc_dich",
                    "ma_bam",
                    "tao_luc",
                    "het_han_luc",
                    "so_lan_sai",
                    "da_dung",
                    "khoa_den",
                ],
                limit=1,
            )
            if ds and isinstance(ds[0], dict) and ds[0].get("name"):
                ten_doc = str(ds[0]["name"]).strip()
        except Exception as exc:
            logger.warning(
                "Không truy vấn được LX Xac Minh Marketing (%s): %s",
                _che_kenh(khoa_kenh),
                type(exc).__name__,
            )

    lich_su_phat = _lay_lich_su_phat_otp_1_gio(khoa_kenh)
    if not ten_doc:
        if lich_su_phat:
            return None, {khoa_kenh: {"lich_su_phat": lich_su_phat}}
        return None, {}

    try:
        doc = frappe.get_doc("LX Xac Minh Marketing", ten_doc)
    except Exception as exc:
        logger.warning(
            "Không đọc được doc LX Xac Minh Marketing %s: %s",
            _che_kenh(ten_doc),
            type(exc).__name__,
        )
        return None, {}

    tao_luc_db = str(getattr(doc, "tao_luc", "") or "").strip()
    if tao_luc_db and tao_luc_db not in lich_su_phat:
        lich_su_phat.append(tao_luc_db)

    kho_otp = {
        khoa_kenh: {
            "email": str(getattr(doc, "email", "") or ""),
            "nguoi": str(getattr(doc, "nguoi", "") or ""),
            "muc_dich": str(getattr(doc, "muc_dich", "marketing") or "marketing"),
            "ma_bam": str(getattr(doc, "ma_bam", "") or ""),
            "tao_luc": tao_luc_db,
            "het_han_luc": str(getattr(doc, "het_han_luc", "") or ""),
            "so_lan_sai": int(getattr(doc, "so_lan_sai", 0) or 0),
            "da_dung": bool(int(getattr(doc, "da_dung", 0) or 0)),
            "khoa_den": getattr(doc, "khoa_den", None) or None,
            "lich_su_phat": lich_su_phat,
        }
    }
    return doc, kho_otp


def _ma_cu_con_hieu_luc(ban_ghi: dict | None, ma_nguoi: str, luc_ghi: str) -> bool:
    """Kiểm tra mã OTP hiện có trong DB còn hạn, chưa dùng, chưa bị khoá và khớp cùng `ma_nguoi`."""
    if not isinstance(ban_ghi, dict):
        return False
    if not str(ban_ghi.get("ma_bam") or "").strip():
        return False
    if bool(ban_ghi.get("da_dung")):
        return False
    if str(ban_ghi.get("nguoi") or "").strip() != ma_nguoi:
        return False
    try:
        dt_luc = dong_y._parse_tg(luc_ghi)
        khoa_den = ban_ghi.get("khoa_den")
        if khoa_den and dt_luc <= dong_y._parse_tg(khoa_den):
            return False
        het_han = ban_ghi.get("het_han_luc")
        if not het_han or dt_luc > dong_y._parse_tg(het_han):
            return False
    except ValueError:
        return False
    return True


def _luu_yeu_cau_otp_marketing_db(
    kenh_raw: str,
    ma_nguoi: str,
    so_dong_y: list[dict],
    luc_ghi: str,
    nguon_ghi: str,
    *,
    ma_otp: str | None = None,
) -> dict | None:
    """Phát mã OTP xác minh marketing, lưu bản băm vào DB trước rồi mới gửi email thông báo."""
    kenh_chuan = xac_minh_marketing._chuan_kenh(kenh_raw)
    if not kenh_chuan or not ma_nguoi:
        return None
    if not _kiem_nguoi_so_huu_kenh_db(ma_nguoi, kenh_chuan):
        return None

    khoa_kenh = xac_minh_marketing._khoa_otp(kenh_chuan, xac_minh_marketing.MUC_DICH_MARKETING)
    doc_cu, kho_otp = _doc_otp_db_for_update(khoa_kenh)
    ban_ghi_cu = kho_otp.get(khoa_kenh) if isinstance(kho_otp, dict) else None

    # Không phát mã mới (và không gửi lại mail) khi mã cũ còn hạn và chưa dùng trong luồng gửi form
    if ma_otp is None and doc_cu is not None and _ma_cu_con_hieu_luc(ban_ghi_cu, ma_nguoi, luc_ghi):
        return {
            "email": kenh_chuan,
            "nguoi": ma_nguoi,
            "muc_dich": xac_minh_marketing.MUC_DICH_MARKETING,
            "trang_thai": "cho_xac_minh",
            "het_han_luc": ban_ghi_cu.get("het_han_luc"),
            "so_dong_y": so_dong_y,
        }

    hang_doi_mail: list[tuple[str, str, str]] = []
    try:
        kq_yc = xac_minh_marketing.tao_yeu_cau(
            kho_otp,
            kenh_chuan,
            ma_nguoi,
            so_dong_y,
            luc_ghi,
            ma_otp=ma_otp,
            gui_mail=lambda em, ma, md: hang_doi_mail.append((em, ma, md)),
        )
    except ValueError as exc:
        logger.warning(
            "Không phát được mã OTP xác minh marketing cho %s: %s",
            _che_kenh(kenh_chuan),
            type(exc).__name__,
        )
        return None

    ban_ghi = xac_minh_marketing._tim_ban_ghi_otp(kho_otp, kenh_chuan)
    if not isinstance(ban_ghi, dict):
        return kq_yc

    du_lieu_otp = {
        "khoa_kenh": khoa_kenh,
        "email": kenh_chuan,
        "nguoi": ma_nguoi,
        "muc_dich": xac_minh_marketing.MUC_DICH_MARKETING,
        "ma_bam": str(ban_ghi.get("ma_bam") or ""),
        "tao_luc": str(ban_ghi.get("tao_luc") or luc_ghi),
        "het_han_luc": str(ban_ghi.get("het_han_luc") or ""),
        "so_lan_sai": int(ban_ghi.get("so_lan_sai", 0) or 0),
        "da_dung": 1 if ban_ghi.get("da_dung") else 0,
        "khoa_den": ban_ghi.get("khoa_den") or None,
        "nguon": nguon_ghi,
    }
    if doc_cu is not None:
        for k, v in du_lieu_otp.items():
            setattr(doc_cu, k, v)
        doc_cu.flags.ignore_permissions = True
        doc_cu.save(ignore_permissions=True)
    else:
        doc_moi = frappe.get_doc({"doctype": "LX Xac Minh Marketing", **du_lieu_otp})
        doc_moi.flags.ignore_permissions = True
        doc_moi.insert(ignore_permissions=True)

    _luu_lich_su_phat_otp_1_gio(khoa_kenh, list(ban_ghi.get("lich_su_phat") or []))

    # Chỉ gửi mail sau khi đã lưu bản ghi OTP vào DB thành công
    for em_nhan, ma_gui, md_gui in hang_doi_mail:
        _gui_mail_xac_minh_marketing(em_nhan, ma_gui, md_gui)

    return kq_yc


def _tra_loi_xac_minh_that_bai() -> dict:
    """Trả cùng một phản hồi lỗi chung cho mọi trường hợp xác minh OTP thất bại để chống dò kênh/người."""
    if hasattr(frappe, "local") and isinstance(getattr(frappe.local, "response", None), dict):
        frappe.local.response["http_status_code"] = 400
    return {
        "ok": False,
        "ly_do": LOI_XAC_MINH_CHUNG,
    }


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=GIOI_HAN_MOI_PHUT, seconds=CUA_SO_GIAY)
def xac_nhan_marketing(
    email: str | None = None,
    nguoi: str | None = None,
    ma_nhap: str | None = None,
    ma_otp: str | None = None,
    dien_thoai: str | None = None,
    **kwargs,
) -> dict:
    """Endpoint xác nhận OTP đồng ý marketing (chỉ nhận POST, lưu trạng thái OTP và LX Dong Y trong DB)."""
    _kiem_module_crm_bat()

    local_obj = getattr(frappe, "local", None)
    req = getattr(local_obj, "request", None)
    pt = str(getattr(req, "method", None) or "POST").strip().upper()
    if pt != "POST":
        if hasattr(frappe, "local") and isinstance(getattr(frappe.local, "response", None), dict):
            frappe.local.response["http_status_code"] = 405
        return {
            "ok": False,
            "can_post": True,
            "ly_do": "phuong_thuc_khong_hop_le",
        }

    tham_so = dict(kwargs)
    for k, v in (
        ("email", email),
        ("nguoi", nguoi),
        ("ma_nhap", ma_nhap),
        ("ma_otp", ma_otp),
        ("dien_thoai", dien_thoai),
    ):
        if v is not None:
            tham_so[k] = v

    try:
        du_lieu = _trich_du_lieu_request(tham_so)
    except ValueError as exc:
        _tra_loi_http(str(exc), 400)

    email_raw = str(du_lieu.get("email") or "").strip()
    dt_raw = str(du_lieu.get("dien_thoai") or "").strip()
    nguoi_param = str(du_lieu.get("nguoi") or "").strip()
    ma_code = str(du_lieu.get("ma_nhap") or du_lieu.get("ma_otp") or du_lieu.get("otp") or "").strip()

    if len(email_raw) > form.DO_DAI_TOI_DA_EMAIL or len(dt_raw) > form.DO_DAI_TOI_DA_DIEN_THOAI:
        _tra_loi_http("Thông tin kênh xác nhận vượt quá độ dài cho phép", 400)
    if len(nguoi_param) > 140 or len(ma_code) > 32:
        _tra_loi_http("Dữ liệu xác nhận không hợp lệ", 400)

    em_chuan = gop_trung.chuan_hoa_email(email_raw)
    dt_chuan = gop_trung.chuan_hoa_dien_thoai(dt_raw)
    kenh_chuan = em_chuan or dt_chuan or xac_minh_marketing._chuan_kenh(email_raw)
    if not kenh_chuan or not ma_code:
        _tra_loi_http("Phải cung cấp kênh xác nhận và mã OTP", 400)

    _kiem_gioi_han_theo_khoa(em_chuan, "", dt_chuan, tien_to="linhx_xm_mkt_rl")
    luc_ghi = dong_y.bay_gio()

    with _khoa_theo_lien_he(em_chuan or kenh_chuan, "", dt_chuan):
        khoa_kenh = xac_minh_marketing._khoa_otp(kenh_chuan, xac_minh_marketing.MUC_DICH_MARKETING)
        doc_otp, kho_otp = _doc_otp_db_for_update(khoa_kenh)
        if doc_otp is None:
            xac_minh_marketing.bam_ma(kenh_chuan, xac_minh_marketing.MUC_DICH_MARKETING, ma_code)
            return _tra_loi_xac_minh_that_bai()

        ma_nguoi_db = str(getattr(doc_otp, "nguoi", "") or "").strip()
        if nguoi_param and ma_nguoi_db and nguoi_param != ma_nguoi_db:
            xac_minh_marketing.bam_ma(kenh_chuan, xac_minh_marketing.MUC_DICH_MARKETING, ma_code)
            return _tra_loi_xac_minh_that_bai()

        ma_nguoi = ma_nguoi_db or nguoi_param
        if not ma_nguoi or not _kiem_nguoi_so_huu_kenh_db(ma_nguoi, kenh_chuan):
            xac_minh_marketing.bam_ma(kenh_chuan, xac_minh_marketing.MUC_DICH_MARKETING, ma_code)
            return _tra_loi_xac_minh_that_bai()

        ds_nguoi_lien_quan = _tim_nguoi_trung({"email": em_chuan, "dien_thoai": dt_chuan})
        cac_ho_so_so = [{"name": ma_nguoi}]
        for u in ds_nguoi_lien_quan:
            if isinstance(u, dict) and u.get("name") and str(u["name"]).strip() != ma_nguoi:
                cac_ho_so_so.append(u)
        so_dong_y_cu = _lay_so_dong_y_hien_co(cac_ho_so_so)

        ma_http, kq = xac_minh_marketing.xac_nhan_marketing(
            "POST",
            kho_otp,
            kenh_chuan,
            ma_nguoi,
            ma_code,
            so_dong_y_cu,
            luc_ghi,
            nguon="xac-minh-otp",
        )

        ban_ghi_cap_nhat = xac_minh_marketing._tim_ban_ghi_otp(kho_otp, kenh_chuan)
        if isinstance(ban_ghi_cap_nhat, dict):
            doc_otp.so_lan_sai = int(ban_ghi_cap_nhat.get("so_lan_sai", 0) or 0)
            doc_otp.da_dung = 1 if ban_ghi_cap_nhat.get("da_dung") else 0
            doc_otp.khoa_den = ban_ghi_cap_nhat.get("khoa_den") or None
            doc_otp.flags.ignore_permissions = True
            doc_otp.save(ignore_permissions=True)

        tao_luc_otp = str(getattr(doc_otp, "tao_luc", "") or "").strip()
        if (
            ma_http != 200
            or not kq.get("ok")
            or xac_minh_marketing.da_rut_dong_y_sau_otp(so_dong_y_cu, ma_nguoi, tao_luc_otp)
        ):
            return _tra_loi_xac_minh_that_bai()

        if hasattr(frappe, "local") and isinstance(getattr(frappe.local, "response", None), dict):
            frappe.local.response["http_status_code"] = 200

        if not dong_y.hieu_luc(so_dong_y_cu, ma_nguoi, "marketing"):
            doc_dy = frappe.get_doc(
                {
                    "doctype": "LX Dong Y",
                    "nguoi": ma_nguoi,
                    "muc_dich": "marketing",
                    "dong_y": 1,
                    "trang_thai": "da_xac_minh",
                    "luc": luc_ghi,
                    "nguon": "xac-minh-otp",
                }
            )
            doc_dy.flags.ignore_permissions = True
            doc_dy.insert(ignore_permissions=True)

        return {
            "ok": True,
            "muc_dich": "marketing",
            "trang_thai": "da_xac_minh",
        }
