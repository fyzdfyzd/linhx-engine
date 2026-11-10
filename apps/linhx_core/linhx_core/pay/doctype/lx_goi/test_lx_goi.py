"""Kiểm thử đơn vị cho giao_hang (thuần Python + nối su_kien + giả lập Frappe DB) và controller LXGoi."""
from __future__ import annotations

import importlib
import json
import sys
import types
import pytest

from linhx_core import giao_hang, su_kien


def test_phat_mot_lan_khi_don_chuyen_sang_da_tra_bo_nho():
	kho: list[dict] = []

	class DonGia:
		def __init__(self, name: str, trang_thai: str, cu: str | None):
			self.name = name
			self.trang_thai = trang_thai
			self._cu = cu

		def get_doc_before_save(self):
			if self._cu is None:
				return None
			return types.SimpleNamespace(trang_thai=self._cu)

	# Mới tạo ở cho_tra -> không phát
	d1 = DonGia("DON-10", "cho_tra", None)
	giao_hang.ghi_nhan_trang_thai_truoc_luu(d1)
	assert giao_hang.phat_khi_don_da_tra(d1, kho=kho) is None
	assert kho == []

	# Chuyển cho_tra -> da_tra -> phát đúng 1 lần
	d2 = DonGia("DON-10", "da_tra", "cho_tra")
	giao_hang.ghi_nhan_trang_thai_truoc_luu(d2)
	sk = giao_hang.phat_khi_don_da_tra(d2, kho=kho)
	assert sk is not None and sk["ten"] == "don.da_tra" and sk["du_lieu"] == {"don": "DON-10"}
	assert len(kho) == 1

	# Lưu lại khi vẫn đang da_tra -> không phát lại
	d3 = DonGia("DON-10", "da_tra", "da_tra")
	giao_hang.ghi_nhan_trang_thai_truoc_luu(d3)
	assert giao_hang.phat_khi_don_da_tra(d3, kho=kho) is None
	assert len(kho) == 1

	# Kể cả gọi lặp thiếu _doc_before_save trên cùng đơn -> chống trùng theo kho
	d4 = DonGia("DON-10", "da_tra", None)
	assert giao_hang.phat_khi_don_da_tra(d4, kho=kho) is None
	assert len(kho) == 1


def test_chon_ham_va_xu_ly_cac_nhanh_loi():
	ds = [
		{"ten": "linhx_goi_baocao", "giao": {"bao_cao": "linhx_goi_baocao.giao.giao"}},
		{"ten": "linhx_goi_booking", "giao": {"lich": "linhx_goi_booking.giao.giao"}},
	]

	with pytest.raises(ValueError):
		giao_hang.chon_ham("", ds)
	with pytest.raises(ValueError):
		giao_hang.chon_ham("quyen_dung", ds)
	with pytest.raises(ValueError):
		giao_hang.chon_ham("lich", ds + [{"ten": "goi_khac", "giao": {"lich": "goi_khac.giao"}}])
	with pytest.raises(ValueError):
		giao_hang.chon_ham("tep", [{"ten": "goi_sai", "giao": {"tep": "khong_dau_cham"}}])

	with pytest.raises(ValueError):
		giao_hang.xu_ly({"ten": "don.da_tra", "du_lieu": {}}, lambda _: {"loai_giao": "lich"}, ds, lambda *_: None)
	with pytest.raises(ValueError):
		giao_hang.xu_ly(
			{"ten": "don.da_tra", "du_lieu": {"don": "DON-1"}},
			lambda _: {"name": "G1", "loai_giao": ""},
			ds,
			lambda *_: None,
		)

	# doc_goi chỉ trả bản ghi gói (name != ten_don) vẫn giữ đúng don["name"] == ten_don
	da_giao: list[tuple[str, str, str]] = []
	duong = giao_hang.xu_ly(
		{"ten": "don.da_tra", "du_lieu": {"don": "DON-88"}},
		lambda _: {"name": "GOI-LICH", "loai_giao": "lich"},
		ds,
		lambda d, don, g: da_giao.append((d, don["name"], g["name"])),
	)
	assert duong == "linhx_goi_booking.giao.giao"
	assert da_giao == [("linhx_goi_booking.giao.giao", "DON-88", "GOI-LICH")]


