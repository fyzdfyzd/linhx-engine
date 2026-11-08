"""Controller DocType LX Don CTS: bảo vệ PII (email, ho_so) và kiểm tra ràng buộc duy nhất."""
from __future__ import annotations

import json

import frappe
from frappe.model.document import Document

VAI_TRO_DUOC_XEM = {"System Manager", "LX Operator"}
VAI_TRO_QUAN_TRI_PII = {"System Manager"}


def _tap_vai_tro(user: str | None = None) -> set[str]:
	nguoi = user or getattr(getattr(frappe, "session", None), "user", None) or "Guest"
	if nguoi == "Guest":
		return set()
	try:
		return set(frappe.get_roles(nguoi) or [])
	except Exception:
		return set()


def co_quyen_don_cts(doc, ptype: str = "read", user: str | None = None) -> bool:
	"""Kiểm tra quyền truy cập đơn CTS (chặn Guest và người dùng không có vai trò điều hành/quản trị)."""
	nguoi = user or getattr(getattr(frappe, "session", None), "user", None) or "Guest"
	if not nguoi or nguoi == "Guest":
		return False
	if nguoi == "Administrator":
		return True
	vai_tro = _tap_vai_tro(nguoi)
	loai = str(ptype or "read").lower()
	if loai in ("write", "create", "delete", "submit", "cancel", "amend"):
		return bool(vai_tro & VAI_TRO_QUAN_TRI_PII)
	return bool(vai_tro & VAI_TRO_DUOC_XEM)


def dieu_kien_truy_van_don_cts(user: str | None = None) -> str:
	"""Điều kiện SQL cho danh sách LX Don CTS: ẩn hoàn toàn với Guest hoặc người không đủ quyền."""
	nguoi = user or getattr(getattr(frappe, "session", None), "user", None) or "Guest"
	if nguoi == "Administrator":
		return ""
	if not nguoi or nguoi == "Guest":
		return "1=0"
	if not (_tap_vai_tro(nguoi) & VAI_TRO_DUOC_XEM):
		return "1=0"
	return ""


class LXDonCTS(Document):
	def autoname(self):
		ma = str(getattr(self, "order_id", None) or "").strip()
		if ma:
			self.order_id = ma
			self.name = ma

	def validate(self):
		ma = str(getattr(self, "order_id", None) or "").strip()
		if not ma:
			frappe.throw("order_id không được để trống")
		self.order_id = ma

		nd = str(getattr(self, "noi_dung_ck", None) or "").strip().upper()
		if not nd:
			frappe.throw("noi_dung_ck không được để trống")
		self.noi_dung_ck = nd

		if isinstance(getattr(self, "ho_so", None), dict):
			self.ho_so = json.dumps(self.ho_so, ensure_ascii=False)

		if getattr(frappe, "db", None) is not None and hasattr(frappe.db, "exists"):
			trung_id = frappe.db.exists(
				"LX Don CTS", {"order_id": ma, "name": ["!=", self.name]}
			)
			if trung_id:
				frappe.throw(f"Mã đơn CTS {ma} đã tồn tại")
			trung_ck = frappe.db.exists(
				"LX Don CTS", {"noi_dung_ck": nd, "name": ["!=", self.name]}
			)
			if trung_ck:
				frappe.throw(f"Nội dung chuyển khoản {nd} đã tồn tại ở đơn {trung_ck}")
