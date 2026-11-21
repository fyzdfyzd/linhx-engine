from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import uuid
from pathlib import Path

import pytest

from runner import hang_doi_git, linhx_runner
from runner._gia_moi_truong import _gia_ram_va_moi_truong_h3  # noqa: F401  (fixture autouse, thay conftest)


BANG_MAU = {
    "_huong_dan": "5 bảng việc LAB133. uu_tien 1 = làm trước.",
    "cap_nhat": "2026-11-21T22:30:00+07:00",
    "bang": [
        {"ma": "cts", "ten": "OPC Chiêm Tinh Số", "uu_tien": 1, "day_chuyen": "dev", "han": "2026-12-01", "bu": "chiemtinhso"},
        {"ma": "ev", "ten": "ifAgent Event", "uu_tien": 2, "day_chuyen": "dev", "bu": "ifagent"},
        {"ma": "mq", "ten": "Máy quét thành MCP", "uu_tien": 3, "day_chuyen": "research", "bu": "linhx"},
        {"ma": "om", "ten": "Own media BU", "uu_tien": 4, "day_chuyen": "craft", "bu": "nhieu"},
        {"ma": "tv", "ten": "Decent AI TUVA", "uu_tien": 5, "day_chuyen": "research", "bu": "tuva"},
        {"ma": "ht", "ten": "Hạ tầng cụm", "uu_tien": 0, "day_chuyen": "dev", "bu": "linhx"},
    ],
    "day_chuyen": {"craft": "may-3", "dev": "may-2", "research": "may-1"},
}


def _xoa_thu_muc(duong_dan: Path):
    if not duong_dan.exists():
        return

    def _xu_ly_loi(fn, p, _):
        try:
            os.chmod(p, stat.S_IWRITE)
            fn(p)
        except OSError:
            pass

    shutil.rmtree(duong_dan, onerror=_xu_ly_loi)


@pytest.fixture
def tmp_path():
    goc_viec = linhx_runner.GOC / "viec"
    viec_da_co = goc_viec.exists()
    tm_goc = goc_viec / f"pytest-tmp-utb-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    tm_goc.mkdir(parents=True, exist_ok=True)
    try:
        yield tm_goc
    finally:
        _xoa_thu_muc(tm_goc)
        if not viec_da_co and goc_viec.exists():
            try:
                next(goc_viec.iterdir())
            except StopIteration:
                goc_viec.rmdir()


def _git(args, cwd):
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    kw = {"creationflags": 0x08000000} if os.name == "nt" else {}
    p = subprocess.run(
        ["git"] + list(args),
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        **kw,
    )
    return p.stdout.strip()


def _ghi_phieu(tm_moi: Path, ten_phieu: str, may: str = "bat-ky", loai: str = "code") -> Path:
    tm_moi.mkdir(parents=True, exist_ok=True)
    tep = tm_moi / f"{ten_phieu}.md"
    tep.write_text(f"may: {may}\nloai: {loai}\n\nNoi dung {ten_phieu}\n", encoding="utf-8")
    return tep


def test_bang_thieu_giu_nguyen_thu_tu_cu(tmp_path):
    tep_bang = tmp_path / "khong-ton-tai" / "bang.json"
    dau_vao = ["tv-code-1.md", "ht-code-1.md", "aaa-khac.md", "cts-code-1.md"]
    assert hang_doi_git.sap_xep_phieu_theo_bang(dau_vao, tep_bang) == dau_vao

    wt = tmp_path / "wt"
    tm_moi = wt / "hang-doi" / "moi"
    for ten in ["tv-code-1", "ht-code-1", "aaa-khac", "cts-code-1"]:
        _ghi_phieu(tm_moi, ten)
    chon = [v["viec"] for _, v in hang_doi_git.chon_ung_vien(wt, "may-2")]
    assert chon == ["aaa-khac", "cts-code-1", "ht-code-1", "tv-code-1"]


