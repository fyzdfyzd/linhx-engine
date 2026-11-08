import sys
import types
from types import SimpleNamespace


def _mock_frappe(monkeypatch):
	da_insert = []
	da_log_error = []
	so_lan_commit = [0]
	loi_insert = [False]

	class FakeDoc:
		def __init__(self, d):
			self.__dict__.update(d)
			self.flags = SimpleNamespace()
			self._new = True

		def is_new(self):
			return self._new

		def insert(self, ignore_permissions=False):
			if loi_insert[0]:
				raise RuntimeError("DB tạm thời gián đoạn")
			self.ignore_permissions = ignore_permissions
			self.name = f"NK-{len(da_insert) + 1:04d}"
			da_insert.append(self)
			return self

	fake_frappe = types.ModuleType("frappe")
	fake_frappe.PermissionError = PermissionError
	fake_frappe.session = SimpleNamespace(user="kiem@test.local")
	fake_frappe.local = SimpleNamespace(
		request_ip="10.0.0.25",
		request=SimpleNamespace(method="GET", path="/api/resource/LX Nguoi/NGUOI-001", headers={}),
		form_dict={},
		response={},
	)

	def _commit():
		so_lan_commit[0] += 1

	def _log_error(title=None, message=None):
		da_log_error.append((title, message))

	fake_frappe.db = SimpleNamespace(commit=_commit)
	fake_frappe.get_doc = lambda d: FakeDoc(d)
	fake_frappe.log_error = _log_error

	def _throw(msg, exc=Exception):
		raise exc(msg)

	fake_frappe.throw = _throw

	fake_doc_mod = types.ModuleType("frappe.model.document")

	class Document:
		def __init__(self, d=None):
			self.flags = SimpleNamespace()
			self._new = True
			if isinstance(d, dict):
				self.__dict__.update(d)

		def is_new(self):
			return self._new

	fake_doc_mod.Document = Document
	fake_utils = types.ModuleType("frappe.utils")
	fake_utils.now_datetime = lambda: "2026-11-08 16:35:00"

	monkeypatch.setitem(sys.modules, "frappe", fake_frappe)
	monkeypatch.setitem(sys.modules, "frappe.model", types.ModuleType("frappe.model"))
	monkeypatch.setitem(sys.modules, "frappe.model.document", fake_doc_mod)
	monkeypatch.setitem(sys.modules, "frappe.utils", fake_utils)
	return fake_frappe, da_insert, da_log_error, so_lan_commit, loi_insert


def _nap_module(monkeypatch, fake_frappe):
	sys.modules.pop("linhx_core.linhx_core.doctype.lx_nhat_ky_truy_cap.lx_nhat_ky_truy_cap", None)
	from linhx_core.linhx_core.doctype.lx_nhat_ky_truy_cap import lx_nhat_ky_truy_cap as nk

	monkeypatch.setattr(nk, "frappe", fake_frappe)
	return nk


def test_ghi_nhat_ky_khi_mo_khach_va_chong_trung(monkeypatch):
	fake_frappe, da_insert, _, so_lan_commit, _ = _mock_frappe(monkeypatch)
	nk = _nap_module(monkeypatch, fake_frappe)

	doc_khach = SimpleNamespace(doctype="LX Nguoi", name="NGUOI-001", flags=SimpleNamespace())
	kq = nk.ghi_nhat_ky_truy_cap(doc_khach, method="onload")
	assert kq is not None
	assert len(da_insert) == 1
	assert da_insert[0].nguoi_dung == "kiem@test.local"
	assert da_insert[0].loai_ban_ghi == "LX Nguoi"
	assert da_insert[0].ma_ban_ghi == "NGUOI-001"
	assert da_insert[0].hanh_dong == "xem"
	assert da_insert[0].ip == "10.0.0.25"
	assert da_insert[0].ignore_permissions is True
	assert so_lan_commit[0] == 1

	# Gọi lần hai trong cùng request hoặc cùng doc flags không tạo bản ghi trùng
	assert nk.ghi_nhat_ky_truy_cap(doc_khach, method="onload") is None
	assert len(da_insert) == 1


def test_loi_insert_ghi_log_error_va_khong_dat_co_trung(monkeypatch):
	fake_frappe, da_insert, da_log_error, _, loi_insert = _mock_frappe(monkeypatch)
	nk = _nap_module(monkeypatch, fake_frappe)

	doc_khach = SimpleNamespace(doctype="LX Nguoi", name="NGUOI-002", flags=SimpleNamespace())
	loi_insert[0] = True
	assert nk.ghi_nhat_ky_truy_cap(doc_khach, method="onload") is None
	assert len(da_insert) == 0
	assert len(da_log_error) == 1
	assert "LX Nguoi/NGUOI-002/xem" in da_log_error[0][1]

	# Lần gọi sau trong cùng request phải thử lại được vì cờ chống trùng chưa bật
	loi_insert[0] = False
	kq = nk.ghi_nhat_ky_truy_cap(doc_khach, method="onload")
	assert kq is not None
	assert len(da_insert) == 1


def test_commit_khi_goi_onload_qua_post(monkeypatch):
	fake_frappe, da_insert, _, so_lan_commit, _ = _mock_frappe(monkeypatch)
	nk = _nap_module(monkeypatch, fake_frappe)

	fake_frappe.local.request = SimpleNamespace(
		method="POST",
		path="/api/method/frappe.desk.form.load.getdoc",
		headers={},
	)
	doc_khach = SimpleNamespace(doctype="LX Nguoi", name="NGUOI-003", flags=SimpleNamespace())
	kq = nk.ghi_nhat_ky_truy_cap(doc_khach, method="onload")
	assert kq is not None
	assert len(da_insert) == 1
	assert so_lan_commit[0] == 1


