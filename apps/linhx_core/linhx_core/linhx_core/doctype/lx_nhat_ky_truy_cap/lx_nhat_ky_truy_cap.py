"""DocType LX Nhat Ky Truy Cap: nhật ký bất biến ghi nhận truy cập dữ liệu khách.

Lưu ý giới hạn hợp đồng N6:
- Tính bất biến được cưỡng chế ở tầng Document (validate, db_update, on_trash) và quyền DocType
  (create=0, write=0, delete=0). Truy vấn SQL trực tiếp (frappe.db.sql, frappe.db.delete) của
  quản trị hệ thống nằm ngoài tầng Document.
- Nhật ký truy cập phủ các đường đọc/ghi dữ liệu khách (LX Nguoi, LX To Chuc, LX Don Vi):
  + Mở/tác động qua Document hook (onload, after_insert, on_update, on_trash).
  + Đọc chi tiết 1 bản ghi (/api/resource/<DT>/<name>, /api/v2/document/<DT>/<name>,
    frappe.client.get, frappe.desk.form.load.getdoc).
  + Đọc danh sách (/api/resource/<DT>, /api/v2/document/<DT>, frappe.client.get_list,
    frappe.desk.reportview.get, frappe.desk.reportview.get_list, frappe.desk.reportview.get_count).
  + Đọc giá trị lẻ (frappe.client.get_value, frappe.client.get_single_value).
  + Xuất dữ liệu (frappe.desk.reportview.export_query,
    frappe.core.doctype.data_export.exporter.export_data,
    frappe.core.doctype.data_import.data_import.download_template).
"""
import json
from urllib.parse import unquote

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

DOCTYPE_KHACH = ("LX Nguoi", "LX To Chuc", "LX Don Vi")
MAP_HANH_DONG = {
	"onload": "xem",
	"after_insert": "tao",
	"on_update": "sua",
	"on_trash": "xoa",
}
HANH_DONG_DOC = ("xem", "xem_danh_sach", "xuat")

METHOD_DOC_CHI_TIET = (
	"/api/method/frappe.client.get",
	"/api/method/frappe.desk.form.load.getdoc",
)
METHOD_DOC_DANH_SACH = (
	"/api/method/frappe.client.get_list",
	"/api/method/frappe.desk.reportview.get",
	"/api/method/frappe.desk.reportview.get_list",
	"/api/method/frappe.desk.reportview.get_count",
)
METHOD_DOC_GIA_TRI = (
	"/api/method/frappe.client.get_value",
	"/api/method/frappe.client.get_single_value",
)
METHOD_XUAT_DU_LIEU = (
	"/api/method/frappe.desk.reportview.export_query",
	"/api/method/frappe.core.doctype.data_export.exporter.export_data",
	"/api/method/frappe.core.doctype.data_import.data_import.download_template",
)


class LXNhatKyTruyCap(Document):
	def before_insert(self):
		if not getattr(self, "thoi_diem", None):
			self.thoi_diem = now_datetime()
		if not getattr(self, "hanh_dong", None):
			self.hanh_dong = "xem"

	def validate(self):
		if not self.is_new():
			frappe.throw("Nhật ký truy cập là bất biến, không được sửa", frappe.PermissionError)

	def db_update(self, *args, **kwargs):
		frappe.throw("Nhật ký truy cập là bất biến, không được sửa", frappe.PermissionError)

	def on_trash(self):
		frappe.throw("Nhật ký truy cập là bất biến, không được xoá", frappe.PermissionError)


def _ghi_loi_nhat_ky(loi: Exception, ngu_canh: str = "") -> None:
	log_fn = getattr(frappe, "log_error", None)
	if not callable(log_fn):
		return
	tieu_de = "Lỗi ghi LX Nhat Ky Truy Cap"
	thong_diep = f"{ngu_canh}: {loi}" if ngu_canh else str(loi)
	try:
		frappe.log_error(title=tieu_de, message=thong_diep)
	except TypeError:
		try:
			frappe.log_error(thong_diep, tieu_de)
		except Exception:
			pass
	except Exception:
		pass


