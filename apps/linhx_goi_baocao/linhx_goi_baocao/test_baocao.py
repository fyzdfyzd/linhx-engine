"""Kiểm thử đơn vị cho gói báo cáo `linhx_goi_baocao` (sau_tra, ban_bao_cao, giao_hang bao_cao)."""
from __future__ import annotations

import pathlib
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

_THU_MUC_APPS = pathlib.Path(__file__).resolve().parents[2]
for _ten_app in ("linhx_core", "linhx_goi_baocao"):
	_duong = str(_THU_MUC_APPS / _ten_app)
	if _duong not in sys.path:
		sys.path.insert(0, _duong)

from linhx_core import dang_ky_module, giao_hang, hooks, su_kien
from linhx_core.api import tim_ham
from linhx_goi_baocao import ban_bao_cao, sau_tra


def test_khai_bao_module_va_hook_loi():
	ds = dang_ky_module.quet(sau_tra._THU_MUC_CORE.parent)
	assert giao_hang.chon_ham("bao_cao", ds) == "linhx_goi_baocao.sau_tra.giao_bao_cao"
	assert tim_ham("giao", "bao_cao") == ["linhx_goi_baocao.sau_tra.giao_bao_cao"]
	assert tim_ham("cung_cap", "baocao.goi_cong_khai") == ["linhx_goi_baocao.ban_bao_cao.goi_cong_khai"]
	assert tim_ham("cung_cap", "baocao.so_tien_don") == ["linhx_goi_baocao.ban_bao_cao.so_tien_don"]
	assert tim_ham("cung_cap", "baocao.mot_dong") == ["linhx_goi_baocao.sau_tra.mot_dong"]
	assert hooks.doc_events.get("LX Don", {}).get("on_update") == "linhx_core.giao_hang.phat_khi_don_da_tra"


def test_ban_bao_cao_catalog_va_so_tien_don():
	ds = [
		{"ma": "BC-1", "ten": "Báo cáo chuẩn", "gia": 99000.0, "mo_ta": "3 AI", "ban": "true", "gia_san": 50000},
		{"ma": "BC-2", "ten": "Ngừng bán", "gia": 199000, "mo_ta": "x", "ban": False},
	]
	assert ban_bao_cao.goi_cong_khai(ds) == [
		{"ma": "BC-1", "ten": "Báo cáo chuẩn", "gia": 99000, "mo_ta": "3 AI"}
	]
	assert ban_bao_cao.so_tien_don("BC-1", ds) == 99000
	assert ban_bao_cao.so_tien_don("BC-2", ds) is None
	assert ban_bao_cao.so_tien_don("", ds) is None


def test_luong_su_kien_don_da_tra_giao_bao_cao_thuan_python():
	kho_sk: list[dict] = []
	su_kien.phat("don.da_tra", {"don": "DON-BC-01"}, kho=kho_sk)

	da_giao: list[dict] = []

	def _doc_goi(ten_don: str) -> dict:
		return {
			"don": {
				"name": ten_don,
				"ma": ten_don,
				"goi": "BC-AI",
				"so_tien": 99000,
				"trang_thai": "da_tra",
				"brand": "Trà Đồi Mây",
				"email": "khach@vd.vn",
			},
			"goi": {
				"name": "BC-AI",
				"ma": "BC-AI",
				"gia": 99000,
				"gia_san": 50000,
				"loai_giao": "bao_cao",
				"workflow": "ai-noi-gi-ve-brand",
			},
		}

	def _goi_ham(duong_ham: str, don: dict, goi: dict):
		kq = giao_hang.goi_ham_giao(duong_ham, don, goi)
		da_giao.append(kq)
		return kq

	duong = giao_hang.xu_ly(kho_sk[0], doc_goi=_doc_goi, goi=_goi_ham)
	assert duong == "linhx_goi_baocao.sau_tra.giao_bao_cao"
	assert len(da_giao) == 1
	assert da_giao[0]["don"] == "DON-BC-01"
	assert da_giao[0]["trang_thai"] == "cho"
	assert da_giao[0]["workflow"] == "ai-noi-gi-ve-brand"
	assert "Trà Đồi Mây" in da_giao[0]["dau_vao"]


def test_giao_bao_cao_qua_frappe_db_tu_dict_don():
	da_insert: list[dict] = []
	jobs_db: list[dict] = []

	fake_frappe = MagicMock()
	fake_frappe.db.table_exists.return_value = True
	fake_frappe.db.has_column.return_value = True
	fake_frappe.generate_hash.return_value = "ma_xem_12345"

	def fake_get_all(doctype, filters=None, **kwargs):
		if doctype == "LX Goi":
			return [
				{
					"name": "BC-AI",
					"ma": "BC-AI",
					"ten": "Báo cáo AI",
					"gia": 99000,
					"gia_san": 50000,
					"loai_giao": "bao_cao",
					"workflow": "ai-noi-gi-ve-brand",
					"ban": 1,
				}
			]
		return []

	def fake_sql(query, params=None, as_dict=False):
		if "tabLX Job" in query:
			return list(jobs_db)
		return [{"name": params[0]}] if params else []

	def fake_get_doc(data):
		doc_job = MagicMock()
		doc_job.name = f"VIEC-{len(da_insert) + 1:05d}"
		doc_job.trang_thai = data["trang_thai"]

		def _insert(ignore_permissions=False):
			da_insert.append(data)
			jobs_db.append(
				{
					"name": doc_job.name,
					"don": data["don"],
					"ma_xem": data["ma_xem"],
					"trang_thai": data["trang_thai"],
				}
			)

		doc_job.insert.side_effect = _insert
		return doc_job

	fake_frappe.get_all.side_effect = fake_get_all
	fake_frappe.db.sql.side_effect = fake_sql
	fake_frappe.get_doc.side_effect = fake_get_doc

	with patch.dict(sys.modules, {"frappe": fake_frappe}):
		don_dict = {
			"name": "DON-300",
			"ma": "DON-300",
			"goi": "BC-AI",
			"so_tien": 99000,
			"trang_thai": "da_tra",
			"brand": "Cà Phê Sương",
			"email": "kh@vd.vn",
		}
		goi_dict = {
			"name": "BC-AI",
			"ma": "BC-AI",
			"gia": 99000,
			"gia_san": 50000,
			"loai_giao": "bao_cao",
		}
		kq = sau_tra.giao_bao_cao(don_dict, goi_dict)
		assert kq == {
			"name": "VIEC-00001",
			"ma_xem": "ma_xem_12345",
			"don": "DON-300",
			"trang_thai": "cho",
		}
		assert len(da_insert) == 1
		assert da_insert[0]["workflow"] == "ai-noi-gi-ve-brand"
		assert da_insert[0]["nguon"] == "don"

		# Gọi lại không tạo trùng LX Job
		kq2 = sau_tra.giao_bao_cao(SimpleNamespace(**don_dict), goi_dict)
		assert kq2 == kq
		assert len(da_insert) == 1