def test_after_request_phu_danh_sach_get_value_reportview_xuat(monkeypatch):
	fake_frappe, da_insert, _, so_lan_commit, _ = _mock_frappe(monkeypatch)
	nk = _nap_module(monkeypatch, fake_frappe)

	# 1. GET /api/resource/LX Nguoi (danh sách)
	fake_frappe.local = SimpleNamespace(
		request_ip="10.0.0.25",
		request=SimpleNamespace(method="GET", path="/api/resource/LX Nguoi", headers={}),
		form_dict={},
		response={"data": [{"name": "NGUOI-101"}, {"name": "NGUOI-102"}]},
	)
	nk.ghi_nhat_ky_tu_request(SimpleNamespace(status_code=200))
	assert [(x.ma_ban_ghi, x.hanh_dong) for x in da_insert] == [
		("NGUOI-101", "xem"),
		("NGUOI-102", "xem"),
	]

	# 2. POST frappe.client.get_list
	da_insert.clear()
	fake_frappe.local = SimpleNamespace(
		request_ip="10.0.0.25",
		request=SimpleNamespace(method="POST", path="/api/method/frappe.client.get_list", headers={}),
		form_dict={"doctype": "LX To Chuc"},
		response={"message": [{"name": "TC-001"}]},
	)
	nk.ghi_nhat_ky_tu_request(SimpleNamespace(status_code=200))
	assert [(x.loai_ban_ghi, x.ma_ban_ghi, x.hanh_dong) for x in da_insert] == [
		("LX To Chuc", "TC-001", "xem"),
	]

	# 3. POST frappe.client.get_value
	da_insert.clear()
	fake_frappe.local = SimpleNamespace(
		request_ip="10.0.0.25",
		request=SimpleNamespace(method="POST", path="/api/method/frappe.client.get_value", headers={}),
		form_dict={"doctype": "LX Nguoi", "filters": '{"name": "NGUOI-201"}'},
		response={"message": {"dien_thoai": "0901234567"}},
	)
	nk.ghi_nhat_ky_tu_request(SimpleNamespace(status_code=200))
	assert [(x.loai_ban_ghi, x.ma_ban_ghi, x.hanh_dong) for x in da_insert] == [
		("LX Nguoi", "NGUOI-201", "xem"),
	]

	# 4. POST frappe.desk.reportview.get (dạng nén keys/values)
	da_insert.clear()
	fake_frappe.local = SimpleNamespace(
		request_ip="10.0.0.25",
		request=SimpleNamespace(method="POST", path="/api/method/frappe.desk.reportview.get", headers={}),
		form_dict={"doctype": "LX Don Vi"},
		response={"message": {"keys": ["ho_ten", "name"], "values": [["Đơn vị A", "DV-01"]]}},
	)
	nk.ghi_nhat_ky_tu_request(SimpleNamespace(status_code=200))
	assert [(x.loai_ban_ghi, x.ma_ban_ghi, x.hanh_dong) for x in da_insert] == [
		("LX Don Vi", "DV-01", "xem"),
	]

	# 5. Xuất dữ liệu frappe.desk.reportview.export_query
	da_insert.clear()
	fake_frappe.local = SimpleNamespace(
		request_ip="10.0.0.25",
		request=SimpleNamespace(method="POST", path="/api/method/frappe.desk.reportview.export_query", headers={}),
		form_dict={"doctype": "LX Nguoi"},
		response={},
	)
	nk.ghi_nhat_ky_tu_request(SimpleNamespace(status_code=200))
	assert [(x.loai_ban_ghi, x.ma_ban_ghi, x.hanh_dong) for x in da_insert] == [
		("LX Nguoi", "*", "xuat"),
	]
	assert so_lan_commit[0] >= 5


def kiem_tren_bench():
	"""Hàm kiểm thực tế trên Frappe bench: tạo LX Nguoi, mở qua onload và trả bản ghi LX Nhat Ky Truy Cap."""
	import frappe

	frappe.set_user("Administrator")
	frappe.local.request_ip = "10.0.0.88"
	khach = frappe.get_doc(
		{
			"doctype": "LX Nguoi",
			"ho_ten": "Khách kiểm N6",
			"dien_thoai": "0911222333",
			"email": "n6@test.local",
		}
	).insert(ignore_permissions=True)
	doc_mo = frappe.get_doc("LX Nguoi", khach.name)
	doc_mo.run_method("onload")
	frappe.db.commit()
	ds = frappe.get_all(
		"LX Nhat Ky Truy Cap",
		filters={"loai_ban_ghi": "LX Nguoi", "ma_ban_ghi": doc_mo.name, "hanh_dong": "xem"},
		fields=["name", "nguoi_dung", "loai_ban_ghi", "ma_ban_ghi", "hanh_dong", "thoi_diem", "ip"],
		order_by="creation desc",
		limit_page_length=1,
	)
	kq = dict(ds[0]) if ds else {}
	if "thoi_diem" in kq and kq["thoi_diem"] is not None:
		kq["thoi_diem"] = str(kq["thoi_diem"])
	return kq
