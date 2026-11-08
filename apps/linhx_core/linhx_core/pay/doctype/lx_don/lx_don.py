import frappe
from frappe.model.document import Document


class LXDon(Document):
	def autoname(self):
		if not getattr(self, "ma", None) and getattr(self, "noi_dung_ck", None):
			self.ma = str(self.noi_dung_ck).strip()
		if getattr(self, "ma", None):
			self.name = str(self.ma).strip()

	def before_validate(self):
		if not getattr(self, "ma", None):
			fallback = getattr(self, "noi_dung_ck", None) or getattr(self, "name", None)
			if fallback:
				self.ma = str(fallback).strip()

	def validate(self):
		nd = str(getattr(self, "noi_dung_ck", None) or "").strip()
		if nd:
			self.noi_dung_ck = nd
			trung = frappe.db.exists("LX Don", {"noi_dung_ck": nd, "name": ["!=", self.name]})
			if trung:
				frappe.throw(f"Nội dung chuyển khoản {nd} đã tồn tại ở đơn {trung}")

