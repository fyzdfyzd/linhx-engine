import frappe
from frappe.model.document import Document


class LXJob(Document):
	def before_validate(self):
		don = str(getattr(self, "don", None) or "").strip()
		self.don = don if don else None

	def validate(self):
		don = str(getattr(self, "don", None) or "").strip()
		self.don = don if don else None
		if self.don:
			trung = frappe.db.exists("LX Job", {"don": self.don, "name": ["!=", self.name]})
			if trung:
				frappe.throw(f"Đơn {self.don} đã có việc {trung}")

	def on_doctype_update(self):
		frappe.db.sql("UPDATE `tabLX Job` SET `don` = NULL WHERE `don` = ''")
		frappe.db.add_unique("LX Job", ["don"])
