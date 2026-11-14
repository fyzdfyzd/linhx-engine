from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import uuid
from pathlib import Path

import pytest

from runner import cai_may, hang_doi_git, linhx_runner
from runner._gia_moi_truong import _gia_ram_va_moi_truong_h3  # noqa: F401  (fixture autouse, thay conftest)


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
    tm_goc = goc_viec / f"pytest-tmp-nbk-{os.getpid()}-{uuid.uuid4().hex[:8]}"
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


def _tao_bare_day_du_runner(tmp_path: Path, phieu_moi: dict[str, str] | None = None) -> Path:
    # Tạo bare repo cục bộ có đủ runner/ trên main và nhánh hang-doi
    bare = tmp_path / f"remote-{uuid.uuid4().hex[:6]}.git"
    bare.mkdir(parents=True)
    _git(["init", "--bare"], bare)

    seed = tmp_path / f"seed-{uuid.uuid4().hex[:6]}"
    seed.mkdir()
    _git(["init"], seed)
    _git(["config", "user.name", "seed"], seed)
    _git(["config", "user.email", "seed@linhx.local"], seed)
    _git(["config", "commit.gpgsign", "false"], seed)
    _git(["checkout", "-b", "main"], seed)

    (seed / ".gitignore").write_text(
        "runner/tho.env\nrunner/viec/\nrunner/tho.log\n__pycache__/\n*pytest-tmp*/\n",
        encoding="utf-8",
    )
    tm_runner_seed = seed / "runner"
    tm_runner_seed.mkdir(parents=True, exist_ok=True)
    for ten in [
        "linhx_runner.py",
        "hang_doi_git.py",
        "cai_may.py",
        "cai-may.ps1",
        "chay-an-tho.vbs",
        "agy-settings.json",
        "tho.env.example",
    ]:
        shutil.copy2(linhx_runner.GOC / ten, tm_runner_seed / ten)
    tm_mau_seed = tm_runner_seed / "phieu-mau"
    tm_mau_seed.mkdir(parents=True, exist_ok=True)
    shutil.copy2(linhx_runner.GOC / "phieu-mau" / "ping.md", tm_mau_seed / "ping.md")

    _git(["add", "-A"], seed)
    _git(["commit", "-m", "khoi tao main"], seed)
    _git(["remote", "add", "origin", str(bare)], seed)
    _git(["push", "origin", "main"], seed)
    _git(["symbolic-ref", "HEAD", "refs/heads/main"], bare)

    _git(["checkout", "--orphan", "hang-doi"], seed)
    _git(["rm", "-rf", "."], seed)
    tm_moi = seed / "hang-doi" / "moi"
    tm_moi.mkdir(parents=True, exist_ok=True)
    (tm_moi / ".gitkeep").write_text("", encoding="utf-8")
    for ten_phieu, noi_dung in (phieu_moi or {}).items():
        (tm_moi / f"{ten_phieu}.md").write_text(noi_dung, encoding="utf-8")
    _git(["add", "-A"], seed)
    _git(["commit", "-m", "khoi tao hang-doi"], seed)
    _git(["push", "origin", "hang-doi"], seed)
    return bare


def _doc_cap_env_tu_tep(tep_env: Path) -> dict[str, str]:
    ket_qua: dict[str, str] = {}
    for dong in tep_env.read_text(encoding="utf-8").splitlines():
        s = dong.strip()
        if s and not s.startswith("#") and "=" in s:
            k, v = s.split("=", 1)
            ket_qua[k.strip()] = v.strip()
    return ket_qua


