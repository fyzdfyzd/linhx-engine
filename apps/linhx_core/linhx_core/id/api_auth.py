"""Endpoint xác thực OAuth cho LINHX Core (Google & Zalo callback)."""
from __future__ import annotations

from contextlib import ExitStack, contextmanager
from datetime import datetime, timezone
import json
import logging
import threading
import urllib.parse
import urllib.request

import frappe
from frappe.rate_limiter import rate_limit

from linhx_core import co_module
from linhx_core.crm import gop_trung
from linhx_core.id import google_oauth, zalo_oauth

logger = logging.getLogger(__name__)

GIOI_HAN_CALLBACK_MOI_PHUT = 20
CUA_SO_GIAY = 60
GIOI_HAN_TRUY_VAN_NGUOI = 20
TOI_DA_KHOA_BO_NHO = 1000
KHOA_STATE_GOOGLE_SESSION = "oauth_state_google"
KHOA_STATE_ZALO_SESSION = "oauth_state_zalo"

GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"
ZALO_TOKEN_ENDPOINT = "https://oauth.zaloapp.com/v4/access_token"
ZALO_USERINFO_ENDPOINT = "https://graph.zalo.me/v2.0/me?fields=id,name,phone"

_KHOA_GUARD = threading.Lock()
_KHOA_THEO_EMAIL: dict[str, threading.Lock] = {}


def _bay_gio() -> str:
    if hasattr(frappe, "utils") and callable(getattr(frappe.utils, "now", None)):
        return str(frappe.utils.now())
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _tra_loi_http(thong_diep: str, ma_http: int, loai_loi=None) -> None:
    if hasattr(frappe, "local") and isinstance(getattr(frappe.local, "response", None), dict):
        frappe.local.response["http_status_code"] = ma_http
    exc_cls = loai_loi or getattr(frappe, "ValidationError", ValueError)
    frappe.throw(thong_diep, exc_cls)


def _kiem_module_crm_bat() -> None:
    cau_hinh = co_module._doc_cau_hinh_frappe()
    if co_module.doctype_bi_an("LX Nguoi", cau_hinh):
        _tra_loi_http("Module CRM đang tắt", 403, getattr(frappe, "PermissionError", PermissionError))


def _co_request_http() -> bool:
    local_obj = getattr(frappe, "local", None)
    return getattr(local_obj, "request", None) is not None


def _lay_cache():
    cache_fn = getattr(frappe, "cache", None)
    if callable(cache_fn):
        try:
            return cache_fn()
        except Exception as exc:
            logger.warning("Không kết nối được frappe.cache(): %s", exc)
            return None
    if cache_fn is not None and hasattr(cache_fn, "get_value"):
        return cache_fn
    return None


def _lay_lock_bo_nho(khoa_lock: str) -> threading.Lock:
    with _KHOA_GUARD:
        lock_obj = _KHOA_THEO_EMAIL.get(khoa_lock)
        if lock_obj is None:
            if len(_KHOA_THEO_EMAIL) >= TOI_DA_KHOA_BO_NHO:
                for k_cu, lk_cu in list(_KHOA_THEO_EMAIL.items()):
                    if not lk_cu.locked():
                        _KHOA_THEO_EMAIL.pop(k_cu, None)
                        break
            lock_obj = threading.Lock()
            _KHOA_THEO_EMAIL[khoa_lock] = lock_obj
        return lock_obj


@contextmanager
def _khoa_theo_email(email_chuan: str):
    khoa_lock = f"linhx_oauth_lock:email:{email_chuan}"
    cache = _lay_cache()
    with ExitStack() as stack:
        stack.enter_context(_lay_lock_bo_nho(khoa_lock))
        if cache is not None and hasattr(cache, "lock"):
            try:
                stack.enter_context(cache.lock(khoa_lock, timeout=15))
            except Exception as exc:
                logger.warning("Không lấy được khoá cache %s: %s", khoa_lock, exc)
        yield


