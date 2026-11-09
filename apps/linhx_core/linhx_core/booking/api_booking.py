"""API đặt lịch gọi tư vấn từ Trang BU (allow_guest=True, có giới hạn tần suất) và xem lịch chờ gọi của người phụ trách."""
from __future__ import annotations

from contextlib import ExitStack, contextmanager
import ipaddress
import json
import logging
import threading
import time

import frappe
from frappe.rate_limiter import rate_limit

from linhx_core import co_module
from linhx_core.booking import dat_lich
from linhx_core.booking.doctype.lx_lich_goi.lx_lich_goi import _lay_ds_lich_phu_trach_db
from linhx_core.crm import co_hoi as mod_co_hoi
from linhx_core.crm import dong_y, form, gop_trung
from linhx_core.crm.api_form import (
    _chon_kenh_otp_cho_nguoi,
    _doc_nguoi_db,
    _lay_so_dong_y_hien_co,
    _luu_hoac_lay_nguoi,
    _tim_nguoi_trung,
)
from linhx_core.crm.doctype.lx_co_hoi.lx_co_hoi import USER_LOAI_TRU, _loc_ung_vien_crm
from linhx_core.crm.quyen_don_vi import la_user_mien, lay_don_vi_cua_user

logger = logging.getLogger(__name__)

GIOI_HAN_MOI_PHUT = 10
GIOI_HAN_THEO_KHOA_MOI_PHUT = 5
CUA_SO_GIAY = 60
GIOI_HAN_BODY_BYTES = 16 * 1024
TOI_DA_KHOA_BO_NHO = 1000
DO_DAI_GHI_CHU_TOI_DA = 2000
TRUONG_CAM_TU_CLIENT = ("nguon", "trang_thai", "don_vi", "ket_thuc")

_BO_DEM_LICH_DU_PHONG: dict[str, list[float]] = {}
_KHOA_GUARD = threading.Lock()
_KHOA_THEO_TEN: dict[str, threading.Lock] = {}


def _che_kenh(gia_tri: object) -> str:
    chu = str(gia_tri or "").strip()
    if not chu:
        return "***"
    if "@" in chu:
        truoc, sau = chu.split("@", 1)
        ky_tu = truoc[0] if truoc else ""
        return f"{ky_tu}***@{sau}"
    if len(chu) <= 4:
        return "***"
    return f"{chu[:2]}***{chu[-2:]}"


def _tra_loi_http(thong_diep: str, ma_http: int, loai_loi=None) -> None:
    if hasattr(frappe, "local") and isinstance(getattr(frappe.local, "response", None), dict):
        frappe.local.response["http_status_code"] = ma_http
    exc_cls = loai_loi or getattr(frappe, "ValidationError", ValueError)
    frappe.throw(thong_diep, exc_cls)


def _kiem_phuong_thuc_post() -> None:
    local_obj = getattr(frappe, "local", None)
    req = getattr(local_obj, "request", None) or getattr(frappe, "request", None)
    if req is not None:
        method = str(getattr(req, "method", "POST") or "POST").upper()
        if method != "POST":
            _tra_loi_http("Chỉ chấp nhận phương thức POST", 405)


def _kiem_module_crm_bat() -> None:
    cau_hinh = co_module._doc_cau_hinh_frappe()
    if co_module.doctype_bi_an("LX Nguoi", cau_hinh):
        _tra_loi_http("Module CRM đang tắt", 403, getattr(frappe, "PermissionError", PermissionError))


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


def _dem_trong_bo_nho(khoa: str, bay_gio_ts: float, gioi_han: int) -> bool:
    with _KHOA_GUARD:
        het_han = [
            k
            for k, ds in _BO_DEM_LICH_DU_PHONG.items()
            if not ds or all(bay_gio_ts - ts >= CUA_SO_GIAY for ts in ds)
        ]
        for k in het_han:
            _BO_DEM_LICH_DU_PHONG.pop(k, None)

        ds_ts = [x for x in _BO_DEM_LICH_DU_PHONG.get(khoa, []) if bay_gio_ts - x < CUA_SO_GIAY]
        if len(ds_ts) >= gioi_han:
            _BO_DEM_LICH_DU_PHONG[khoa] = ds_ts
            return True

        if khoa not in _BO_DEM_LICH_DU_PHONG and len(_BO_DEM_LICH_DU_PHONG) >= TOI_DA_KHOA_BO_NHO:
            khoa_cu = min(
                _BO_DEM_LICH_DU_PHONG,
                key=lambda k: max(_BO_DEM_LICH_DU_PHONG[k]) if _BO_DEM_LICH_DU_PHONG[k] else 0.0,
            )
            _BO_DEM_LICH_DU_PHONG.pop(khoa_cu, None)

        ds_ts.append(bay_gio_ts)
        _BO_DEM_LICH_DU_PHONG[khoa] = ds_ts
        return False


