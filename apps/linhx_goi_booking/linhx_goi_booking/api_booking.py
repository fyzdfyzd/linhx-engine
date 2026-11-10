"""API đặt lịch gọi tư vấn từ Trang BU (allow_guest=True, có giới hạn tần suất) và xem lịch chờ gọi của người phụ trách.

Thuần Python ở mức nạp file (không `import frappe` ở đầu file); chỉ giao tiếp với lõi qua `linhx_core.api`.

Ghi chú kiến trúc (G3):
- Theo luật 3 lớp (`_dot3.kiem_kien_truc`), app lớp `goi` (`linhx_goi_booking`) chỉ được phép import
  `linhx_core.api` và không được import trực tiếp `linhx_core.crm.*`.
- Đồng thời phạm vi vùng được sửa của phiếu G3 không bao gồm `apps/linhx_core/linhx_core/api.py`.
- Vì vậy các hàm nội bộ phục vụ kiểm quyền đơn vị, gộp trùng Người, đối chiếu kênh OTP/chống đoán hồ sơ
  và kiểm rút đồng ý (`_tim_nguoi_trung`, `_cac_dang_dien_thoai`, `_doc_nguoi_db`, `_nguoi_so_huu_kenh`,
  `_chon_kenh_otp_cho_nguoi`, `_lay_so_dong_y_hien_co`, `_da_rut_dong_y`, `_loc_ung_vien_crm`,
  `_la_user_mien`, `_lay_don_vi_cua_user`, `_chon_phu_trach_it_viec`) được giữ tại module này,
  uỷ quyền tối đa qua các hàm mặt cắt `linhx_core.api` và được kiểm thử đối chiếu trực tiếp (parity test)
  với bản gốc trong `linhx_core.crm` tại `test_goi_booking.py`.
"""
from __future__ import annotations

from contextlib import ExitStack, contextmanager
import ipaddress
import json
import logging
import threading
import time

from linhx_core.api import (
    chuan_hoa_dien_thoai,
    chuan_hoa_email,
    chuan_hoa_zalo,
    doctype_bi_an,
    ghi_dong_y,
    gop_nguoi,
    hieu_luc_dong_y,
    khoa_gop,
)
from linhx_goi_booking import dat_lich

logger = logging.getLogger(__name__)

GIOI_HAN_MOI_PHUT = 10
GIOI_HAN_THEO_KHOA_MOI_PHUT = 5
CUA_SO_GIAY = 60
GIOI_HAN_BODY_BYTES = 16 * 1024
TOI_DA_KHOA_BO_NHO = 1000
DO_DAI_GHI_CHU_TOI_DA = 2000
DO_DAI_TOI_DA_HO_TEN = 120
DO_DAI_TOI_DA_DIEN_THOAI = 20
DO_DAI_TOI_DA_EMAIL = 254
DO_DAI_TOI_DA_NHU_CAU = 2000
GIOI_HAN_TRUY_VAN_NGUOI = 20
TRUONG_HONEYPOT = ("website", "hp_url", "trap_field")
TRUONG_CAM_TU_CLIENT = ("nguon", "trang_thai", "don_vi", "ket_thuc")
USER_LOAI_TRU = ("Administrator", "Guest")
VAI_TRO_CRM = ("LX Nhan Vien", "Sales User", "Sales Manager", "CRM User")

_BO_DEM_LICH_DU_PHONG: dict[str, list[float]] = {}
_KHOA_GUARD = threading.Lock()
_KHOA_THEO_TEN: dict[str, threading.Lock] = {}


def _lay_frappe():
    """Nạp trễ `frappe` khi chạy trong môi trường Frappe; trả `None` khi chạy thuần Python."""
    try:
        import frappe
    except ImportError:
        return None
    return frappe


def _yeu_cau_frappe():
    frappe = _lay_frappe()
    if frappe is None:
        raise RuntimeError("Cần môi trường Frappe để gọi HTTP endpoint của linhx_goi_booking")
    return frappe


def _whitelist(*, allow_guest: bool = False, methods: list[str] | None = None):
    def _trang_tri(fn):
        frappe = _lay_frappe()
        if frappe is not None and callable(getattr(frappe, "whitelist", None)):
            if methods is not None:
                return frappe.whitelist(allow_guest=allow_guest, methods=methods)(fn)
            return frappe.whitelist(allow_guest=allow_guest)(fn)
        return fn

    return _trang_tri


