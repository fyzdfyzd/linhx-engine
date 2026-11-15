from __future__ import annotations

import io
import json
import os
import subprocess
import time
import urllib.error
import uuid
from pathlib import Path
from types import SimpleNamespace

import pytest

from runner import bao_claude, hang_doi_git
from runner._gia_moi_truong import _gia_ram_va_moi_truong_h3  # noqa: F401  (fixture autouse, thay conftest)


@pytest.fixture(autouse=True)
def _bat_bao_claude_va_bo_ngu(monkeypatch, _gia_ram_va_moi_truong_h3):
    # Bat lai cong tac bao_claude cho file test nay sau khi fixture chung tat no
    monkeypatch.setenv("LINHX_BAO_CLAUDE", "1")
    monkeypatch.setattr(time, "sleep", lambda _s: None)
    monkeypatch.setattr(bao_claude, "_CHAY_LENH_FN", None)
    monkeypatch.setattr(bao_claude, "_URLOPEN_FN", None)


class _FakeHttpResponse:
    def __init__(self, status: int = 201, body: str = '{"id": 1}'):
        self.status = status
        self._body = body.encode("utf-8")

    def read(self) -> bytes:
        return self._body

    def getcode(self) -> int:
        return self.status

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def _run_git(args: list[str], cwd: Path) -> str:
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    kw = {"creationflags": 0x08000000} if os.name == "nt" else {}
    proc = subprocess.run(
        ["git"] + list(args),
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
        **kw,
    )
    return proc.stdout.strip()


def _create_bare_queue_repo(
    tmp_path: Path,
    initial_tickets: dict[str, str],
    finished_results: dict[str, str] | None = None,
) -> Path:
    bare_repo = tmp_path / f"remote-{uuid.uuid4().hex[:6]}.git"
    bare_repo.mkdir(parents=True)
    _run_git(["init", "--bare"], bare_repo)

    seed_repo = tmp_path / f"seed-{uuid.uuid4().hex[:6]}"
    seed_repo.mkdir()
    _run_git(["init"], seed_repo)
    _run_git(["config", "user.name", "seed"], seed_repo)
    _run_git(["config", "user.email", "seed@linhx.local"], seed_repo)
    _run_git(["config", "commit.gpgsign", "false"], seed_repo)

    _run_git(["checkout", "-b", "main"], seed_repo)
    (seed_repo / "README.md").write_text("linhx-engine\n", encoding="utf-8")
    _run_git(["add", "-A"], seed_repo)
    _run_git(["commit", "-m", "init main"], seed_repo)
    _run_git(["remote", "add", "origin", str(bare_repo)], seed_repo)
    _run_git(["push", "origin", "main"], seed_repo)
    _run_git(["symbolic-ref", "HEAD", "refs/heads/main"], bare_repo)

    _run_git(["checkout", "--orphan", "hang-doi"], seed_repo)
    _run_git(["rm", "-rf", "."], seed_repo)
    moi_dir = seed_repo / "hang-doi" / "moi"
    moi_dir.mkdir(parents=True, exist_ok=True)
    (moi_dir / ".gitkeep").write_text("", encoding="utf-8")
    for ticket_id, content in initial_tickets.items():
        (moi_dir / f"{ticket_id}.md").write_text(content, encoding="utf-8")
    for done_id, result_md in (finished_results or {}).items():
        done_file = seed_repo / "hang-doi" / "xong" / done_id / "KET-QUA.md"
        done_file.parent.mkdir(parents=True, exist_ok=True)
        done_file.write_text(result_md, encoding="utf-8")

    _run_git(["add", "-A"], seed_repo)
    _run_git(["commit", "-m", "init hang-doi"], seed_repo)
    _run_git(["push", "origin", "hang-doi"], seed_repo)
    return bare_repo


def _clone_worker_cfg(bare_repo: Path, tmp_path: Path, worker_name: str = "may-2", **extra_cfg) -> dict:
    clone_dir = tmp_path / f"clone-{worker_name}-{uuid.uuid4().hex[:4]}"
    _run_git(["clone", str(bare_repo), str(clone_dir)], tmp_path)
    work_dir = tmp_path / f"work-{worker_name}-{uuid.uuid4().hex[:4]}"
    work_dir.mkdir(parents=True, exist_ok=True)
    cfg = {
        "nguon": "github",
        "tho": worker_name,
        "agy": "agy-gia",
        "agy_args": "--output-format json",
        "thu_muc": work_dir,
        "nghi": 0.01,
        "repo_hang_doi": clone_dir,
        "nhanh_hang_doi": "hang-doi",
        "remote_hang_doi": "origin",
        "wt_hang_doi": "",
        "thu_muc_drive": tmp_path / f"drive-{worker_name}",
        "thu_muc_log": tmp_path / f"log-{worker_name}",
    }
    cfg.update(extra_cfg)
    return cfg


