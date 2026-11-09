"""Logic thuần Python đặt lịch gọi tư vấn (F2): kiểm giờ làm 8–18h giờ VN, chặn trùng giờ cùng người phụ trách, liệt kê việc chờ."""
from __future__ import annotations

import copy
from datetime import datetime, timedelta, timezone
import re

GIO_BAT_DAU = 8
GIO_KET_THUC = 18
PHUT_MAC_DINH = 30
PHUT_TOI_DA = (GIO_KET_THUC - GIO_BAT_DAU) * 60
DINH_DANG_TG = "%Y-%m-%d %H:%M:%S"
DINH_DANG_TG_PHUT = "%Y-%m-%d %H:%M"
TRANG_THAI_LICH = ("cho_goi", "da_goi", "huy")
MUI_GIO_VN = timezone(timedelta(hours=7))

_MAU_NGAY_CHI_CO_NGAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def bay_gio() -> str:
    """Trả thời điểm hiện tại theo giờ Việt Nam (UTC+7) dạng 'YYYY-MM-DD HH:MM:SS'."""
    return datetime.now(MUI_GIO_VN).replace(tzinfo=None, microsecond=0).strftime(DINH_DANG_TG)


def _parse_tg_vn(gia_tri: object) -> datetime:
    """Phân tích thời điểm về datetime (naive) theo múi giờ Việt Nam (UTC+7)."""
    if isinstance(gia_tri, bool) or gia_tri is None:
        raise ValueError("Thời gian không hợp lệ")
    if isinstance(gia_tri, datetime):
        if type(gia_tri) is not datetime:
            raise ValueError("Thời gian phải có đầy đủ ngày và giờ")
        dt = gia_tri
        if dt.tzinfo is not None:
            dt = dt.astimezone(MUI_GIO_VN).replace(tzinfo=None)
        return dt.replace(microsecond=0)
    if not isinstance(gia_tri, str):
        raise ValueError("Thời gian phải là chuỗi hoặc datetime")

    chu = gia_tri.strip()
    if not chu:
        raise ValueError("Thời gian không được để trống")
    if _MAU_NGAY_CHI_CO_NGAY.match(chu):
        raise ValueError("Thời gian đặt lịch phải có giờ và phút")

    try:
        dt = datetime.fromisoformat(chu.replace("Z", "+00:00"))
        if dt.tzinfo is not None:
            dt = dt.astimezone(MUI_GIO_VN).replace(tzinfo=None)
        return dt.replace(microsecond=0)
    except ValueError:
        pass

    if "." in chu:
        chu = chu.split(".", 1)[0]
    if "T" in chu:
        chu = chu.replace("T", " ")

    for fmt in (DINH_DANG_TG, DINH_DANG_TG_PHUT):
        try:
            return datetime.strptime(chu, fmt)
        except ValueError:
            continue
    raise ValueError(f"Định dạng thời gian không hợp lệ: {gia_tri!r}")


def chuan_hoa_tg(gia_tri: object) -> str:
    """Chuẩn hoá thời điểm về chuỗi 'YYYY-MM-DD HH:MM:SS' theo giờ VN."""
    return _parse_tg_vn(gia_tri).strftime(DINH_DANG_TG)


def _chuan_phut(gia_tri: object) -> int:
    """Kiểm tra và chuẩn hoá thời lượng cuộc gọi (phút nguyên dương trong khung giờ làm)."""
    if gia_tri is None or (isinstance(gia_tri, str) and not gia_tri.strip()):
        return PHUT_MAC_DINH
    if isinstance(gia_tri, bool):
        raise ValueError("Số phút không hợp lệ")
    if isinstance(gia_tri, int):
        phut = gia_tri
    elif isinstance(gia_tri, str) and gia_tri.strip().isdigit():
        phut = int(gia_tri.strip())
    else:
        raise ValueError("Số phút phải là số nguyên dương")

    if phut <= 0 or phut > PHUT_TOI_DA:
        raise ValueError(f"Số phút phải nằm trong khoảng 1..{PHUT_TOI_DA}")
    return phut


