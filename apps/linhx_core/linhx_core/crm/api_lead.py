"""API chuyển lead giữa hai bản cài Frappe (gui_lead và nhan_lead)."""
from __future__ import annotations

import json
import urllib.error
import urllib.request

import frappe

from linhx_core.crm import chuyen_lead, dong_y

VAI_TRO_CHUYEN_LEAD = "LX Chuyen Lead"


def _giai_ma_json(gia_tri: object) -> object:
    if isinstance(gia_tri, str):
        s = gia_tri.strip()
        if s.startswith("{") or s.startswith("["):
            try:
                return json.loads(s)
            except Exception:
                return gia_tri
    return gia_tri


def _chuan_site(ten: object) -> str:
    return str(ten or "").strip().removesuffix(".local")


def _lay_cau_hinh_dich(site_dich: str) -> tuple[str, str]:
    """Đọc URL và chuỗi xác thực API (api_key:api_secret) của bản cài đích từ site_config['chuyen_lead_dich'][site_dich]."""
    conf = getattr(frappe, "conf", None) or {}
    ds_dich = conf.get("chuyen_lead_dich")
    muc = ds_dich.get(site_dich) if isinstance(ds_dich, dict) else None
    if not isinstance(muc, dict):
        frappe.throw(f"Thiếu cấu hình chuyen_lead_dich.{site_dich} trong site_config")

    url = str(muc.get("url") or "").strip().rstrip("/")
    xac_thuc = str(muc.get("xac_thuc") or "").strip()
    if not url or not xac_thuc:
        frappe.throw(f"Thiếu url hoặc xac_thuc trong chuyen_lead_dich.{site_dich} của site_config")
    return url, xac_thuc


def _kiem_quyen_nhan_lead() -> None:
    """Chặn Guest và user thường; chỉ cho phép user tích hợp bản cài nguồn (vai trò LX Chuyen Lead / chuyen_lead_user)."""
    user = getattr(frappe.session, "user", "Guest") or "Guest"
    if user == "Guest":
        frappe.throw("Không cho phép khách gọi nhan_lead", frappe.PermissionError)

    conf = getattr(frappe, "conf", None) or {}
    user_nguon = str(conf.get("chuyen_lead_user") or "").strip()
    if user_nguon and user not in (user_nguon, "Administrator"):
        frappe.throw("Chỉ tài khoản tích hợp bản cài nguồn được phép gọi nhan_lead", frappe.PermissionError)

    frappe.only_for(VAI_TRO_CHUYEN_LEAD)


@frappe.whitelist()
def nhan_lead(goi=None, **kwargs):
    """Nhận gói chuyển lead từ bản cài nguồn (xác thực qua API key user riêng có vai trò LX Chuyen Lead)."""
    _kiem_quyen_nhan_lead()

    du_lieu = _giai_ma_json(goi)
    if not isinstance(du_lieu, dict):
        body = {}
        if getattr(frappe, "request", None):
            try:
                body = frappe.request.get_json(silent=True) or {}
            except Exception:
                body = {}
        if isinstance(body.get("goi"), (dict, str)):
            du_lieu = _giai_ma_json(body.get("goi"))
        elif "nguoi" in body or "ghi_cong" in body:
            du_lieu = body
        elif "nguoi" in kwargs or "ghi_cong" in kwargs:
            du_lieu = {
                "nguoi": _giai_ma_json(kwargs.get("nguoi")),
                "ghi_cong": _giai_ma_json(kwargs.get("ghi_cong")),
            }

    if not isinstance(du_lieu, dict):
        frappe.throw("Gói chuyển lead không hợp lệ")

    ds_hien_co = frappe.get_all(
        "LX Nguoi",
        fields=["name", "ho_ten", "dien_thoai", "email", "zalo", "don_vi", "to_chuc", "ghi_cong"],
        order_by="creation asc",
    )
    for dong in ds_hien_co:
        dong["ghi_cong"] = _giai_ma_json(dong.get("ghi_cong"))

    try:
        _, nguoi_nhan = chuyen_lead.nhan(du_lieu, ds_hien_co)
    except ValueError as exc:
        frappe.throw(str(exc))

    gc_dict = _giai_ma_json(nguoi_nhan.get("ghi_cong"))
    gc_json = json.dumps(gc_dict, ensure_ascii=False) if isinstance(gc_dict, dict) else str(gc_dict or "")

    ten_nguoi = nguoi_nhan.get("name")
    if ten_nguoi:
        doc = frappe.get_doc("LX Nguoi", ten_nguoi)
        for tr in ("ho_ten", "dien_thoai", "email", "zalo"):
            if not getattr(doc, tr, None) and nguoi_nhan.get(tr):
                setattr(doc, tr, nguoi_nhan.get(tr))
        if not getattr(doc, "ghi_cong", None) and gc_json:
            doc.ghi_cong = gc_json
        doc.save()
    else:
        doc = frappe.get_doc(
            {
                "doctype": "LX Nguoi",
                "ho_ten": nguoi_nhan.get("ho_ten"),
                "dien_thoai": nguoi_nhan.get("dien_thoai"),
                "email": nguoi_nhan.get("email"),
                "zalo": nguoi_nhan.get("zalo"),
                "ghi_cong": gc_json,
            }
        )
        doc.insert()
        ten_nguoi = doc.name

    return {
        "nguoi_moi": ten_nguoi,
        "ghi_cong": gc_dict,
    }


