"""Kiểm thử đơn vị cho gói báo cáo `linhx_goi_baocao` (sau_tra, ban_bao_cao, giao_hang bao_cao)."""
from __future__ import annotations

import pathlib
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

_THU_MUC_APPS = pathlib.Path(__file__).resolve().parents[2]
for _ten_app in ("linhx_core", "linhx_worker", "linhx_goi_baocao"):
	_duong = str(_THU_MUC_APPS / _ten_app)
	if _duong not in sys.path:
		sys.path.insert(0, _duong)

from linhx_core import dang_ky_module, giao_hang, hooks, su_kien
from linhx_core.api import tim_ham
from linhx_goi_baocao import ban_bao_cao, hooks as goi_hooks, sau_tra


def test_khai_bao_module_va_hook_loi():
	ds = dang_ky_module.quet(_THU_MUC_APPS)
	assert giao_hang.chon_ham("bao_cao", ds) == "linhx_goi_baocao.sau_tra.giao_bao_cao"
	assert tim_ham("giao", "bao_cao") == ["linhx_goi_baocao.sau_tra.giao_bao_cao"]
	assert tim_ham("cung_cap", "baocao.goi_cong_khai") == ["linhx_goi_baocao.ban_bao_cao.goi_cong_khai"]
	assert tim_ham("cung_cap", "baocao.so_tien_don") == ["linhx_goi_baocao.ban_bao_cao.so_tien_don"]
	assert tim_ham("cung_cap", "baocao.mot_dong") == ["linhx_goi_baocao.sau_tra.mot_dong"]
	assert hooks.doc_events.get("LX Don", {}).get("on_update") == "linhx_core.giao_hang.phat_khi_don_da_tra"
	assert goi_hooks.after_install == "linhx_goi_baocao.sau_tra.dam_bao_loai_giao_bao_cao"
	assert "linhx_goi_baocao.sau_tra.dam_bao_loai_giao_bao_cao" in goi_hooks.after_migrate


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


def test_giao_bao_cao_khong_db_khong_tra_job_ao_va_chan_thieu_so_tien():
	with patch.dict(sys.modules, {"frappe": None}):
		don_thieu_tien = {
			"name": "DON-BC-THIEU",
			"ma": "DON-BC-THIEU",
			"goi": "BC-AI",
			"so_tien": None,
			"trang_thai": "da_tra",
			"brand": "Trà Đồi Mây",
		}
		goi_dict = {
			"name": "BC-AI",
			"ma": "BC-AI",
			"gia": 99000,
			"gia_san": 50000,
			"loai_giao": "bao_cao",
			"workflow": "ai-noi-gi-ve-brand",
		}
		assert sau_tra.giao_bao_cao(don_thieu_tien, goi_dict) is None
		assert don_thieu_tien.get("so_tien") is None
		assert don_thieu_tien.get("can_xu_ly") == 1
		assert don_thieu_tien.get("_ly_do_chua_tao_job") == "can_nguoi_xu_ly"

		don_co_tien = {
			"name": "DON-BC-NO-DB",
			"ma": "DON-BC-NO-DB",
			"goi": "BC-AI",
			"so_tien": 99000,
			"trang_thai": "da_tra",
			"brand": "Trà Đồi Mây",
		}
		assert sau_tra.giao_bao_cao(don_co_tien, goi_dict) is None
		assert don_co_tien.get("can_xu_ly") == 1
		assert don_co_tien.get("_ly_do_chua_tao_job") == "loi_tam_thoi"


