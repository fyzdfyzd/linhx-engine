"""Bảng phễu 6 tầng bản 1 (biết, mồi, liên hệ, cơ hội/đơn, khách, quay lại) đếm từ crm + pay."""
from __future__ import annotations

from collections import Counter

TANG = ("biet", "moi", "lien_he", "co_hoi_don", "khach", "quay_lai")


def dem(nguoi: list, co_hoi: list, don: list, luot_xem: int = 0) -> dict[str, int]:
    """Đếm số lượng từng tầng trong phễu 6 tầng bản 1."""
    ds_nguoi = [n for n in (nguoi or []) if isinstance(n, dict)]
    ds_co_hoi = [c for c in (co_hoi or []) if isinstance(c, dict)]
    ds_don = [d for d in (don or []) if isinstance(d, dict)]

    tap_nguoi = {n.get("name") for n in ds_nguoi if n.get("name")}

    def _hop_le(ma: object) -> bool:
        if not ma or not isinstance(ma, str):
            return False
        return (not tap_nguoi) or (ma in tap_nguoi)

    co_co_hoi_hoac_don: set[str] = set()
    for c in ds_co_hoi:
        ma = c.get("nguoi")
        if _hop_le(ma):
            co_co_hoi_hoac_don.add(ma)

    dem_da_tra: Counter[str] = Counter()
    for d in ds_don:
        ma = d.get("nguoi")
        if _hop_le(ma):
            co_co_hoi_hoac_don.add(ma)
            if d.get("trang_thai") == "da_tra":
                dem_da_tra[ma] += 1

    return {
        "biet": int(luot_xem or 0),
        "moi": sum(1 for n in ds_nguoi if n.get("nguon") == "T1"),
        "lien_he": len(ds_nguoi),
        "co_hoi_don": len(co_co_hoi_hoac_don),
        "khach": sum(1 for so_don in dem_da_tra.values() if so_don >= 1),
        "quay_lai": sum(1 for so_don in dem_da_tra.values() if so_don >= 2),
    }
