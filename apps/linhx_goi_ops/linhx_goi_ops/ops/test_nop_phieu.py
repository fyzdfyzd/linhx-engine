"""Kiểm thử đơn vị cho nop_phieu.py và api_tho.nop."""
from __future__ import annotations

import datetime
import sys
import types

from linhx_goi_ops.ops import keo_phieu as kp


def _stub_frappe(monkeypatch, ds_db: list[dict], tho_khoa_bam: dict):
    frappe_mod = types.ModuleType("frappe")
    utils_mod = types.ModuleType("frappe.utils")
    utils_mod.now_datetime = lambda: datetime.datetime(2026, 11, 9, 22, 10, 0)

    frappe_mod.whitelist = lambda *a, **kw: (lambda fn: fn)
    frappe_mod.local = types.SimpleNamespace(response={})
    frappe_mod.conf = {"tho_khoa_bam": tho_khoa_bam}
    frappe_mod.request = None
    frappe_mod.get_site_path = lambda *a: "khong_ton_tai_site_config.json"
    frappe_mod.get_request_header = lambda *a: None

    ghi_sql = []
    ghi_set_value = []
    da_commit = {"n": 0}
    da_rollback = {"n": 0}

    def _sql(query, params=None, *a, **kw):
        ghi_sql.append((query, params))
        if params and len(params) >= 1:
            ten = params[0]
            return [dict(r) for r in ds_db if r.get("name") == ten]
        return [dict(r) for r in ds_db]

    def _set_value(dt, name, vals, **kw):
        ghi_set_value.append((dt, name, dict(vals)))
        for r in ds_db:
            if r["name"] == name:
                r.update(vals)

    frappe_mod.db = types.SimpleNamespace(
        sql=_sql,
        set_value=_set_value,
        commit=lambda: da_commit.__setitem__("n", da_commit["n"] + 1),
        rollback=lambda: da_rollback.__setitem__("n", da_rollback["n"] + 1),
    )

    monkeypatch.setitem(sys.modules, "frappe", frappe_mod)
    monkeypatch.setitem(sys.modules, "frappe.utils", utils_mod)
    sys.modules.pop("linhx_goi_ops.ops.api_tho", None)
    from linhx_goi_ops.ops import api_tho

    return api_tho, frappe_mod, ghi_sql, ghi_set_value, da_commit, da_rollback


def test_api_tho_nop_401_403_200_va_chong_trung(monkeypatch):
    ds_db = [
        {
            "name": "PH-301",
            "loai_phieu": "feature",
            "de": "Làm O3 API nộp phiếu",
            "vung": "apps/linhx_goi_ops/**",
            "trang_thai": "giao",
            "tho": "tho-1",
            "giao_luc": "2026-11-09 21:55:00",
            "so_lan_giao": 1,
            "commit": None,
            "nhanh": None,
            "nhat_ky": None,
            "phut": 0,
            "token": 0,
            "nop_luc": None,
        }
    ]
    tho_bam = {
        "tho-1": kp.bam_khoa("khoa-that-1"),
        "tho-2": kp.bam_khoa("khoa-that-2"),
    }
    api_tho, frappe_mod, ghi_sql, ghi_set_value, da_commit, da_rollback = _stub_frappe(
        monkeypatch, ds_db, tho_bam
    )

    # 1. Sai khoá -> 401
    frappe_mod.local.response.clear()
    kq_401 = api_tho.nop(ma_tho="tho-1", khoa="khoa-sai", ma_phieu="PH-301", commit="abc1234")
    assert kq_401["ok"] is False
    assert frappe_mod.local.response.get("http_status_code") == 401
    assert len(ghi_set_value) == 0

    # 2. Thợ khác nộp -> 403, không sửa phiếu
    frappe_mod.local.response.clear()
    kq_403 = api_tho.nop(
        ma_tho="tho-2",
        khoa="khoa-that-2",
        ma_phieu="PH-301",
        commit="abc1234",
        nhanh="tu-dong/engine-t2",
        nhat_ky="test",
        phut=12,
        token=30000,
    )
    assert kq_403["ok"] is False
    assert frappe_mod.local.response.get("http_status_code") == 403
    assert len(ghi_set_value) == 0
    assert ds_db[0]["trang_thai"] == "giao"

    # 3. Đúng thợ nộp lần 1 -> 200, lưu phut/token/commit/nhanh/nhat_ky
    frappe_mod.local.response.clear()
    kq_200 = api_tho.nop(
        ma_tho="tho-1",
        khoa="khoa-that-1",
        ma_phieu="PH-301",
        commit="deadbeef99",
        nhanh="tu-dong/engine-t1",
        nhat_ky="4 passed in 0.04s",
        phut=19,
        token=84000,
    )
    assert kq_200["ok"] is True and kq_200["trung"] is False
    assert len(ghi_set_value) == 1
    assert da_commit["n"] == 1
    assert ds_db[0]["trang_thai"] == "nop"
    assert ds_db[0]["phut"] == 19 and ds_db[0]["token"] == 84000
    assert ds_db[0]["commit"] == "deadbeef99"

    # 4. Nộp lại cùng commit lần 2 -> 200, trung=True, không ghi thêm bản ghi
    frappe_mod.local.response.clear()
    kq_trung = api_tho.nop(
        ma_tho="tho-1",
        khoa="khoa-that-1",
        ma_phieu="PH-301",
        commit="deadbeef99",
        nhanh="tu-dong/engine-t1",
        nhat_ky="4 passed in 0.04s",
        phut=19,
        token=84000,
    )
    assert kq_trung["ok"] is True and kq_trung["trung"] is True
    assert len(ghi_set_value) == 1
    assert da_commit["n"] == 1