def _rate_limit(*, limit: int = GIOI_HAN_MOI_PHUT, seconds: int = CUA_SO_GIAY):
    def _trang_tri(fn):
        try:
            from frappe.rate_limiter import rate_limit

            if callable(rate_limit):
                return rate_limit(limit=limit, seconds=seconds)(fn)
        except ImportError:
            pass
        return fn

    return _trang_tri


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
    frappe = _lay_frappe()
    if frappe is not None:
        if hasattr(frappe, "local") and isinstance(getattr(frappe.local, "response", None), dict):
            frappe.local.response["http_status_code"] = ma_http
        exc_cls = loai_loi or getattr(frappe, "ValidationError", ValueError)
        throw_fn = getattr(frappe, "throw", None)
        if callable(throw_fn):
            throw_fn(thong_diep, exc_cls)
    exc_cls = loai_loi if isinstance(loai_loi, type) and issubclass(loai_loi, BaseException) else ValueError
    raise exc_cls(thong_diep)


def _kiem_phuong_thuc_post() -> None:
    frappe = _lay_frappe()
    local_obj = getattr(frappe, "local", None) if frappe is not None else None
    req = getattr(local_obj, "request", None) or (getattr(frappe, "request", None) if frappe is not None else None)
    if req is not None:
        method = str(getattr(req, "method", "POST") or "POST").upper()
        if method != "POST":
            _tra_loi_http("Chỉ chấp nhận phương thức POST", 405)


def _kiem_module_crm_bat() -> None:
    frappe = _lay_frappe()
    if doctype_bi_an("LX Nguoi"):
        _tra_loi_http(
            "Module CRM đang tắt",
            403,
            getattr(frappe, "PermissionError", PermissionError) if frappe is not None else PermissionError,
        )


def _lay_cache():
    frappe = _lay_frappe()
    cache_fn = getattr(frappe, "cache", None) if frappe is not None else None
    if callable(cache_fn):
        try:
            return cache_fn()
        except Exception as exc:
            logger.warning("Không kết nối được frappe.cache(): %s", type(exc).__name__)
            return None
    return None


def _la_ip_proxy_tin_cay(ip_str: str) -> bool:
    frappe = _lay_frappe()
    conf = getattr(frappe, "conf", None) if frappe is not None else None
    ds_tin_cay = getattr(conf, "get", lambda *_: None)("trusted_proxies") if conf is not None else None
    if isinstance(ds_tin_cay, (list, tuple, set)) and ip_str in ds_tin_cay:
        return True
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        return bool(ip_obj.is_loopback or ip_obj.is_private)
    except ValueError:
        return False


def _lay_ip_khach() -> str:
    frappe = _lay_frappe()
    local_obj = getattr(frappe, "local", None) if frappe is not None else None
    ip_ket_noi = str(getattr(local_obj, "request_ip", None) or "127.0.0.1").strip()
    req = getattr(local_obj, "request", None) or (getattr(frappe, "request", None) if frappe is not None else None)
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
    frappe = _lay_frappe()
    local_obj = getattr(frappe, "local", None) if frappe is not None else None
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


def _la_user_mien(user: str | None = None) -> bool:
    frappe = _lay_frappe()
    if frappe is None:
        return False
    nguoi_dung = user or getattr(getattr(frappe, "session", None), "user", None)
    if not nguoi_dung or nguoi_dung == "Guest":
        return False
    if nguoi_dung == "Administrator":
        return True
    try:
        get_roles_fn = getattr(frappe, "get_roles", None)
        roles = set(get_roles_fn(nguoi_dung) or []) if callable(get_roles_fn) else set()
    except Exception:
        roles = set()
    return "System Manager" in roles


