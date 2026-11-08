"""Unit test cho co_hoi và controller LXCoHoi."""
from datetime import datetime, timezone
from pathlib import Path
import sys
import types
from unittest.mock import patch

_CORE_DIR = str(Path(__file__).resolve().parents[4])
if _CORE_DIR not in sys.path:
	sys.path.insert(0, _CORE_DIR)

from linhx_core.crm import co_hoi


def _nap_lx_co_hoi():
	try:
		import frappe.model.document  # noqa: F401
		from linhx_core.crm.doctype.lx_co_hoi.lx_co_hoi import LXCoHoi

		return LXCoHoi
	except ModuleNotFoundError:
		pass

	frappe_mod = types.ModuleType("frappe")
	model_mod = types.ModuleType("frappe.model")
	doc_mod = types.ModuleType("frappe.model.document")

	class _Document:
		pass

	doc_mod.Document = _Document
	model_mod.document = doc_mod
	frappe_mod.model = model_mod

	with patch.dict(
		sys.modules,
		{
			"frappe": frappe_mod,
			"frappe.model": model_mod,
			"frappe.model.document": doc_mod,
		},
	):
		sys.modules.pop("linhx_core.crm.doctype.lx_co_hoi.lx_co_hoi", None)
		from linhx_core.crm.doctype.lx_co_hoi.lx_co_hoi import LXCoHoi

		return LXCoHoi


def test_viec_cho_han_giao_sai_dinh_dang_va_thieu():
	ds = [
		{"name": "CH_TRONG", "phu_trach": "", "han_giao": ""},
		{"name": "CH_DUNG", "phu_trach": None, "han_giao": "2026-11-09 10:00:00"},
		{"name": "CH_SAI", "phu_trach": None, "han_giao": "khong-phai-ngay"},
	]
	vc = co_hoi.viec_cho(ds, "2026-11-09 09:00:00")
	theo_ten = {x["name"]: x for x in vc}
	assert theo_ten["CH_SAI"]["qua_han"] is True
	assert theo_ten["CH_DUNG"]["qua_han"] is False
	assert theo_ten["CH_TRONG"]["qua_han"] is False
	assert [x["name"] for x in vc] == ["CH_SAI", "CH_DUNG", "CH_TRONG"]


def test_parse_tg_chuoi_iso_co_mui_gio():
	dt_utc = datetime(2026, 11, 9, 1, 0, 0, tzinfo=timezone.utc)
	assert co_hoi._parse_tg("2026-11-09T01:00:00Z") == co_hoi._parse_tg(dt_utc)
	assert co_hoi._parse_tg("2026-11-09T08:00:00+07:00") == co_hoi._parse_tg(dt_utc)


def test_controller_before_insert_kep_han_giao_va_tu_giao():
	LXCoHoi = _nap_lx_co_hoi()
	doc = LXCoHoi()
	doc.name = "CH-TEST-1"
	doc.creation = "2026-11-09 08:00:00"
	doc.han_giao = "2026-11-09 12:00:00"
	doc._ds_phu_trach = ["nv1@linhx.vn", "nv2@linhx.vn"]
	doc._ds_co_hoi_mo = [{"phu_trach": "nv1@linhx.vn", "trang_thai": "moi"}]
	doc.before_insert()
	assert doc.han_giao == "2026-11-09 09:00:00"
	assert doc.phu_trach == "nv2@linhx.vn"
	assert doc.trang_thai == "moi"


def test_controller_nuot_loi_db_va_loc_vai_tro_crm():
	LXCoHoi = _nap_lx_co_hoi()
	for doctype_loi in ("User", "Has Role", "User Permission"):
		frappe_gia = types.ModuleType("frappe")
		frappe_gia.db = object()
		ds_log = []
		frappe_gia.log_error = lambda message="", title="": ds_log.append((title, message))

		def _get_all(doctype, *_a, _dt_loi=doctype_loi, **_kw):
			if doctype == _dt_loi:
				raise RuntimeError(f"DB lỗi tại {doctype}")
			if doctype == "User":
				return ["nv1@linhx.vn"]
			if doctype == "Has Role":
				return ["nv1@linhx.vn"]
			return []

		frappe_gia.get_all = _get_all
		with patch.dict(sys.modules, {"frappe": frappe_gia}):
			doc = LXCoHoi()
			doc.name = f"CH-LOI-{doctype_loi}"
			doc.don_vi = "DV-HN"
			doc.creation = "2026-11-09 08:00:00"
			doc.before_insert()
			assert not getattr(doc, "phu_trach", None)
			assert ds_log


def test_controller_khong_ai_co_vai_tro_crm_khong_giao():
	LXCoHoi = _nap_lx_co_hoi()
	frappe_gia = types.ModuleType("frappe")
	frappe_gia.db = object()
	ds_log = []
	frappe_gia.log_error = lambda message="", title="": ds_log.append((title, message))

	def _get_all(doctype, *_a, **_kw):
		if doctype == "User":
			return ["ke_toan@linhx.vn", "it@linhx.vn"]
		if doctype == "Has Role":
			return []
		return []

	frappe_gia.get_all = _get_all
	with patch.dict(sys.modules, {"frappe": frappe_gia}):
		doc = LXCoHoi()
		doc.name = "CH-KHONG-VAI-TRO"
		doc.creation = "2026-11-09 08:00:00"
		doc.before_insert()
		assert not getattr(doc, "phu_trach", None)
		assert ds_log
		vc = co_hoi.viec_cho(
			[{"name": doc.name, "phu_trach": getattr(doc, "phu_trach", None), "han_giao": doc.han_giao}],
			"2026-11-09 08:30:00",
		)
		assert [x["name"] for x in vc] == ["CH-KHONG-VAI-TRO"]


def test_controller_khong_ai_thuoc_don_vi_khong_giao():
	LXCoHoi = _nap_lx_co_hoi()
	frappe_gia = types.ModuleType("frappe")
	frappe_gia.db = object()
	ds_log = []
	frappe_gia.log_error = lambda message="", title="": ds_log.append((title, message))

	def _get_all(doctype, *_a, **_kw):
		if doctype == "User":
			return ["nv_bac@linhx.vn", "nv_trung@linhx.vn"]
		if doctype == "Has Role":
			return ["nv_bac@linhx.vn", "nv_trung@linhx.vn"]
		if doctype == "User Permission":
			return []
		return []

	frappe_gia.get_all = _get_all
	with patch.dict(sys.modules, {"frappe": frappe_gia}):
		doc = LXCoHoi()
		doc.name = "CH-KHONG-DON-VI"
		doc.don_vi = "DV-NAM"
		doc.creation = "2026-11-09 08:00:00"
		doc.before_insert()
		assert not getattr(doc, "phu_trach", None)
		assert ds_log