def _chay_cai_may_ps1_gia_lich(
    tmp_path: Path,
    may: str,
    thu_muc: Path,
    repo_url: Path,
    goc_gioi_han: Path,
    chi_dich_danh: bool = False,
):
    ps_bin = cai_may.tim_powershell()
    if ps_bin is None:
        return cai_may.cai_may_python(
            may=may,
            thu_muc=thu_muc,
            repo_url=repo_url,
            goc_gioi_han=goc_gioi_han,
            thu_muc_drive=tmp_path / "drive",
            thu_muc_log=goc_gioi_han / "log",
            agy_cmd="agy-gia",
            khong_chay_ngay=True,
            chi_dich_danh=chi_dich_danh,
        )

    tep_cfg_json = tmp_path / f"cfg-{uuid.uuid4().hex[:8]}.json"
    tep_wrapper = tmp_path / f"goi-{uuid.uuid4().hex[:8]}.ps1"
    cfg_in = {
        "ScriptCai": str(cai_may.DUONG_DAN_CAI_MAY_PS1),
        "May": str(may),
        "ThuMuc": str(thu_muc),
        "RepoUrl": str(repo_url),
        "GocGioiHan": str(goc_gioi_han),
        "ThuMucDrive": str(tmp_path / "drive"),
        "ThuMucLog": str(goc_gioi_han / "log"),
        "AgyCmd": "agy-gia",
        "ChiDichDanh": bool(chi_dich_danh),
    }
    tep_cfg_json.write_text(json.dumps(cfg_in, ensure_ascii=False), encoding="utf-8")

    ma_ps = f"""
$ErrorActionPreference = "Stop"
$c = Get-Content -LiteralPath '{str(tep_cfg_json).replace("'", "''")}' -Raw -Encoding UTF8 | ConvertFrom-Json
function global:New-ScheduledTaskAction {{ param([string]$Execute, [string]$Argument, [string]$WorkingDirectory) return @{{}} }}
function global:New-ScheduledTaskTrigger {{ param([switch]$Once, $At, [TimeSpan]$RepetitionInterval) return @{{}} }}
function global:New-ScheduledTaskPrincipal {{ param([string]$UserId, [string]$LogonType, [string]$RunLevel) return @{{}} }}
function global:New-ScheduledTaskSettingsSet {{
    param([switch]$AllowStartIfOnBatteries, [switch]$DontStopIfGoingOnBatteries, [switch]$StartWhenAvailable, [string]$MultipleInstances, [TimeSpan]$ExecutionTimeLimit)
    return @{{}}
}}
function global:Register-ScheduledTask {{ param([string]$TaskName, $Action, $Trigger, $Principal, $Settings, [switch]$Force) return @{{}} }}
function global:Start-ScheduledTask {{ param([string]$TaskName) }}

$thamSo = @{{
    May = [string]$c.May
    ThuMuc = [string]$c.ThuMuc
    RepoUrl = [string]$c.RepoUrl
    GocGioiHan = [string]$c.GocGioiHan
    ThuMucDrive = [string]$c.ThuMucDrive
    ThuMucLog = [string]$c.ThuMucLog
    AgyCmd = [string]$c.AgyCmd
    KhongChayNgay = $true
}}
if ([bool]$c.ChiDichDanh) {{
    $thamSo["ChiDichDanh"] = $true
}}
& $c.ScriptCai @thamSo | Out-Null
"""
    tep_wrapper.write_bytes(b"\xef\xbb\xbf" + ma_ps.encode("utf-8"))
    kw = {"creationflags": 0x08000000} if os.name == "nt" else {}
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    p = subprocess.run(
        [ps_bin, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(tep_wrapper)],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        **kw,
    )
    if p.returncode != 0:
        raise RuntimeError(f"cai-may.ps1 loi ({p.returncode}): {(p.stderr or p.stdout).strip()}")