def _kiem_gioi_han_tan_suat_dat_lich(
    *,
    dt_chuan: str = "",
    em_chuan: str = "",
    ma_nguoi: str = "",
) -> None:
    ip_khach = _lay_ip_khach()
    cac_khoa: list[tuple[str, int]] = [(f"linhx_booking_rl:ip:{ip_khach}", GIOI_HAN_MOI_PHUT)]
    if dt_chuan:
        cac_khoa.append((f"linhx_booking_rl:dt:{dt_chuan}", GIOI_HAN_THEO_KHOA_MOI_PHUT))
    if em_chuan:
        cac_khoa.append((f"linhx_booking_rl:email:{em_chuan}", GIOI_HAN_THEO_KHOA_MOI_PHUT))
    if ma_nguoi:
        cac_khoa.append((f"linhx_booking_rl:nguoi:{ma_nguoi}", GIOI_HAN_THEO_KHOA_MOI_PHUT))

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
                    "Lỗi đọc/ghi cache giới hạn tần suất đặt lịch (%s): %s",
                    _che_kenh(khoa),
                    type(exc).__name__,
                )

        if not da_kiem_cache:
            da_vuot = _dem_trong_bo_nho(khoa, bay_gio_ts, gioi_han)

        if da_vuot:
            _tra_loi_http(
                "Quá nhiều yêu cầu đặt lịch trong thời gian ngắn, vui lòng thử lại sau.",
                429,
            )


def _lay_lock_bo_nho(khoa_lock: str) -> threading.Lock:
    with _KHOA_GUARD:
        lock_obj = _KHOA_THEO_TEN.get(khoa_lock)
        if lock_obj is None:
            if len(_KHOA_THEO_TEN) >= TOI_DA_KHOA_BO_NHO:
                for k_cu, lk_cu in list(_KHOA_THEO_TEN.items()):
                    if not lk_cu.locked():
                        _KHOA_THEO_TEN.pop(k_cu, None)
                        break
            lock_obj = threading.Lock()
            _KHOA_THEO_TEN[khoa_lock] = lock_obj
        return lock_obj


@contextmanager
def _khoa_dat_lich(*cac_khoa: str):
    """Khoá phân tán qua `frappe.cache().lock` kèm khoá luồng nội bộ `threading.Lock`."""
    ds_khoa = sorted({f"linhx_booking_lock:{k.strip()}" for k in cac_khoa if k and str(k).strip()})
    cache = _lay_cache()
    with ExitStack() as stack:
        for k_lock in ds_khoa:
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


def _tim_co_hoi_mo_cua_nguoi(ma_nguoi: str) -> dict | None:
    ng = str(ma_nguoi or "").strip()
    if not ng or not callable(getattr(frappe, "get_all", None)):
        return None
    try:
        ds = frappe.get_all(
            "LX Co Hoi",
            filters={"nguoi": ng, "trang_thai": ["in", ["moi", "dang_lam"]]},
            fields=["name", "nguoi", "phu_trach", "don_vi", "trang_thai", "creation"],
            order_by="creation desc",
            limit=5,
        )
        if ds and isinstance(ds[0], dict):
            return ds[0]
    except Exception as exc:
        logger.warning("Không truy vấn được LX Co Hoi của %s: %s", _che_kenh(ng), type(exc).__name__)
    return None


def _chon_phu_trach_tu_dong(don_vi: str | None = None) -> str:
    if not callable(getattr(frappe, "get_all", None)):
        return ""
    try:
        ds_user = frappe.get_all(
            "User",
            filters={
                "enabled": 1,
                "user_type": "System User",
                "name": ["not in", list(USER_LOAI_TRU)],
            },
            pluck="name",
            order_by="creation asc",
        )
    except Exception as exc:
        logger.warning("Không truy vấn được danh sách System User: %s", type(exc).__name__)
        return ""

    ung_vien = _loc_ung_vien_crm(frappe, list(ds_user or []), don_vi)
    if not ung_vien and don_vi:
        ung_vien = _loc_ung_vien_crm(frappe, list(ds_user or []), None)
    if not ung_vien:
        ung_vien = [str(u).strip() for u in (ds_user or []) if str(u or "").strip()]
    if not ung_vien:
        return ""

    ds_mo: list[dict] = []
    try:
        ds_mo = list(
            frappe.get_all(
                "LX Co Hoi",
                filters={"trang_thai": ["in", ["moi", "dang_lam"]]},
                fields=["name", "phu_trach", "trang_thai"],
            )
            or []
        )
    except Exception:
        ds_mo = []
    return mod_co_hoi.giao({}, ung_vien, ds_mo)


