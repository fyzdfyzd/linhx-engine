"""Controller DocType LX Giao Dich CTS: lưu vết giao dịch SePay chống trùng tx_id (unique)."""
from __future__ import annotations

import frappe
from frappe.model.document import Document


class LXGiaoDichCTS(Document):
    def autoname(self):
        tx = str(getattr(self, "tx_id", None) or "").strip()
        if tx:
            self.tx_id = tx
            self.name = tx

    def validate(self):
        tx = str(getattr(self, "tx_id", None) or "").strip()
        if not tx:
            frappe.throw("tx_id không được để trống")
        self.tx_id = tx

        if not self.is_new():
            frappe.throw("Không được sửa giao dịch CTS đã ghi nhận", frappe.PermissionError)

        if getattr(frappe, "db", None) is not None and hasattr(frappe.db, "exists"):
            trung = frappe.db.exists(
                "LX Giao Dich CTS", {"tx_id": tx, "name": ["!=", self.name]}
            )
            if trung:
                frappe.throw(
                    f"Mã giao dịch {tx} đã tồn tại",
                    getattr(frappe, "DuplicateEntryError", frappe.ValidationError),
                )

    def on_trash(self):
        frappe.throw("Không được xoá giao dịch CTS đã ghi nhận", frappe.PermissionError)
