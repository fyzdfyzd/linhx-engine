"""Kiểm thử DocType và controller `LX Lich Goi` trong `linhx_core` (F2 / G3):
kiểm tra quyền đơn vị và tra hàm kiểm giờ làm / trùng giờ qua `dang_ky_module`.
Note: các ca kiểm thử logic đặt lịch (`dat_lich`), endpoint `api_booking` và giao hàng (`giao`)
đã chuyển sang `apps/linhx_goi_booking/linhx_goi_booking/test_goi_booking.py`.
"""
from __future__ import annotations

import importlib
import json
import pathlib
import sys
import types
from unittest.mock import patch

import pytest

GOC_APPS = pathlib.Path(__file__).resolve().parents[3]
for p in (GOC_APPS / "linhx_core", GOC_APPS / "linhx_goi_booking"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def test_doctype_lx_lich_goi_cau_truc():
    thu_muc_dt = pathlib.Path(__file__).resolve().parent / "doctype" / "lx_lich_goi"
    d = json.loads((thu_muc_dt / "lx_lich_goi.json").read_text(encoding="utf-8"))
    assert d["name"] == "LX Lich Goi"
    truong = {f["fieldname"]: f for f in d["fields"]}
    for ten in ("nguoi", "co_hoi", "phu_trach", "don_vi", "bat_dau", "ket_thuc", "phut", "trang_thai", "ghi_chu", "nguon"):
        assert ten in truong, f"thiếu trường {ten}"
    quyen = {p["role"]: p for p in d.get("permissions", [])}
    assert quyen["System Manager"]["read"] == 1
    assert quyen["LX Nhan Vien"]["read"] == 1


def test_controller_lx_lich_goi_goi_qua_dang_ky_module():
    class FakeValidationError(ValueError):
        pass

    class FakePermissionError(PermissionError):
        pass

    kho_lich = [
        {
            "name": "LG-001",
            "nguoi": "NG-01",
            "co_hoi": "CH-01",
            "phu_trach": "sale1@vd.vn",
            "don_vi": "DV-A",
            "bat_dau": "2026-11-10 09:00:00",
            "ket_thuc": "2026-11-10 09:30:00",
            "phut": 30,
            "trang_thai": "cho_goi",
        }
    ]
    kho_nguoi = {
        "NG-01": {"name": "NG-01", "don_vi": "DV-A"},
        "NG-02": {"name": "NG-02", "don_vi": "DV-B"},
    }
    kho_co_hoi = {
        "CH-01": {"name": "CH-01", "nguoi": "NG-01", "don_vi": "DV-A"},
        "CH-02": {"name": "CH-02", "nguoi": "NG-02", "don_vi": "DV-B"},
    }

    def fake_throw(msg, exc=FakeValidationError):
        if isinstance(exc, type) and issubclass(exc, BaseException):
            raise exc(msg)
        raise FakeValidationError(msg)

    def fake_get_all(doctype, filters=None, pluck=None, **kwargs):
        if doctype == "LX Lich Goi":
            pt = (filters or {}).get("phu_trach")
            return [dict(x) for x in kho_lich if (not pt or x.get("phu_trach") == pt) and x.get("trang_thai") != "huy"]
        if doctype == "User Permission":
            user_f = (filters or {}).get("user")
            if user_f == "sale1@vd.vn":
                return ["DV-A"] if pluck else [{"user": "sale1@vd.vn", "for_value": "DV-A"}]
            if user_f == "sale2@vd.vn":
                return ["DV-B"] if pluck else [{"user": "sale2@vd.vn", "for_value": "DV-B"}]
            return []
        return []

    def fake_get_value(doctype, name, fieldname, as_dict=False):
        if doctype == "LX Nguoi" and name in kho_nguoi:
            return dict(kho_nguoi[name]) if as_dict else kho_nguoi[name].get(fieldname)
        if doctype == "LX Co Hoi" and name in kho_co_hoi:
            return dict(kho_co_hoi[name]) if as_dict else kho_co_hoi[name].get(fieldname)
        if doctype == "LX Lich Goi" and name == "LG-001":
            return dict(kho_lich[0]) if as_dict else kho_lich[0].get(fieldname)
        return None

    fake_frappe = types.ModuleType("frappe")
    fake_frappe.ValidationError = FakeValidationError
    fake_frappe.PermissionError = FakePermissionError
    fake_frappe.throw = fake_throw
    fake_frappe.get_all = fake_get_all
    fake_frappe.get_roles = lambda u=None: ["System Manager"] if u == "Administrator" else ["LX Nhan Vien"]
    fake_frappe.session = types.SimpleNamespace(user="sale1@vd.vn")
    fake_frappe.db = types.SimpleNamespace(
        get_value=fake_get_value,
        exists=lambda dt, n: True,
        sql=None,
    )

    fake_model = types.ModuleType("frappe.model")
    fake_doc_mod = types.ModuleType("frappe.model.document")

    class BaseDocument:
        def __init__(self, d=None):
            self.flags = types.SimpleNamespace(ignore_permissions=False)
            for k, v in (d or {}).items():
                setattr(self, k, v)

    fake_doc_mod.Document = BaseDocument
    ten_mod = "linhx_core.booking.doctype.lx_lich_goi.lx_lich_goi"

    with patch.dict(
        sys.modules,
        {
            "frappe": fake_frappe,
            "frappe.model": fake_model,
            "frappe.model.document": fake_doc_mod,
        },
    ):
        try:
            sys.modules.pop(ten_mod, None)
            mod_lg = importlib.import_module(ten_mod)

            doc_hop_le = mod_lg.LXLichGoi(
                {
                    "nguoi": "NG-01",
                    "phu_trach": "sale1@vd.vn",
                    "bat_dau": "2026-11-10 14:00:00",
                    "phut": 30,
                    "trang_thai": "cho_goi",
                }
            )
            doc_hop_le.before_insert()
            assert doc_hop_le.don_vi == "DV-A"
            assert doc_hop_le.ket_thuc == "2026-11-10 14:30:00"
            assert doc_hop_le.has_permission("read", user="sale1@vd.vn") is True
            assert doc_hop_le.has_permission("read", user="sale2@vd.vn") is False

            # Điều kiện lọc SQL theo đơn vị
            cond_s1 = mod_lg.frappe_permission_query_conditions(user="sale1@vd.vn")
            assert "DV-A" in cond_s1
            assert mod_lg.frappe_permission_query_conditions(user="Administrator") == ""

            # Trùng giờ với LG-001 (09:00 - 09:30) -> bị chặn
            doc_trung = mod_lg.LXLichGoi(
                {
                    "nguoi": "NG-01",
                    "phu_trach": "sale1@vd.vn",
                    "bat_dau": "2026-11-10 09:15:00",
                    "phut": 30,
                    "trang_thai": "cho_goi",
                }
            )
            with pytest.raises(FakeValidationError):
                doc_trung.before_insert()

            # Cơ hội của khách khác -> bị chặn
            doc_sai_co_hoi = mod_lg.LXLichGoi(
                {
                    "nguoi": "NG-01",
                    "co_hoi": "CH-02",
                    "phu_trach": "sale1@vd.vn",
                    "bat_dau": "2026-11-10 15:00:00",
                    "phut": 30,
                    "trang_thai": "cho_goi",
                }
            )
            with pytest.raises(FakeValidationError):
                doc_sai_co_hoi.before_insert()

            # Không được đổi người đặt của lịch đã tạo
            doc_sua_nguoi = mod_lg.LXLichGoi(
                {
                    "name": "LG-001",
                    "nguoi": "NG-02",
                    "phu_trach": "sale1@vd.vn",
                    "don_vi": "DV-A",
                    "bat_dau": "2026-11-10 16:00:00",
                    "phut": 30,
                    "trang_thai": "cho_goi",
                }
            )
            with pytest.raises((FakeValidationError, FakePermissionError)):
                doc_sua_nguoi.validate()
        finally:
            sys.modules.pop(ten_mod, None)
            from linhx_core.booking.doctype import lx_lich_goi as pkg_lg

            if hasattr(pkg_lg, "lx_lich_goi"):
                delattr(pkg_lg, "lx_lich_goi")
