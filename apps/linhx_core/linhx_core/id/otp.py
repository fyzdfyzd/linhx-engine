"""OTP email dùng chung cho LINHX Core (đăng nhập và xác minh đồng ý marketing C2B).

Module thuần Python (không import frappe ở đầu file):
- Chỉ lưu bản băm SHA-256 của mã OTP trong kho (không bao giờ lưu mã trần).
- Mã hết hạn sau 10 phút (`HAN_PHUT = 10`).
- Nhập sai 5 lần (`SAI_TOI_DA = 5`) thì khoá kênh 15 phút (`KHOA_PHUT = 15`).
- Mã chỉ dùng một lần (`da_dung = True` ngay sau khi xác minh thành công).
"""
from __future__ import annotations

from datetime import datetime, timedelta
import hashlib
import hmac
import secrets
from typing import Callable

from linhx_core.crm import gop_trung

HAN_PHUT = 10
SAI_TOI_DA = 5
KHOA_PHUT = 15

DO_DAI_MA_OTP = 6
DO_DAI_EMAIL_TOI_DA = 254
DO_DAI_MUC_DICH_TOI_DA = 128
DO_DAI_MA_TOI_DA = 64
DINH_DANG_LUC_MAC_DINH = "%Y-%m-%d %H:%M:%S"


def _chuan_hoa_email(email: str) -> str:
    """Chuẩn hoá email chữ thường và kiểm tra khuôn dạng cơ bản."""
    if not isinstance(email, str):
        raise ValueError("Email phải là chuỗi ký tự")
    email_chuan = gop_trung.chuan_hoa_email(email)
    if (
        not email_chuan
        or len(email_chuan) > DO_DAI_EMAIL_TOI_DA
        or "@" not in email_chuan
        or any(ch.isspace() for ch in email_chuan)
    ):
        raise ValueError("Email không hợp lệ")
    local_part, _, domain_part = email_chuan.partition("@")
    if not local_part or not domain_part or "@" in domain_part:
        raise ValueError("Email không hợp lệ")
    return email_chuan


def _chuan_hoa_muc_dich(muc_dich: str) -> str:
    """Chuẩn hoá và kiểm tra chuỗi mục đích OTP."""
    if not isinstance(muc_dich, str):
        raise ValueError("Mục đích OTP phải là chuỗi ký tự")
    muc_dich_chuan = muc_dich.strip()
    if not muc_dich_chuan or len(muc_dich_chuan) > DO_DAI_MUC_DICH_TOI_DA:
        raise ValueError("Mục đích OTP không hợp lệ")
    return muc_dich_chuan


def _chuan_hoa_ma_otp(ma_otp: str) -> str:
    """Chuẩn hoá và kiểm tra chuỗi mã OTP."""
    if not isinstance(ma_otp, str):
        raise ValueError("Mã OTP phải là chuỗi ký tự")
    ma_chuan = ma_otp.strip()
    if not ma_chuan or len(ma_chuan) > DO_DAI_MA_TOI_DA:
        raise ValueError("Mã OTP không hợp lệ")
    return ma_chuan


def _phan_tich_luc(luc: str) -> datetime:
    """Phân tích chuỗi thời điểm `YYYY-MM-DD HH:MM:SS` hoặc ISO-8601."""
    if not isinstance(luc, str) or not luc.strip():
        raise ValueError("Thời điểm (luc) không hợp lệ")
    chuoi = luc.strip()
    try:
        return datetime.strptime(chuoi, DINH_DANG_LUC_MAC_DINH)
    except ValueError:
        try:
            return datetime.fromisoformat(chuoi)
        except ValueError as exc:
            raise ValueError(f"Thời điểm không đúng định dạng: {luc!r}") from exc


def _dinh_dang_luc(thoi_diem: datetime, luc_goc: str = "") -> str:
    """Định dạng lại thời điểm theo chuẩn `YYYY-MM-DD HH:MM:SS` (hoặc ISO nếu đầu vào có 'T')."""
    if isinstance(luc_goc, str) and "T" in luc_goc and thoi_diem.tzinfo is not None:
        return thoi_diem.isoformat( timespec="seconds")
    return thoi_diem.strftime(DINH_DANG_LUC_MAC_DINH)


