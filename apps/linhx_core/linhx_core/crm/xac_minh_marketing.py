"""Xác minh chủ email/SĐT (double opt-in) trước khi đồng ý marketing có hiệu lực (C2B).

Thuần Python, không import frappe ở đầu file.
Tái sử dụng cơ chế OTP của I3 (`linhx_core.id.otp` khi có sẵn, hoặc bộ hàm chuẩn tương đương):
- Chỉ lưu mã băm HMAC-SHA256 (có khoá bí mật) trong `kho_otp`, tuyệt đối không lưu mã OTP trần.
- Mã OTP tự sinh có độ dài 8 chữ số; hạn dùng 10 phút (`HAN_PHUT = 10`), dùng một lần (`da_dung = True`).
- Sai 5 lần khoá 15 phút; phát lại mã giữ nguyên `so_lan_sai` và `khoa_den`, có trần số lần phát mỗi kênh mỗi giờ.
- Yêu cầu thao tác của người qua phương thức `POST`; truy cập `GET` (như bộ quét link trong mail)
  không tiêu thụ mã OTP và không ghi đồng ý marketing.
"""
from __future__ import annotations

import copy
from datetime import datetime, timedelta
import hashlib
import hmac
import os
import secrets
import sys
from typing import Callable

from linhx_core.crm import dong_y, form, gop_trung

try:
    from linhx_core.id import otp as _id_otp
except ImportError:
    _id_otp = None

MUC_DICH_MARKETING = "marketing"
HAN_PHUT = 10
SAI_TOI_DA = 5
KHOA_PHUT = 15
DO_DAI_MA_OTP = 8
PHAT_TOI_DA_MOI_GIO = 5
CUA_SO_PHAT_PHUT = 60
_KHOA_HMAC_MAC_DINH = "linhx-c2b-otp-hmac-sha256-v1"


def _chuan_kenh(email: str) -> str:
    """Chuẩn hoá kênh xác nhận (email chữ thường hoặc SĐT chuẩn 84...)."""
    raw = str(email or "").strip()
    if not raw:
        return ""
    if "@" in raw:
        return gop_trung.chuan_hoa_email(raw) or raw.lower()
    dt = gop_trung.chuan_hoa_dien_thoai(raw)
    if dt:
        return dt
    return raw.lower()


def _khoa_otp(email_chuan: str, muc_dich: str) -> str:
    return f"{email_chuan}:{muc_dich}"


def _lay_khoa_bi_mat(khoa_bi_mat: str | None = None) -> bytes:
    """Lấy khoá bí mật cho HMAC-SHA256 từ tham số, biến môi trường hoặc cấu hình site."""
    if isinstance(khoa_bi_mat, str) and khoa_bi_mat.strip():
        return khoa_bi_mat.strip().encode("utf-8")
    tu_env = os.environ.get("LINHX_OTP_SECRET", "").strip()
    if tu_env:
        return tu_env.encode("utf-8")
    frappe_mod = sys.modules.get("frappe")
    if frappe_mod is not None:
        conf = getattr(frappe_mod, "conf", None)
        if conf is not None:
            getter = getattr(conf, "get", None)
            if callable(getter):
                for ten_khoa in ("otp_hmac_secret", "secret_key", "encryption_key"):
                    val = str(getter(ten_khoa) or "").strip()
                    if val:
                        return val.encode("utf-8")
    return _KHOA_HMAC_MAC_DINH.encode("utf-8")


def bam_ma(
    email: str,
    muc_dich: str,
    ma_otp: str,
    *,
    khoa_bi_mat: str | None = None,
) -> str:
    """Băm HMAC-SHA256 hex (64 ký tự) của (email chuẩn hoá, muc_dich, ma_otp) với khoá bí mật."""
    em_chuan = _chuan_kenh(email)
    md_chuan = str(muc_dich or "").strip()
    ma_chuan = str(ma_otp or "").strip()
    chuoi = f"{em_chuan}:{md_chuan}:{ma_chuan}"
    khoa_bytes = _lay_khoa_bi_mat(khoa_bi_mat)
    return hmac.new(khoa_bytes, chuoi.encode("utf-8"), hashlib.sha256).hexdigest()