def test_giao_bao_cao_qua_frappe_db_va_chi_tin_goi_db():
	da_insert: list[dict] = []
	jobs_db: list[dict] = []
	goi_db_rows: list[dict] = [
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

	fake_frappe = MagicMock()
	fake_frappe.db.table_exists.return_value = True
	fake_frappe.db.has_column.return_value = True
	fake_frappe.generate_hash.return_value = "ma_xem_12345"

	def fake_get_all(doctype, filters=None, **kwargs):
		if doctype == "LX Goi":
			if not filters:
				return list(goi_db_rows)
			for k, v in filters.items():
				matched = [g for g in goi_db_rows if g.get(k) == v]
				if matched:
					return matched
			return []
		return []

	def fake_sql(query, params=None, as_dict=False):
		if "tabLX Job" in query:
			ma_d = params[0] if params else ""
			return [j for j in jobs_db if j.get("don") == ma_d]
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
		kho_sk: list[dict] = []
		su_kien.phat("don.da_tra", {"don": "DON-300"}, kho=kho_sk)

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
		duong = giao_hang.xu_ly(
			kho_sk[0],
			doc_goi=lambda _ten: {"don": don_dict, "goi": goi_dict},
		)
		assert duong == "linhx_goi_baocao.sau_tra.giao_bao_cao"
		assert len(da_insert) == 1
		assert da_insert[0]["workflow"] == "ai-noi-gi-ve-brand"
		assert da_insert[0]["nguon"] == "don"

		# Gọi lại không tạo trùng LX Job
		kq2 = sau_tra.giao_bao_cao(SimpleNamespace(**don_dict), goi_dict)
		assert kq2 == {
			"name": "VIEC-00001",
			"ma_xem": "ma_xem_12345",
			"don": "DON-300",
			"trang_thai": "cho",
		}
		assert len(da_insert) == 1

		# Gói không có trong DB: không tin dict goi của caller, không tạo job
		don_goi_la = {
			"name": "DON-301",
			"ma": "DON-301",
			"goi": "GOI-KHONG-CO-TRONG-DB",
			"so_tien": 99000,
			"trang_thai": "da_tra",
			"brand": "Cà Phê Sương",
		}
		goi_gia_mao = {
			"name": "GOI-KHONG-CO-TRONG-DB",
			"ma": "GOI-KHONG-CO-TRONG-DB",
			"gia": 1000,
			"gia_san": 1000,
			"workflow": "ai-noi-gi-ve-brand",
			"loai_giao": "bao_cao",
		}
		assert sau_tra.xu_ly_sau_tra(don_goi_la, goi=goi_gia_mao) is None
		assert don_goi_la.get("can_xu_ly") == 1
		assert len(da_insert) == 1

		# Đơn dưới giá sàn trong DB: dù caller truyền goi có gia_san thấp hơn cũng bị chặn
		don_duoi_san = {
			"name": "DON-302",
			"ma": "DON-302",
			"goi": "BC-AI",
			"so_tien": 10000,
			"trang_thai": "da_tra",
			"brand": "Cà Phê Sương",
		}
		assert sau_tra.xu_ly_sau_tra(don_duoi_san, goi={"name": "BC-AI", "gia": 5000, "gia_san": 5000}) is None
		assert don_duoi_san.get("_ly_do_chua_tao_job") == "can_nguoi_xu_ly"
		assert len(da_insert) == 1


def test_tao_don_khong_doi_loai_giao_va_nap_tre_cung_cap():
	fake_frappe = MagicMock()
	fake_frappe.whitelist = lambda *a, **kw: (lambda fn: fn)
	fake_frappe.conf = {"vietqr_bin": "970422", "vietqr_so_tk": "0123456789", "vietqr_ten_tk": "LINHX"}
	fake_frappe.generate_hash.return_value = "12345678"

	catalog_db = [
		{
			"name": "GOI-QUYEN-DUNG",
			"ma": "GOI-QUYEN-DUNG",
			"ten": "Gói quyền dùng (không phải báo cáo)",
			"gia": 150000,
			"gia_san": 100000,
			"mo_ta": "Quyền dùng",
			"ban": 1,
			"workflow": "",
			"loai_giao": "quyen_dung",
		},
		{
			"name": "BC-AI",
			"ma": "BC-AI",
			"ten": "Báo cáo AI",
			"gia": 99000,
			"gia_san": 50000,
			"mo_ta": "Báo cáo",
			"ban": 1,
			"workflow": "ai-noi-gi-ve-brand",
			"loai_giao": "",
		},
	]
	fake_rate_limiter = MagicMock()
	fake_rate_limiter.rate_limit = lambda *a, **kw: (lambda fn: fn)
	fake_frappe.get_all.side_effect = lambda doctype, **kw: [dict(x) for x in catalog_db] if doctype == "LX Goi" else []
	fake_frappe.db.table_exists.return_value = True
	fake_frappe.db.has_column.return_value = True

	with patch.dict(sys.modules, {"frappe": fake_frappe, "frappe.rate_limiter": fake_rate_limiter}):
		sys.modules.pop("linhx_core.pay.api_ban", None)
		import linhx_core.pay.api_ban as api_ban

		with patch.object(api_ban, "tim_ham", return_value=[]):
			# Khi chưa cài gói cung cấp, gọi endpoint báo lỗi rõ ràng thay vì sập lúc import
			fake_frappe.throw.side_effect = RuntimeError("chua_cai_goi")
			with pytest.raises(RuntimeError, match="chua_cai_goi"):
				api_ban.goi()
			fake_frappe.throw.side_effect = None

		kq_don = api_ban.tao_don(brand="Thương Hiệu A", goi="GOI-QUYEN-DUNG")
		assert kq_don["so_tien"] == 150000
		# tao_don tuyệt đối không ghi đè loai_giao của LX Goi
		fake_frappe.db.set_value.assert_not_called()
		assert catalog_db[0]["loai_giao"] == "quyen_dung"

		# Hàm migrate dam_bao_loai_giao_bao_cao chỉ điền loai_giao='bao_cao' cho gói báo cáo đang trống loai_giao
		da_cap_nhat = sau_tra.dam_bao_loai_giao_bao_cao()
		assert da_cap_nhat == ["BC-AI"]
		fake_frappe.db.set_value.assert_called_once_with(
			"LX Goi",
			"BC-AI",
			"loai_giao",
			"bao_cao",
			update_modified=False,
		)


def test_worker_don_dep_ghi_log_khi_su_kien_loi():
	fake_frappe = MagicMock()
	fake_frappe.whitelist = lambda *a, **kw: (lambda fn: fn)
	fake_frappe.db.table_exists.return_value = False
	fake_frappe.get_all.return_value = []
	fake_rate_limiter = MagicMock()
	fake_rate_limiter.rate_limit = lambda *a, **kw: (lambda fn: fn)
	fake_utils = MagicMock()

	with patch.dict(
		sys.modules,
		{
			"frappe": fake_frappe,
			"frappe.rate_limiter": fake_rate_limiter,
			"frappe.utils": fake_utils,
		},
	):
		sys.modules.pop("linhx_worker.quy_trinh", None)
		sys.modules.pop("linhx_worker.api", None)
		import linhx_worker.api as worker_api

		with patch.object(worker_api.su_kien, "chay", side_effect=RuntimeError("loi_outbox")):
			worker_api.don_dep()
			fake_frappe.log_error.assert_called_once()


