"""Kiểm thử đơn vị cho pilot của gói Agent Force."""
from __future__ import annotations

import copy
import pytest

from linhx_goi_agentforce.agent import pilot


def test_tao_pilot_kiem_tra_dau_vao_va_7_buoc():
    with pytest.raises(ValueError):
        pilot.tao_pilot("", "2026-11-01 09:00:00")
    with pytest.raises(ValueError):
        pilot.tao_pilot(True, "2026-11-01 09:00:00")
    with pytest.raises(ValueError):
        pilot.tao_pilot("CH-01", "khong-phai-ngay")

    p = pilot.tao_pilot("  CH-01  ", "2026-11-01T09:30:00", phu_trach=" sale@vd.vn ")
    assert p["co_hoi"] == "CH-01"
    assert p["phu_trach"] == "sale@vd.vn"
    assert p["bat_dau_luc"] == "2026-11-01 09:30:00"
    assert p["han_hoan_thanh"] == "2026-11-15 09:30:00"
    assert p["trang_thai"] == "dang_chay"
    assert len(p["cac_buoc"]) == pilot.SO_BUOC == 7
    assert [b["so"] for b in p["cac_buoc"]] == [1, 2, 3, 4, 5, 6, 7]
    assert all(b["trang_thai"] == "chua_lam" and b["xong_luc"] is None for b in p["cac_buoc"])


def test_hoan_thanh_buoc_khong_sua_dict_dau_vao_va_chan_bien():
    p_goc = pilot.tao_pilot("CH-02", "2026-11-01 08:00:00")
    ban_sao = copy.deepcopy(p_goc)

    for so_sai in (0, -1, 8, True, False, "1"):
        with pytest.raises(ValueError):
            pilot.hoan_thanh_buoc(p_goc, so_sai, "2026-11-01 10:00:00")

    with pytest.raises(ValueError):
        pilot.hoan_thanh_buoc(p_goc, 2, "2026-11-01 10:00:00")

    assert p_goc == ban_sao

    p1 = pilot.hoan_thanh_buoc(p_goc, 1, "2026-11-01 10:00:00")
    assert p_goc["cac_buoc"][0]["trang_thai"] == "chua_lam"
    assert p1["cac_buoc"][0]["trang_thai"] == "xong"
    assert p1["cac_buoc"][0]["xong_luc"] == "2026-11-01 10:00:00"
    assert p1["trang_thai"] == "dang_chay"

    p_huy = copy.deepcopy(p1)
    p_huy["trang_thai"] = "huy"
    with pytest.raises(ValueError):
        pilot.hoan_thanh_buoc(p_huy, 2, "2026-11-02 10:00:00")

    p_xong = copy.deepcopy(p1)
    for s in range(2, 8):
        p_xong = pilot.hoan_thanh_buoc(p_xong, s, f"2026-11-0{s} 10:00:00")
    assert p_xong["trang_thai"] == "xong"
    p_xong_huy = copy.deepcopy(p_xong)
    p_xong_huy["trang_thai"] = "huy"
    with pytest.raises(ValueError):
        pilot.kiem_pilot(p_xong_huy)


def test_viec_cho_xep_thu_tu_han_hoan_thanh_tang_dan():
    p_muon_hon = pilot.tao_pilot("CH-MUON", "2026-11-02 09:00:00", phu_trach="s1@vd.vn")
    p_som_hon = pilot.tao_pilot("CH-SOM", "2026-11-01 08:00:00", phu_trach="s2@vd.vn")
    p_dung_han = pilot.tao_pilot("CH-BIEN", "2026-11-03 12:00:00", phu_trach="s1@vd.vn")
    p_huy = pilot.tao_pilot("CH-HUY", "2026-10-15 08:00:00", phu_trach="s1@vd.vn")
    p_huy["trang_thai"] = "huy"

    ds = [p_muon_hon, p_som_hon, p_dung_han, p_huy]
    vc = pilot.viec_cho(ds, "2026-11-17 12:00:00")
    assert [x["co_hoi"] for x in vc] == ["CH-SOM", "CH-MUON"]
    assert all(x["qua_han"] is True for x in vc)
    assert "qua_han" not in p_som_hon
