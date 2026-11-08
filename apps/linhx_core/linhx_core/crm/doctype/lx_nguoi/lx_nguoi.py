from frappe.model.document import Document

from linhx_core.crm import gop_trung
from linhx_core.linhx_core.doctype.lx_nhat_ky_truy_cap.lx_nhat_ky_truy_cap import ghi_nhat_ky_truy_cap

TRUONG_CO_BAN = ("ho_ten", "dien_thoai", "email", "zalo", "don_vi", "to_chuc")
TRUONG_HE_THONG = {
	"name",
	"creation",
	"modified",
	"modified_by",
	"owner",
	"docstatus",
	"idx",
	"doctype",
	"parent",
	"parentfield",
	"parenttype",
	"_user_tags",
	"_comments",
	"_assign",
	"_liked_by",
}


class LXNguoi(Document):
	def _cac_truong_du_lieu(self) -> list[str]:
		if getattr(self, "meta", None) and hasattr(self.meta, "get_valid_columns"):
			return [c for c in self.meta.get_valid_columns() if c not in TRUONG_HE_THONG]
		return list(TRUONG_CO_BAN)

	def onload(self):
		ghi_nhat_ky_truy_cap(self, "onload")

	def before_insert(self):
		self._gop_trung_khi_them()

	def _gop_trung_khi_them(self):
		cac_truong = self._cac_truong_du_lieu()
		ban_moi = {f: getattr(self, f, None) for f in cac_truong}
		khoa_moi = gop_trung.khoa_gop(ban_moi)
		if not khoa_moi:
			return
		try:
			import frappe

			ds_cu = frappe.get_all(
				"LX Nguoi",
				fields=["name", *cac_truong],
				order_by="creation asc",
			)
		except Exception:
			return

		for cu in ds_cu:
			if gop_trung.khoa_gop(cu) & khoa_moi:
				da_gop = gop_trung.gop([cu], ban_moi)[0]
				for f in cac_truong:
					if da_gop.get(f) is not None:
						setattr(self, f, da_gop.get(f))
				self._gop_vao_name = cu.get("name")
				return

	def db_insert(self, *args, **kwargs):
		ten_cu = getattr(self, "_gop_vao_name", None)
		if ten_cu:
			import frappe

			self.name = ten_cu
			for f in self._cac_truong_du_lieu():
				val = getattr(self, f, None)
				if val is not None:
					frappe.db.set_value("LX Nguoi", ten_cu, f, val, update_modified=True)
			return
		return super().db_insert(*args, **kwargs)