def _loc_lich_su_phat_1_gio(lich_su_cu: object, dt_luc: datetime) -> list[str]:
    if not isinstance(lich_su_cu, list):
        return []
    ket_qua: list[str] = []
    nguong = timedelta(minutes=CUA_SO_PHAT_PHUT)
    for moc in lich_su_cu:
        try:
            dt_moc = dong_y._parse_tg(moc)
        except ValueError:
            continue
        khoang = dt_luc - dt_moc
        if timedelta(0) <= khoang < nguong:
            ket_qua.append(dt_moc.replace(microsecond=0).strftime(dong_y.DINH_DANG_TG))
    return ket_qua


def phat_ma(
    kho: dict,
    email: str,
    muc_dich: str,
    luc: str | datetime,
    ma_otp: str | None = None,
    gui_mail: Callable[[str, str, str], None] | None = None,
) -> dict:
    """Phát mã OTP 8 chữ số, chỉ lưu bản băm HMAC-SHA256 vào `kho`, hạn 10 phút, dùng 1 lần.

    Khi phát lại mã:
    - Giữ nguyên `so_lan_sai` và `khoa_den` nếu kênh chưa hết thời gian khoá và mã trước chưa xác minh.
    - Áp trần số lần phát mã mỗi kênh mỗi giờ (`PHAT_TOI_DA_MOI_GIO`).
    """
    if not isinstance(kho, dict):
        raise ValueError("Kho OTP không hợp lệ")
    em_chuan = _chuan_kenh(email)
    if not em_chuan:
        raise ValueError("Thiếu địa chỉ kênh nhận OTP")
    md_chuan = str(muc_dich or "").strip()
    if not md_chuan:
        raise ValueError("Thiếu mục đích xác minh OTP")

    dt_luc = dong_y._parse_tg(luc)
    luc_str = dt_luc.replace(microsecond=0).strftime(dong_y.DINH_DANG_TG)
    khoa = _khoa_otp(em_chuan, md_chuan)

    hien_co = kho.get(khoa)
    so_lan_sai_giu = 0
    khoa_den_giu: str | None = None
    nguoi_giu: str | None = None

    if isinstance(hien_co, dict):
        nguoi_giu = str(hien_co.get("nguoi") or "").strip() or None
        khoa_den_cu = hien_co.get("khoa_den")
        if khoa_den_cu:
            dt_khoa_den = dong_y._parse_tg(khoa_den_cu)
            if dt_luc <= dt_khoa_den:
                raise ValueError(f"Kênh đang bị khoá tạm thời tới {khoa_den_cu}")
            # Đã qua thời hạn khoá 15 phút -> cho phép đặt lại bộ đếm sai
            so_lan_sai_giu = 0
            khoa_den_giu = None
        elif not bool(hien_co.get("da_dung")):
            so_lan_sai_giu = max(0, int(hien_co.get("so_lan_sai") or 0))

    lich_su_phat = _loc_lich_su_phat_1_gio(
        hien_co.get("lich_su_phat") if isinstance(hien_co, dict) else None,
        dt_luc,
    )
    if len(lich_su_phat) >= PHAT_TOI_DA_MOI_GIO:
        raise ValueError("Đã vượt quá giới hạn số lần phát mã OTP mỗi giờ cho kênh này")
    lich_su_phat.append(luc_str)

    ma_sinh = (
        str(ma_otp).strip()
        if ma_otp is not None
        else f"{secrets.randbelow(10 ** DO_DAI_MA_OTP):0{DO_DAI_MA_OTP}d}"
    )
    if not ma_sinh:
        raise ValueError("Mã OTP không được rỗng")

    het_han_dt = dt_luc + timedelta(minutes=HAN_PHUT)
    het_han_str = het_han_dt.replace(microsecond=0).strftime(dong_y.DINH_DANG_TG)
    ma_bam = bam_ma(em_chuan, md_chuan, ma_sinh)

    ban_ghi_moi: dict = {
        "email": em_chuan,
        "muc_dich": md_chuan,
        "ma_bam": ma_bam,
        "tao_luc": luc_str,
        "het_han_luc": het_han_str,
        "so_lan_sai": so_lan_sai_giu,
        "da_dung": False,
        "khoa_den": khoa_den_giu,
        "lich_su_phat": lich_su_phat,
    }
    if nguoi_giu:
        ban_ghi_moi["nguoi"] = nguoi_giu
    kho[khoa] = ban_ghi_moi

    if callable(gui_mail):
        gui_mail(em_chuan, ma_sinh, md_chuan)

    return {
        "email": em_chuan,
        "muc_dich": md_chuan,
        "het_han_luc": het_han_str,
    }


