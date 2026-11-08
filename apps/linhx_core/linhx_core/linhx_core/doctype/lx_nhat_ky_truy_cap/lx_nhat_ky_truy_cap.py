from frappe.model.document import Document
from frappe.utils import now_datetime


class LXNhatKyTruyCap(Document):
	def before_insert(self):
		if not getattr(self, "thoi_diem", None):
			self.thoi_diem = now_datetime()
