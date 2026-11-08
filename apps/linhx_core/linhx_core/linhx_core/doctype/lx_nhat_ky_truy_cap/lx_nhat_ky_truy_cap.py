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


class LXNhatKyTruyCap(Document):
	def before_insert(self):
		if not getattr(self, "thoi_diem", None):
			self.thoi_diem = now_datetime()
		if not getattr(self, "hanh_dong", None):
			self.hanh_dong = "xem"

	def validate(self):
		if not self.is_new():
			frappe.throw("Nhật ký truy cập là bất biến, không được sửa", frappe.PermissionError)

	def on_trash(self):
		frappe.throw("Nhật ký truy cập là bất biến, không được xoá", frappe.PermissionError)


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
	if flags is not None:
		co_doc = f"_da_ghi_nhat_ky_{hd}"
		if getattr(flags, co_doc, False):
			return None
		setattr(flags, co_doc, True)

	local_obj = getattr(frappe, "local", None)
	co_req = getattr(local_obj, "request", None) is not None
	if co_req and local_obj is not None:
		da_ghi = getattr(local_obj, "_lx_nhat_ky_da_ghi", None)
		if not isinstance(da_ghi, set):
			da_ghi = set()
			local_obj._lx_nhat_ky_da_ghi = da_ghi
		if khoa in da_ghi:
			return None
		da_ghi.add(khoa)

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
		req = getattr(local_obj, "request", None)
		if req is not None and getattr(req, "method", "GET") == "GET":
			frappe.db.commit()
		return ban_ghi
	except Exception:
		return None


def ghi_nhat_ky_tu_request(response=None, **kwargs):
	"""Hook after_request: ghi nhật ký khi đọc chi tiết bản ghi khách qua HTTP GET API."""
	try:
		local_obj = getattr(frappe, "local", None)
		req = getattr(local_obj, "request", None)
		if req is None or getattr(req, "method", "") != "GET":
			return
		status = getattr(response, "status_code", 200) if response is not None else 200
		if status >= 400:
			return

		duong = unquote(getattr(req, "path", "") or "")
		for tien_to in ("/api/resource/", "/api/v2/document/"):
			if duong.startswith(tien_to):
				phan = [p.strip() for p in duong[len(tien_to) :].strip("/").split("/") if p.strip()]
				if len(phan) >= 2 and phan[0] in DOCTYPE_KHACH:
					ghi_nhat_ky_truy_cap({"doctype": phan[0], "name": phan[1]}, method="onload")
					return

		if duong in ("/api/method/frappe.client.get", "/api/method/frappe.desk.form.load.getdoc"):
			form_dict = getattr(local_obj, "form_dict", None) or {}
			dt = form_dict.get("doctype")
			ten = form_dict.get("name")
			if dt in DOCTYPE_KHACH and ten:
				ghi_nhat_ky_truy_cap({"doctype": dt, "name": ten}, method="onload")
	except Exception:
		pass
