"""Kiểm thử đơn vị cho adapter Việt Nam `linhx_vn.pay`."""
from __future__ import annotations

import pathlib
import sys
import types

import pytest

GOC_REPO = pathlib.Path(__file__).resolve().parents[4]
for _app_dir in (GOC_REPO / "apps" / "linhx_core", GOC_REPO / "apps" / "linhx_vn", GOC_REPO / "apps" / "linhx_goi_baocao"):
    _s = str(_app_dir)
    if _s not in sys.path:
        sys.path.insert(0, _s)

from linhx_core import api as core_api
from linhx_vn.pay import api_sepay, api_thue, sepay, so_s1a, vietqr


def test_khai_bao_cung_cap_va_nghe_module_json():
    assert core_api.tim_ham("cung_cap", "vn.tao_don") == ["linhx_vn.pay.vietqr.tao_don"]
    assert core_api.tim_ham("cung_cap", "vn.noi_dung_ck") == ["linhx_vn.pay.vietqr.noi_dung_ck"]
    assert core_api.tim_ham("cung_cap", "vn.qr_url") == ["linhx_vn.pay.vietqr.qr_url"]
    assert core_api.tim_ham("cung_cap", "vn.xu_ly_sepay") == ["linhx_vn.pay.sepay.xu_ly"]
    assert core_api.tim_ham("cung_cap", "vn.webhook_sepay") == ["linhx_vn.pay.api_sepay.webhook"]
    assert core_api.tim_ham("cung_cap", "vn.xac_thuc_sepay_hook") == ["linhx_vn.pay.api_sepay.xac_thuc_sepay_hook"]
    assert core_api.tim_ham("cung_cap", "vn.ghi_so_s1a_tu_don") == ["linhx_vn.pay.so_s1a.ghi_so_s1a_tu_don"]
    assert core_api.tim_ham("cung_cap", "vn.canh_bao_thue") == ["linhx_vn.pay.api_thue.canh_bao_thue"]
    assert core_api.tim_ham("nghe", "don.da_tra") == [
        "linhx_core.giao_hang.nghe",
        "linhx_vn.pay.so_s1a.nghe_don_da_tra",
    ]


def test_webhook_sepay_goi_danh_dau_da_tra_cua_loi(monkeypatch):
    da_goi_danh_dau: list[tuple] = []
    nhat_ky_da_ghi: list[dict] = []

    class _DocGia:
        def __init__(self, du_lieu: dict):
            self.__dict__.update(du_lieu)

        def insert(self, ignore_permissions: bool = False):
            nhat_ky_da_ghi.append(dict(self.__dict__))
            return self

    don_doc = _DocGia(
        {
            "name": "DON-VN-01",
            "ma": "DON-VN-01",
            "so_tien": 99000,
            "trang_thai": "cho_tra",
            "noi_dung_ck": "LXDONVN01",
            "tx_id": None,
        }
    )

    class _DB:
        def sql(self, query, params=(), as_dict=False):
            return []

        def commit(self):
            pass

        def rollback(self):
            pass

    frappe_gia = types.SimpleNamespace(
        conf={"sepay_khoa": "khoa-thu-vn"},
        local=types.SimpleNamespace(response={}, _lx_sepay_auth="Apikey khoa-thu-vn"),
        request=None,
        db=_DB(),
        DuplicateEntryError=RuntimeError,
        get_request_header=lambda h: "Apikey khoa-thu-vn",
        get_site_path=lambda p: "/khong-ton-tai/site_config.json",
        get_all=lambda dt, **kw: [
            {
                "name": "DON-VN-01",
                "ma": "DON-VN-01",
                "so_tien": 99000,
                "trang_thai": "cho_tra",
                "noi_dung_ck": "LXDONVN01",
                "tx_id": None,
            }
        ],
        get_doc=lambda arg1, arg2=None, **kw: (
            don_doc if arg1 == "LX Don" else _DocGia(arg1)
        ),
    )

    monkeypatch.setattr(api_sepay, "_lay_frappe", lambda: frappe_gia)
    monkeypatch.setattr(
        api_sepay,
        "danh_dau_da_tra",
        lambda don, tx_id=None, so_tien=None: da_goi_danh_dau.append((don, tx_id, so_tien)) or {"name": don, "trang_thai": "da_tra"},
    )

    kq = api_sepay.webhook(
        id=778899,
        transferType="in",
        transferAmount=99000,
        content="Chuyen khoan LXDONVN01",
        accountNumber="001100998877",
    )
    assert kq["success"] is True and kq["khop"] is True and kq["ma_don"] == "DON-VN-01"
    assert da_goi_danh_dau == [("DON-VN-01", "778899", 99000)]
    assert don_doc.trang_thai == "cho_tra", "webhook không tự sửa trạng thái đơn mà uỷ quyền cho linhx_core.api.danh_dau_da_tra"
    assert len(nhat_ky_da_ghi) == 1 and "***8877" in nhat_ky_da_ghi[0]["du_lieu"]


