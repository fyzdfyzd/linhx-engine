from frappe.model.document import Document

from linhx_core.linhx_core.doctype.lx_nhat_ky_truy_cap.lx_nhat_ky_truy_cap import ghi_nhat_ky_truy_cap


class LXDonVi(Document):
	def onload(self):
		ghi_nhat_ky_truy_cap(self, "onload")

	def autoname(self):
		if getattr(self, "ma", None):
			self.name = str(self.ma).strip()
		elif getattr(self, "ten", None):
			self.name = str(self.ten).strip()