def _xac_minh_phu_trach_hop_le(phu_trach: str, don_vi: str | None = None) -> str:
    pt = str(phu_trach or "").strip()
    if not pt:
        return ""
    if pt == "Guest":
        _tra_loi_http("Người phụ trách không hợp lệ", 400)
    db = getattr(frappe, "db", None)
    if db is not None and callable(getattr(db, "get_value", None)):
        try:
            tt_user = db.get_value("User", pt, ["name", "enabled", "user_type"], as_dict=True)
            if isinstance(tt_user, dict) and tt_user:
                if int(tt_user.get("enabled", 1) or 0) != 1:
                    _tra_loi_http("Người phụ trách đang ngừng hoạt động", 400)
                if tt_user.get("user_type") and tt_user.get("user_type") != "System User":
                    _tra_loi_http("Người phụ trách phải là nhân sự hệ thống", 400)
                if don_vi and callable(getattr(frappe, "get_all", None)) and not la_user_mien(pt):
                    ds_up = frappe.get_all(
                        "User Permission",
                        filters={"allow": "LX Don Vi"},
                        fields=["user", "for_value"],
                        limit=50,
                    )
                    if ds_up:
                        dv_user = lay_don_vi_cua_user(pt)
                        if dv_user and don_vi not in dv_user:
                            _tra_loi_http("Người phụ trách không thuộc đơn vị của khách hàng", 403)
        except Exception as exc:
            if type(exc).__name__ in ("ValidationError", "PermissionError") or isinstance(
                exc, (ValueError, PermissionError)
            ):
                raise
    return pt


