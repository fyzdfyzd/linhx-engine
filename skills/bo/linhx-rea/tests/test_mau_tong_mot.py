"""Kiểm thử 2: bảng 6 màu k-means có tổng `ti_le` xấp xỉ 1 (±0.01)."""
from __future__ import annotations

import re
from pathlib import Path

import cv2
import numpy as np

import anh_do


def test_mau_tong_mot(tmp_path: Path) -> None:
    cao, rong = 300, 420
    img = np.zeros((cao, rong, 3), dtype=np.uint8)
    # Chia 6 miền màu khác nhau kèm chuyển sắc nhẹ
    bang_bgr = [
        (30, 40, 210),
        (190, 95, 35),
        (55, 175, 70),
        (45, 200, 235),
        (165, 55, 155),
        (235, 235, 230),
    ]
    buoc = rong // 6
    for idx, bgr in enumerate(bang_bgr):
        x0 = idx * buoc
        x1 = rong if idx == 5 else (idx + 1) * buoc
        img[:, x0:x1] = bgr
    img = cv2.GaussianBlur(img, (7, 7), 1.5)

    p_anh = tmp_path / "anh_6_mau.png"
    anh_do.ghi_anh(p_anh, img)

    ket_qua = anh_do.do_mot_anh(p_anh, tmp_path / "ra_mau")
    ds_mau = ket_qua["mau"]

    assert len(ds_mau) == 6
    mau_hex_re = re.compile(r"^#[0-9a-f]{6}$")
    for muc in ds_mau:
        assert mau_hex_re.match(muc["hex"])
        assert 0.0 <= float(muc["ti_le"]) <= 1.0

    tong_ti_le = sum(float(m["ti_le"]) for m in ds_mau)
    assert abs(tong_ti_le - 1.0) <= 0.01