def test_chon_ung_vien_mac_dinh_nhan_bat_ky_va_tat_khi_dat_0(tmp_path, monkeypatch):
    # Kiểm tra trực tiếp hàm chon_ung_vien với mặc định (1) và khi đặt LINHX_NHAN_BAT_KY=0
    wt = tmp_path / "wt"
    tm_moi = wt / "hang-doi" / "moi"
    tm_moi.mkdir(parents=True)
    (tm_moi / "01-bat-ky.md").write_text("may: bat-ky\nloai: code\n\nViệc chung 1\n", encoding="utf-8")
    (tm_moi / "02-khong-ghi-may.md").write_text("loai: code\n\nViệc mặc định bất kỳ\n", encoding="utf-8")
    (tm_moi / "03-sao.md").write_text("may: *\nloai: code\n\nViệc dấu sao\n", encoding="utf-8")
    (tm_moi / "04-may-2.md").write_text("may: may-2\nloai: code\n\nViệc máy 2\n", encoding="utf-8")
    (tm_moi / "05-may-1.md").write_text("may: MAY-1\nloai: code\n\nViệc đích danh máy 1\n", encoding="utf-8")

    # Mặc định (LINHX_NHAN_BAT_KY=1): nhận phiếu riêng trước rồi tới các phiếu bat-ky
    assert hang_doi_git.co_nhan_bat_ky() is True
    uv_mac_dinh = [v["viec"] for _, v in hang_doi_git.chon_ung_vien(wt, "may-1")]
    assert uv_mac_dinh == ["05-may-1", "01-bat-ky", "02-khong-ghi-may", "03-sao"]

    # Đặt qua biến môi trường LINHX_NHAN_BAT_KY=0 -> chỉ nhận 05-may-1
    monkeypatch.setenv("LINHX_NHAN_BAT_KY", "0")
    assert hang_doi_git.co_nhan_bat_ky() is False
    uv_env_0 = [v["viec"] for _, v in hang_doi_git.chon_ung_vien(wt, "may-1")]
    assert uv_env_0 == ["05-may-1"]
    assert hang_doi_git.chon_ung_vien(wt, "may-3") == []

    # Đặt qua cfg ghi đè biến môi trường
    assert [v["viec"] for _, v in hang_doi_git.chon_ung_vien(wt, "may-1", cfg={"nhan_bat_ky": 1})] == uv_mac_dinh
    monkeypatch.setenv("LINHX_NHAN_BAT_KY", "1")
    assert [v["viec"] for _, v in hang_doi_git.chon_ung_vien(wt, "may-1", cfg={"nhan_bat_ky": 0})] == ["05-may-1"]


