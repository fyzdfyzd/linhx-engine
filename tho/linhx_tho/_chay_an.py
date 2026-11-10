"""Trình con cô lập (`python -I -X utf8`) hỗ trợ `chay-an.vbs` khởi chạy `agy` ẩn (`CREATE_NO_WINDOW`),
lọc sạch biến môi trường nhạy cảm, gắn Windows Job Object (`KILL_ON_JOB_CLOSE`) và thu hồi trọn cây
tiến trình khi hết giờ.
"""
from __future__ import annotations

import ctypes
import json
import os
import pathlib
import subprocess
import sys

CO_KHONG_CUA_SO = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)

_DUOI_SCRIPT_CAM = frozenset(
    {".bat", ".cmd", ".com", ".ps1", ".vbs", ".wsf", ".hta", ".js", ".jse", ".msi", ".scr", ".sh"}
)

_BIEN_MOI_TRUONG_AN_TOAN = (
    "ALLUSERSPROFILE",
    "APPDATA",
    "COMMONPROGRAMFILES",
    "COMMONPROGRAMFILES(X86)",
    "COMMONPROGRAMW6432",
    "COMPUTERNAME",
    "COMSPEC",
    "HOMEDRIVE",
    "HOMEPATH",
    "HOME",
    "LANG",
    "LOCALAPPDATA",
    "NUMBER_OF_PROCESSORS",
    "OS",
    "PATH",
    "PATHEXT",
    "PROCESSOR_ARCHITECTURE",
    "PROGRAMDATA",
    "PROGRAMFILES",
    "PROGRAMFILES(X86)",
    "PROGRAMW6432",
    "PUBLIC",
    "SYSTEMDRIVE",
    "SYSTEMROOT",
    "TEMP",
    "TMP",
    "USERDOMAIN",
    "USERNAME",
    "USERPROFILE",
    "WINDIR",
)


class _JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_int64),
        ("PerJobUserTimeLimit", ctypes.c_int64),
        ("LimitFlags", ctypes.c_uint32),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", ctypes.c_uint32),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", ctypes.c_uint32),
        ("SchedulingClass", ctypes.c_uint32),
    ]


class _IO_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("ReadOperationCount", ctypes.c_uint64),
        ("WriteOperationCount", ctypes.c_uint64),
        ("OtherOperationCount", ctypes.c_uint64),
        ("ReadTransferCount", ctypes.c_uint64),
        ("WriteTransferCount", ctypes.c_uint64),
        ("OtherTransferCount", ctypes.c_uint64),
    ]


class _JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", _JOBOBJECT_BASIC_LIMIT_INFORMATION),
        ("IoInfo", _IO_COUNTERS),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


def _gan_job_kill_on_close(pid: int):
    """Gắn tiến trình con vào Windows Job Object tự huỷ cây tiến trình khi đóng handle."""
    if os.name != "nt":
        return None
    try:
        k32 = ctypes.windll.kernel32
        job = k32.CreateJobObjectW(None, None)
        if not job:
            return None
        info = _JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        info.BasicLimitInformation.LimitFlags = 0x00002000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        ok = k32.SetInformationJobObject(job, 9, ctypes.byref(info), ctypes.sizeof(info))
        if not ok:
            k32.CloseHandle(job)
            return None
        proc_handle = k32.OpenProcess(0x0100 | 0x0001, False, int(pid))  # PROCESS_SET_QUOTA | PROCESS_TERMINATE
        if not proc_handle:
            k32.CloseHandle(job)
            return None
        try:
            k32.AssignProcessToJobObject(job, proc_handle)
        finally:
            k32.CloseHandle(proc_handle)
        return job
    except Exception:
        return None


def _dong_job(job) -> None:
    if os.name == "nt" and job:
        try:
            ctypes.windll.kernel32.CloseHandle(job)
        except Exception:
            pass


def _giet_cay_tien_trinh(pid: int) -> None:
    if pid <= 0:
        return
    if os.name == "nt":
        taskkill_sys = pathlib.Path(os.environ.get("SYSTEMROOT", r"C:\Windows")) / "System32" / "taskkill.exe"
        lenh_tk = str(taskkill_sys) if taskkill_sys.is_file() else "taskkill.exe"
        subprocess.run(
            [lenh_tk, "/PID", str(int(pid)), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=CO_KHONG_CUA_SO,
            timeout=15,
            check=False,
        )


def _tao_env_sach() -> dict[str, str]:
    """Chỉ giữ biến môi trường hệ thống tối thiểu, không truyền khoá thợ/token sang agy."""
    env_sach: dict[str, str] = {"PYTHONUTF8": "1"}
    for k in _BIEN_MOI_TRUONG_AN_TOAN:
        val = os.environ.get(k)
        if isinstance(val, str) and val:
            env_sach[k] = val
    return env_sach


def main() -> int:
    exe = os.environ.get("LINHX_THO_EXE", "").strip()
    args_raw = os.environ.get("LINHX_THO_ARGS_JSON", "[]")
    cwd = os.environ.get("LINHX_THO_CWD", "").strip()
    tap_out = os.environ.get("LINHX_THO_STDOUT", "").strip()
    tap_err = os.environ.get("LINHX_THO_STDERR", "").strip()
    tap_pid = os.environ.get("LINHX_THO_PID_FILE", "").strip()
    timeout_s = int(os.environ.get("LINHX_THO_TIMEOUT", "2400") or "2400")

    if not exe or not tap_out or not cwd:
        return 2

    duong_exe = pathlib.Path(exe).resolve()
    if not duong_exe.is_file() or duong_exe.suffix.lower() in _DUOI_SCRIPT_CAM:
        return 6

    duong_cwd = pathlib.Path(cwd).resolve()
    if not duong_cwd.is_dir():
        return 2

    try:
        ds_tham_so = json.loads(args_raw)
        if not isinstance(ds_tham_so, list) or not all(isinstance(x, str) for x in ds_tham_so):
            return 2
    except Exception:
        return 2

    duong_out = pathlib.Path(tap_out)
    duong_out.parent.mkdir(parents=True, exist_ok=True)
    duong_err = pathlib.Path(tap_err) if tap_err else duong_out.with_suffix(".err")
    duong_err.parent.mkdir(parents=True, exist_ok=True)

    env_con = _tao_env_sach()
    job_handle = None
    with open(duong_out, "wb") as f_out, open(duong_err, "wb") as f_err:
        proc = subprocess.Popen(
            [str(duong_exe), *ds_tham_so],
            cwd=str(duong_cwd),
            env=env_con,
            stdin=subprocess.DEVNULL,
            stdout=f_out,
            stderr=f_err,
            creationflags=CO_KHONG_CUA_SO,
        )
        try:
            job_handle = _gan_job_kill_on_close(proc.pid)
            if tap_pid:
                try:
                    p_pid = pathlib.Path(tap_pid)
                    p_pid.parent.mkdir(parents=True, exist_ok=True)
                    p_pid.write_text(str(proc.pid), encoding="utf-8")
                except OSError:
                    pass
            try:
                ma_thoat = proc.wait(timeout=timeout_s)
                return int(ma_thoat)
            except subprocess.TimeoutExpired:
                _giet_cay_tien_trinh(proc.pid)
                try:
                    proc.kill()
                except OSError:
                    pass
                try:
                    proc.wait(timeout=5)
                except Exception:
                    pass
                return 124
        finally:
            _dong_job(job_handle)


if __name__ == "__main__":
    sys.exit(main())
