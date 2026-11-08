import sys
import types
from types import SimpleNamespace


def _mock_frappe(monkeypatch):
	da_insert = []

	class FakeDoc:
		def __init__(self, d):
			self.__dict__.update(d)
			self.flags = SimpleNamespace()
			self._new = True

		def is_new(self):
			return self._new

		def insert(self, ignore_permissions=False):
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
	)
	fake_frappe.db = SimpleNamespace(commit=lambda: None)
	fake_frappe.get_doc = lambda d: FakeDoc(d)

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
	return fake_frappe, da_insert


def test_ghi_nhat_ky_khi_mo_khach_va_chong_trung(monkeypatch):
	fake_frappe, da_insert = _mock_frappe(monkeypatch)
	sys.modules.pop("linhx_core.linhx_core.doctype.lx_nhat_ky_truy_cap.lx_nhat_ky_truy_cap", None)
	from linhx_core.linhx_core.doctype.lx_nhat_ky_truy_cap import lx_nhat_ky_truy_cap as nk

	monkeypatch.setattr(nk, "frappe", fake_frappe)
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

	# Gọi lần hai trong cùng request hoặc cùng doc flags không tạo bản ghi trùng
	assert nk.ghi_nhat_ky_truy_cap(doc_khach, method="onload") is None
	assert len(da_insert) == 1


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