def _doc_va_tieu_thu_state_phien(khoa_session: str) -> str:
    """Đọc và xoá ngay state OAuth khỏi phiên máy chủ để chống phát lại (replay)."""
    session_obj = getattr(frappe, "session", None)
    session_data = getattr(session_obj, "data", None)
    if isinstance(session_data, dict) and khoa_session in session_data:
        gia_tri = session_data.pop(khoa_session, None)
        if isinstance(gia_tri, str) and gia_tri.strip():
            return gia_tri

    sid = str(getattr(session_obj, "sid", "") or "").strip()
    cache = _lay_cache()
    if sid and cache is not None and hasattr(cache, "get_value"):
        khoa_cache = f"linhx_oauth_state:{khoa_session}:{sid}"
        try:
            gia_tri = cache.get_value(khoa_cache)
            if hasattr(cache, "delete_value"):
                cache.delete_value(khoa_cache)
            if isinstance(gia_tri, str) and gia_tri.strip():
                return gia_tri
        except Exception as exc:
            logger.warning("Không đọc được state OAuth từ cache: %s", exc)
    return ""


def _doi_code_lay_ho_so_google(code: str) -> dict:
    """Đổi authorization code lấy hồ sơ người dùng đã xác thực từ Google OIDC."""
    if not isinstance(code, str) or not code.strip():
        raise ValueError("Thiếu mã uỷ quyền OAuth (code)")

    conf = getattr(frappe, "conf", None) or {}
    client_id = str(conf.get("google_oauth_client_id") or "").strip()
    client_secret = str(conf.get("google_oauth_client_secret") or "").strip()
    redirect_uri = str(conf.get("google_oauth_redirect_uri") or "").strip()
    if not client_id or not client_secret or not redirect_uri:
        raise ValueError("Chưa cấu hình Google OAuth trên máy chủ")

    form_body = urllib.parse.urlencode(
        {
            "code": code.strip(),
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
    ).encode("utf-8")

    req_tok = urllib.request.Request(
        GOOGLE_TOKEN_ENDPOINT,
        data=form_body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req_tok, timeout=10) as resp:
            du_lieu_tok = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        raise ValueError("Không đổi được mã uỷ quyền Google OAuth") from exc

    ma_truy_cap = str(du_lieu_tok.get("access_token") or "").strip()
    if not ma_truy_cap:
        raise ValueError("Phản hồi Google OAuth thiếu access_token")

    req_info = urllib.request.Request(
        GOOGLE_USERINFO_ENDPOINT,
        headers={"Authorization": f"Bearer {ma_truy_cap}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req_info, timeout=10) as resp:
            ho_so = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        raise ValueError("Không lấy được hồ sơ người dùng từ Google") from exc

    if not isinstance(ho_so, dict):
        raise ValueError("Hồ sơ Google trả về không hợp lệ")
    return ho_so


def _tim_nguoi_theo_email(email_chuan: str) -> list[dict]:
    """Tìm các bản ghi LX Nguoi khớp email không phân biệt hoa thường."""
    if not email_chuan:
        return []
    ds_ung_vien = frappe.get_all(
        "LX Nguoi",
        fields=["name", "ho_ten", "dien_thoai", "email", "zalo", "don_vi", "to_chuc", "nguon", "tang_pheu"],
        or_filters=[
            ["LX Nguoi", "email", "=", email_chuan],
            ["LX Nguoi", "email", "like", email_chuan],
        ],
        order_by="creation asc",
        limit=GIOI_HAN_TRUY_VAN_NGUOI,
    )
    khoa_can = f"email:{email_chuan}"
    ket_qua: list[dict] = []
    for u in ds_ung_vien or []:
        if isinstance(u, dict) and khoa_can in gop_trung.khoa_gop(u):
            ket_qua.append(dict(u))
    return ket_qua


def _luu_nguoi_sau_gop(nguoi_ket_qua: dict, da_gop: bool, email_chuan: str) -> str:
    """Cập nhật bản ghi LX Nguoi đã có (chỉ bù trường trống) hoặc tạo mới trong DB."""
    if da_gop and nguoi_ket_qua.get("name"):
        ten_nguoi = str(nguoi_ket_qua["name"]).strip()
        doc_nguoi = frappe.get_doc("LX Nguoi", ten_nguoi)
        co_thay_doi = False
        if not getattr(doc_nguoi, "ho_ten", None) and nguoi_ket_qua.get("ho_ten"):
            doc_nguoi.ho_ten = nguoi_ket_qua["ho_ten"]
            co_thay_doi = True
        if not getattr(doc_nguoi, "email", None) and email_chuan:
            doc_nguoi.email = email_chuan
            co_thay_doi = True
        if co_thay_doi:
            doc_nguoi.flags.ignore_permissions = True
            doc_nguoi.save(ignore_permissions=True)
        return ten_nguoi

    doc_moi = frappe.get_doc(
        {
            "doctype": "LX Nguoi",
            "ho_ten": nguoi_ket_qua.get("ho_ten") or email_chuan.split("@")[0],
            "email": email_chuan,
            "nguon": google_oauth.KENH_GOOGLE,
        }
    )
    doc_moi.flags.ignore_permissions = True
    doc_moi.insert(ignore_permissions=True)
    return str(doc_moi.name)


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=GIOI_HAN_CALLBACK_MOI_PHUT, seconds=CUA_SO_GIAY)
def google_callback(
    state: str | None = None,
    code: str | None = None,
    **kwargs,
) -> dict:
    """Xử lý callback đăng nhập Google OAuth và gộp hồ sơ vào `LX Nguoi`."""
    _kiem_module_crm_bat()

    state_gui = state if state is not None else kwargs.get("state_gui")
    if not isinstance(state_gui, str):
        state_gui = ""

    la_http = _co_request_http()
    state_phien = _doc_va_tieu_thu_state_phien(KHOA_STATE_GOOGLE_SESSION)
    if not state_phien and not la_http and isinstance(kwargs.get("state_phien"), str):
        state_phien = kwargs["state_phien"]

    try:
        google_oauth.kiem_state_oauth(state_gui, state_phien)
        if not la_http and isinstance(kwargs.get("ho_so_google"), dict):
            ho_so_google = kwargs["ho_so_google"]
        else:
            ho_so_google = _doi_code_lay_ho_so_google(code or "")
        ho_so_chuan = google_oauth.chuan_hoa_ho_so_google(ho_so_google)
    except ValueError as exc:
        _tra_loi_http(str(exc), 400)

    email_chuan = ho_so_chuan["email"]
    luc_nay = _bay_gio()

    with _khoa_theo_email(email_chuan):
        ds_nguoi_cu = _tim_nguoi_theo_email(email_chuan)
        nhat_ky_gop: list[dict] = []
        try:
            ket_qua = google_oauth.dang_nhap_google(
                ho_so_google=ho_so_google,
                state_gui=state_gui,
                state_phien=state_phien,
                ds_nguoi=ds_nguoi_cu,
                nhat_ky_gop=nhat_ky_gop,
                luc=luc_nay,
            )
        except ValueError as exc:
            _tra_loi_http(str(exc), 400)

        ten_nguoi = _luu_nguoi_sau_gop(
            ket_qua["nguoi"],
            ket_qua["da_gop"],
            email_chuan,
        )
        if ket_qua["nhat_ky_gop"]:
            ket_qua["nhat_ky_gop"][-1]["nguoi"] = ten_nguoi

    return {
        "ok": True,
        "nguoi": ten_nguoi,
        "da_gop": ket_qua["da_gop"],
        "nhat_ky_gop": ket_qua["nhat_ky_gop"],
    }


@contextmanager
def _khoa_theo_zalo(zalo_id: str, dien_thoai_chuan: str):
    ds_khoa = [f"linhx_oauth_lock:zalo:{zalo_id}"]
    if dien_thoai_chuan:
        ds_khoa.append(f"linhx_oauth_lock:dt:{dien_thoai_chuan}")
    ds_khoa = sorted(set(ds_khoa))
    cache = _lay_cache()
    with ExitStack() as stack:
        for khoa_lock in ds_khoa:
            stack.enter_context(_lay_lock_bo_nho(khoa_lock))
            if cache is not None and hasattr(cache, "lock"):
                try:
                    stack.enter_context(cache.lock(khoa_lock, timeout=15))
                except Exception as exc:
                    logger.warning("Không lấy được khoá cache %s: %s", khoa_lock, type(exc).__name__)
        yield


def _doi_code_lay_ho_so_zalo(code: str, oa_id_gui: str = "") -> dict:
    """Đổi authorization code lấy hồ sơ người dùng từ Zalo OAuth v4 (OA IF Agent)."""
    if not isinstance(code, str) or not code.strip():
        raise ValueError("Thiếu mã uỷ quyền Zalo OAuth (code)")

    conf = getattr(frappe, "conf", None) or {}
    app_id = str(conf.get("zalo_oauth_app_id") or "").strip()
    secret_key = str(conf.get("zalo_oauth_secret_key") or "").strip()
    oa_id_conf = str(conf.get("zalo_oa_id") or "").strip()
    if not app_id or not secret_key:
        raise ValueError("Chưa cấu hình Zalo OAuth trên máy chủ")

    form_body = urllib.parse.urlencode(
        {
            "code": code.strip(),
            "app_id": app_id,
            "grant_type": "authorization_code",
        }
    ).encode("utf-8")

    req_tok = urllib.request.Request(
        ZALO_TOKEN_ENDPOINT,
        data=form_body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "secret_key": secret_key,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req_tok, timeout=10) as resp:
            du_lieu_tok = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        raise ValueError("Không đổi được mã uỷ quyền Zalo OAuth") from exc

    ma_truy_cap = str(du_lieu_tok.get("access_token") or "").strip()
    if not ma_truy_cap:
        raise ValueError("Phản hồi Zalo OAuth thiếu access_token")

    req_info = urllib.request.Request(
        ZALO_USERINFO_ENDPOINT,
        headers={"access_token": ma_truy_cap},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req_info, timeout=10) as resp:
            du_lieu_me = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        raise ValueError("Không lấy được hồ sơ người dùng từ Zalo") from exc

    if not isinstance(du_lieu_me, dict):
        raise ValueError("Hồ sơ Zalo trả về không hợp lệ")

    zalo_id = str(du_lieu_me.get("id") or du_lieu_me.get("zalo_id") or "").strip()
    ho_ten = str(du_lieu_me.get("name") or du_lieu_me.get("ho_ten") or "").strip()
    raw_phone = du_lieu_me.get("phone") or du_lieu_me.get("dien_thoai")
    dien_thoai = str(raw_phone).strip() if isinstance(raw_phone, str) else ""
    oa_id = oa_id_conf or str(oa_id_gui or "").strip()

    ho_so: dict = {
        "zalo_id": zalo_id,
        "ho_ten": ho_ten,
    }
    if dien_thoai:
        ho_so["dien_thoai"] = dien_thoai
    if oa_id:
        ho_so["oa_id"] = oa_id
    return ho_so


def _tim_nguoi_theo_zalo_hoac_sdt(zalo_id: str, dien_thoai_chuan: str) -> list[dict]:
    """Tìm các bản ghi LX Nguoi khớp `zalo_id` hoặc số điện thoại chuẩn hoá `84...`."""
    or_filters: list[list[str]] = []
    khoa_can: set[str] = set()
    if zalo_id:
        or_filters.append(["LX Nguoi", "zalo", "=", zalo_id])
        khoa_can.add(f"zalo:{zalo_id}")
    if dien_thoai_chuan:
        khoa_can.add(f"dt:{dien_thoai_chuan}")
        bien_the = {dien_thoai_chuan, f"+{dien_thoai_chuan}"}
        if dien_thoai_chuan.startswith("84") and len(dien_thoai_chuan) > 2:
            bien_the.add("0" + dien_thoai_chuan[2:])
        for bt in sorted(bien_the):
            or_filters.append(["LX Nguoi", "dien_thoai", "=", bt])
        if len(dien_thoai_chuan) >= 3:
            or_filters.append(["LX Nguoi", "dien_thoai", "like", f"%{dien_thoai_chuan[-3:]}"])

    if not or_filters:
        return []

    ds_ung_vien = frappe.get_all(
        "LX Nguoi",
        fields=["name", "ho_ten", "dien_thoai", "email", "zalo", "don_vi", "to_chuc", "nguon", "tang_pheu"],
        or_filters=or_filters,
        order_by="creation asc",
        limit=GIOI_HAN_TRUY_VAN_NGUOI,
    )
    ket_qua: list[dict] = []
    da_thay: set[str] = set()
    for u in ds_ung_vien or []:
        if not isinstance(u, dict):
            continue
        ma_u = str(u.get("name") or "")
        if ma_u and ma_u in da_thay:
            continue
        if gop_trung.khoa_gop(u) & khoa_can:
            if ma_u:
                da_thay.add(ma_u)
            ket_qua.append(dict(u))
    return ket_qua


def _luu_nguoi_zalo_sau_gop(
    nguoi_ket_qua: dict,
    da_gop: bool,
    zalo_id: str,
    dien_thoai_chuan: str,
) -> str:
    """Cập nhật bản ghi LX Nguoi đã có (chỉ bù trường trống) hoặc tạo mới từ Zalo."""
    if da_gop and nguoi_ket_qua.get("name"):
        ten_nguoi = str(nguoi_ket_qua["name"]).strip()
        doc_nguoi = frappe.get_doc("LX Nguoi", ten_nguoi)
        co_thay_doi = False
        if not getattr(doc_nguoi, "ho_ten", None) and nguoi_ket_qua.get("ho_ten"):
            doc_nguoi.ho_ten = nguoi_ket_qua["ho_ten"]
            co_thay_doi = True
        if not getattr(doc_nguoi, "zalo", None) and zalo_id:
            doc_nguoi.zalo = zalo_id
            co_thay_doi = True
        if not getattr(doc_nguoi, "dien_thoai", None) and dien_thoai_chuan:
            doc_nguoi.dien_thoai = dien_thoai_chuan
            co_thay_doi = True
        if co_thay_doi:
            doc_nguoi.flags.ignore_permissions = True
            doc_nguoi.save(ignore_permissions=True)
        return ten_nguoi

    du_lieu_moi: dict = {
        "doctype": "LX Nguoi",
        "ho_ten": nguoi_ket_qua.get("ho_ten") or f"Zalo {zalo_id}",
        "zalo": zalo_id,
        "nguon": zalo_oauth.KENH_ZALO,
    }
    if dien_thoai_chuan:
        du_lieu_moi["dien_thoai"] = dien_thoai_chuan
    doc_moi = frappe.get_doc(du_lieu_moi)
    doc_moi.flags.ignore_permissions = True
    doc_moi.insert(ignore_permissions=True)
    return str(doc_moi.name)


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=GIOI_HAN_CALLBACK_MOI_PHUT, seconds=CUA_SO_GIAY)
def zalo_callback(
    state: str | None = None,
    code: str | None = None,
    oa_id: str | None = None,
    **kwargs,
) -> dict:
    """Xử lý callback đăng nhập Zalo (OA IF Agent) và gộp hồ sơ vào `LX Nguoi`."""
    _kiem_module_crm_bat()

    state_gui = state if state is not None else kwargs.get("state_gui")
    if not isinstance(state_gui, str):
        state_gui = ""

    la_http = _co_request_http()
    state_phien = _doc_va_tieu_thu_state_phien(KHOA_STATE_ZALO_SESSION)
    if not state_phien and not la_http and isinstance(kwargs.get("state_phien"), str):
        state_phien = kwargs["state_phien"]

    try:
        zalo_oauth.kiem_state_oauth(state_gui, state_phien)
        if not la_http and isinstance(kwargs.get("ho_so_zalo"), dict):
            ho_so_zalo = kwargs["ho_so_zalo"]
        else:
            ho_so_zalo = _doi_code_lay_ho_so_zalo(code or "", oa_id or "")
        ho_so_chuan = zalo_oauth.chuan_hoa_ho_so_zalo(ho_so_zalo)
    except ValueError as exc:
        _tra_loi_http(str(exc), 400)

    zalo_id = ho_so_chuan["zalo_id"]
    dien_thoai_chuan = ho_so_chuan["dien_thoai"]
    luc_nay = _bay_gio()

    with _khoa_theo_zalo(zalo_id, dien_thoai_chuan):
        ds_nguoi_cu = _tim_nguoi_theo_zalo_hoac_sdt(zalo_id, dien_thoai_chuan)
        nhat_ky_gop: list[dict] = []
        try:
            ket_qua = zalo_oauth.dang_nhap_zalo(
                ho_so_zalo=ho_so_zalo,
                state_gui=state_gui,
                state_phien=state_phien,
                ds_nguoi=ds_nguoi_cu,
                nhat_ky_gop=nhat_ky_gop,
                luc=luc_nay,
            )
        except ValueError as exc:
            _tra_loi_http(str(exc), 400)

        ten_nguoi = _luu_nguoi_zalo_sau_gop(
            ket_qua["nguoi"],
            ket_qua["da_gop"],
            zalo_id,
            dien_thoai_chuan,
        )
        if ket_qua["nhat_ky_gop"]:
            ket_qua["nhat_ky_gop"][-1]["nguoi"] = ten_nguoi

    return {
        "ok": True,
        "nguoi": ten_nguoi,
        "da_gop": ket_qua["da_gop"],
        "nhat_ky_gop": ket_qua["nhat_ky_gop"],
    }

