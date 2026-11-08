import frappe
from frappe.model.document import Document

from linhx_core.crm import dong_y


def _lay_luc_mac_dinh() -> str:
	try:
		now_dt = getattr(getattr(frappe, "utils", None), "now_datetime", None)
		if callable(now_dt):
			return dong_y._parse_tg(now_dt()).replace(microsecond=0).strftime(dong_y.DINH_DANG_TG)
	except Exception:
		pass
	return dong_y.bay_gio()


def _chan_sua_xoa(thong_diep: str) -> None:
	throw_fn = getattr(frappe, "throw", None)
	loi_quyen = getattr(frappe, "PermissionError", PermissionError)
	if callable(throw_fn):
		throw_fn(thong_diep, loi_quyen)
	raise loi_quyen(thong_diep)


def _bao_loi_du_lieu(thong_diep: str) -> None:
	throw_fn = getattr(frappe, "throw", None)
	loi_dl = getattr(frappe, "ValidationError", ValueError)
	if callable(throw_fn):
		throw_fn(thong_diep, loi_dl)
	raise ValueError(thong_diep)


class LXDongY(Document):
	def is_new(self) -> bool:
		is_new_super = getattr(super(), "is_new", None)
		if callable(is_new_super):
			return bool(is_new_super())
		return bool(getattr(self, "__islocal", True))

	def before_insert(self):
		if not getattr(self, "luc", None):
			self.luc = _lay_luc_mac_dinh()
		self.dong_y = 1 if dong_y._chuan_dong_y(getattr(self, "dong_y", 0)) else 0

	def validate(self):
		if not self.is_new():
			_chan_sua_xoa(
				"Bản ghi LX Dong Y là nhật ký bất biến, không được sửa; để rút đồng ý hãy thêm dòng mới với dong_y = 0"
			)
		nguoi = str(getattr(self, "nguoi", "") or "").strip()
		if not nguoi:
			_bao_loi_du_lieu("LX Dong Y bắt buộc phải có người (nguoi)")
		muc_dich = str(getattr(self, "muc_dich", "") or "").strip()
		if muc_dich not in dong_y.MUC_DICH:
			_bao_loi_du_lieu(f"Mục đích đồng ý không hợp lệ: {muc_dich!r}")
		if not getattr(self, "luc", None):
			self.luc = _lay_luc_mac_dinh()
		self.dong_y = 1 if dong_y._chuan_dong_y(getattr(self, "dong_y", 0)) else 0

	def db_update(self, *args, **kwargs):
		_chan_sua_xoa("Bản ghi LX Dong Y là nhật ký bất biến, không được cập nhật")

	def on_trash(self):
		_chan_sua_xoa("Bản ghi LX Dong Y là nhật ký bất biến, không được xoá")