def _giai_quyet_nguoi_va_co_hoi(
    du_lieu: dict,
    *,
    dt_chuan: str,
    em_chuan: str,
    nguon_ghi: str,
) -> tuple[str, str, str, str]:
    """Xác định `(ma_nguoi, ma_co_hoi, phu_trach_co_hoi, don_vi)` an toàn từ thông tin đặt lịch."""
    ma_nguoi_gui = str(du_lieu.get("nguoi") or "").strip()
    ma_co_hoi_gui = str(du_lieu.get("co_hoi") or "").strip()
    co_kenh_lien_he = bool(dt_chuan or em_chuan)

    if co_kenh_lien_he:
        ho_ten_raw = str(du_lieu.get("ho_ten") or "").strip() or "Khách đặt lịch"
        du_lieu_form = {
            "ho_ten": ho_ten_raw,
            "dien_thoai": du_lieu.get("dien_thoai"),
            "email": du_lieu.get("email"),
            "nhu_cau": str(du_lieu.get("ghi_chu") or "Đặt lịch gọi tư vấn").strip(),
            "dong_y_lien_he": True,
            "dong_y_marketing": False,
        }
        try:
            form._kiem_tra_dau_vao(du_lieu_form)
        except ValueError as exc:
            _tra_loi_http(str(exc), 400)

        ds_nguoi_cu = _tim_nguoi_trung(du_lieu_form)
        nguoi_da_co = ds_nguoi_cu[0] if ds_nguoi_cu else None

        if ma_nguoi_gui:
            nguoi_theo_ma = _doc_nguoi_db(ma_nguoi_gui)
            if nguoi_theo_ma is not None:
                kenh_hop_le = _chon_kenh_otp_cho_nguoi(
                    nguoi_theo_ma,
                    em_chuan=em_chuan,
                    dt_chuan=dt_chuan,
                )
                if not kenh_hop_le:
                    _tra_loi_http("Thông tin liên hệ không khớp với hồ sơ khách hàng", 400)
                if nguoi_da_co is None:
                    nguoi_da_co = nguoi_theo_ma
                    ds_nguoi_cu = [nguoi_theo_ma]
                elif str(nguoi_da_co.get("name") or "").strip() != ma_nguoi_gui:
                    _tra_loi_http("Thông tin liên hệ không khớp với hồ sơ khách hàng", 400)

        so_dong_y_cu = _lay_so_dong_y_hien_co(ds_nguoi_cu) if ds_nguoi_cu else []
        ma_ung_vien = str(nguoi_da_co.get("name") or "").strip() if nguoi_da_co else ""

        if ma_ung_vien and form.da_rut_dong_y(so_dong_y_cu, ma_ung_vien, "lien_he"):
            _tra_loi_http("Khách hàng đã rút đồng ý liên hệ, không thể đặt lịch gọi", 400)

        da_co_dong_y_lh = bool(ma_ung_vien and dong_y.hieu_luc(so_dong_y_cu, ma_ung_vien, "lien_he"))
        dong_y_gui = form._la_dong_y_true(du_lieu.get("dong_y_lien_he"))
        if not dong_y_gui and not da_co_dong_y_lh:
            _tra_loi_http("Khách hàng phải đồng ý liên hệ trước khi đặt lịch gọi", 400)

        luc_ghi = dong_y.bay_gio()
        so_luong_dy_cu = len(so_dong_y_cu)
        ket_qua_form = form.xu_ly(du_lieu_form, ds_nguoi_cu, so_dong_y_cu, luc_ghi, nguon_ghi)
        ma_nguoi = _luu_hoac_lay_nguoi(
            ket_qua_form["nguoi"],
            ds_nguoi_cu,
            du_lieu_goc=du_lieu_form,
        )

        if dong_y_gui and not da_co_dong_y_lh:
            for dy in ket_qua_form["so_dong_y"][so_luong_dy_cu:]:
                if dy.get("muc_dich") == "lien_he":
                    doc_dy = frappe.get_doc(
                        {
                            "doctype": "LX Dong Y",
                            "nguoi": ma_nguoi,
                            "muc_dich": "lien_he",
                            "dong_y": 1,
                            "luc": dy.get("luc") or luc_ghi,
                            "nguon": nguon_ghi,
                        }
                    )
                    doc_dy.flags.ignore_permissions = True
                    doc_dy.insert(ignore_permissions=True)
    else:
        if not ma_nguoi_gui:
            _tra_loi_http("Phải cung cấp mã khách hàng (nguoi) hoặc số điện thoại / email", 400)
        nguoi_db = _doc_nguoi_db(ma_nguoi_gui)
        if nguoi_db is None:
            db = getattr(frappe, "db", None)
            if db is not None and callable(getattr(db, "exists", None)):
                try:
                    ton_tai = db.exists("LX Nguoi", ma_nguoi_gui)
                except Exception:
                    ton_tai = True
                if ton_tai is False:
                    _tra_loi_http("Không tìm thấy hồ sơ khách hàng để đặt lịch", 404)
        so_dy = _lay_so_dong_y_hien_co(ma_nguoi_gui)
        if so_dy and form.da_rut_dong_y(so_dy, ma_nguoi_gui, "lien_he"):
            _tra_loi_http("Khách hàng đã rút đồng ý liên hệ, không thể đặt lịch gọi", 400)
        ma_nguoi = ma_nguoi_gui

    ch_hien_co = _tim_co_hoi_mo_cua_nguoi(ma_nguoi)
    ma_co_hoi = ma_co_hoi_gui or (str(ch_hien_co.get("name") or "").strip() if ch_hien_co else "")
    pt_co_hoi = str(ch_hien_co.get("phu_trach") or "").strip() if ch_hien_co else ""
    don_vi = str(ch_hien_co.get("don_vi") or "").strip() if ch_hien_co else ""

    if not don_vi:
        db = getattr(frappe, "db", None)
        if db is not None and callable(getattr(db, "get_value", None)):
            try:
                dv_ng = db.get_value("LX Nguoi", ma_nguoi, "don_vi")
                if dv_ng:
                    don_vi = str(dv_ng).strip()
            except Exception:
                pass

    if not ma_co_hoi and co_kenh_lien_he and callable(getattr(frappe, "get_doc", None)):
        try:
            doc_ch = frappe.get_doc(
                {
                    "doctype": "LX Co Hoi",
                    "nguoi": ma_nguoi,
                    "nhu_cau": str(du_lieu.get("ghi_chu") or "Đặt lịch gọi tư vấn").strip(),
                    "nguon": nguon_ghi,
                    "trang_thai": "moi",
                }
            )
            doc_ch.flags.ignore_permissions = True
            doc_ch.insert(ignore_permissions=True)
            ma_co_hoi = str(getattr(doc_ch, "name", "") or "").strip()
            if not pt_co_hoi and getattr(doc_ch, "phu_trach", None):
                pt_co_hoi = str(doc_ch.phu_trach).strip()
            if not don_vi and getattr(doc_ch, "don_vi", None):
                don_vi = str(doc_ch.don_vi).strip()
        except Exception as exc:
            logger.warning("Không tự tạo được LX Co Hoi khi đặt lịch: %s", type(exc).__name__)

    return ma_nguoi, ma_co_hoi, pt_co_hoi, don_vi


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=GIOI_HAN_MOI_PHUT, seconds=CUA_SO_GIAY)
def dat_lich_goi(
    nguoi: str | None = None,
    phu_trach: str | None = None,
    bat_dau: str | None = None,
    phut: int | str | None = dat_lich.PHUT_MAC_DINH,
    ghi_chu: str | None = None,
    ho_ten: str | None = None,
    dien_thoai: str | None = None,
    email: str | None = None,
    dong_y_lien_he: bool | int | str | None = None,
    co_hoi: str | None = None,
    **kwargs,
) -> dict:
    """Đặt lịch gọi tư vấn từ Trang BU vào lịch người phụ trách (chặn ngoài 8–18h giờ VN và chặn trùng giờ)."""
    _kiem_phuong_thuc_post()
    _kiem_module_crm_bat()

    tham_so = dict(kwargs)
    for k, v in (
        ("nguoi", nguoi),
        ("phu_trach", phu_trach),
        ("bat_dau", bat_dau),
        ("phut", phut),
        ("ghi_chu", ghi_chu),
        ("ho_ten", ho_ten),
        ("dien_thoai", dien_thoai),
        ("email", email),
        ("dong_y_lien_he", dong_y_lien_he),
        ("co_hoi", co_hoi),
    ):
        if v is not None:
            tham_so[k] = v

    try:
        du_lieu = _trich_du_lieu_request(tham_so)
    except ValueError as exc:
        _tra_loi_http(str(exc), 400)

    ghi_chu_raw = du_lieu.get("ghi_chu")
    if ghi_chu_raw is not None:
        if isinstance(ghi_chu_raw, bool) or not isinstance(ghi_chu_raw, str):
            _tra_loi_http("Ghi chú không hợp lệ", 400)
        if len(ghi_chu_raw.strip()) > DO_DAI_GHI_CHU_TOI_DA:
            _tra_loi_http(f"Ghi chú vượt quá {DO_DAI_GHI_CHU_TOI_DA} ký tự", 400)

    try:
        dt_bd, dt_kt, phut_int = dat_lich.kiem_gio_lam_viec(
            du_lieu.get("bat_dau"),
            du_lieu.get("phut", dat_lich.PHUT_MAC_DINH),
        )
    except ValueError as exc:
        _tra_loi_http(str(exc), 400)

    dt_chuan = gop_trung.chuan_hoa_dien_thoai(du_lieu.get("dien_thoai"))
    em_chuan = gop_trung.chuan_hoa_email(du_lieu.get("email"))
    ma_nguoi_gui = str(du_lieu.get("nguoi") or "").strip()

    _kiem_gioi_han_tan_suat_dat_lich(
        dt_chuan=dt_chuan,
        em_chuan=em_chuan,
        ma_nguoi=ma_nguoi_gui,
    )

    ten_site = str(getattr(getattr(frappe, "local", None), "site", "") or "").strip()
    nguon_ghi = f"trang-{ten_site}" if ten_site else "trang-bu"

    with _khoa_dat_lich(
        f"dt:{dt_chuan}" if dt_chuan else "",
        f"email:{em_chuan}" if em_chuan else "",
        f"nguoi:{ma_nguoi_gui}" if ma_nguoi_gui else "",
    ):
        ma_nguoi, ma_co_hoi, pt_co_hoi, don_vi = _giai_quyet_nguoi_va_co_hoi(
            du_lieu,
            dt_chuan=dt_chuan,
            em_chuan=em_chuan,
            nguon_ghi=nguon_ghi,
        )

    pt_yeu_cau = str(du_lieu.get("phu_trach") or "").strip()
    pt_chon = pt_yeu_cau or pt_co_hoi or _chon_phu_trach_tu_dong(don_vi)
    if not pt_chon:
        _tra_loi_http("Chưa có người phụ trách khả dụng để nhận lịch gọi", 400)
    pt_chon = _xac_minh_phu_trach_hop_le(pt_chon, don_vi)

    with _khoa_dat_lich(f"pt:{pt_chon}"):
        ds_lich_hien_co = _lay_ds_lich_phu_trach_db(pt_chon, khoa_dong=True)
        goi_dat = {
            "nguoi": ma_nguoi,
            "phu_trach": pt_chon,
            "bat_dau": dt_bd.strftime(dat_lich.DINH_DANG_TG),
            "phut": phut_int,
            "ghi_chu": str(du_lieu.get("ghi_chu") or "").strip(),
        }
        if ma_co_hoi:
            goi_dat["co_hoi"] = ma_co_hoi
        if don_vi:
            goi_dat["don_vi"] = don_vi

        try:
            ds_moi = dat_lich.dat_lich(ds_lich_hien_co, goi_dat)
        except ValueError as exc:
            _tra_loi_http(str(exc), 409)

        ban_ghi_moi = ds_moi[-1]
        du_lieu_doc = {
            "doctype": "LX Lich Goi",
            "nguoi": ban_ghi_moi["nguoi"],
            "phu_trach": ban_ghi_moi["phu_trach"],
            "bat_dau": ban_ghi_moi["bat_dau"],
            "ket_thuc": ban_ghi_moi["ket_thuc"],
            "phut": ban_ghi_moi["phut"],
            "trang_thai": ban_ghi_moi["trang_thai"],
            "ghi_chu": ban_ghi_moi.get("ghi_chu") or "",
            "nguon": nguon_ghi,
        }
        if ma_co_hoi:
            du_lieu_doc["co_hoi"] = ma_co_hoi
        if don_vi:
            du_lieu_doc["don_vi"] = don_vi

        doc_lich = frappe.get_doc(du_lieu_doc)
        doc_lich._ds_lich_hien_co = ds_lich_hien_co
        doc_lich.flags.ignore_permissions = True
        try:
            doc_lich.insert(ignore_permissions=True)
        except ValueError as exc:
            _tra_loi_http(str(exc), 409)

        ma_lich = str(getattr(doc_lich, "name", "") or "").strip()

    return {
        "ok": True,
        "lich": ma_lich,
        "nguoi": ma_nguoi,
        "co_hoi": ma_co_hoi,
        "phu_trach": pt_chon,
        "bat_dau": ban_ghi_moi["bat_dau"],
        "ket_thuc": ban_ghi_moi["ket_thuc"],
        "phut": ban_ghi_moi["phut"],
        "trang_thai": ban_ghi_moi["trang_thai"],
        "ban_cai": ten_site,
    }


