"""Đăng nhập Zalo (OA IF Agent) và gộp hồ sơ vào LX Nguoi theo khoá gộp trùng A1.

Module thuần Python (không import frappe ở đầu file), tái sử dụng
`linhx_core.crm.gop_trung` để chuẩn hoá số điện thoại / `zalo_id` và gộp hồ sơ Người.
"""
from __future__ import annotations

import hmac

from linhx_core.crm import gop_trung

KENH_ZALO = "zalo"
HANH_DONG_GOP = "gop"
HANH_DONG_TAO_MOI = "tao_moi"

DO_DAI_ZALO_ID_TOI_DA = 255
DO_DAI_TEN_TOI_DA = 140
DO_DAI_OA_ID_TOI_DA = 255
DO_DAI_STATE_TOI_DA = 512
DO_DAI_SDT_TOI_THIEU = 9
DO_DAI_SDT_TOI_DA = 15


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


def chuan_hoa_ho_so_zalo(ho_so_zalo: dict) -> dict:
    """Kiểm tra và chuẩn hoá thông tin hồ sơ trả về từ Zalo OAuth (OA IF Agent)."""
    if not isinstance(ho_so_zalo, dict):
        raise ValueError("Hồ sơ Zalo không hợp lệ")

    raw_zalo_id = ho_so_zalo.get("zalo_id")
    if not isinstance(raw_zalo_id, str):
        raise ValueError("Thiếu định danh Zalo (zalo_id)")
    zalo_id = gop_trung.chuan_hoa_zalo(raw_zalo_id)
    if not zalo_id or len(zalo_id) > DO_DAI_ZALO_ID_TOI_DA or any(ch.isspace() for ch in zalo_id):
        raise ValueError("Thiếu hoặc sai định danh Zalo (zalo_id)")

    raw_dt = ho_so_zalo.get("dien_thoai")
    dien_thoai_chuan = ""
    if raw_dt is not None:
        if not isinstance(raw_dt, str):
            raise ValueError("Số điện thoại Zalo không hợp lệ")
        if raw_dt.strip():
            dien_thoai_chuan = gop_trung.chuan_hoa_dien_thoai(raw_dt)
            if (
                not dien_thoai_chuan
                or len(dien_thoai_chuan) < DO_DAI_SDT_TOI_THIEU
                or len(dien_thoai_chuan) > DO_DAI_SDT_TOI_DA
            ):
                raise ValueError("Số điện thoại Zalo không hợp lệ")

    raw_ten = ho_so_zalo.get("ho_ten")
    if raw_ten is None or (isinstance(raw_ten, str) and not raw_ten.strip()):
        raw_ten = ho_so_zalo.get("name")
    ho_ten = str(raw_ten if raw_ten is not None else "").strip()
    if len(ho_ten) > DO_DAI_TEN_TOI_DA:
        ho_ten = ho_ten[:DO_DAI_TEN_TOI_DA].rstrip()

    raw_oa = ho_so_zalo.get("oa_id")
    oa_id = str(raw_oa if raw_oa is not None else "").strip()
    if len(oa_id) > DO_DAI_OA_ID_TOI_DA:
        raise ValueError("Định danh OA vượt quá độ dài cho phép")

    return {
        "zalo_id": zalo_id,
        "dien_thoai": dien_thoai_chuan,
        "ho_ten": ho_ten,
        "oa_id": oa_id,
    }


def dang_nhap_zalo(
    ho_so_zalo: dict,
    state_gui: str,
    state_phien: str,
    ds_nguoi: list[dict],
    nhat_ky_gop: list[dict],
    luc: str,
) -> dict:
    """Xác thực đăng nhập Zalo, gộp vào `ds_nguoi` theo khoá gộp trùng A1 và ghi `nhat_ky_gop`.

    - Kiểm tra `state_gui` và `state_phien` hằng thời gian (`hmac.compare_digest`).
    - Đòi hỏi `zalo_id` hợp lệ; chuẩn hoá `dien_thoai` (`0...`, `+84...`, `84...` về `84...`).
    - Nếu trùng SĐT hoặc trùng `zalo_id` trong `ds_nguoi`: gộp vào bản ghi cũ (không tạo mới,
      bù trường còn trống như `zalo`, `dien_thoai`, `ho_ten`).
    - Ghi một dòng vào `nhat_ky_gop` với `kenh="zalo"` và `hanh_dong` là `"gop"` hoặc `"tao_moi"`.
    """
    kiem_state_oauth(state_gui, state_phien)
    ho_so = chuan_hoa_ho_so_zalo(ho_so_zalo)

    if not isinstance(ds_nguoi, list):
        raise ValueError("ds_nguoi phải là danh sách")
    if not isinstance(nhat_ky_gop, list):
        raise ValueError("nhat_ky_gop phải là danh sách")

    luc_str = str(luc or "").strip()
    zalo_id = ho_so["zalo_id"]
    dien_thoai_chuan = ho_so["dien_thoai"]
    ho_ten = ho_so["ho_ten"]
    oa_id = ho_so["oa_id"]

    ban_moi: dict = {
        "zalo": zalo_id,
    }
    if dien_thoai_chuan:
        ban_moi["dien_thoai"] = dien_thoai_chuan
    if ho_ten:
        ban_moi["ho_ten"] = ho_ten
    if oa_id:
        ban_moi["oa_id"] = oa_id

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

    dong_nhat_ky: dict = {
        "luc": luc_str,
        "kenh": KENH_ZALO,
        "hanh_dong": HANH_DONG_GOP if da_gop else HANH_DONG_TAO_MOI,
        "zalo_id": zalo_id,
        "nguoi": nguoi_ket_qua.get("name") or zalo_id,
    }
    if dien_thoai_chuan:
        dong_nhat_ky["dien_thoai"] = dien_thoai_chuan
    if oa_id:
        dong_nhat_ky["oa_id"] = oa_id

    ds_nguoi[:] = ds_ket_qua
    nhat_ky_gop.append(dong_nhat_ky)

    return {
        "ds_nguoi": ds_nguoi,
        "nguoi": nguoi_ket_qua,
        "nhat_ky_gop": nhat_ky_gop,
        "da_gop": da_gop,
    }