def xac_minh(
    kho: dict,
    email: str,
    muc_dich: str,
    ma_nhap: str,
    luc: str | datetime,
) -> dict:
    """Kiểm mã OTP theo băm hằng thời gian, hạn 10 phút, dùng 1 lần, sai 5 lần khoá 15 phút."""
    if not isinstance(kho, dict):
        return {"ok": False, "ly_do": "khong_co_ma"}
    em_chuan = _chuan_kenh(email)
    md_chuan = str(muc_dich or "").strip()
    if not em_chuan or not md_chuan:
        return {"ok": False, "ly_do": "khong_co_ma"}

    khoa = _khoa_otp(em_chuan, md_chuan)
    ban_ghi = kho.get(khoa)
    if not isinstance(ban_ghi, dict):
        if _id_otp is not None and hasattr(_id_otp, "xac_minh"):
            return _id_otp.xac_minh(kho, email, muc_dich, ma_nhap, luc)
        return {"ok": False, "ly_do": "khong_co_ma"}

    dt_luc = dong_y._parse_tg(luc)
    if ban_ghi.get("khoa_den"):
        dt_khoa_den = dong_y._parse_tg(ban_ghi["khoa_den"])
        if dt_luc <= dt_khoa_den:
            return {"ok": False, "ly_do": "bi_khoa"}

    if bool(ban_ghi.get("da_dung")):
        return {"ok": False, "ly_do": "da_dung"}

    het_han_raw = ban_ghi.get("het_han_luc")
    if not het_han_raw or dt_luc > dong_y._parse_tg(het_han_raw):
        return {"ok": False, "ly_do": "het_han"}

    ma_nhap_str = str(ma_nhap or "").strip()
    bam_nhap = bam_ma(em_chuan, md_chuan, ma_nhap_str)
    bam_luu = str(ban_ghi.get("ma_bam") or "")

    khop = bool(bam_luu) and hmac.compare_digest(bam_luu, bam_nhap)
    if not khop and _id_otp is not None and hasattr(_id_otp, "bam_ma"):
        bam_id = str(_id_otp.bam_ma(em_chuan, md_chuan, ma_nhap_str) or "")
        khop = bool(bam_luu and bam_id) and hmac.compare_digest(bam_luu, bam_id)

    if not khop:
        so_lan_sai = int(ban_ghi.get("so_lan_sai") or 0) + 1
        ban_ghi["so_lan_sai"] = so_lan_sai
        if so_lan_sai >= SAI_TOI_DA:
            khoa_den_dt = dt_luc + timedelta(minutes=KHOA_PHUT)
            ban_ghi["khoa_den"] = khoa_den_dt.replace(microsecond=0).strftime(dong_y.DINH_DANG_TG)
            return {"ok": False, "ly_do": "bi_khoa"}
        return {"ok": False, "ly_do": "sai_ma"}

    ban_ghi["da_dung"] = True
    ban_ghi["so_lan_sai"] = 0
    return {"ok": True, "ly_do": None}


def _tim_ban_ghi_otp(kho_otp: dict, em_chuan: str) -> dict | None:
    if not isinstance(kho_otp, dict):
        return None
    for k_ung_vien in (
        _khoa_otp(em_chuan, MUC_DICH_MARKETING),
        (em_chuan, MUC_DICH_MARKETING),
        em_chuan,
    ):
        val = kho_otp.get(k_ung_vien)
        if isinstance(val, dict):
            return val
    for val in kho_otp.values():
        if (
            isinstance(val, dict)
            and _chuan_kenh(val.get("email") or "") == em_chuan
            and val.get("muc_dich") == MUC_DICH_MARKETING
        ):
            return val
    return None