def _inspect_queue_branch(bare_repo: Path, tmp_path: Path, label: str = "inspect") -> Path:
    inspect_dir = tmp_path / label
    if inspect_dir.exists():
        _run_git(["fetch", "origin", "hang-doi"], inspect_dir)
        _run_git(["reset", "--hard", "origin/hang-doi"], inspect_dir)
    else:
        _run_git(["clone", "-b", "hang-doi", str(bare_repo), str(inspect_dir)], tmp_path)
    return inspect_dir


def test_bao_bang_gh_dung_mot_dong():
    cac_lenh: list[list[str]] = []

    def fake_run(cmd, **_kwargs):
        cac_lenh.append(list(cmd))
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    ok1 = bao_claude.bao("yl-code-a2", "co", "may-2", 12.4, chay_lenh_fn=fake_run, ngu_fn=lambda _s: None)
    ok2 = bao_claude.bao("yl-test-b1", "khong", "may-1", 0.6, chay_lenh_fn=fake_run, ngu_fn=lambda _s: None)
    ok3 = bao_claude.bao("lx-khan", "chua-ro", "may-4", None, chay_lenh_fn=fake_run, ngu_fn=lambda _s: None)

    assert ok1 is True and ok2 is True and ok3 is True
    assert cac_lenh == [
        ["gh", "auth", "status"],
        ["gh", "pr", "comment", "36", "-R", "fyzdfyzd/linhx-engine", "-b", "XONG yl-code-a2 dat=co may=may-2 phut=12"],
        ["gh", "auth", "status"],
        ["gh", "pr", "comment", "36", "-R", "fyzdfyzd/linhx-engine", "-b", "XONG yl-test-b1 dat=khong may=may-1 phut=1"],
        ["gh", "auth", "status"],
        ["gh", "pr", "comment", "36", "-R", "fyzdfyzd/linhx-engine", "-b", "XONG lx-khan dat=? may=may-4 phut=0"],
    ]
    for cmd in cac_lenh:
        for phan in cmd:
            assert "\n" not in phan and "\r" not in phan


def test_bao_fallback_rest_api_va_thu_lai_3_lan(tmp_path):
    khoa_gia = "gh" + "p_" + ("Ab3" * 8)
    tep_env = tmp_path / "tho.env"
    tep_env.write_text(f'LINHX_THO=may-2\nLINHX_GH_TOKEN="{khoa_gia}" # comment cuoi dong\n', encoding="utf-8")

    def fake_no_gh(_cmd, **_kwargs):
        raise FileNotFoundError("khong co gh")

    yeu_cau: list[tuple[str, str, dict, dict]] = []

    def fake_urlopen(req, timeout=30):
        yeu_cau.append(
            (
                req.full_url,
                req.get_method(),
                dict(req.header_items()),
                json.loads(req.data.decode("utf-8")),
            )
        )
        if len(yeu_cau) < 3:
            raise urllib.error.URLError("mang chap chon")
        return _FakeHttpResponse(201)

    ok = bao_claude.bao(
        "yl-a2-1b",
        "co",
        "may-2",
        8.6,
        tep_env=tep_env,
        chay_lenh_fn=fake_no_gh,
        urlopen_fn=fake_urlopen,
        ngu_fn=lambda _s: None,
    )
    assert ok is True
    assert len(yeu_cau) == 3
    url, method, headers, body = yeu_cau[-1]
    assert url == "https://api.github.com/repos/fyzdfyzd/linhx-engine/issues/36/comments"
    assert method == "POST"
    headers_lower = {k.lower(): v for k, v in headers.items()}
    assert headers_lower["authorization"] == f"Bearer {khoa_gia}"
    assert body == {"body": "XONG yl-a2-1b dat=co may=may-2 phut=9"}
    assert "\n" not in body["body"] and "\r" not in body["body"]

    # Loi HTTP ca 3 lan: thu lai dung 3 lan roi bo qua (tra False, khong nem ngoai le)
    so_lan_http_502 = 0

    def fake_502(req, timeout=30):
        nonlocal so_lan_http_502
        so_lan_http_502 += 1
        raise urllib.error.HTTPError(req.full_url, 502, "Bad Gateway", {}, io.BytesIO(b"bad gateway"))

    ok_fail = bao_claude.bao(
        "yl-loi-mang",
        "khong",
        "may-2",
        5,
        tep_env=tep_env,
        chay_lenh_fn=fake_no_gh,
        urlopen_fn=fake_502,
        ngu_fn=lambda _s: None,
    )
    assert ok_fail is False
    assert so_lan_http_502 == 3

    # Thieu ca gh lan LINHX_GH_TOKEN -> bo qua an toan, tra False
    tep_rong = tmp_path / "tho-rong.env"
    tep_rong.write_text("LINHX_THO=may-2\n", encoding="utf-8")
    assert bao_claude.bao("yl-thieu-token", "?", "may-2", 0, tep_env=tep_rong, chay_lenh_fn=fake_no_gh) is False


