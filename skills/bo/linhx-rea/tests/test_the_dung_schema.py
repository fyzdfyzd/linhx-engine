"""Kiểm thử 4: thẻ thủ pháp mẫu đúng schema được nhận, thẻ thiếu trường bắt buộc bị loại vào `the-loi.jsonl`."""
from __future__ import annotations

import json
from pathlib import Path

import rea_core


def test_the_dung_schema(tmp_path: Path) -> None:
    the_dung = {
        "ten": "Tương phản điểm nóng tại giao điểm một phần ba",
        "loai": "mau_sac",
        "moc": {"vung": "B3"},
        "mo_ta": "Nền lạnh trầm chiếm 80% diện tích đẩy khối ấm ở B3 thành tiêu điểm số 1.",
        "cach_lam": "Giữ 80% khung ở sắc lạnh tối, đặt chủ thể ấm bão hoà cao đúng ô B3.",
        "khi_dung": "Dùng cho keyframe cao trào hoặc poster cần gom mắt tức thì.",
        "nguon": "anh_tu_sinh_the.png",
    }
    the_thieu_truong = {
        "ten": "Thẻ lỗi cố tình thiếu cach_lam và khi_dung",
        "loai": "bo_cuc",
        "moc": {"x": 0.5, "y": 0.5},
        "mo_ta": "Thẻ này thiếu các trường bắt buộc để kiểm tra bộ lọc schema.",
        "nguon": "anh_tu_sinh_the.png",
    }

    assert rea_core.kiem_tra_the_thu_phap(the_dung, loai="anh") == []
    loi_kiem = rea_core.kiem_tra_the_thu_phap(the_thieu_truong, loai="anh")
    assert len(loi_kiem) >= 2

    # Kiểm qua lệnh `chay_the` trên thư mục tạm
    muc_anh = tmp_path / "anh_tu_sinh_the"
    rea_core.ghi_json(muc_anh / "do.json", {"anh": "anh_tu_sinh_the.png"})
    rea_core.ghi_json(
        muc_anh / "doc.json",
        {
            "do": {"anh": "anh_tu_sinh_the.png"},
            "doc": {
                "anh": "anh_tu_sinh_the.png",
                "nguoi_doc": "pytest",
                "tra_loi": [],
                "the_de_xuat": [the_dung, the_thieu_truong],
            },
            "xung_dot": [],
            "canh_bao": [],
        },
    )

    kq = rea_core.chay_the(tmp_path)
    assert len(kq["hop_le"]) == 1
    assert len(kq["the_loi"]) == 1
    assert kq["anh_thieu_the"] == []

    dong_hop_le = [
        json.loads(ln)
        for ln in (tmp_path / "thu-phap" / "thu-phap.jsonl").read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ]
    assert dong_hop_le == [the_dung]
    assert (tmp_path / "thu-phap" / "README.md").is_file()

    p_the_loi = tmp_path / "thu-phap" / "the-loi.jsonl"
    assert p_the_loi.is_file()
    dong_loi = [json.loads(ln) for ln in p_the_loi.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(dong_loi) == 1
    assert dong_loi[0]["the"]["ten"] == the_thieu_truong["ten"]
