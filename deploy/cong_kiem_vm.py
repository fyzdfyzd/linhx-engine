#!/usr/bin/env python3
"""Cổng kiểm độc lập trên VM linhx-engine-1 có trần RAM qua systemd-run, khoá flock, tách user và cách ly mạng."""
from __future__ import annotations

import argparse
import contextlib
import datetime
import hashlib
import json
import os
import pathlib
import re
import shlex
import shutil
import socket
import subprocess
import time

try:
    import fcntl
except ImportError:  # Hệ điều hành cục bộ không có fcntl khi chạy kiểm thử đơn vị trên Windows
    fcntl = None

try:
    import pwd
except ImportError:
    pwd = None

REPO_MAC_DINH = "https://github.com/fyzdfyzd/linhx-engine.git"
USER_CHAY_KIEM = "congkiem"
TEN_NETNS_VM = "congkiem-net"
DUONG_NETNS_VM = pathlib.Path("/run/netns") / TEN_NETNS_VM
DUONG_KHOA_TOAN_CUC = pathlib.Path("/var/lock/cong-kiem-vm.lock")
THU_MUC_RUNTIME_VM = pathlib.Path("/opt/cong-kiem-vm")
VENV_VM_PYTHON = THU_MUC_RUNTIME_VM / "venv" / "bin" / "python"
PLAYWRIGHT_VM_PATH = THU_MUC_RUNTIME_VM / "ms-playwright"
GOI_PIP_GHIM = ("pytest==9.2.0", "playwright==1.65.0")

_MAU_NHANH = re.compile(r"(?:main|tu-dong/engine-t[0-9]+)")
_MAU_FEATURES = re.compile(r"features-dot[0-9a-z]+\.json")
_MAU_RAM = re.compile(r"[1-9][0-9]*[KMG]")
_MAU_MA_FEATURE = re.compile(r"[A-Za-z0-9_]+")
_MAU_THEM = re.compile(r"\s*[A-Za-z0-9_]+(?:\s*,\s*[A-Za-z0-9_]+)*\s*")
_MAU_REPO_URL = re.compile(r"(?:https://[A-Za-z0-9._/-]+\.git|/[A-Za-z0-9._/-]+)")
_MAU_UNIT = re.compile(r"cong-kiem-vm-[a-z0-9-]+")

TEP_TU_NAP_CAM = frozenset(
    {
        "conftest.py",
        "pytest.py",
        "sitecustomize.py",
        "usercustomize.py",
        "_pytest",
        ".pytest.ini",
    }
)
TEP_CAU_HINH_PYTEST_CAM = frozenset({"pyproject.toml", "tox.ini", "setup.cfg", ".pytest.ini"})
THU_MUC_BO_QUA_QUET = frozenset({".git", "node_modules", ".venv", "venv", "__pycache__", ".next"})

TIEN_TO_REGISTRY_NPM = "https://registry.npmjs.org/"
TIEN_TO_DEP_CAM = (
    "file:",
    "link:",
    "git+",
    "git:",
    "ssh:",
    "github:",
    "http://",
    "https://",
    "ftp://",
)

MA_THOAT_LOI_MAY = (137, -9)
CO_LOI_DONG_BO_VM = "LOI_MAY_DONG_BO_VM"
DAU_HIEU_LOI_MAY = (
    "Out of memory",
    "oom-kill",
    "TimeoutExpired",
    "No space left",
    CO_LOI_DONG_BO_VM,
)

GIOI_HAN_RA = 3000
GIOI_HAN_RA_BANG_CHUNG = 500


def nhanh_hop_le(ten: str) -> bool:
    """Chỉ nhận nhánh 'main' hoặc 'tu-dong/engine-t<số>', chặn mọi ký tự lạ."""
    if not isinstance(ten, str) or not ten.isascii():
        return False
    if "\n" in ten or "\r" in ten:
        return False
    return bool(_MAU_NHANH.fullmatch(ten))


def _kiem_file_features(file_features: str) -> None:
    if (
        not isinstance(file_features, str)
        or not file_features.isascii()
        or "\n" in file_features
        or "\r" in file_features
        or not _MAU_FEATURES.fullmatch(file_features)
    ):
        raise ValueError(f"file features không hợp lệ: {file_features!r}")


def _kiem_ram(ram: str) -> None:
    if (
        not isinstance(ram, str)
        or not ram.isascii()
        or "\n" in ram
        or "\r" in ram
        or not _MAU_RAM.fullmatch(ram)
    ):
        raise ValueError(f"giá trị ram không hợp lệ: {ram!r}")


def _kiem_them(them: str) -> str:
    if not isinstance(them, str) or not them.isascii() or "\n" in them or "\r" in them:
        raise ValueError(f"danh sách thêm không hợp lệ: {them!r}")
    if them == "":
        return ""
    if not _MAU_THEM.fullmatch(them):
        raise ValueError(f"danh sách thêm không hợp lệ: {them!r}")
    return ",".join(x.strip() for x in them.split(",") if x.strip())


def _ten_unit_mac_dinh(nhanh: str) -> str:
    if not nhanh_hop_le(nhanh):
        raise ValueError(f"nhánh không hợp lệ: {nhanh!r}")
    duoi = nhanh.replace("/", "-")
    ten_unit = f"cong-kiem-vm-{duoi}"
    if not _MAU_UNIT.fullmatch(ten_unit):
        raise ValueError(f"tên unit không hợp lệ: {ten_unit!r}")
    return ten_unit


def _goc_chay_mac_dinh() -> pathlib.Path:
    tu_bien = os.environ.get("CONG_KIEM_VM_GOC", "").strip()
    if tu_bien:
        return pathlib.Path(tu_bien)
    if os.name != "nt":
        return pathlib.Path("/var/lib/cong-kiem-vm")
    return pathlib.Path.home() / "cong-kiem-vm"


def _tim_python() -> str:
    if os.name != "nt" and VENV_VM_PYTHON.is_file():
        return VENV_VM_PYTHON.as_posix()
    return "python3"


def thu_muc_nhanh(nhanh: str, goc_chay: pathlib.Path | None = None) -> pathlib.Path:
    if not nhanh_hop_le(nhanh):
        raise ValueError(f"nhánh không hợp lệ: {nhanh!r}")
    goc = (pathlib.Path(goc_chay) if goc_chay is not None else _goc_chay_mac_dinh()).resolve()
    goc_nhanh = (goc / "nhanh").resolve()
    dich = (goc_nhanh / nhanh.replace("/", "__")).resolve()
    if dich == goc_nhanh or goc_nhanh not in dich.parents:
        raise ValueError(f"đường dẫn nhánh thoát khỏi gốc: {nhanh!r}")
    return dich


def _tao_lenh_chay(
    nhanh: str,
    file_features: str,
    them: str = "",
    ram: str = "3G",
    goc_chay: pathlib.Path | None = None,
    ten_unit: str | None = None,
) -> list[str]:
    if not nhanh_hop_le(nhanh):
        raise ValueError(f"nhánh không hợp lệ: {nhanh!r}")
    _kiem_file_features(file_features)
    _kiem_them(them)
    _kiem_ram(ram)
    unit = ten_unit if ten_unit is not None else _ten_unit_mac_dinh(nhanh)
    if not isinstance(unit, str) or not _MAU_UNIT.fullmatch(unit):
        raise ValueError(f"tên unit không hợp lệ: {unit!r}")

    tm = thu_muc_nhanh(nhanh, goc_chay=goc_chay).as_posix()
    return [
        "systemd-run",
        "--scope",
        "--quiet",
        f"--unit={unit}",
        "-p",
        f"MemoryMax={ram}",
        "-p",
        "OOMPolicy=kill",
        "-p",
        "IPAddressDeny=any",
        "-p",
        "IPAddressAllow=localhost",
        "--",
        "/usr/bin/unshare",
        f"--net={DUONG_NETNS_VM.as_posix()}",
        "--pid",
        "--fork",
        "--mount-proc",
        "--kill-child=SIGKILL",
        "/usr/bin/setpriv",
        f"--reuid={USER_CHAY_KIEM}",
        f"--regid={USER_CHAY_KIEM}",
        "--clear-groups",
        "--no-new-privs",
        _tim_python(),
        f"{tm}/canh/cong_kiem.py",
        "kiem",
        f"{tm}/{file_features}",
    ]


def lenh_chay(nhanh: str, file_features: str, them: str = "", ram: str = "3G") -> list[str]:
    """Dựng danh sách đối số chạy cổng kiểm dưới systemd-run có MemoryMax, cách ly mạng và tách user."""
    return _tao_lenh_chay(nhanh=nhanh, file_features=file_features, them=them, ram=ram, goc_chay=None)


