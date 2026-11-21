"""Nghiệm thu khoá: viec/neon-ab/sua/lich.py — doc_gio(chuoi, goc) -> datetime."""
import sys
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "sua"))
from lich import doc_gio  # noqa: E402

GOC = datetime(2026, 11, 21, 10, 0)  # thứ Bảy 21/11/2026 10:00


@pytest.mark.parametrize("chuoi, mong", [
    ("14:00", datetime(2026, 11, 21, 14, 0)),
    ("8h30", datetime(2026, 11, 22, 8, 30)),
    ("8h30 sáng mai", datetime(2026, 11, 22, 8, 30)),
    ("3h chiều", datetime(2026, 11, 21, 15, 0)),
    ("9 giờ tối nay", datetime(2026, 11, 21, 21, 0)),
    ("12h trưa", datetime(2026, 11, 21, 12, 0)),
    ("sáng mai", datetime(2026, 11, 22, 8, 0)),
    ("tối nay", datetime(2026, 11, 21, 19, 0)),
    ("21/11 14:00", datetime(2026, 11, 21, 14, 0)),
    ("1/12", datetime(2026, 12, 1, 9, 0)),
    ("5/1 7h", datetime(2027, 1, 5, 7, 0)),
    ("20/11", datetime(2027, 11, 20, 9, 0)),
    ("thứ 6", datetime(2026, 11, 27, 9, 0)),
    ("chiều thứ 2", datetime(2026, 11, 23, 14, 0)),
    ("chủ nhật 10h", datetime(2026, 11, 22, 10, 0)),
    ("thứ 7", datetime(2026, 11, 28, 9, 0)),
    ("ngày kia", datetime(2026, 11, 23, 9, 0)),
    ("2 tiếng nữa", datetime(2026, 11, 21, 12, 0)),
    ("30 phút nữa", datetime(2026, 11, 21, 10, 30)),
    ("thu 6", datetime(2026, 11, 27, 9, 0)),
    ("8h30 sang mai", datetime(2026, 11, 22, 8, 30)),
    ("  CHIỀU   Thứ 2 ", datetime(2026, 11, 23, 14, 0)),
    ("7h tối thứ 4", datetime(2026, 11, 25, 19, 0)),
])
def test_doc_gio(chuoi, mong):
    assert doc_gio(chuoi, GOC) == mong


@pytest.mark.parametrize("chuoi", ["abc", "25/13", "", "25:00", "thứ 9"])
def test_loi(chuoi):
    with pytest.raises(ValueError):
        doc_gio(chuoi, GOC)


def test_khong_doi_goc():
    g = datetime(2026, 11, 21, 10, 0)
    doc_gio("mai", g)
    assert g == datetime(2026, 11, 21, 10, 0)
    assert doc_gio("mai", g) == datetime(2026, 11, 22, 9, 0)
