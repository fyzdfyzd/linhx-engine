"""Sổ doanh thu S1a-HKD và cảnh báo ngưỡng doanh thu thuế theo năm.

Chuyển từ: nguon/03-opc-os/modules/07_chi_phi_loi_nhuan/module.py
(FinanceLedgerModule.record_paid_order: ghi một dòng sổ doanh thu khi đơn chuyển da_tra,
chống ghi trùng ma_don, tính luỹ kế doanh thu và bật cảnh báo khi chạm ngưỡng).
"""
from __future__ import annotations

from datetime import date
import json
import re

NGUON_PROTO = "nguon/03-opc-os/modules/07_chi_phi_loi_nhuan/module.py"
NGUONG_MAC_DINH = 1_000_000_000


def _chuan_ngay(ngay: object) -> str:
	if hasattr(ngay, "strftime"):
		s = ngay.strftime("%Y-%m-%d")
	else:
		s = str(ngay or "").strip()
	if len(s) >= 10:
		s = s[:10]
	if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
		return ""
	try:
		date.fromisoformat(s)
	except ValueError:
		return ""
	return s


def _chuan_so_tien(val: object) -> int | None:
	if val is None or isinstance(val, bool):
		return None
	try:
		tien_f = float(val)
	except (TypeError, ValueError):
		return None
	if tien_f <= 0:
		return None
	return int(round(tien_f))


def dong_so(don: dict, ngay: str) -> dict | None:
	"""Tạo dòng sổ S1a-HKD từ đơn đã trả (`trang_thai == "da_tra"`).

	Trả `{"ngay", "ma_don", "dien_giai", "so_tien"}` hoặc `None` nếu đơn chưa trả/không hợp lệ.
	"""
	if not isinstance(don, dict):
		return None
	if don.get("trang_thai") != "da_tra":
		return None

	raw_ma = (
		don.get("ma")
		if don.get("ma") is not None
		else (don.get("ma_don") if don.get("ma_don") is not None else don.get("name"))
	)
	if raw_ma is None or isinstance(raw_ma, bool):
		return None
	ma_don = str(raw_ma).strip()
	if not ma_don:
		return None

	so_tien = _chuan_so_tien(don.get("so_tien"))
	if so_tien is None:
		return None

	ngay_str = _chuan_ngay(ngay if ngay is not None else don.get("ngay"))
	if not ngay_str:
		return None

	dien_giai = str(don.get("dien_giai") or "").strip()
	if not dien_giai:
		goi = str(don.get("goi") or "").strip()
		brand = str(don.get("brand") or "").strip()
		if goi and brand:
			dien_giai = f"Thu tiền đơn {ma_don} - gói {goi} ({brand})"
		elif goi:
			dien_giai = f"Thu tiền đơn {ma_don} - gói {goi}"
		else:
			dien_giai = f"Thu tiền đơn {ma_don}"

	return {
		"ngay": ngay_str,
		"ma_don": ma_don,
		"dien_giai": dien_giai,
		"so_tien": so_tien,
	}


def ghi(so: list, don: dict, ngay: str) -> list:
	"""Ghi đơn `da_tra` vào danh sách sổ `so` (chống ghi trùng `ma_don`)."""
	ds = list(so) if isinstance(so, list) else []
	dong = dong_so(don, ngay)
	if dong is None:
		return ds
	if any(isinstance(r, dict) and str(r.get("ma_don") or "").strip() == dong["ma_don"] for r in ds):
		return ds
	ds.append(dong)
	if isinstance(so, list):
		so[:] = ds
		return so
	return ds


def tong_nam(so: list, nam: int) -> int:
	"""Tính tổng doanh thu trong sổ `so` của năm `nam`."""
	if not isinstance(so, list) or nam is None or isinstance(nam, bool):
		return 0
	try:
		nam_int = int(nam)
	except (TypeError, ValueError):
		return 0
	tien_to = f"{nam_int:04d}-"
	tong = 0
	for r in so:
		if not isinstance(r, dict):
			continue
		ngay_r = _chuan_ngay(r.get("ngay"))
		if not ngay_r.startswith(tien_to):
			continue
		tien = _chuan_so_tien(r.get("so_tien"))
		if tien is not None:
			tong += tien
	return tong


