import frappe
from frappe.model.document import Document

from linhx_core.pay import _chuan_hoa_tx_id_rong, dang_ky_auth_hook
from linhx_core.pay.so_s1a import ghi_so_s1a_tu_don


class LXDon(Document):
	def autoname(self):
		if not getattr(self, "ma", None) and getattr(self, "noi_dung_ck", None):
			self.ma = str(self.noi_dung_ck).strip()
		if getattr(self, "ma", None):
			self.name = str(self.ma).strip()

	def before_validate(self):
		dang_ky_auth_hook()
		if not getattr(self, "ma", None):
			fallback = getattr(self, "noi_dung_ck", None) or getattr(self, "name", None)
			if fallback:
				self.ma = str(fallback).strip()
		tx = str(getattr(self, "tx_id", None) or "").strip()
		self.tx_id = tx if tx else None

	def validate(self):
		nd = str(getattr(self, "noi_dung_ck", None) or "").strip()
		if nd:
			self.noi_dung_ck = nd
			trung = frappe.db.exists("LX Don", {"noi_dung_ck": nd, "name": ["!=", self.name]})
			if trung:
				frappe.throw(f"Nội dung chuyển khoản {nd} đã tồn tại ở đơn {trung}")
		tx = str(getattr(self, "tx_id", None) or "").strip()
		if tx:
			self.tx_id = tx
			trung_tx = frappe.db.exists("LX Don", {"tx_id": tx, "name": ["!=", self.name]})
			if trung_tx:
				frappe.throw(f"Mã giao dịch {tx} đã tồn tại ở đơn {trung_tx}")

	def on_update(self):
		if getattr(self, "trang_thai", None) == "da_tra":
			ghi_so_s1a_tu_don(self)

	def on_doctype_update(self):
		_chuan_hoa_tx_id_rong()