def _lay_ip() -> str:
	local_obj = getattr(frappe, "local", None)
	ip = getattr(local_obj, "request_ip", None)
	if ip:
		return str(ip)
	req = getattr(local_obj, "request", None)
	if req is not None:
		xff = getattr(req, "headers", {}).get("X-Forwarded-For") if hasattr(req, "headers") else None
		if xff:
			return str(xff).split(",")[0].strip()
		ra = getattr(req, "remote_addr", None)
		if ra:
			return str(ra)
	return "127.0.0.1"


def ghi_nhat_ky_truy_cap(doc, method=None, hanh_dong=None, nguoi_dung=None, ip=None):
	"""Ghi bản ghi LX Nhat Ky Truy Cap bất biến khi mở/tác động dữ liệu khách (LX Nguoi, LX To Chuc, LX Don Vi)."""
	if isinstance(doc, dict):
		loai = doc.get("doctype")
		ma = doc.get("name")
	else:
		loai = getattr(doc, "doctype", None)
		ma = getattr(doc, "name", None)

	if loai not in DOCTYPE_KHACH or not ma:
		return None

	hd = hanh_dong or MAP_HANH_DONG.get(str(method or ""), "xem")
	khoa = (str(loai), str(ma), str(hd))

	flags = getattr(doc, "flags", None)
	co_doc = f"_da_ghi_nhat_ky_{hd}"
	if flags is not None and getattr(flags, co_doc, False):
		return None

	local_obj = getattr(frappe, "local", None)
	co_req = getattr(local_obj, "request", None) is not None
	da_ghi = getattr(local_obj, "_lx_nhat_ky_da_ghi", None) if (co_req and local_obj is not None) else None
	if isinstance(da_ghi, set) and khoa in da_ghi:
		return None

	user = nguoi_dung or getattr(getattr(frappe, "session", None), "user", None) or "Guest"
	dia_chi_ip = ip if ip is not None else _lay_ip()

	try:
		ban_ghi = frappe.get_doc(
			{
				"doctype": "LX Nhat Ky Truy Cap",
				"nguoi_dung": str(user),
				"loai_ban_ghi": str(loai),
				"ma_ban_ghi": str(ma),
				"hanh_dong": str(hd),
				"thoi_diem": now_datetime(),
				"ip": str(dia_chi_ip),
			}
		)
		ban_ghi.insert(ignore_permissions=True)

		if flags is not None:
			setattr(flags, co_doc, True)
		if co_req and local_obj is not None:
			if not isinstance(da_ghi, set):
				da_ghi = set()
				local_obj._lx_nhat_ky_da_ghi = da_ghi
			da_ghi.add(khoa)

		req = getattr(local_obj, "request", None)
		if hd in HANH_DONG_DOC or (req is not None and getattr(req, "method", "GET") == "GET"):
			frappe.db.commit()
		return ban_ghi
	except Exception as exc:
		_ghi_loi_nhat_ky(exc, f"{loai}/{ma}/{hd}")
		return None


def _doc_json_phan_hoi(local_obj, response) -> dict:
	resp_local = getattr(local_obj, "response", None)
	if isinstance(resp_local, dict) and resp_local:
		return resp_local
	if response is None:
		return {}
	try:
		if hasattr(response, "get_data"):
			raw = response.get_data(as_text=True)
		else:
			raw = getattr(response, "data", "")
			if isinstance(raw, bytes):
				raw = raw.decode("utf-8", errors="ignore")
		if isinstance(raw, str) and raw.strip().startswith("{"):
			d = json.loads(raw)
			if isinstance(d, dict):
				return d
	except Exception:
		pass
	return {}


def _trich_danh_sach_ma(payload) -> list[str]:
	ds_ma: list[str] = []
	if isinstance(payload, list):
		for muc in payload:
			if isinstance(muc, dict) and muc.get("name"):
				ds_ma.append(str(muc["name"]))
			elif isinstance(muc, (list, tuple)) and muc and muc[0]:
				ds_ma.append(str(muc[0]))
	elif isinstance(payload, dict):
		keys = payload.get("keys")
		values = payload.get("values")
		if isinstance(keys, list) and isinstance(values, list):
			idx = keys.index("name") if "name" in keys else 0
			for dong in values:
				if isinstance(dong, (list, tuple)) and len(dong) > idx and dong[idx]:
					ds_ma.append(str(dong[idx]))
				elif isinstance(dong, dict) and dong.get("name"):
					ds_ma.append(str(dong["name"]))
		elif isinstance(payload.get("data"), list):
			return _trich_danh_sach_ma(payload["data"])
	return list(dict.fromkeys(ds_ma))


