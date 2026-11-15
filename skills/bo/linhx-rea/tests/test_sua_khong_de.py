"""Kiểm thử 10 (R5b): `rea_core.py sua <dir_ra>` ghi riêng từng thư mục ra, chạy 2 lần không nhân đôi và không mất mục cũ."""
from __future__ import annotations

import json
from pathlib import Path

import rea_core


def _doc_jsonl(path: Path) -> list[dict]:
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def _tao_muc_mau(dir_ra: Path, ten_muc: str, ten_anh: str, ds_ghi_chu: list[tuple[str, str]]) -> Path:
    muc = dir_ra / ten_muc
    rea_core.ghi_json(
        muc / "do.json",
        {
            "anh": ten_anh,
            "kich_thuoc": [640, 480],
            "mau": [{"hex": "#223344", "ti_le": 1.0}],
            "tong": {"kieu": "trung-tinh", "trung_binh": 0.45, "do_lech": 0.15},
            "hut_mat": [{"x": 0.50, "y": 0.50, "diem": 1.0}],
            "bo_cuc": {"khop_nhat": "mot_phan_ba", "mot_phan_ba": 0.8, "cheo": 0.3, "doi_xung": 0.4},
            "do_sau": {"ti_le": {"gan": 0.3, "giua": 0.3, "xa": 0.4}, "phang": False, "ly_do_phang": ""},
        },
    )
    rea_core.ghi_json(
        muc / "dap_an.json",
        {
            "anh": ten_anh,
            "trang_thai": "da_dien",
            "nguoi_doc": "pytest",
            "tra_loi": [
                {"ma": truc, "gia_tri": "chan_dung_nguoi", "ghi_chu": mo_ta, "moc": {"x": 0.50, "y": 0.50}}
                for truc, mo_ta in ds_ghi_chu
            ],
            "the_de_xuat": [],
        },
    )
    return muc


def test_sua_khong_ghi_de_giua_hai_dir_ra(tmp_path: Path) -> None:
    dir_a = tmp_path / "bo_a" / "ra"
    dir_b = tmp_path / "bo_b" / "ra"

    _tao_muc_mau(
        dir_a,
        "anh_a1",
        "anh_a1.jpg",
        [
            ("chu_the_chinh", "MAY-SAI: điểm hút mắt #1 lệch khỏi chủ thể chính tại x=0.50, y=0.50."),
            ("bo_cuc", "MAY-SAI: máy chấm mot_phan_ba nhưng thực tế bố cục đối xứng."),
        ],
    )
    _tao_muc_mau(
        dir_b,
        "anh_b1",
        "anh_b1.jpg",
        [
            ("mau", "MAY-SAI: bảng 6 màu thiếu sắc đỏ tại x=0.40, y=0.40."),
        ],
    )

    # Lần chạy 1 trên cả hai thư mục ra -> mỗi thư mục có file sua-sai.jsonl riêng biệt
    assert rea_core.main(["sua", str(dir_a)]) == 0
    assert rea_core.main(["sua", str(dir_b)]) == 0

    p_sua_a = dir_a / "sua-sai.jsonl"
    p_sua_b = dir_b / "sua-sai.jsonl"
    assert p_sua_a.is_file() and p_sua_b.is_file()

    muc_a_lan1 = _doc_jsonl(p_sua_a)
    muc_b_lan1 = _doc_jsonl(p_sua_b)
    assert len(muc_a_lan1) == 2
    assert len(muc_b_lan1) == 1
    assert all(x["anh"] == "anh_a1.jpg" for x in muc_a_lan1)
    assert all(x["anh"] == "anh_b1.jpg" for x in muc_b_lan1)

    # Lần chạy 2 trên cả hai thư mục -> không nhân đôi bản ghi, không ghi đè lẫn nhau
    assert rea_core.main(["sua", str(dir_a)]) == 0
    assert rea_core.main(["sua", str(dir_b)]) == 0
    assert len(_doc_jsonl(p_sua_a)) == 2
    assert len(_doc_jsonl(p_sua_b)) == 1

    # Thay đổi dap_an của dir_a (bỏ bớt 1 câu cũ, thêm 1 câu mới) -> chạy sua vẫn GIỮ mục cũ + nối mục mới
    _tao_muc_mau(
        dir_a,
        "anh_a1",
        "anh_a1.jpg",
        [
            ("khong_gian", "MAY-SAI: lop.png gộp nhầm tiền cảnh và trung cảnh."),
        ],
    )
    assert rea_core.main(["sua", str(dir_a)]) == 0
    muc_a_lan3 = _doc_jsonl(p_sua_a)
    assert len(muc_a_lan3) == 3

    # Chạy --kiem-lai cập nhật trạng thái tại chỗ và giữ đủ cả 3 mục
    assert rea_core.main(["sua", str(dir_a), "--kiem-lai"]) == 0
    muc_a_kiem_lai = _doc_jsonl(p_sua_a)
    assert len(muc_a_kiem_lai) == 3
    assert muc_a_kiem_lai[0]["trang_thai"] == "da_sua"
    assert muc_a_kiem_lai[1]["trang_thai"] == "mo"
    assert muc_a_kiem_lai[2]["trang_thai"] == "chua_kiem_duoc"
