"""Kiểm thử đơn vị cho su_kien (thuần Python + giả lập Frappe DB) và controller LXSuKien."""
from __future__ import annotations

import importlib
import json
import sys
import types
import pytest

from linhx_core import su_kien


def test_phat_sao_chep_du_lieu_va_chong_sua_ngoai():
	kho: list[dict] = []
	goc = {"don": "DON-1", "chi_tiet": {"so_tien": 100000}}
	ban_ghi = su_kien.phat("don.da_tra", goc, kho)
	goc["don"] = "BI-SUA"
	goc["chi_tiet"]["so_tien"] = 0

	assert ban_ghi["du_lieu"] == {"don": "DON-1", "chi_tiet": {"so_tien": 100000}}
	assert ban_ghi["trang_thai"] == "cho"
	assert ban_ghi["lan"] == 0
	assert ban_ghi["da_giao"] == []

	nhan: list[str] = []

	def ham_nghe(duong: str, su_kien_nhan: dict):
		nhan.append(f"{duong}:{su_kien_nhan['du_lieu']['don']}")
		su_kien_nhan["du_lieu"]["don"] = "HONG"

	kq = su_kien.chay(kho, {"don.da_tra": ["goi_a.xu_ly", "goi_b.xu_ly"]}, ham_nghe)
	assert kq == {"xong": 1, "loi": 0}
	assert nhan == ["goi_a.xu_ly:DON-1", "goi_b.xu_ly:DON-1"]
	assert kho[0]["trang_thai"] == "xong"


def test_chay_hoi_phuc_truoc_tran_va_su_kien_khong_nguoi_nghe():
	kho: list[dict] = []
	su_kien.phat("don.da_tra", {"don": "DON-3"}, kho)
	su_kien.phat("he_thong.ping", None, kho)

	dem = {"lan": 0}

	def goi(duong: str, b: dict):
		dem["lan"] += 1
		if dem["lan"] < 3:
			raise ConnectionError("tạm đứt kết nối")

	bang = {"don.da_tra": ["goi_bc.giao"]}
	kq1 = su_kien.chay(kho, bang, goi)
	assert kq1 == {"xong": 1, "loi": 1}
	assert kho[0]["trang_thai"] == "cho" and kho[0]["lan"] == 1
	assert kho[1]["trang_thai"] == "xong"

	kq2 = su_kien.chay(kho, bang, goi)
	assert kq2 == {"xong": 0, "loi": 1}
	assert kho[0]["lan"] == 2 and kho[0]["trang_thai"] == "cho"

	kq3 = su_kien.chay(kho, bang, goi)
	assert kq3 == {"xong": 1, "loi": 0}
	assert kho[0]["trang_thai"] == "xong"
	assert kho[0]["loi"] == ""
	assert kho[0]["da_giao"] == ["goi_bc.giao"]


def test_lay_bang_nghe_va_goi_ham_nghe_dong(tmp_path, monkeypatch):
	app_loi = tmp_path / "linhx_core"
	app_loi.mkdir()
	(app_loi / "module.json").write_text(
		json.dumps(
			{
				"ten": "linhx_core",
				"ban": "0.3.0",
				"lop": "loi",
				"nghe": {"don.da_tra": "mod_gia_su_kien.nghe_loi"},
			}
		),
		encoding="utf-8",
	)
	app_goi = tmp_path / "linhx_goi_thu"
	app_goi.mkdir()
	(app_goi / "module.json").write_text(
		json.dumps(
			{
				"ten": "linhx_goi_thu",
				"ban": "0.1.0",
				"lop": "goi",
				"can_loi": ">=0.3.0",
				"phu_thuoc": ["linhx_core"],
				"nghe": {"don.da_tra": "mod_gia_su_kien.nghe_goi"},
			}
		),
		encoding="utf-8",
	)

	da_nhan: list[tuple[str, str]] = []
	mod_gia = types.ModuleType("mod_gia_su_kien")
	mod_gia.nghe_loi = lambda b: da_nhan.append(("loi", b["du_lieu"]["don"]))  # type: ignore[attr-defined]
	mod_gia.nghe_goi = lambda b: da_nhan.append(("goi", b["du_lieu"]["don"]))  # type: ignore[attr-defined]
	monkeypatch.setitem(sys.modules, "mod_gia_su_kien", mod_gia)

	bang = su_kien.lay_bang_nghe(tmp_path)
	assert bang == {"don.da_tra": ["mod_gia_su_kien.nghe_loi", "mod_gia_su_kien.nghe_goi"]}

	kho: list[dict] = []
	su_kien.phat("don.da_tra", {"don": "DON-7"}, kho)
	kq = su_kien.chay(kho, bang)
	assert kq == {"xong": 1, "loi": 0}
	assert da_nhan == [("loi", "DON-7"), ("goi", "DON-7")]


