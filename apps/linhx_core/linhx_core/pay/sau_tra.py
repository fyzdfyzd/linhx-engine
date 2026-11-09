"""Xử lý sau khi đơn báo cáo chuyển sang `da_tra`: tự sinh `LX Job` vào hàng chờ ngay và tạo đường dẫn báo cáo.

Chuyển từ: nguon/03-opc-os/modules/03_flow_thanh_toan_sinh_report/module.py
(handle_sepay_webhook: khi đơn chuyển sang paid và đủ tiền thì phát sự kiện don.da_tra / don_hang.da_thanh_toan
để sinh báo cáo tự động ngay không cần duyệt tay).
"""
from __future__ import annotations

from linhx_core.pay.quyen_dung import gia_hop_le

NGUON_PROTO = "nguon/03-opc-os/modules/03_flow_thanh_toan_sinh_report/module.py"


def mot_dong(gt: object, toi_da: int, mac_dinh: str = "") -> str:
	"""Chuẩn hoá giá trị thành một dòng đơn (bỏ CR/LF, khoảng trắng thừa) và cắt theo `toi_da`."""
	chuoi = str(gt if gt is not None else "").replace("\r", " ").replace("\n", " ").strip()
	if not chuoi and mac_dinh:
		chuoi = mac_dinh
	return chuoi[:toi_da]


_mot_dong = mot_dong


def tao_dau_vao(don: dict) -> str:
	"""Tạo chuỗi `dau_vao` 5 dòng chuẩn cho workflow báo cáo từ các trường đã cắt ngắn và loại xuống dòng."""
	brand = mot_dong(don.get("brand") or don.get("thuong_hieu"), 80)
	nganh = mot_dong(don.get("nganh"), 80)
	thi_truong = mot_dong(don.get("thi_truong"), 60, mac_dinh="Việt Nam")
	doi_thu = mot_dong(don.get("doi_thu"), 120)
	su_that = mot_dong(don.get("su_that"), 600)

	return "\n".join(
		[
			f"brand: {brand}",
			f"nganh: {nganh}",
			f"thi_truong: {thi_truong}",
			f"doi_thu: {doi_thu}",
			f"su_that: {su_that}",
		]
	)


_tao_dau_vao = tao_dau_vao


def viec_can_tao(don: dict, goi: dict, job_da_co: list[dict] | None) -> dict | None:
	"""Xác định `LX Job` cần tạo cho đơn đã trả.

	Chỉ tạo khi:
	- `don["trang_thai"] == "da_tra"`
	- `goi` có `"workflow"` hợp lệ
	- Chưa có job nào trong `job_da_co` có `job["don"] == don["ma"]`
	- `don["so_tien"]` có mặt và đạt giá sàn của `goi`.

	Trả dict với `trang_thai = "cho"` (vào hàng ngay, bỏ duyệt tay) và `nguon = "don"`.
	"""
	if not isinstance(don, dict) or not isinstance(goi, dict):
		return None
	if don.get("trang_thai") != "da_tra":
		return None

	workflow = str(goi.get("workflow") or "").strip()
	if not workflow:
		return None

	ma_don = str(don.get("ma") or don.get("name") or "").strip()
	if not ma_don:
		return None

	ma_goi_don = str(don.get("goi") or "").strip()
	ma_goi = str(goi.get("ma") or goi.get("name") or "").strip()
	if ma_goi_don and ma_goi and ma_goi_don not in {
		str(goi.get("ma") or "").strip(),
		str(goi.get("name") or "").strip(),
	}:
		return None

	if not gia_hop_le(don.get("so_tien"), goi):
		return None

	for j in job_da_co or []:
		if isinstance(j, dict) and str(j.get("don") or "").strip() == ma_don:
			return None

	email = don.get("email")
	if isinstance(email, str):
		email = email.replace("\r", " ").replace("\n", " ").strip()[:120] or None

	return {
		"workflow": workflow,
		"dau_vao": _tao_dau_vao(don),
		"trang_thai": "cho",
		"nguon": "don",
		"don": ma_don,
		"email_khach": email,
	}