def _xac_dinh_don_vi_ghi_cong(doc_nguoi: dict, user: str, don_vi_tham_so: object) -> str:
    """Ưu tiên đơn vị của bản ghi LX Nguoi trong DB, sau đó tới User Permission của người gọi."""
    don_vi_db = str(doc_nguoi.get("don_vi") or "").strip()
    if don_vi_db:
        return don_vi_db

    don_vi_up = frappe.get_all(
        "User Permission",
        filters={"user": user, "allow": "LX Don Vi"},
        pluck="for_value",
        order_by="creation asc",
    )
    if don_vi_up:
        dv_client = str(don_vi_tham_so or "").strip()
        if dv_client and dv_client in don_vi_up:
            return dv_client
        return str(don_vi_up[0]).strip()

    conf = getattr(frappe, "conf", None) or {}
    return str(conf.get("don_vi_mac_dinh") or don_vi_tham_so or "").strip()


@frappe.whitelist()
def gui_lead(nguoi, site_dich="linhx", don_vi=None):
    """Kiểm quyền đọc, kiểm đồng ý chuyển chéo và gửi lead từ bản cài hiện tại sang site_dich."""
    user = getattr(frappe.session, "user", "Guest") or "Guest"
    if user == "Guest":
        frappe.throw("Không cho phép khách gọi gui_lead", frappe.PermissionError)

    nguoi_in = _giai_ma_json(nguoi)
    if isinstance(nguoi_in, str):
        ma_nguoi = nguoi_in.strip()
    elif isinstance(nguoi_in, dict):
        ma_nguoi = str(nguoi_in.get("name") or "").strip()
    else:
        ma_nguoi = ""

    if not ma_nguoi:
        frappe.throw("Phải cung cấp mã bản ghi LX Nguoi (name) có trong hệ thống")

    doc_obj = frappe.get_doc("LX Nguoi", ma_nguoi)
    if not frappe.has_permission("LX Nguoi", "read", doc_obj):
        frappe.throw("Không có quyền đọc hồ sơ LX Nguoi này", frappe.PermissionError)
    if not frappe.has_permission("LX Dong Y", "read"):
        frappe.throw("Không có quyền đọc sổ đồng ý LX Dong Y", frappe.PermissionError)

    doc_nguoi = doc_obj.as_dict()
    so_dong_y = frappe.get_list(
        "LX Dong Y",
        filters={"nguoi": ma_nguoi},
        fields=["nguoi", "muc_dich", "dong_y", "luc", "nguon"],
        order_by="luc asc, creation asc",
    )

    conf = getattr(frappe, "conf", None) or {}
    site_nguon = _chuan_site(conf.get("site_nguon") or getattr(frappe.local, "site", "") or "ifagent")
    don_vi_str = _xac_dinh_don_vi_ghi_cong(doc_nguoi, user, don_vi)
    luc_str = dong_y.bay_gio()

    try:
        goi = chuyen_lead.goi_di(doc_nguoi, so_dong_y, site_nguon, don_vi_str, luc_str)
    except dong_y.TuChoi as exc:
        if getattr(frappe.local, "response", None) is not None:
            frappe.local.response["http_status_code"] = 403
        frappe.throw(str(exc), frappe.PermissionError)

    site_dich_chuan = _chuan_site(site_dich)
    url_dich, xac_thuc = _lay_cau_hinh_dich(site_dich_chuan)
    endpoint = f"{url_dich}/api/method/linhx_core.crm.api_lead.nhan_lead"

    header_auth = xac_thuc if xac_thuc.lower().startswith("token ") else f"token {xac_thuc}"
    req = urllib.request.Request(
        endpoint,
        data=json.dumps({"goi": goi}, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
            "Authorization": header_auth,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            phan_hoi = json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        chi_tiet = exc.read().decode("utf-8", errors="ignore")
        frappe.throw(f"Bản cài đích trả lỗi HTTP {exc.code}: {chi_tiet}")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        frappe.throw(f"Không thể kết nối tới bản cài đích {site_dich_chuan!r}: {exc}")

    ket_qua = phan_hoi.get("message") if isinstance(phan_hoi, dict) and "message" in phan_hoi else phan_hoi
    if not isinstance(ket_qua, dict):
        ket_qua = {}

    return {
        "luc": luc_str,
        "tu": site_nguon,
        "toi": site_dich_chuan,
        "nguoi_moi": ket_qua.get("nguoi_moi"),
        "ghi_cong": ket_qua.get("ghi_cong") or goi["ghi_cong"],
    }
