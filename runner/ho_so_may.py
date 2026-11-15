"""Thu thập hồ sơ máy và năng lực cho linhx-runner (chỉ dùng Python stdlib)."""
from __future__ import annotations

import ctypes
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time

try:
    from runner import linhx_runner
except ImportError:
    import linhx_runner

HO_SO_CHU_KY_PHUT_MAC_DINH = 60.0
_EMAIL_RE = re.compile(r"[^\s@<>\"']+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")
_SECRET_KEY_WORDS = ("password", "passwd", "secret", "token", "api_key", "apikey", "email")
_SECRET_VAL_PATTERNS = (
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{16,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._-]{12,}\b", re.IGNORECASE),
)


class _LogicalProcessorInfo(ctypes.Structure):
    _fields_ = [
        ("ProcessorMask", ctypes.c_size_t),
        ("Relationship", ctypes.c_int),
        ("Reserved", ctypes.c_ulonglong * 2),
    ]


def loc_thong_tin_nhay_cam(gia_tri: str) -> str:
    """Loại bỏ email, token hoặc chuỗi bí mật vô tình lọt vào văn bản."""
    s = str(gia_tri or "")
    s = _EMAIL_RE.sub("[ẩn]", s)
    for pat in _SECRET_VAL_PATTERNS:
        s = pat.sub("[ẩn]", s)
    return s.strip()


def lam_sach_du_lieu_ho_so(obj):
    """Đệ quy kiểm tra và lọc bỏ mọi khóa nhạy cảm (mật khẩu, token, email) khỏi dict/list."""
    if isinstance(obj, dict):
        sach = {}
        for k, v in obj.items():
            k_str = str(k)
            k_low = k_str.lower()
            if any(tu in k_low for tu in _SECRET_KEY_WORDS):
                continue
            sach[k_str] = lam_sach_du_lieu_ho_so(v)
        return sach
    if isinstance(obj, list):
        return [lam_sach_du_lieu_ho_so(x) for x in obj]
    if isinstance(obj, str):
        return loc_thong_tin_nhay_cam(obj)
    return obj


def _doc_cpu_ten() -> str:
    if os.name == "nt":
        try:
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",
            ) as k:
                val, _ = winreg.QueryValueEx(k, "ProcessorNameString")
                if val and str(val).strip():
                    return " ".join(str(val).strip().split())
        except OSError:
            pass
    else:
        p = Path("/proc/cpuinfo")
        if p.is_file():
            try:
                for dong in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                    if ":" in dong:
                        k, v = dong.split(":", 1)
                        if k.strip().lower() in ("model name", "hardware", "cpu"):
                            if v.strip():
                                return " ".join(v.strip().split())
            except OSError:
                pass
    ten = platform.processor() or platform.machine() or "chưa rõ"
    return " ".join(ten.strip().split()) or "chưa rõ"


def _doc_cpu_nhan_vat_ly(so_luong: int) -> int:
    if os.name == "nt":
        k32 = getattr(getattr(ctypes, "windll", None), "kernel32", None)
        if k32 is not None and hasattr(k32, "GetLogicalProcessorInformation"):
            try:
                sz = ctypes.c_ulong(0)
                k32.GetLogicalProcessorInformation(None, ctypes.byref(sz))
                kich_thuoc_muc = ctypes.sizeof(_LogicalProcessorInfo)
                if sz.value > 0 and kich_thuoc_muc > 0:
                    so_muc = sz.value // kich_thuoc_muc
                    buf = (_LogicalProcessorInfo * so_muc)()
                    if k32.GetLogicalProcessorInformation(buf, ctypes.byref(sz)):
                        nhan = sum(1 for item in buf if item.Relationship == 0)
                        if nhan > 0:
                            return int(nhan)
            except Exception:
                pass
    else:
        p = Path("/proc/cpuinfo")
        if p.is_file():
            try:
                cap_nhan = set()
                phys_id = "0"
                for dong in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                    if not dong.strip():
                        phys_id = "0"
                        continue
                    if ":" not in dong:
                        continue
                    k, v = dong.split(":", 1)
                    kl = k.strip().lower()
                    if kl == "physical id":
                        phys_id = v.strip()
                    elif kl == "core id":
                        cap_nhan.add((phys_id, v.strip()))
                if cap_nhan:
                    return len(cap_nhan)
            except OSError:
                pass
    return max(1, int(so_luong))