@frappe.whitelist(methods=["GET", "POST"])
def viec_cho_lich_goi(phu_trach: str | None = None) -> list[dict]:
    """Trả danh sách lịch chờ gọi (`trang_thai == 'cho_goi'`) của người phụ trách, xếp `bat_dau` tăng dần."""
    _kiem_module_crm_bat()
    nguoi_dung = str(getattr(getattr(frappe, "session", None), "user", None) or "").strip()
    if not nguoi_dung or nguoi_dung == "Guest":
        _tra_loi_http("Cần đăng nhập để xem danh sách lịch chờ gọi", 403, getattr(frappe, "PermissionError", PermissionError))

    mien = la_user_mien(nguoi_dung)
    pt_loc = str(phu_trach).strip() if isinstance(phu_trach, str) and phu_trach.strip() else (None if mien else nguoi_dung)
    if not mien and pt_loc != nguoi_dung:
        _tra_loi_http("Chỉ được xem lịch chờ gọi của chính mình", 403, getattr(frappe, "PermissionError", PermissionError))

    bo_loc: dict[str, object] = {"trang_thai": "cho_goi"}
    if pt_loc:
        bo_loc["phu_trach"] = pt_loc
    if not mien:
        ds_don_vi = lay_don_vi_cua_user(nguoi_dung)
        if ds_don_vi:
            bo_loc["don_vi"] = ["in", ds_don_vi]

    ds_raw = frappe.get_all(
        "LX Lich Goi",
        filters=bo_loc,
        fields=[
            "name",
            "nguoi",
            "co_hoi",
            "phu_trach",
            "don_vi",
            "bat_dau",
            "ket_thuc",
            "phut",
            "trang_thai",
            "ghi_chu",
        ],
        order_by="bat_dau asc",
    )
    return dat_lich.viec_cho(list(ds_raw or []), phu_trach=pt_loc)
