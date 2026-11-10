"""Kiểm thử đơn vị cho gói `linhx_goi_booking` (F2 / G3):
nạp thuần Python không cần Frappe, kiểm giờ làm việc 8–18h giờ VN, chặn trùng giờ,
API đặt lịch `dat_lich_goi` / `viec_cho_lich_goi`, và hàm giao hàng `giao` cho `loai_giao == 'lich'`.
"""
from __future__ import annotations

import importlib
import pathlib
import sys
import types
from unittest.mock import patch

import pytest

GOC_APPS = pathlib.Path(__file__).resolve().parents[2]
for p in (GOC_APPS / "linhx_core", GOC_APPS / "linhx_goi_booking"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from linhx_goi_booking import api_booking, dat_lich, giao


def test_nap_thuan_python_khong_can_frappe():
    with patch.dict(sys.modules, {"frappe": None}):
        for mod_name in (
            "linhx_goi_booking.dat_lich",
            "linhx_goi_booking.api_booking",
            "linhx_goi_booking.giao",
        ):
            sys.modules.pop(mod_name, None)
            mod = importlib.import_module(mod_name)
            assert mod is not None


def test_dat_lich_gio_lam_viec_va_mui_gio():
    ds = dat_lich.dat_lich(
        [],
        {"nguoi": "NG-01", "phu_trach": "sale1@vd.vn", "bat_dau": "2026-11-10 08:00:00", "phut": 30},
    )
    assert len(ds) == 1
    assert ds[0]["ket_thuc"] == "2026-11-10 08:30:00"
    assert ds[0]["trang_thai"] == "cho_goi"

    ds = dat_lich.dat_lich(
        ds,
        {"nguoi": "NG-02", "phu_trach": "sale1@vd.vn", "bat_dau": "2026-11-10T02:00:00Z", "phut": 30},
    )
    assert ds[-1]["bat_dau"] == "2026-11-10 09:00:00"
    assert ds[-1]["ket_thuc"] == "2026-11-10 09:30:00"

    for gio_sai in (
        "2026-11-10 07:59:59",
        "2026-11-10 17:31:00",
        "2026-11-10 18:00:00",
        "2026-11-10",
        "",
    ):
        with pytest.raises(ValueError):
            dat_lich.dat_lich(
                [],
                {"nguoi": "NG-01", "phu_trach": "sale1@vd.vn", "bat_dau": gio_sai, "phut": 30},
            )


def test_dat_lich_trung_gio_va_viec_cho():
    goc = [
        {
            "nguoi": "NG-01",
            "phu_trach": "sale1@vd.vn",
            "bat_dau": "2026-11-10 10:00:00",
            "ket_thuc": "2026-11-10 10:30:00",
            "phut": 30,
            "trang_thai": "cho_goi",
        },
        {
            "nguoi": "NG-02",
            "phu_trach": "sale1@vd.vn",
            "bat_dau": "2026-11-10 11:00:00",
            "ket_thuc": "2026-11-10 11:30:00",
            "phut": 30,
            "trang_thai": "huy",
        },
    ]
    with pytest.raises(ValueError):
        dat_lich.dat_lich(
            goc,
            {"nguoi": "NG-03", "phu_trach": "sale1@vd.vn", "bat_dau": "2026-11-10 10:15:00", "phut": 30},
        )

    moi = dat_lich.dat_lich(
        goc,
        {"nguoi": "NG-03", "phu_trach": "sale1@vd.vn", "bat_dau": "2026-11-10 11:00:00", "phut": 30},
    )
    assert len(goc) == 2
    assert len(moi) == 3

    vc = dat_lich.viec_cho(moi, phu_trach="sale1@vd.vn")
    assert [x["nguoi"] for x in vc] == ["NG-01", "NG-03"]


def test_giao_lich_qua_luong_giao_hang_chung():
    from linhx_core import dang_ky_module, giao_hang

    ds_mod = dang_ky_module.quet(GOC_APPS)
    duong_ham = giao_hang.chon_ham("lich", ds_mod)
    assert duong_ham == "linhx_goi_booking.giao.giao"

    don = {
        "name": "DON-LICH-01",
        "ma": "DON-LICH-01",
        "goi": "GOI-TU-VAN",
        "nguoi": "NG-01",
        "phu_trach": "sale1@vd.vn",
        "bat_dau": "2026-11-10 09:00:00",
        "phut": 30,
        "so_tien": 500000,
        "trang_thai": "da_tra",
    }
    goi_dict = {
        "name": "GOI-TU-VAN",
        "ma": "GOI-TU-VAN",
        "gia": 500000,
        "gia_san": 400000,
        "loai_giao": "lich",
    }

    kho_lich: list[dict] = []
    kho_quyen: list[dict] = []
    kq = giao.giao(don, goi_dict, ds_lich=kho_lich, kho_quyen=kho_quyen)
    assert kq["ok"] is True
    assert kq["loai_giao"] == "lich"
    assert kq["trang_thai"] == "da_dat_lich"
    assert len(kho_lich) == 1
    assert kho_lich[0]["bat_dau"] == "2026-11-10 09:00:00"
    assert len(kho_quyen) == 1
    assert kho_quyen[0]["don"] == "DON-LICH-01"

    # Đơn chưa thanh toán hoặc dưới giá sàn -> từ chối
    with pytest.raises(ValueError):
        giao.giao({**don, "trang_thai": "cho_tra"}, goi_dict)
    with pytest.raises(ValueError):
        giao.giao({**don, "so_tien": 100000}, goi_dict)


def test_api_booking_voi_mock_frappe():
    class FakeValidationError(ValueError):
        pass

    class FakePermissionError(PermissionError):
        pass

    kho_lich: list[dict] = []
    kho_nguoi: dict[str, dict] = {
        "NG-01": {
            "name": "NG-01",
            "ho_ten": "Khách Một",
            "dien_thoai": "0912345678",
            "email": "khach1@vd.vn",
            "don_vi": "DV-A",
        }
    }
    kho_co_hoi: list[dict] = [
        {
            "name": "CH-01",
            "nguoi": "NG-01",
            "phu_trach": "sale1@vd.vn",
            "don_vi": "DV-A",
            "trang_thai": "moi",
            "creation": "2026-11-10 08:00:00",
        }
    ]
    kho_dong_y: list[dict] = [
        {
            "name": "DY-01",
            "nguoi": "NG-01",
            "muc_dich": "lien_he",
            "dong_y": 1,
            "luc": "2026-11-10 08:00:00",
            "nguon": "trang-ifagent",
        }
    ]

    class FakeDoc:
        def __init__(self, d: dict):
            self.flags = types.SimpleNamespace(ignore_permissions=False)
            for k, v in d.items():
                setattr(self, k, v)

        def insert(self, ignore_permissions: bool = False):
            if getattr(self, "doctype", "") == "LX Lich Goi":
                self.name = f"LG-{len(kho_lich) + 1:03d}"
                kho_lich.append(
                    {
                        "name": self.name,
                        "nguoi": self.nguoi,
                        "co_hoi": getattr(self, "co_hoi", ""),
                        "phu_trach": self.phu_trach,
                        "don_vi": getattr(self, "don_vi", ""),
                        "bat_dau": self.bat_dau,
                        "ket_thuc": self.ket_thuc,
                        "phut": self.phut,
                        "trang_thai": self.trang_thai,
                        "ghi_chu": getattr(self, "ghi_chu", ""),
                    }
                )
            return self

    def fake_throw(msg, exc=FakeValidationError):
        if isinstance(exc, type) and issubclass(exc, BaseException):
            raise exc(msg)
        raise FakeValidationError(msg)

    def fake_get_all(doctype, filters=None, pluck=None, **kwargs):
        if doctype == "LX Lich Goi":
            pt = (filters or {}).get("phu_trach")
            return [dict(x) for x in kho_lich if (not pt or x.get("phu_trach") == pt) and x.get("trang_thai") != "huy"]
        if doctype == "LX Co Hoi":
            ng = (filters or {}).get("nguoi")
            return [dict(x) for x in kho_co_hoi if not ng or x.get("nguoi") == ng]
        if doctype == "LX Dong Y":
            return [dict(x) for x in kho_dong_y]
        if doctype == "LX Nguoi":
            return [dict(v) for v in kho_nguoi.values()]
        if doctype == "User Permission":
            user_f = (filters or {}).get("user")
            if user_f == "sale1@vd.vn":
                return ["DV-A"] if pluck else [{"user": "sale1@vd.vn", "for_value": "DV-A"}]
            return []
        return []

    def fake_get_value(doctype, name, fieldname, as_dict=False):
        if doctype == "LX Nguoi" and name in kho_nguoi:
            return dict(kho_nguoi[name]) if as_dict else kho_nguoi[name].get(fieldname)
        if doctype == "LX Co Hoi":
            for ch in kho_co_hoi:
                if ch["name"] == name:
                    return dict(ch) if as_dict else ch.get(fieldname)
            return None
        if doctype == "User":
            return {"name": name, "enabled": 1, "user_type": "System User"} if as_dict else 1
        return None

    fake_frappe = types.ModuleType("frappe")
    fake_frappe.ValidationError = FakeValidationError
    fake_frappe.PermissionError = FakePermissionError
    fake_frappe.DuplicateEntryError = RuntimeError
    fake_frappe.throw = fake_throw
    fake_frappe.whitelist = lambda *a, **kw: (lambda fn: fn)
    fake_frappe.get_all = fake_get_all
    fake_frappe.get_roles = lambda u=None: ["LX Nhan Vien"]
    fake_frappe.get_doc = lambda arg1, arg2=None: (
        FakeDoc(kho_nguoi[arg2]) if arg1 == "LX Nguoi" and arg2 in kho_nguoi else FakeDoc(arg1 if isinstance(arg1, dict) else {})
    )
    fake_frappe.local = types.SimpleNamespace(
        site="ifagent",
        request_ip="127.0.0.1",
        request=types.SimpleNamespace(
            method="POST",
            headers={},
            content_length=120,
            get_data=lambda **kw: b"{}",
            get_json=lambda **kw: None,
        ),
        form_dict={},
        response={},
        _lx_cau_hinh_cache={"bat_crm": 1, "bat_pay": 1},
    )
    fake_frappe.session = types.SimpleNamespace(user="Guest")
    fake_frappe.db = types.SimpleNamespace(
        get_value=fake_get_value,
        exists=lambda dt, n: n in kho_nguoi if dt == "LX Nguoi" else True,
        sql=None,
    )
    fake_frappe.cache = lambda: None

    with patch.dict(sys.modules, {"frappe": fake_frappe}):
        kq1 = api_booking.dat_lich_goi(
            nguoi="NG-01",
            dien_thoai="0912345678",
            bat_dau="2026-11-10 09:00:00",
            phut=30,
            ghi_chu="Tư vấn Agent Force",
            dong_y_lien_he=True,
        )
        assert kq1["ok"] is True
        assert kq1["phu_trach"] == "sale1@vd.vn"
        assert kq1["bat_dau"] == "2026-11-10 09:00:00"

        with pytest.raises(FakeValidationError):
            api_booking.dat_lich_goi(
                nguoi="NG-01",
                dien_thoai="0912345678",
                phu_trach="sale1@vd.vn",
                bat_dau="2026-11-10 09:15:00",
                phut=30,
                dong_y_lien_he=True,
            )
        assert fake_frappe.local.response.get("http_status_code") == 409

        fake_frappe.session.user = "sale1@vd.vn"
        ds_vc = api_booking.viec_cho_lich_goi()
        assert len(ds_vc) == 1
        assert ds_vc[0]["nguoi"] == "NG-01"
