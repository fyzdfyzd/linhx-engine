from frappe.model.document import Document


class LXGoi(Document):
	def autoname(self):
		if getattr(self, "ma", None):
			self.name = str(self.ma).strip()
		elif getattr(self, "ten", None):
			self.name = str(self.ten).strip()