def test_cai_may_co_chi_dich_danh_va_chay_hang_doi_git(tmp_path, monkeypatch):
    bare = _tao_bare_day_du_runner(
        tmp_path,
        {
            "01-chung": "may: bat-ky\nloai: code\n\nPhiếu bất kỳ cho máy chung",
            "02-dich-danh-may1": "may: may-1\nloai: code\n\nPhiếu riêng máy 1",
            "03-khong-ghi-may": "loai: code\n\nPhiếu không ghi may (mặc định bat-ky)",
        },
    )
    goc_linhx = tmp_path / "linhx"

    # 1. Kiểm tra cai_may.py trực tiếp (cả mặc định và chi_dich_danh=True)
    nd_env_thuong = cai_may.tao_noi_dung_tho_env(
        may="may-2",
        thu_muc_repo=goc_linhx / "hd-2",
        thu_muc_lam_viec=goc_linhx / "hd-2" / "runner" / "viec" / "lam-viec",
        goc_gioi_han=goc_linhx,
        tep_settings=goc_linhx / "hd-2" / "runner" / "viec" / "agy-settings.json",
    )
    assert "LINHX_NHAN_BAT_KY=1" in nd_env_thuong.splitlines()

    tm_py = goc_linhx / "hang-doi-py"
    cai_may.cai_may_python(
        may="may-py",
        thu_muc=tm_py,
        repo_url=bare,
        goc_gioi_han=goc_linhx,
        thu_muc_drive=tmp_path / "drive-py",
        thu_muc_log=goc_linhx / "log-py",
        agy_cmd="agy-gia",
        khong_chay_ngay=True,
        chi_dich_danh=True,
    )
    kv_py = _doc_cap_env_tu_tep(tm_py / "runner" / "tho.env")
    assert kv_py["LINHX_NHAN_BAT_KY"] == "0"

    # 2. Cài may-1 bằng cai-may.ps1 -ChiDichDanh và may-2 mặc định (không có -ChiDichDanh)
    tm_may1 = goc_linhx / "hang-doi-may-1"
    _chay_cai_may_ps1_gia_lich(
        tmp_path=tmp_path,
        may="may-1",
        thu_muc=tm_may1,
        repo_url=bare,
        goc_gioi_han=goc_linhx,
        chi_dich_danh=True,
    )
    kv_m1 = _doc_cap_env_tu_tep(tm_may1 / "runner" / "tho.env")
    assert kv_m1["LINHX_NHAN_BAT_KY"] == "0"

    tm_may2 = goc_linhx / "hang-doi-may-2"
    _chay_cai_may_ps1_gia_lich(
        tmp_path=tmp_path,
        may="may-2",
        thu_muc=tm_may2,
        repo_url=bare,
        goc_gioi_han=goc_linhx,
        chi_dich_danh=False,
    )
    kv_m2 = _doc_cap_env_tu_tep(tm_may2 / "runner" / "tho.env")
    assert kv_m2["LINHX_NHAN_BAT_KY"] == "1"

    # Nạp cấu hình từ tho.env vừa sinh cho may-1 và may-2
    for k in list(os.environ.keys()):
        if k.startswith("LINHX_") or k.startswith("AGY_"):
            monkeypatch.delenv(k, raising=False)
    cfg_m1 = linhx_runner.doc_env(tm_may1 / "runner" / "tho.env")
    assert cfg_m1["nhan_bat_ky"] is False

    for k in list(os.environ.keys()):
        if k.startswith("LINHX_") or k.startswith("AGY_"):
            monkeypatch.delenv(k, raising=False)
    cfg_m2 = linhx_runner.doc_env(tm_may2 / "runner" / "tho.env")
    assert cfg_m2["nhan_bat_ky"] is True

    da_chay: list[tuple[str, str]] = []

    def gia_agy(cfg, viec):
        da_chay.append((cfg["tho"], viec["viec"]))
        return "xong", f"{cfg['tho']}:{viec['viec']}", "ok", 10, 5

    monkeypatch.setattr(hang_doi_git, "chay_agy", gia_agy)

    # may-1 chạy hết vòng: chỉ nhận 02-dich-danh-may1, bỏ qua cả 2 phiếu bat-ky
    linhx_runner.vong(cfg_m1, mot_lan=True)
    assert da_chay == [("may-1", "02-dich-danh-may1")]
    assert hang_doi_git.nhan_phieu_git(cfg_m1) is None

    # 2 phiếu bat-ky vẫn còn nguyên trong hang-doi/moi/ để may-2 (mặc định = 1) nhận tiếp
    linhx_runner.vong(cfg_m2, mot_lan=True)
    assert [v for m, v in da_chay if m == "may-2"] == ["01-chung", "03-khong-ghi-may"]


def test_theo_doi_thu_muc_ngoai_tinh_la_tien(tmp_path):
    """Phieu ghi theo_doi: thay doi o thu muc ngoai (repo clone rieng) lam doi dau nhip tien do."""
    from runner import linhx_runner as lr
    ngoai = tmp_path / "repo"
    ngoai.mkdir()
    tm = tmp_path / "lam-viec"
    tm.mkdir()
    td = lr._thu_muc_theo_doi({"theo_doi": f"{ngoai}; {tmp_path / 'khong-co'}"})
    assert td == (str(ngoai),)
    dem = [0, 0]
    a = lr._dau_nhip_tien_do(tm, dem, None, td)
    (ngoai / "index.html").write_text("x", encoding="utf-8")
    b = lr._dau_nhip_tien_do(tm, dem, None, td)
    assert a != b
