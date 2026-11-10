"""Lọc danh mục gói báo cáo công khai và tính số tiền đơn từ catalog.

Thuần Python, không import frappe ở đầu file; không nhận giá từ client.
"""
from __future__ import annotations


def _dang_ban(g: dict) -> bool:
    b = g.get("ban")
    if isinstance(b, str):
        return b.strip().lower() in ("1", "true", "yes")
    return bool(b)


def _chuan_gia(v):
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, float) and v.is_integer():
        return int(v)
    return v


def goi_cong_khai(ds_goi: list[dict]) -> list[dict]:
    """Chỉ trả các gói có `ban` là True với đúng 4 trường công khai `ma`, `ten`, `gia`, `mo_ta`."""
    ket_qua: list[dict] = []
    for g in ds_goi or []:
        if not isinstance(g, dict) or not _dang_ban(g):
            continue
        ket_qua.append(
            {
                "ma": g.get("ma"),
                "ten": g.get("ten"),
                "gia": _chuan_gia(g.get("gia")),
                "mo_ta": g.get("mo_ta"),
            }
        )
    return ket_qua


def so_tien_don(ma_goi: str, ds_goi: list[dict]) -> int | None:
    """Lấy giá theo catalog của gói đang bán; gói ngừng bán hoặc không tồn tại trả None."""
    if not ma_goi or not isinstance(ma_goi, str):
        return None
    for g in ds_goi or []:
        if not isinstance(g, dict) or not _dang_ban(g):
            continue
        if g.get("ma") == ma_goi or g.get("name") == ma_goi:
            gia = _chuan_gia(g.get("gia"))
            if isinstance(gia, int) and not isinstance(gia, bool) and gia > 0:
                return gia
            return None
    return None