def test_bang_json_hong_giu_nguyen_thu_tu_cu(tmp_path):
    dau_vao = ["om-code-1.md", "ht-code-1.md", "cts-code-1.md"]
    cac_mau_hong = [
        "{json hong cu phap",
        "",
        "[1, 2, 3]",
        json.dumps({"bang": "khong-phai-list"}),
        json.dumps(
            {
                "bang": [
                    {"ma": "ht", "uu_tien": True},
                    {"ma": "cts", "uu_tien": "khong-phai-so"},
                    {"ma": "om", "uu_tien": None},
                    {"ma": "", "uu_tien": 0},
                ]
            }
        ),
    ]
    for idx, noi_dung in enumerate(cac_mau_hong):
        tep_bang = tmp_path / f"bang-hong-{idx}.json"
        tep_bang.write_text(noi_dung, encoding="utf-8")
        assert hang_doi_git.sap_xep_phieu_theo_bang(dau_vao, tep_bang) == dau_vao

    wt = tmp_path / "wt"
    tm_moi = wt / "hang-doi" / "moi"
    for ten in ["om-code-1", "ht-code-1", "cts-code-1"]:
        _ghi_phieu(tm_moi, ten)
    (wt / "hang-doi" / "bang.json").write_text("{hong", encoding="utf-8")
    chon = [v["viec"] for _, v in hang_doi_git.chon_ung_vien(wt, "may-2")]
    assert chon == ["cts-code-1", "ht-code-1", "om-code-1"]


def test_uu_tien_0_dung_dau_va_tang_dan(tmp_path):
    tep_bang = tmp_path / "bang.json"
    tep_bang.write_text(json.dumps(BANG_MAU, ensure_ascii=False), encoding="utf-8")
    dau_vao = [
        Path("tv-kiem-5.md"),
        Path("om-code-4.md"),
        Path("mq-code-3.md"),
        Path("ev-code-2.md"),
        Path("cts-code-1.md"),
        Path("ht-code-0.md"),
    ]
    ket_qua = [p.name for p in hang_doi_git.sap_xep_phieu_theo_bang(dau_vao, tep_bang)]
    assert ket_qua == [
        "ht-code-0.md",
        "cts-code-1.md",
        "ev-code-2.md",
        "mq-code-3.md",
        "om-code-4.md",
        "tv-kiem-5.md",
    ]


def test_cung_uu_tien_giu_thu_tu_cu(tmp_path):
    tep_bang = tmp_path / "bang.json"
    tep_bang.write_text(
        json.dumps(
            {
                "bang": [
                    {"ma": "cts", "uu_tien": 1},
                    {"ma": "ev", "uu_tien": 1},
                    {"ma": "om", "uu_tien": 3},
                ]
            }
        ),
        encoding="utf-8",
    )
    dau_vao = [
        "om-code-1.md",
        "cts-code-b.md",
        "ev-code-2.md",
        "cts-code-a.md",
        "ev-code-1.md",
    ]
    assert hang_doi_git.sap_xep_phieu_theo_bang(dau_vao, tep_bang) == [
        "cts-code-b.md",
        "ev-code-2.md",
        "cts-code-a.md",
        "ev-code-1.md",
        "om-code-1.md",
    ]

    wt = tmp_path / "wt"
    (wt / "hang-doi").mkdir(parents=True)
    (wt / "hang-doi" / "bang.json").write_text(tep_bang.read_text(encoding="utf-8"), encoding="utf-8")
    tm_moi = wt / "hang-doi" / "moi"
    for ten in ["om-code-1", "cts-code-b", "ev-code-2", "cts-code-a", "ev-code-1"]:
        _ghi_phieu(tm_moi, ten)
    chon = [v["viec"] for _, v in hang_doi_git.chon_ung_vien(wt, "may-2")]
    assert chon == ["cts-code-a", "cts-code-b", "ev-code-1", "ev-code-2", "om-code-1"]


