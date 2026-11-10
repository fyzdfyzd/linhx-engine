"""Unit test cho ops/cham_phieu.py (O6)."""
from __future__ import annotations

from linhx_goi_ops.ops.cham_phieu import cham_phieu, la_loi_het_han_muc


def test_cham_phieu_rao_cong_claude_va_ngoai_le_het_han_muc():
    assert la_loi_het_han_muc("You've hit your daily limit")
    assert not la_loi_het_han_muc("CHUA_DAT: sai hợp đồng")

    dem = {"claude": 0}

    def claude_ngoai_le(_p):
        dem["claude"] += 1
        raise RuntimeError("You've hit your daily limit")

    p = {"name": "PH-610", "trang_thai": "nop", "so_lan_chua_dat": 1}
    kq = cham_phieu(
        p,
        chay_rao=lambda _: {"ok": True, "loi": []},
        chay_cong_kiem=lambda _: {"ok": True, "dau_ra": "3 passed"},
        goi_claude=claude_ngoai_le,
    )
    assert dem["claude"] == 1
    assert kq["loi_may"] is True
    assert kq["ket_luan"] == "LOI_MAY"
    assert kq["trang_thai"] == "nop"
    assert kq["so_lan_chua_dat"] == 1
