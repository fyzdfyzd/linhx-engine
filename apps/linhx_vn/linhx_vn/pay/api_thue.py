"""API cảnh báo ngưỡng doanh thu thuế S1a-HKD cho bàn điều hành."""
from __future__ import annotations

try:
	from linhx_core.api import doc_cau_hinh, doctype_bi_an
except ModuleNotFoundError:
	doc_cau_hinh = None
	doctype_bi_an = None

from linhx_vn.pay.so_s1a import NGUONG_MAC_DINH, canh_bao


def _lay_frappe():
	try:
		import frappe
	except ImportError:
		return None
	return frappe


def _whitelist(fn):
	frappe = _lay_frappe()
	if frappe is not None and callable(getattr(frappe, "whitelist", None)):
		return frappe.whitelist()(fn)
	return fn


def _la_dieu_hanh() -> None:
	frappe = _lay_frappe()
	if frappe is None:
		raise RuntimeError("Cần môi trường Frappe để gọi canh_bao_thue")
	nguoi_dung = getattr(getattr(frappe, "session", None), "user", "Guest") or "Guest"
	if nguoi_dung == "Guest":
		frappe.throw("Cần đăng nhập điều hành", frappe.PermissionError)
	roles = set(frappe.get_roles(nguoi_dung))
	if not (roles & {"System Manager", "LX Operator", "Administrator"}):
		frappe.throw("Cần quyền LX Operator", frappe.PermissionError)
	kiem_an = doctype_bi_an
	if kiem_an is None:
		from linhx_core.api import doctype_bi_an as kiem_an
	if nguoi_dung != "Administrator" and kiem_an("LX So S1a"):
		frappe.throw("Module Pay đang tắt", frappe.PermissionError)


def _doc_nguong_cau_hinh() -> int:
	frappe = _lay_frappe()
	if doc_cau_hinh is not None:
		try:
			val_api = doc_cau_hinh("nguong_doanh_thu")
			if val_api is not None and float(val_api) > 0:
				return int(round(float(val_api)))
		except Exception:
			pass
	if frappe is not None and frappe.db.exists("DocType", "LX Cau Hinh Pay"):
		try:
			val = frappe.db.get_single_value("LX Cau Hinh Pay", "nguong_doanh_thu")
			if val is not None and float(val) > 0:
				return int(round(float(val)))
		except Exception:
			pass
	return NGUONG_MAC_DINH


@_whitelist
def canh_bao_thue(nam: int | None = None):
	"""Trả cảnh báo doanh thu năm hiện tại (hoặc `nam` truyền vào) theo sổ `LX So S1a` và ngưỡng `LX Cau Hinh Pay`."""
	frappe = _lay_frappe()
	if frappe is None:
		raise RuntimeError("Cần môi trường Frappe để gọi canh_bao_thue")

	_la_dieu_hanh()
	if nam is not None and str(nam).strip() != "":
		try:
			nam_tinh = int(nam)
		except (TypeError, ValueError):
			frappe.throw("Năm tra cứu không hợp lệ")
	else:
		try:
			from frappe.utils import now_datetime

			nam_tinh = now_datetime().year
		except ImportError:
			from datetime import datetime

			nam_tinh = datetime.now().year

	nguong = _doc_nguong_cau_hinh()
	ds_so: list[dict] = []
	if frappe.db.exists("DocType", "LX So S1a"):
		tu_ngay = f"{nam_tinh:04d}-01-01"
		den_ngay = f"{nam_tinh:04d}-12-31"
		rows = frappe.get_all(
			"LX So S1a",
			filters=[["ngay", ">=", tu_ngay], ["ngay", "<=", den_ngay]],
			fields=["ngay", "ma_don", "dien_giai", "so_tien"],
			order_by="ngay asc, creation asc",
			limit_page_length=0,
		)
		for r in rows:
			ds_so.append(
				{
					"ngay": str(r.get("ngay") or ""),
					"ma_don": str(r.get("ma_don") or ""),
					"dien_giai": str(r.get("dien_giai") or ""),
					"so_tien": r.get("so_tien") or 0,
				}
			)

	return canh_bao(ds_so, nam_tinh, nguong=nguong)
