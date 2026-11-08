from datetime import datetime

from frappe.model.document import Document

from linhx_core.crm import co_hoi


class LXCoHoi(Document):
	def before_insert(self):
		if not getattr(self, "trang_thai", None):
			self.trang_thai = "moi"
		if not getattr(self, "han_giao", None):
			tao_luc = getattr(self, "creation", None) or datetime.now().strftime(co_hoi.DINH_DANG_TG)
			self.han_giao = co_hoi.han_giao(tao_luc)
		if not getattr(self, "don_vi", None) and getattr(self, "nguoi", None):
			try:
				import frappe

				dv = frappe.db.get_value("LX Nguoi", self.nguoi, "don_vi")
				if dv:
					self.don_vi = dv
			except Exception:
				pass
		if not getattr(self, "phu_trach", None):
			self._tu_giao_phu_trach()

	def _tu_giao_phu_trach(self):
		ds_phu_trach = getattr(self, "_ds_phu_trach", None)
		ds_mo = getattr(self, "_ds_co_hoi_mo", None)
		if ds_phu_trach is None:
			try:
				import frappe

				users = frappe.get_all(
					"User",
					filters={
						"enabled": 1,
						"user_type": "System User",
						"name": ["not in", ["Guest"]],
					},
					pluck="name",
					order_by="creation asc",
				)
				thuong = [u for u in users if u != "Administrator"]
				ds_phu_trach = thuong or users
				if ds_mo is None and ds_phu_trach:
					ds_mo = frappe.get_all(
						"LX Co Hoi",
						filters={"trang_thai": ["in", ["moi", "dang_lam"]]},
						fields=["name", "phu_trach", "trang_thai"],
					)
			except Exception:
				ds_phu_trach = []
				ds_mo = []
		if ds_phu_trach:
			nguoi_nhan = co_hoi.giao(
				{"name": getattr(self, "name", None)},
				list(ds_phu_trach),
				list(ds_mo or []),
			)
			if nguoi_nhan:
				self.phu_trach = nguoi_nhan
