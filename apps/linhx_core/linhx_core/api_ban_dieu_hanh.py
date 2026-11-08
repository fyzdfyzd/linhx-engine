"""API bàn điều hành (/engine): trả việc chờ duyệt, lead mới, đơn mới."""
from __future__ import annotations

import frappe
from frappe.utils import now_datetime

from linhx_core import ban as _ban


def _la_dieu_hanh():
    if getattr(frappe.session, "user", "Guest") == "Guest":
        frappe.throw("Cần đăng nhập điều hành", frappe.PermissionError)
    roles = set(frappe.get_roles())
    if not (roles & {"System Manager", "LX Operator", "Administrator"}):
        frappe.throw("Cần quyền LX Operator", frappe.PermissionError)


def _chuan_ds(ds: list[dict]) -> list[dict]:
    kq = []
    for d in ds or []:
        ban_ghi = dict(d)
        if ban_ghi.get("creation") is not None:
            try:
                ban_ghi["creation"] = _ban._parse_tg(ban_ghi["creation"]).strftime(_ban.DINH_DANG_TG)
            except ValueError:
                ban_ghi["creation"] = str(ban_ghi["creation"])
        kq.append(ban_ghi)
    return kq


@frappe.whitelist()
def ban(gio: int = 24):
    _la_dieu_hanh()
    jobs = []
    if frappe.db.exists("DocType", "LX Job"):
        jobs = _chuan_ds(
            frappe.get_all(
                "LX Job",
                filters={"trang_thai": "cho_duyet"},
                fields=["name", "workflow", "trang_thai", "nguon", "ten_khach", "email_khach", "dau_vao", "creation"],
                order_by="creation desc",
                limit=50,
            )
        )
    nguoi = []
    if frappe.db.exists("DocType", "LX Nguoi"):
        nguoi = _chuan_ds(
            frappe.get_all(
                "LX Nguoi",
                fields=["name", "ho_ten", "dien_thoai", "email", "zalo", "don_vi", "to_chuc", "creation"],
                order_by="creation desc",
                limit=100,
            )
        )
    don = []
    if frappe.db.exists("DocType", "LX Don"):
        don = _chuan_ds(
            frappe.get_all(
                "LX Don",
                fields=["name", "ma", "goi", "nguoi", "so_tien", "trang_thai", "brand", "email", "creation"],
                order_by="creation desc",
                limit=100,
            )
        )
    luc = _ban._parse_tg(now_datetime()).strftime(_ban.DINH_DANG_TG)
    for x in (*jobs, *nguoi, *don):
        c = x.get("creation")
        if isinstance(c, str) and len(c) == 19 and c > luc:
            luc = c
    return _ban.tong_hop(jobs, nguoi, don, luc, gio=int(gio or 24))
