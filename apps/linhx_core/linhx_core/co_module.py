"""Kiểm tra cờ bật/tắt module từ LX Cau Hinh và nối vào quyền Frappe."""
import functools
import json
import pathlib
from urllib.parse import unquote

CAC_MODULE_CO_CO = ("crm", "pay")


def _quet_doctype_module() -> dict[str, str]:
    """Tự động quét các DocType thuộc module có cờ (crm, pay) trong linhx_core."""
    kq: dict[str, str] = {}
    goc = pathlib.Path(__file__).resolve().parent
    for p in sorted(goc.rglob("*.json")):
        if "doctype" not in p.parts:
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(d, dict) and d.get("doctype") == "DocType":
            ten = str(d.get("name") or "").strip()
            mod = str(d.get("module") or "").strip().lower()
            if ten and mod in CAC_MODULE_CO_CO:
                kq[ten] = mod
    return kq


DOCTYPE_MODULE = _quet_doctype_module()


def _co_bat(gia_tri) -> bool:
    if isinstance(gia_tri, bool):
        return gia_tri
    if isinstance(gia_tri, (int, float)):
        return gia_tri == 1
    if isinstance(gia_tri, str):
        return gia_tri.strip().lower() in ("1", "true", "yes", "on")
    return False


def module_bat(ten_module: str, cau_hinh: dict) -> bool:
    """Trả True nếu module đang bật trong cau_hinh (ví dụ {"bat_crm": 1}). Thiếu/lỗi cờ coi là tắt."""
    ten = str(ten_module or "").strip().lower()
    if ten in ("linhx_core", "linhx core", "core"):
        return True
    if not ten or not isinstance(cau_hinh, dict):
        return False
    khoa = f"bat_{ten}"
    return _co_bat(cau_hinh.get(khoa, 0))


@functools.lru_cache(maxsize=None)
def _tim_module_doctype(ten_doctype: str) -> str | None:
    if ten_doctype in DOCTYPE_MODULE:
        return DOCTYPE_MODULE[ten_doctype]
    tep = str(ten_doctype or "").strip().lower().replace(" ", "_") + ".json"
    goc = pathlib.Path(__file__).resolve().parent
    for p in goc.rglob(tep):
        if "doctype" in p.parts:
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            if d.get("name") == ten_doctype and d.get("doctype") == "DocType":
                return str(d.get("module") or "").strip().lower()
    return None


def doctype_bi_an(ten_doctype: str, cau_hinh: dict) -> bool:
    """Trả True nếu DocType thuộc module có cờ đang tắt; DocType lõi luôn trả False."""
    mod = _tim_module_doctype(ten_doctype)
    if not mod or mod not in CAC_MODULE_CO_CO:
        return False
    return not module_bat(mod, cau_hinh)


def xoa_cache_cau_hinh(doc=None, method=None):
    """Xoá cache cờ module trên frappe.local khi bắt đầu request hoặc khi lưu LX Cau Hinh."""
    try:
        import frappe

        local_obj = getattr(frappe, "local", None)
        if local_obj is not None:
            local_obj._lx_cau_hinh_cache = None
    except Exception:
        pass


def _doc_cau_hinh_frappe() -> dict:
    """Đọc cờ module từ Single DocType LX Cau Hinh (cache theo request trên frappe.local)."""
    import frappe

    local_obj = getattr(frappe, "local", None)
    co_req = getattr(local_obj, "request", None) is not None
    if co_req:
        da_cache = getattr(local_obj, "_lx_cau_hinh_cache", None)
        if isinstance(da_cache, dict):
            return dict(da_cache)

    cau_hinh = {f"bat_{m}": 0 for m in CAC_MODULE_CO_CO}
    try:
        for m in CAC_MODULE_CO_CO:
            co = f"bat_{m}"
            if hasattr(frappe.db, "sql"):
                rows = frappe.db.sql(
                    "SELECT value FROM `tabSingles` WHERE doctype=%s AND field=%s LIMIT 1",
                    ("LX Cau Hinh", co),
                )
                val = rows[0][0] if rows else None
            else:
                val = frappe.db.get_single_value("LX Cau Hinh", co)
            cau_hinh[co] = int(_co_bat(val)) if val is not None else 0
    except Exception:
        return {f"bat_{m}": 0 for m in CAC_MODULE_CO_CO}

    if co_req and local_obj is not None:
        local_obj._lx_cau_hinh_cache = dict(cau_hinh)
    return cau_hinh


