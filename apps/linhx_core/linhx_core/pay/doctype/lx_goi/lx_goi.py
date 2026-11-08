import frappe
from frappe.model.document import Document

from linhx_core.pay import dang_ky_auth_hook


class LXGoi(Document):
	def autoname(self):
		dang_ky_auth_hook()
		# Chỉ đặt name theo ma hoặc ten khi chưa trùng bản ghi hiện có;
		# nếu đã tồn tại bản ghi trùng tên thì để Frappe tự sinh name duy nhất.
		ung_vien = None
		if getattr(self, "ma", None):
			ung_vien = str(self.ma).strip()
		elif getattr(self, "ten", None):
			ung_vien = str(self.ten).strip()
		if ung_vien and not frappe.db.exists("LX Goi", ung_vien):
			self.name = ung_vien
