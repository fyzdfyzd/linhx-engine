import logging

from frappe.model.document import Document

from linhx_core.crm import co_hoi
from linhx_core.crm.quyen_don_vi import kiem_tra_quyen_doc

logger = logging.getLogger(__name__)
USER_LOAI_TRU = ("Administrator", "Guest")
VAI_TRO_CRM = ("LX Nhan Vien", "Sales User", "Sales Manager", "CRM User")


def _lay_tao_luc(doc) -> str:
	tao_luc = getattr(doc, "creation", None)
	if tao_luc:
		return co_hoi._parse_tg(tao_luc).strftime(co_hoi.DINH_DANG_TG)
	try:
		import frappe

		now_dt = getattr(getattr(frappe, "utils", None), "now_datetime", None)
		if callable(now_dt):
			return co_hoi._parse_tg(now_dt()).strftime(co_hoi.DINH_DANG_TG)
	except (ImportError, AttributeError):
		pass
	return co_hoi.bay_gio()


def _ghi_log_loi(tieu_de: str, chi_tiet: str) -> None:
	logger.warning("%s: %s", tieu_de, chi_tiet)
	try:
		import frappe

		log_err = getattr(frappe, "log_error", None)
		if callable(log_err) and getattr(frappe, "db", None):
			log_err(message=chi_tiet, title=tieu_de)
	except Exception:
		pass


def _loc_ung_vien_crm(frappe_mod, ds_user: list[str], don_vi: str | None) -> list[str]:
	if not ds_user:
		return []
	ket_qua = list(ds_user)
	try:
		co_vai_tro = set(
			frappe_mod.get_all(
				"Has Role",
				filters={
					"parenttype": "User",
					"parent": ["in", ket_qua],
					"role": ["in", list(VAI_TRO_CRM)],
				},
				pluck="parent",
			)
			or []
		)
	except Exception as exc:
		_ghi_log_loi("LX Co Hoi: lỗi truy vấn vai trò CRM", str(exc))
		return []
	ket_qua = [u for u in ket_qua if u in co_vai_tro]
	if not ket_qua:
		return []

	if don_vi:
		try:
			co_don_vi = set(
				frappe_mod.get_all(
					"User Permission",
					filters={
						"user": ["in", ket_qua],
						"allow": "LX Don Vi",
						"for_value": don_vi,
					},
					pluck="user",
				)
				or []
			)
		except Exception as exc:
			_ghi_log_loi("LX Co Hoi: lỗi truy vấn quyền đơn vị", str(exc))
			return []
		ket_qua = [u for u in ket_qua if u in co_don_vi]
	return ket_qua


class LXCoHoi(Document):
	def _gan_don_vi_tu_nguoi(self):
		if not getattr(self, "don_vi", None) and getattr(self, "nguoi", None):
			try:
				import frappe

				if getattr(frappe, "db", None):
					dv = frappe.db.get_value("LX Nguoi", self.nguoi, "don_vi")
					if dv:
						self.don_vi = dv
			except (ImportError, AttributeError):
				pass
			except Exception as exc:
				_ghi_log_loi("LX Co Hoi: lỗi đọc đơn vị từ LX Nguoi", str(exc))

	def validate(self):
		self._gan_don_vi_tu_nguoi()
		kiem_tra_quyen_doc(self, "validate")

	def before_insert(self):
		if not getattr(self, "trang_thai", None):
			self.trang_thai = "moi"
		tao_luc = _lay_tao_luc(self)
		han_toi_da = co_hoi.han_giao(tao_luc)
		han_hien_tai = getattr(self, "han_giao", None)
		if not han_hien_tai:
			self.han_giao = han_toi_da
		else:
			try:
				dt_hien_tai = co_hoi._parse_tg(han_hien_tai)
				dt_toi_da = co_hoi._parse_tg(han_toi_da)
				if dt_hien_tai > dt_toi_da:
					self.han_giao = han_toi_da
				else:
					self.han_giao = dt_hien_tai.strftime(co_hoi.DINH_DANG_TG)
			except ValueError:
				self.han_giao = han_toi_da

		self._gan_don_vi_tu_nguoi()
		kiem_tra_quyen_doc(self, "before_insert")

		if not getattr(self, "phu_trach", None):
			self._tu_giao_phu_trach()

	def _tu_giao_phu_trach(self):
		ds_phu_trach = getattr(self, "_ds_phu_trach", None)
		ds_mo = getattr(self, "_ds_co_hoi_mo", None)
		if ds_phu_trach is None:
			try:
				import frappe

				if getattr(frappe, "db", None) and callable(getattr(frappe, "get_all", None)):
					ds_user = frappe.get_all(
						"User",
						filters={
							"enabled": 1,
							"user_type": "System User",
							"name": ["not in", list(USER_LOAI_TRU)],
						},
						pluck="name",
						order_by="creation asc",
					)
					ds_phu_trach = _loc_ung_vien_crm(
						frappe,
						list(ds_user or []),
						getattr(self, "don_vi", None),
					)
				else:
					ds_phu_trach = []
			except (ImportError, AttributeError):
				ds_phu_trach = []
			except Exception as exc:
				_ghi_log_loi("LX Co Hoi: lỗi truy vấn người phụ trách", str(exc))
				ds_phu_trach = []

		if not ds_phu_trach:
			_ghi_log_loi(
				"LX Co Hoi: chưa có người phụ trách khả dụng",
				f"Cơ hội {getattr(self, 'name', '') or '(mới)'} chưa giao được do danh sách người phụ trách trống.",
			)
			return

		if ds_mo is None:
			try:
				import frappe

				if getattr(frappe, "db", None) and callable(getattr(frappe, "get_all", None)):
					ds_mo = frappe.get_all(
						"LX Co Hoi",
						filters={"trang_thai": ["in", ["moi", "dang_lam"]]},
						fields=["name", "phu_trach", "trang_thai"],
					)
				else:
					ds_mo = []
			except (ImportError, AttributeError):
				ds_mo = []
			except Exception as exc:
				_ghi_log_loi("LX Co Hoi: lỗi truy vấn cơ hội đang mở", str(exc))
				ds_mo = []

		nguoi_nhan = co_hoi.giao(
			{"name": getattr(self, "name", None)},
			list(ds_phu_trach),
			list(ds_mo or []),
		)
		if nguoi_nhan:
			self.phu_trach = nguoi_nhan
