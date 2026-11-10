"""Logic thuần Python cho bàn duyệt phiếu Agy (/engine): liệt kê phiếu chờ, duyệt phiếu, trả phiếu có lý do."""
from __future__ import annotations

from datetime import datetime

from linhx_goi_ops.ops import phieu_agy

DINH_DANG_TG = "%Y-%m-%d %H:%M:%S"


def _parse_tg(gia_tri: object) -> tuple[int, str]:
    if isinstance(gia_tri, datetime):
        if gia_tri.tzinfo is not None:
            gia_tri = gia_tri.astimezone().replace(tzinfo=None)
        return 1, gia_tri.strftime("%Y-%m-%d %H:%M:%S.%f")
    chu = str(gia_tri or "").strip()
    if not chu:
        return 0, ""
    try:
        dt = datetime.fromisoformat(chu.replace("Z", "+00:00"))
        if dt.tzinfo is not None:
            dt = dt.astimezone().replace(tzinfo=None)
        return 1, dt.strftime("%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        pass
    return 1, chu


def _tim_phieu(ds_phieu: list[dict], ma_phieu: str) -> dict:
    if not isinstance(ds_phieu, list):
        raise ValueError("Danh sách phiếu phải là list")
    ma = str(ma_phieu or "").strip()
    if not ma:
        raise ValueError("Mã phiếu không được để trống")
    for p in ds_phieu:
        if isinstance(p, dict) and (p.get("name") == ma or p.get("ma_phieu") == ma):
            return p
    raise ValueError(f"Không tìm thấy phiếu: {ma!r}")


def ds_phieu_cho(ds_phieu: list[dict]) -> list[dict]:
    """Chỉ lấy phiếu có trang_thai == 'nhap', xếp mới nhất trước."""
    if not isinstance(ds_phieu, list):
        return []
    ung_vien: list[tuple[tuple[int, str, int], dict]] = []
    for idx, p in enumerate(ds_phieu):
        if not isinstance(p, dict):
            continue
        if p.get("trang_thai") != "nhap":
            continue
        co_tg, moc_tg = _parse_tg(p.get("creation"))
        ung_vien.append(((co_tg, moc_tg, idx), dict(p)))
    ung_vien.sort(key=lambda x: x[0], reverse=True)
    return [ban_ghi for _, ban_ghi in ung_vien]


def duyet_phieu(ds_phieu: list[dict], ma_phieu: str, vai_tro: list[str]) -> dict:
    """Chuyển phiếu ma_phieu từ 'nhap' sang 'duyet' (chỉ vai điều hành System Manager / LX Operator)."""
    phieu = _tim_phieu(ds_phieu, ma_phieu)
    if phieu.get("trang_thai") != "nhap":
        raise ValueError(f"Chỉ duyệt được phiếu ở trạng thái 'nhap' (hiện tại: {phieu.get('trang_thai')!r})")
    cap_nhat = phieu_agy.chuyen_trang_thai(phieu, "duyet", vai_tro=vai_tro)
    phieu.update(cap_nhat)
    return phieu


def tra_phieu(ds_phieu: list[dict], ma_phieu: str, ly_do: str, vai_tro: list[str]) -> dict:
    """Trả lại phiếu từ 'nhap' sang 'tra', bắt buộc có lý do và chỉ vai điều hành được thực hiện."""
    if not isinstance(ly_do, str) or not ly_do.strip():
        raise ValueError("Lý do trả phiếu không được để trống")
    ly_do_sach = ly_do.strip()
    phieu = _tim_phieu(ds_phieu, ma_phieu)
    if phieu.get("trang_thai") != "nhap":
        raise ValueError(f"Chỉ trả lại được phiếu chờ duyệt ở trạng thái 'nhap' (hiện tại: {phieu.get('trang_thai')!r})")
    cap_nhat = phieu_agy.chuyen_trang_thai(phieu, "tra", vai_tro=vai_tro, ly_do_tra=ly_do_sach)
    phieu.update(cap_nhat)
    return phieu