def test_khong_bao_phieu_lx_thuong_nhung_bao_khi_co_header_hoac_cong_claude(tmp_path, monkeypatch):
    da_bao_gui: list[str] = []

    def fake_run_gh(cmd, **_kwargs):
        if cmd[:3] == ["gh", "auth", "status"]:
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        if cmd[:3] == ["gh", "pr", "comment"]:
            da_bao_gui.append(cmd[cmd.index("-b") + 1])
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        raise AssertionError(f"Lenh khong mong doi: {cmd}")

    monkeypatch.setattr(bao_claude, "_CHAY_LENH_FN", fake_run_gh)

    # 1. Phieu lx- thuong, moi/ chi co phieu khong phai cong Claude -> KHONG bao
    bare1 = _create_bare_queue_repo(
        tmp_path,
        {
            "lx-code-thuong": "may: may-2\nloai: code\n\nLam viec thuong.",
            "lx-cho-khac": "may: may-2\nloai: code\nphu_thuoc: lx-code-thuong\n\nCho viec thuong.",
        },
    )
    cfg1 = _clone_worker_cfg(bare1, tmp_path, "may-2")
    kq1 = hang_doi_git.xu_ly_mot_phieu(cfg1, chay_agy_fn=lambda _c, _v: ("xong", "dat: co", "ok", 10, 5))
    assert kq1 is not None and kq1["trang_thai"] == "xong"
    assert da_bao_gui == []
    insp1 = _inspect_queue_branch(bare1, tmp_path, "insp1")
    assert (insp1 / "hang-doi" / "xong" / "lx-code-thuong" / "KET-QUA.md").is_file()
    assert not (insp1 / "hang-doi" / "xong" / "lx-code-thuong" / ".da-bao").exists()

    # 2. Phieu lx- co header `bao: claude` -> CO bao
    bare2 = _create_bare_queue_repo(
        tmp_path,
        {
            "lx-code-khan": "may: may-2\nloai: code\nbao: claude\n\nCan Claude xem ngay.",
        },
    )
    cfg2 = _clone_worker_cfg(bare2, tmp_path, "may-2")
    kq2 = hang_doi_git.xu_ly_mot_phieu(cfg2, chay_agy_fn=lambda _c, _v: ("xong", "dat: co", "ok", 10, 5))
    assert kq2 is not None and kq2["trang_thai"] == "xong"
    assert len(da_bao_gui) == 1
    assert da_bao_gui[0].startswith("XONG lx-code-khan dat=co may=may-2 phut=")
    insp2 = _inspect_queue_branch(bare2, tmp_path, "insp2")
    assert (insp2 / "hang-doi" / "xong" / "lx-code-khan" / ".da-bao").is_file()

    # 3. Phieu lx- thuong ket thuc khi trong moi/ co phieu phu_thuoc vao yl-khoa-t1 hoac yl-duyet-* chua xong -> CO bao
    da_bao_gui.clear()
    bare3 = _create_bare_queue_repo(
        tmp_path,
        {
            "lx-code-phu": "may: may-2\nloai: code\n\nXong viec phu.",
            "yl-code-a2": "may: may-2\nloai: code\nphu_thuoc: yl-duyet-rc6\n\nCho Claude duyet.",
        },
    )
    cfg3 = _clone_worker_cfg(bare3, tmp_path, "may-2")
    kq3 = hang_doi_git.xu_ly_mot_phieu(cfg3, chay_agy_fn=lambda _c, _v: ("xong", "Xong phan phu.", "ok", 10, 5))
    assert kq3 is not None and kq3["trang_thai"] == "xong"
    assert len(da_bao_gui) == 1
    assert da_bao_gui[0].startswith("XONG lx-code-phu dat=? may=may-2 phut=")

    # 4. Khi yl-khoa-t1 da co trong xong/ -> phieu lx- tiep theo KHONG bao nua
    da_bao_gui.clear()
    bare4 = _create_bare_queue_repo(
        tmp_path,
        {
            "lx-code-sau": "may: may-2\nloai: code\n\nViec sau khi da mo khoa.",
            "yl-code-a2": "may: may-2\nloai: code\nphu_thuoc: yl-khoa-t1\n\nDa co khoa.",
        },
        finished_results={"yl-khoa-t1": "phieu: yl-khoa-t1\nmay: claude\ntrang_thai: xong\ndat: co\n"},
    )
    cfg4 = _clone_worker_cfg(bare4, tmp_path, "may-2")
    kq4 = hang_doi_git.xu_ly_mot_phieu(cfg4, chay_agy_fn=lambda _c, _v: ("xong", "dat: co", "ok", 10, 5))
    assert kq4 is not None and kq4["trang_thai"] == "xong"
    assert da_bao_gui == []