def link_bao_cao(job: dict, goc_url: str) -> str:
	"""Ghép đường dẫn xem báo cáo của khách: `<goc_url>/#/bao-cao/<job name>/<ma_xem>`."""
	if not isinstance(job, dict):
		raise ValueError("job phải là dict")
	ten_job = str(job.get("name") or job.get("viec") or "").strip()
	ma_xem = str(job.get("ma_xem") or "").strip()
	if not ten_job or not ma_xem:
		raise ValueError("job phải có name và ma_xem")
	goc = str(goc_url or "").strip().rstrip("/")
	return f"{goc}/#/bao-cao/{ten_job}/{ma_xem}"


def _tim_goi_db(frappe_mod, ma_hoac_ten: str) -> dict | None:
	"""Đọc bản ghi `LX Goi` theo `name` hoặc `ma`."""
	if not ma_hoac_ten or not frappe_mod.db.table_exists("LX Goi"):
		return None
	fields = ["name", "ma", "ten", "gia", "gia_san", "workflow", "ban"]
	rows = frappe_mod.get_all(
		"LX Goi",
		filters={"name": ma_hoac_ten},
		fields=fields,
		limit_page_length=1,
		ignore_permissions=True,
	)
	if not rows:
		rows = frappe_mod.get_all(
			"LX Goi",
			filters={"ma": ma_hoac_ten},
			fields=fields,
			limit_page_length=1,
			ignore_permissions=True,
		)
	if not rows:
		return None
	d = dict(rows[0])
	d["ma"] = d.get("ma") or d.get("name")
	return d


def _ghi_log_loi_don_mot_lan(frappe_mod, doc, title: str, message: str) -> None:
	"""Chỉ ghi `Error Log` tối đa một lần cho mỗi đơn và mỗi loại lỗi khi `on_update` lặp lại.

	Trong Frappe v15 (`frappe.core.doctype.error_log.error_log.log_error`), `frappe.log_error(title=..., message=...)`
	lưu `title` vào cột `method` và `message` vào cột `error` của bảng `tabError Log`.
	"""
	da_log = getattr(doc, "_da_log_loi_sau_tra", None)
	if isinstance(da_log, set) and title in da_log:
		return
	db = getattr(frappe_mod, "db", None)
	try:
		if (
			db is not None
			and getattr(db, "table_exists", None)
			and db.table_exists("Error Log")
			and getattr(db, "exists", None)
			and db.exists("Error Log", {"method": title})
		):
			return
	except Exception:
		pass
	frappe_mod.log_error(title=title, message=message)
	try:
		if not isinstance(da_log, set):
			da_log = set()
			setattr(doc, "_da_log_loi_sau_tra", da_log)
		da_log.add(title)
	except Exception:
		pass


def _loai_loi_trung_khoa(frappe_mod) -> tuple[type[BaseException], ...]:
	"""Trả tuple các lớp ngoại lệ trùng khoá/validate của Frappe để tách riêng với lỗi DB khác."""
	ket_qua: list[type[BaseException]] = []
	for ten in ("DuplicateEntryError", "UniqueValidationError"):
		cls = getattr(frappe_mod, ten, None)
		if isinstance(cls, type) and issubclass(cls, BaseException):
			ket_qua.append(cls)
	return tuple(ket_qua)


