"""Kiểm thử 7 (R4b): ảnh phẳng tự sinh (khối màu + chữ cv2.putText) -> phang=true, bo_cuc.json có ti_le cộng ≈ 1."""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

import anh_do
import rea_core
import ve_nguoc


def _sinh_poster_phang_tu_sinh(cao: int = 720, rong: int = 512) -> np.ndarray:
    # Nền kem phẳng đồng nhất (khoảng trống rộng)
    img = np.full((cao, rong, 3), (226, 238, 245), dtype=np.uint8)

    # Khối màu hình học phẳng (mảng hình)
    cv2.rectangle(img, (44, 300), (260, 520), (175, 72, 28), -1)
    cv2.rectangle(img, (280, 340), (468, 520), (42, 78, 208), -1)
    cv2.circle(img, (374, 430), 54, (226, 238, 245), -1)

    # Nhiều dòng chữ ngang nét mảnh rõ bằng cv2.putText
    cv2.putText(img, "REA ANH POSTER 2026", (42, 92), cv2.FONT_HERSHEY_SIMPLEX, 1.05, (28, 30, 34), 2, cv2.LINE_AA)
    cv2.putText(img, "DESIGN SYSTEM GRID LAYOUT", (42, 142), cv2.FONT_HERSHEY_SIMPLEX, 0.82, (28, 30, 34), 2, cv2.LINE_AA)
    cv2.putText(img, "TYPOGRAPHY & VISUAL STORY", (42, 188), cv2.FONT_HERSHEY_SIMPLEX, 0.80, (42, 78, 208), 2, cv2.LINE_AA)
    cv2.putText(img, "CONG NGHE X CON NGUOI", (42, 608), cv2.FONT_HERSHEY_SIMPLEX, 0.88, (28, 30, 34), 2, cv2.LINE_AA)
    cv2.putText(img, "HANOI - SAIGON EXHIBITION HALL A3", (42, 650), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (60, 62, 68), 1, cv2.LINE_AA)
    return img


def test_anh_phang_sinh_bo_cuc_json(tmp_path: Path) -> None:
    p_anh = tmp_path / "vao" / "poster_tu_sinh.png"
    ra_muc = tmp_path / "ra" / "poster_tu_sinh"
    anh_do.ghi_anh(p_anh, _sinh_poster_phang_tu_sinh())

    do_data = anh_do.do_mot_anh(p_anh, ra_muc)
    assert do_data["do_sau"]["phang"] is True, f"Ảnh poster tự sinh phải ra phang=True: {do_data['do_sau']}"
    assert str(do_data["do_sau"].get("ly_do_phang") or "").strip() != ""

    kq_vn = ve_nguoc.ve_nguoc_mot_anh(ra_muc)
    p_bo_cuc = ra_muc / "ve-nguoc" / "bo_cuc.json"
    assert p_bo_cuc.is_file()
    assert kq_vn.get("bo_cuc") == p_bo_cuc

    khoi_bgr = anh_do.doc_anh_bgr(kq_vn["khoi"])
    assert max(khoi_bgr.shape[:2]) == 1024

    bo_cuc = rea_core.doc_json(p_bo_cuc)
    ti_le = bo_cuc["ti_le"]
    assert set(ti_le.keys()) == {"chu", "hinh", "khoang_trong"}
    tong_ti_le = float(ti_le["chu"]) + float(ti_le["hinh"]) + float(ti_le["khoang_trong"])
    assert abs(tong_ti_le - 1.0) <= 0.01
    assert ti_le["chu"] > 0.0 and ti_le["hinh"] > 0.0 and ti_le["khoang_trong"] > 0.0
    assert isinstance(bo_cuc.get("khoi_chu_lon"), list) and len(bo_cuc["khoi_chu_lon"]) >= 1

    prompt_txt = kq_vn["prompt"].read_text(encoding="utf-8")
    assert "bo_cuc.json" in prompt_txt
    assert "khoang_trong" in prompt_txt