def kiem_gio_lam_viec(
    bat_dau: object,
    phut: object = PHUT_MAC_DINH,
) -> tuple[datetime, datetime, int]:
    """Kiểm tra khoảng [bat_dau, bat_dau + phut] nằm trọn trong khung 08:00:00 – 18:00:00 giờ VN."""
    phut_int = _chuan_phut(phut)
    dt_bd = _parse_tg_vn(bat_dau)
    dt_kt = dt_bd + timedelta(minutes=phut_int)

    if dt_bd.date() != dt_kt.date():
        raise ValueError("Lịch gọi không được kéo dài qua ngày hôm sau")

    moc_bat_dau_ngay = dt_bd.replace(hour=GIO_BAT_DAU, minute=0, second=0, microsecond=0)
    moc_ket_thuc_ngay = dt_bd.replace(hour=GIO_KET_THUC, minute=0, second=0, microsecond=0)

    if dt_bd < moc_bat_dau_ngay or dt_bd >= moc_ket_thuc_ngay or dt_kt > moc_ket_thuc_ngay:
        raise ValueError(
            f"Lịch gọi phải nằm trong giờ làm việc ({GIO_BAT_DAU:02d}:00 đến {GIO_KET_THUC:02d}:00 giờ VN)"
        )
    return dt_bd, dt_kt, phut_int


def _khoang_tg_lich(lich: dict) -> tuple[datetime, datetime]:
    dt_bd = _parse_tg_vn(lich.get("bat_dau"))
    kt_raw = lich.get("ket_thuc")
    if kt_raw is not None and str(kt_raw).strip():
        dt_kt = _parse_tg_vn(kt_raw)
        if dt_kt <= dt_bd:
            phut_cu = _chuan_phut(lich.get("phut", PHUT_MAC_DINH))
            dt_kt = dt_bd + timedelta(minutes=phut_cu)
    else:
        phut_cu = _chuan_phut(lich.get("phut", PHUT_MAC_DINH))
        dt_kt = dt_bd + timedelta(minutes=phut_cu)
    return dt_bd, dt_kt


def kiem_trung_gio(
    ds_lich: list[dict] | tuple[dict, ...],
    phu_trach: str,
    dt_bd: datetime,
    dt_kt: datetime,
    *,
    bo_qua_name: str | None = None,
) -> None:
    """Kiểm tra khoảng [dt_bd, dt_kt) không giao với bất kỳ lịch chưa huỷ nào của cùng phu_trach."""
    pt_chuan = str(phu_trach or "").strip()
    if not pt_chuan:
        raise ValueError("Người phụ trách không được để trống")
    ten_bo_qua = str(bo_qua_name or "").strip()

    for idx, lich in enumerate(ds_lich or []):
        if not isinstance(lich, dict):
            raise ValueError(f"Bản ghi lịch tại vị trí {idx} không hợp lệ")
        if ten_bo_qua and str(lich.get("name") or "").strip() == ten_bo_qua:
            continue
        trang_thai = str(lich.get("trang_thai") or "cho_goi").strip()
        if trang_thai == "huy":
            continue
        pt_cu = str(lich.get("phu_trach") or "").strip()
        if pt_cu != pt_chuan:
            continue

        cu_bd, cu_kt = _khoang_tg_lich(lich)
        if dt_bd < cu_kt and cu_bd < dt_kt:
            raise ValueError(
                f"Người phụ trách {pt_chuan} đã có lịch gọi trùng giờ "
                f"({cu_bd.strftime(DINH_DANG_TG)} - {cu_kt.strftime(DINH_DANG_TG)})"
            )


