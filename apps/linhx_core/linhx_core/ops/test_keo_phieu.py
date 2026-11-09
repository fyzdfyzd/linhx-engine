"""Kiểm thử đơn vị cho keo_phieu.py và api_tho.keo."""
from __future__ import annotations

import datetime
import sys
import types

from linhx_core.ops import keo_phieu as kp


def _stub_frappe(monkeypatch, ds_db: list[dict], tho_khoa_bam: dict):
    frappe_mod = types.ModuleType("frappe")
    utils_mod = types.ModuleType("frappe.utils")
    utils_mod.now_datetime = lambda: datetime.datetime(2026, 11, 9, 12, 35, 0)

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

    def _sql(query, *a, **kw):
        ghi_sql.append(query)
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
    sys.modules.pop("linhx_core.ops.api_tho", None)
    from linhx_core.ops import api_tho

    return api_tho, frappe_mod, ghi_sql, ghi_set_value, da_commit


def test_api_tho_keo_sai_khoa_va_dung_khoa_thu_hoi_qua_han(monkeypatch):
    ds_db = [
        {
            "name": "PH-QUA-HAN",
            "loai_phieu": "feature",
            "de": "Phiếu giao lúc 09:50 đã quá 150 phút",
            "vung": "apps/linhx_core/linhx_core/ops/**",
            "trang_thai": "giao",
            "tho": "tho-cu",
            "giao_luc": "2026-11-09 09:50:00",
            "so_lan_giao": 1,
        }
    ]
    tho_bam = {"tho-1": kp.bam_khoa("khoa-that-may-1")}
    api_tho, frappe_mod, ghi_sql, ghi_set_value, da_commit = _stub_frappe(monkeypatch, ds_db, tho_bam)

    # Sai khoá -> 401, không chạy truy vấn DB
    kq_sai = api_tho.keo(ma_tho="tho-1", khoa="khoa-sai")
    assert kq_sai["ok"] is False
    assert frappe_mod.local.response.get("http_status_code") == 401
    assert len(ghi_sql) == 0

    # Đúng khoá -> FOR UPDATE, thu hồi phiếu quá hạn (so_lan_giao: 1 -> 2) rồi giao cho tho-1
    frappe_mod.local.response.clear()
    kq_dung = api_tho.keo(ma_tho="tho-1", khoa="khoa-that-may-1")
    assert kq_dung["ok"] is True
    assert kq_dung["phieu"]["name"] == "PH-QUA-HAN"
    assert kq_dung["phieu"]["trang_thai"] == "giao"
    assert kq_dung["phieu"]["tho"] == "tho-1"
    assert kq_dung["phieu"]["so_lan_giao"] == 2
    assert any("FOR UPDATE" in q.upper() for q in ghi_sql)
    assert len(ghi_set_value) == 1
    assert da_commit["n"] == 1
