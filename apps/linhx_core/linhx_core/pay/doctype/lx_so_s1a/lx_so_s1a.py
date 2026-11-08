import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class LXSoS1a(Document):
	def autoname(self):
		if getattr(self, "ma_don", None):
			self.name = str(self.ma_don).strip()

	def before_validate(self):
		if not getattr(self, "ngay", None):
			self.ngay = nowdate()
		if getattr(self, "ma_don", None):
			self.ma_don = str(self.ma_don).strip()

	def validate(self):
		ma = str(getattr(self, "ma_don", None) or "").strip()
		if not ma:
			frappe.throw("Mã đơn trên dòng sổ S1a không được để trống")
		self.ma_don = ma
		trung = frappe.db.exists("LX So S1a", {"ma_don": ma, "name": ["!=", self.name]})
		if trung:
			frappe.throw(
				f"Mã đơn {ma} đã được ghi trong sổ S1a ({trung})",
				frappe.DuplicateEntryError,
			)
		try:
			tien = float(getattr(self, "so_tien", 0) or 0)
		except (TypeError, ValueError):
			tien = -1
		if tien <= 0:
			frappe.throw("Số tiền ghi sổ S1a phải lớn hơn 0")
