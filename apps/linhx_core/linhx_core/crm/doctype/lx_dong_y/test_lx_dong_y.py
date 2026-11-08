"""Unit test cho dong_y và controller LXDongY."""
from datetime import datetime, timezone
from pathlib import Path
import sys
import types
from unittest.mock import patch

import pytest

_CORE_DIR = str(Path(__file__).resolve().parents[4])
if _CORE_DIR not in sys.path:
	sys.path.insert(0, _CORE_DIR)

from linhx_core.crm import dong_y


def _nap_lx_dong_y():
	try:
		import frappe.model.document  # noqa: F401
		from linhx_core.crm.doctype.lx_dong_y.lx_dong_y import LXDongY

		return LXDongY
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
	frappe_mod.PermissionError = PermissionError
	frappe_mod.ValidationError = ValueError

	def _throw(msg, exc=Exception):
		raise exc(msg)

	frappe_mod.throw = _throw

	with patch.dict(
		sys.modules,
		{
			"frappe": frappe_mod,
			"frappe.model": model_mod,
			"frappe.model.document": doc_mod,
		},
	):
		sys.modules.pop("linhx_core.crm.doctype.lx_dong_y.lx_dong_y", None)
		from linhx_core.crm.doctype.lx_dong_y.lx_dong_y import LXDongY

		return LXDongY


def test_ghi_va_hieu_luc_cung_thoi_diem_hoac_iso():
	dt_utc = datetime(2026, 11, 9, 1, 0, 0, tzinfo=timezone.utc)
	so = dong_y.ghi([], {"name": "N1"}, "lien_he", 1, dt_utc, "form")
	so = dong_y.ghi(so, "N1", "lien_he", "0", so[0]["luc"], "rut-ngay")
	assert dong_y.hieu_luc(so, "N1", "lien_he") is False
	assert dong_y.hieu_luc(so, "N1", "muc_dich_la") is False


def test_controller_chan_sua_va_xoa_ban_ghi_cu():
	LXDongY = _nap_lx_dong_y()
	doc = LXDongY()
	doc.nguoi = "N1"
	doc.muc_dich = "chuyen_cheo"
	doc.dong_y = True
	doc.__islocal = True
	doc.before_insert()
	doc.validate()
	assert doc.dong_y == 1
	assert doc.luc

	doc.__islocal = False
	with pytest.raises(PermissionError):
		doc.validate()
	with pytest.raises(PermissionError):
		doc.db_update()
	with pytest.raises(PermissionError):
		doc.on_trash()


def test_controller_kiem_tra_muc_dich_va_nguoi():
	LXDongY = _nap_lx_dong_y()
	doc = LXDongY()
	doc.nguoi = "N1"
	doc.muc_dich = "sai_muc_dich"
	doc.__islocal = True
	with pytest.raises(ValueError):
		doc.validate()