def test_luong_day_du_su_kien_den_nghe_va_frappe_gia_lap(monkeypatch):
	bang_don = {
		"DON_100%": {
			"name": "DON_100%",
			"ma": "DON_100%",
			"goi": "GOI-BC",
			"so_tien": 99000,
			"trang_thai": "da_tra",
		}
	}
	bang_goi = {
		"GOI-BC": {
			"name": "GOI-BC",
			"ma": "GOI-BC",
			"loai_giao": "bao_cao",
			"gia_san": 50000,
		}
	}
	bang_su_kien: list[dict] = []
	da_goi_giao: list[tuple[str, str]] = []

	mod_goi_gia = types.ModuleType("mod_goi_baocao_gia")
	mod_goi_gia.giao_ngay = lambda don, goi: da_goi_giao.append((don["name"], goi["loai_giao"]))  # type: ignore[attr-defined]
	monkeypatch.setitem(sys.modules, "mod_goi_baocao_gia", mod_goi_gia)

	class FakeValidationError(Exception):
		pass

	class FakeDoc:
		def __init__(self, du_lieu: dict):
			self._data = dict(du_lieu)
			for k, v in du_lieu.items():
				setattr(self, k, v)

		def as_dict(self):
			return dict(self._data)

		def insert(self, ignore_permissions: bool = False):
			self.name = f"SK-{len(bang_su_kien) + 1}"
			bang_su_kien.append(
				{
					"name": self.name,
					"ten": self.ten,
					"du_lieu": self.du_lieu,
					"trang_thai": self.trang_thai,
					"lan": self.lan,
					"da_giao": self.da_giao,
					"loi": self.loi,
				}
			)
			return self

	class FakeDB:
		@staticmethod
		def table_exists(dt: str) -> bool:
			return dt in {"LX Don", "LX Goi", "LX Su Kien"}

		@staticmethod
		def exists(dt: str, name: object) -> bool:
			if dt == "LX Don":
				return str(name) in bang_don
			if dt == "LX Goi":
				return str(name) in bang_goi
			return False

		@staticmethod
		def get_value(dt: str, filters: object, fieldname: str):
			if dt == "LX Don" and isinstance(filters, str) and filters in bang_don:
				return bang_don[filters].get(fieldname)
			return None

		@staticmethod
		def sql(query: str, params: tuple = (), as_dict: bool = False):
			if "FROM `tabLX Su Kien`" in query:
				return list(bang_su_kien)
			return []

	fake_frappe = types.ModuleType("frappe")
	fake_frappe.ValidationError = FakeValidationError  # type: ignore[attr-defined]
	fake_frappe.db = FakeDB()  # type: ignore[attr-defined]
	fake_frappe.local = types.SimpleNamespace(site=None)  # type: ignore[attr-defined]

	def _throw(msg, exc=FakeValidationError):
		raise exc(msg)

	fake_frappe.throw = _throw  # type: ignore[attr-defined]

	def _get_doc(arg1, arg2=None, **kwargs):
		if isinstance(arg1, dict):
			return FakeDoc(arg1)
		if arg1 == "LX Don":
			return FakeDoc(bang_don[arg2])
		if arg1 == "LX Goi":
			return FakeDoc(bang_goi[arg2])
		raise KeyError((arg1, arg2))

	fake_frappe.get_doc = _get_doc  # type: ignore[attr-defined]

	fake_model = types.ModuleType("frappe.model")
	fake_doc_mod = types.ModuleType("frappe.model.document")

	class BaseDocument:
		def __init__(self, **kw):
			for k, v in kw.items():
				setattr(self, k, v)

	fake_doc_mod.Document = BaseDocument  # type: ignore[attr-defined]

	monkeypatch.setitem(sys.modules, "frappe", fake_frappe)
	monkeypatch.setitem(sys.modules, "frappe.model", fake_model)
	monkeypatch.setitem(sys.modules, "frappe.model.document", fake_doc_mod)
	monkeypatch.setattr(
		giao_hang,
		"_lay_danh_sach_module",
		lambda thu_muc_apps=None: [
			{"ten": "linhx_goi_baocao", "giao": {"bao_cao": "mod_goi_baocao_gia.giao_ngay"}}
		],
	)

	# Phát qua DB giả lập (kèm ký tự % và _ trong mã đơn) chỉ 1 lần duy nhất
	don_obj = types.SimpleNamespace(
		name="DON_100%",
		trang_thai="da_tra",
		get_doc_before_save=lambda: types.SimpleNamespace(trang_thai="cho_tra"),
	)
	sk1 = giao_hang.phat_khi_don_da_tra(don_obj)
	sk2 = giao_hang.phat_khi_don_da_tra(don_obj)
	assert sk1 is not None and sk2 is None
	assert len(bang_su_kien) == 1

	# Bảng nghe đọc từ apps/linhx_core/module.json phải nối đúng linhx_core.giao_hang.nghe
	bang_nghe = su_kien.lay_bang_nghe()
	assert "linhx_core.giao_hang.nghe" in bang_nghe.get("don.da_tra", [])

	kho_chay = [dict(bang_su_kien[0])]
	kq = su_kien.chay(kho=kho_chay, bang_nghe=bang_nghe)
	assert kq == {"xong": 1, "loi": 0}
	assert da_goi_giao == [("DON_100%", "bao_cao")]

	# Kiểm thử controller LXGoi.validate
	mod_lx_goi = importlib.import_module("linhx_core.pay.doctype.lx_goi.lx_goi")
	importlib.reload(mod_lx_goi)
	goi_ok = mod_lx_goi.LXGoi(ma="G1", loai_giao=" lich ")
	goi_ok.validate()
	assert goi_ok.loai_giao == "lich"

	goi_rong = mod_lx_goi.LXGoi(ma="G2", loai_giao="  ")
	goi_rong.validate()
	assert goi_rong.loai_giao is None

	with pytest.raises(FakeValidationError):
		mod_lx_goi.LXGoi(ma="G3", loai_giao="khong_hop_le").validate()
