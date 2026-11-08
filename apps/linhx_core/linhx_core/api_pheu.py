"""API bảng phễu 6 tầng (/engine): chỉ người điều hành."""
from __future__ import annotations

import frappe

from linhx_core import pheu as _pheu


def _la_dieu_hanh():
    if getattr(frappe.session, "user", "Guest") == "Guest":
        frappe.throw("Cần đăng nhập điều hành", frappe.PermissionError)
    roles = set(frappe.get_roles())
    if not (roles & {"System Manager", "LX Operator", "Administrator"}):
        frappe.throw("Cần quyền LX Operator", frappe.PermissionError)


@frappe.whitelist()
def pheu(luot_xem: int = 0):
    _la_dieu_hanh()
    nguoi = []
    if frappe.db.exists("DocType", "LX Nguoi"):
        try:
            nguoi = frappe.get_all("LX Nguoi", fields=["name", "nguon"])
        except Exception:
            nguoi = frappe.get_all("LX Nguoi", fields=["name"])
    co_hoi = []
    if frappe.db.exists("DocType", "LX Co Hoi"):
        co_hoi = frappe.get_all("LX Co Hoi", fields=["name", "nguoi"])
    don = []
    if frappe.db.exists("DocType", "LX Don"):
        don = frappe.get_all("LX Don", fields=["name", "ma", "nguoi", "trang_thai"])
    return _pheu.dem(nguoi, co_hoi, don, int(luot_xem or 0))