def _khoa_kenh(email_chuan: str, muc_dich_chuan: str) -> str:
    """Tạo khoá kênh kiểu chuỗi (tương thích `json.dumps`) cho cặp `(email, muc_dich)`."""
    return f"{email_chuan}|{muc_dich_chuan}"


def bam_ma(email: str, muc_dich: str, ma_otp: str) -> str:
    """Băm SHA-256 hex của `(email chuẩn hoá chữ thường, muc_dich, ma_otp)`.

    Không bao giờ trả mã OTP trần.
    """
    email_chuan = _chuan_hoa_email(email)
    muc_dich_chuan = _chuan_hoa_muc_dich(muc_dich)
    ma_chuan = _chuan_hoa_ma_otp(ma_otp)
    du_lieu = (
        f"linhx-otp-v1|{len(email_chuan)}:{email_chuan}"
        f"|{len(muc_dich_chuan)}:{muc_dich_chuan}"
        f"|{len(ma_chuan)}:{ma_chuan}"
    )
    return hashlib.sha256(du_lieu.encode("utf-8")).hexdigest()


def _sinh_ma_otp(email_chuan: str, muc_dich_chuan: str) -> str:
    """Sinh mã OTP ngẫu nhiên an toàn gồm 6 chữ số."""
    for _ in range(16):
        ung_vien = f"{secrets.randbelow(10 ** DO_DAI_MA_OTP):0{DO_DAI_MA_OTP}d}"
        if ung_vien not in bam_ma(email_chuan, muc_dich_chuan, ung_vien):
            return ung_vien
    return f"{secrets.randbelow(10 ** DO_DAI_MA_OTP):0{DO_DAI_MA_OTP}d}"


def phat_ma(
    kho: dict,
    email: str,
    muc_dich: str,
    luc: str,
    ma_otp: str | None = None,
    gui_mail: Callable[[str, str, str], object] | None = None,
) -> dict:
    """Phát mã OTP mới cho kênh `(email, muc_dich)` tại thời điểm `luc`.

    - Nếu kênh đang bị khoá tại thời điểm `luc` (`luc < khoa_den`) -> `raise ValueError`.
    - Sinh mã 6 chữ số (hoặc dùng `ma_otp` truyền vào khi kiểm thử).
    - Chỉ lưu bản băm `ma_bam = bam_ma(...)` vào `kho`, tuyệt đối không lưu mã trần.
    - Nếu có `gui_mail` thì gọi `gui_mail(email_chuan, ma_otp, muc_dich)`.
    - Trả `{"email": email_chuan, "muc_dich": muc_dich, "het_han_luc": str}`.
    """
    if not isinstance(kho, dict):
        raise ValueError("Kho lưu OTP phải là dict")
    if gui_mail is not None and not callable(gui_mail):
        raise ValueError("gui_mail phải là hàm gọi được")

    email_chuan = _chuan_hoa_email(email)
    muc_dich_chuan = _chuan_hoa_muc_dich(muc_dich)
    thoi_diem = _phan_tich_luc(luc)
    khoa = _khoa_kenh(email_chuan, muc_dich_chuan)

    ban_ghi_cu = kho.get(khoa)
    if isinstance(ban_ghi_cu, dict):
        khoa_den_cu = ban_ghi_cu.get("khoa_den")
        if khoa_den_cu and thoi_diem < _phan_tich_luc(str(khoa_den_cu)):
            raise ValueError("Kênh OTP đang bị khoá tạm thời do nhập sai quá số lần cho phép")

    if ma_otp is None:
        ma_chuan = _sinh_ma_otp(email_chuan, muc_dich_chuan)
    else:
        ma_chuan = _chuan_hoa_ma_otp(ma_otp)

    ma_bam = bam_ma(email_chuan, muc_dich_chuan, ma_chuan)
    tao_luc_str = _dinh_dang_luc(thoi_diem, luc)
    het_han_str = _dinh_dang_luc(thoi_diem + timedelta(minutes=HAN_PHUT), luc)

    kho[khoa] = {
        "email": email_chuan,
        "muc_dich": muc_dich_chuan,
        "ma_bam": ma_bam,
        "tao_luc": tao_luc_str,
        "het_han_luc": het_han_str,
        "so_lan_sai": 0,
        "da_dung": False,
        "khoa_den": None,
    }

    if gui_mail is not None:
        gui_mail(email_chuan, ma_chuan, muc_dich_chuan)

    return {
        "email": email_chuan,
        "muc_dich": muc_dich_chuan,
        "het_han_luc": het_han_str,
    }