def doc_thong_tin_cpu() -> dict:
    """Trả về thông tin CPU: ten, nhan, luong."""
    luong = max(1, int(os.cpu_count() or 1))
    nhan = _doc_cpu_nhan_vat_ly(luong)
    return {
        "ten": _doc_cpu_ten(),
        "nhan": nhan,
        "luong": luong,
    }


def doc_thong_tin_ram() -> dict:
    """Trả về thông tin RAM (GiB): tong_gb, trong_gb."""
    tong_gb = None
    trong_gb = None
    if os.name == "nt":
        k32 = getattr(getattr(ctypes, "windll", None), "kernel32", None)
        if k32 is not None:
            st = linhx_runner._MemoryStatusEx()
            st.dwLength = ctypes.sizeof(linhx_runner._MemoryStatusEx)
            if k32.GlobalMemoryStatusEx(ctypes.byref(st)):
                tong_gb = round(float(st.ullTotalPhys) / float(1024 ** 3), 2)
                trong_gb = round(float(st.ullAvailPhys) / float(1024 ** 3), 2)
    else:
        p = Path("/proc/meminfo")
        if p.is_file():
            try:
                thong_so = {}
                for dong in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                    if ":" not in dong:
                        continue
                    k, v = dong.split(":", 1)
                    phan = v.strip().split()
                    if phan and phan[0].isdigit():
                        thong_so[k.strip()] = int(phan[0])
                if "MemTotal" in thong_so:
                    tong_gb = round(float(thong_so["MemTotal"]) / float(1024 ** 2), 2)
                if "MemAvailable" in thong_so:
                    trong_gb = round(float(thong_so["MemAvailable"]) / float(1024 ** 2), 2)
                elif "MemFree" in thong_so:
                    kb = thong_so["MemFree"] + thong_so.get("Buffers", 0) + thong_so.get("Cached", 0)
                    trong_gb = round(float(kb) / float(1024 ** 2), 2)
            except OSError:
                pass
        if (tong_gb is None or trong_gb is None) and hasattr(os, "sysconf"):
            try:
                co_trang = os.sysconf("SC_PAGE_SIZE")
                if tong_gb is None and "SC_PHYS_PAGES" in os.sysconf_names:
                    tong_trang = os.sysconf("SC_PHYS_PAGES")
                    if tong_trang > 0 and co_trang > 0:
                        tong_gb = round(float(tong_trang * co_trang) / float(1024 ** 3), 2)
                if trong_gb is None and "SC_AVPHYS_PAGES" in os.sysconf_names:
                    trong_trang = os.sysconf("SC_AVPHYS_PAGES")
                    if trong_trang > 0 and co_trang > 0:
                        trong_gb = round(float(trong_trang * co_trang) / float(1024 ** 3), 2)
            except (ValueError, OSError):
                pass
    if trong_gb is None:
        ram_fb = linhx_runner._doc_ram_he_thong_gb()
        if ram_fb is not None:
            trong_gb = round(float(ram_fb), 2)
    return {
        "tong_gb": tong_gb if tong_gb is not None else 0.0,
        "trong_gb": trong_gb if trong_gb is not None else 0.0,
    }