def dat_lich(ds_lich: list[dict], du_lieu: dict) -> list[dict]:
    """Đặt lịch gọi mới vào danh sách lịch sau khi kiểm giờ làm việc (8–18h VN) và kiểm trùng giờ."""
    if not isinstance(ds_lich, (list, tuple)):
        raise ValueError("ds_lich phải là danh sách")
    if not isinstance(du_lieu, dict):
        raise ValueError("du_lieu phải là dict")

    nguoi = du_lieu.get("nguoi")
    if isinstance(nguoi, bool) or not isinstance(nguoi, str) or not nguoi.strip():
        raise ValueError("Thiếu mã khách hàng / người đặt lịch (nguoi)")
    nguoi_chuan = nguoi.strip()

    phu_trach = du_lieu.get("phu_trach")
    if isinstance(phu_trach, bool) or not isinstance(phu_trach, str) or not phu_trach.strip():
        raise ValueError("Thiếu người phụ trách (phu_trach)")
    phu_trach_chuan = phu_trach.strip()

    ghi_chu_raw = du_lieu.get("ghi_chu")
    if isinstance(ghi_chu_raw, bool) or (ghi_chu_raw is not None and not isinstance(ghi_chu_raw, str)):
        raise ValueError("Ghi chú không hợp lệ")
    ghi_chu_chuan = (ghi_chu_raw or "").strip()

    trang_thai_raw = du_lieu.get("trang_thai")
    if trang_thai_raw is not None:
        if isinstance(trang_thai_raw, bool) or not isinstance(trang_thai_raw, str) or trang_thai_raw not in TRANG_THAI_LICH:
            raise ValueError(f"Trạng thái lịch không hợp lệ: {trang_thai_raw!r}")
        trang_thai = trang_thai_raw
    else:
        trang_thai = "cho_goi"

    dt_bd, dt_kt, phut_int = kiem_gio_lam_viec(
        du_lieu.get("bat_dau"),
        du_lieu.get("phut", PHUT_MAC_DINH),
    )
    kiem_trung_gio(ds_lich, phu_trach_chuan, dt_bd, dt_kt)

    ban_ghi_moi: dict[str, object] = {
        "nguoi": nguoi_chuan,
        "phu_trach": phu_trach_chuan,
        "bat_dau": dt_bd.strftime(DINH_DANG_TG),
        "ket_thuc": dt_kt.strftime(DINH_DANG_TG),
        "phut": phut_int,
        "trang_thai": trang_thai,
    }
    if "ghi_chu" in du_lieu or ghi_chu_chuan:
        ban_ghi_moi["ghi_chu"] = ghi_chu_chuan
    if du_lieu.get("co_hoi") and isinstance(du_lieu.get("co_hoi"), str) and du_lieu["co_hoi"].strip():
        ban_ghi_moi["co_hoi"] = du_lieu["co_hoi"].strip()
    if du_lieu.get("don_vi") and isinstance(du_lieu.get("don_vi"), str) and du_lieu["don_vi"].strip():
        ban_ghi_moi["don_vi"] = du_lieu["don_vi"].strip()

    ket_qua = [copy.deepcopy(x) for x in ds_lich]
    ket_qua.append(ban_ghi_moi)
    return ket_qua


def viec_cho(ds_lich: list[dict], phu_trach: str | None = None) -> list[dict]:
    """Lọc các lịch có trang_thai == 'cho_goi' (và đúng phu_trach nếu truyền vào), xếp bat_dau tăng dần."""
    if not isinstance(ds_lich, (list, tuple)):
        raise ValueError("ds_lich phải là danh sách")
    if phu_trach is not None:
        if isinstance(phu_trach, bool) or not isinstance(phu_trach, str):
            raise ValueError("phu_trach phải là chuỗi hoặc None")
        pt_loc = phu_trach.strip()
    else:
        pt_loc = None

    ket_qua: list[tuple[tuple[datetime, int], dict]] = []
    for idx, lich in enumerate(ds_lich):
        if not isinstance(lich, dict):
            continue
        if lich.get("trang_thai") != "cho_goi":
            continue
        if pt_loc is not None and str(lich.get("phu_trach") or "").strip() != pt_loc:
            continue
        try:
            dt_bd = _parse_tg_vn(lich.get("bat_dau"))
        except ValueError:
            continue
        ket_qua.append(((dt_bd, idx), copy.deepcopy(lich)))

    ket_qua.sort(key=lambda item: item[0])
    return [ban for _, ban in ket_qua]
