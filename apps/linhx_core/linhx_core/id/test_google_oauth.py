"""Kiểm thử đơn vị cho `linhx_core.id.google_oauth` và `linhx_core.id.api_auth`."""
from __future__ import annotations

import sys
import types
from types import SimpleNamespace
from unittest import mock

import pytest

from linhx_core.id import google_oauth

LUC = "2026-11-09 10:00:00"


def test_gop_trung_bu_truong_trong_va_giu_truong_cu():
    ds = [{"name": "NG-01", "email": "  LAN.NGUYEN@VD.VN  ", "dien_thoai": "0912345678"}]
    nk: list[dict] = []
    kq = google_oauth.dang_nhap_google(
        {"sub": "gg-1001", "email": "lan.nguyen@vd.vn", "email_verified": True, "name": "Lan Google"},
        state_gui="st-abc-123",
        state_phien="st-abc-123",
        ds_nguoi=ds,
        nhat_ky_gop=nk,
        luc=LUC,
    )
    assert kq["da_gop"] is True
    assert len(kq["ds_nguoi"]) == 1
    assert kq["nguoi"]["ho_ten"] == "Lan Google"
    assert kq["nguoi"]["google_sub"] == "gg-1001"
    assert kq["nguoi"]["dien_thoai"] == "0912345678"
    assert len(nk) == 1
    assert nk[0]["hanh_dong"] == "gop"
    assert nk[0]["nguoi"] == "NG-01"


def test_tao_moi_khi_email_chua_co():
    ds = [{"name": "NG-01", "ho_ten": "Lan", "email": "lan@vd.vn"}]
    nk: list[dict] = []
    kq = google_oauth.dang_nhap_google(
        {"sub": "gg-2002", "email": "Minh.Moi@VD.vn", "email_verified": True, "name": "Minh Mới"},
        state_gui="st-xyz",
        state_phien="st-xyz",
        ds_nguoi=ds,
        nhat_ky_gop=nk,
        luc=LUC,
    )
    assert kq["da_gop"] is False
    assert len(kq["ds_nguoi"]) == 2
    assert kq["nguoi"]["email"] == "minh.moi@vd.vn"
    assert kq["nguoi"]["ho_ten"] == "Minh Mới"
    assert kq["nguoi"]["google_sub"] == "gg-2002"
    assert len(nk) == 1
    assert nk[0]["hanh_dong"] == "tao_moi"
    assert nk[0]["email"] == "minh.moi@vd.vn"


def test_tu_choi_dau_vao_khong_hop_le():
    ho_so_ok = {"sub": "gg-1", "email": "a@vd.vn", "email_verified": True}
    with pytest.raises(ValueError):
        google_oauth.dang_nhap_google(ho_so_ok, "   ", "   ", [], [], LUC)
    with pytest.raises(ValueError):
        google_oauth.dang_nhap_google(ho_so_ok, None, "st", [], [], LUC)  # type: ignore[arg-type]

    for ev in (False, None, "true", 1, 0):
        with pytest.raises(ValueError):
            google_oauth.dang_nhap_google(
                {"sub": "gg-1", "email": "a@vd.vn", "email_verified": ev},
                "st-ok",
                "st-ok",
                [],
                [],
                LUC,
            )

    for bad in (
        {"sub": "gg-1", "email": "", "email_verified": True},
        {"sub": "gg-1", "email": "khong-co-a-cong", "email_verified": True},
        {"sub": "", "email": "a@vd.vn", "email_verified": True},
    ):
        with pytest.raises(ValueError):
            google_oauth.dang_nhap_google(bad, "st-ok", "st-ok", [], [], LUC)


def test_api_google_callback_tieu_thu_state_va_gop_nguoi():
    frappe_mod = types.ModuleType("frappe")
    frappe_mod.whitelist = lambda *a, **kw: (lambda fn: fn)
    frappe_mod.ValidationError = ValueError
    frappe_mod.PermissionError = PermissionError

    def _throw(msg, exc=ValueError):
        raise exc(msg)

    frappe_mod.throw = _throw
    session_data = {"oauth_state_google": "st-session-99"}
    frappe_mod.session = SimpleNamespace(data=session_data, sid="sid-1")
    frappe_mod.local = SimpleNamespace(request=None, response={})

    rl_mod = types.ModuleType("frappe.rate_limiter")
    rl_mod.rate_limit = lambda *a, **kw: (lambda fn: fn)

    with mock.patch.dict(sys.modules, {"frappe": frappe_mod, "frappe.rate_limiter": rl_mod}):
        sys.modules.pop("linhx_core.id.api_auth", None)
        from linhx_core.id import api_auth

        api_auth._kiem_module_crm_bat = lambda: None
        kho_db = [{"name": "NG-55", "ho_ten": "Lan Cũ", "email": "LAN.CU@VD.VN", "dien_thoai": "0909000111"}]
        api_auth._tim_nguoi_theo_email = lambda em: list(kho_db)
        api_auth._luu_nguoi_sau_gop = lambda ng, dg, em: ng.get("name") or "NG-MOI"

        kq = api_auth.google_callback(
            state="st-session-99",
            ho_so_google={"sub": "gg-55", "email": "lan.cu@vd.vn", "email_verified": True, "name": "Lan Mới"},
        )
        assert kq["ok"] is True
        assert kq["nguoi"] == "NG-55"
        assert kq["da_gop"] is True
        assert "oauth_state_google" not in session_data, "state OAuth trong session phải được tiêu thụ một lần"

        # Gọi lại lần 2 với cùng state -> bị từ chối vì state trong session đã được tiêu thụ
        with pytest.raises(ValueError):
            api_auth.google_callback(
                state="st-session-99",
                ho_so_google={"sub": "gg-55", "email": "lan.cu@vd.vn", "email_verified": True},
            )
