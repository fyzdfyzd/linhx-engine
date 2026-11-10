"""Test đơn vị cho linhx_goi_ops.ops.ban_phieu và linhx_goi_ops.ops.api_ban_phieu."""
from __future__ import annotations

import importlib
import sys
import types
import pytest

from linhx_goi_ops.ops import ban_phieu


def test_ds_phieu_cho_va_duyet_tra_phieu():
    ds = [
        {"name": "P1", "loai_phieu": "feature", "de": "Đề 1", "trang_thai": "nhap", "creation": "2026-11-09 08:00:00"},
        {"name": "P2", "loai_phieu": "feature", "de": "Đề 2", "trang_thai": "duyet", "creation": "2026-11-09 09:00:00"},
        {"name": "P3", "loai_phieu": "sua_loi", "de": "Đề 3", "trang_thai": "nhap", "creation": "2026-11-09 10:00:00"},
    ]
    cho = ban_phieu.ds_phieu_cho(ds)
    assert [p["name"] for p in cho] == ["P3", "P1"]

    with pytest.raises(PermissionError):
        ban_phieu.duyet_phieu(ds, "P3", ["Guest"])

    da_duyet = ban_phieu.duyet_phieu(ds, "P3", ["System Manager"])
    assert da_duyet["trang_thai"] == "duyet"
    assert ds[2]["trang_thai"] == "duyet"

    with pytest.raises(ValueError):
        ban_phieu.duyet_phieu(ds, "P3", ["System Manager"])

    with pytest.raises(ValueError):
        ban_phieu.tra_phieu(ds, "P1", "   ", ["LX Operator"])

    with pytest.raises(PermissionError):
        ban_phieu.tra_phieu(ds, "P1", "Thiếu mô tả", ["Desk User"])

    da_tra = ban_phieu.tra_phieu(ds, "P1", "  Thiếu tiêu chí kiểm thử  ", ["LX Operator"])
    assert da_tra["trang_thai"] == "tra"
    assert da_tra["ly_do_tra"] == "Thiếu tiêu chí kiểm thử"
    assert ds[0]["trang_thai"] == "tra"
    assert ds[0]["ly_do_tra"] == "Thiếu tiêu chí kiểm thử"


def test_api_ban_phieu_voi_frappe_gia(monkeypatch):
    class FakeDoc:
        def __init__(self, data: dict):
            self.__dict__.update(data)
            self.saved = False

        def save(self):
            self.saved = True

    kho = {
        "PH-10": FakeDoc(
            {
                "name": "PH-10",
                "loai_phieu": "feature",
                "de": "Thêm nút duyệt trên bàn",
                "vung": "front/**",
                "trang_thai": "nhap",
                "ly_do_tra": "",
                "creation": "2026-11-09 10:00:00",
            }
        ),
        "PH-11": FakeDoc(
            {
                "name": "PH-11",
                "loai_phieu": "sua_loi",
                "de": "Sửa tràn ngang 390px",
                "vung": "front/**",
                "trang_thai": "nhap",
                "ly_do_tra": "",
                "creation": "2026-11-09 11:00:00",
            }
        ),
    }

    fake_frappe = types.ModuleType("frappe")
    fake_frappe.PermissionError = PermissionError
    fake_frappe.ValidationError = ValueError
    fake_frappe.session = types.SimpleNamespace(user="operator@linhx.local")
    fake_frappe.request = None
    fake_frappe.db = types.SimpleNamespace(exists=lambda dt, name: True)
    fake_frappe.get_roles = lambda: ["LX Operator"]

    def _throw(msg, exc=Exception):
        raise exc(msg)

    fake_frappe.throw = _throw
    fake_frappe.whitelist = lambda *a, **kw: (lambda fn: fn)
    fake_frappe.get_all = lambda *a, **kw: [
        {
            "name": d.name,
            "loai_phieu": d.loai_phieu,
            "de": d.de,
            "vung": d.vung,
            "trang_thai": d.trang_thai,
            "ly_do_tra": d.ly_do_tra,
            "creation": d.creation,
        }
        for d in kho.values()
        if d.trang_thai == "nhap"
    ]
    fake_frappe.get_doc = lambda dt, name: kho[name]

    monkeypatch.setitem(sys.modules, "frappe", fake_frappe)
    sys.modules.pop("linhx_goi_ops.ops.api_ban_phieu", None)

    api_bp = importlib.import_module("linhx_goi_ops.ops.api_ban_phieu")

    ds = api_bp.phieu_cho()
    assert [x["name"] for x in ds] == ["PH-11", "PH-10"]

    kq_duyet = api_bp.duyet(ma_phieu="PH-11")
    assert kq_duyet["ok"] is True and kq_duyet["trang_thai"] == "duyet"
    assert kho["PH-11"].trang_thai == "duyet" and kho["PH-11"].saved is True

    with pytest.raises(ValueError):
        api_bp.tra_lai(ma_phieu="PH-10", ly_do="   ")

    kq_tra = api_bp.tra_lai(ma_phieu="PH-10", ly_do="Chưa rõ vùng sửa")
    assert kq_tra["ok"] is True and kq_tra["trang_thai"] == "tra"
    assert kq_tra["ly_do_tra"] == "Chưa rõ vùng sửa"
    assert kho["PH-10"].trang_thai == "tra" and kho["PH-10"].ly_do_tra == "Chưa rõ vùng sửa"