def canh_bao(so: list, nam: int, nguong: int | float | None = None) -> dict | None:
	"""Kiểm tra ngưỡng doanh thu năm:
	- `>= nguong`: `{"muc": "do", "tong", "nguong"}`
	- `>= 90% nguong`: `{"muc": "vang", "tong", "nguong"}`
	- Còn lại: `None`
	"""
	if nguong is None or isinstance(nguong, bool):
		nguong_int = NGUONG_MAC_DINH
	else:
		try:
			nguong_int = int(round(float(nguong)))
		except (TypeError, ValueError):
			nguong_int = NGUONG_MAC_DINH
		if nguong_int <= 0:
			nguong_int = NGUONG_MAC_DINH

	tong = tong_nam(so, nam)
	if tong >= nguong_int:
		return {"muc": "do", "tong": tong, "nguong": nguong_int}
	if tong * 10 >= nguong_int * 9:
		return {"muc": "vang", "tong": tong, "nguong": nguong_int}
	return None


def ghi_so_s1a_tu_don(doc_don, method: str | None = None) -> object | None:
	"""Tự động ghi một dòng `LX So S1a` trong Frappe khi `LX Don` ở trạng thái `da_tra`."""
	import frappe
	from frappe.utils import nowdate

	if getattr(doc_don, "trang_thai", None) != "da_tra":
		return None
	if not frappe.db.exists("DocType", "LX So S1a"):
		return None
	if hasattr(frappe.db, "table_exists") and not frappe.db.table_exists("LX So S1a"):
		return None

	don_dict = {
		"ma": getattr(doc_don, "ma", None) or getattr(doc_don, "name", None),
		"so_tien": getattr(doc_don, "so_tien", 0),
		"trang_thai": getattr(doc_don, "trang_thai", None),
		"goi": getattr(doc_don, "goi", None),
		"brand": getattr(doc_don, "brand", None),
	}
	ngay_raw = (
		getattr(doc_don, "ngay", None)
		or getattr(doc_don, "modified", None)
		or getattr(doc_don, "creation", None)
		or nowdate()
	)
	dong = dong_so(don_dict, str(ngay_raw))
	if dong is None:
		return None

	if frappe.db.exists("LX So S1a", {"ma_don": dong["ma_don"]}):
		return None

	try:
		ban_ghi = frappe.get_doc(
			{
				"doctype": "LX So S1a",
				"ngay": dong["ngay"],
				"ma_don": dong["ma_don"],
				"dien_giai": dong["dien_giai"],
				"so_tien": dong["so_tien"],
			}
		)
		ban_ghi.insert(ignore_permissions=True)
		return ban_ghi
	except frappe.DuplicateEntryError:
		return None


def nghe_don_da_tra(ban_ghi_su_kien: dict) -> object | None:
	"""Hàm nghe sự kiện `don.da_tra`: ghi dòng sổ `LX So S1a` cho đơn đã trả."""
	if not isinstance(ban_ghi_su_kien, dict):
		return None
	du_lieu = ban_ghi_su_kien.get("du_lieu")
	if isinstance(du_lieu, str):
		try:
			du_lieu = json.loads(du_lieu)
		except ValueError:
			return None
	if not isinstance(du_lieu, dict):
		return None
	ma_don = str(du_lieu.get("don") or "").strip()
	if not ma_don:
		return None
	try:
		import frappe
	except ImportError:
		return None
	if getattr(frappe, "db", None) is None:
		return None
	if not frappe.db.exists("LX Don", ma_don):
		return None
	doc_don = frappe.get_doc("LX Don", ma_don)
	return ghi_so_s1a_tu_don(doc_don)
