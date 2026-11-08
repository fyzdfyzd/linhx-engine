from frappe.model.document import Document


class LXDon(Document):
	def autoname(self):
		if getattr(self, "ma", None):
			self.name = str(self.ma).strip()