def test_che_do_frappe_db_rollback_khi_loi_va_validate_controller(monkeypatch):
	class FakeValidationError(Exception):
		pass

	da_commit_db: dict[str, dict] = {}
	ban_nhap_tx: dict[str, dict] = {}
	lich_su_tx: list[str] = []
	log_loi: list[tuple[str, str]] = []

	class FakeDoc:
		def __init__(self, d: dict):
			for k, v in d.items():
				setattr(self, k, v)

		def insert(self, ignore_permissions: bool = False):
			if not getattr(self, "name", None):
				self.name = f"SK-{len(da_commit_db) + len(ban_nhap_tx) + 1}"
			ban_nhap_tx[self.name] = {
				"name": self.name,
				"ten": self.ten,
				"du_lieu": self.du_lieu,
				"trang_thai": self.trang_thai,
				"lan": self.lan,
				"da_giao": self.da_giao,
				"loi": self.loi,
			}
			return self

		def save(self, ignore_permissions: bool = False):
			ban_nhap_tx[self.name] = {
				"name": self.name,
				"ten": self.ten,
				"du_lieu": self.du_lieu,
				"trang_thai": self.trang_thai,
				"lan": self.lan,
				"da_giao": self.da_giao,
				"loi": self.loi,
			}
			return self

	class FakeDB:
		@staticmethod
		def commit():
			for k, v in ban_nhap_tx.items():
				da_commit_db[k] = dict(v)
			ban_nhap_tx.clear()
			lich_su_tx.append("commit")

		@staticmethod
		def rollback():
			ban_nhap_tx.clear()
			lich_su_tx.append("rollback")

	fake_frappe = types.ModuleType("frappe")
	fake_frappe.ValidationError = FakeValidationError  # type: ignore[attr-defined]
	fake_frappe.db = FakeDB()  # type: ignore[attr-defined]
	fake_frappe.local = types.SimpleNamespace(site="test.local")  # type: ignore[attr-defined]
	fake_frappe.get_installed_apps = lambda: ["linhx_core"]  # type: ignore[attr-defined]

	def _throw(msg, exc=FakeValidationError):
		raise exc(msg)

	fake_frappe.throw = _throw  # type: ignore[attr-defined]
	fake_frappe.log_error = lambda title="", message="": log_loi.append((title, message))  # type: ignore[attr-defined]

	def _get_doc(arg1, arg2=None, for_update: bool = False):
		if isinstance(arg1, dict):
			return FakeDoc(arg1)
		nguon = ban_nhap_tx.get(arg2) or da_commit_db[arg2]
		return FakeDoc(dict(nguon))

	def _get_all(dt, filters=None, pluck=None, **kwargs):
		ket = [
			k
			for k, v in da_commit_db.items()
			if not filters or v.get("trang_thai") == filters.get("trang_thai")
		]
		return ket

	fake_frappe.get_doc = _get_doc  # type: ignore[attr-defined]
	fake_frappe.get_all = _get_all  # type: ignore[attr-defined]

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

	# Kiểm thử phat + chay qua Frappe giả lập
	su_kien.phat("don.da_tra", {"don": "DON-99"})
	fake_frappe.db.commit()

	da_goi: list[str] = []

	def goi_thu(duong: str, b: dict):
		da_goi.append(duong)
		if duong == "b.loi":
			# Ghi bẩn chưa commit phải bị rollback
			ban_nhap_tx["BAN-NHAP"] = {"name": "BAN-NHAP", "trang_thai": "rac"}
			raise RuntimeError("lỗi cổng mạng")

	for _ in range(su_kien.TRAN_LAN + 1):
		su_kien.chay(kho=None, bang_nghe={"don.da_tra": ["a.xong", "b.loi"]}, goi=goi_thu)

	assert "BAN-NHAP" not in da_commit_db
	assert da_goi.count("a.xong") == 1
	assert da_goi.count("b.loi") == su_kien.TRAN_LAN
	assert da_commit_db["SK-1"]["trang_thai"] == "hong"
	assert json.loads(da_commit_db["SK-1"]["da_giao"]) == ["a.xong"]
	assert "lỗi cổng mạng" in da_commit_db["SK-1"]["loi"]
	assert len(log_loi) == 1

	# Kiểm thử controller LXSuKien.validate
	mod_ctrl = importlib.import_module("linhx_core.linhx_core.doctype.lx_su_kien.lx_su_kien")
	importlib.reload(mod_ctrl)
	doc_ok = mod_ctrl.LXSuKien(ten=" don.da_tra ", du_lieu={"don": "D1"}, trang_thai="cho", lan="0")
	doc_ok.validate()
	assert doc_ok.ten == "don.da_tra"
	assert json.loads(doc_ok.du_lieu) == {"don": "D1"}
	assert doc_ok.da_giao == "[]"

	with pytest.raises(FakeValidationError):
		mod_ctrl.LXSuKien(ten="", trang_thai="cho").validate()
	with pytest.raises(FakeValidationError):
		mod_ctrl.LXSuKien(ten="x", trang_thai="sai").validate()
	with pytest.raises(FakeValidationError):
		mod_ctrl.LXSuKien(ten="x", trang_thai="cho", du_lieu="{khong-json").validate()
