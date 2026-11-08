import frappe
from frappe.model.document import Document


class LXCauHinhPay(Document):
	def validate(self):
		if getattr(self, "nguong_doanh_thu", None) is not None:
			try:
				val = float(self.nguong_doanh_thu)
			except (TypeError, ValueError):
				frappe.throw("Ngưỡng doanh thu không hợp lệ")
			if val < 0:
				frappe.throw("Ngưỡng doanh thu không được âm")