def _lay_don_vi_cua_user(user: str | None = None) -> list[str]:
    frappe = _lay_frappe()
    if frappe is None:
        return []
    nguoi_dung = user or getattr(getattr(frappe, "session", None), "user", None)
    if not nguoi_dung or nguoi_dung in ("Guest", "Administrator"):
        return []

    ds: list[str] = []
    try:
        db = getattr(frappe, "db", None)
        if db is not None and callable(getattr(db, "sql", None)):
            rows = db.sql(
                "SELECT for_value FROM `tabUser Permission` WHERE user=%s AND allow=%s",
                (nguoi_dung, "LX Don Vi"),
            )
            for r in rows or []:
                if r and r[0]:
                    ds.append(str(r[0]))
        elif callable(getattr(frappe, "get_all", None)):
            vals = frappe.get_all(
                "User Permission",
                filters={"user": nguoi_dung, "allow": "LX Don Vi"},
                pluck="for_value",
                ignore_permissions=True,
            )
            ds.extend(str(v) for v in (vals or []) if v)
    except Exception:
        pass

    kq: list[str] = []
    for dv in ds:
        chu = str(dv or "").strip()
        if chu and chu not in kq:
            kq.append(chu)
    return kq


def _loc_ung_vien_crm(frappe_mod, ds_user: list[str], don_vi: str | None) -> list[str]:
    if not ds_user or frappe_mod is None or not callable(getattr(frappe_mod, "get_all", None)):
        return []
    ket_qua = list(ds_user)
    try:
        co_vai_tro = set(
            frappe_mod.get_all(
                "Has Role",
                filters={
                    "parenttype": "User",
                    "parent": ["in", ket_qua],
                    "role": ["in", list(VAI_TRO_CRM)],
                },
                pluck="parent",
            )
            or []
        )
    except Exception:
        return []
    ket_qua = [u for u in ket_qua if u in co_vai_tro]
    if not ket_qua:
        return []

    if don_vi:
        try:
            co_don_vi = set(
                frappe_mod.get_all(
                    "User Permission",
                    filters={
                        "user": ["in", ket_qua],
                        "allow": "LX Don Vi",
                        "for_value": don_vi,
                    },
                    pluck="user",
                )
                or []
            )
        except Exception:
            return []
        ket_qua = [u for u in ket_qua if u in co_don_vi]
    return ket_qua


def _chon_phu_trach_it_viec(ds_phu_trach: list[str], ds_co_hoi_mo: list[dict]) -> str:
    ung_vien = [str(u).strip() for u in (ds_phu_trach or []) if str(u or "").strip()]
    if not ung_vien:
        return ""
    dem: dict[str, int] = {u: 0 for u in ung_vien}
    for ch in ds_co_hoi_mo or []:
        if not isinstance(ch, dict):
            continue
        if ch.get("trang_thai") in ("thang", "thua"):
            continue
        pt = str(ch.get("phu_trach") or "").strip()
        if pt in dem:
            dem[pt] += 1
    return min(ung_vien, key=lambda u: dem[u])


def _lay_ds_lich_phu_trach_db(phu_trach: str, *, khoa_dong: bool = False) -> list[dict]:
    pt = str(phu_trach or "").strip()
    if not pt:
        return []
    frappe = _lay_frappe()
    if frappe is None:
        return []

    db = getattr(frappe, "db", None)
    if db is not None and khoa_dong and callable(getattr(db, "sql", None)):
        try:
            rows = db.sql(
                """
                SELECT name, nguoi, phu_trach, bat_dau, ket_thuc, phut, trang_thai, ghi_chu, co_hoi, don_vi
                FROM `tabLX Lich Goi`
                WHERE phu_trach = %s AND trang_thai != 'huy'
                ORDER BY bat_dau ASC
                FOR UPDATE
                """,
                (pt,),
                as_dict=True,
            )
            if isinstance(rows, (list, tuple)):
                return [dict(r) for r in rows if isinstance(r, dict)]
        except Exception as exc:
            logger.warning("Lỗi truy vấn FOR UPDATE LX Lich Goi: %s", type(exc).__name__)

    get_all_fn = getattr(frappe, "get_all", None)
    if callable(get_all_fn):
        try:
            ds = get_all_fn(
                "LX Lich Goi",
                filters={"phu_trach": pt, "trang_thai": ["!=", "huy"]},
                fields=[
                    "name",
                    "nguoi",
                    "phu_trach",
                    "bat_dau",
                    "ket_thuc",
                    "phut",
                    "trang_thai",
                    "ghi_chu",
                    "co_hoi",
                    "don_vi",
                ],
                order_by="bat_dau asc",
            )
            if isinstance(ds, (list, tuple)):
                return [dict(r) for r in ds if isinstance(r, dict)]
        except Exception as exc:
            logger.warning("Lỗi get_all LX Lich Goi: %s", type(exc).__name__)
    return []


