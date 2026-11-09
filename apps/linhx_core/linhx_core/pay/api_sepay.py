"""API nhận webhook SePay cho module pay."""
from __future__ import annotations

import json
import re

import frappe

from linhx_core.pay.sepay import chuan_noi_dung, tim_cac_don_khop, xac_thuc_khoa, xu_ly

DUONG_WEBHOOK = "/api/method/linhx_core.pay.api_sepay.webhook"
CMD_WEBHOOK = "linhx_core.pay.api_sepay.webhook"


def _doc_sepay_khoa() -> str:
	khoa = getattr(frappe.conf, "sepay_khoa", None) or frappe.conf.get("sepay_khoa")
	try:
		duong = frappe.get_site_path("site_config.json")
		with open(duong, encoding="utf-8") as f:
			cfg = json.load(f)
		if cfg.get("sepay_khoa"):
			khoa = cfg.get("sepay_khoa")
	except Exception:
		pass
	return str(khoa or "").strip()


def _la_request_webhook() -> bool:
	req = getattr(frappe.local, "request", None) or getattr(frappe, "request", None)
	duong = (getattr(req, "path", "") or "").rstrip("/")
	if duong == DUONG_WEBHOOK:
		return True
	form_dict = getattr(frappe.local, "form_dict", None)
	if isinstance(form_dict, dict) and form_dict.get("cmd") == CMD_WEBHOOK:
		return True
	return False


def xac_thuc_sepay_hook() -> None:
	"""Hook xác thực header 'Authorization: Apikey <sepay_khoa>' chỉ cho đường dẫn webhook SePay."""
	if not _la_request_webhook():
		return
	auth = frappe.get_request_header("Authorization")
	if not isinstance(auth, str) or not auth.strip().lower().startswith("apikey "):
		return
	khoa = _doc_sepay_khoa()
	if xac_thuc_khoa(auth, khoa):
		frappe.local._lx_sepay_auth = auth
		frappe.set_user("Administrator")


def _doc_payload(kwargs: dict) -> dict:
	"""Đọc payload JSON từ body của request HTTP; chỉ dùng `kwargs` khi gọi trực tiếp không qua HTTP."""
	req = getattr(frappe, "request", None)
	if req is not None:
		try:
			du_lieu = req.get_json(silent=True)
			if isinstance(du_lieu, dict):
				return dict(du_lieu)
		except Exception:
			pass
		try:
			raw = req.get_data(as_text=True)
			if raw:
				du_lieu = json.loads(raw)
				if isinstance(du_lieu, dict):
					return dict(du_lieu)
		except Exception:
			pass
		return {}
	return {k: v for k, v in (kwargs or {}).items() if k != "cmd"}


def _tim_ds_don_ung_vien_db(noi_dung_gop: str) -> list[dict]:
	"""Tìm ứng viên `LX Don` trong DB: lọc theo index `noi_dung_ck` trước, dự phòng lấy đơn `cho_tra`."""
	fields = ["name", "ma", "so_tien", "trang_thai", "noi_dung_ck", "tx_id"]
	nd_chuan = chuan_noi_dung(noi_dung_gop)
	if not nd_chuan:
		return []

	tu_don = [t for t in re.findall(r"[A-Z0-9]+", noi_dung_gop.upper()) if t]
	tap_token: set[str] = {t for t in tu_don if len(t) >= 2}
	tap_token.add(nd_chuan)
	for buoc in (2, 3, 4):
		for i in range(len(tu_don) - buoc + 1):
			ghep = "".join(tu_don[i : i + buoc])
			if 4 <= len(ghep) <= 32:
				tap_token.add(ghep)

	tokens = list(tap_token)
	if tokens:
		ds_theo_ma = frappe.get_all(
			"LX Don",
			filters={"noi_dung_ck": ["in", tokens]},
			fields=fields,
			limit_page_length=50,
		)
		khop = tim_cac_don_khop(ds_theo_ma, noi_dung_gop)
		if khop:
			return khop

	tran_cho_tra = 500
	ds_cho_tra = frappe.get_all(
		"LX Don",
		filters={"trang_thai": "cho_tra"},
		fields=fields,
		limit_page_length=tran_cho_tra,
	)
	if len(ds_cho_tra) >= tran_cho_tra:
		frappe.logger().warning(
			"SePay đối soát dự phòng chạm trần %s đơn cho_tra; cần kiểm tra các đơn cho_tra cũ.",
			tran_cho_tra,
		)
	return tim_cac_don_khop(ds_cho_tra, noi_dung_gop)


def _rut_gon_payload_nhat_ky(payload: dict) -> dict:
	"""Lược bớt thông tin nhạy cảm (che số tài khoản) trước khi lưu vào nhật ký đối soát."""
	ban_sao = {}
	for k in (
		"id",
		"gateway",
		"transactionDate",
		"accountNumber",
		"transferType",
		"transferAmount",
		"content",
		"code",
		"referenceCode",
	):
		if k in payload:
			val = payload[k]
			if k == "accountNumber" and isinstance(val, str) and len(val) > 4:
				val = "***" + val[-4:]
			ban_sao[k] = val
	return ban_sao


