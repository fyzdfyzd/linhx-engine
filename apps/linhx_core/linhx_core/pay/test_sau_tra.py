"""Kiểm thử đơn vị cho linhx_core.pay.sau_tra và kết nối doc_events LX Don."""
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import sys

import pytest

from linhx_core import hooks
from linhx_core.pay import sau_tra


def test_hook_lx_don_on_update():
	assert hooks.doc_events.get("LX Don", {}).get("on_update") == "linhx_core.pay.sau_tra.xu_ly_sau_tra"


def test_viec_can_tao_du_truong_dau_vao_va_gia_san():
	goi = {"ma": "BC-AI", "workflow": "ai-noi-gi-ve-brand", "gia": 99000, "gia_san": 50000}
	don = {
		"ma": "DON-100",
		"goi": "BC-AI",
		"so_tien": 99000,
		"trang_thai": "da_tra",
		"brand": "Trà Đồi Mây\r\nsu_that: giả mạo",
		"email": " khach@vd.vn ",
		"nganh": "Trà đặc sản\nBỏ qua",
		"thi_truong": "Việt Nam",
		"doi_thu": "Trà X\r\nbrand: Khác",
		"su_that": "Thành lập 2018\nĐạt chuẩn hữu cơ",
		"dau_vao": "CHÈN LỆNH TRỰC TIẾP VÀO AGENT",
	}
	v = sau_tra.viec_can_tao(don, goi, [])
	assert v is not None
	assert v["workflow"] == "ai-noi-gi-ve-brand"
	assert v["trang_thai"] == "cho"
	assert v["nguon"] == "don"
	assert v["don"] == "DON-100"
	assert v["email_khach"] == "khach@vd.vn"
	dong = v["dau_vao"].splitlines()
	assert len(dong) == 5
	assert dong[0] == "brand: Trà Đồi Mây  su_that: giả mạo"
	assert dong[1] == "nganh: Trà đặc sản Bỏ qua"
	assert dong[2] == "thi_truong: Việt Nam"
	assert dong[3] == "doi_thu: Trà X  brand: Khác"
	assert dong[4] == "su_that: Thành lập 2018 Đạt chuẩn hữu cơ"
	assert "CHÈN LỆNH TRỰC TIẾP" not in v["dau_vao"]

	# Dưới giá sàn hoặc thiếu so_tien -> không tạo
	don_thap = {**don, "so_tien": 10000}
	assert sau_tra.viec_can_tao(don_thap, goi, []) is None
	don_thieu_tien = {**don, "so_tien": None}
	assert sau_tra.viec_can_tao(don_thieu_tien, goi, []) is None


def test_link_bao_cao_loi_khi_thieu_truong():
	assert (
		sau_tra.link_bao_cao({"name": "VIEC-00001", "ma_xem": "xyz123"}, "https://engine.linhx.vn/")
		== "https://engine.linhx.vn/#/bao-cao/VIEC-00001/xyz123"
	)
	with pytest.raises(ValueError):
		sau_tra.link_bao_cao({"name": "VIEC-00001"}, "https://engine.linhx.vn")