def _tim_co_hoi_mo_cua_nguoi(ma_nguoi: str) -> dict | None:
    ng = str(ma_nguoi or "").strip()
    frappe = _lay_frappe()
    if not ng or frappe is None or not callable(getattr(frappe, "get_all", None)):
        return None
    try:
        ds = frappe.get_all(
            "LX Co Hoi",
            filters={"nguoi": ng, "trang_thai": ["in", ["moi", "dang_lam"]]},
            fields=["name", "nguoi", "phu_trach", "don_vi", "trang_thai", "creation"],
            order_by="creation desc",
            limit=5,
        )
        for item in ds or []:
            if isinstance(item, dict) and str(item.get("nguoi") or "").strip() == ng:
                return item
    except Exception as exc:
        logger.warning("Không truy vấn được LX Co Hoi của %s: %s", _che_kenh(ng), type(exc).__name__)
    return None


def _xac_minh_co_hoi_cua_nguoi(ma_co_hoi: str, ma_nguoi: str) -> dict | None:
    """Xác nhận `LX Co Hoi` tồn tại và có `nguoi == ma_nguoi`; nếu không khớp thì bỏ qua."""
    ch = str(ma_co_hoi or "").strip()
    ng = str(ma_nguoi or "").strip()
    if not ch or not ng:
        return None

    frappe = _lay_frappe()
    if frappe is None:
        return None
    db = getattr(frappe, "db", None)
    if db is not None and callable(getattr(db, "get_value", None)):
        try:
            tt_ch = db.get_value(
                "LX Co Hoi",
                ch,
                ["name", "nguoi", "phu_trach", "don_vi", "trang_thai"],
                as_dict=True,
            )
            if isinstance(tt_ch, dict) and tt_ch:
                if str(tt_ch.get("nguoi") or "").strip() == ng:
                    return tt_ch
                return None
        except Exception as exc:
            logger.warning("Không đọc được LX Co Hoi %s từ DB: %s", _che_kenh(ch), type(exc).__name__)

    if callable(getattr(frappe, "get_all", None)):
        try:
            ds = frappe.get_all(
                "LX Co Hoi",
                filters={"name": ch, "nguoi": ng},
                fields=["name", "nguoi", "phu_trach", "don_vi", "trang_thai", "creation"],
                limit=5,
            )
            for item in ds or []:
                if (
                    isinstance(item, dict)
                    and str(item.get("name") or "").strip() == ch
                    and str(item.get("nguoi") or "").strip() == ng
                ):
                    return item
        except Exception as exc:
            logger.warning("Không truy vấn được LX Co Hoi %s: %s", _che_kenh(ch), type(exc).__name__)
    return None


def _chon_phu_trach_tu_dong(don_vi: str | None = None) -> str:
    frappe = _lay_frappe()
    if frappe is None or not callable(getattr(frappe, "get_all", None)):
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
    if not ung_vien:
        return ""

    try:
        ds_mo = list(
            frappe.get_all(
                "LX Co Hoi",
                filters={"trang_thai": ["in", ["moi", "dang_lam"]]},
                fields=["name", "phu_trach", "trang_thai"],
            )
            or []
        )
    except Exception as exc:
        logger.warning("Không truy vấn được danh sách LX Co Hoi đang mở: %s", type(exc).__name__)
        return ""
    return _chon_phu_trach_it_viec(ung_vien, ds_mo)


def _xac_minh_phu_trach_hop_le(phu_trach: str, don_vi: str | None = None) -> tuple[str, str]:
    pt = str(phu_trach or "").strip()
    dv_chon = str(don_vi or "").strip()
    if not pt:
        return "", dv_chon
    if pt in USER_LOAI_TRU:
        _tra_loi_http("Người phụ trách không hợp lệ", 400)

    frappe = _lay_frappe()
    db = getattr(frappe, "db", None) if frappe is not None else None
    if db is not None and callable(getattr(db, "get_value", None)):
        try:
            tt_user = db.get_value("User", pt, ["name", "enabled", "user_type"], as_dict=True)
        except Exception as exc:
            logger.warning("Không đọc được thông tin User %s: %s", _che_kenh(pt), type(exc).__name__)
            tt_user = None
        if not isinstance(tt_user, dict) or not tt_user:
            _tra_loi_http("Người phụ trách không tồn tại", 400)
        if int(tt_user.get("enabled", 1) or 0) != 1:
            _tra_loi_http("Người phụ trách đang ngừng hoạt động", 400)
        if tt_user.get("user_type") and tt_user.get("user_type") != "System User":
            _tra_loi_http("Người phụ trách phải là nhân sự hệ thống", 400)

    if not _la_user_mien(pt):
        dv_user = _lay_don_vi_cua_user(pt)
        perm_cls = getattr(frappe, "PermissionError", PermissionError) if frappe is not None else PermissionError
        if not dv_user:
            _tra_loi_http(
                "Người phụ trách chưa được phân quyền đơn vị",
                403,
                perm_cls,
            )
        if dv_chon:
            if dv_chon not in dv_user:
                _tra_loi_http(
                    "Người phụ trách không thuộc đơn vị của khách hàng",
                    403,
                    perm_cls,
                )
        else:
            dv_chon = dv_user[0]

    return pt, dv_chon