def test_phieu_sua_khong_bao_luot_dung_chi_bao_luot_cuoi(tmp_path, monkeypatch):
    da_bao_gui: list[str] = []

    def fake_run_gh(cmd, **_kwargs):
        if cmd[:3] == ["gh", "auth", "status"]:
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        if cmd[:3] == ["gh", "pr", "comment"]:
            da_bao_gui.append(cmd[cmd.index("-b") + 1])
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        raise AssertionError(f"Lenh khong mong doi: {cmd}")

    monkeypatch.setattr(bao_claude, "_CHAY_LENH_FN", fake_run_gh)

    bare = _create_bare_queue_repo(
        tmp_path,
        {
            "yl-code-tu-sua": "may: may-2\nloai: code\ntu_sua: 1\n\nSua loi lan 1.",
        },
    )
    cfg = _clone_worker_cfg(bare, tmp_path, "may-2")

    # Luot 1 dung: sinh yl-code-tu-sua-sua-1 -> KHONG bao
    kq1 = hang_doi_git.xu_ly_mot_phieu(cfg, chay_agy_fn=lambda _c, _v: ("dung", "dung giua chung", "dung", 1, 1))
    assert kq1 is not None and kq1["viec"] == "yl-code-tu-sua"
    assert da_bao_gui == []
    insp = _inspect_queue_branch(bare, tmp_path, "insp-sua-1")
    assert not (insp / "hang-doi" / "xong" / "yl-code-tu-sua" / ".da-bao").exists()
    assert (insp / "hang-doi" / "moi" / "yl-code-tu-sua-sua-1.md").is_file()

    # Luot 2 (luot cuoi) ket thuc -> BAO dung 1 lan
    kq2 = hang_doi_git.xu_ly_mot_phieu(cfg, chay_agy_fn=lambda _c, _v: ("xong", "dat: co\nDa sua xong.", "ok", 10, 5))
    assert kq2 is not None and kq2["viec"] == "yl-code-tu-sua-sua-1"
    assert len(da_bao_gui) == 1
    assert da_bao_gui[0].startswith("XONG yl-code-tu-sua-sua-1 dat=co may=may-2 phut=")
    insp2 = _inspect_queue_branch(bare, tmp_path, "insp-sua-2")
    assert (insp2 / "hang-doi" / "xong" / "yl-code-tu-sua-sua-1" / ".da-bao").is_file()

    # Neu luot cuoi cua -sua- ket thuc `loi` (het tu_sua) -> BAO dung 1 lan voi dat=khong
    da_bao_gui.clear()
    bare_loi = _create_bare_queue_repo(
        tmp_path,
        {
            "yl-code-het-sua": "may: may-2\nloai: code\ntu_sua: 1\n\nHet luot tu sua.",
        },
    )
    cfg_loi = _clone_worker_cfg(bare_loi, tmp_path, "may-2")
    hang_doi_git.xu_ly_mot_phieu(cfg_loi, chay_agy_fn=lambda _c, _v: ("loi", "loi luot 1", "loi", 1, 1))
    assert da_bao_gui == []
    kq_cuoi = hang_doi_git.xu_ly_mot_phieu(cfg_loi, chay_agy_fn=lambda _c, _v: ("loi", "loi luot cuoi", "loi", 1, 1))
    assert kq_cuoi is not None and kq_cuoi["viec"] == "yl-code-het-sua-sua-1"
    assert len(da_bao_gui) == 1
    assert da_bao_gui[0].startswith("XONG yl-code-het-sua-sua-1 dat=khong may=may-2 phut=")


