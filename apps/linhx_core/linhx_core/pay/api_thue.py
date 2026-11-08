"""API cảnh báo ngưỡng doanh thu thuế S1a-HKD cho bàn điều hành."""
from __future__ import annotations

import frappe
from frappe.utils import now_datetime

from linhx_core.co_module import _doc_cau_hinh_frappe, doctype_bi_an
from linhx_core.pay.so_s1a import NGUONG_MAC_DINH, canh_bao


def _la_dieu_hanh() -> None:
	nguoi_dung = getattr(getattr(frappe, "session", None), "user", "Guest") or "Guest"
	if nguoi_dung == "Guest":
		frappe.throw("Cần đăng nhập điều hành", frappe.PermissionError)
	roles = set(frappe.get_roles(nguoi_dung))
	if not (roles & {"System Manager", "LX Operator", "Administrator"}):
		frappe.throw("Cần quyền LX Operator", frappe.PermissionError)
	if nguoi_dung != "Administrator" and doctype_bi_an("LX So S1a", _doc_cau_hinh_frappe()):
		frappe.throw("Module Pay đang tắt", frappe.PermissionError)


def _doc_nguong_cau_hinh() -> int:
	if frappe.db.exists("DocType", "LX Cau Hinh Pay"):
		try:
			val = frappe.db.get_single_value("LX Cau Hinh Pay", "nguong_doanh_thu")
			if val is not None and float(val) > 0:
				return int(round(float(val)))
		except Exception:
			pass
	return NGUONG_MAC_DINH


@frappe.whitelist()
def canh_bao_thue(nam: int | None = None):
	"""Trả cảnh báo doanh thu năm hiện tại (hoặc `nam` truyền vào) theo sổ `LX So S1a` và ngưỡng `LX Cau Hinh Pay`."""
	_la_dieu_hanh()
	if nam is not None and str(nam).strip() != "":
		try:
			nam_tinh = int(nam)
		except (TypeError, ValueError):
			frappe.throw("Năm tra cứu không hợp lệ")
	else:
		nam_tinh = now_datetime().year

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
