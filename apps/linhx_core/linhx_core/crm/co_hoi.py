"""Quản lý Cơ hội (LX Co Hoi): tính hạn giao 1 giờ, chia việc phụ trách, liệt kê việc chờ.

Tham khảo luồng CRM từ: nguon/03-opc-os/modules/04_quan_ly_user/module.py
"""
from __future__ import annotations

from datetime import datetime, timedelta
import logging

DINH_DANG_TG = "%Y-%m-%d %H:%M:%S"
TRANG_THAI_DONG = {"thang", "thua"}

logger = logging.getLogger(__name__)


def bay_gio() -> str:
    """Trả thời điểm hiện tại theo giờ hệ thống dạng 'YYYY-MM-DD HH:MM:SS'."""
    return datetime.now().replace(microsecond=0).strftime(DINH_DANG_TG)


def _parse_tg(gia_tri: object) -> datetime:
    if isinstance(gia_tri, datetime):
        if gia_tri.tzinfo is not None:
            gia_tri = gia_tri.astimezone().replace(tzinfo=None)
        return gia_tri.replace(microsecond=0)
    chu = str(gia_tri or "").strip()
    if "." in chu:
        chu = chu.split(".", 1)[0]
    if "T" in chu:
        chu = chu.replace("T", " ")
    if "+" in chu:
        chu = chu.split("+", 1)[0].strip()
    if chu.endswith("Z"):
        chu = chu[:-1].strip()
    return datetime.strptime(chu, DINH_DANG_TG)


def han_giao(tao_luc: str | datetime) -> str:
    """Trả thời điểm hạn giao = tao_luc + 1 giờ (chuỗi 'YYYY-MM-DD HH:MM:SS')."""
    dt = _parse_tg(tao_luc) + timedelta(hours=1)
    return dt.strftime(DINH_DANG_TG)


def giao(co_hoi: dict, ds_phu_trach: list[str], ds_co_hoi_mo: list[dict]) -> str:
    """Chọn người đang giữ ít cơ hội mở nhất; nếu bằng nhau chọn theo thứ tự trong ds_phu_trach."""
    ung_vien = [str(u).strip() for u in (ds_phu_trach or []) if str(u or "").strip()]
    if not ung_vien:
        if isinstance(co_hoi, dict) and co_hoi.get("phu_trach"):
            return str(co_hoi["phu_trach"])
        return ""
    dem: dict[str, int] = {u: 0 for u in ung_vien}
    for ch in ds_co_hoi_mo or []:
        if not isinstance(ch, dict):
            continue
        if ch.get("trang_thai") in TRANG_THAI_DONG:
            continue
        pt = str(ch.get("phu_trach") or "").strip()
        if pt in dem:
            dem[pt] += 1
    return min(ung_vien, key=lambda u: dem[u])


def viec_cho(ds_co_hoi: list[dict], luc: str | datetime) -> list[dict]:
    """Lọc các cơ hội chưa có người phụ trách, xếp han_giao tăng dần, gắn cờ qua_han (bool)."""
    moc = _parse_tg(luc)
    ket_qua: list[tuple[tuple[int, str], dict]] = []
    for ch in ds_co_hoi or []:
        if not isinstance(ch, dict):
            continue
        if ch.get("trang_thai") in TRANG_THAI_DONG:
            continue
        pt = str(ch.get("phu_trach") or "").strip()
        if pt:
            continue
        ban = dict(ch)
        hg = str(ban.get("han_giao") or "").strip()
        if not hg:
            ban["qua_han"] = False
            khoa_xep = (1, "")
        else:
            try:
                dt_hg = _parse_tg(hg)
                ban["qua_han"] = dt_hg < moc
                khoa_xep = (0, dt_hg.strftime(DINH_DANG_TG))
            except ValueError:
                logger.warning("LX Co Hoi %s có han_giao sai định dạng: %r", ban.get("name"), hg)
                ban["qua_han"] = True
                khoa_xep = (0, "")
        ket_qua.append((khoa_xep, ban))
    ket_qua.sort(key=lambda item: item[0])
    return [ban for _, ban in ket_qua]