def test_chong_lap_khong_bao_hai_lan(tmp_path, monkeypatch):
    da_bao_gui: list[str] = []

    def fake_run_gh(cmd, **_kwargs):
        if cmd[:3] == ["gh", "auth", "status"]:
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        if cmd[:3] == ["gh", "pr", "comment"]:
            da_bao_gui.append(cmd[cmd.index("-b") + 1])
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        raise AssertionError(f"Lenh khong mong doi: {cmd}")

    monkeypatch.setattr(bao_claude, "_CHAY_LENH_FN", fake_run_gh)

    # Kiem truc tiep bao(..., thu_muc_xong=...) chong lap
    tm_xong = tmp_path / "xong-truc-tiep"
    assert bao_claude.bao("yl-truc-tiep", "co", "may-2", 3, thu_muc_xong=tm_xong) is True
    assert bao_claude.bao("yl-truc-tiep", "co", "may-2", 3, thu_muc_xong=tm_xong) is False
    assert len(da_bao_gui) == 1
    assert (tm_xong / "yl-truc-tiep" / ".da-bao").is_file()

    # Kiem qua hang_doi_git: bao_ket_qua_git goi lai lan 2 van khong gui them
    da_bao_gui.clear()
    bare = _create_bare_queue_repo(
        tmp_path,
        {"yl-test-lap": "may: may-2\nloai: test\n\nKiem tra chong lap."},
    )
    cfg = _clone_worker_cfg(bare, tmp_path, "may-2")
    kq = hang_doi_git.xu_ly_mot_phieu(cfg, chay_agy_fn=lambda _c, _v: ("xong", "dat: co", "ok", 10, 5))
    assert kq is not None and len(da_bao_gui) == 1

    hang_doi_git.bao_ket_qua_git(
        cfg,
        {"viec": "yl-test-lap", "may": "may-2", "loai": "test", "meta": {}},
        trang_thai="xong",
        ket_qua="dat: co",
        phut=1.0,
    )
    assert len(da_bao_gui) == 1


def test_token_khong_xuat_hien_trong_log_va_loi_mang_khong_lam_hong_phieu(tmp_path, monkeypatch, capsys):
    khoa_gia = "gh" + "p_" + ("Zx8" * 8)
    tep_env = tmp_path / "tho.env"
    tep_env.write_text(f"LINHX_THO=may-2\nLINHX_GH_TOKEN={khoa_gia}\n", encoding="utf-8")

    def fake_gh_leaks_secret(_cmd, **_kwargs):
        # Gia lap gh that bai nhung stdout/stderr vo tinh dinh chuoi khoa
        return SimpleNamespace(returncode=1, stdout=f"Authorization: Bearer {khoa_gia}", stderr=khoa_gia)

    so_lan_http = 0

    def fake_http_loi_dinh_token(req, timeout=30):
        nonlocal so_lan_http
        so_lan_http += 1
        raise urllib.error.URLError(f"khong ket noi duoc voi Bearer {khoa_gia}")

    monkeypatch.setattr(bao_claude, "_CHAY_LENH_FN", fake_gh_leaks_secret)
    monkeypatch.setattr(bao_claude, "_URLOPEN_FN", fake_http_loi_dinh_token)

    bare = _create_bare_queue_repo(
        tmp_path,
        {"yl-an-toan-token": "may: may-2\nloai: code\n\nKiem che token khi loi mang."},
    )
    cfg = _clone_worker_cfg(bare, tmp_path, "may-2", tep_env=tep_env)

    kq = hang_doi_git.xu_ly_mot_phieu(cfg, chay_agy_fn=lambda _c, _v: ("xong", "dat: co\nHoan tat.", "ok", 10, 5))
    assert kq is not None
    assert kq["trang_thai"] == "xong"
    assert so_lan_http == 3

    insp = _inspect_queue_branch(bare, tmp_path, "insp-token")
    ket_qua_md = (insp / "hang-doi" / "xong" / "yl-an-toan-token" / "KET-QUA.md").read_text(encoding="utf-8")
    assert "trang_thai: xong" in ket_qua_md
    assert not (insp / "hang-doi" / "xong" / "yl-an-toan-token" / ".da-bao").exists()

    captured = capsys.readouterr()
    assert khoa_gia not in captured.out
    assert khoa_gia not in captured.err
    assert khoa_gia not in ket_qua_md
    log_dir = Path(cfg["thu_muc_log"])
    for tep_log in log_dir.rglob("*"):
        if tep_log.is_file():
            assert khoa_gia not in tep_log.read_text(encoding="utf-8", errors="replace")
