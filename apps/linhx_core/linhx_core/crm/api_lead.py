"""API chuyển lead giữa hai bản cài Frappe (gui_lead và nhan_lead)."""
from __future__ import annotations

import json
import urllib.error
import urllib.request

import frappe

from linhx_core.crm import chuyen_lead, dong_y


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
    s = str(ten or "").strip()
    if s.endswith(".local"):
        s = s[:-6]
    return s


def _lay_cau_hinh_dich(site_dich: str) -> tuple[str, str]:
    """Đọc URL và chuỗi xác thực API của bản cài đích từ site_config (frappe.conf)."""
    conf = getattr(frappe, "conf", None) or {}
    ds_dich = conf.get("chuyen_lead_dich") or conf.get("sites_dich") or {}
    muc = ds_dich.get(site_dich) if isinstance(ds_dich, dict) else None
    if not isinstance(muc, dict):
        muc = {}

    url = (
        muc.get("url")
        or conf.get(f"lead_dich_{site_dich}_url")
        or conf.get("lead_dich_url")
        or ""
    )
    xac_thuc = (
        muc.get("xac_thuc")
        or muc.get("auth")
        or conf.get(f"lead_dich_{site_dich}_auth")
        or conf.get("lead_dich_auth")
        or ""
    )
    if not xac_thuc:
        k = (
            muc.get("key")
            or muc.get("api_key")
            or conf.get(f"lead_dich_{site_dich}_key")
            or conf.get("lead_dich_key")
            or ""
        )
        sec = (
            muc.get("secret")
            or muc.get("api_secret")
            or conf.get(f"lead_dich_{site_dich}_secret")
            or conf.get("lead_dich_secret")
            or ""
        )
        if k and sec:
            xac_thuc = f"{k}:{sec}"

    url = str(url).strip().rstrip("/")
    xac_thuc = str(xac_thuc).strip()
    if not url or not xac_thuc:
        frappe.throw(f"Thiếu cấu hình URL hoặc khoá xác thực cho bản cài đích {site_dich!r} trong site_config")
    return url, xac_thuc


@frappe.whitelist()
def nhan_lead(goi=None, **kwargs):
    """Nhận gói chuyển lead từ bản cài nguồn (xác thực qua API key user riêng, không mở cho Guest)."""
    if getattr(frappe.session, "user", "Guest") == "Guest":
        frappe.throw("Không cho phép khách gọi nhan_lead", frappe.PermissionError)

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
        for tr in ("ho_ten", "dien_thoai", "email", "zalo"):
            if nguoi_nhan.get(tr):
                frappe.db.set_value("LX Nguoi", ten_nguoi, tr, nguoi_nhan.get(tr), update_modified=True)
        if gc_json:
            frappe.db.set_value("LX Nguoi", ten_nguoi, "ghi_cong", gc_json, update_modified=True)
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
        doc.insert(ignore_permissions=True)
        ten_nguoi = doc.name
        if gc_json and not frappe.db.get_value("LX Nguoi", ten_nguoi, "ghi_cong"):
            frappe.db.set_value("LX Nguoi", ten_nguoi, "ghi_cong", gc_json, update_modified=True)

    frappe.db.commit()
    return {
        "nguoi_moi": ten_nguoi,
        "ghi_cong": gc_dict,
    }


@frappe.whitelist()
def gui_lead(nguoi, site_dich="linhx", don_vi=None):
    """Kiểm đồng ý chuyển chéo và gửi lead từ bản cài hiện tại sang site_dich."""
    if getattr(frappe.session, "user", "Guest") == "Guest":
        frappe.throw("Không cho phép khách gọi gui_lead", frappe.PermissionError)

    nguoi_in = _giai_ma_json(nguoi)
    if isinstance(nguoi_in, str):
        doc_nguoi = frappe.get_doc("LX Nguoi", nguoi_in).as_dict()
    elif isinstance(nguoi_in, dict):
        if nguoi_in.get("name") and not any(nguoi_in.get(k) for k in ("ho_ten", "dien_thoai", "email", "zalo")):
            doc_nguoi = frappe.get_doc("LX Nguoi", nguoi_in["name"]).as_dict()
        else:
            doc_nguoi = dict(nguoi_in)
    else:
        frappe.throw("Tham số nguoi không hợp lệ")

    ma_nguoi = str(doc_nguoi.get("name") or "").strip()
    so_dong_y = []
    if ma_nguoi:
        so_dong_y = frappe.get_all(
            "LX Dong Y",
            filters={"nguoi": ma_nguoi},
            fields=["nguoi", "muc_dich", "dong_y", "luc", "nguon"],
            order_by="luc asc, creation asc",
        )

    conf = getattr(frappe, "conf", None) or {}
    site_nguon = _chuan_site(conf.get("site_nguon") or getattr(frappe.local, "site", "") or "ifagent")
    don_vi_str = str(don_vi or doc_nguoi.get("don_vi") or conf.get("don_vi_mac_dinh") or "IFAGENT").strip()
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
