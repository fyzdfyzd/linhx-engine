"""Kiểm thử đơn vị cho gói `linhx_goi_chiemtinh` (K2a)."""
from __future__ import annotations

import pytest

from linhx_goi_chiemtinh import giao

MAU = {"ma_don": "ord_1", "so_tien": 99000, "goi": "natal", "trang_thai": "da_tra"}


def test_so_khop_khong_lech_va_chi_ra_truong_lech_theo_thu_tu():
    assert giao.so_khop(MAU, dict(MAU)) == []
    assert giao.so_khop(MAU, {**MAU, "so_tien": 199000}) == ["so_tien"]
    assert giao.so_khop(MAU, {**MAU, "goi": "transit", "trang_thai": "cho_tra"}) == ["goi", "trang_thai"]
    assert giao.so_khop(MAU, {**MAU, "ma_don": "ord_2", "so_tien": 1}) == ["ma_don", "so_tien"]


def test_so_khop_truong_thieu_la_lech_khong_lap_bang_gia():
    thieu = {k: v for k, v in MAU.items() if k != "so_tien"}
    assert giao.so_khop(MAU, {**thieu, "gia": 99000}) == ["so_tien"]
    assert giao.so_khop({**thieu, "gia": 99000}, MAU) == ["so_tien"]
    assert giao.so_khop(MAU, {**MAU, "so_tien": None}) == ["so_tien"]
    assert giao.so_khop(thieu, dict(thieu)) == ["so_tien"]


def test_giao_mac_dinh_tat_cts_that_chi_ghi_doi_chieu():
    kho: list[dict] = []
    da_goi: list[tuple] = []
    kq = giao.giao(
        dict(MAU),
        {"ma": "natal", "gia": 99000, "gia_san": 99000},
        don_cts=dict(MAU),
        goi_api=lambda u, p, h: da_goi.append((u, p, h)) or {"ok": True},
        kho_doi_chieu=kho,
    )
    assert kq["ok"] is True
    assert kq["lech"] == []
    assert kq["co_cts_that"] is False
    assert kq["da_giao_khach"] is False
    assert da_goi == []
    assert len(kho) == 1


def test_giao_bat_cts_that_goi_api_tu_cau_hinh_va_chan_khi_lech():
    da_goi: list[tuple] = []
    kq = giao.giao(
        dict(MAU),
        {"ma": "natal", "gia": 99000, "gia_san": 99000},
        cau_hinh={
            "cts_that": True,
            "cts_bao_cao_url": "https://cts.internal.local/v1/reports/deliver",
            "cts_api_khoa": "khoa_test_bao_cao",
        },
        don_cts=dict(MAU),
        goi_api=lambda u, p, h: da_goi.append((u, p, h)) or {"ok": True, "delivered": True},
    )
    assert kq["ok"] is True
    assert kq["co_cts_that"] is True
    assert kq["da_giao_khach"] is True
    assert len(da_goi) == 1
    assert da_goi[0][0] == "https://cts.internal.local/v1/reports/deliver"

    with pytest.raises(ValueError):
        giao.giao(
            dict(MAU),
            {"ma": "natal", "gia": 99000, "gia_san": 99000},
            cau_hinh={
                "cts_that": True,
                "cts_bao_cao_url": "https://cts.internal.local/v1/reports/deliver",
                "cts_api_khoa": "khoa_test_bao_cao",
            },
            don_cts={**MAU, "so_tien": 199000},
            goi_api=lambda u, p, h: {"ok": True},
        )