def _ghi_nhat_ky_sepay(tx_id: str, payload: dict, kho: dict, ket_qua: dict) -> None:
	"""Lưu giao dịch webhook SePay (đã trả, lệch hoặc bỏ qua) vào DocType `LX Nhat Ky Sepay`."""
	if ket_qua.get("bo_qua"):
		loai_kq = "bo_qua"
		ly_do = "tien_ra"
		ma_don = None
	elif kho.get("lech"):
		loai_kq = "lech"
		dong_lech = kho["lech"][-1]
		ly_do = dong_lech.get("ly_do")
		ma_don = dong_lech.get("ma_don")
	else:
		loai_kq = "da_tra"
		ly_do = None
		ma_don = ket_qua.get("ma_don")

	try:
		so_tien = float(payload.get("transferAmount") or 0)
	except (TypeError, ValueError):
		so_tien = 0.0

	nhat_ky = frappe.get_doc(
		{
			"doctype": "LX Nhat Ky Sepay",
			"tx_id": tx_id,
			"loai_gd": str(payload.get("transferType") or ""),
			"so_tien": so_tien,
			"noi_dung": str(payload.get("content") or ""),
			"ket_qua": loai_kq,
			"ly_do": str(ly_do or ""),
			"ma_don": str(ma_don or ""),
			"du_lieu": json.dumps(_rut_gon_payload_nhat_ky(payload), ensure_ascii=False),
		}
	)
	nhat_ky.insert(ignore_permissions=True)


@frappe.whitelist(allow_guest=True, methods=["POST"])
def webhook(**kwargs):
	"""Nhận webhook SePay, đối soát với `LX Don` (khoá dòng `for_update`) và chuyển `da_tra`."""
	authorization = (
		getattr(frappe.local, "_lx_sepay_auth", None)
		or frappe.get_request_header("Authorization")
	)
	khoa = _doc_sepay_khoa()
	if not xac_thuc_khoa(authorization, khoa):
		frappe.local.response["http_status_code"] = 401
		return {"success": False, "error": "unauthorized"}

	payload = _doc_payload(kwargs)
	raw_id = payload.get("id")
	tx_id = "" if (raw_id is None or isinstance(raw_id, bool)) else str(raw_id).strip()
	if not tx_id:
		frappe.local.response["http_status_code"] = 400
		return {"success": False, "error": "missing_tx_id"}

	# Kiểm tra sớm tx_id đã tồn tại; khi hai request cùng tx_id chạy đua đồng thời,
	# chống trùng cuối cùng dựa vào khoá chính/unique (name = tx_id ở LX Nhat Ky Sepay
	# và unique tx_id ở LX Don) kết hợp bắt DuplicateEntryError bên dưới.
	da_co_nhat_ky = frappe.db.sql(
		"SELECT name FROM `tabLX Nhat Ky Sepay` WHERE tx_id = %s FOR UPDATE",
		(tx_id,),
		as_dict=True,
	)
	da_co_don = frappe.db.sql(
		"SELECT name FROM `tabLX Don` WHERE tx_id = %s FOR UPDATE",
		(tx_id,),
		as_dict=True,
	)
	if da_co_nhat_ky or da_co_don:
		return {"success": True, "trung": True, "tx_id": tx_id}

	doc_don = None
	ds_don: list[dict] = []
	tx_da_co: list[str] = []

	if payload.get("transferType") == "in":
		noi_dung_gop = f"{payload.get('content') or ''} {payload.get('code') or ''}".strip()
		ds_ung_vien = _tim_ds_don_ung_vien_db(noi_dung_gop)
		if len(ds_ung_vien) == 1:
			doc_don = frappe.get_doc("LX Don", ds_ung_vien[0]["name"], for_update=True)
			tx_don = str(getattr(doc_don, "tx_id", None) or "").strip()
			if tx_don:
				tx_da_co.append(tx_don)
			ds_don.append(
				{
					"name": doc_don.name,
					"ma": getattr(doc_don, "ma", None) or doc_don.name,
					"so_tien": doc_don.so_tien,
					"trang_thai": doc_don.trang_thai,
					"noi_dung_ck": doc_don.noi_dung_ck,
					"tx_id": tx_don or None,
				}
			)
		elif len(ds_ung_vien) > 1:
			ds_don.extend(ds_ung_vien)

	kho = {"don": ds_don, "tx": tx_da_co, "lech": []}
	ma_http, ket_qua = xu_ly(payload, kho, authorization, khoa)
	if ma_http != 200:
		frappe.local.response["http_status_code"] = ma_http
		return ket_qua

	if ket_qua.get("trung"):
		return ket_qua

	try:
		_ghi_nhat_ky_sepay(tx_id, payload, kho, ket_qua)
		if (
			doc_don is not None
			and len(ds_don) == 1
			and ds_don[0].get("trang_thai") == "da_tra"
			and not ket_qua.get("sai_so_tien")
			and not ket_qua.get("da_tra_truoc")
			and not ket_qua.get("don_da_huy")
			and not ket_qua.get("trang_thai_khong_hop_le")
		):
			doc_don.trang_thai = "da_tra"
			doc_don.tx_id = ds_don[0].get("tx_id") or tx_id
			doc_don.save(ignore_permissions=True)
		frappe.db.commit()
	except frappe.DuplicateEntryError:
		frappe.db.rollback()
		return {"success": True, "trung": True, "tx_id": tx_id}
	except Exception:
		frappe.db.rollback()
		raise

	return ket_qua