def da_rut_dong_y_sau_otp(
    so_dong_y: list[dict],
    ma_nguoi: str,
    tao_luc_otp: str = "",
) -> bool:
    """Kiểm tra người dùng đã rút đồng ý marketing (trạng thái hiệu lực đang rút hoặc có dòng rút >= tao_luc_otp)."""
    if not so_dong_y or not ma_nguoi:
        return False
    if form.da_rut_dong_y(so_dong_y, ma_nguoi, MUC_DICH_MARKETING):
        return True
    khoa_tao = dong_y._khoa_luc(tao_luc_otp) if str(tao_luc_otp or "").strip() else None
    for d in so_dong_y:
        if not isinstance(d, dict):
            continue
        if dong_y._ma_nguoi(d.get("nguoi")) != ma_nguoi:
            continue
        if d.get("muc_dich") != MUC_DICH_MARKETING:
            continue
        if str(d.get("trang_thai") or "").strip() == "cho_xac_minh":
            continue
        if not dong_y._chuan_dong_y(d.get("dong_y")):
            if khoa_tao is None or dong_y._khoa_luc(d.get("luc")) >= khoa_tao:
                return True
    return False


def tao_yeu_cau(
    kho_otp: dict,
    email: str,
    nguoi: str | dict,
    so_dong_y: list[dict],
    luc: str | datetime,
    ma_otp: str | None = None,
    gui_mail: Callable[[str, str, str], None] | None = None,
) -> dict:
    """Phát mã OTP cho kênh `email` (chỉ lưu băm trong `kho_otp`, hạn 10 phút, dùng 1 lần)
    và đảm bảo dòng đồng ý `marketing` trong `so_dong_y` ở trạng thái `cho_xac_minh` (chưa hiệu lực).
    """
    em_chuan = _chuan_kenh(email)
    if not em_chuan:
        raise ValueError("Thiếu email hoặc kênh liên hệ để xác minh đồng ý marketing")
    ma_nguoi = dong_y._ma_nguoi(nguoi)
    if not ma_nguoi:
        raise ValueError("Thiếu mã người cần xác minh đồng ý marketing")

    dt_luc = dong_y._parse_tg(luc)
    luc_str = dt_luc.replace(microsecond=0).strftime(dong_y.DINH_DANG_TG)

    kq_phat = phat_ma(
        kho_otp,
        em_chuan,
        MUC_DICH_MARKETING,
        luc_str,
        ma_otp=ma_otp,
        gui_mail=gui_mail,
    )

    ban_ghi = _tim_ban_ghi_otp(kho_otp, em_chuan)
    if isinstance(ban_ghi, dict):
        ban_ghi["nguoi"] = ma_nguoi

    if isinstance(so_dong_y, list):
        da_hieu_luc = dong_y.hieu_luc(so_dong_y, ma_nguoi, MUC_DICH_MARKETING)
        da_rut = form.da_rut_dong_y(so_dong_y, ma_nguoi, MUC_DICH_MARKETING)
        if not da_hieu_luc and not da_rut:
            ung_vien_mkt: list[tuple[tuple[int, object], int, dict]] = []
            for idx, d in enumerate(so_dong_y):
                if not isinstance(d, dict):
                    continue
                if dong_y._ma_nguoi(d.get("nguoi")) == ma_nguoi and d.get("muc_dich") == MUC_DICH_MARKETING:
                    ung_vien_mkt.append((dong_y._khoa_luc(d.get("luc")), idx, d))

            if ung_vien_mkt:
                _, _, dong_moi_nhat = max(ung_vien_mkt, key=lambda item: (item[0], item[1]))
                if dong_y._chuan_dong_y(dong_moi_nhat.get("dong_y")):
                    dong_moi_nhat["trang_thai"] = "cho_xac_minh"
            else:
                so_dong_y.append(
                    {
                        "nguoi": ma_nguoi,
                        "muc_dich": MUC_DICH_MARKETING,
                        "dong_y": True,
                        "luc": luc_str,
                        "nguon": "cho-xac-minh",
                        "trang_thai": "cho_xac_minh",
                    }
                )

    return {
        "email": em_chuan,
        "nguoi": ma_nguoi,
        "muc_dich": MUC_DICH_MARKETING,
        "trang_thai": "cho_xac_minh",
        "het_han_luc": kq_phat.get("het_han_luc"),
        "so_dong_y": so_dong_y,
    }


