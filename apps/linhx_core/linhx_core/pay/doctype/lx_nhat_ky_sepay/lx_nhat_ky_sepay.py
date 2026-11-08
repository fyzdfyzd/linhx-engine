import frappe
from frappe.model.document import Document


class LXNhatKySepay(Document):
	def autoname(self):
		if getattr(self, "tx_id", None):
			self.name = str(self.tx_id).strip()

	def on_trash(self):
		frappe.throw("Không được xoá bản ghi nhật ký đối soát SePay")
