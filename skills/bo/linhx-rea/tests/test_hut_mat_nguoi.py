"""Kiểm thử 6 (R4a): hút mắt bị kéo về vùng mặt khi truyền hộp mặt giả vào hàm trộn (không cần YuNet)."""
from __future__ import annotations

import numpy as np

import anh_do


def _sinh_anh_co_nhieu_xa_va_vung_mat_gia(cao: int = 360, rong: int = 480) -> np.ndarray:
    img = np.full((cao, rong, 3), (38, 42, 46), dtype=np.uint8)
    # Vùng nhiễu màu vàng cam rực ở góc trái-trên làm saliency R2 gốc đặt #1 ở bên trái
    img[65:125, 80:145] = (15, 215, 250)
    # Vùng chân dung trung tính dịu ở bên phải (hop=[0.68, 0.22, 0.80, 0.44])
    x0, x1 = int(0.68 * rong), int(0.80 * rong)
    y0, y1 = int(0.22 * cao), int(0.44 * cao)
    img[y0:y1, x0:x1] = (118, 128, 138)
    return img


def test_hut_mat_bi_keo_ve_hop_mat_gia() -> None:
    img = _sinh_anh_co_nhieu_xa_va_vung_mat_gia()

    # 1. Không có hộp mặt -> giữ nguyên saliency R2 (bị hút về mảng màu rực bên trái x < 0.40)
    sal_r2 = anh_do.tinh_saliency_r2(img)
    sal_khong_mat, than_rong = anh_do.tron_hut_mat_nguoi(sal_r2, [])
    assert than_rong == []
    assert np.allclose(sal_khong_mat, sal_r2)
    hm_goc = anh_do.trich_dinh_hut_mat(sal_r2)
    assert hm_goc[0]["x"] < 0.40

    # 2. Truyền hộp mặt giả + landmark mắt/miệng vào hàm trộn độc lập (không gọi YuNet)
    hop_mat_gia = [
        {
            "hop": [0.68, 0.22, 0.80, 0.44],
            "diem": 0.95,
            "mat_trai": [0.76, 0.30],
            "mat_phai": [0.71, 0.30],
            "mieng": [0.74, 0.39],
        }
    ]
    sal_moi, ds_than = anh_do.tron_hut_mat_nguoi(sal_r2, hop_mat_gia)
    hm_moi = anh_do.trich_dinh_hut_mat(sal_moi)

    # Vùng thân ước lượng rộng ≈ 3× mặt (0.36), cao ≈ 4× mặt xuống dưới (cắt tại 1.0)
    assert len(ds_than) == 1
    tx0, ty0, tx1, ty1 = ds_than[0]
    assert abs((tx1 - tx0) - 0.36) <= 0.02
    assert abs(ty0 - 0.44) <= 0.01 and ty1 == 1.0

    # Điểm hút mắt #1 bị kéo thẳng về vùng hộp mặt giả ở bên phải
    hm1 = hm_moi[0]
    assert 0.68 <= hm1["x"] <= 0.80, f"Điểm hút mắt #1 chưa kéo vào hộp mặt theo X: {hm1}"
    assert 0.22 <= hm1["y"] <= 0.44, f"Điểm hút mắt #1 chưa kéo vào hộp mặt theo Y: {hm1}"