def phan_loai(ma: int, ra: str) -> dict:
    """Tách lỗi máy (mã 137/-9, hết RAM, quá giờ, hết đĩa, lỗi đồng bộ hạ tầng) khỏi lỗi mã nguồn."""
    chu = "" if ra is None else str(ra)
    ma_so = int(ma)
    loi_may = ma_so in MA_THOAT_LOI_MAY or any(dau in chu for dau in DAU_HIEU_LOI_MAY)
    return {
        "ma": ma_so,
        "loi_may": bool(loi_may),
        "ra": chu[-GIOI_HAN_RA:],
    }


def _tim_features_can_kiem_them(noi_dung_main: str, noi_dung_nhanh: str) -> list[str]:
    """Luôn bắt chạy lại lệnh kiểm cho mọi feature đổi passes sang true hoặc đổi bằng chứng so với main."""
    try:
        du_lieu_nhanh = json.loads(noi_dung_nhanh)
    except Exception:
        return []
    try:
        du_lieu_main = json.loads(noi_dung_main) if noi_dung_main else {}
    except Exception:
        du_lieu_main = {}

    theo_main = {
        str(f["id"]): f
        for f in du_lieu_main.get("features", [])
        if isinstance(f, dict) and isinstance(f.get("id"), str)
    }
    ket_qua: list[str] = []
    for f in du_lieu_nhanh.get("features", []):
        if not isinstance(f, dict) or not f.get("passes"):
            continue
        fid = str(f.get("id", "")).strip()
        if not fid or not _MAU_MA_FEATURE.fullmatch(fid):
            continue
        cu = theo_main.get(fid)
        if cu is None or not cu.get("passes") or cu.get("bang_chung") != f.get("bang_chung"):
            ket_qua.append(fid)
    return ket_qua


def _duong_khoa_he_thong(goc: pathlib.Path) -> pathlib.Path:
    """Ưu tiên khoá cố định toàn máy (/var/lock/cong-kiem-vm.lock) để hai --goc-chay không đụng nhau."""
    if os.name != "nt" and DUONG_KHOA_TOAN_CUC.parent.is_dir():
        return DUONG_KHOA_TOAN_CUC
    return goc / "cong-kiem.lock"


