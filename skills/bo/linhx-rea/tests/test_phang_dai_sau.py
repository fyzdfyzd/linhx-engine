"""Kiểm thử 9 (R5a): `quyet_dinh_phang` loại ảnh 3D dải sâu rộng (sony24), nhận đúng 3 poster (kv1..kv3), và lưới ô vuông đều cv2.rectangle không làm tăng `so_ky_tu_ngang` quá ngưỡng."""
from __future__ import annotations

import cv2
import numpy as np

import anh_do


def test_phang_dai_sau_va_luoi_cua_so() -> None:
    # 1. Chỉ số của sony24-01_pavy (ghi cứng từ đề R5 và từ do.json) -> bắt buộc False
    chi_so_sony24_de = {
        "ti_le_mang_phang": 0.45,
        "so_ky_tu_ngang": 365.0,
        "so_dong_chu": 39.0,
        "dai_norm_p95_p5": 0.78,
    }
    phang_s1, ly_do_s1 = anh_do.quyet_dinh_phang(chi_so_sony24_de)
    assert phang_s1 is False and ly_do_s1 == ""

    chi_so_sony24_do_json = {
        "dai_raw_p95_p5": 5.5741,
        "dai_norm_p95_p5": 0.7768,
        "ti_le_mang_phang": 0.452,
        "so_ky_tu_ngang": 365.0,
        "so_dong_chu": 39.0,
    }
    phang_s2, ly_do_s2 = anh_do.quyet_dinh_phang(chi_so_sony24_do_json)
    assert phang_s2 is False and ly_do_s2 == ""

    # 2. Chỉ số của 3 poster lấy từ do.json (ghi cứng) -> bắt buộc True
    ds_poster = [
        {
            "dai_raw_p95_p5": 4.827,
            "dai_norm_p95_p5": 0.8271,
            "ti_le_mang_phang": 0.4962,
            "so_ky_tu_ngang": 513.0,
            "so_dong_chu": 14.0,
        },
        {
            "dai_raw_p95_p5": 2.2389,
            "dai_norm_p95_p5": 0.7562,
            "ti_le_mang_phang": 0.8,
            "so_ky_tu_ngang": 73.0,
            "so_dong_chu": 5.0,
        },
        {
            "dai_raw_p95_p5": 1.8066,
            "dai_norm_p95_p5": 0.6861,
            "ti_le_mang_phang": 0.6538,
            "so_ky_tu_ngang": 349.0,
            "so_dong_chu": 11.0,
        },
    ]
    for chi_so_kv in ds_poster:
        phang_kv, ly_do_kv = anh_do.quyet_dinh_phang(chi_so_kv)
        assert phang_kv is True, f"Poster phải ra phang=True: {chi_so_kv}"
        assert ly_do_kv != ""

    # 3. Ảnh tự sinh lưới ô vuông đều (cv2.rectangle: cả khung rỗng lẫn ô đặc làm mờ nhẹ)
    cao, rong = 640, 800
    d_norm = np.tile(np.linspace(0.02, 0.98, cao, dtype=np.float32)[:, None], (1, rong))
    d_raw = d_norm * np.float32(4.2)  # dải raw vừa phải để kiểm riêng bộ lọc cửa sổ

    # 3a. Lưới 9x10 = 90 khung ô vuông rỗng đều nhau bằng cv2.rectangle
    img_khung = np.full((cao, rong, 3), (232, 236, 240), dtype=np.uint8)
    for hang in range(9):
        for cot in range(10):
            x0 = 70 + cot * 64
            y0 = 55 + hang * 58
            cv2.rectangle(img_khung, (x0, y0), (x0 + 18, y0 + 18), (32, 36, 42), 2)

    phang_g1, _, chi_so_g1 = anh_do.do_dac_trung_phang(img_khung, d_raw, d_norm)
    assert chi_so_g1["so_ky_tu_ngang"] < anh_do.NGUONG_KY_TU_NGANG, f"Lưới khung vuông bị đếm nhầm: {chi_so_g1}"
    assert phang_g1 is False

    # 3b. Lưới 9x10 = 90 ô cửa sổ đặc có biên mềm (cv2.rectangle thickness=-1 + blur nhẹ)
    img_dac = np.full((cao, rong, 3), (232, 236, 240), dtype=np.uint8)
    for hang in range(9):
        for cot in range(10):
            x0 = 70 + cot * 64
            y0 = 55 + hang * 58
            cv2.rectangle(img_dac, (x0, y0), (x0 + 14, y0 + 16), (28, 32, 38), -1)
    img_dac = cv2.GaussianBlur(img_dac, (3, 3), 0.8)

    phang_g2, _, chi_so_g2 = anh_do.do_dac_trung_phang(img_dac, d_raw, d_norm)
    assert chi_so_g2["so_ky_tu_ngang"] < anh_do.NGUONG_KY_TU_NGANG, f"Lưới ô đặc bị đếm nhầm: {chi_so_g2}"
    assert phang_g2 is False
