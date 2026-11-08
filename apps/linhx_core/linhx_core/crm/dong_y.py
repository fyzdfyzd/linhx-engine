"""Quản lý đồng ý dữ liệu cá nhân (LX Dong Y) theo mục đích, rút đồng ý và sổ nhật ký bất biến.

Tham khảo luồng tuân thủ NĐ 13/2023 và CRM từ:
- nguon/03-opc-os/modules/09_tuan_thu/module.py
- nguon/03-opc-os/modules/04_quan_ly_user/module.py
"""
from __future__ import annotations

import copy
from datetime import datetime

MUC_DICH = ("lien_he", "chuyen_cheo", "marketing")
DINH_DANG_TG = "%Y-%m-%d %H:%M:%S"


class TuChoi(Exception):
    """Ngoại lệ khi người dùng chưa đồng ý hoặc đã rút đồng ý cho mục đích yêu cầu."""


def bay_gio() -> str:
    """Trả thời điểm hiện tại theo giờ hệ thống dạng 'YYYY-MM-DD HH:MM:SS'."""
    return datetime.now().replace(microsecond=0).strftime(DINH_DANG_TG)


def _parse_tg(gia_tri: object) -> datetime:
    if isinstance(gia_tri, datetime):
        if gia_tri.tzinfo is not None:
            gia_tri = gia_tri.astimezone().replace(tzinfo=None)
        return gia_tri
    chu = str(gia_tri or "").strip()
    if not chu:
        raise ValueError("Thời điểm trống")
    try:
        dt = datetime.fromisoformat(chu.replace("Z", "+00:00"))
        if dt.tzinfo is not None:
            dt = dt.astimezone().replace(tzinfo=None)
        return dt
    except ValueError:
        pass
    if "." in chu:
        chu = chu.split(".", 1)[0]
    if "T" in chu:
        chu = chu.replace("T", " ")
    return datetime.strptime(chu, DINH_DANG_TG)


def _khoa_luc(gia_tri: object) -> tuple[int, object]:
    try:
        dt = _parse_tg(gia_tri)
        return (1, (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond))
    except ValueError:
        return (0, str(gia_tri or "").strip())


def _ma_nguoi(nguoi: object) -> str:
    if isinstance(nguoi, dict):
        return str(nguoi.get("name") or nguoi.get("nguoi") or "").strip()
    return str(nguoi or "").strip()


def _chuan_dong_y(gia_tri: object) -> bool:
    if isinstance(gia_tri, bool):
        return gia_tri
    if isinstance(gia_tri, (int, float)):
        return bool(gia_tri)
    if isinstance(gia_tri, str):
        s = gia_tri.strip().lower()
        if s in ("0", "false", "no", "off", ""):
            return False
        if s in ("1", "true", "yes", "on"):
            return True
    return bool(gia_tri)


def ghi(
    so: list[dict],
    nguoi: str | dict,
    muc_dich: str,
    dong_y: bool,
    luc: str | datetime,
    nguon: str,
) -> list[dict]:
    """Trả sổ mới = sổ cũ + 1 dòng nhật ký đồng ý; không sửa sổ cũ; muc_dich lạ -> ValueError."""
    if not isinstance(muc_dich, str) or muc_dich not in MUC_DICH:
        raise ValueError(f"Mục đích đồng ý không hợp lệ: {muc_dich!r}")
    ma = _ma_nguoi(nguoi)
    if not ma:
        raise ValueError("Thiếu mã người đồng ý")
    if isinstance(luc, datetime):
        luc_str = _parse_tg(luc).replace(microsecond=0).strftime(DINH_DANG_TG)
    else:
        luc_str = str(luc or "").strip()
    if not luc_str:
        raise ValueError("Thiếu thời điểm ghi đồng ý")

    so_moi = [copy.deepcopy(d) if isinstance(d, dict) else d for d in (so or [])]
    so_moi.append(
        {
            "nguoi": ma,
            "muc_dich": muc_dich,
            "dong_y": _chuan_dong_y(dong_y),
            "luc": luc_str,
            "nguon": str(nguon or "").strip(),
        }
    )
    return so_moi


def hieu_luc(so: list[dict], nguoi: str | dict, muc_dich: str) -> bool:
    """Trả trạng thái đồng ý theo dòng có luc mới nhất của người + mục đích; không có -> False."""
    if not isinstance(muc_dich, str) or muc_dich not in MUC_DICH:
        return False
    ma = _ma_nguoi(nguoi)
    if not ma or not so:
        return False

    ung_vien: list[tuple[tuple[int, object], int, dict]] = []
    for idx, dong in enumerate(so):
        if not isinstance(dong, dict):
            continue
        if _ma_nguoi(dong.get("nguoi")) != ma:
            continue
        if dong.get("muc_dich") != muc_dich:
            continue
        ung_vien.append((_khoa_luc(dong.get("luc")), idx, dong))

    if not ung_vien:
        return False

    _, _, dong_moi_nhat = max(ung_vien, key=lambda item: (item[0], item[1]))
    return _chuan_dong_y(dong_moi_nhat.get("dong_y"))


def kiem_chuyen_cheo(so: list[dict], nguoi: str | dict) -> None:
    """Ném TuChoi khi người dùng không còn đồng ý mục đích chuyen_cheo."""
    if not hieu_luc(so, nguoi, "chuyen_cheo"):
        raise TuChoi(f"Người {_ma_nguoi(nguoi)!r} không có đồng ý chuyển chéo đang hiệu lực")
