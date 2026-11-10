"""DocType LX Su Kien: hàng đợi outbox lưu sự kiện phát từ lõi để giao cho các gói nghe."""
import json

import frappe
from frappe.model.document import Document

TRANG_THAI_HOP_LE = ("cho", "xong", "hong")


def _chuan_du_lieu_json(gia_tri) -> str:
	if gia_tri is None or gia_tri == "":
		return "{}"
	if isinstance(gia_tri, dict):
		return json.dumps(gia_tri, ensure_ascii=False, default=str)
	if isinstance(gia_tri, str):
		try:
			parsed = json.loads(gia_tri)
		except json.JSONDecodeError as exc:
			frappe.throw("Trường du_lieu phải là JSON hợp lệ", frappe.ValidationError)
			raise exc
		if not isinstance(parsed, dict):
			frappe.throw("Trường du_lieu phải là JSON object", frappe.ValidationError)
		return json.dumps(parsed, ensure_ascii=False)
	frappe.throw("Trường du_lieu phải là dict hoặc chuỗi JSON", frappe.ValidationError)
	return "{}"


def _chuan_da_giao_json(gia_tri) -> str:
	if gia_tri is None or gia_tri == "":
		return "[]"
	if isinstance(gia_tri, (list, tuple)):
		if not all(isinstance(x, str) and x.strip() for x in gia_tri):
			frappe.throw("Trường da_giao phải là danh sách đường hàm hợp lệ", frappe.ValidationError)
		return json.dumps([x.strip() for x in gia_tri], ensure_ascii=False)
	if isinstance(gia_tri, str):
		try:
			parsed = json.loads(gia_tri)
		except json.JSONDecodeError as exc:
			frappe.throw("Trường da_giao phải là JSON hợp lệ", frappe.ValidationError)
			raise exc
		if not isinstance(parsed, list) or not all(isinstance(x, str) and x.strip() for x in parsed):
			frappe.throw("Trường da_giao phải là danh sách JSON các đường hàm", frappe.ValidationError)
		return json.dumps([x.strip() for x in parsed], ensure_ascii=False)
	frappe.throw("Trường da_giao phải là list hoặc chuỗi JSON", frappe.ValidationError)
	return "[]"


class LXSuKien(Document):
	def validate(self):
		ten = str(getattr(self, "ten", "") or "").strip()
		if not ten:
			frappe.throw("Thiếu tên sự kiện (ten)", frappe.ValidationError)
		self.ten = ten

		trang_thai = str(getattr(self, "trang_thai", "") or "cho").strip()
		if trang_thai not in TRANG_THAI_HOP_LE:
			frappe.throw(
				f"Trạng thái sự kiện không hợp lệ: {trang_thai!r}",
				frappe.ValidationError,
			)
		self.trang_thai = trang_thai

		lan = getattr(self, "lan", 0)
		try:
			so_lan = int(0 if lan is None or lan == "" else lan)
		except (TypeError, ValueError) as exc:
			frappe.throw("Số lần lỗi (lan) phải là số nguyên", frappe.ValidationError)
			raise exc
		if so_lan < 0:
			frappe.throw("Số lần lỗi (lan) không được âm", frappe.ValidationError)
		self.lan = so_lan

		self.du_lieu = _chuan_du_lieu_json(getattr(self, "du_lieu", None))
		self.da_giao = _chuan_da_giao_json(getattr(self, "da_giao", None))
		if getattr(self, "loi", None) is None:
			self.loi = ""