def xac_nhan_marketing(
    phuong_thuc: str,
    kho_otp: dict,
    email: str,
    nguoi: str | dict,
    ma_nhap: str,
    so_dong_y: list[dict],
    luc: str | datetime,
    nguon: str = "xac-minh-otp",
) -> tuple[int, dict]:
    """Xác nhận đồng ý marketing qua OTP:
    - Nếu `phuong_thuc != "POST"` (vd. `"GET"` khi bộ quét mail tự mở link):
      KHÔNG tiêu thụ mã OTP và KHÔNG ghi đồng ý marketing, trả `(405, {"ok": False, "can_post": True, "so_dong_y": ...})`.
    - Nếu `phuong_thuc == "POST"`:
      Kiểm mã qua `xac_minh(kho_otp, email, "marketing", ma_nhap, luc)`.
      * Đúng, còn hạn, chưa dùng và chưa rút đồng ý sau khi phát OTP: ghi dòng `marketing` đã xác minh
        (`trang_thai="da_xac_minh"`, `dong_y=True`) vào sổ mới để `dong_y.hieu_luc(so_moi, nguoi, "marketing") == True`;
        trả `(200, {"ok": True, "so_dong_y": so_moi})`.
      * Sai, hết hạn, đã dùng, bị khoá hoặc đã rút đồng ý: không kích hoạt đồng ý marketing,
        trả `(400, {"ok": False, "ly_do": ..., "so_dong_y": ...})`.
    """
    so_ban_sao = [copy.deepcopy(d) if isinstance(d, dict) else d for d in (so_dong_y or [])]
    pt = str(phuong_thuc or "").strip().upper()
    if pt != "POST":
        return (
            405,
            {
                "ok": False,
                "can_post": True,
                "ly_do": "phuong_thuc_khong_hop_le",
                "so_dong_y": so_ban_sao,
            },
        )

    em_chuan = _chuan_kenh(email)
    ma_nguoi = dong_y._ma_nguoi(nguoi)
    ma_nhap_str = str(ma_nhap or "").strip()
    if not isinstance(kho_otp, dict) or not em_chuan or not ma_nguoi or not ma_nhap_str:
        return (
            400,
            {
                "ok": False,
                "ly_do": "du_lieu_khong_hop_le",
                "so_dong_y": so_ban_sao,
            },
        )

    ban_ghi = _tim_ban_ghi_otp(kho_otp, em_chuan)
    tao_luc_otp = ""
    if isinstance(ban_ghi, dict):
        tao_luc_otp = str(ban_ghi.get("tao_luc") or "").strip()
        nguoi_trong_otp = str(ban_ghi.get("nguoi") or "").strip()
        if nguoi_trong_otp and nguoi_trong_otp != ma_nguoi:
            return (
                400,
                {
                    "ok": False,
                    "ly_do": "khong_khop_nguoi",
                    "so_dong_y": so_ban_sao,
                },
            )

    try:
        kq_otp = xac_minh(kho_otp, em_chuan, MUC_DICH_MARKETING, ma_nhap_str, luc)
    except ValueError:
        return (
            400,
            {
                "ok": False,
                "ly_do": "thoi_diem_khong_hop_le",
                "so_dong_y": so_ban_sao,
            },
        )

    if not kq_otp.get("ok"):
        return (
            400,
            {
                "ok": False,
                "ly_do": kq_otp.get("ly_do") or "xac_minh_that_bai",
                "so_dong_y": so_ban_sao,
            },
        )

    if da_rut_dong_y_sau_otp(so_ban_sao, ma_nguoi, tao_luc_otp):
        return (
            400,
            {
                "ok": False,
                "ly_do": "da_rut_dong_y",
                "so_dong_y": so_ban_sao,
            },
        )

    so_moi = dong_y.ghi(
        so_ban_sao,
        ma_nguoi,
        MUC_DICH_MARKETING,
        True,
        luc,
        str(nguon or "").strip() or "xac-minh-otp",
        trang_thai="da_xac_minh",
    )
    return (
        200,
        {
            "ok": True,
            "ly_do": None,
            "so_dong_y": so_moi,
        },
    )