@contextlib.contextmanager
def khoa_luot(duong_khoa: pathlib.Path):
    """Khoá độc quyền bằng fcntl.flock để một thời điểm chỉ chạy một lượt kiểm trên toàn máy."""
    duong_khoa.parent.mkdir(parents=True, exist_ok=True)
    if duong_khoa != DUONG_KHOA_TOAN_CUC:
        try:
            os.chmod(duong_khoa.parent, 0o711)
        except OSError:
            pass
    with open(duong_khoa, "a+", encoding="utf-8") as tep_khoa:
        try:
            os.chmod(duong_khoa, 0o600)
        except OSError:
            pass
        if fcntl is not None:
            fcntl.flock(tep_khoa.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(tep_khoa.fileno(), fcntl.LOCK_UN)


def _chay_buoc(
    lenh: list[str],
    cwd: pathlib.Path | None = None,
    env: dict[str, str] | None = None,
    timeout: int = 300,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        lenh,
        cwd=str(cwd) if cwd is not None else None,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def _la_root() -> bool:
    return hasattr(os, "geteuid") and os.geteuid() == 0


def _chay_root(
    lenh: list[str],
    cwd: pathlib.Path | None = None,
    timeout: int = 300,
) -> subprocess.CompletedProcess:
    lenh_thuc = lenh if _la_root() else ["sudo", "-n", *lenh]
    env_root = {
        "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        "LANG": "C.UTF-8",
    }
    return _chay_buoc(lenh_thuc, cwd=cwd, env=env_root, timeout=timeout)


def _moi_truong_sach(
    home_tam: pathlib.Path,
    tmp_tam: pathlib.Path,
    npm_cache_tam: pathlib.Path,
) -> dict[str, str]:
    """Dựng môi trường sạch: không giữ HOME thật, không giữ CONG_KIEM_DOI của người gọi."""
    giu = ("PATH", "LANG", "LC_ALL", "TZ")
    env = {k: os.environ[k] for k in giu if k in os.environ}
    env["HOME"] = home_tam.as_posix()
    env["TMPDIR"] = tmp_tam.as_posix()
    env["NPM_CONFIG_CACHE"] = npm_cache_tam.as_posix()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONSAFEPATH"] = "1"
    env["PYTHONNOUSERSITE"] = "1"
    env["NEXT_TELEMETRY_DISABLED"] = "1"
    env.setdefault("LANG", "C.UTF-8")

    if PLAYWRIGHT_VM_PATH.is_dir():
        env["PLAYWRIGHT_BROWSERS_PATH"] = PLAYWRIGHT_VM_PATH.as_posix()
    else:
        tu_bien_pw = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "").strip()
        if tu_bien_pw:
            env["PLAYWRIGHT_BROWSERS_PATH"] = tu_bien_pw

    duong_path = env.get("PATH", "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin")
    if VENV_VM_PYTHON.parent.is_dir():
        duong_path = f"{VENV_VM_PYTHON.parent.as_posix()}:{duong_path}"
    env["PATH"] = duong_path
    return env


def _dam_bao_luat_iptables(cong_cu: str, quy_tac: list[str]) -> bool:
    """Đảm bảo một quy tắc iptables/ip6tables tồn tại ở đầu chuỗi OUTPUT."""
    r_kiem = _chay_root([cong_cu, "-C", "OUTPUT", *quy_tac], timeout=15)
    if r_kiem.returncode == 0:
        return True
    r_them = _chay_root([cong_cu, "-I", "OUTPUT", "1", *quy_tac], timeout=15)
    return r_them.returncode == 0


def _thiet_lap_cach_ly_mang_vm() -> tuple[bool, str]:
    """Dựng namespace mạng riêng congkiem-net (chỉ có loopback) và tường lửa iptables chặn metadata/nội bộ cho user congkiem."""
    if os.name == "nt":
        return True, ""

    if not DUONG_NETNS_VM.exists():
        r_ns = _chay_root(["ip", "netns", "add", TEN_NETNS_VM], timeout=15)
        if r_ns.returncode != 0 and not DUONG_NETNS_VM.exists():
            return False, f"{CO_LOI_DONG_BO_VM}: Không tạo được netns {TEN_NETNS_VM}: {r_ns.stderr}"

    r_lo = _chay_root(["ip", "-n", TEN_NETNS_VM, "link", "set", "dev", "lo", "up"], timeout=15)
    if r_lo.returncode != 0:
        return False, f"{CO_LOI_DONG_BO_VM}: Không bật được loopback trong netns {TEN_NETNS_VM}: {r_lo.stderr}"

    # Chặn ở cả tầng host iptables cho user congkiem (phòng vệ chiều sâu cho cả bước npm ci và chặn metadata GCP/dịch vụ nội bộ)
    cac_luat_v4 = (
        ["-m", "owner", "--uid-owner", USER_CHAY_KIEM, "-d", "169.254.169.254/32", "-j", "REJECT"],
        ["-m", "owner", "--uid-owner", USER_CHAY_KIEM, "-d", "169.254.0.0/16", "-j", "REJECT"],
        [
            "-m",
            "owner",
            "--uid-owner",
            USER_CHAY_KIEM,
            "-d",
            "127.0.0.0/8",
            "-p",
            "tcp",
            "-m",
            "multiport",
            "--dports",
            "3306,6379,8000:8010,9000:9010,11000:13010",
            "-j",
            "REJECT",
        ],
        ["-m", "owner", "--uid-owner", USER_CHAY_KIEM, "-d", "10.0.0.0/8", "-j", "REJECT"],
        ["-m", "owner", "--uid-owner", USER_CHAY_KIEM, "-d", "172.16.0.0/12", "-j", "REJECT"],
        ["-m", "owner", "--uid-owner", USER_CHAY_KIEM, "-d", "192.168.0.0/16", "-j", "REJECT"],
    )
    for luat in cac_luat_v4:
        if not _dam_bao_luat_iptables("iptables", luat):
            return False, f"{CO_LOI_DONG_BO_VM}: Không đặt được luật iptables bảo vệ cho {USER_CHAY_KIEM}: {luat}"

    if shutil.which("ip6tables"):
        for luat6 in (
            ["-m", "owner", "--uid-owner", USER_CHAY_KIEM, "-d", "fe80::/10", "-j", "REJECT"],
            ["-m", "owner", "--uid-owner", USER_CHAY_KIEM, "-d", "fc00::/7", "-j", "REJECT"],
        ):
            _dam_bao_luat_iptables("ip6tables", luat6)

    return True, ""


def kiem_chan_metadata_va_mang() -> tuple[bool, str]:
    """Khẳng định tiến trình chạy dưới user congkiem trong netns bị từ chối khi gọi GCP metadata 169.254.169.254 và chỉ dùng được loopback riêng."""
    if os.name == "nt":
        return True, "windows-skip"
    ma_kiem = (
        "import socket, sys, urllib.request\n"
        "s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n"
        "s.bind(('127.0.0.1', 0))\n"
        "s.close()\n"
        "req = urllib.request.Request(\n"
        "    'http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token',\n"
        "    headers={'Metadata-Flavor': 'Google'},\n"
        ")\n"
        "try:\n"
        "    urllib.request.urlopen(req, timeout=2)\n"
        "    print('LO_METADATA')\n"
        "    sys.exit(1)\n"
        "except Exception:\n"
        "    pass\n"
        "for port in (6379, 3306, 8000):\n"
        "    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n"
        "    c.settimeout(0.5)\n"
        "    try:\n"
        "        c.connect(('127.0.0.1', port))\n"
        "        c.close()\n"
        "        print(f'LO_CONG_NOI_BO:{port}')\n"
        "        sys.exit(1)\n"
        "    except Exception:\n"
        "        c.close()\n"
        "print('CHAN_MANG_OK')\n"
    )
    r = _chay_root(
        [
            "systemd-run",
            "--scope",
            "--quiet",
            "-p",
            "MemoryMax=256M",
            "-p",
            "IPAddressDeny=any",
            "-p",
            "IPAddressAllow=localhost",
            "--",
            "/usr/bin/unshare",
            f"--net={DUONG_NETNS_VM.as_posix()}",
            "--pid",
            "--fork",
            "--mount-proc",
            "--kill-child=SIGKILL",
            "/usr/bin/setpriv",
            f"--reuid={USER_CHAY_KIEM}",
            f"--regid={USER_CHAY_KIEM}",
            "--clear-groups",
            "--no-new-privs",
            _tim_python(),
            "-I",
            "-c",
            ma_kiem,
        ],
        timeout=30,
    )
    dau_ra = ((r.stdout or "") + (r.stderr or "")).strip()
    if r.returncode != 0 or "CHAN_MANG_OK" not in dau_ra:
        return False, f"{CO_LOI_DONG_BO_VM}: Kiểm tra chặn metadata/mạng cho {USER_CHAY_KIEM} thất bại: {dau_ra}"
    return True, "CHAN_MANG_OK"


def _dam_bao_moi_truong_cach_ly(goc: pathlib.Path) -> tuple[bool, str]:
    """Đảm bảo user riêng congkiem, netns/iptables chặn metadata và runtime chỉ đọc /opt/cong-kiem-vm tồn tại trên Linux VM."""
    if os.name == "nt":
        return True, ""

    if not _la_root():
        r_sudo = _chay_buoc(["sudo", "-n", "true"], env={"PATH": "/usr/bin:/bin"}, timeout=15)
        if r_sudo.returncode != 0:
            return False, f"{CO_LOI_DONG_BO_VM}: Cần quyền root hoặc sudo không mật khẩu trên VM để tách user chạy cổng kiểm."

    co_user = False
    if pwd is not None:
        try:
            pwd.getpwnam(USER_CHAY_KIEM)
            co_user = True
        except KeyError:
            co_user = False
    if not co_user:
        r_u = _chay_root(
            [
                "useradd",
                "--system",
                "--user-group",
                "--home-dir",
                "/nonexistent",
                "--no-create-home",
                "--shell",
                "/usr/sbin/nologin",
                USER_CHAY_KIEM,
            ],
            timeout=30,
        )
        if r_u.returncode != 0:
            return False, f"{CO_LOI_DONG_BO_VM}: Không tạo được user {USER_CHAY_KIEM}: {r_u.stdout}\n{r_u.stderr}"

    r_mkdir = _chay_root(
        ["mkdir", "-p", str(THU_MUC_RUNTIME_VM), str(goc), str(goc / "nhanh"), str(goc / "chay-tam")],
        timeout=30,
    )
    if r_mkdir.returncode != 0:
        return False, f"{CO_LOI_DONG_BO_VM}: Không chuẩn bị được thư mục gốc chạy: {r_mkdir.stderr}"

    uid_goi = os.getuid()
    gid_goi = os.getgid()
    _chay_root(
        ["chown", "-h", f"{uid_goi}:{gid_goi}", str(goc), str(goc / "nhanh"), str(goc / "chay-tam")],
        timeout=30,
    )
    _chay_root(["chmod", "0711", str(goc), str(goc / "nhanh"), str(goc / "chay-tam")], timeout=30)

    can_khoa_quyen_rt = False
    if not VENV_VM_PYTHON.is_file():
        r_venv = _chay_root(["python3", "-m", "venv", str(THU_MUC_RUNTIME_VM / "venv")], timeout=120)
        if r_venv.returncode != 0:
            return False, f"{CO_LOI_DONG_BO_VM}: Không tạo được venv chỉ đọc: {r_venv.stdout}\n{r_venv.stderr}"
        r_pip = _chay_root(
            [str(THU_MUC_RUNTIME_VM / "venv" / "bin" / "pip"), "install", "-q", *GOI_PIP_GHIM],
            timeout=300,
        )
        if r_pip.returncode != 0:
            return False, f"{CO_LOI_DONG_BO_VM}: Không cài được pytest/playwright vào venv chỉ đọc: {r_pip.stdout}\n{r_pip.stderr}"
        can_khoa_quyen_rt = True

    if can_khoa_quyen_rt or not PLAYWRIGHT_VM_PATH.is_dir():
        lenh_pw = [
            "/usr/bin/env",
            f"PLAYWRIGHT_BROWSERS_PATH={PLAYWRIGHT_VM_PATH.as_posix()}",
            str(THU_MUC_RUNTIME_VM / "venv" / "bin" / "playwright"),
            "install",
            "chromium",
        ]
        if not _la_root():
            lenh_pw = ["sudo", "-n", *lenh_pw]
        r_pw = _chay_buoc(
            lenh_pw,
            env={"PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin", "LANG": "C.UTF-8"},
            timeout=300,
        )
        if r_pw.returncode != 0:
            return False, f"{CO_LOI_DONG_BO_VM}: Không cài được Chromium cho Playwright: {r_pw.stdout}\n{r_pw.stderr}"
        can_khoa_quyen_rt = True

    r_kiem_rt = _chay_root(
        ["find", str(THU_MUC_RUNTIME_VM), "(", "!", "-user", "root", "-o", "-perm", "/022", ")", "-print", "-quit"],
        timeout=60,
    )
    if can_khoa_quyen_rt or r_kiem_rt.returncode != 0 or r_kiem_rt.stdout.strip():
        _chay_root(["chown", "-R", "root:root", str(THU_MUC_RUNTIME_VM)], timeout=120)
        _chay_root(["chmod", "-R", "a+rX,go-w", str(THU_MUC_RUNTIME_VM)], timeout=120)

    ok_mang, loi_mang = _thiet_lap_cach_ly_mang_vm()
    if not ok_mang:
        return False, loi_mang

    ok_xm, loi_xm = kiem_chan_metadata_va_mang()
    if not ok_xm:
        return False, loi_xm

    return True, ""


def _ket_qua_systemd_oom(ten_unit: str, tu_luc_iso: str = "") -> bool:
    """Kiểm tra dấu hiệu OOM từ cả systemctl show lẫn journalctl của unit và kernel."""
    if os.name == "nt":
        return False
    scope = f"{ten_unit}.scope"
    r_show = _chay_root(["systemctl", "show", "-p", "Result", "-p", "SubState", scope], timeout=15)
    chu = (r_show.stdout or "") + "\n" + (r_show.stderr or "")
    if "oom-kill" in chu or "Out of memory" in chu:
        return True

    cmd_j = ["journalctl", "-u", scope, "--no-pager", "-n", "50"]
    if tu_luc_iso:
        cmd_j.extend(["--since", tu_luc_iso])
    r_j = _chay_root(cmd_j, timeout=15)
    chu_j = (r_j.stdout or "") + "\n" + (r_j.stderr or "")
    if "oom-kill" in chu_j or "Out of memory" in chu_j or "Killed process" in chu_j:
        return True

    if tu_luc_iso:
        r_k = _chay_root(["journalctl", "-k", "--since", tu_luc_iso, "--no-pager", "-n", "50"], timeout=15)
        chu_k = (r_k.stdout or "") + "\n" + (r_k.stderr or "")
        if ("Out of memory" in chu_k or "oom-kill" in chu_k) and (ten_unit in chu_k or "python" in chu_k or "chromium" in chu_k):
            return True

    return False


def _dung_unit_va_user(ten_unit: str) -> None:
    """Dừng hẳn scope systemd, mọi tiến trình sót và tệp tạm của user chạy kiểm."""
    if os.name == "nt":
        return
    scope = f"{ten_unit}.scope"
    _chay_root(["systemctl", "kill", "--kill-who=all", "-s", "SIGKILL", scope], timeout=15)
    _chay_root(["systemctl", "stop", scope], timeout=15)
    _chay_root(["systemctl", "reset-failed", scope], timeout=15)
    _chay_root(["pkill", "-KILL", "-u", USER_CHAY_KIEM], timeout=15)
    _chay_root(["find", "/tmp", "/var/tmp", "/dev/shm", "-P", "-user", USER_CHAY_KIEM, "-delete"], timeout=30)


def _chmod_khong_symlink(duong: pathlib.Path, quyen: str, timeout: int = 120) -> subprocess.CompletedProcess:
    return _chay_root(
        ["find", "-P", str(duong), "-not", "-type", "l", "-exec", "chmod", quyen, "{}", "+"],
        timeout=timeout,
    )


def _trang_bu_that(thu_muc: pathlib.Path) -> pathlib.Path | None:
    """Trả về đường dẫn trang-bu chỉ khi không phải symlink và nằm trực tiếp dưới thu_muc."""
    if thu_muc.is_symlink():
        return None
    trang_bu = thu_muc / "trang-bu"
    if trang_bu.is_symlink() or not trang_bu.is_dir():
        return None
    try:
        goc_thuc = thu_muc.resolve(strict=True)
        tb_thuc = trang_bu.resolve(strict=True)
    except OSError:
        return None
    if tb_thuc.parent != goc_thuc:
        return None
    return trang_bu


def _kiem_khong_symlink_ngoai(thu_muc: pathlib.Path) -> tuple[bool, str]:
    """Chặn mọi symlink trong nhánh thợ (trừ symlink nội bộ hợp lệ bên trong trang-bu/node_modules thật)."""
    if thu_muc.is_symlink():
        return False, f"Thư mục nhánh là symlink không hợp lệ: {thu_muc}"
    if (thu_muc / ".git").is_symlink():
        return False, "Thư mục .git là symlink không hợp lệ"

    nm_thuc: pathlib.Path | None = None
    trang_bu = _trang_bu_that(thu_muc)
    if trang_bu is not None:
        nm_dir = trang_bu / "node_modules"
        if not nm_dir.is_symlink() and nm_dir.is_dir():
            try:
                cand = nm_dir.resolve(strict=True)
                if cand.parent == trang_bu.resolve(strict=True):
                    nm_thuc = cand
            except OSError:
                nm_thuc = None

    for cha, ds_tm, ds_tep in os.walk(thu_muc, followlinks=False):
        cha_p = pathlib.Path(cha)
        if cha_p == thu_muc:
            ds_tm[:] = [d for d in ds_tm if d != ".git"]
        for ten in [*ds_tm, *ds_tep]:
            muc = cha_p / ten
            if not muc.is_symlink():
                continue
            if nm_thuc is not None and (cha_p == nm_thuc or nm_thuc in cha_p.parents):
                try:
                    dich = muc.resolve()
                except OSError:
                    return False, f"Symlink hỏng trong node_modules: {muc}"
                if dich != nm_thuc and nm_thuc not in dich.parents:
                    return False, f"Symlink trong node_modules trỏ ra ngoài: {muc}"
                continue
            return False, f"Từ chối symlink không được phép trong nhánh: {muc.relative_to(thu_muc)}"
    return True, ""


def _kiem_khong_tep_moc_cau(thu_muc: pathlib.Path) -> tuple[bool, str]:
    """Từ chối nhánh có file Python/pytest tự nạp hoặc cấu hình pytest giả mạo ngoài tests/nghiem-thu."""
    for muc_goc_cam in sorted(TEP_CAU_HINH_PYTEST_CAM):
        p_goc = thu_muc / muc_goc_cam
        if p_goc.is_symlink() or p_goc.exists():
            return False, f"Từ chối nhánh có file cấu hình can thiệp cổng kiểm ở gốc: {muc_goc_cam}"

    tm_tests = thu_muc / "tests"
    if tm_tests.is_dir() and not tm_tests.is_symlink():
        for muc_tests_cam in (*sorted(TEP_CAU_HINH_PYTEST_CAM), "pytest.ini", "__init__.py"):
            p_tests = tm_tests / muc_tests_cam
            if p_tests.is_symlink() or p_tests.exists():
                return False, f"Từ chối nhánh có file can thiệp pytest trong tests/: tests/{muc_tests_cam}"

    for cha, ds_tm, ds_tep in os.walk(thu_muc, followlinks=False):
        cha_p = pathlib.Path(cha)
        tuong_doi = cha_p.relative_to(thu_muc).as_posix()
        if tuong_doi == "tests/nghiem-thu" or tuong_doi.startswith("tests/nghiem-thu/"):
            ds_tm[:] = []
            continue

        tm_vi_pham = [d for d in ds_tm if d in TEP_TU_NAP_CAM or d.endswith(".pth")]
        if tm_vi_pham:
            rel = f"{tuong_doi}/{tm_vi_pham[0]}".lstrip("./")
            return False, f"Từ chối nhánh có thư mục tự nạp can thiệp cổng kiểm: {rel}"

        ds_tm[:] = [d for d in ds_tm if d not in THU_MUC_BO_QUA_QUET]
        for tep in ds_tep:
            if tep in TEP_TU_NAP_CAM or tep.endswith(".pth"):
                rel = f"{tuong_doi}/{tep}".lstrip("./")
                return False, f"Từ chối nhánh có file tự nạp can thiệp cổng kiểm: {rel}"
            if tuong_doi != "." and tep == "pytest.ini":
                rel = f"{tuong_doi}/{tep}".lstrip("./")
                return False, f"Từ chối nhánh có pytest.ini ngoài gốc: {rel}"
    return True, ""


def _kiem_bang_chung_trong_nhanh(thu_muc: pathlib.Path, file_features: str) -> tuple[bool, str]:
    """Đảm bảo mọi đường dẫn bang_chung của feature báo đạt đều nằm gọn dưới bang-chung/<ID>/ của nhánh."""
    tep_ff = thu_muc / file_features
    if tep_ff.is_symlink() or not tep_ff.is_file():
        return False, f"Không tìm thấy file features hợp lệ: {file_features}"
    try:
        du_lieu = json.loads(tep_ff.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, f"Không đọc được JSON {file_features}: {exc}"

    goc_thuc = thu_muc.resolve()
    for f in du_lieu.get("features", []):
        if not isinstance(f, dict) or not f.get("passes"):
            continue
        fid = str(f.get("id", "")).strip()
        bc = f.get("bang_chung")
        if not fid or not _MAU_MA_FEATURE.fullmatch(fid):
            return False, f"Mã feature không hợp lệ trong {file_features}: {fid!r}"
        if not isinstance(bc, str) or not bc.strip():
            return False, f"{fid}: báo đạt nhưng thiếu trường bang_chung"
        chu_bc = bc.replace("\\", "/")
        if chu_bc.startswith("/") or ":" in chu_bc or ".." in chu_bc.split("/"):
            return False, f"{fid}: đường dẫn bang_chung không hợp lệ: {bc!r}"
        dich = thu_muc / chu_bc
        if any(q.is_symlink() for q in [dich, *dich.parents] if q != thu_muc and thu_muc in q.parents):
            return False, f"{fid}: bang_chung đi qua symlink bị cấm: {bc!r}"
        try:
            dich_thuc = dich.resolve(strict=True)
            dich_thuc.relative_to((goc_thuc / "bang-chung" / fid).resolve())
        except (OSError, ValueError):
            return False, f"{fid}: bang_chung phải nằm dưới bang-chung/{fid}/ và tồn tại thật: {bc!r}"
    return True, ""


def _kiem_package_lock_an_toan(trang_bu: pathlib.Path) -> tuple[bool, str]:
    """Chặn package.json / package-lock.json có resolved ngoài registry.npmjs.org hoặc dùng file:/git+/link:/http."""
    pkg = trang_bu / "package.json"
    lock = trang_bu / "package-lock.json"
    if not pkg.is_file():
        return True, ""
    try:
        du_lieu_pkg = json.loads(pkg.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, f"Từ chối trang-bu/package.json không hợp lệ: {exc}"
    if not isinstance(du_lieu_pkg, dict):
        return False, "Từ chối trang-bu/package.json không phải object JSON"

    for muc_dep in ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies", "overrides"):
        khoi = du_lieu_pkg.get(muc_dep)
        if not isinstance(khoi, dict):
            continue
        for ten_goi, gia_tri in khoi.items():
            chu_gt = str(gia_tri).strip().lower()
            if any(chu_gt.startswith(tien_to) or tien_to in chu_gt for tien_to in TIEN_TO_DEP_CAM) or ".." in chu_gt:
                return False, f"Từ chối phụ thuộc không an toàn trong package.json ({ten_goi}: {gia_tri!r})"

    if not lock.is_file():
        return False, "Từ chối trang-bu thiếu package-lock.json khi có package.json"
    try:
        du_lieu_lock = json.loads(lock.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, f"Từ chối trang-bu/package-lock.json không hợp lệ: {exc}"
    if not isinstance(du_lieu_lock, dict):
        return False, "Từ chối trang-bu/package-lock.json không phải object JSON"

    KHOA_DEP_TRONG_LOCK = frozenset(
        {"dependencies", "devDependencies", "optionalDependencies", "peerDependencies", "overrides"}
    )
    ngan_xep: list[object] = [du_lieu_lock]
    while ngan_xep:
        hien_tai = ngan_xep.pop()
        if isinstance(hien_tai, dict):
            for k, v in hien_tai.items():
                if k == "resolved":
                    if (
                        not isinstance(v, str)
                        or not v.startswith(TIEN_TO_REGISTRY_NPM)
                        or ".." in v
                        or "@" in v.split("://", 1)[-1].split("/", 1)[0]
                    ):
                        return False, f"Từ chối package-lock.json có resolved ngoài registry chuẩn: {v!r}"
                elif k == "version" and isinstance(v, str):
                    v_thap = v.strip().lower()
                    if any(v_thap.startswith(tp) for tp in TIEN_TO_DEP_CAM) or ".." in v_thap:
                        return False, f"Từ chối version không an toàn trong package-lock.json: {v!r}"
                elif k in KHOA_DEP_TRONG_LOCK and isinstance(v, dict):
                    for ten_dep, spec_dep in v.items():
                        if isinstance(spec_dep, str):
                            s_thap = spec_dep.strip().lower()
                            if any(s_thap.startswith(tp) or tp in s_thap for tp in TIEN_TO_DEP_CAM) or ".." in s_thap:
                                return False, f"Từ chối phụ thuộc không an toàn trong package-lock.json ({ten_dep}: {spec_dep!r})"
                        elif isinstance(spec_dep, (dict, list)):
                            ngan_xep.append(spec_dep)
                elif isinstance(v, (dict, list)):
                    ngan_xep.append(v)
        elif isinstance(hien_tai, list):
            ngan_xep.extend(hien_tai)

    return True, ""


def _xoa_duong_dan(duong: pathlib.Path) -> None:
    if duong.is_symlink() or duong.is_file():
        duong.unlink(missing_ok=True)
    elif duong.exists():
        shutil.rmtree(duong, ignore_errors=True)


def _tra_quyen_quan_tri(thu_muc: pathlib.Path) -> None:
    if os.name == "nt":
        return
    if _chay_root(["test", "!", "-L", str(thu_muc), "-a", "-d", str(thu_muc)], timeout=15).returncode != 0:
        return
    uid_goi = os.getuid()
    gid_goi = os.getgid()

    trang_bu = thu_muc / "trang-bu"
    nm_dir = trang_bu / "node_modules"
    co_nm_that = (
        _chay_root(["test", "!", "-L", str(trang_bu), "-a", "-d", str(trang_bu)], timeout=15).returncode == 0
        and _chay_root(["test", "!", "-L", str(nm_dir), "-a", "-d", str(nm_dir)], timeout=15).returncode == 0
    )
    if co_nm_that:
        _chay_root(
            ["find", "-P", str(thu_muc), "-path", str(nm_dir), "-prune", "-o", "-type", "l", "-delete"],
            timeout=60,
        )
    else:
        _chay_root(["find", "-P", str(thu_muc), "-type", "l", "-delete"], timeout=60)

    _chay_root(["chown", "-hRP", f"{uid_goi}:{gid_goi}", str(thu_muc)], timeout=120)
    _chmod_khong_symlink(thu_muc, "u+rwX", timeout=120)
    _chay_root(["chmod", "0700", str(thu_muc)], timeout=30)


def _khoa_quyen_truoc_kiem(thu_muc: pathlib.Path, file_features: str) -> tuple[bool, str]:
    """Cấp quyền tối thiểu cho congkiem: canh/, .khoa, .git, tests/nghiem-thu, node_modules đều chỉ đọc."""
    if os.name == "nt":
        return True, ""

    ok_sym, loi_sym = _kiem_khong_symlink_ngoai(thu_muc)
    if not ok_sym:
        return False, loi_sym

    ok_moc, loi_moc = _kiem_khong_tep_moc_cau(thu_muc)
    if not ok_moc:
        return False, loi_moc

    anh_dir = thu_muc / ".canh-tho" / "anh"
    if (thu_muc / ".canh-tho").is_symlink():
        return False, "Từ chối symlink .canh-tho"
    anh_dir.mkdir(parents=True, exist_ok=True)

    trang_bu = _trang_bu_that(thu_muc)
    cac_sticky: list[pathlib.Path] = [thu_muc]
    if trang_bu is not None:
        cac_sticky.append(trang_bu)

    co_tm_tests = (thu_muc / "tests").is_dir() and not (thu_muc / "tests").is_symlink()

    ung_vien_chi_doc: list[pathlib.Path] = [
        thu_muc / ".git",
        thu_muc / "canh",
        thu_muc / f"{file_features}.khoa",
        thu_muc / "pytest.ini",
        thu_muc / "tests" / "nghiem-thu",
    ]
    if trang_bu is not None:
        ung_vien_chi_doc.extend(
            [
                trang_bu / "node_modules",
                trang_bu / "package.json",
                trang_bu / "package-lock.json",
                trang_bu / "next.config.mjs",
                trang_bu / "pages",
            ]
        )
    for tep_khoa in thu_muc.glob("*.khoa"):
        if tep_khoa not in ung_vien_chi_doc:
            ung_vien_chi_doc.append(tep_khoa)
    muc_chi_doc = [p for p in ung_vien_chi_doc if p.exists() and not p.is_symlink()]

    r1 = _chay_root(["chown", "-hRP", f"{USER_CHAY_KIEM}:{USER_CHAY_KIEM}", str(thu_muc)], timeout=120)
    if r1.returncode != 0:
        return False, f"{CO_LOI_DONG_BO_VM}: Không đặt được quyền nhánh chạy kiểm: {r1.stderr}"

    for d_sticky in cac_sticky:
        _chay_root(["chown", "-h", f"root:{USER_CHAY_KIEM}", str(d_sticky)], timeout=30)
        _chay_root(["chmod", "1775", str(d_sticky)], timeout=30)

    if co_tm_tests:
        _chay_root(["chown", "-h", "root:root", str(thu_muc / "tests")], timeout=30)
        _chay_root(["chmod", "0755", str(thu_muc / "tests")], timeout=30)

    for p in muc_chi_doc:
        r_ro = _chay_root(["chown", "-hRP", "root:root", str(p)], timeout=120)
        if r_ro.returncode != 0:
            return False, f"{CO_LOI_DONG_BO_VM}: Không khoá chủ sở hữu {p.name}: {r_ro.stderr}"
        r_cm = _chmod_khong_symlink(p, "a+rX,go-w", timeout=120)
        if r_cm.returncode != 0:
            return False, f"{CO_LOI_DONG_BO_VM}: Không đặt chỉ đọc cho {p.name}: {r_cm.stderr}"

    return True, ""


def _chuan_bi_node_modules(thu_muc: pathlib.Path, goc_chay: pathlib.Path, env: dict[str, str]) -> tuple[bool, str]:
    raw_tb = thu_muc / "trang-bu"
    if raw_tb.is_symlink():
        return False, "Từ chối symlink tại trang-bu"
    if not raw_tb.exists():
        return True, ""
    trang_bu = _trang_bu_that(thu_muc)
    if trang_bu is None:
        return False, "Đường dẫn trang-bu không phải thư mục hợp lệ trong nhánh"

    pkg = trang_bu / "package.json"
    lock = trang_bu / "package-lock.json"
    dich_nm = trang_bu / "node_modules"
    for p_kiem in (pkg, lock, dich_nm):
        if p_kiem.is_symlink():
            return False, f"Từ chối symlink trong trang-bu: {p_kiem.name}"
    if not pkg.is_file():
        return True, ""

    ok_lock, loi_lock = _kiem_package_lock_an_toan(trang_bu)
    if not ok_lock:
        return False, loi_lock

    npm_bin = shutil.which("npm", path=env.get("PATH"))
    if not npm_bin:
        return True, "CẢNH BÁO: không tìm thấy npm trong PATH, bỏ qua chuẩn bị trang-bu/node_modules.\n"

    nguon_bam = lock.read_bytes()
    ma_bam = hashlib.sha256(nguon_bam).hexdigest()[:16]

    goc_kho = goc_chay / "cache-node-modules"
    goc_kho.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(goc_kho, 0o700)
    except OSError:
        pass

    kho_nm = goc_kho / ma_bam / "node_modules"
    dau_bam = dich_nm / ".cong_kiem_lock_sha256"

    shutil.rmtree(dich_nm, ignore_errors=True)
    if kho_nm.is_dir():
        cp = _chay_buoc(["cp", "-a", str(kho_nm), str(dich_nm)], env=env, timeout=180)
        if cp.returncode == 0 and not dich_nm.is_symlink():
            dau_bam.write_text(ma_bam, encoding="utf-8")
            return True, ""
        shutil.rmtree(dich_nm, ignore_errors=True)

    # Hạ quyền sang user congkiem (đã bị chặn metadata/dịch vụ nội bộ qua iptables) khi chạy npm ci
    if os.name != "nt":
        npm_cache_dir = pathlib.Path(env["NPM_CONFIG_CACHE"])
        home_dir = pathlib.Path(env["HOME"])
        tmp_dir = pathlib.Path(env["TMPDIR"])
        for d_phu in (trang_bu, npm_cache_dir, home_dir, tmp_dir):
            _chay_root(["chown", "-hRP", f"{USER_CHAY_KIEM}:{USER_CHAY_KIEM}", str(d_phu)], timeout=60)
        cap_env_npm = [f"{k}={v}" for k, v in sorted(env.items())]
        lenh_npm = [
            "systemd-run",
            "--scope",
            "--quiet",
            "-p",
            "MemoryMax=2G",
            "-p",
            "OOMPolicy=kill",
            "--",
            "/usr/bin/setpriv",
            f"--reuid={USER_CHAY_KIEM}",
            f"--regid={USER_CHAY_KIEM}",
            "--clear-groups",
            "--no-new-privs",
            "/usr/bin/env",
            "-i",
            *cap_env_npm,
            npm_bin,
            "ci",
            "--ignore-scripts",
            "--no-audit",
            "--no-fund",
        ]
        r = _chay_root(lenh_npm, cwd=trang_bu, timeout=420)
        _tra_quyen_quan_tri(thu_muc)
    else:
        r = _chay_buoc(
            [npm_bin, "ci", "--ignore-scripts", "--no-audit", "--no-fund"],
            cwd=trang_bu,
            env=env,
            timeout=420,
        )

    if r.returncode != 0:
        return False, f"{CO_LOI_DONG_BO_VM}: npm ci thất bại ({r.returncode}):\n{r.stdout}\n{r.stderr}"
    if dich_nm.is_symlink():
        dich_nm.unlink(missing_ok=True)
        return False, "Từ chối symlink phát sinh tại trang-bu/node_modules"

    ok_sym_nm, loi_sym_nm = _kiem_khong_symlink_ngoai(thu_muc)
    if not ok_sym_nm:
        shutil.rmtree(dich_nm, ignore_errors=True)
        return False, loi_sym_nm

    dau_bam.write_text(ma_bam, encoding="utf-8")
    shutil.rmtree(kho_nm, ignore_errors=True)
    kho_nm.parent.mkdir(parents=True, exist_ok=True)
    _chay_buoc(["cp", "-a", str(dich_nm), str(kho_nm)], env=env, timeout=180)
    return True, ""


def _bam_sha256_file(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _kiem_ref_khong_symlink_git(thu_muc: pathlib.Path, ref_dich: str, env: dict[str, str]) -> tuple[bool, str]:
    """Kiểm tra cây git của nhánh trước khi checkout: từ chối ngay nếu commit chứa symlink (mode 120000)."""
    r_ls = _chay_buoc(["git", "-C", str(thu_muc), "ls-tree", "-r", ref_dich], env=env, timeout=60)
    if r_ls.returncode != 0:
        return False, f"{CO_LOI_DONG_BO_VM}: Không đọc được cây git của {ref_dich}: {r_ls.stderr}"
    for dong in r_ls.stdout.splitlines():
        if dong.startswith("120000 "):
            ten_muc = dong.split("\t", 1)[-1] if "\t" in dong else dong
            return False, f"Từ chối nhánh chứa symlink trong commit git (mode 120000): {ten_muc}"
    return True, ""


def _dong_bo_nhanh(
    thu_muc: pathlib.Path,
    nhanh: str,
    file_features: str,
    repo_url: str,
    goc_chay: pathlib.Path,
    env: dict[str, str],
) -> tuple[bool, str, dict]:
    if (
        not isinstance(repo_url, str)
        or not repo_url.isascii()
        or ".." in repo_url.split("/")
        or not _MAU_REPO_URL.fullmatch(repo_url)
    ):
        raise ValueError(f"repo_url không hợp lệ: {repo_url!r}")

    thu_muc.parent.mkdir(parents=True, exist_ok=True)
    if thu_muc.is_symlink():
        thu_muc.unlink(missing_ok=True)
    if not (thu_muc / ".git").is_dir() or (thu_muc / ".git").is_symlink():
        shutil.rmtree(thu_muc, ignore_errors=True)
        thu_muc.mkdir(parents=True, exist_ok=True)
        for b in (
            ["git", "init", str(thu_muc)],
            ["git", "-C", str(thu_muc), "remote", "add", "origin", repo_url],
        ):
            r = _chay_buoc(b, env=env, timeout=60)
            if r.returncode != 0:
                return False, f"{CO_LOI_DONG_BO_VM}: {r.stdout}\n{r.stderr}", {}

    for b in (
        ["git", "-C", str(thu_muc), "config", "core.hooksPath", "/dev/null"],
        ["git", "-C", str(thu_muc), "config", "core.fsmonitor", "false"],
        ["git", "-C", str(thu_muc), "config", "core.symlinks", "false"],
        ["git", "-C", str(thu_muc), "remote", "set-url", "origin", repo_url],
    ):
        r = _chay_buoc(b, env=env, timeout=30)
        if r.returncode != 0:
            return False, f"{CO_LOI_DONG_BO_VM}: {r.stdout}\n{r.stderr}", {}

    refspecs = ["+refs/heads/main:refs/remotes/origin/main"]
    if nhanh != "main":
        refspecs.append(f"+refs/heads/{nhanh}:refs/remotes/origin/{nhanh}")

    r_fetch = _chay_buoc(
        ["git", "-C", str(thu_muc), "fetch", "--prune", "--no-tags", "origin", "--", *refspecs],
        env=env,
        timeout=300,
    )
    if r_fetch.returncode != 0:
        return False, f"{CO_LOI_DONG_BO_VM}: git fetch lỗi:\n{r_fetch.stdout}\n{r_fetch.stderr}", {}

    ref_main = "refs/remotes/origin/main"
    ref_dich = f"refs/remotes/origin/{nhanh}"

    ok_cay, loi_cay = _kiem_ref_khong_symlink_git(thu_muc, ref_dich, env)
    if not ok_cay:
        return False, loi_cay, {}

    tep_khoa_ten = f"{file_features}.khoa"
    for duong_bat_buoc in ("canh/cong_kiem.py", tep_khoa_ten):
        r_co = _chay_buoc(
            ["git", "-C", str(thu_muc), "cat-file", "-e", f"{ref_main}:{duong_bat_buoc}"],
            env=env,
            timeout=30,
        )
        if r_co.returncode != 0:
            return False, f"origin/main chưa có file bắt buộc {duong_bat_buoc}, từ chối chạy cổng kiểm.", {}

    if (thu_muc / "trang-bu").is_symlink():
        _xoa_duong_dan(thu_muc / "trang-bu")
    elif (thu_muc / "trang-bu" / "node_modules").is_symlink():
        _xoa_duong_dan(thu_muc / "trang-bu" / "node_modules")

    for b in (
        ["git", "-C", str(thu_muc), "checkout", "-f", "-B", nhanh, ref_dich],
        ["git", "-C", str(thu_muc), "reset", "--hard", ref_dich],
        ["git", "-C", str(thu_muc), "clean", "-fdx", "-e", "trang-bu/node_modules"],
    ):
        r = _chay_buoc(b, env=env, timeout=120)
        if r.returncode != 0:
            return False, f"{CO_LOI_DONG_BO_VM}: {r.stdout}\n{r.stderr}", {}

    ok_sym, loi_sym = _kiem_khong_symlink_ngoai(thu_muc)
    if not ok_sym:
        return False, loi_sym, {}

    for muc_xoa in (
        thu_muc / "canh",
        thu_muc / "tests" / "nghiem-thu",
        thu_muc / "pytest.ini",
        *thu_muc.glob("*.khoa"),
    ):
        _xoa_duong_dan(muc_xoa)
    if not (thu_muc / "tests").is_dir() or (thu_muc / "tests").is_symlink():
        _xoa_duong_dan(thu_muc / "tests")

    muc_tu_main = ["canh", tep_khoa_ten]
    for muc_them in ("tests/nghiem-thu", "pytest.ini"):
        r_co_them = _chay_buoc(
            ["git", "-C", str(thu_muc), "cat-file", "-e", f"{ref_main}:{muc_them}"],
            env=env,
            timeout=15,
        )
        if r_co_them.returncode == 0:
            muc_tu_main.append(muc_them)

    r_ls_khoa = _chay_buoc(
        ["git", "-C", str(thu_muc), "ls-tree", "--name-only", ref_main],
        env=env,
        timeout=15,
    )
    if r_ls_khoa.returncode == 0:
        for dong in r_ls_khoa.stdout.splitlines():
            ten_tep = dong.strip()
            if ten_tep.endswith(".khoa") and ten_tep not in muc_tu_main:
                muc_tu_main.append(ten_tep)

    r_canh = _chay_buoc(
        ["git", "-C", str(thu_muc), "checkout", ref_main, "--", *muc_tu_main],
        env=env,
        timeout=60,
    )
    if r_canh.returncode != 0:
        return False, f"{CO_LOI_DONG_BO_VM}: {r_canh.stdout}\n{r_canh.stderr}", {}

    ok_moc, loi_moc = _kiem_khong_tep_moc_cau(thu_muc)
    if not ok_moc:
        return False, loi_moc, {}

    ok_bc, loi_bc = _kiem_bang_chung_trong_nhanh(thu_muc, file_features)
    if not ok_bc:
        return False, loi_bc, {}

    tep_khoa_path = thu_muc / tep_khoa_ten
    tep_cong_path = thu_muc / "canh" / "cong_kiem.py"
    tep_pytest_ini = thu_muc / "pytest.ini"
    if not tep_khoa_path.is_file() or not tep_cong_path.is_file():
        return False, f"{CO_LOI_DONG_BO_VM}: Không khôi phục được {tep_khoa_ten} hoặc canh/cong_kiem.py từ origin/main.", {}

    r_rev_nhanh = _chay_buoc(["git", "-C", str(thu_muc), "rev-parse", "HEAD"], env=env, timeout=15)
    r_rev_main = _chay_buoc(["git", "-C", str(thu_muc), "rev-parse", ref_main], env=env, timeout=15)
    r_ff_main = _chay_buoc(["git", "-C", str(thu_muc), "show", f"{ref_main}:{file_features}"], env=env, timeout=30)

    meta = {
        "commit_nhanh": r_rev_nhanh.stdout.strip() if r_rev_nhanh.returncode == 0 else "",
        "commit_main": r_rev_main.stdout.strip() if r_rev_main.returncode == 0 else "",
        "bam_khoa": _bam_sha256_file(tep_khoa_path),
        "bam_cong_kiem": _bam_sha256_file(tep_cong_path),
        "bam_pytest_ini": _bam_sha256_file(tep_pytest_ini) if tep_pytest_ini.is_file() else "",
        "features_main_json": r_ff_main.stdout if r_ff_main.returncode == 0 else "",
    }

    ok_nm, canh_bao_nm = _chuan_bi_node_modules(thu_muc, goc_chay, env)
    if not ok_nm:
        return False, canh_bao_nm, meta
    return True, canh_bao_nm, meta


def _chay_kiem_duoi_systemd(
    lenh: list[str],
    cwd: pathlib.Path,
    env: dict[str, str],
    timeout: int,
) -> subprocess.CompletedProcess:
    if os.name != "nt" and not _la_root():
        cap_env = [f"{k}={v}" for k, v in sorted(env.items())]
        lenh_thuc = ["sudo", "-n", "/usr/bin/env", "-i", *cap_env, *lenh]
        return _chay_buoc(lenh_thuc, cwd=cwd, env={"PATH": "/usr/bin:/bin"}, timeout=timeout)
    return _chay_buoc(lenh, cwd=cwd, env=env, timeout=timeout)


def _chay_kiem_chi_tiet(
    nhanh: str,
    file_features: str,
    them: str = "",
    ram: str = "3G",
    goc_chay: pathlib.Path | None = None,
    repo_url: str = REPO_MAC_DINH,
    timeout: int = 1200,
) -> tuple[dict, dict]:
    goc = (pathlib.Path(goc_chay) if goc_chay is not None else _goc_chay_mac_dinh()).resolve()
    them_sach = _kiem_them(them)
    ten_unit = _ten_unit_mac_dinh(nhanh)
    lenh = _tao_lenh_chay(
        nhanh=nhanh,
        file_features=file_features,
        them=them_sach,
        ram=ram,
        goc_chay=goc,
        ten_unit=ten_unit,
    )
    thu_muc = thu_muc_nhanh(nhanh, goc_chay=goc)

    with khoa_luot(_duong_khoa_he_thong(goc)):
        ok_mt, loi_mt = _dam_bao_moi_truong_cach_ly(goc)
        if not ok_mt:
            return phan_loai(1, loi_mt), {"unit": ten_unit}

        _dung_unit_va_user(ten_unit)
        _tra_quyen_quan_tri(thu_muc)

        vung_tam = goc / "chay-tam" / nhanh.replace("/", "__")
        if os.name != "nt" and vung_tam.exists():
            _chay_root(["rm", "-rf", str(vung_tam)], timeout=60)
        else:
            shutil.rmtree(vung_tam, ignore_errors=True)

        home_tam = vung_tam / "home"
        tmp_tam = vung_tam / "tmp"
        pytest_tam = vung_tam / "pytest-tmp"
        npm_cache_tam = vung_tam / "npm-cache"
        for tm_con in (home_tam, tmp_tam, pytest_tam, npm_cache_tam):
            tm_con.mkdir(parents=True, exist_ok=True)

        env = _moi_truong_sach(home_tam=home_tam, tmp_tam=tmp_tam, npm_cache_tam=npm_cache_tam)
        meta: dict = {"unit": ten_unit}
        canh_bao_dau = ""
        try:
            ok, thong_bao, meta_db = _dong_bo_nhanh(
                thu_muc=thu_muc,
                nhanh=nhanh,
                file_features=file_features,
                repo_url=repo_url,
                goc_chay=goc,
                env=env,
            )
            meta.update(meta_db)
            if not ok:
                return phan_loai(1, thong_bao), meta
            canh_bao_dau = thong_bao

            for tm_lam_moi in (home_tam, tmp_tam):
                shutil.rmtree(tm_lam_moi, ignore_errors=True)
                tm_lam_moi.mkdir(parents=True, exist_ok=True)

            env_kiem = dict(env)
            env_kiem["PYTHONSAFEPATH"] = "1"
            env_kiem["PYTHONNOUSERSITE"] = "1"
            addopts_phan = [
                f"--rootdir={shlex.quote(thu_muc.as_posix())}",
                f"--confcutdir={shlex.quote((thu_muc / 'tests' / 'nghiem-thu').as_posix())}",
                f"--basetemp={shlex.quote((pytest_tam / 'run').as_posix())}",
            ]
            if (thu_muc / "pytest.ini").is_file():
                addopts_phan.insert(0, f"-c {shlex.quote((thu_muc / 'pytest.ini').as_posix())}")
            env_kiem["PYTEST_ADDOPTS"] = " ".join(addopts_phan)
            env_kiem["GIT_CONFIG_COUNT"] = "1"
            env_kiem["GIT_CONFIG_KEY_0"] = "safe.directory"
            env_kiem["GIT_CONFIG_VALUE_0"] = thu_muc.as_posix()

            # Luôn tính mới danh sách feature cần kiểm thêm và git diff ở MỌI lượt chạy (kể cả không truyền --them)
            tep_doi = vung_tam / "doi.txt"
            tep_doi.unlink(missing_ok=True)
            ds_them = [x for x in them_sach.split(",") if x] if them_sach else []
            tep_ff_nhanh = thu_muc / file_features
            if tep_ff_nhanh.is_file():
                for fid_moi in _tim_features_can_kiem_them(
                    meta.get("features_main_json", ""),
                    tep_ff_nhanh.read_text(encoding="utf-8", errors="replace"),
                ):
                    if fid_moi not in ds_them:
                        ds_them.append(fid_moi)

            r_diff = _chay_buoc(
                ["git", "-C", str(thu_muc), "diff", "--name-only", "refs/remotes/origin/main...HEAD"],
                env=env,
                timeout=60,
            )
            if r_diff.returncode == 0:
                for dong_doi in r_diff.stdout.splitlines():
                    phan = dong_doi.strip().replace("\\", "/").split("/")
                    if len(phan) >= 2 and phan[0] == "bang-chung" and _MAU_MA_FEATURE.fullmatch(phan[1]):
                        if phan[1] not in ds_them:
                            ds_them.append(phan[1])
                if nhanh != "main" or them_sach or r_diff.stdout.strip():
                    tep_doi.write_text(r_diff.stdout, encoding="utf-8")
                    env_kiem["CONG_KIEM_DOI"] = tep_doi.as_posix()

            if ds_them:
                env_kiem["CONG_KIEM_THEM"] = ",".join(ds_them)

            if os.name != "nt":
                _chay_root(["chown", "-h", "root:root", str(vung_tam)], timeout=30)
                _chay_root(["chmod", "0755", str(vung_tam)], timeout=30)
                if tep_doi.is_file():
                    _chay_root(["chown", "-h", "root:root", str(tep_doi)], timeout=15)
                    _chay_root(["chmod", "0644", str(tep_doi)], timeout=15)
                for tm_ghi in (home_tam, tmp_tam, pytest_tam, npm_cache_tam):
                    _chay_root(["chown", "-hRP", f"{USER_CHAY_KIEM}:{USER_CHAY_KIEM}", str(tm_ghi)], timeout=30)
                    _chay_root(["chmod", "0700", str(tm_ghi)], timeout=15)

            ok_quyen, loi_quyen = _khoa_quyen_truoc_kiem(thu_muc, file_features)
            if not ok_quyen:
                return phan_loai(1, loi_quyen), meta

            luc_bat_dau_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            r = _chay_kiem_duoi_systemd(lenh, cwd=thu_muc, env=env_kiem, timeout=timeout)
            dau_ra = canh_bao_dau + (r.stdout or "") + (r.stderr or "")
            if r.returncode != 0 and _ket_qua_systemd_oom(ten_unit, tu_luc_iso=luc_bat_dau_iso):
                dau_ra += "\nsystemd scope Result=oom-kill"

            _dung_unit_va_user(ten_unit)
            _tra_quyen_quan_tri(thu_muc)

            tep_khoa_path = thu_muc / f"{file_features}.khoa"
            tep_cong_path = thu_muc / "canh" / "cong_kiem.py"
            tep_pytest_ini = thu_muc / "pytest.ini"
            try:
                toan_ven = (
                    tep_khoa_path.is_file()
                    and tep_cong_path.is_file()
                    and _bam_sha256_file(tep_khoa_path) == meta.get("bam_khoa")
                    and _bam_sha256_file(tep_cong_path) == meta.get("bam_cong_kiem")
                    and (
                        not meta.get("bam_pytest_ini")
                        or (
                            tep_pytest_ini.is_file()
                            and _bam_sha256_file(tep_pytest_ini) == meta.get("bam_pytest_ini")
                        )
                    )
                )
            except OSError:
                toan_ven = False
            if not toan_ven:
                return phan_loai(1, dau_ra + "\nPHÁT HIỆN SỬA TRÁI PHÉP mốc .khoa, pytest.ini hoặc canh/cong_kiem.py."), meta

            return phan_loai(r.returncode, dau_ra), meta
        except subprocess.TimeoutExpired as exc:
            _dung_unit_va_user(ten_unit)
            out = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
            err = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
            dau_ra = f"{canh_bao_dau}{out}\n{err}\nsubprocess.TimeoutExpired: {exc}"
            return phan_loai(124, dau_ra), meta
        except OSError as exc:
            return phan_loai(1, f"{canh_bao_dau}{CO_LOI_DONG_BO_VM}: OSError: {exc}"), meta
        finally:
            _dung_unit_va_user(ten_unit)
            _tra_quyen_quan_tri(thu_muc)
            if os.name != "nt" and vung_tam.exists():
                _chay_root(["rm", "-rf", str(vung_tam)], timeout=60)
            else:
                shutil.rmtree(vung_tam, ignore_errors=True)


def chay_kiem(
    nhanh: str,
    file_features: str,
    them: str = "",
    ram: str = "3G",
    goc_chay: pathlib.Path | None = None,
    repo_url: str = REPO_MAC_DINH,
    timeout: int = 1200,
) -> dict:
    """Thực thi trọn vẹn một lượt cổng kiểm trên VM dưới khoá flock, systemd-run, netns và user tách biệt."""
    ket_qua, _ = _chay_kiem_chi_tiet(
        nhanh=nhanh,
        file_features=file_features,
        them=them,
        ram=ram,
        goc_chay=goc_chay,
        repo_url=repo_url,
        timeout=timeout,
    )
    return ket_qua


def _ten_may() -> str:
    ten = socket.gethostname().strip()
    return ten.split(".")[0] if ten else "unknown"


def _ma_thoat_cli(ma: int) -> int:
    if ma == 0:
        return 0
    if 1 <= ma <= 255:
        return ma
    if ma < 0 and (128 + abs(ma)) <= 255:
        return 128 + abs(ma)
    return 1


def main(argv: list[str] | None = None) -> int:
    """CLI cổng kiểm VM: in một dòng JSON phan_loai ra stdout và trả mã thoát tương ứng ket_qua['ma']."""
    p = argparse.ArgumentParser(description="Chạy cổng kiểm trên VM dưới systemd-run MemoryMax và flock.")
    p.add_argument("--nhanh", required=True, help="Nhánh cần kiểm (main hoặc tu-dong/engine-tN)")
    p.add_argument("--features", required=True, help="Tên file features-dot*.json")
    p.add_argument("--them", default="", help="Danh sách feature ID kiểm thêm, phân tách dấu phẩy")
    p.add_argument("--ram", default="3G", help="Trần bộ nhớ cho systemd-run MemoryMax (mặc định: 3G)")
    p.add_argument("--goc-chay", default=None, help="Thư mục gốc lưu kho nhánh trên VM")
    p.add_argument("--repo-url", default=os.environ.get("CONG_KIEM_REPO_URL", REPO_MAC_DINH), help="URL kho git")
    p.add_argument("--timeout", type=int, default=1200, help="Giới hạn thời gian lượt chạy (giây)")
    p.add_argument("--ghi-bang-chung", default=None, help="Đường dẫn ghi thêm JSON bằng chứng trên VM")
    args = p.parse_args(argv)

    try:
        _tao_lenh_chay(
            nhanh=args.nhanh,
            file_features=args.features,
            them=args.them,
            ram=args.ram,
            goc_chay=pathlib.Path(args.goc_chay) if args.goc_chay else None,
        )
    except ValueError as exc:
        print(json.dumps({"ma": 2, "loi_may": False, "ra": str(exc)}, ensure_ascii=False))
        return 2

    t0 = time.monotonic()
    ket_qua, meta = _chay_kiem_chi_tiet(
        nhanh=args.nhanh,
        file_features=args.features,
        them=args.them,
        ram=args.ram,
        goc_chay=pathlib.Path(args.goc_chay) if args.goc_chay else None,
        repo_url=args.repo_url,
        timeout=args.timeout,
    )
    giay = round(max(time.monotonic() - t0, 0.001), 3)

    if args.ghi_bang_chung:
        bc_path = pathlib.Path(args.ghi_bang_chung)
        bc_path.parent.mkdir(parents=True, exist_ok=True)
        bc = {
            "luc": datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec="seconds"),
            "may": _ten_may(),
            "nhanh": args.nhanh,
            "features": args.features,
            "unit": meta.get("unit", ""),
            "commit_nhanh": meta.get("commit_nhanh", ""),
            "commit_main": meta.get("commit_main", ""),
            "bam_khoa": meta.get("bam_khoa", ""),
            "bam_cong_kiem": meta.get("bam_cong_kiem", ""),
            "ma": ket_qua["ma"],
            "loi_may": ket_qua["loi_may"],
            "giay": giay,
            "ram": args.ram,
            "ra_cuoi": ket_qua["ra"][-GIOI_HAN_RA_BANG_CHUNG:],
        }
        bc_path.write_text(json.dumps(bc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps(ket_qua, ensure_ascii=False))
    return _ma_thoat_cli(ket_qua["ma"])


if __name__ == "__main__":
    raise SystemExit(main())
