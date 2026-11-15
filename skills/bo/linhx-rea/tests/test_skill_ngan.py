"""Kiểm thử 5: `skills/rea-anh/SKILL.md` ngắn gọn ≤ 120 dòng và đủ các bước quy trình."""
from __future__ import annotations

from conftest import THU_MUC_SKILL


def test_skill_ngan() -> None:
    p_skill = THU_MUC_SKILL / "skills" / "rea-anh" / "SKILL.md"
    assert p_skill.is_file()

    noi_dung = p_skill.read_text(encoding="utf-8")
    so_dong = len(noi_dung.splitlines())
    assert 1 <= so_dong <= 120, f"SKILL.md vượt quá 120 dòng: {so_dong}"

    for tu_khoa in ("anh_do.py", "viec-doc", "ap", "ve_nguoc.py", "the", "tom"):
        assert tu_khoa in noi_dung
