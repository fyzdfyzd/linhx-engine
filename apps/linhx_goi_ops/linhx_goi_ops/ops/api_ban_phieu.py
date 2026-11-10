"""API Frappe cho bàn duyệt phiếu Agy (/engine): liệt kê phiếu chờ, duyệt và trả lại phiếu.

Thuần Python ở mức nạp file (không `import frappe` ở đầu file); nạp trễ `frappe` trong hàm.
"""
from __future__ import annotations

import json

from linhx_goi_ops.ops import ban_phieu, phieu_agy


def _lay_frappe():
    try:
        import frappe
    except ImportError:
        return None
    return frappe


def _yeu_cau_frappe():
    frappe = _lay_frappe()
    if frappe is None:
        raise RuntimeError("Cần môi trường Frappe để gọi API bàn phiếu")
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


def _doc_payload(kwargs: dict) -> dict:
    du_lieu: dict = {}
    frappe = _lay_frappe()
    req = getattr(frappe, "request", None) if frappe is not None else None
    if req is not None:
        try:
            body = req.get_json(silent=True)
            if isinstance(body, dict):
                du_lieu.update(body)
        except Exception:
            pass
        if not du_lieu:
            try:
                raw = req.get_data(as_text=True)
                if raw:
                    body = json.loads(raw)
                    if isinstance(body, dict):
                        du_lieu.update(body)
            except Exception:
                pass
    for k, v in (kwargs or {}).items():
        if k != "cmd" and v is not None:
            du_lieu.setdefault(k, v)
    return du_lieu


def _lay_vai_tro_dieu_hanh() -> list[str]:
    frappe = _yeu_cau_frappe()
    user = getattr(getattr(frappe, "session", None), "user", "Guest")
    if not user or user == "Guest":
        frappe.throw("Cần đăng nhập điều hành", frappe.PermissionError)
    vai_tro = list(frappe.get_roles() or [])
    if not (set(vai_tro) & set(phieu_agy.VAI_DIEU_HANH)):
        frappe.throw(
            "Chỉ vai điều hành (System Manager, LX Operator) mới được duyệt hoặc trả phiếu",
            frappe.PermissionError,
        )
    return vai_tro


def _chuan_ban_ghi(d: dict) -> dict:
    ban_ghi = dict(d)
    c = ban_ghi.get("creation")
    if c is not None and hasattr(c, "strftime"):
        ban_ghi["creation"] = c.strftime(ban_phieu.DINH_DANG_TG)
    elif c is not None:
        ban_ghi["creation"] = str(c)
    return ban_ghi


@_whitelist()
def phieu_cho():
    """Trả danh sách phiếu Agy đang ở trạng thái 'nhap' (mới nhất trước)."""
    frappe = _yeu_cau_frappe()
    _lay_vai_tro_dieu_hanh()
    if not frappe.db.exists("DocType", "LX Phieu Agy"):
        return []
    ds = frappe.get_all(
        "LX Phieu Agy",
        filters={"trang_thai": "nhap"},
        fields=["name", "loai_phieu", "de", "vung", "trang_thai", "ly_do_tra", "creation"],
        order_by="creation desc",
        limit=100,
    )
    return ban_phieu.ds_phieu_cho([_chuan_ban_ghi(x) for x in (ds or [])])


@_whitelist(methods=["POST"])
def duyet(ma_phieu: str | None = None, **kwargs):
    """Duyệt phiếu từ 'nhap' sang 'duyet'."""
    frappe = _yeu_cau_frappe()
    vai_tro = _lay_vai_tro_dieu_hanh()
    payload = _doc_payload(kwargs)
    ma = str(ma_phieu if ma_phieu is not None else (payload.get("ma_phieu") or payload.get("name") or "")).strip()
    if not ma:
        frappe.throw("Thiếu mã phiếu", frappe.ValidationError)

    doc = frappe.get_doc("LX Phieu Agy", ma)
    ban_ghi = {
        "name": doc.name,
        "loai_phieu": getattr(doc, "loai_phieu", None),
        "de": getattr(doc, "de", "") or "",
        "vung": getattr(doc, "vung", "") or "",
        "trang_thai": getattr(doc, "trang_thai", None),
        "ly_do_tra": getattr(doc, "ly_do_tra", "") or "",
    }
    kq = ban_phieu.duyet_phieu([ban_ghi], ma, vai_tro)
    doc.trang_thai = kq["trang_thai"]
    doc.save()
    return {"ok": True, "name": doc.name, "trang_thai": doc.trang_thai}


@_whitelist(methods=["POST"])
def tra_lai(ma_phieu: str | None = None, ly_do: str | None = None, **kwargs):
    """Trả lại phiếu từ 'nhap' sang 'tra' kèm lý do bắt buộc."""
    frappe = _yeu_cau_frappe()
    vai_tro = _lay_vai_tro_dieu_hanh()
    payload = _doc_payload(kwargs)
    ma = str(ma_phieu if ma_phieu is not None else (payload.get("ma_phieu") or payload.get("name") or "")).strip()
    ly_do_raw = ly_do if ly_do is not None else payload.get("ly_do")
    if not ma:
        frappe.throw("Thiếu mã phiếu", frappe.ValidationError)
    if not isinstance(ly_do_raw, str) or not ly_do_raw.strip():
        frappe.throw("Lý do trả phiếu không được để trống", frappe.ValidationError)

    doc = frappe.get_doc("LX Phieu Agy", ma)
    ban_ghi = {
        "name": doc.name,
        "loai_phieu": getattr(doc, "loai_phieu", None),
        "de": getattr(doc, "de", "") or "",
        "vung": getattr(doc, "vung", "") or "",
        "trang_thai": getattr(doc, "trang_thai", None),
        "ly_do_tra": getattr(doc, "ly_do_tra", "") or "",
    }
    kq = ban_phieu.tra_phieu([ban_ghi], ma, ly_do_raw, vai_tro)
    doc.trang_thai = kq["trang_thai"]
    doc.ly_do_tra = kq["ly_do_tra"]
    doc.save()
    return {
        "ok": True,
        "name": doc.name,
        "trang_thai": doc.trang_thai,
        "ly_do_tra": doc.ly_do_tra,
    }
