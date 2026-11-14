from __future__ import annotations

import io
import json
import os
import shutil
import stat
import subprocess
import threading
import time
import uuid
from pathlib import Path

import pytest

from runner import cai_may, hang_doi_git, linhx_runner


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
    tm_goc = goc_viec / f"pytest-tmp-h4-{os.getpid()}-{uuid.uuid4().hex[:8]}"
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
    """Tao bare repo cuc bo co du runner/ tren main va nhanh hang-doi (khong goi mang)."""
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
    cac_tep_runner = [
        "linhx_runner.py",
        "hang_doi_git.py",
        "cai_may.py",
        "cai-may.ps1",
        "chay-an-tho.vbs",
        "agy-settings.json",
        "tho.env.example",
    ]
    for ten in cac_tep_runner:
        shutil.copy2(linhx_runner.GOC / ten, tm_runner_seed / ten)
    tm_mau_seed = tm_runner_seed / "phieu-mau"
    tm_mau_seed.mkdir(parents=True, exist_ok=True)
    shutil.copy2(linhx_runner.GOC / "phieu-mau" / "ping.md", tm_mau_seed / "ping.md")

    _git(["add", "-A"], seed)
    _git(["commit", "-m", "khoi tao main day du runner"], seed)
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


def _chay_cai_may_co_gia_lich(
    tmp_path: Path,
    may: str,
    thu_muc: str | Path,
    repo_url: str | Path,
    goc_gioi_han: str | Path,
    thu_muc_drive: str | Path,
    thu_muc_log: str | Path,
    ten_lich: str = "LINHX-HangDoi",
    agy_cmd: str = "agy-gia",
    so_phieu: int = 1,
    khong_chay_ngay: bool = False,
) -> dict:
    """Chay runner/cai-may.ps1 voi PowerShell mock Task Scheduler (hoac cai_may_python neu he thong khong co pwsh)."""
    ps_bin = cai_may.tim_powershell()
    if ps_bin is None:
        ket_qua_lich = {}
        cai_may.cai_may_python(
            may=may,
            thu_muc=thu_muc,
            repo_url=repo_url,
            goc_gioi_han=goc_gioi_han,
            thu_muc_drive=thu_muc_drive,
            thu_muc_log=thu_muc_log,
            ten_lich=ten_lich,
            agy_cmd=agy_cmd,
            so_phieu=so_phieu,
            khong_chay_ngay=khong_chay_ngay,
            dang_ky_lich_fn=lambda d: ket_qua_lich.update(d),
        )
        return ket_qua_lich

    tep_json_lich = tmp_path / f"lich-mock-{uuid.uuid4().hex[:8]}.json"
    tep_wrapper = tmp_path / f"goi-cai-may-{uuid.uuid4().hex[:8]}.ps1"
    cfg_in = {
        "ScriptCai": str(cai_may.DUONG_DAN_CAI_MAY_PS1),
        "TepJson": str(tep_json_lich),
        "May": str(may),
        "ThuMuc": str(thu_muc),
        "RepoUrl": str(repo_url),
        "GocGioiHan": str(goc_gioi_han),
        "ThuMucDrive": str(thu_muc_drive),
        "ThuMucLog": str(thu_muc_log),
        "TenLich": str(ten_lich),
        "AgyCmd": str(agy_cmd),
        "SoPhieu": int(so_phieu),
        "KhongChayNgay": bool(khong_chay_ngay),
    }
    tep_cfg_json = tmp_path / f"cfg-cai-{uuid.uuid4().hex[:8]}.json"
    tep_cfg_json.write_text(json.dumps(cfg_in, ensure_ascii=False), encoding="utf-8")

    ma_ps = f"""
$ErrorActionPreference = "Stop"
$c = Get-Content -LiteralPath '{str(tep_cfg_json).replace("'", "''")}' -Raw -Encoding UTF8 | ConvertFrom-Json
$global:__LichDaDangKy = @{{ Started = $false; StartedTasks = @() }}

function global:New-ScheduledTaskAction {{
    param([string]$Execute, [string]$Argument, [string]$WorkingDirectory)
    return [pscustomobject]@{{
        Execute = $Execute
        Argument = $Argument
        WorkingDirectory = $WorkingDirectory
    }}
}}

function global:New-ScheduledTaskTrigger {{
    param([switch]$Once, $At, [TimeSpan]$RepetitionInterval)
    return [pscustomobject]@{{
        Once = [bool]$Once
        At = [string]$At
        RepetitionIntervalMinutes = [double]$RepetitionInterval.TotalMinutes
    }}
}}

function global:New-ScheduledTaskPrincipal {{
    param([string]$UserId, [string]$LogonType, [string]$RunLevel)
    return [pscustomobject]@{{
        UserId = $UserId
        LogonType = $LogonType
        RunLevel = $RunLevel
    }}
}}

function global:New-ScheduledTaskSettingsSet {{
    param(
        [switch]$AllowStartIfOnBatteries,
        [switch]$DontStopIfGoingOnBatteries,
        [switch]$StartWhenAvailable,
        [string]$MultipleInstances,
        [TimeSpan]$ExecutionTimeLimit
    )
    return [pscustomobject]@{{
        AllowStartIfOnBatteries = [bool]$AllowStartIfOnBatteries
        DontStopIfGoingOnBatteries = [bool]$DontStopIfGoingOnBatteries
        StartWhenAvailable = [bool]$StartWhenAvailable
        MultipleInstances = $MultipleInstances
        ExecutionTimeLimitMinutes = [double]$ExecutionTimeLimit.TotalMinutes
    }}
}}

function global:Register-ScheduledTask {{
    param([string]$TaskName, $Action, $Trigger, $Principal, $Settings, [switch]$Force)
    $global:__LichDaDangKy.TaskName = $TaskName
    $global:__LichDaDangKy.Force = [bool]$Force
    $global:__LichDaDangKy.Action = $Action
    $global:__LichDaDangKy.Trigger = $Trigger
    $global:__LichDaDangKy.Principal = $Principal
    $global:__LichDaDangKy.Settings = $Settings
    return [pscustomobject]@{{ TaskName = $TaskName }}
}}

function global:Start-ScheduledTask {{
    param([string]$TaskName)
    $global:__LichDaDangKy.Started = $true
    $global:__LichDaDangKy.StartedTasks += $TaskName
}}

$thamSo = @{{
    May = [string]$c.May
    ThuMuc = [string]$c.ThuMuc
    RepoUrl = [string]$c.RepoUrl
    GocGioiHan = [string]$c.GocGioiHan
    ThuMucDrive = [string]$c.ThuMucDrive
    ThuMucLog = [string]$c.ThuMucLog
    TenLich = [string]$c.TenLich
    AgyCmd = [string]$c.AgyCmd
    SoPhieu = [int]$c.SoPhieu
}}
if ([bool]$c.KhongChayNgay) {{
    $thamSo["KhongChayNgay"] = $true
}}

& $c.ScriptCai @thamSo | Out-Null
$jsonOut = $global:__LichDaDangKy | ConvertTo-Json -Depth 6
[System.IO.File]::WriteAllText($c.TepJson, $jsonOut, (New-Object System.Text.UTF8Encoding($false)))
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
    return json.loads(tep_json_lich.read_text(encoding="utf-8"))


def _doc_cap_env_tu_tep(tep_env: Path) -> dict[str, str]:
    raw = tep_env.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf"), "tho.env khong duoc co UTF-8 BOM"
    ket_qua: dict[str, str] = {}
    for dong in raw.decode("utf-8").splitlines():
        s = dong.strip()
        if s and not s.startswith("#") and "=" in s:
            k, v = s.split("=", 1)
            ket_qua[k.strip()] = v.strip()
    return ket_qua


def test_cai_may_clone_tao_tho_env_va_dang_ky_lich_moi_phut_interactive(tmp_path):
    bare = _tao_bare_day_du_runner(tmp_path)
    goc_linhx = tmp_path / "linhx"
    tm_hang_doi = goc_linhx / "hang-doi"
    tm_drive = tmp_path / "drive"
    tm_log = goc_linhx / "linhx-runner" / "log"

    assert not tm_hang_doi.exists()
    lich = _chay_cai_may_co_gia_lich(
        tmp_path=tmp_path,
        may="may-1",
        thu_muc=tm_hang_doi,
        repo_url=bare,
        goc_gioi_han=goc_linhx,
        thu_muc_drive=tm_drive,
        thu_muc_log=tm_log,
        agy_cmd="agy-gia-test",
    )

    # 1. Da clone repo vao thu muc rieng hang-doi va cay git van sach (tho.env khong bi dua vao git)
    assert (tm_hang_doi / ".git").exists()
    assert _git(["status", "--porcelain"], tm_hang_doi) == ""

    # 2. Kiem tra tho.env du bien, khong chua token/bi mat
    tep_env = tm_hang_doi / "runner" / "tho.env"
    assert tep_env.is_file()
    kv = _doc_cap_env_tu_tep(tep_env)
    assert kv["LINHX_NGUON"] == "github"
    assert kv["LINHX_THO"] == "may-1"
    assert Path(kv["LINHX_REPO_HANG_DOI"]).resolve() == tm_hang_doi.resolve()
    assert Path(kv["LINHX_GIOI_HAN_THU_MUC"]).resolve() == goc_linhx.resolve()
    assert Path(kv["LINHX_THU_MUC"]).resolve().parent == (tm_hang_doi / "runner" / "viec").resolve()
    assert kv["AGY_CMD"] == "agy-gia-test"
    assert "--mode auto" in kv["AGY_ARGS"]
    assert "--sandbox" in kv["AGY_ARGS"]
    assert "--add-dir" in kv["AGY_ARGS"]
    assert "--settings" in kv["AGY_ARGS"]
    assert "LINHX_TOKEN" not in kv

    # 3. Kiem tra agy-settings.json duoc tao va gioi han trong goc_linhx
    tep_settings = tm_hang_doi / "runner" / "viec" / "agy-settings.json"
    assert tep_settings.is_file()
    st_json = json.loads(tep_settings.read_text(encoding="utf-8"))
    assert st_json["agentMode"] == "auto"
    allow = st_json["permissions"]["allow"]
    deny = st_json["permissions"]["deny"]
    assert "command(*)" in allow
    assert "mcp(browsentic/*)" in allow
    assert f"write_file({goc_linhx.as_posix()})" in allow
    assert "write_file(*)" not in allow
    assert "read_file(*)" not in allow
    assert any("tho.env" in r for r in deny)
    assert any("LINHX-ENGINE" in r for r in deny)

    # 4. Kiem tra Task Scheduler: MOI PHUT, CHI KHI USER DA DANG NHAP (Interactive), an qua chay-an-tho.vbs
    assert lich["TaskName"] == "LINHX-HangDoi"
    assert lich["Force"] is True
    assert lich["Started"] is True
    assert lich["Action"]["Execute"].lower() == "wscript.exe"
    assert "//B" in lich["Action"]["Argument"]
    assert "chay-an-tho.vbs" in lich["Action"]["Argument"]
    assert "--mot-lan" in lich["Action"]["Argument"]
    assert Path(lich["Action"]["WorkingDirectory"]).resolve() == (tm_hang_doi / "runner").resolve()
    assert lich["Trigger"]["Once"] is True
    assert lich["Trigger"]["RepetitionIntervalMinutes"] == 1.0
    assert lich["Principal"]["LogonType"] == "Interactive"
    assert lich["Principal"]["RunLevel"] == "Limited"
    assert lich["Settings"]["MultipleInstances"] == "IgnoreNew"
    assert lich["Settings"]["ExecutionTimeLimitMinutes"] == 0.0


def test_cai_may_idempotent_khi_repo_da_clone_san(tmp_path):
    bare = _tao_bare_day_du_runner(tmp_path)
    goc_linhx = tmp_path / "linhx"
    goc_linhx.mkdir(parents=True, exist_ok=True)
    tm_hang_doi = goc_linhx / "hang-doi"
    _git(["clone", str(bare), str(tm_hang_doi)], tmp_path)

    lich = _chay_cai_may_co_gia_lich(
        tmp_path=tmp_path,
        may="MAY-2",
        thu_muc=tm_hang_doi,
        repo_url="https://khong-goi-mang.invalid/repo.git",
        goc_gioi_han=goc_linhx,
        thu_muc_drive=tmp_path / "drive",
        thu_muc_log=goc_linhx / "log",
        khong_chay_ngay=True,
    )
    kv = _doc_cap_env_tu_tep(tm_hang_doi / "runner" / "tho.env")
    assert kv["LINHX_THO"] == "may-2"
    assert lich["Started"] is False
    assert _git(["status", "--porcelain"], tm_hang_doi) == ""


def test_cai_may_chan_linhx_engine_khong_phan_biet_hoa_thuong_va_ngoai_goc(tmp_path, monkeypatch):
    bare = _tao_bare_day_du_runner(tmp_path)
    goc_linhx = tmp_path / "linhx"

    # Kiem tra truc tiep trong Python (moi he dieu hanh)
    for duong_cam in [
        r"D:\LINHX\LINHX-ENGINE",
        r"d:\linhx\linhx-engine",
        r"D:/LiNhX/lInHx-EnGiNe/runner",
    ]:
        with pytest.raises(ValueError, match="LINHX-ENGINE"):
            cai_may.kiem_tra_tham_so_cai("may-1", thu_muc=duong_cam, goc_gioi_han=r"D:\linhx")

    # Chan thu muc nam ngoai goc_gioi_han hoac trung goc_gioi_han
    with pytest.raises(ValueError):
        cai_may.kiem_tra_tham_so_cai("may-1", thu_muc=tmp_path / "ngoai" / "hang-doi", goc_gioi_han=goc_linhx)
    with pytest.raises(ValueError):
        cai_may.kiem_tra_tham_so_cai("may-1", thu_muc=goc_linhx, goc_gioi_han=goc_linhx)
    with pytest.raises(ValueError):
        cai_may.kiem_tra_tham_so_cai("bat-ky", thu_muc=goc_linhx / "hang-doi", goc_gioi_han=goc_linhx)

    # Kiem tra PowerShell cai-may.ps1 cung chan D:\linhx\linhx-engine (khong phan biet hoa thuong)
    with pytest.raises((RuntimeError, ValueError), match="LINHX-ENGINE"):
        _chay_cai_may_co_gia_lich(
            tmp_path=tmp_path,
            may="may-1",
            thu_muc=r"d:\linhx\linhx-engine",
            repo_url=bare,
            goc_gioi_han=r"D:\linhx",
            thu_muc_drive=tmp_path / "drive",
            thu_muc_log=tmp_path / "log",
        )

    # Kiem tra nhanh fallback Python khi monkeypatch tim_powershell -> None
    monkeypatch.setattr(cai_may, "tim_powershell", lambda: None)
    lich_py = _chay_cai_may_co_gia_lich(
        tmp_path=tmp_path,
        may="may-3",
        thu_muc=goc_linhx / "hang-doi-py",
        repo_url=bare,
        goc_gioi_han=goc_linhx,
        thu_muc_drive=tmp_path / "drive",
        thu_muc_log=goc_linhx / "log-py",
    )
    assert lich_py["Principal"]["LogonType"] == "Interactive"
    assert lich_py["Trigger"]["RepetitionIntervalMinutes"] == 1.0


def test_agy_tu_chay_lenh_va_gioi_han_trong_d_linhx(tmp_path, monkeypatch):
    # 1. Kiem tra file runner/agy-settings.json trong repo
    tep_settings_goc = linhx_runner.GOC / "agy-settings.json"
    st = json.loads(tep_settings_goc.read_text(encoding="utf-8"))
    assert st["agentMode"] == "auto"
    allow = st["permissions"]["allow"]
    deny = st["permissions"]["deny"]
    assert "command(*)" in allow
    assert "mcp(browsentic/*)" in allow
    assert "read_file(D:/linhx)" in allow
    assert "write_file(D:/linhx)" in allow
    assert "edit_file(D:/linhx)" in allow
    assert not any(r in allow for r in ("read_file(*)", "write_file(*)", "read_file(/)", "write_file(/)"))
    assert any("LINHX-ENGINE" in r for r in deny)
    assert any("tho.env" in r for r in deny)

    # 2. Kiem tra runtime linhx_runner.chay_agy chan ngoai vung va chan D:\LINHX\LINHX-ENGINE
    da_goi_popen = []

    class _ProcGia:
        pid = 42424
        returncode = 0

        def __init__(self, cmd, cwd):
            da_goi_popen.append((list(cmd), str(cwd)))
            ket_qua_json = json.dumps({"status": "SUCCESS", "response": "OK", "usage": {"input_tokens": 8, "output_tokens": 4}})
            self.stdout = io.BytesIO(ket_qua_json.encode("utf-8"))
            self.stderr = io.BytesIO(b"")

        def poll(self):
            return 0

        def wait(self, timeout=None):
            return 0

    monkeypatch.setattr(
        linhx_runner,
        "_tao_tien_trinh_agy",
        lambda cmd, cwd=None, **kw: _ProcGia(cmd, cwd),
    )

    goc_cho_phep = tmp_path / "goc co dau cach"
    goc_cho_phep.mkdir(parents=True, exist_ok=True)
    tm_hop_le = goc_cho_phep / "viec-hop-le"
    tm_anh_em_gia_mao = tmp_path / "goc co dau cach-ngoai"
    tm_anh_em_gia_mao.mkdir(parents=True, exist_ok=True)

    # Chan thu muc gia mao cung tien to chuoi nhung nam ngoai goc_cho_phep
    tt_ngoai, _, nk_ngoai, _, _ = linhx_runner.chay_agy(
        {
            "tho": "may-1",
            "agy": "agy-gia",
            "agy_args": "--output-format json",
            "thu_muc": tm_anh_em_gia_mao,
            "gioi_han_thu_muc": goc_cho_phep,
        },
        {"viec": "v-ngoai", "de": "thu"},
    )
    assert tt_ngoai == "loi"
    assert "ngoài giới hạn" in nk_ngoai
    assert da_goi_popen == []

    # Chan D:\LINHX\LINHX-ENGINE khong phan biet hoa thuong ngay ca khi khong dat gioi_han_thu_muc
    tt_eng, _, nk_eng, _, _ = linhx_runner.chay_agy(
        {
            "tho": "may-1",
            "agy": "agy-gia",
            "agy_args": "--output-format json",
            "thu_muc": Path(r"d:\linhx\linhx-engine\viec"),
        },
        {"viec": "v-eng", "de": "thu"},
    )
    assert tt_eng == "loi"
    assert "LINHX-ENGINE" in nk_eng
    assert da_goi_popen == []

    # Cho phep thu muc ben trong goc_cho_phep va tach dung duong dan co dau cach trong AGY_ARGS
    tep_st_tam = goc_cho_phep / "agy-settings.json"
    tep_st_tam.write_text("{}", encoding="utf-8")
    agy_args = (
        f'--output-format json --mode auto --sandbox '
        f'--add-dir "{goc_cho_phep}" --settings "{tep_st_tam}"'
    )
    tt_ok, kq_ok, _, tv, tr = linhx_runner.chay_agy(
        {
            "tho": "may-1",
            "agy": "agy-gia",
            "agy_args": agy_args,
            "thu_muc": tm_hop_le,
            "gioi_han_thu_muc": goc_cho_phep,
        },
        {"viec": "v-ok", "de": "ping"},
    )
    assert tt_ok == "xong"
    assert kq_ok == "OK"
    assert (tv, tr) == (8, 4)
    assert len(da_goi_popen) == 1
    cmd_da_goi, cwd_da_goi = da_goi_popen[0]
    assert Path(cwd_da_goi).resolve() == tm_hop_le.resolve()
    assert "--mode" in cmd_da_goi and "auto" in cmd_da_goi
    assert "--sandbox" in cmd_da_goi
    assert str(goc_cho_phep) in cmd_da_goi
    assert str(tep_st_tam) in cmd_da_goi


def test_chay_an_tho_vbs_va_khoa_mot_tien_trinh(tmp_path, monkeypatch):
    noi_dung_vbs = (linhx_runner.GOC / "chay-an-tho.vbs").read_text(encoding="utf-8")
    assert ", 0, False" in noi_dung_vbs
    assert "--log tho.log" in noi_dung_vbs
    assert "WScript.Arguments" in noi_dung_vbs

    tep_khoa = tmp_path / "runner.lock"
    tep_log = tmp_path / "tho.log"
    tep_env = tmp_path / "tho.env"
    tep_env.write_text(
        f"LINHX_NGUON=github\nLINHX_THO=may-1\nLINHX_THU_MUC={tmp_path / 'viec'}\n",
        encoding="utf-8",
    )

    so_lan_chay_vong = []

    def gia_vong(cfg, mot_lan=False, mot_viec=False):
        so_lan_chay_vong.append((cfg["tho"], mot_lan, mot_viec))
        linhx_runner.log("tick-chay-ok")

    monkeypatch.setattr(linhx_runner, "vong", gia_vong)
    for bien in ("LINHX_NGUON", "LINHX_THO", "LINHX_THU_MUC"):
        monkeypatch.delenv(bien, raising=False)

    # Khi tien trinh truoc dang giu khoa, luot moi (1 phut sau) thoat ngay ma khong goi vong()
    with linhx_runner.khoa_mot_tien_trinh(tep_khoa) as da_giu:
        assert da_giu is True
        ma_thoat = linhx_runner.chay_cli(
            ["--mot-lan", "--log", str(tep_log), "--tep-khoa", str(tep_khoa)],
            tep_env=tep_env,
        )
        assert ma_thoat == 0
        assert so_lan_chay_vong == []

    # Sau khi tien trinh truoc nha khoa, luot ke tiep chay binh thuong va ghi vao tho.log
    ma_thoat_2 = linhx_runner.chay_cli(
        ["--mot-lan", "--log", str(tep_log), "--tep-khoa", str(tep_khoa)],
        tep_env=tep_env,
    )
    assert ma_thoat_2 == 0
    assert so_lan_chay_vong == [("may-1", True, False)]
    assert "tick-chay-ok" in tep_log.read_text(encoding="utf-8")


def test_phieu_mau_ping_chay_tron_vong_3_may_trong_3_phut(tmp_path, monkeypatch):
    # 1. Kiem tra phieu mau ping.md di kem
    assert hang_doi_git.DUONG_DAN_PHIEU_PING_MAU.is_file()
    nd_mau = hang_doi_git.DUONG_DAN_PHIEU_PING_MAU.read_text(encoding="utf-8")
    phieu_mau = hang_doi_git.phan_tich_phieu(nd_mau, "ping")
    assert phieu_mau["may"] == "bat-ky"
    assert phieu_mau["loai"] == "code"
    assert phieu_mau["tran_phut"] <= 3
    assert "PONG" in phieu_mau["de"]

    # 2. Tao bare repo co phieu ping cho may-1, may-2, may-3 va 1 phieu ping bat-ky tranh chap
    bare = _tao_bare_day_du_runner(
        tmp_path,
        {
            "ping-may-1": hang_doi_git.tao_phieu_ping("may-1"),
            "ping-may-2": hang_doi_git.tao_phieu_ping("may-2"),
            "ping-may-3": hang_doi_git.tao_phieu_ping("may-3"),
            "ping-chung": nd_mau,
        },
    )

    # Cai ca 3 may bang cai-may.ps1 vao cac thu muc rieng trong goc_linhx
    goc_linhx = tmp_path / "linhx"
    cau_hinh_may: dict[str, dict] = {}
    for ten_may in ("may-1", "may-2", "may-3"):
        tm_cai = goc_linhx / f"hang-doi-{ten_may}"
        _chay_cai_may_co_gia_lich(
            tmp_path=tmp_path,
            may=ten_may,
            thu_muc=tm_cai,
            repo_url=bare,
            goc_gioi_han=goc_linhx,
            thu_muc_drive=tmp_path / f"drive-{ten_may}",
            thu_muc_log=goc_linhx / f"log-{ten_may}",
            khong_chay_ngay=True,
        )
        # Nap dung tho.env ma cai-may.ps1 vua sinh ra
        for k in list(os.environ.keys()):
            if k.startswith("LINHX_") or k.startswith("AGY_"):
                monkeypatch.delenv(k, raising=False)
        cau_hinh_may[ten_may] = linhx_runner.doc_env(tm_cai / "runner" / "tho.env")

    lich_su_agy: list[tuple[str, str]] = []
    khoa_ls = threading.Lock()

    def gia_agy_ping(cfg, viec):
        # Xac nhan runtime van kiem tra thu_muc nam trong gioi_han_thu_muc
        ok_tm, ly_do = linhx_runner.kiem_tra_thu_muc_lam_viec(cfg["thu_muc"], cfg.get("gioi_han_thu_muc"))
        assert ok_tm, ly_do
        with khoa_ls:
            lich_su_agy.append((cfg["tho"], viec["viec"]))
        return "xong", f"PONG {cfg['tho']} {cfg['thu_muc']}", "ok", 18, 9

    monkeypatch.setattr(hang_doi_git, "chay_agy", gia_agy_ping)

    # 3. Cho 3 may chay song song nhu 3 may cong ty nhan lich moi phut -> xong het duoi 3 phut
    t0 = time.monotonic()
    loi_luong: list[Exception] = []

    def chay_mot_may(cfg_m):
        try:
            linhx_runner.vong(cfg_m, mot_lan=True)
        except Exception as e:
            loi_luong.append(e)

    cac_luong = [threading.Thread(target=chay_mot_may, args=(cau_hinh_may[m],)) for m in ("may-1", "may-2", "may-3")]
    for t in cac_luong:
        t.start()
    for t in cac_luong:
        t.join(timeout=60)
    thoi_gian_chay = time.monotonic() - t0

    assert loi_luong == []
    assert thoi_gian_chay < 180.0  # <= 3 phut

    # Kiem tra nhanh hang-doi tren remote: moi/ va dang/ rong, ca 4 KET-QUA.md <= 2000 ky tu
    tm_kiem = tmp_path / "kiem-nhanh-hang-doi"
    _git(["clone", "-b", "hang-doi", str(bare), str(tm_kiem)], tmp_path)
    assert list((tm_kiem / "hang-doi" / "moi").glob("*.md")) == []
    assert not (tm_kiem / "hang-doi" / "dang").exists() or list((tm_kiem / "hang-doi" / "dang").glob("*.md")) == []

    for ma_phieu, may_mong_doi in [
        ("ping-may-1", "may-1"),
        ("ping-may-2", "may-2"),
        ("ping-may-3", "may-3"),
    ]:
        tep_kq = tm_kiem / "hang-doi" / "xong" / ma_phieu / "KET-QUA.md"
        assert tep_kq.is_file()
        nd_kq = tep_kq.read_text(encoding="utf-8")
        assert len(nd_kq) <= 2000
        assert f"may: {may_mong_doi}\n" in nd_kq
        assert "trang_thai: xong\n" in nd_kq
        assert f"PONG {may_mong_doi}" in nd_kq

    # Phieu ping-chung (bat-ky) chi duoc dung 1 may nhan va xu ly
    may_nhan_chung = [m for m, v in lich_su_agy if v == "ping-chung"]
    assert len(may_nhan_chung) == 1
    tep_kq_chung = tm_kiem / "hang-doi" / "xong" / "ping-chung" / "KET-QUA.md"
    assert tep_kq_chung.is_file()
    assert len(tep_kq_chung.read_text(encoding="utf-8")) <= 2000
