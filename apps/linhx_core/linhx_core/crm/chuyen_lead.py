"""Chuyển lead giữa hai bản cài có ghi công (nguồn, đơn vị, thời điểm) và kiểm đồng ý chuyển chéo.

Tham khảo luồng tuân thủ và hồ sơ khách từ:
- nguon/03-opc-os/modules/04_quan_ly_user/module.py
- nguon/03-opc-os/modules/09_tuan_thu/module.py
"""
from __future__ import annotations

import copy

from linhx_core.crm import dong_y, gop_trung

TRUONG_CHUYEN = ("ho_ten", "dien_thoai", "email", "zalo")
TRUONG_GHI_CONG = ("nguon", "don_vi", "luc")


def goi_di(
    nguoi: dict,
    so_dong_y: list[dict],
    site_nguon: str,
    don_vi: str,
    luc: str,
) -> dict:
    """Kiểm đồng ý chuyển chéo và đóng gói hồ sơ liên hệ kèm ghi công để gửi sang bản cài đích.

    Ném dong_y.TuChoi nếu người dùng chưa đồng ý hoặc đã rút đồng ý mục đích 'chuyen_cheo'.
    Không mang theo trường nội bộ (name, owner, ghi_chu...).
    """
    if not isinstance(nguoi, dict):
        raise ValueError("Hồ sơ người không hợp lệ")

    dong_y.kiem_chuyen_cheo(so_dong_y, nguoi)

    nguon_str = str(site_nguon or "").strip()
    don_vi_str = str(don_vi or "").strip()
    luc_str = str(luc or "").strip()
    if not nguon_str or not don_vi_str or not luc_str:
        raise ValueError("Thiếu thông tin ghi công (nguon, don_vi, luc)")

    nguoi_sach = {
        k: nguoi.get(k)
        for k in TRUONG_CHUYEN
        if k in nguoi and nguoi.get(k) is not None
    }
    return {
        "nguoi": nguoi_sach,
        "ghi_cong": {
            "nguon": nguon_str,
            "don_vi": don_vi_str,
            "luc": luc_str,
        },
    }


def nhan(goi: dict, ds_nguoi: list[dict]) -> tuple[list[dict], dict]:
    """Nhận gói lead từ bản cài nguồn, kiểm tra ghi_cong và gộp trùng vào danh sách Người.

    Thiếu ghi_cong.nguon/don_vi/luc -> ValueError.
    Người nhận được giữ ghi_cong của gói gửi (không ghi đè ghi_cong cũ nếu đã có).
    """
    if not isinstance(goi, dict):
        raise ValueError("Gói chuyển lead không hợp lệ")

    gc = goi.get("ghi_cong")
    if not isinstance(gc, dict):
        raise ValueError("Thiếu ghi_cong trong gói chuyển lead")

    ghi_cong_chuan: dict[str, str] = {}
    for k in TRUONG_GHI_CONG:
        val = str(gc.get(k) or "").strip()
        if not val:
            raise ValueError(f"Thiếu trường ghi_cong.{k}")
        ghi_cong_chuan[k] = val

    nguoi_goi = goi.get("nguoi")
    if not isinstance(nguoi_goi, dict):
        raise ValueError("Thiếu thông tin nguoi trong gói chuyển lead")

    ban_moi = {
        k: nguoi_goi.get(k)
        for k in TRUONG_CHUYEN
        if k in nguoi_goi and nguoi_goi.get(k) is not None
    }
    ban_moi["ghi_cong"] = copy.deepcopy(ghi_cong_chuan)

    ds_moi = gop_trung.gop(ds_nguoi or [], ban_moi)
    khoa_moi = gop_trung.khoa_gop(ban_moi)
    nguoi_nhan = None
    if khoa_moi:
        for item in ds_moi:
            if gop_trung.khoa_gop(item) & khoa_moi:
                nguoi_nhan = item
                break
    if nguoi_nhan is None:
        nguoi_nhan = ds_moi[-1]

    return ds_moi, nguoi_nhan
