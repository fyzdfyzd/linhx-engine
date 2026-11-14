"""Ho tro cai may nhan viec qua hang doi GitHub (runner/cai-may.ps1)."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

try:
    from runner import linhx_runner
except ImportError:
    import linhx_runner

THU_MUC_MAC_DINH = r"D:\linhx\hang-doi"
GOC_GIOI_HAN_MAC_DINH = r"D:\linhx"
THU_MUC_DRIVE_MAC_DINH = r"G:\My Drive\LINHX-VIEC"
THU_MUC_LOG_MAC_DINH = r"D:\linhx\linhx-runner\log"
TEN_LICH_MAC_DINH = "LINHX-HangDoi"
REPO_URL_MAC_DINH = "https://github.com/fyzdfyzd/linhx-engine.git"
DUONG_DAN_CAI_MAY_PS1 = linhx_runner.GOC / "cai-may.ps1"

_MAU_TEN_MAY = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


def _chuan_hoa_win(duong_dan: str | Path) -> str:
    s = str(duong_dan or "").strip().replace("/", "\\")
    while "\\\\" in s:
        s = s.replace("\\\\", "\\")
    if len(s) > 3:
        s = s.rstrip("\\")
    return s


def kiem_tra_tham_so_cai(
    may: str,
    thu_muc: str | Path = THU_MUC_MAC_DINH,
    goc_gioi_han: str | Path = GOC_GIOI_HAN_MAC_DINH,
    so_phieu: int = 1,
) -> tuple[str, str, str]:
    """Kiem tra va chuan hoa (may_chuan, thu_muc_chuan, goc_chuan). Sai thi nem ValueError."""
    may_chuan = str(may or "").strip().lower()
    if not _MAU_TEN_MAY.match(may_chuan) or may_chuan in ("bat-ky", "all", "tat-ca"):
        raise ValueError(f"Tên máy không hợp lệ: '{may}' (dùng may-1, may-2, may-3, ...; không dùng bat-ky).")
    if int(so_phieu) < 1:
        raise ValueError(f"SoPhieu phải >= 1 (nhận được: {so_phieu}).")

    cam = r"d:\linhx\linhx-engine"
    raw_tm = _chuan_hoa_win(thu_muc)
    if raw_tm.lower() == cam or raw_tm.lower().startswith(cam + "\\"):
        raise ValueError(
            f"KHÔNG dùng '{thu_muc}': trùng 'D:\\LINHX\\LINHX-ENGINE' "
            r"(Windows không phân biệt hoa thường, trùng repo đang chạy thợ ENGINE). Hãy dùng D:\linhx\hang-doi."
        )

    la_win_ao_tren_posix = os.name != "nt" and (
        linhx_runner._la_duong_dan_win_tuyet_doi(str(thu_muc).strip())
        or linhx_runner._la_duong_dan_win_tuyet_doi(str(goc_gioi_han).strip())
    )
    if la_win_ao_tren_posix:
        tm_s = _chuan_hoa_win(thu_muc)
        gh_s = _chuan_hoa_win(goc_gioi_han)
        if tm_s.lower() == gh_s.lower() or not tm_s.lower().startswith(gh_s.lower() + "\\"):
            raise ValueError(
                f"Thư mục cài '{tm_s}' phải nằm bên trong gốc giới hạn '{gh_s}' (ví dụ D:\\linhx\\hang-doi)."
            )
        return may_chuan, tm_s, gh_s

    tm_full = str(Path(thu_muc).resolve())
    gh_full = str(Path(goc_gioi_han).resolve())
    tm_win = _chuan_hoa_win(tm_full)
    if tm_win.lower() == cam or tm_win.lower().startswith(cam + "\\"):
        raise ValueError(
            f"KHÔNG dùng '{thu_muc}': trùng 'D:\\LINHX\\LINHX-ENGINE' "
            r"(Windows không phân biệt hoa thường, trùng repo đang chạy thợ ENGINE). Hãy dùng D:\linhx\hang-doi."
        )

    tm_nc = os.path.normcase(tm_full)
    gh_nc = os.path.normcase(gh_full)
    try:
        chung = os.path.commonpath([gh_nc, tm_nc])
    except ValueError as e:
        raise ValueError(
            f"Thư mục cài '{tm_full}' phải nằm bên trong gốc giới hạn '{gh_full}'."
        ) from e
    if tm_nc == gh_nc or chung != gh_nc:
        raise ValueError(
            f"Thư mục cài '{tm_full}' phải nằm bên trong gốc giới hạn '{gh_full}' (ví dụ D:\\linhx\\hang-doi)."
        )
    return may_chuan, tm_full, gh_full


def tao_agy_settings_dict(goc_gioi_han: str | Path, tep_tho_env: str | Path) -> dict:
    goc_posix = str(goc_gioi_han).replace("\\", "/").rstrip("/")
    goc_win = str(goc_gioi_han).replace("/", "\\").rstrip("\\")
    env_posix = str(tep_tho_env).replace("\\", "/")
    env_win = str(tep_tho_env).replace("/", "\\")
    return {
        "agentMode": "auto",
        "permissions": {
            "allow": [
                "command(*)",
                f"read_file({goc_posix})",
                f"write_file({goc_posix})",
                f"edit_file({goc_posix})",
                f"read_file({goc_win})",
                f"write_file({goc_win})",
                f"edit_file({goc_win})",
                "mcp(browsentic/*)",
                "mcp(*)",
            ],
            "deny": [
                f"read_file({env_posix})",
                f"write_file({env_posix})",
                f"edit_file({env_posix})",
                f"read_file({env_win})",
                f"write_file({env_win})",
                f"edit_file({env_win})",
                "write_file(D:/LINHX/LINHX-ENGINE)",
                "edit_file(D:/LINHX/LINHX-ENGINE)",
                r"write_file(D:\LINHX\LINHX-ENGINE)",
                r"edit_file(D:\LINHX\LINHX-ENGINE)",
            ],
        },
    }


def _bao_tham_so(s: str) -> str:
    return f'"{s}"' if any(c.isspace() for c in s) else s


def tao_noi_dung_tho_env(
    may: str,
    thu_muc_repo: str | Path,
    thu_muc_lam_viec: str | Path,
    goc_gioi_han: str | Path,
    tep_settings: str | Path,
    thu_muc_drive: str | Path = THU_MUC_DRIVE_MAC_DINH,
    thu_muc_log: str | Path = THU_MUC_LOG_MAC_DINH,
    so_phieu: int = 1,
    agy_cmd: str = "agy",
) -> str:
    agy_args = (
        f"--output-format json --mode auto --dangerously-skip-permissions "
        f"--add-dir {_bao_tham_so(str(goc_gioi_han))} "
        f"--settings {_bao_tham_so(str(tep_settings))} "
        f"--print-timeout 2400s"
    )
    cac_dong = [
        "# Cau hinh tho hang-doi GitHub (tao boi runner/cai-may.ps1). KHONG commit file nay.",
        "LINHX_NGUON=github",
        f"LINHX_THO={may}",
        f"LINHX_REPO_HANG_DOI={thu_muc_repo}",
        "LINHX_NHANH_HANG_DOI=hang-doi",
        "LINHX_REMOTE_HANG_DOI=origin",
        f"LINHX_THU_MUC={thu_muc_lam_viec}",
        f"LINHX_GIOI_HAN_THU_MUC={goc_gioi_han}",
        f"LINHX_DRIVE={thu_muc_drive}",
        f"LINHX_LOG_DIR={thu_muc_log}",
        f"LINHX_SO_PHIEU={int(so_phieu)}",
        "LINHX_TRAN_PHUT=40",
        "LINHX_KHONG_TIEN_PHUT=10",
        "LINHX_RAM_TOI_THIEU_GB=1.5",
        f"AGY_CMD={agy_cmd}",
        f"AGY_ARGS={agy_args}",
    ]
    return "\n".join(cac_dong) + "\n"


def tim_powershell() -> str | None:
    if os.name == "nt":
        return shutil.which("powershell") or shutil.which("pwsh")
    return shutil.which("pwsh") or shutil.which("powershell")


def cai_may_python(
    may: str,
    thu_muc: str | Path = THU_MUC_MAC_DINH,
    repo_url: str | Path = REPO_URL_MAC_DINH,
    goc_gioi_han: str | Path = GOC_GIOI_HAN_MAC_DINH,
    thu_muc_drive: str | Path = THU_MUC_DRIVE_MAC_DINH,
    thu_muc_log: str | Path = THU_MUC_LOG_MAC_DINH,
    ten_lich: str = TEN_LICH_MAC_DINH,
    agy_cmd: str = "",
    so_phieu: int = 1,
    khong_chay_ngay: bool = False,
    dang_ky_lich_fn=None,
) -> dict:
    """Cai dat may tuong duong runner/cai-may.ps1 (dung cho moi truong khong co PowerShell hoac test Python)."""
    may_chuan, tm_str, gh_str = kiem_tra_tham_so_cai(may, thu_muc, goc_gioi_han, so_phieu=so_phieu)
    tm = Path(tm_str)
    gh = Path(gh_str)
    gh.mkdir(parents=True, exist_ok=True)
    tm.parent.mkdir(parents=True, exist_ok=True)

    cham_git = tm / ".git"
    tep_runner_py = tm / "runner" / "linhx_runner.py"
    if cham_git.exists():
        if not tep_runner_py.is_file():
            raise RuntimeError(f"Thư mục '{tm}' đã có .git nhưng thiếu runner/linhx_runner.py.")
    else:
        if tm.exists() and any(tm.iterdir()):
            raise RuntimeError(f"Thư mục '{tm}' đã tồn tại và không rỗng nhưng chưa phải git repo.")
        kw = {"creationflags": 0x08000000} if os.name == "nt" else {}
        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"
        p = subprocess.run(
            ["git", "clone", str(repo_url), str(tm)],
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            **kw,
        )
        if p.returncode != 0 or not cham_git.exists():
            raise RuntimeError(f"git clone thất bại ({p.returncode}): {(p.stderr or p.stdout).strip()}")
        if not tep_runner_py.is_file():
            raise RuntimeError(f"Repo vừa clone tại '{tm}' thiếu runner/linhx_runner.py.")

    tm_runner = tm / "runner"
    tm_viec_goc = tm_runner / "viec"
    tm_lam_viec = tm_viec_goc / "lam-viec"
    tm_lam_viec.mkdir(parents=True, exist_ok=True)
    Path(thu_muc_log).mkdir(parents=True, exist_ok=True)

    tep_tho_env = tm_runner / "tho.env"
    tep_settings_repo = tm_runner / "agy-settings.json"
    dung_repo_mac_dinh = (
        _chuan_hoa_win(gh_str).lower() == r"d:\linhx"
        and _chuan_hoa_win(tm_str).lower() == r"d:\linhx\hang-doi"
        and tep_settings_repo.is_file()
    )
    if dung_repo_mac_dinh:
        tep_settings = tep_settings_repo
    else:
        tep_settings = tm_viec_goc / "agy-settings.json"
        tep_settings.write_text(
            json.dumps(tao_agy_settings_dict(gh, tep_tho_env), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    lenh_agy = agy_cmd.strip() if agy_cmd and agy_cmd.strip() else ""
    if not lenh_agy:
        ung_vien = Path.home() / ".gemini" / "bin" / "agy.exe"
        lenh_agy = str(ung_vien) if ung_vien.is_file() else "agy"

    tep_tho_env.write_text(
        tao_noi_dung_tho_env(
            may=may_chuan,
            thu_muc_repo=tm,
            thu_muc_lam_viec=tm_lam_viec,
            goc_gioi_han=gh,
            tep_settings=tep_settings,
            thu_muc_drive=thu_muc_drive,
            thu_muc_log=thu_muc_log,
            so_phieu=so_phieu,
            agy_cmd=lenh_agy,
        ),
        encoding="utf-8",
    )

    tep_vbs = tm_runner / "chay-an-tho.vbs"
    nguoi_dung = os.environ.get("USERNAME") or os.environ.get("USER") or "user"
    thong_so_lich = {
        "TaskName": ten_lich,
        "Force": True,
        "Started": not khong_chay_ngay,
        "Action": {
            "Execute": "wscript.exe",
            "Argument": f'//B "{tep_vbs}" --mot-lan',
            "WorkingDirectory": str(tm_runner),
        },
        "Trigger": {
            "Once": True,
            "RepetitionIntervalMinutes": 1.0,
        },
        "Principal": {
            "UserId": nguoi_dung,
            "LogonType": "Interactive",
            "RunLevel": "Limited",
        },
        "Settings": {
            "AllowStartIfOnBatteries": True,
            "DontStopIfGoingOnBatteries": True,
            "StartWhenAvailable": True,
            "MultipleInstances": "IgnoreNew",
            "ExecutionTimeLimitMinutes": 0.0,
        },
    }
    if dang_ky_lich_fn is not None:
        dang_ky_lich_fn(thong_so_lich)
    return thong_so_lich
