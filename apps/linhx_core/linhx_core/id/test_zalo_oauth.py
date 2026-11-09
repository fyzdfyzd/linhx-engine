"""Kiểm thử đơn vị cho `linhx_core.id.zalo_oauth` và `linhx_core.id.api_auth.zalo_callback`."""
from __future__ import annotations

import importlib
import sys
import types
from types import SimpleNamespace
from unittest import mock

import pytest

import linhx_core.id as _id_pkg
from linhx_core.id import zalo_oauth

LUC = "2026-11-09 10:30:00"


def test_gop_theo_sdt_va_zalo_id_bu_truong_trong():
    ds = [{"name": "NG-10", "ho_ten": "Hùng", "dien_thoai": "0912 345 678"}]
    nk: list[dict] = []
    kq = zalo_oauth.dang_nhap_zalo(
        {"zalo_id": "zl_hung_1", "dien_thoai": "84912345678", "ho_ten": "Hùng Zalo", "oa_id": "oa_ifagent"},
        state_gui="st-zl-1",
        state_phien="st-zl-1",
        ds_nguoi=ds,
        nhat_ky_gop=nk,
        luc=LUC,
    )
    assert kq["da_gop"] is True
    assert len(kq["ds_nguoi"]) == 1
    assert kq["nguoi"]["ho_ten"] == "Hùng"
    assert kq["nguoi"]["zalo"] == "zl_hung_1"
    assert kq["nguoi"]["oa_id"] == "oa_ifagent"
    assert len(nk) == 1
    assert nk[0]["kenh"] == "zalo"
    assert nk[0]["hanh_dong"] == "gop"
    assert nk[0]["zalo_id"] == "zl_hung_1"
    assert nk[0]["nguoi"] == "NG-10"


def test_tao_moi_khi_chua_co_sdt_va_zalo_id():
    ds = [{"name": "NG-10", "ho_ten": "Hùng", "dien_thoai": "0912345678", "zalo": "zl_hung_1"}]
    nk: list[dict] = []
    kq = zalo_oauth.dang_nhap_zalo(
        {"zalo_id": "zl_lan_moi", "dien_thoai": "0933444555", "ho_ten": "Lan Mới"},
        state_gui="st-zl-moi",
        state_phien="st-zl-moi",
        ds_nguoi=ds,
        nhat_ky_gop=nk,
        luc=LUC,
    )
    assert kq["da_gop"] is False
    assert len(kq["ds_nguoi"]) == 2
    assert kq["nguoi"]["zalo"] == "zl_lan_moi"
    assert kq["nguoi"]["dien_thoai"] == "84933444555"
    assert kq["nguoi"]["ho_ten"] == "Lan Mới"
    assert len(nk) == 1
    assert nk[0]["hanh_dong"] == "tao_moi"
    assert nk[0]["zalo_id"] == "zl_lan_moi"


def test_tu_choi_state_hoac_ho_so_zalo_khong_hop_le():
    ho_so_ok = {"zalo_id": "zl_1", "dien_thoai": "0912345678"}
    for st_gui, st_phien in (("a", "b"), ("", "b"), ("a", ""), ("   ", "   ")):
        with pytest.raises(ValueError):
            zalo_oauth.dang_nhap_zalo(ho_so_ok, st_gui, st_phien, [], [], LUC)

    for bad in (
        {},
        {"zalo_id": ""},
        {"zalo_id": "   "},
        {"zalo_id": None},
        {"zalo_id": "zl co khoang trang"},
        {"zalo_id": "zl_1", "dien_thoai": "abc"},
        {"zalo_id": "zl_1", "dien_thoai": "123"},
    ):
        with pytest.raises(ValueError):
            zalo_oauth.dang_nhap_zalo(bad, "st-ok", "st-ok", [], [], LUC)


def test_api_zalo_callback_tieu_thu_state_va_gop_nguoi():
    frappe_mod = types.ModuleType("frappe")
    frappe_mod.whitelist = lambda *a, **kw: (lambda fn: fn)
    frappe_mod.ValidationError = ValueError
    frappe_mod.PermissionError = PermissionError

    def _throw(msg, exc=ValueError):
        raise exc(msg)

    frappe_mod.throw = _throw
    session_data = {"oauth_state_zalo": "st-zalo-99"}
    frappe_mod.session = SimpleNamespace(data=session_data, sid="sid-zl-1")
    frappe_mod.local = SimpleNamespace(request=None, response={})

    rl_mod = types.ModuleType("frappe.rate_limiter")
    rl_mod.rate_limit = lambda *a, **kw: (lambda fn: fn)

    try:
        with mock.patch.dict(sys.modules, {"frappe": frappe_mod, "frappe.rate_limiter": rl_mod}):
            sys.modules.pop("linhx_core.id.api_auth", None)
            _id_pkg.__dict__.pop("api_auth", None)
            api_auth = importlib.import_module("linhx_core.id.api_auth")

            api_auth._kiem_module_crm_bat = lambda: None
            kho_db = [{"name": "NG-88", "ho_ten": "Hùng Cũ", "dien_thoai": "0912 345 678"}]
            api_auth._tim_nguoi_theo_zalo_hoac_sdt = lambda zid, dt: list(kho_db)
            api_auth._luu_nguoi_zalo_sau_gop = lambda ng, dg, zid, dt: ng.get("name") or "NG-MOI"

            kq = api_auth.zalo_callback(
                state="st-zalo-99",
                ho_so_zalo={"zalo_id": "zl_88", "dien_thoai": "84912345678", "ho_ten": "Hùng Zalo"},
            )
            assert kq["ok"] is True
            assert kq["nguoi"] == "NG-88"
            assert kq["da_gop"] is True
            assert kq["nhat_ky_gop"][0]["kenh"] == "zalo"
            assert kq["nhat_ky_gop"][0]["hanh_dong"] == "gop"
            assert "oauth_state_zalo" not in session_data

            # Gọi lại lần 2 với cùng state -> bị từ chối vì state đã được tiêu thụ
            with pytest.raises(ValueError):
                api_auth.zalo_callback(
                    state="st-zalo-99",
                    ho_so_zalo={"zalo_id": "zl_88", "dien_thoai": "84912345678"},
                )
    finally:
        sys.modules.pop("linhx_core.id.api_auth", None)
        _id_pkg.__dict__.pop("api_auth", None)