def _la_dong_y_true(gia_tri: object) -> bool:
    if isinstance(gia_tri, bool):
        return gia_tri
    if isinstance(gia_tri, int):
        return gia_tri == 1
    if isinstance(gia_tri, str):
        return gia_tri.strip().lower() in ("1", "true", "yes", "on")
    return False


def _kiem_tra_dau_vao(du_lieu: dict) -> tuple[str, str, str, str]:
    for tr_hp in TRUONG_HONEYPOT:
        if str(du_lieu.get(tr_hp) or "").strip():
            raise ValueError("Phát hiện gửi tự động không hợp lệ")

    ho_ten = str(du_lieu.get("ho_ten") or "").strip()
    dien_thoai = str(du_lieu.get("dien_thoai") or "").strip()
    email = str(du_lieu.get("email") or "").strip()
    nhu_cau = str(du_lieu.get("nhu_cau") or "").strip()

    if len(ho_ten) > DO_DAI_TOI_DA_HO_TEN:
        raise ValueError(f"Họ tên vượt quá độ dài tối đa ({DO_DAI_TOI_DA_HO_TEN} ký tự)")
    if len(dien_thoai) > DO_DAI_TOI_DA_DIEN_THOAI:
        raise ValueError(f"Số điện thoại vượt quá độ dài tối đa ({DO_DAI_TOI_DA_DIEN_THOAI} ký tự)")
    if len(email) > DO_DAI_TOI_DA_EMAIL:
        raise ValueError(f"Email vượt quá độ dài tối đa ({DO_DAI_TOI_DA_EMAIL} ký tự)")
    if len(nhu_cau) > DO_DAI_TOI_DA_NHU_CAU:
        raise ValueError(f"Nhu cầu vượt quá độ dài tối đa ({DO_DAI_TOI_DA_NHU_CAU} ký tự)")

    return ho_ten, dien_thoai, email, nhu_cau


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


def _cac_dang_dien_thoai(dien_thoai_raw: str, dt_chuan: str) -> list[str]:
    """Sinh các dạng biểu diễn SĐT (đồng bộ với `linhx_core.crm.api_form._cac_dang_dien_thoai`)."""
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
    """Truy vấn các bản ghi LX Nguoi khớp khoá liên hệ chuẩn hoá (đồng bộ với `linhx_core.crm.api_form._tim_nguoi_trung`)."""
    if not isinstance(du_lieu, dict):
        return []
    frappe = _lay_frappe()
    if frappe is None or not callable(getattr(frappe, "get_all", None)):
        return []

    dt_raw = str(du_lieu.get("dien_thoai") or "").strip()
    em_raw = str(du_lieu.get("email") or "").strip()
    zl_raw = str(du_lieu.get("zalo") or "").strip()
    dt_chuan = chuan_hoa_dien_thoai(dt_raw)
    em_chuan = chuan_hoa_email(em_raw)
    zl_chuan = chuan_hoa_zalo(zl_raw)
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
            khop = khoa_gop(u) & khoa_tim
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
                if khoa_gop(u) & khoa_tim:
                    ket_qua.append(_chuan_ban_ghi_nguoi(u))
                    co_them_phu = True
                    if ten_u:
                        da_co_ten.add(ten_u)
        if co_them_phu:
            ket_qua.sort(key=lambda d: str(d.get("creation") or ""))
    return ket_qua