def xu_ly_sau_tra(doc, method: str | None = None) -> dict | None:
	"""Hook `doc_events` (`LX Don.on_update` / `on_change`): tự tạo `LX Job` ngay khi đơn `da_tra`."""
	import frappe

	if getattr(doc, "trang_thai", None) != "da_tra":
		return None
	if not frappe.db.table_exists("LX Job") or not frappe.db.table_exists("LX Goi"):
		return None

	ten_don = str(getattr(doc, "name", None) or "").strip()
	ma_don = str(getattr(doc, "ma", None) or ten_don).strip()
	if not ma_don:
		return None

	# Khoá dòng đơn để tuần tự hoá khi nhiều tiến trình cập nhật cùng một đơn
	if ten_don and frappe.db.table_exists("LX Don"):
		frappe.db.sql(
			"SELECT name FROM `tabLX Don` WHERE name = %s FOR UPDATE",
			(ten_don,),
		)

	goi_id = str(getattr(doc, "goi", None) or "").strip()
	goi = _tim_goi_db(frappe, goi_id)
	if not goi:
		_ghi_log_loi_don_mot_lan(
			frappe,
			doc,
			title=f"Đơn {ma_don} đã trả nhưng không tìm thấy gói",
			message=f"Đơn {ma_don} đã trả nhưng không tìm thấy bản ghi LX Goi '{goi_id}'.",
		)
		return None

	job_da_co = frappe.db.sql(
		"SELECT name, don, ma_xem, trang_thai FROM `tabLX Job` WHERE don = %s",
		(ma_don,),
		as_dict=True,
	)

	don_dict = {
		"name": ten_don,
		"ma": ma_don,
		"goi": goi_id,
		"so_tien": getattr(doc, "so_tien", None),
		"trang_thai": getattr(doc, "trang_thai", None),
		"brand": getattr(doc, "brand", None),
		"email": getattr(doc, "email", None),
		"nganh": getattr(doc, "nganh", None),
		"thi_truong": getattr(doc, "thi_truong", None),
		"doi_thu": getattr(doc, "doi_thu", None),
		"su_that": getattr(doc, "su_that", None),
	}
	viec = viec_can_tao(don_dict, goi, list(job_da_co or []))
	if not viec:
		if job_da_co:
			j0 = job_da_co[0]
			return {
				"name": j0.get("name"),
				"ma_xem": j0.get("ma_xem"),
				"don": ma_don,
				"trang_thai": j0.get("trang_thai"),
			}
		if don_dict.get("so_tien") is None:
			_ghi_log_loi_don_mot_lan(
				frappe,
				doc,
				title=f"Đơn {ma_don} đã trả nhưng thiếu số tiền",
				message=f"Đơn {ma_don} (gói {goi_id}) ở trạng thái da_tra nhưng thiếu so_tien; không tự sinh LX Job.",
			)
		elif not gia_hop_le(don_dict.get("so_tien"), goi):
			_ghi_log_loi_don_mot_lan(
				frappe,
				doc,
				title=f"Đơn {ma_don} đã trả dưới giá sàn",
				message=(
					f"Đơn {ma_don} (gói {goi_id}) ở trạng thái da_tra với so_tien={don_dict.get('so_tien')} "
					f"thấp hơn giá sàn của gói (gia_san={goi.get('gia_san')}, gia={goi.get('gia')}); "
					"không tự sinh LX Job."
				),
			)
		return None

	ma_xem = frappe.generate_hash(length=12)
	loi_trung = _loai_loi_trung_khoa(frappe)
	try:
		job_doc = frappe.get_doc(
			{
				"doctype": "LX Job",
				"workflow": viec["workflow"],
				"dau_vao": viec["dau_vao"],
				"trang_thai": "cho",
				"nguon": "don",
				"don": viec["don"],
				"email_khach": viec.get("email_khach"),
				"ma_xem": ma_xem,
			}
		)
		job_doc.insert(ignore_permissions=True)
	except Exception as exc:
		la_loi_trung = bool(loi_trung and isinstance(exc, loi_trung)) or (
			"Duplicate entry" in str(exc) or f"Đơn {ma_don} đã có việc" in str(exc)
		)
		if la_loi_trung:
			job_sau_loi = frappe.db.sql(
				"SELECT name, don, ma_xem, trang_thai FROM `tabLX Job` WHERE don = %s",
				(ma_don,),
				as_dict=True,
			)
			if job_sau_loi:
				j0 = job_sau_loi[0]
				return {
					"name": j0.get("name"),
					"ma_xem": j0.get("ma_xem"),
					"don": ma_don,
					"trang_thai": j0.get("trang_thai"),
				}
		tb = ""
		lay_tb = getattr(frappe, "get_traceback", None)
		if callable(lay_tb):
			try:
				tb = str(lay_tb() or "").strip()
			except Exception:
				tb = ""
		chi_tiet = f"{exc}\n{tb}".strip() if tb else str(exc)
		_ghi_log_loi_don_mot_lan(
			frappe,
			doc,
			title=f"Lỗi tạo LX Job cho đơn {ma_don}",
			message=f"Đơn {ma_don} đã trả nhưng tạo LX Job thất bại ({type(exc).__name__}): {chi_tiet}",
		)
		return None

	return {
		"name": job_doc.name,
		"ma_xem": ma_xem,
		"don": viec["don"],
		"trang_thai": job_doc.trang_thai,
	}
