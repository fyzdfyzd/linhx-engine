"""Tổng hợp bàn điều hành (/engine): việc chờ duyệt, lead mới, đơn mới."""
from __future__ import annotations

from datetime import datetime, timedelta

DINH_DANG_TG = "%Y-%m-%d %H:%M:%S"


def _parse_tg(gia_tri: object) -> datetime:
    if isinstance(gia_tri, datetime):
        if gia_tri.tzinfo is not None:
            gia_tri = gia_tri.astimezone().replace(tzinfo=None)
        return gia_tri.replace(microsecond=0)
    chu = str(gia_tri or "").strip()
    if not chu:
        raise ValueError("Thời gian trống")
    try:
        dt = datetime.fromisoformat(chu.replace("Z", "+00:00"))
        if dt.tzinfo is not None:
            dt = dt.astimezone().replace(tzinfo=None)
        return dt.replace(microsecond=0)
    except ValueError:
        pass
    if "." in chu:
        chu = chu.split(".", 1)[0]
    if "T" in chu:
        chu = chu.replace("T", " ")
    return datetime.strptime(chu, DINH_DANG_TG)


def _loc_moi_trong_gio(ds: list, moc: datetime, dt_luc: datetime) -> list[dict]:
    kq: list[tuple[datetime, dict]] = []
    for item in ds or []:
        if not isinstance(item, dict):
            continue
        try:
            dt = _parse_tg(item.get("creation"))
        except ValueError:
            continue
        if moc <= dt <= dt_luc:
            kq.append((dt, dict(item)))
    kq.sort(key=lambda x: x[0], reverse=True)
    return [ban for _, ban in kq]


def tong_hop(jobs: list, nguoi: list, don: list, luc: str, gio: int | float = 24) -> dict:
    """Tổng hợp việc chờ duyệt (cho_duyet), lead mới và đơn mới trong `gio` giờ trước `luc`."""
    dt_luc = _parse_tg(luc)
    moc = dt_luc - timedelta(hours=float(gio))

    viec_cho_raw: list[tuple[tuple[int, datetime], dict]] = []
    for j in jobs or []:
        if not isinstance(j, dict):
            continue
        if j.get("trang_thai") != "cho_duyet":
            continue
        try:
            dt = _parse_tg(j.get("creation"))
            khoa = (1, dt)
        except ValueError:
            khoa = (0, datetime.min)
        viec_cho_raw.append((khoa, dict(j)))
    viec_cho_raw.sort(key=lambda x: x[0], reverse=True)

    return {
        "viec_cho": [ban for _, ban in viec_cho_raw],
        "lead_moi": _loc_moi_trong_gio(nguoi, moc, dt_luc),
        "don_moi": _loc_moi_trong_gio(don, moc, dt_luc),
    }