def doc_thong_tin_gpu() -> list[dict]:
    """Trả về danh sách GPU: [{"ten": ..., "vram_gb": ...}]."""
    ds_gpu: list[dict] = []
    if os.name == "nt":
        try:
            import winreg

            duong_lop = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, duong_lop) as khoa_lop:
                idx = 0
                da_thay = set()
                while True:
                    try:
                        ten_con = winreg.EnumKey(khoa_lop, idx)
                        idx += 1
                    except OSError:
                        break
                    if not ten_con.isdigit():
                        continue
                    try:
                        with winreg.OpenKey(khoa_lop, ten_con) as sk:
                            ten_gpu, _ = winreg.QueryValueEx(sk, "DriverDesc")
                            ten_sach = " ".join(str(ten_gpu or "").strip().split())
                            if not ten_sach:
                                continue
                            # Bỏ qua adapter ảo từ xa phổ biến nếu không có phần cứng thật
                            low = ten_sach.lower()
                            if "microsoft basic display" in low or "remote desktop" in low:
                                continue
                            vram_bytes = None
                            for ten_vram in (
                                "HardwareInformation.qwMemorySize",
                                "HardwareInformation.MemorySize",
                            ):
                                try:
                                    raw_v, _ = winreg.QueryValueEx(sk, ten_vram)
                                    if isinstance(raw_v, bytes) and raw_v:
                                        val_int = int.from_bytes(raw_v, "little", signed=False)
                                    elif isinstance(raw_v, int):
                                        val_int = raw_v
                                    else:
                                        val_int = 0
                                    if val_int > 0:
                                        vram_bytes = val_int
                                        break
                                except OSError:
                                    continue
                            vram_gb = round(float(vram_bytes) / float(1024 ** 3), 2) if vram_bytes else None
                            khoa_duy_nhat = (ten_sach, vram_gb)
                            if khoa_duy_nhat not in da_thay:
                                da_thay.add(khoa_duy_nhat)
                                ds_gpu.append({"ten": ten_sach, "vram_gb": vram_gb})
                    except OSError:
                        continue
        except OSError:
            pass
    return ds_gpu


def doc_thong_tin_o_dia(thu_muc_tham_chieu: Path | None = None) -> list[dict]:
    """Đọc dung lượng tổng/trống (GiB) của các ổ đĩa cố định trên máy."""
    ket_qua: list[dict] = []
    if os.name == "nt":
        k32 = getattr(getattr(ctypes, "windll", None), "kernel32", None)
        bitmask = k32.GetLogicalDrives() if k32 is not None else 0
        for i in range(26):
            if not (bitmask & (1 << i)):
                continue
            ky_tu = chr(65 + i)
            goc_o = f"{ky_tu}:\\"
            if k32 is not None:
                loai_o = k32.GetDriveTypeW(goc_o)
                # DRIVE_FIXED = 3
                if loai_o != 3:
                    continue
            try:
                st = shutil.disk_usage(goc_o)
                ket_qua.append(
                    {
                        "o": f"{ky_tu}:",
                        "tong_gb": round(float(st.total) / float(1024 ** 3), 2),
                        "trong_gb": round(float(st.free) / float(1024 ** 3), 2),
                    }
                )
            except OSError:
                continue
    else:
        cac_diem = ["/"]
        if thu_muc_tham_chieu is not None:
            cac_diem.append(str(thu_muc_tham_chieu))
        da_do_dev = set()
        for diem in cac_diem:
            p = Path(diem)
            if not p.exists():
                continue
            try:
                dev_id = p.stat().st_dev
                if dev_id in da_do_dev:
                    continue
                da_do_dev.add(dev_id)
                st = shutil.disk_usage(str(p))
                nhan = "/" if diem == "/" else str(p.resolve())
                ket_qua.append(
                    {
                        "o": nhan,
                        "tong_gb": round(float(st.total) / float(1024 ** 3), 2),
                        "trong_gb": round(float(st.free) / float(1024 ** 3), 2),
                    }
                )
            except OSError:
                continue
    return ket_qua