def frappe_has_permission(doc, ptype=None, user=None, **kwargs):
    """Hook has_permission theo DocType: trả False nếu module đang tắt (trừ Administrator)."""
    import frappe

    nguoi_dung = user or getattr(getattr(frappe, "session", None), "user", None)
    if nguoi_dung == "Administrator":
        return None
    ten_doctype = doc.get("doctype") if isinstance(doc, dict) else getattr(doc, "doctype", None) or str(doc)
    if doctype_bi_an(ten_doctype, _doc_cau_hinh_frappe()):
        return False
    return None


def frappe_permission_query_conditions(user=None, doctype=None, **kwargs):
    """Hook permission_query_conditions theo DocType: trả '1=0' nếu module đang tắt (trừ Administrator)."""
    import frappe

    nguoi_dung = user or getattr(getattr(frappe, "session", None), "user", None)
    if nguoi_dung == "Administrator":
        return ""
    if doctype and doctype_bi_an(doctype, _doc_cau_hinh_frappe()):
        return "1=0"
    return ""


def frappe_kiem_tra_doc_event(doc, method=None):
    """Hook doc_events theo DocType: chặn ghi/xoá khi module đang tắt (trừ Administrator)."""
    import frappe

    nguoi_dung = getattr(getattr(frappe, "session", None), "user", None)
    if nguoi_dung == "Administrator":
        return
    ten_doctype = doc.get("doctype") if isinstance(doc, dict) else getattr(doc, "doctype", None) or ""
    if ten_doctype and doctype_bi_an(ten_doctype, _doc_cau_hinh_frappe()):
        frappe.throw(f"DocType {ten_doctype} đang ẩn do module tắt", frappe.PermissionError)


def _trich_doctype_tu_request() -> list[str]:
    import frappe

    ds = []
    req = getattr(frappe.local, "request", None)
    if req:
        duong = unquote(getattr(req, "path", "") or "")
        for tien_to in ("/api/resource/", "/api/v2/document/"):
            if duong.startswith(tien_to):
                phan = duong[len(tien_to):].strip("/").split("/")[0].strip()
                if phan:
                    ds.append(phan)
        args = getattr(req, "args", None)
        if args:
            for k in ("doctype", "dt", "ref_doctype"):
                v = args.get(k)
                if isinstance(v, str) and v.strip():
                    ds.append(v.strip())

    form_dict = getattr(frappe.local, "form_dict", None) or {}
    if isinstance(form_dict, dict):
        for k in ("doctype", "dt", "ref_doctype"):
            v = form_dict.get(k)
            if isinstance(v, str) and v.strip():
                ds.append(v.strip())
        doc = form_dict.get("doc")
        if isinstance(doc, str):
            try:
                doc = json.loads(doc)
            except Exception:
                doc = None
        if isinstance(doc, dict):
            v = doc.get("doctype")
            if isinstance(v, str) and v.strip():
                ds.append(v.strip())
    return ds


def frappe_before_request():
    """Hook before_request: chặn truy cập HTTP API tới DocType của module đang tắt (trừ Administrator)."""
    import frappe

    xoa_cache_cau_hinh()
    nguoi_dung = getattr(getattr(frappe, "session", None), "user", None)
    if nguoi_dung in (None, "", "Guest") and frappe.get_request_header("Authorization"):
        try:
            import frappe.auth

            frappe.auth.validate_auth()
            nguoi_dung = getattr(getattr(frappe, "session", None), "user", None)
        except Exception:
            pass
    if nguoi_dung == "Administrator":
        return

    ung_vien = [dt for dt in _trich_doctype_tu_request() if _tim_module_doctype(dt) in CAC_MODULE_CO_CO]
    if not ung_vien:
        return
    cau_hinh = _doc_cau_hinh_frappe()
    for dt in ung_vien:
        if doctype_bi_an(dt, cau_hinh):
            raise frappe.PermissionError(f"DocType {dt} đang ẩn do module tắt")
