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
		gioi_han = (
			("brand", 80, "Thương hiệu"),
			("email", 120, "Email khách"),
			("nganh", 80, "Ngành"),
			("thi_truong", 60, "Thị trường"),
			("doi_thu", 120, "Đối thủ"),
			("su_that", 600, "Sự thật thương hiệu"),
		)
		for truong, toi_da, nhan in gioi_han:
			gt = getattr(self, truong, None)
			if gt is not None:
				chuoi = str(gt).replace("\r", " ").replace("\n", " ").strip()
				if len(chuoi) > toi_da:
					frappe.throw(f"{nhan} vượt quá {toi_da} ký tự")
				setattr(self, truong, chuoi or None)
		if not self.is_new():
			has_changed = getattr(self, "has_value_changed", None)
			if callable(has_changed) and any(
				has_changed(t) for t in ("goi", "so_tien", "trang_thai", "brand", "email", "nganh", "thi_truong", "doi_thu", "su_that")
			):
				self.so_lan_thu_job = 0
				self.lan_thu_job_cuoi = None

	def on_update(self):
		if getattr(self, "trang_thai", None) == "da_tra":
			ghi_so_s1a_tu_don(self)

	def on_doctype_update(self):
		_chuan_hoa_tx_id_rong()