def doc_thong_tin_agy(agy_cmd: str = "agy", chay_lenh_fn=None) -> dict:
    """Tìm đường dẫn và đọc phiên bản agy (tiền cảnh, timeout ngắn, không lộ bí mật)."""
    lenh = (agy_cmd or "agy").strip() or "agy"
    duong_dan = ""
    p_UngVien = Path(lenh)
    if p_UngVien.is_file():
        duong_dan = str(p_UngVien)
    else:
        tim = shutil.which(lenh)
        if tim:
            duong_dan = str(tim)
        else:
            mac_dinh_home = Path.home() / ".gemini" / "bin" / ("agy.exe" if os.name == "nt" else "agy")
            if mac_dinh_home.is_file():
                duong_dan = str(mac_dinh_home)

    phien_ban = ""
    thuc_thi = duong_dan or lenh
    ham_chay = chay_lenh_fn or subprocess.run
    if duong_dan or chay_lenh_fn is not None:
        kw = {"creationflags": 0x08000000} if os.name == "nt" else {}
        try:
            proc = ham_chay(
                [thuc_thi, "--version"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=5,
                **kw,
            )
            dau_ra = (proc.stdout or proc.stderr or "").strip()
            if proc.returncode == 0 and dau_ra:
                dong_dau = dau_ra.splitlines()[0].strip()
                phien_ban = loc_thong_tin_nhay_cam(dong_dau)[:120]
        except Exception:
            phien_ban = ""

    return {
        "co": bool(duong_dan or phien_ban),
        "duong_dan": loc_thong_tin_nhay_cam(duong_dan or lenh),
        "phien_ban": phien_ban or "chưa rõ",
    }


def _ten_profile_hop_le(ten: str) -> str:
    """Lọc tên hiển thị của profile Chrome, bỏ nếu là địa chỉ email."""
    s = " ".join(str(ten or "").strip().split())
    if not s:
        return ""
    if "@" in s and _EMAIL_RE.search(s):
        return ""
    return loc_thong_tin_nhay_cam(s)[:80]


def doc_thong_tin_chrome(thu_muc_user_data: Path | None = None, duong_dan_exe: str | None = None) -> dict:
    """Kiểm tra Chrome có cài không và đọc danh sách tên hiển thị profile (KHÔNG lấy email)."""
    exe_found = ""
    if duong_dan_exe is not None:
        exe_found = duong_dan_exe
    else:
        ung_vien_exe = []
        if os.name == "nt":
            for bien in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
                goc = os.environ.get(bien, "").strip()
                if goc:
                    ung_vien_exe.append(Path(goc) / "Google" / "Chrome" / "Application" / "chrome.exe")
        else:
            for ten_bin in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
                w = shutil.which(ten_bin)
                if w:
                    ung_vien_exe.append(Path(w))
        for p in ung_vien_exe:
            if p.is_file():
                exe_found = str(p)
                break

    if thu_muc_user_data is not None:
        ud = Path(thu_muc_user_data)
    elif os.name == "nt" and os.environ.get("LOCALAPPDATA", "").strip():
        ud = Path(os.environ["LOCALAPPDATA"].strip()) / "Google" / "Chrome" / "User Data"
    elif sys.platform == "darwin":
        ud = Path.home() / "Library" / "Application Support" / "Google" / "Chrome"
    else:
        ud = Path.home() / ".config" / "google-chrome"

    profiles: list[str] = []
    tep_local_state = ud / "Local State"
    if tep_local_state.is_file():
        try:
            du_lieu = json.loads(tep_local_state.read_text(encoding="utf-8", errors="ignore"))
            info_cache = (du_lieu.get("profile") or {}).get("info_cache") or {}
            if isinstance(info_cache, dict):
                for thu_muc_prof in sorted(info_cache.keys()):
                    muc = info_cache.get(thu_muc_prof)
                    if not isinstance(muc, dict):
                        continue
                    # Chỉ đọc trường 'name' hiển thị, tuyệt đối không đọc user_name / gaia / email
                    ten_hien_thi = _ten_profile_hop_le(muc.get("name") or "")
                    nhan = ten_hien_thi if ten_hien_thi else str(thu_muc_prof)
                    if nhan and nhan not in profiles:
                        profiles.append(nhan)
        except (OSError, ValueError, TypeError):
            pass

    co_chrome = bool(exe_found or ud.is_dir())
    return {
        "co": co_chrome,
        "profiles": profiles,
    }


def _phan_tich_iso_epoch(chuoi_iso: str) -> float | None:
    s = str(chuoi_iso or "").strip()
    if not s:
        return None
    if s.endswith(("Z", "z")):
        s = s[:-1] + "+00:00"
    elif len(s) >= 5 and (s[-5] in "+-") and s[-4:].isdigit():
        s = s[:-2] + ":" + s[-2:]
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except ValueError:
        return None


def dem_phieu_24h_qua(wt: Path | None, ma_may: str, bay_gio_epoch: float | None = None) -> dict:
    """Đếm số phiếu xong và lỗi/dừng của `ma_may` trong 24 giờ qua trên nhánh hang-doi."""
    ket_qua = {"xong": 0, "loi": 0}
    if wt is None or not Path(wt).exists():
        return ket_qua
    wt_path = Path(wt)
    goc_hd = (wt_path / "hang-doi") if (wt_path / "hang-doi").exists() or not (wt_path / "xong").exists() else wt_path
    tm_xong = goc_hd / "xong"
    if not tm_xong.is_dir():
        return ket_qua

    now_ts = float(bay_gio_epoch if bay_gio_epoch is not None else time.time())
    moc_24h = now_ts - 86400.0
    may_chuan = str(ma_may or "").strip().lower()

    # Đọc thời điểm commit git nếu có để chính xác ngay cả khi vừa checkout worktree
    git_ts: dict[str, int] = {}
    if (wt_path / ".git").exists():
        kw = {"creationflags": 0x08000000} if os.name == "nt" else {}
        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"
        try:
            proc = subprocess.run(
                ["git", "-c", "core.quotepath=false", "log", "--since=26.hours", "--format=COMMIT|%ct", "--name-only"],
                cwd=str(wt_path),
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=15,
                **kw,
            )
            if proc.returncode == 0:
                cur = None
                for raw in proc.stdout.splitlines():
                    line = raw.strip()
                    if not line:
                        continue
                    if line.startswith("COMMIT|"):
                        try:
                            cur = int(line.split("|", 1)[1])
                        except ValueError:
                            cur = None
                    elif cur is not None and line not in git_ts:
                        git_ts[line] = cur
        except Exception:
            pass

    for tm_phieu in tm_xong.iterdir():
        if not tm_phieu.is_dir():
            continue
        tep_kq = tm_phieu / "KET-QUA.md"
        if not tep_kq.is_file():
            continue
        try:
            van_ban = tep_kq.read_text(encoding="utf-8", errors="replace").lstrip("\ufeff")
        except OSError:
            continue
        may_phieu = ""
        trang_thai = ""
        xong_luc = ""
        for dong in van_ban.splitlines()[:20]:
            s = dong.strip()
            if not s:
                break
            if ":" not in s:
                continue
            k, v = s.split(":", 1)
            kl = k.strip().lower()
            vl = v.strip()
            if kl == "may":
                may_phieu = vl.lower()
            elif kl == "trang_thai":
                trang_thai = vl.lower()
            elif kl in ("xong_luc", "luc"):
                xong_luc = vl
        if may_phieu != may_chuan:
            continue

        ts = _phan_tich_iso_epoch(xong_luc)
        if ts is None:
            try:
                rel = tep_kq.relative_to(wt_path).as_posix()
                if rel in git_ts:
                    ts = float(git_ts[rel])
            except ValueError:
                pass
        if ts is None:
            try:
                ts = float(tep_kq.stat().st_mtime)
            except OSError:
                continue

        if ts < moc_24h or ts > now_ts + 3600:
            continue
        if trang_thai == "xong":
            ket_qua["xong"] += 1
        elif trang_thai in ("loi", "dung"):
            ket_qua["loi"] += 1
    return ket_qua


def thu_thap_ho_so_may(
    cfg: dict,
    wt: Path | None = None,
    chay_lenh_fn=None,
    thu_muc_chrome: Path | None = None,
    duong_dan_chrome_exe: str | None = None,
    bay_gio_epoch: float | None = None,
) -> dict:
    """Thu thập toàn bộ hồ sơ máy an toàn (không chứa mật khẩu, token, email)."""
    ma_may = str(cfg.get("tho") or platform.node() or "may").strip().lower()
    vai_tro = str(cfg.get("vai_tro") or os.environ.get("LINHX_VAI") or "").strip()
    so_phieu = linhx_runner._ep_so_nguyen_khong_am(cfg.get("so_phieu"), linhx_runner.SO_PHIEU_CODE_MAC_DINH)
    nhan_bat_ky = linhx_runner._ep_cong_tac(cfg.get("nhan_bat_ky"), bool(linhx_runner.NHAN_BAT_KY_MAC_DINH))

    tm_tham_chieu = Path(cfg["thu_muc"]) if cfg.get("thu_muc") else linhx_runner.GOC
    ho_so = {
        "ma_may": ma_may,
        "ten_windows": platform.node() or ma_may,
        "he_dieu_hanh": f"{platform.system()} {platform.release()}".strip(),
        "vai_tro": vai_tro,
        "cpu": doc_thong_tin_cpu(),
        "ram": doc_thong_tin_ram(),
        "gpu": doc_thong_tin_gpu(),
        "o_dia": doc_thong_tin_o_dia(tm_tham_chieu),
        "agy": doc_thong_tin_agy(str(cfg.get("agy") or "agy"), chay_lenh_fn=chay_lenh_fn),
        "python": platform.python_version(),
        "chrome": doc_thong_tin_chrome(thu_muc_user_data=thu_muc_chrome, duong_dan_exe=duong_dan_chrome_exe),
        "nhan_phieu": {
            "so_phieu": so_phieu,
            "nhan_bat_ky": bool(nhan_bat_ky),
            "che_do_nhan": "bat-ky" if nhan_bat_ky else "chi-dich-danh",
        },
        "thong_ke_24h": dem_phieu_24h_qua(wt, ma_may, bay_gio_epoch=bay_gio_epoch),
        "cap_nhat_luc": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    return lam_sach_du_lieu_ho_so(ho_so)


def _ban_so_sanh_ho_so(ho_so: dict) -> dict:
    """Tạo bản sao chuẩn hóa để so sánh hồ sơ có thực sự thay đổi không (bỏ qua cap_nhat_luc và biến động nhỏ <0.5GB)."""
    ban = json.loads(json.dumps(ho_so))
    ban.pop("cap_nhat_luc", None)
    ram = ban.get("ram")
    if isinstance(ram, dict) and isinstance(ram.get("trong_gb"), (int, float)):
        ram["trong_gb"] = round(float(ram["trong_gb"]) * 2.0) / 2.0
    o_dia = ban.get("o_dia")
    if isinstance(o_dia, list):
        for od in o_dia:
            if isinstance(od, dict) and isinstance(od.get("trong_gb"), (int, float)):
                od["trong_gb"] = round(float(od["trong_gb"]) * 2.0) / 2.0
    return ban


def ho_so_da_doi(ho_so_cu: dict | None, ho_so_moi: dict) -> bool:
    """Trả về True nếu hồ sơ mới khác với hồ sơ cũ đang lưu trên nhánh hang-doi."""
    if not isinstance(ho_so_cu, dict) or not ho_so_cu:
        return True
    return _ban_so_sanh_ho_so(ho_so_cu) != _ban_so_sanh_ho_so(ho_so_moi)