def xac_minh(
    kho: dict,
    email: str,
    muc_dich: str,
    ma_nhap: str,
    luc: str,
) -> dict:
    """Xác minh mã OTP `ma_nhap` cho kênh `(email, muc_dich)` tại thời điểm `luc`.

    Trả `{"ok": bool, "ly_do": str | None}`:
    - Đang trong thời gian khoá (`luc < khoa_den`) -> `{"ok": False, "ly_do": "bi_khoa"}`
    - Mã đã dùng (`da_dung == True`) -> `{"ok": False, "ly_do": "da_dung"}`
    - Quá 10 phút (`luc > het_han_luc`) -> `{"ok": False, "ly_do": "het_han"}`
    - Băm không khớp: tăng `so_lan_sai += 1`; nếu `so_lan_sai >= 5` thì đặt
      `khoa_den = luc + 15 phút` và trả `{"ok": False, "ly_do": "bi_khoa"}`;
      chưa tới 5 lần trả `{"ok": False, "ly_do": "sai_ma"}`
    - Băm khớp, còn hạn, chưa dùng, không khoá: đặt `da_dung = True`,
      trả `{"ok": True, "ly_do": None}`.
    """
    if not isinstance(kho, dict):
        raise ValueError("Kho lưu OTP phải là dict")

    email_chuan = _chuan_hoa_email(email)
    muc_dich_chuan = _chuan_hoa_muc_dich(muc_dich)
    thoi_diem = _phan_tich_luc(luc)
    khoa = _khoa_kenh(email_chuan, muc_dich_chuan)

    ban_ghi = kho.get(khoa)
    if not isinstance(ban_ghi, dict):
        return {"ok": False, "ly_do": "sai_ma"}

    khoa_den = ban_ghi.get("khoa_den")
    if khoa_den and thoi_diem < _phan_tich_luc(str(khoa_den)):
        return {"ok": False, "ly_do": "bi_khoa"}

    if ban_ghi.get("da_dung") is True:
        return {"ok": False, "ly_do": "da_dung"}

    het_han_luc = ban_ghi.get("het_han_luc")
    if not het_han_luc or thoi_diem > _phan_tich_luc(str(het_han_luc)):
        return {"ok": False, "ly_do": "het_han"}

    if int(ban_ghi.get("so_lan_sai") or 0) >= SAI_TOI_DA:
        return {"ok": False, "ly_do": "bi_khoa"}

    ma_nhap_str = ma_nhap.strip() if isinstance(ma_nhap, str) else ""
    ma_bam_luu = str(ban_ghi.get("ma_bam") or "")
    khop = False
    if ma_nhap_str and len(ma_nhap_str) <= DO_DAI_MA_TOI_DA and ma_bam_luu:
        bam_nhap = bam_ma(email_chuan, muc_dich_chuan, ma_nhap_str)
        khop = hmac.compare_digest(ma_bam_luu.encode("utf-8"), bam_nhap.encode("utf-8"))

    if not khop:
        so_lan_sai = int(ban_ghi.get("so_lan_sai") or 0) + 1
        ban_ghi["so_lan_sai"] = so_lan_sai
        if so_lan_sai >= SAI_TOI_DA:
            ban_ghi["khoa_den"] = _dinh_dang_luc(thoi_diem + timedelta(minutes=KHOA_PHUT), luc)
            return {"ok": False, "ly_do": "bi_khoa"}
        return {"ok": False, "ly_do": "sai_ma"}

    ban_ghi["da_dung"] = True
    return {"ok": True, "ly_do": None}
