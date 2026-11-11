"""Kiểm thử 1: `do.json` đủ trường R1+R2 + assert phụ hồi quy 2 lỗi R2 (độ sâu k-means 1D & hút mắt bỏ lề 4%)."""
from __future__ import annotations

import math
from pathlib import Path

import cv2
import numpy as np

import anh_do
import rea_core
import ve_nguoc
from conftest import sinh_anh_bau_troi_rong_va_vat_nho, sinh_anh_phoi_canh_co_diem_do_va_nhieu_le


def test_do_du_truong(tmp_path: Path) -> None:
    p_anh_1 = tmp_path / "vao" / "canh_1.png"
    p_anh_2 = tmp_path / "vao" / "canh_2.png"
    anh_do.ghi_anh(p_anh_1, sinh_anh_phoi_canh_co_diem_do_va_nhieu_le())
    anh_do.ghi_anh(p_anh_2, sinh_anh_bau_troi_rong_va_vat_nho())

    ra_1 = tmp_path / "ra" / "canh_1"
    ra_2 = tmp_path / "ra" / "canh_2"
    do_1 = anh_do.do_mot_anh(p_anh_1, ra_1)
    do_2 = anh_do.do_mot_anh(p_anh_2, ra_2)

    # 1. Đủ các khoá R1 + R2 trong do.json và đủ tệp đầu ra
    khoa_bat_buoc = {"anh", "kich_thuoc", "mau", "tong", "hut_mat", "bo_cuc", "do_sau", "ocr", "phien_ban"}
    on_disk = rea_core.doc_json(ra_1 / "do.json")
    assert khoa_bat_buoc.issubset(on_disk.keys())
    assert on_disk == do_1

    for fn in ("do.json", "do.png", "hut_mat.png", "depth.png", "lop.png"):
        assert (ra_1 / fn).is_file()

    assert on_disk["kich_thuoc"] == [480, 360]
    assert len(on_disk["tong"]["histogram"]) == 16
    assert on_disk["tong"]["kieu"] in {"high-key", "low-key", "tuong-phan-cao", "trung-tinh"}
    assert {"mot_phan_ba", "cheo", "doi_xung", "khop_nhat"}.issubset(on_disk["bo_cuc"].keys())
    assert {"co_cong_cu", "chu"}.issubset(on_disk["ocr"].keys())

    ds1 = on_disk["do_sau"]
    assert ds1["quy_uoc"] == "inverse_depth_lon_la_gan"
    assert len(ds1["nguong"]) == 2 and 0.0 < ds1["nguong"][0] < ds1["nguong"][1] < 1.0
    assert {"gan", "giua", "xa"} == set(ds1["ti_le"].keys())
    assert {"x", "y"} == set(ds1["vung_gan_tam"].keys())
    assert 0.0 <= ds1["vung_gan_tam"]["x"] <= 1.0 and 0.0 <= ds1["vung_gan_tam"]["y"] <= 1.0

    # Kiểm thêm ve_nguoc sinh đủ khoi.png (cạnh dài 1024), khung.png, prompt.md
    kq_vn = ve_nguoc.ve_nguoc_mot_anh(ra_1)
    khoi_img = anh_do.doc_anh_bgr(kq_vn["khoi"])
    assert max(khoi_img.shape[:2]) == 1024
    assert kq_vn["khung"].is_file() and kq_vn["prompt"].is_file()
    assert "chưa đọc" in kq_vn["prompt"].read_text(encoding="utf-8")

    # 2. Assert phụ hồi quy R2 #1: tỉ lệ độ sâu KHÔNG cố định [0.25, 0.35, 0.40], lớp gần sáng nhất (235 > 45)
    tl_r1_co_dinh = {"gan": 0.25, "giua": 0.35, "xa": 0.40}
    assert ds1["ti_le"] != tl_r1_co_dinh
    assert do_2["do_sau"]["ti_le"] != tl_r1_co_dinh
    assert ds1["ti_le"] != do_2["do_sau"]["ti_le"]

    depth_u8 = cv2.imdecode(np.frombuffer((ra_1 / "depth.png").read_bytes(), np.uint8), cv2.IMREAD_GRAYSCALE)
    lop_gray = cv2.cvtColor(anh_do.doc_anh_bgr(ra_1 / "lop.png"), cv2.COLOR_BGR2GRAY)
    vung_kiem = slice(48, None)  # bỏ qua hộp chú giải nhỏ góc trên-trái
    d_norm = depth_u8[vung_kiem, :].astype(np.float32) / 255.0
    lop_kiem = lop_gray[vung_kiem, :]
    t1, t2 = ds1["nguong"]
    if np.any(d_norm >= t2 + 0.02) and np.any(d_norm < t1 - 0.02):
        assert float(lop_kiem[d_norm >= t2 + 0.02].mean()) > float(lop_kiem[d_norm < t1 - 0.02].mean())

    # 3. Assert phụ hồi quy R2 #2: hút mắt loại bỏ hoàn toàn lề 4% mép và bắt đúng khối đỏ nổi bật ở tâm
    for hm_list in (on_disk["hut_mat"], do_2["hut_mat"]):
        assert len(hm_list) >= 1
        for pt in hm_list:
            assert 0.04 <= pt["x"] <= 0.96, f"Điểm hút mắt lọt vào lề 4% theo trục X: {pt}"
            assert 0.04 <= pt["y"] <= 0.96, f"Điểm hút mắt lọt vào lề 4% theo trục Y: {pt}"

    hm_dau = on_disk["hut_mat"][0]
    assert math.hypot(hm_dau["x"] - 0.50, hm_dau["y"] - 0.46) <= 0.12
