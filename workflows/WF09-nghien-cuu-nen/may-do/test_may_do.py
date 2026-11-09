"""Test máy đo WF09 (không gọi mạng). Chạy: python -m pytest -q may-do/"""
import json, subprocess, sys
from pathlib import Path

D = Path(__file__).parent
sys.path.insert(0, str(D))
import kiem_trich as kt  # noqa: E402


TRANG = "<html><body><p>Đào tạo, đào tạo lại, bồi dưỡng tối thiểu 500.000 người lao động về AI đến năm 2030.</p>" + "x " * 300 + "</body></html>"


def test_trich_rut_chu_bi_bat():
    # Trang ghi "bồi dưỡng tối thiểu 500.000", thợ chép bỏ "tối thiểu" và chèn **: không được tính là nguyên văn
    n, ty, thieu = kt.cham("Đào tạo, đào tạo lại, bồi dưỡng **500.000** người lao động", [500000], kt.van_ban(TRANG.encode(), "text/html"))
    assert n != "KHOP" and not thieu


def test_khop_nguyen_van():
    n, _, _ = kt.cham("bồi dưỡng tối thiểu 500.000 người lao động", [500000], kt.van_ban(TRANG.encode(), "text/html"))
    assert n == "KHOP"


def test_trich_bia():
    n, _, thieu = kt.cham("70% lao động có kỹ năng AI cơ bản theo dự thảo", [70], kt.van_ban(TRANG.encode(), "text/html"))
    assert n == "KHONG" and thieu == [70]


def test_so_sai():
    _, _, thieu = kt.cham("bồi dưỡng tối thiểu 500.000 người lao động", [50000], kt.van_ban(TRANG.encode(), "text/html"))
    assert thieu == [50000]


def test_khong_tai():
    assert kt.cham("gì cũng được", [1], "")[0] == "KHONG_TAI"


def chay(*a):
    return subprocess.run([sys.executable, str(D / "kiem_mat_so.py"), *a], capture_output=True, text=True)


def test_mat_so(tmp_path):
    (tmp_path / "t.md").write_text("Có 14,2 triệu người 60+ (2024). Tỷ lệ 11,9%. Quy mô 1.234.567 hộ.", encoding="utf-8")
    (tmp_path / "s.md").write_text("Có 14,2 triệu người 60+ (2024). Tỷ lệ 12,5%.", encoding="utf-8")
    bc = tmp_path / "bc.jsonl"
    bc.write_text(json.dumps({"so": [12.5]}) + "\n", encoding="utf-8")
    r = chay(str(tmp_path / "t.md"), str(tmp_path / "s.md"), "--bang-chung", str(bc))
    assert r.returncode == 1 and "1234567" in r.stdout and "11.9" in r.stdout
    r = chay(str(tmp_path / "t.md"), str(tmp_path / "s.md"), "--bang-chung", str(bc), "--cho-doi", "11,9;1.234.567")
    assert r.returncode == 0, r.stdout


def test_so_moi_khong_nguon(tmp_path):
    (tmp_path / "t.md").write_text("Tỷ lệ 11,9%.", encoding="utf-8")
    (tmp_path / "s.md").write_text("Tỷ lệ 11,9%. Thêm 37% người dùng.", encoding="utf-8")
    r = chay(str(tmp_path / "t.md"), str(tmp_path / "s.md"), "--bang-chung", str(tmp_path / "khong-co.jsonl"))
    assert r.returncode == 1 and "37" in r.stdout
