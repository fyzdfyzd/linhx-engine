"""Logic thuần Python cho API thợ kéo phiếu Agy: băm khoá SHA-256, xác thực hằng thời gian,
thu hồi phiếu giao quá 150 phút và khoá đồng bộ chống hai thợ nhận trùng phiếu.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
import hmac
import threading

PHUT_QUA_HAN = 150
DINH_DANG_TG = "%Y-%m-%d %H:%M:%S"

_KHOA_LUONG = threading.RLock()


def _parse_luc(gia_tri: object) -> datetime | None:
    if isinstance(gia_tri, datetime):
        if gia_tri.tzinfo is not None:
            return gia_tri.astimezone().replace(tzinfo=None)
        return gia_tri
    if not isinstance(gia_tri, str):
        return None
    chu = gia_tri.strip()
    if not chu:
        return None
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
    try:
        return datetime.strptime(chu, DINH_DANG_TG)
    except ValueError:
        return None


def bam_khoa(khoa_tran: str) -> str:
    """Trả mã băm SHA-256 dạng hex của `khoa_tran`; không bao giờ trả khoá trần."""
    if not isinstance(khoa_tran, str):
        raise TypeError("khoa_tran phải là kiểu str")
    return hashlib.sha256(khoa_tran.encode("utf-8")).hexdigest()


def dang_ky_tho(kho: dict, ma_tho: str, khoa_tran: str) -> dict:
    """Đăng ký thợ vào `kho["tho"][ma_tho]` chỉ với mã băm SHA-256, tuyệt đối không lưu khoá trần."""
    if not isinstance(kho, dict):
        raise ValueError("kho phải là kiểu dict")
    if not isinstance(ma_tho, str) or not ma_tho.strip():
        raise ValueError("ma_tho không được để trống")
    if not isinstance(khoa_tran, str) or not khoa_tran:
        raise ValueError("khoa_tran không được để trống")

    ma = ma_tho.strip()
    ban_ghi = {
        "ma_tho": ma,
        "khoa_bam": bam_khoa(khoa_tran),
    }
    with _KHOA_LUONG:
        ds_tho = kho.setdefault("tho", {})
        if not isinstance(ds_tho, dict):
            ds_tho = {}
            kho["tho"] = ds_tho
        ds_tho[ma] = ban_ghi
    return dict(ban_ghi)


def xac_thuc_tho(kho: dict, ma_tho: str, khoa_tran: str | None) -> bool:
    """Xác thực khoá thợ bằng so sánh hằng thời gian (`hmac.compare_digest`) trên mã băm SHA-256."""
    if not isinstance(kho, dict):
        return False
    if not isinstance(ma_tho, str) or not ma_tho.strip():
        return False
    if not isinstance(khoa_tran, str) or not khoa_tran:
        return False

    ds_tho = kho.get("tho")
    if not isinstance(ds_tho, dict):
        return False

    thong_tin = ds_tho.get(ma_tho.strip())
    if isinstance(thong_tin, dict):
        khoa_bam_luu = thong_tin.get("khoa_bam")
    elif isinstance(thong_tin, str):
        khoa_bam_luu = thong_tin
    else:
        return False

    if not isinstance(khoa_bam_luu, str) or not khoa_bam_luu:
        return False

    bam_gui = bam_khoa(khoa_tran)
    return hmac.compare_digest(bam_gui.encode("utf-8"), khoa_bam_luu.encode("utf-8"))


def thu_hoi_qua_han(
    ds_phieu: list[dict],
    luc: str,
    phut_qua_han: int = PHUT_QUA_HAN,
) -> list[dict]:
    """Chuyển các phiếu đang `giao` quá `phut_qua_han` phút về `duyet`, xoá `tho` và tăng `so_lan_giao`."""
    if not isinstance(ds_phieu, list):
        return []
    dt_luc = _parse_luc(luc)
    if dt_luc is None:
        raise ValueError(f"Thời điểm luc không hợp lệ: {luc!r}")

    nguong_giay = float(phut_qua_han) * 60.0
    with _KHOA_LUONG:
        for phieu in ds_phieu:
            if not isinstance(phieu, dict):
                continue
            if phieu.get("trang_thai") != "giao":
                continue
            dt_giao = _parse_luc(phieu.get("giao_luc"))
            if dt_giao is None:
                continue
            if (dt_luc - dt_giao).total_seconds() > nguong_giay:
                phieu["trang_thai"] = "duyet"
                phieu["tho"] = None
                phieu["so_lan_giao"] = int(phieu.get("so_lan_giao") or 0) + 1
    return ds_phieu


def keo_phieu(
    kho: dict,
    ma_tho: str,
    khoa_tran: str | None,
    luc: str,
) -> tuple[int, dict]:
    """Xác thực thợ, thu hồi phiếu quá hạn và giao nguyên tử phiếu `duyet` đầu tiên cho `ma_tho`."""
    with _KHOA_LUONG:
        if not xac_thuc_tho(kho, ma_tho, khoa_tran):
            return 401, {"ok": False, "loi": "unauthorized"}

        ma = ma_tho.strip()
        ds_phieu = kho.get("phieu")
        if not isinstance(ds_phieu, list):
            ds_phieu = []

        thu_hoi_qua_han(ds_phieu, luc, phut_qua_han=PHUT_QUA_HAN)

        for phieu in ds_phieu:
            if not isinstance(phieu, dict):
                continue
            if phieu.get("trang_thai") == "duyet":
                phieu["trang_thai"] = "giao"
                phieu["tho"] = ma
                phieu["giao_luc"] = luc
                return 200, {"ok": True, "phieu": dict(phieu)}

        return 200, {"ok": True, "phieu": None}