def _doc_nguoi_db(ma_nguoi: str) -> dict | None:
    ma = str(ma_nguoi or "").strip()
    frappe = _lay_frappe()
    if not ma or frappe is None:
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
    if callable(getattr(frappe, "get_all", None)):
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


def _chuan_kenh(kenh_raw: object) -> str:
    """Chuẩn hoá kênh xác nhận (đồng bộ với `linhx_core.crm.xac_minh_marketing._chuan_kenh`)."""
    raw = str(kenh_raw or "").strip()
    if not raw:
        return ""
    if "@" in raw:
        return chuan_hoa_email(raw) or raw.lower()
    dt = chuan_hoa_dien_thoai(raw)
    if dt:
        return dt
    return raw.lower()


def _nguoi_so_huu_kenh(nguoi_dict: dict | None, kenh_chuan: str) -> bool:
    """Kiểm tra hồ sơ LX Nguoi có thực sự sở hữu kênh liên hệ `kenh_chuan` hay không
    (đồng bộ với `linhx_core.crm.api_form._nguoi_so_huu_kenh`).
    """
    if not isinstance(nguoi_dict, dict):
        return False
    kenh = _chuan_kenh(kenh_chuan)
    if not kenh:
        return False
    em_db = chuan_hoa_email(nguoi_dict.get("email"))
    dt_db = chuan_hoa_dien_thoai(nguoi_dict.get("dien_thoai"))
    zl_db = chuan_hoa_zalo(nguoi_dict.get("zalo"))
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
    """Chọn kênh xác minh cho `nguoi_db`: chỉ chấp nhận khi mọi kênh liên hệ gửi lên đều khớp
    đúng kênh đã lưu trên `nguoi_db` (chống kẻ tấn công ghép kênh của nạn nhân với kênh lạ).
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


def _lay_so_dong_y_hien_co(ds_nguoi_cu: list[dict] | str) -> list[dict]:
    """Đọc toàn bộ sổ đồng ý của các bản ghi LX Nguoi khớp khoá liên hệ
    (đồng bộ với `linhx_core.crm.api_form._lay_so_dong_y_hien_co`).
    """
    frappe = _lay_frappe()
    if frappe is None or not callable(getattr(frappe, "get_all", None)):
        return []
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


def _da_rut_dong_y(
    so_dong_y: list[dict],
    dinh_danh: str | list[str] | set[str],
    muc_dich: str,
) -> bool:
    if not so_dong_y:
        return False
    if isinstance(dinh_danh, str):
        tap_ma = {dinh_danh.strip()} if dinh_danh.strip() else set()
    else:
        tap_ma = {str(x).strip() for x in (dinh_danh or []) if str(x or "").strip()}
    if not tap_ma:
        return False

    ma_dai_dien = next(iter(tap_ma))
    so_quy_doi: list[dict] = []
    co_dong = False
    for d in so_dong_y:
        if not isinstance(d, dict):
            continue
        ng_raw = d.get("nguoi")
        ma_d = str(ng_raw.get("name") or ng_raw.get("nguoi") or "").strip() if isinstance(ng_raw, dict) else str(ng_raw or "").strip()
        if ma_d in tap_ma:
            if str(d.get("trang_thai") or "").strip() == "cho_xac_minh":
                continue
            if d.get("muc_dich") == muc_dich:
                co_dong = True
            ban_sao = dict(d)
            ban_sao["nguoi"] = ma_dai_dien
            so_quy_doi.append(ban_sao)

    if not co_dong:
        return False
    return not hieu_luc_dong_y(so_quy_doi, ma_dai_dien, muc_dich)


def _tim_nguoi_da_co(nguoi_dict: dict, ds_nguoi_cu: list[dict]) -> dict | None:
    khoa_nguoi = khoa_gop(nguoi_dict)
    ten_nguoi = str(nguoi_dict.get("name") or "").strip()
    for cu in ds_nguoi_cu:
        if not isinstance(cu, dict):
            continue
        ten_cu = str(cu.get("name") or "").strip()
        if not ten_cu:
            continue
        if ten_cu == ten_nguoi or (khoa_nguoi and (khoa_gop(cu) & khoa_nguoi)):
            return cu
    return None


def _luu_hoac_lay_nguoi(
    nguoi_dict: dict,
    ds_nguoi_cu: list[dict],
    *,
    du_lieu_goc: dict | None = None,
) -> str:
    nguoi_da_co = _tim_nguoi_da_co(nguoi_dict, ds_nguoi_cu)
    if nguoi_da_co is not None:
        return str(nguoi_da_co["name"]).strip()

    frappe = _yeu_cau_frappe()
    em_luu = chuan_hoa_email(nguoi_dict.get("email")) or nguoi_dict.get("email")
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
    if hasattr(doc_nguoi, "flags"):
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


def _giai_quyet_nguoi_va_co_hoi(
    du_lieu: dict,
    *,
    dt_chuan: str,
    em_chuan: str,
    nguon_ghi: str,
) -> tuple[str, str, str, str]:
    """Xác định `(ma_nguoi, ma_co_hoi, phu_trach_co_hoi, don_vi)` an toàn từ thông tin đặt lịch."""
    frappe = _yeu_cau_frappe()
    ma_nguoi_gui = str(du_lieu.get("nguoi") or "").strip()
    ma_co_hoi_gui = str(du_lieu.get("co_hoi") or "").strip()
    co_kenh_lien_he = bool(dt_chuan or em_chuan)

    if not co_kenh_lien_he:
        _tra_loi_http(
            "Phải cung cấp số điện thoại hoặc email hợp lệ khớp hồ sơ để đặt lịch gọi",
            400,
        )

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
        ho_ten_sach, dien_thoai_sach, email_sach, _ = _kiem_tra_dau_vao(du_lieu_form)
    except ValueError as exc:
        _tra_loi_http(str(exc), 400)

    ds_nguoi_cu = _tim_nguoi_trung(du_lieu_form)
    nguoi_da_co = ds_nguoi_cu[0] if ds_nguoi_cu else None

    if ma_nguoi_gui:
        nguoi_theo_ma = _doc_nguoi_db(ma_nguoi_gui)
        if nguoi_theo_ma is None:
            _tra_loi_http("Thông tin liên hệ không khớp với hồ sơ khách hàng", 400)
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

    if ma_ung_vien and _da_rut_dong_y(so_dong_y_cu, ma_ung_vien, "lien_he"):
        _tra_loi_http("Khách hàng đã rút đồng ý liên hệ, không thể đặt lịch gọi", 400)

    da_co_dong_y_lh = bool(ma_ung_vien and hieu_luc_dong_y(so_dong_y_cu, ma_ung_vien, "lien_he"))
    dong_y_gui = _la_dong_y_true(du_lieu.get("dong_y_lien_he"))
    if not dong_y_gui and not da_co_dong_y_lh:
        _tra_loi_http("Khách hàng phải đồng ý liên hệ trước khi đặt lịch gọi", 400)

    luc_ghi = dat_lich.bay_gio()
    ban_moi_ng = {
        "ho_ten": ho_ten_sach,
        "dien_thoai": dien_thoai_sach,
        "email": email_sach,
    }
    khoa_moi = khoa_gop(ban_moi_ng)
    ds_nguoi_moi = gop_nguoi(ds_nguoi_cu or [], ban_moi_ng)
    nguoi_ket_qua = None
    for muc in ds_nguoi_moi:
        if isinstance(muc, dict) and (khoa_gop(muc) & khoa_moi):
            nguoi_ket_qua = muc
            break
    if nguoi_ket_qua is None:
        nguoi_ket_qua = ds_nguoi_moi[-1]

    ma_nguoi = _luu_hoac_lay_nguoi(
        nguoi_ket_qua,
        ds_nguoi_cu,
        du_lieu_goc=du_lieu_form,
    )

    if dong_y_gui and not da_co_dong_y_lh:
        so_tam = [dict(d) for d in so_dong_y_cu]
        dong_dy_moi = ghi_dong_y(
            ma_nguoi,
            "lien_he",
            True,
            luc_ghi,
            nguon_ghi,
            kho=so_tam,
        )
        doc_dy = frappe.get_doc(
            {
                "doctype": "LX Dong Y",
                "nguoi": ma_nguoi,
                "muc_dich": "lien_he",
                "dong_y": 1,
                "luc": dong_dy_moi.get("luc") or luc_ghi,
                "nguon": nguon_ghi,
            }
        )
        if hasattr(doc_dy, "flags"):
            doc_dy.flags.ignore_permissions = True
        doc_dy.insert(ignore_permissions=True)

    ch_chon = _xac_minh_co_hoi_cua_nguoi(ma_co_hoi_gui, ma_nguoi) if ma_co_hoi_gui else None
    if ch_chon is None:
        ch_chon = _tim_co_hoi_mo_cua_nguoi(ma_nguoi)

    ma_co_hoi = str(ch_chon.get("name") or "").strip() if ch_chon else ""
    pt_co_hoi = str(ch_chon.get("phu_trach") or "").strip() if ch_chon else ""
    don_vi = str(ch_chon.get("don_vi") or "").strip() if ch_chon else ""

    if not don_vi:
        db = getattr(frappe, "db", None)
        if db is not None and callable(getattr(db, "get_value", None)):
            try:
                dv_ng = db.get_value("LX Nguoi", ma_nguoi, "don_vi")
                if dv_ng:
                    don_vi = str(dv_ng).strip()
            except Exception as exc:
                logger.warning("Không đọc được don_vi của LX Nguoi %s: %s", _che_kenh(ma_nguoi), type(exc).__name__)

    if not ma_co_hoi and callable(getattr(frappe, "get_doc", None)):
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
            if hasattr(doc_ch, "flags"):
                doc_ch.flags.ignore_permissions = True
            doc_ch.insert(ignore_permissions=True)
            ma_co_hoi = str(getattr(doc_ch, "name", "") or "").strip()
            if not pt_co_hoi and getattr(doc_ch, "phu_trach", None):
                pt_co_hoi = str(doc_ch.phu_trach).strip()
            if not don_vi and getattr(doc_ch, "don_vi", None):
                don_vi = str(doc_ch.don_vi).strip()
        except Exception as exc:
            logger.warning("Không tự tạo được LX Co Hoi khi đặt lịch: %s", type(exc).__name__)
            _tra_loi_http("Không tạo được cơ hội tư vấn cho lịch gọi", 500)

    return ma_nguoi, ma_co_hoi, pt_co_hoi, don_vi


@_whitelist(allow_guest=True, methods=["POST"])
@_rate_limit(limit=GIOI_HAN_MOI_PHUT, seconds=CUA_SO_GIAY)
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
    frappe = _yeu_cau_frappe()
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

    dt_chuan = chuan_hoa_dien_thoai(du_lieu.get("dien_thoai"))
    em_chuan = chuan_hoa_email(du_lieu.get("email"))
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
    pt_hop_le_tu_khach = pt_yeu_cau if (pt_yeu_cau and pt_co_hoi and pt_yeu_cau == pt_co_hoi) else ""
    pt_chon = pt_hop_le_tu_khach or pt_co_hoi or _chon_phu_trach_tu_dong(don_vi)
    if not pt_chon:
        _tra_loi_http("Chưa có người phụ trách khả dụng để nhận lịch gọi", 400)
    pt_chon, don_vi = _xac_minh_phu_trach_hop_le(pt_chon, don_vi)

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
        if hasattr(doc_lich, "flags"):
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


@_whitelist(methods=["GET", "POST"])
def viec_cho_lich_goi(phu_trach: str | None = None) -> list[dict]:
    """Trả danh sách lịch chờ gọi (`trang_thai == 'cho_goi'`) của người phụ trách, xếp `bat_dau` tăng dần."""
    frappe = _yeu_cau_frappe()
    _kiem_module_crm_bat()
    nguoi_dung = str(getattr(getattr(frappe, "session", None), "user", None) or "").strip()
    perm_cls = getattr(frappe, "PermissionError", PermissionError)
    if not nguoi_dung or nguoi_dung == "Guest":
        _tra_loi_http("Cần đăng nhập để xem danh sách lịch chờ gọi", 403, perm_cls)

    mien = _la_user_mien(nguoi_dung)
    pt_loc = str(phu_trach).strip() if isinstance(phu_trach, str) and phu_trach.strip() else (None if mien else nguoi_dung)
    if not mien and pt_loc != nguoi_dung:
        _tra_loi_http("Chỉ được xem lịch chờ gọi của chính mình", 403, perm_cls)

    bo_loc: dict[str, object] = {"trang_thai": "cho_goi"}
    if pt_loc:
        bo_loc["phu_trach"] = pt_loc
    if not mien:
        ds_don_vi = _lay_don_vi_cua_user(nguoi_dung)
        if not ds_don_vi:
            return []
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