def test_phieu_khong_thuoc_bang_xep_sau_cung(tmp_path):
    tep_bang = tmp_path / "bang.json"
    tep_bang.write_text(json.dumps(BANG_MAU, ensure_ascii=False), encoding="utf-8")
    dau_vao = [
        "aaa-ngoai-1.md",
        "html-kiem-1.md",
        "tv-kiem-1.md",
        "neon-code-2.md",
        "ht-code-1.md",
        "cts-code-1.md",
    ]
    assert hang_doi_git.sap_xep_phieu_theo_bang(dau_vao, tep_bang) == [
        "ht-code-1.md",
        "cts-code-1.md",
        "tv-kiem-1.md",
        "aaa-ngoai-1.md",
        "html-kiem-1.md",
        "neon-code-2.md",
    ]


def test_chon_ung_vien_va_nhan_phieu_git_theo_bang(tmp_path, monkeypatch):
    bare = tmp_path / "remote.git"
    bare.mkdir(parents=True)
    _git(["init", "--bare"], bare)

    seed = tmp_path / "seed"
    seed.mkdir()
    _git(["init"], seed)
    _git(["config", "user.name", "seed"], seed)
    _git(["config", "user.email", "seed@linhx.local"], seed)
    _git(["config", "commit.gpgsign", "false"], seed)
    _git(["checkout", "-b", "main"], seed)
    (seed / "README.md").write_text("linhx-engine\n", encoding="utf-8")
    _git(["add", "-A"], seed)
    _git(["commit", "-m", "khoi tao main"], seed)
    _git(["remote", "add", "origin", str(bare)], seed)
    _git(["push", "origin", "main"], seed)
    _git(["symbolic-ref", "HEAD", "refs/heads/main"], bare)

    _git(["checkout", "--orphan", "hang-doi"], seed)
    _git(["rm", "-rf", "."], seed)
    tm_hd = seed / "hang-doi"
    tm_moi = tm_hd / "moi"
    tm_moi.mkdir(parents=True, exist_ok=True)
    (tm_hd / "bang.json").write_text(json.dumps(BANG_MAU, ensure_ascii=False), encoding="utf-8")
    for ten in ["aaa-ngoai-1", "om-code-1", "cts-code-1", "ht-code-1"]:
        _ghi_phieu(tm_moi, ten, may="bat-ky", loai="code")
    _git(["add", "-A"], seed)
    _git(["commit", "-m", "khoi tao hang-doi"], seed)
    _git(["push", "origin", "hang-doi"], seed)

    clone_may2 = tmp_path / "may-2"
    _git(["clone", str(bare), str(clone_may2)], tmp_path)
    tm_viec = tmp_path / "viec-may-2"
    tm_viec.mkdir(parents=True, exist_ok=True)
    cfg = {
        "nguon": "github",
        "tho": "may-2",
        "so_phieu": 10,
        "agy": "agy-gia",
        "agy_args": "--output-format json",
        "thu_muc": tm_viec,
        "nghi": 0.01,
        "repo_hang_doi": clone_may2,
        "nhanh_hang_doi": "hang-doi",
        "remote_hang_doi": "origin",
        "wt_hang_doi": "",
        "thu_muc_drive": tmp_path / "drive",
        "thu_muc_log": tmp_path / "log",
    }
    monkeypatch.setattr(hang_doi_git, "lay_moc_head", lambda *_a, **_kw: "")

    wt = hang_doi_git.dam_bao_worktree(cfg)
    assert wt is not None
    assert [v["viec"] for _, v in hang_doi_git.chon_ung_vien(wt, "may-2", cfg=cfg)] == [
        "ht-code-1",
        "cts-code-1",
        "om-code-1",
        "aaa-ngoai-1",
    ]

    thu_tu_nhan = []
    while True:
        viec = hang_doi_git.nhan_phieu_git(cfg)
        if viec is None:
            break
        thu_tu_nhan.append(viec["viec"])

    assert thu_tu_nhan == ["ht-code-1", "cts-code-1", "om-code-1", "aaa-ngoai-1"]