def _trich_ma_tu_filters(filters, message) -> str:
	if isinstance(message, dict) and message.get("name"):
		return str(message["name"])
	if isinstance(filters, str):
		s = filters.strip()
		if s.startswith("{"):
			try:
				filters = json.loads(s)
			except Exception:
				return s or "*"
		elif s and not s.startswith("["):
			return s
	if isinstance(filters, dict):
		ten = filters.get("name")
		if isinstance(ten, str) and ten.strip():
			return ten.strip()
	return "*"


def _ghi_danh_sach_khach(dt: str, ds_ma: list[str]) -> None:
	if ds_ma:
		for ma in ds_ma:
			ghi_nhat_ky_truy_cap({"doctype": dt, "name": ma}, method="onload", hanh_dong="xem")
	else:
		ghi_nhat_ky_truy_cap({"doctype": dt, "name": "*"}, hanh_dong="xem_danh_sach")


def ghi_nhat_ky_tu_request(response=None, **kwargs):
	"""Hook after_request: ghi nhật ký khi đọc chi tiết, danh sách, giá trị lẻ hoặc xuất dữ liệu khách qua API."""
	try:
		local_obj = getattr(frappe, "local", None)
		req = getattr(local_obj, "request", None)
		if req is None:
			return
		method_http = getattr(req, "method", "")
		if method_http not in ("GET", "POST"):
			return
		status = getattr(response, "status_code", 200) if response is not None else 200
		if status >= 400:
			return

		duong = unquote(getattr(req, "path", "") or "")
		for tien_to in ("/api/resource/", "/api/v2/document/"):
			if duong.startswith(tien_to):
				if method_http != "GET":
					return
				phan = [p.strip() for p in duong[len(tien_to) :].strip("/").split("/") if p.strip()]
				if len(phan) >= 2 and phan[0] in DOCTYPE_KHACH:
					ghi_nhat_ky_truy_cap({"doctype": phan[0], "name": phan[1]}, method="onload")
					return
				if len(phan) == 1 and phan[0] in DOCTYPE_KHACH:
					d = _doc_json_phan_hoi(local_obj, response)
					ds_ma = _trich_danh_sach_ma(d.get("data"))
					_ghi_danh_sach_khach(phan[0], ds_ma)
					return

		form_dict = getattr(local_obj, "form_dict", None) or {}
		dt = form_dict.get("doctype") or form_dict.get("reference_doctype")

		if duong in METHOD_DOC_CHI_TIET:
			ten = form_dict.get("name")
			if dt in DOCTYPE_KHACH and ten:
				ghi_nhat_ky_truy_cap({"doctype": dt, "name": ten}, method="onload")
				return
			d = _doc_json_phan_hoi(local_obj, response)
			for doc_item in d.get("docs") or []:
				if isinstance(doc_item, dict) and doc_item.get("doctype") in DOCTYPE_KHACH and doc_item.get("name"):
					ghi_nhat_ky_truy_cap(
						{"doctype": doc_item["doctype"], "name": doc_item["name"]},
						method="onload",
					)
			return

		if duong in METHOD_DOC_DANH_SACH and dt in DOCTYPE_KHACH:
			d = _doc_json_phan_hoi(local_obj, response)
			ds_ma = _trich_danh_sach_ma(d.get("message"))
			_ghi_danh_sach_khach(dt, ds_ma)
			return

		if duong in METHOD_DOC_GIA_TRI and dt in DOCTYPE_KHACH:
			d = _doc_json_phan_hoi(local_obj, response)
			ma = _trich_ma_tu_filters(form_dict.get("filters"), d.get("message"))
			ghi_nhat_ky_truy_cap({"doctype": dt, "name": ma}, method="onload", hanh_dong="xem")
			return

		if duong in METHOD_XUAT_DU_LIEU and dt in DOCTYPE_KHACH:
			ghi_nhat_ky_truy_cap({"doctype": dt, "name": "*"}, hanh_dong="xuat")
			return
	except Exception as exc:
		_ghi_loi_nhat_ky(exc, "after_request")
