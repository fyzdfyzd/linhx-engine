import frappe
from frappe.model.document import Document


class LXJob(Document):
	def before_validate(self):
		don = str(getattr(self, "don", None) or "").strip()
		self.don = don if don else None

	def validate(self):
		don = str(getattr(self, "don", None) or "").strip()
		if don:
			self.don = don
			trung = frappe.db.exists("LX Job", {"don": don, "name": ["!=", self.name]})
			if trung:
				frappe.throw(f"Đơn {don} đã có việc {trung}")

