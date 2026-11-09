"""API nhận kết quả T1 Khám từ Trang BU (allow_guest=True, giới hạn tần suất qua rate_limit)."""
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
from linhx_core.crm import dong_y, gop_trung, t1

logger = logging.getLogger(__name__)

GIOI_HAN_MOI_PHUT = 10
GIOI_HAN_THEO_KHOA_MOI_PHUT = 5
CUA_SO_GIAY = 60
GIOI_HAN_BODY_BYTES = 16 * 1024
GIOI_HAN_TRUY_VAN_NGUOI = 20
TOI_DA_KHOA_BO_NHO = 1000
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
TRUONG_CAM_TU_CLIENT = ("nguon", "tang_pheu", "bang_muc", "cau")

_BO_DEM_KHOA_DU_PHONG: dict[str, list[float]] = {}
_KHOA_BO_NHO_GUARD = threading.Lock()
_KHOA_BO_NHO_THEO_LIEN_HE: dict[str, threading.Lock] = {}
_CACHE_KHAM_JSON: dict | None = None


def _la_dong_y_true(gia_tri: object) -> bool:
    if isinstance(gia_tri, bool):
        return gia_tri
    if isinstance(gia_tri, int):
        return gia_tri == 1
    if isinstance(gia_tri, str):
        return gia_tri.strip().lower() in ("1", "true", "yes", "on")
    return False


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
            logger.warning("Không kết nối được frappe.cache(): %s", exc)
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
                logger.warning("Lỗi đọc raw request body: %s", exc)
        if hasattr(req, "get_json"):
            try:
                body_json = req.get_json(silent=True)
                if isinstance(body_json, dict):
                    du_lieu.update(body_json)
            except Exception as exc:
                logger.warning("Lỗi phân tích JSON request body: %s", exc)

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
                logger.warning("Lỗi phân tích form_dict['data']: %s", exc)

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


def _dem_trong_bo_nho(khoa: str, bay_gio_ts: float, gioi_han: int) -> bool:
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


def _kiem_gioi_han_theo_khoa(em_chuan: str, zl_chuan: str, dt_chuan: str = "") -> None:
    """Giới hạn tần suất theo IP khách và từng khoá liên hệ (email/Zalo/SĐT) chuẩn hoá."""
    ip_khach = _lay_ip_khach()
    cac_khoa: list[tuple[str, int]] = [(f"linhx_t1_rl:ip:{ip_khach}", GIOI_HAN_MOI_PHUT)]
    if em_chuan:
        cac_khoa.append((f"linhx_t1_rl:email:{em_chuan}", GIOI_HAN_THEO_KHOA_MOI_PHUT))
    if zl_chuan:
        cac_khoa.append((f"linhx_t1_rl:zalo:{zl_chuan}", GIOI_HAN_THEO_KHOA_MOI_PHUT))
    if dt_chuan:
        cac_khoa.append((f"linhx_t1_rl:dt:{dt_chuan}", GIOI_HAN_THEO_KHOA_MOI_PHUT))

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
                logger.warning("Lỗi đọc/ghi cache giới hạn tần suất (%s), chuyển sang bộ đếm dự phòng: %s", khoa, exc)

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
def _khoa_theo_lien_he(em_chuan: str, zl_chuan: str, dt_chuan: str = ""):
    """Khoá phân tán qua `frappe.cache().lock` kèm khoá luồng nội bộ `threading.Lock`."""
    cac_khoa_lock = sorted(
        {
            *([f"linhx_t1_lock:email:{em_chuan}"] if em_chuan else []),
            *([f"linhx_t1_lock:zalo:{zl_chuan}"] if zl_chuan else []),
            *([f"linhx_t1_lock:dt:{dt_chuan}"] if dt_chuan else []),
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
                    logger.warning("Không lấy được khoá cache %s, dùng khoá bộ nhớ dự phòng: %s", k_lock, exc)
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
            logger.warning("Không đọc được %s, dùng cấu hình khám mặc định: %s", duong_dan, exc)

    _CACHE_KHAM_JSON = dict(t1.CAU_HINH_KHAM_MAC_DINH)
    return _CACHE_KHAM_JSON


def _cac_dang_dien_thoai(dien_thoai_raw: str, dt_chuan: str) -> list[str]:
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
    return sorted(cac_dang)


def _tim_nguoi_trung(du_lieu: dict) -> list[dict]:
    """Truy vấn các bản ghi LX Nguoi khớp khoá email, Zalo hoặc điện thoại đã chuẩn hoá."""
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
    for u in ds_ung_vien or []:
        if isinstance(u, dict) and (gop_trung.khoa_gop(u) & khoa_tim):
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
            ket_qua.append(ban_sao)
    return ket_qua


def _lay_so_dong_y_hien_co(ds_nguoi_cu: list[dict] | str) -> list[dict]:
    """Đọc toàn bộ sổ đồng ý của các bản ghi LX Nguoi khớp khoá liên hệ."""
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
                fields=["name", "nguoi", "muc_dich", "dong_y", "luc", "nguon"],
                order_by="luc asc, creation asc",
            )
            for x in ds or []:
                if isinstance(x, dict):
                    ban_sao = dict(x)
                    ban_sao["nguoi"] = ma_chinh
                    ket_qua.append(ban_sao)
        except Exception as exc:
            logger.warning("Không đọc được sổ đồng ý hiện có của %s: %s", ma, exc)
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
    doc_nguoi.flags.ignore_permissions = True
    try:
        doc_nguoi.insert(ignore_permissions=True)
        return str(doc_nguoi.name)
    except Exception:
        ds_lai = _tim_nguoi_trung(du_lieu_goc)
        if ds_lai and ds_lai[0].get("name"):
            return str(ds_lai[0]["name"]).strip()
        raise


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

    _kiem_gioi_han_theo_khoa(em_chuan, zl_chuan, dt_chuan)

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

        cac_dong_dy_moi = ket_qua["so_dong_y"][so_luong_dy_cu:]
        for dy in cac_dong_dy_moi:
            muc_dich = dy["muc_dich"]
            if nguoi_da_co is not None and t1.da_rut_dong_y(so_dong_y_cu, ma_nguoi, muc_dich):
                continue
            doc_dy = frappe.get_doc(
                {
                    "doctype": "LX Dong Y",
                    "nguoi": ma_nguoi,
                    "muc_dich": muc_dich,
                    "dong_y": 1 if dy.get("dong_y") else 0,
                    "luc": dy.get("luc") or luc_ghi,
                    "nguon": t1.NGUON_T1,
                }
            )
            doc_dy.flags.ignore_permissions = True
            doc_dy.insert(ignore_permissions=True)

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
