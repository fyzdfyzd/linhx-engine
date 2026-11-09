"""Đăng nhập Google OAuth và gộp hồ sơ vào LX Nguoi theo khoá gộp trùng A1.

Module thuần Python (không import frappe ở đầu file), tái sử dụng
`linhx_core.crm.gop_trung` để chuẩn hoá email và gộp hồ sơ Người.
"""
from __future__ import annotations

import hmac

from linhx_core.crm import gop_trung

KENH_GOOGLE = "google"
HANH_DONG_GOP = "gop"
HANH_DONG_TAO_MOI = "tao_moi"

DO_DAI_EMAIL_TOI_DA = 254
DO_DAI_TEN_TOI_DA = 140
DO_DAI_SUB_TOI_DA = 255
DO_DAI_STATE_TOI_DA = 512


def kiem_state_oauth(state_gui: str, state_phien: str) -> None:
    """Kiểm tra state OAuth hằng thời gian bằng `hmac.compare_digest`."""
    if not isinstance(state_gui, str) or not isinstance(state_phien, str):
        raise ValueError("State OAuth phải là chuỗi ký tự")
    if not state_gui or not state_phien or not state_gui.strip() or not state_phien.strip():
        raise ValueError("State OAuth không được để trống")
    if len(state_gui) > DO_DAI_STATE_TOI_DA or len(state_phien) > DO_DAI_STATE_TOI_DA:
        raise ValueError("State OAuth vượt quá độ dài cho phép")
    if not hmac.compare_digest(state_gui.encode("utf-8"), state_phien.encode("utf-8")):
        raise ValueError("State OAuth không khớp")


def chuan_hoa_ho_so_google(ho_so_google: dict) -> dict:
    """Kiểm tra và chuẩn hoá thông tin hồ sơ trả về từ Google OAuth."""
    if not isinstance(ho_so_google, dict):
        raise ValueError("Hồ sơ Google không hợp lệ")

    if ho_so_google.get("email_verified") is not True:
        raise ValueError("Email Google chưa được xác minh")

    raw_email = ho_so_google.get("email")
    if not isinstance(raw_email, str):
        raise ValueError("Email Google không hợp lệ")
    email_chuan = gop_trung.chuan_hoa_email(raw_email)
    if (
        not email_chuan
        or len(email_chuan) > DO_DAI_EMAIL_TOI_DA
        or "@" not in email_chuan
        or any(ch.isspace() for ch in email_chuan)
    ):
        raise ValueError("Email Google không hợp lệ")
    local_part, _, domain_part = email_chuan.partition("@")
    if not local_part or not domain_part or "@" in domain_part:
        raise ValueError("Email Google không hợp lệ")

    raw_sub = ho_so_google.get("sub")
    sub = str(raw_sub if raw_sub is not None else "").strip()
    if not sub or len(sub) > DO_DAI_SUB_TOI_DA:
        raise ValueError("Thiếu định danh Google (sub)")

    raw_ten = ho_so_google.get("ho_ten")
    if raw_ten is None or (isinstance(raw_ten, str) and not raw_ten.strip()):
        raw_ten = ho_so_google.get("name")
    ho_ten = str(raw_ten if raw_ten is not None else "").strip()
    if len(ho_ten) > DO_DAI_TEN_TOI_DA:
        ho_ten = ho_ten[:DO_DAI_TEN_TOI_DA].rstrip()

    return {
        "sub": sub,
        "email": email_chuan,
        "ho_ten": ho_ten,
    }


def dang_nhap_google(
    ho_so_google: dict,
    state_gui: str,
    state_phien: str,
    ds_nguoi: list[dict],
    nhat_ky_gop: list[dict],
    luc: str,
) -> dict:
    """Xác thực đăng nhập Google, gộp vào `ds_nguoi` theo khoá gộp trùng A1 và ghi `nhat_ky_gop`.

    - Kiểm tra `state_gui` và `state_phien` hằng thời gian (`hmac.compare_digest`).
    - Đòi hỏi `email_verified is True` và `email` hợp lệ.
    - Nếu email đã tồn tại trong `ds_nguoi` (không phân biệt hoa thường): không tạo bản ghi mới,
      giữ nguyên trường cũ đã có giá trị và bù trường còn trống (như `ho_ten`, `google_sub`).
    - Ghi một dòng vào `nhat_ky_gop` với `hanh_dong` là `"gop"` hoặc `"tao_moi"`.
    """
    kiem_state_oauth(state_gui, state_phien)
    ho_so = chuan_hoa_ho_so_google(ho_so_google)

    if not isinstance(ds_nguoi, list):
        raise ValueError("ds_nguoi phải là danh sách")
    if not isinstance(nhat_ky_gop, list):
        raise ValueError("nhat_ky_gop phải là danh sách")

    luc_str = str(luc or "").strip()
    email_chuan = ho_so["email"]
    sub = ho_so["sub"]
    ho_ten = ho_so["ho_ten"]

    ban_moi: dict = {
        "email": email_chuan,
        "google_sub": sub,
    }
    if ho_ten:
        ban_moi["ho_ten"] = ho_ten

    khoa_moi = gop_trung.khoa_gop(ban_moi)
    vi_tri_trung: int | None = None
    for idx, cu in enumerate(ds_nguoi):
        if isinstance(cu, dict) and (gop_trung.khoa_gop(cu) & khoa_moi):
            vi_tri_trung = idx
            break

    ds_ket_qua = gop_trung.gop(ds_nguoi, ban_moi)
    da_gop = vi_tri_trung is not None and len(ds_ket_qua) == len(ds_nguoi)
    nguoi_ket_qua = (
        ds_ket_qua[vi_tri_trung]
        if da_gop and vi_tri_trung is not None
        else ds_ket_qua[-1]
    )

    dong_nhat_ky = {
        "luc": luc_str,
        "kenh": KENH_GOOGLE,
        "hanh_dong": HANH_DONG_GOP if da_gop else HANH_DONG_TAO_MOI,
        "email": email_chuan,
        "google_sub": sub,
        "nguoi": nguoi_ket_qua.get("name") or email_chuan,
    }

    ds_nguoi[:] = ds_ket_qua
    nhat_ky_gop.append(dong_nhat_ky)

    return {
        "ds_nguoi": ds_nguoi,
        "nguoi": nguoi_ket_qua,
        "nhat_ky_gop": nhat_ky_gop,
        "da_gop": da_gop,
    }