def test_nghe_don_da_tra_ghi_so_s1a_chong_trung(monkeypatch):
    da_insert: list[dict] = []

    class _DocDon:
        name = "DON-S1A-1"
        ma = "DON-S1A-1"
        so_tien = 150000
        trang_thai = "da_tra"
        goi = "BC-AI"
        brand = "Cà Phê Núi"
        ngay = "2026-11-10"

    class _DocSo:
        def __init__(self, d):
            self.d = d

        def insert(self, ignore_permissions=False):
            da_insert.append(self.d)
            return self

    class _DB:
        def exists(self, dt, ten=None):
            if dt == "DocType":
                return True
            if dt == "LX Don":
                return ten == "DON-S1A-1"
            if dt == "LX So S1a" and isinstance(ten, dict):
                return any(x.get("ma_don") == ten.get("ma_don") for x in da_insert)
            return False

        def table_exists(self, dt):
            return True

    frappe_gia = types.SimpleNamespace(
        db=_DB(),
        DuplicateEntryError=RuntimeError,
        get_doc=lambda a, b=None: _DocDon() if a == "LX Don" else _DocSo(a),
    )
    utils_gia = types.SimpleNamespace(nowdate=lambda: "2026-11-10")
    monkeypatch.setitem(sys.modules, "frappe", frappe_gia)
    monkeypatch.setitem(sys.modules, "frappe.utils", utils_gia)

    so_s1a.nghe_don_da_tra({"ten": "don.da_tra", "du_lieu": '{"don": "DON-S1A-1"}'})
    so_s1a.nghe_don_da_tra({"ten": "don.da_tra", "du_lieu": {"don": "DON-S1A-1"}})
    assert len(da_insert) == 1
    assert da_insert[0]["ma_don"] == "DON-S1A-1" and da_insert[0]["so_tien"] == 150000


def test_canh_bao_thue_qua_api_loi(monkeypatch):
    class _PermErr(Exception):
        pass

    frappe_gia = types.SimpleNamespace(
        session=types.SimpleNamespace(user="op@linhx.vn"),
        PermissionError=_PermErr,
        throw=lambda msg, exc=ValueError: (_ for _ in ()).throw(exc(msg)),
        get_roles=lambda u: ["LX Operator"],
        db=types.SimpleNamespace(exists=lambda dt, ten=None: True),
        get_all=lambda dt, **kw: [
            {"ngay": "2026-05-01", "ma_don": "D1", "dien_giai": "Đơn 1", "so_tien": 950_000_000}
        ],
    )
    monkeypatch.setattr(api_thue, "_lay_frappe", lambda: frappe_gia)
    monkeypatch.setattr(api_thue, "doctype_bi_an", lambda dt: False)
    monkeypatch.setattr(api_thue, "doc_cau_hinh", lambda k: 1_000_000_000)

    kq = api_thue.canh_bao_thue(2026)
    assert kq == {"muc": "vang", "tong": 950_000_000, "nguong": 1_000_000_000}

    monkeypatch.setattr(api_thue, "doctype_bi_an", lambda dt: True)
    with pytest.raises(_PermErr):
        api_thue.canh_bao_thue(2026)
