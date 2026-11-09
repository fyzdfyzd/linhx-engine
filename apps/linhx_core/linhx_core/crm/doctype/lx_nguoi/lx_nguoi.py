import json

from frappe.model.document import Document

from linhx_core.crm import gop_trung
from linhx_core.crm.quyen_don_vi import (
	kiem_ghi,
	kiem_tra_quyen_doc,
	la_user_mien,
	lay_don_vi_cua_user,
)
from linhx_core.linhx_core.doctype.lx_nhat_ky_truy_cap.lx_nhat_ky_truy_cap import ghi_nhat_ky_truy_cap

TRUONG_CO_BAN = (
	"ho_ten",
	"dien_thoai",
	"email",
	"zalo",
	"don_vi",
	"to_chuc",
	"nguon",
	"tang_pheu",
	"t1_tong",
	"t1_muc",
	"lich_su_t1",
	"ghi_cong",
)
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

	def validate(self):
		kiem_tra_quyen_doc(self, "validate")

	def before_insert(self):
		kiem_tra_quyen_doc(self, "before_insert")
		self._gop_trung_khi_them()

	def _gop_trung_khi_them(self):
		cac_truong = self._cac_truong_du_lieu()
		ban_moi = {f: getattr(self, f, None) for f in cac_truong}
		dv_moi = str(ban_moi.get("don_vi") or "").strip()
		if not dv_moi:
			return
		khoa_moi = gop_trung.khoa_gop(ban_moi)
		if not khoa_moi:
			return

		bo_qua_quyen = bool(getattr(getattr(self, "flags", None), "ignore_permissions", False))
		mien = la_user_mien() or bo_qua_quyen
		ds_don_vi = [] if mien else lay_don_vi_cua_user()
		if not mien and dv_moi not in ds_don_vi:
			return

		try:
			import frappe

			ds_cu = frappe.get_all(
				"LX Nguoi",
				filters={"don_vi": dv_moi},
				fields=["name", *cac_truong],
				order_by="creation asc",
			)
		except Exception:
			return

		for cu in ds_cu:
			dv_cu = str(cu.get("don_vi") or "").strip()
			if not dv_cu or dv_cu != dv_moi:
				continue
			if not kiem_ghi({"don_vi": dv_moi}, {"don_vi": dv_cu}, None, ds_don_vi, mien):
				continue
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

			dv_moi = str(getattr(self, "don_vi", None) or "").strip()
			dv_cu_db = ""
			if getattr(frappe, "db", None) and callable(getattr(frappe.db, "get_value", None)):
				dv_cu_db = str(frappe.db.get_value("LX Nguoi", ten_cu, "don_vi") or "").strip()
			doc_cu = {"don_vi": dv_cu_db}
			bo_qua_quyen = bool(getattr(getattr(self, "flags", None), "ignore_permissions", False))
			mien = la_user_mien() or bo_qua_quyen
			ds_don_vi = [] if mien else lay_don_vi_cua_user()
			if (
				not dv_moi
				or not dv_cu_db
				or dv_cu_db != dv_moi
				or not kiem_ghi({"don_vi": dv_moi}, doc_cu, None, ds_don_vi, mien)
			):
				frappe.throw(
					"Không có quyền ghi đè bản ghi LX Nguoi của đơn vị khác",
					frappe.PermissionError,
				)

			self.name = ten_cu
			for f in self._cac_truong_du_lieu():
				if f == "don_vi":
					continue
				val = getattr(self, f, None)
				if val is not None:
					if isinstance(val, (dict, list)):
						val = json.dumps(val, ensure_ascii=False)
					frappe.db.set_value("LX Nguoi", ten_cu, f, val, update_modified=True)
			return
		return super().db_insert(*args, **kwargs)