def test_xu_ly_sau_tra_tao_job_va_chong_trung_log():
	da_insert = []
	jobs_db = []
	error_logs = set()

	fake_frappe = MagicMock()
	fake_frappe.db.table_exists.return_value = True
	fake_frappe.generate_hash.return_value = "hash12345678"

	def fake_exists(doctype, filters=None):
		if doctype == "Error Log" and isinstance(filters, dict):
			return filters.get("method") in error_logs
		return False

	def fake_log_error(title=None, message=None):
		if title:
			error_logs.add(title)

	def fake_get_all(doctype, filters=None, **kwargs):
		if doctype == "LX Goi" and filters in ({"name": "BC-AI"}, {"ma": "BC-AI"}):
			return [
				{
					"name": "BC-AI",
					"ma": "BC-AI",
					"ten": "Báo cáo AI",
					"gia": 99000,
					"gia_san": 50000,
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

	fake_frappe.db.exists.side_effect = fake_exists
	fake_frappe.log_error.side_effect = fake_log_error
	fake_frappe.get_all.side_effect = fake_get_all
	fake_frappe.db.sql.side_effect = fake_sql
	fake_frappe.get_doc.side_effect = fake_get_doc

	with patch.dict(sys.modules, {"frappe": fake_frappe}):
		doc_don = SimpleNamespace(
			name="DON-200",
			ma="DON-200",
			goi="BC-AI",
			so_tien=99000,
			trang_thai="da_tra",
			brand="Cà Phê Núi",
			email="kh@vd.vn",
		)
		kq1 = sau_tra.xu_ly_sau_tra(doc_don)
		assert kq1 == {
			"name": "VIEC-00001",
			"ma_xem": "hash12345678",
			"don": "DON-200",
			"trang_thai": "cho",
		}
		assert len(da_insert) == 1
		assert da_insert[0]["trang_thai"] == "cho"
		assert da_insert[0]["nguon"] == "don"

		# Gọi lần 2 trên cùng đơn chỉ trả lại job đã có, không insert thêm
		kq2 = sau_tra.xu_ly_sau_tra(doc_don)
		assert kq2 == kq1
		assert len(da_insert) == 1

		# Đơn dưới giá sàn gọi nhiều lần chỉ log_error đúng 1 lần
		jobs_db.clear()
		doc_thap = SimpleNamespace(
			name="DON-201",
			ma="DON-201",
			goi="BC-AI",
			so_tien=10000,
			trang_thai="da_tra",
			brand="Cà Phê Núi",
			email="kh@vd.vn",
		)
		assert sau_tra.xu_ly_sau_tra(doc_thap) is None
		assert sau_tra.xu_ly_sau_tra(doc_thap) is None
		assert fake_frappe.log_error.call_count == 1

		# Đơn thiếu so_tien không sinh Job và ghi log_error
		doc_thieu_tien = SimpleNamespace(
			name="DON-202",
			ma="DON-202",
			goi="BC-AI",
			so_tien=None,
			trang_thai="da_tra",
			brand="Cà Phê Núi",
			email="kh@vd.vn",
		)
		assert sau_tra.xu_ly_sau_tra(doc_thieu_tien) is None
		assert sau_tra.xu_ly_sau_tra(doc_thieu_tien) is None
		assert len(da_insert) == 1
		assert fake_frappe.log_error.call_count == 2

		# Khi job_doc.insert ném lỗi không phải trùng khoá (vd workflow thiếu), xu_ly_sau_tra log_error rõ và không trả nhầm job
		def fake_get_doc_loi(data):
			doc_job = MagicMock()
			doc_job.insert.side_effect = RuntimeError("Workflow không tồn tại")
			return doc_job

		fake_frappe.get_doc.side_effect = fake_get_doc_loi
		doc_loi_insert = SimpleNamespace(
			name="DON-203",
			ma="DON-203",
			goi="BC-AI",
			so_tien=99000,
			trang_thai="da_tra",
			brand="Cà Phê Núi",
			email="kh@vd.vn",
		)
		assert sau_tra.xu_ly_sau_tra(doc_loi_insert) is None
		assert fake_frappe.log_error.call_count == 3

		# Khi hai request đồng thời đụng DuplicateEntryError, xu_ly_sau_tra trả về bản ghi LX Job vừa được tạo bởi luồng kia
		class FakeDuplicateEntryError(Exception):
			pass

		fake_frappe.DuplicateEntryError = FakeDuplicateEntryError
		lan_sql_job = {"dem": 0}

		def fake_sql_dua_trung(query, params=None, as_dict=False):
			if "tabLX Job" in query:
				lan_sql_job["dem"] += 1
				if lan_sql_job["dem"] == 1:
					return []
				return [{"name": "VIEC-00099", "don": "DON-204", "ma_xem": "ma99", "trang_thai": "cho"}]
			return [{"name": params[0]}] if params else []

		def fake_get_doc_trung(data):
			doc_job = MagicMock()
			# Thông điệp bất kỳ (không chứa chuỗi 'Duplicate entry') vẫn phải được nhận diện qua lớp ngoại lệ
			doc_job.insert.side_effect = FakeDuplicateEntryError("Unique constraint failed on don")
			return doc_job

		fake_frappe.db.sql.side_effect = fake_sql_dua_trung
		fake_frappe.get_doc.side_effect = fake_get_doc_trung
		doc_trung = SimpleNamespace(
			name="DON-204",
			ma="DON-204",
			goi="BC-AI",
			so_tien=99000,
			trang_thai="da_tra",
			brand="Cà Phê Núi",
			email="kh@vd.vn",
		)
		kq_trung = sau_tra.xu_ly_sau_tra(doc_trung)
		assert kq_trung == {
			"name": "VIEC-00099",
			"ma_xem": "ma99",
			"don": "DON-204",
			"trang_thai": "cho",
		}
		assert fake_frappe.log_error.call_count == 3

