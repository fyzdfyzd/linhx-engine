"""linhx-runner: tho nhan viec cua LINHX ENGINE.

Chay o bat cu dau (may cty Windows, MSI, container tren cloud). Chi KEO viec qua HTTPS,
khong mo cong. Server chi gui DE (chu), khong bao gio gui lenh shell.

Cau hinh bang bien moi truong hoac file tho.env canh script:
  LINHX_NGUON   engine (mac dinh) hoac github (nhanh hang-doi)
  LINHX_URL     vd https://engine.linhx.vn
  LINHX_TOKEN   key:secret (bench execute linhx_worker.setup.tao_tho)
  LINHX_THO     ma tho, vd may-cty / may-1
  AGY_CMD       duong dan agy (mac dinh: agy)
  AGY_ARGS      them co cho agy (mac dinh: --output-format json)
  LINHX_THU_MUC thu muc lam viec cua agy (mac dinh: ./viec)
  LINHX_NGHI    giay giua 2 lan hoi (mac dinh 15)
  LINHX_SO_PHIEU        so phieu code chay song song toi da tren moi may (mac dinh 1)
  LINHX_TRAN_PHUT       tran phut toi da moi phieu truoc khi dung agy (mac dinh 40)
  LINHX_KHONG_TIEN_PHUT so phut khong tien truoc khi dung agy (mac dinh 10)
  LINHX_RAM_TOI_THIEU_GB nguong RAM trong toi thieu de nhan phieu (mac dinh 1.5)
Chi stdlib, Python >= 3.9.
"""
import ctypes
import json
import os
import platform
import shlex
import signal
import subprocess
import sys
import threading
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PHIEN_BAN = "0.1.1"
DE_DAI = 6000  # ky tu; dai hon thi dua de qua file
PHUT_TOI_DA_MAC_DINH = 40
PHUT_KHONG_TIEN_MAC_DINH = 10
NGUONG_RAM_TRONG_GB = 1.5
SO_PHIEU_CODE_MAC_DINH = 1
GOC = Path(__file__).resolve().parent

_SUBPROCESS_RUN_GOC = subprocess.run
_POPEN_GOC = subprocess.Popen
_tao_tien_trinh_agy = None
_dong_ho = None
_ngu = None


def _gio() -> float:
    return _dong_ho() if _dong_ho is not None else time.monotonic()


def _tam_nghi(giay: float) -> None:
    if _ngu is not None:
        _ngu(giay)
    else:
        time.sleep(giay)


def _ep_so_duong(gia_tri, mac_dinh: float) -> float:
    if gia_tri is None:
        return float(mac_dinh)
    s = str(gia_tri).strip()
    if not s:
        return float(mac_dinh)
    try:
        v = float(s)
        return v if v > 0 else float(mac_dinh)
    except (ValueError, TypeError):
        return float(mac_dinh)


def _ep_so_nguyen_khong_am(gia_tri, mac_dinh: int = SO_PHIEU_CODE_MAC_DINH) -> int:
    if gia_tri is None:
        return int(mac_dinh)
    s = str(gia_tri).strip()
    if not s:
        return int(mac_dinh)
    try:
        return max(0, int(s))
    except (ValueError, TypeError):
        return int(mac_dinh)


def _dinh_dang_phut(phut: float) -> str:
    n = float(phut)
    if abs(n - round(n)) < 1e-6:
        return str(int(round(n)))
    return f"{n:g}"


class _MemoryStatusEx(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def _doc_ram_win32_gb():
    kernel32 = getattr(getattr(ctypes, "windll", None), "kernel32", None)
    if kernel32 is None:
        return None
    st = _MemoryStatusEx()
    st.dwLength = ctypes.sizeof(_MemoryStatusEx)
    if not kernel32.GlobalMemoryStatusEx(ctypes.byref(st)):
        return None
    return float(st.ullAvailPhys) / float(1024 ** 3)


def _doc_ram_proc_meminfo_gb(duong_dan="/proc/meminfo"):
    p = Path(duong_dan)
    if not p.is_file():
        return None
    thong_so = {}
    try:
        for dong in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            if ":" not in dong:
                continue
            k, v = dong.split(":", 1)
            phan = v.strip().split()
            if phan and phan[0].isdigit():
                thong_so[k.strip()] = int(phan[0])
    except OSError:
        return None
    if "MemAvailable" in thong_so:
        return float(thong_so["MemAvailable"]) / float(1024 ** 2)
    if "MemFree" in thong_so:
        kb = thong_so["MemFree"] + thong_so.get("Buffers", 0) + thong_so.get("Cached", 0)
        return float(kb) / float(1024 ** 2)
    return None


def _doc_ram_he_thong_gb():
    """Tra ve dung luong RAM trong cua may tinh theo GB (GiB = 1024^3 byte)."""
    if os.name == "nt":
        return _doc_ram_win32_gb()
    ram = _doc_ram_proc_meminfo_gb()
    if ram is not None:
        return ram
    if hasattr(os, "sysconf"):
        try:
            trang = os.sysconf("SC_AVPHYS_PAGES")
            co_trang = os.sysconf("SC_PAGE_SIZE")
            if trang > 0 and co_trang > 0:
                return float(trang * co_trang) / float(1024 ** 3)
        except (ValueError, OSError):
            pass
    return None


lay_ram_trong_gb = _doc_ram_he_thong_gb


def du_ram_nhan_viec(cfg=None, lay_ram_fn=None):
    """Tra ve (du_ram: bool, ram_trong_gb: float | None)."""
    nguong = _ep_so_duong(
        (cfg or {}).get("nguong_ram_gb") if cfg else None,
        _ep_so_duong(os.environ.get("LINHX_RAM_TOI_THIEU_GB"), NGUONG_RAM_TRONG_GB),
    )
    ham = lay_ram_fn or lay_ram_trong_gb
    ram = ham()
    if ram is not None and ram < nguong:
        return False, ram
    return True, ram


def doc_env(tep_env=None):
    f = Path(tep_env) if tep_env else (GOC / "tho.env")
    if f.exists():
        for dong in f.read_text(encoding="utf-8").splitlines():
            dong = dong.strip()
            if dong and not dong.startswith("#") and "=" in dong:
                k, v = dong.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    cfg = {
        "nguon": os.environ.get("LINHX_NGUON", "engine").strip().lower(),
        "url": os.environ.get("LINHX_URL", "http://localhost:8080").rstrip("/"),
        "token": os.environ.get("LINHX_TOKEN", ""),
        "tho": os.environ.get("LINHX_THO", platform.node().lower()),
        "agy": os.environ.get("AGY_CMD", "agy"),
        "agy_args": os.environ.get("AGY_ARGS", "--output-format json"),
        "thu_muc": Path(os.environ.get("LINHX_THU_MUC", str(GOC / "viec"))),
        "nghi": float(os.environ.get("LINHX_NGHI", "15")),
        "host": os.environ.get("LINHX_HOST", ""),
        "repo_hang_doi": Path(os.environ.get("LINHX_REPO_HANG_DOI", str(GOC.parent))),
        "nhanh_hang_doi": os.environ.get("LINHX_NHANH_HANG_DOI", "hang-doi"),
        "remote_hang_doi": os.environ.get("LINHX_REMOTE_HANG_DOI", "origin"),
        "wt_hang_doi": os.environ.get("LINHX_WT_HANG_DOI", ""),
        "thu_muc_drive": Path(os.environ["LINHX_DRIVE"]) if os.environ.get("LINHX_DRIVE", "").strip() else None,
        "thu_muc_log": Path(os.environ["LINHX_LOG_DIR"]) if os.environ.get("LINHX_LOG_DIR", "").strip() else None,
        "so_phieu": _ep_so_nguyen_khong_am(os.environ.get("LINHX_SO_PHIEU"), SO_PHIEU_CODE_MAC_DINH),
        "tran_phut": _ep_so_duong(os.environ.get("LINHX_TRAN_PHUT"), PHUT_TOI_DA_MAC_DINH),
        "khong_tien_phut": _ep_so_duong(os.environ.get("LINHX_KHONG_TIEN_PHUT"), PHUT_KHONG_TIEN_MAC_DINH),
        "nguong_ram_gb": _ep_so_duong(os.environ.get("LINHX_RAM_TOI_THIEU_GB"), NGUONG_RAM_TRONG_GB),
    }
    cfg["thu_muc"].mkdir(parents=True, exist_ok=True)
    return cfg


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def _ghi_agy_raw(tep_log, phieu_id, returncode, giay, stdout, stderr, ghi_chu=""):
    try:
        p = Path(tep_log)
        p.parent.mkdir(parents=True, exist_ok=True)
        ban_ghi = {
            "luc": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "su_kien": "agy_raw",
            "viec": phieu_id,
            "returncode": returncode,
            "giay": round(giay, 2),
            "stdout": stdout,
            "stderr": stderr,
        }
        if ghi_chu:
            ban_ghi["ghi_chu"] = ghi_chu
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(ban_ghi, ensure_ascii=False) + "\n")
    except OSError:
        pass


def goi(cfg, method, **data):
    url = f"{cfg['url']}/api/method/linhx_worker.api.{method}"
    body = urllib.parse.urlencode({k: v for k, v in data.items() if v is not None}).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Authorization", f"token {cfg['token']}")
    req.add_header("Accept", "application/json")
    if cfg["host"]:
        req.add_header("Host", cfg["host"])
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode() or "{}").get("message")


def _goi_taskkill_cay(pid: int) -> None:
    """Dung taskkill /T /F tren Windows de diet ca cay tien trinh con cua agy (hoc dieu-phoi-engine.ps1)."""
    p = _POPEN_GOC(
        ["taskkill.exe", "/PID", str(pid), "/T", "/F"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=0x08000000,
    )
    p.wait(timeout=10)


def dung_tien_trinh_agy(proc) -> None:
    """Dung tien trinh agy va toan bo cay tien trinh con (hoc canh/dieu-phoi-engine.ps1)."""
    if proc is None:
        return
    try:
        if proc.poll() is not None:
            return
    except Exception:
        pass
    pid = getattr(proc, "pid", None)
    if os.name == "nt" and pid:
        try:
            _goi_taskkill_cay(int(pid))
        except Exception:
            pass
    elif pid:
        try:
            os.killpg(int(pid), signal.SIGKILL)
        except Exception:
            pass
    try:
        if proc.poll() is None:
            proc.kill()
    except Exception:
        pass
    try:
        proc.wait(timeout=5)
    except Exception:
        pass


def _tim_git_dir(thu_muc: Path):
    for tm in [thu_muc] + list(thu_muc.parents)[:3]:
        cham_git = tm / ".git"
        try:
            if cham_git.is_dir():
                return cham_git
            if cham_git.is_file():
                dong = cham_git.read_text(encoding="utf-8", errors="ignore").splitlines()
                if dong and dong[0].lower().startswith("gitdir:"):
                    gd = Path(dong[0].split(":", 1)[1].strip())
                    if not gd.is_absolute():
                        gd = (tm / gd).resolve()
                    if gd.is_dir():
                        return gd
        except OSError:
            continue
    return None


def _dau_git_head(thu_muc: Path):
    gd = _tim_git_dir(thu_muc)
    if gd is None:
        return None
    head_txt = ""
    thong_ke = []
    try:
        tep_head = gd / "HEAD"
        if tep_head.is_file():
            head_txt = tep_head.read_text(encoding="utf-8", errors="ignore").strip()
    except OSError:
        pass
    cac_tep = [gd / "HEAD", gd / "logs" / "HEAD", gd / "index"]
    if head_txt.startswith("ref:"):
        ref_rel = head_txt.split(":", 1)[1].strip()
        cac_tep.append(gd / ref_rel)
        tep_common = gd / "commondir"
        try:
            if tep_common.is_file():
                cd = Path(tep_common.read_text(encoding="utf-8", errors="ignore").strip())
                if not cd.is_absolute():
                    cd = (gd / cd).resolve()
                cac_tep.append(cd / ref_rel)
        except OSError:
            pass
    for p in cac_tep:
        try:
            st = p.stat()
            thong_ke.append((st.st_size, st.st_mtime_ns))
        except OSError:
            thong_ke.append(None)
    return (head_txt, tuple(thong_ke))


def _dau_thu_muc_nhanh(thu_muc: Path, gioi_han_tep: int = 5000):
    if not thu_muc.is_dir():
        return (0, 0, 0, 0)
    so_tep = 0
    tong_co = 0
    max_mtime = 0
    dau_xor = 0
    bo_qua_tm = {".git", "node_modules", ".venv", "venv"}
    try:
        for goc_con, ds_tm, ds_tep in os.walk(str(thu_muc)):
            ds_tm[:] = [d for d in ds_tm if d not in bo_qua_tm]
            for ten in ds_tep:
                if so_tep >= gioi_han_tep:
                    return (so_tep, tong_co, max_mtime, dau_xor)
                duong = os.path.join(goc_con, ten)
                try:
                    st = os.stat(duong)
                except OSError:
                    continue
                so_tep += 1
                tong_co += st.st_size
                if st.st_mtime_ns > max_mtime:
                    max_mtime = st.st_mtime_ns
                dau_xor ^= hash((duong, st.st_size, st.st_mtime_ns))
    except OSError:
        pass
    return (so_tep, tong_co, max_mtime, dau_xor)


def _dau_nhip_tien_do(thu_muc: Path, dem_byte, tep_log=None):
    dau_log = None
    if tep_log:
        try:
            st = Path(tep_log).stat()
            dau_log = (st.st_size, st.st_mtime_ns)
        except OSError:
            dau_log = None
    return (
        dem_byte[0],
        dem_byte[1],
        _dau_thu_muc_nhanh(thu_muc),
        _dau_git_head(thu_muc),
        dau_log,
    )


def _phan_tich_ket_qua_agy(returncode: int, giay_chay: float, stdout: str, stderr: str):
    nhat_ky = f"exit={returncode} giay={giay_chay:.0f}\n--- stderr ---\n{stderr[-8000:]}"
    out = stdout.strip()
    ket_qua, tv, tr = out, 0, 0
    try:
        j = json.loads(out)
        ket_qua = j.get("response") or j.get("result") or out
        u = j.get("usage") or j.get("stats") or {}
        tv = int(u.get("input_tokens") or u.get("prompt_tokens") or 0)
        tr = int(u.get("output_tokens") or u.get("completion_tokens") or 0)
        if str(j.get("status", "SUCCESS")).upper() not in ("SUCCESS", "OK", "DONE"):
            return "loi", ket_qua, nhat_ky + f"\nstatus={j.get('status')}", tv, tr
    except (ValueError, AttributeError, TypeError):
        pass
    if returncode != 0:
        return "loi", ket_qua, nhat_ky, tv, tr
    return "xong", ket_qua, nhat_ky, tv, tr


def chay_agy(cfg, viec):
    """Tra ve (trang_thai, ket_qua, nhat_ky, token_vao, token_ra).

    Dung agy (tra trang_thai='dung') khi:
    - Chay qua tran_phut (mac dinh 40 phut), hoac
    - Khong tien (khong stdout/stderr moi, khong thay doi tep/git commit) qua khong_tien_phut (mac dinh 10 phut).
    """
    if viec.get("che_do") == "kiem":
        return "xong", f"Thợ {cfg['tho']} trên {platform.node()} nhận được: {viec['de']}", "che_do=kiem, khong goi agy", 0, 0

    tran_cfg = _ep_so_duong(
        cfg.get("tran_phut"),
        _ep_so_duong(os.environ.get("LINHX_TRAN_PHUT"), PHUT_TOI_DA_MAC_DINH),
    )
    tran_viec = _ep_so_duong(viec.get("tran_phut"), tran_cfg)
    tran_phut = min(tran_viec, tran_cfg)
    tran_giay = tran_phut * 60.0

    kt_cfg = _ep_so_duong(
        cfg.get("khong_tien_phut"),
        _ep_so_duong(os.environ.get("LINHX_KHONG_TIEN_PHUT"), PHUT_KHONG_TIEN_MAC_DINH),
    )
    meta_viec = viec.get("meta") if isinstance(viec.get("meta"), dict) else {}
    kt_viec = _ep_so_duong(viec.get("khong_tien_phut") or meta_viec.get("khong_tien_phut"), kt_cfg)
    khong_tien_phut = min(kt_viec, kt_cfg)
    khong_tien_giay = khong_tien_phut * 60.0

    thu_muc = Path(cfg["thu_muc"])
    thu_muc.mkdir(parents=True, exist_ok=True)
    de = viec["de"]
    if len(de) > DE_DAI:
        # Windows gioi han dong lenh 32.767 ky tu: de dai thi ghi ra file, -p chi tro toi file
        f = thu_muc / f"de-{viec['viec']}.md"
        f.write_text(de, encoding="utf-8")
        de = (f"Đọc toàn bộ file {f.name} trong thư mục hiện tại (chỉ đọc, không chạy lệnh shell) "
              f"và làm đúng theo đề trong đó. Trả lời đúng khuôn đề yêu cầu.")
    cmd = [cfg["agy"], "-p", de] + shlex.split(cfg.get("agy_args", "--output-format json"), posix=os.name != "nt")
    tep_log_raw = cfg.get("_tep_log_phieu")

    # Tuong thich nguoc khi test monkeypatch truc tiep subprocess.run
    if subprocess.run is not _SUBPROCESS_RUN_GOC:
        kw_run = {"creationflags": 0x08000000} if os.name == "nt" else {}
        t0_run = _gio()
        try:
            p = subprocess.run(cmd, cwd=str(thu_muc), capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=tran_giay, **kw_run)
        except subprocess.TimeoutExpired as e:
            if tep_log_raw:
                _ghi_agy_raw(tep_log_raw, viec.get("viec"), -1, _gio() - t0_run, e.stdout or "", e.stderr or "", "qua_gio")
            return "dung", None, f"dừng agy: quá trần {_dinh_dang_phut(tran_phut)} phút\n{(e.stdout or '')[-4000:]}", 0, 0
        except FileNotFoundError:
            return "loi", None, f"không thấy agy ở '{cfg['agy']}' (đặt AGY_CMD)", 0, 0
        except OSError as e:
            if getattr(e, "winerror", None) == 206:
                return "loi", None, f"dòng lệnh quá dài ({len(de)} ký tự)", 0, 0
            return "loi", None, f"không chạy được agy: {e}", 0, 0
        giay_chay = _gio() - t0_run
        if tep_log_raw:
            _ghi_agy_raw(tep_log_raw, viec.get("viec"), p.returncode, giay_chay, p.stdout, p.stderr)
        return _phan_tich_ket_qua_agy(p.returncode, giay_chay, p.stdout, p.stderr)

    kw = {}
    if os.name == "nt":
        kw["creationflags"] = 0x08000000  # CREATE_NO_WINDOW: chay an, khong bat console
    else:
        kw["start_new_session"] = True

    ham_popen = _tao_tien_trinh_agy if _tao_tien_trinh_agy is not None else subprocess.Popen
    t0 = _gio()
    try:
        proc = ham_popen(
            cmd,
            cwd=str(thu_muc),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
            **kw,
        )
    except FileNotFoundError:
        return "loi", None, f"không thấy agy ở '{cfg['agy']}' (đặt AGY_CMD)", 0, 0
    except OSError as e:
        if getattr(e, "winerror", None) == 206:
            return "loi", None, f"dòng lệnh quá dài ({len(de)} ký tự)", 0, 0
        return "loi", None, f"không chạy được agy: {e}", 0, 0

    buf_out: list[bytes] = []
    buf_err: list[bytes] = []
    dem_byte = [0, 0]

    def _doc_pipe(pipe, ds: list[bytes], idx: int):
        if pipe is None:
            return
        try:
            while True:
                khuc = pipe.read(4096)
                if not khuc:
                    break
                if isinstance(khuc, str):
                    khuc = khuc.encode("utf-8", errors="replace")
                ds.append(khuc)
                dem_byte[idx] += len(khuc)
        except Exception:
            pass
        finally:
            try:
                pipe.close()
            except Exception:
                pass

    luong_out = threading.Thread(target=_doc_pipe, args=(proc.stdout, buf_out, 0), daemon=True)
    luong_err = threading.Thread(target=_doc_pipe, args=(proc.stderr, buf_err, 1), daemon=True)
    luong_out.start()
    luong_err.start()

    dau_cu = _dau_nhip_tien_do(thu_muc, dem_byte, tep_log_raw)
    moc_tien_cuoi = t0
    ly_do_dung = None
    buoc_nghi = min(1.0, max(0.01, min(tran_giay, khong_tien_giay) / 20.0))

    try:
        while True:
            if proc.poll() is not None:
                break
            bay_gio = _gio()
            dau_moi = _dau_nhip_tien_do(thu_muc, dem_byte, tep_log_raw)
            if dau_moi != dau_cu:
                dau_cu = dau_moi
                moc_tien_cuoi = bay_gio
            if (bay_gio - t0) >= tran_giay:
                ly_do_dung = "qua_gio"
                dung_tien_trinh_agy(proc)
                break
            if (bay_gio - moc_tien_cuoi) >= khong_tien_giay:
                ly_do_dung = "khong_tien"
                dung_tien_trinh_agy(proc)
                break
            _tam_nghi(buoc_nghi)
    finally:
        if proc.poll() is None:
            dung_tien_trinh_agy(proc)
        luong_out.join(timeout=2.0)
        luong_err.join(timeout=2.0)

    giay_chay = _gio() - t0
    stdout = b"".join(buf_out).decode("utf-8", errors="replace")
    stderr = b"".join(buf_err).decode("utf-8", errors="replace")

    if ly_do_dung == "qua_gio":
        if tep_log_raw:
            _ghi_agy_raw(tep_log_raw, viec.get("viec"), -1, giay_chay, stdout, stderr, "qua_gio")
        duoi = f"\n{stdout[-4000:]}" if stdout else (f"\n{stderr[-2000:]}" if stderr else "")
        return "dung", None, f"dừng agy: quá trần {_dinh_dang_phut(tran_phut)} phút{duoi}", 0, 0

    if ly_do_dung == "khong_tien":
        if tep_log_raw:
            _ghi_agy_raw(tep_log_raw, viec.get("viec"), -1, giay_chay, stdout, stderr, "khong_tien")
        duoi = f"\n{stdout[-4000:]}" if stdout else (f"\n{stderr[-2000:]}" if stderr else "")
        return "dung", None, f"dừng agy: quá {_dinh_dang_phut(khong_tien_phut)} phút không tiến{duoi}", 0, 0

    returncode = proc.returncode if proc.returncode is not None else -1
    if tep_log_raw:
        _ghi_agy_raw(tep_log_raw, viec.get("viec"), returncode, giay_chay, stdout, stderr)
    return _phan_tich_ket_qua_agy(returncode, giay_chay, stdout, stderr)


def vong(cfg, mot_lan=False, mot_viec=False):
    if str(cfg.get("nguon") or "engine").strip().lower() == "github":
        try:
            from runner import hang_doi_git
        except ImportError:
            import hang_doi_git
        return hang_doi_git.vong_git(cfg, mot_lan=mot_lan, mot_viec=mot_viec)
    log(f"linhx-runner {PHIEN_BAN} tho={cfg['tho']} url={cfg['url']}")
    while True:
        try:
            ok_ram, ram_gb = du_ram_nhan_viec(cfg)
            if not ok_ram:
                log(f"RAM trong {ram_gb:.2f} GB < {cfg.get('nguong_ram_gb', NGUONG_RAM_TRONG_GB)} GB, tam ngung nhan viec")
            else:
                viec = goi(cfg, "nhan_viec", ma=cfg["tho"], phien_ban=PHIEN_BAN, may=platform.node())
                if viec:
                    log("nhan", viec["viec"], viec["workflow"])
                    tt, kq, nk, tv, tr = chay_agy(cfg, viec)
                    tt_bao = "loi" if tt == "dung" else tt
                    goi(cfg, "bao_ket_qua", ma=cfg["tho"], viec=viec["viec"], trang_thai=tt_bao,
                        ket_qua=kq, nhat_ky=nk, token_vao=tv, token_ra=tr)
                    log("xong", viec["viec"], tt)
                    if mot_viec:
                        return
                    continue  # co viec thi hoi tiep ngay
        except urllib.error.HTTPError as e:
            log("loi HTTP", e.code, e.read()[:300])
        except Exception:
            log("loi", traceback.format_exc()[-800:])
        if mot_lan:
            return
        time.sleep(cfg["nghi"])


if __name__ == "__main__":
    # --mot-lan: het viec thi thoat; --mot-viec: lam toi da 1 viec roi thoat
    vong(doc_env(), mot_lan="--mot-lan" in sys.argv or "--mot-viec" in sys.argv, mot_viec="--mot-viec" in sys.argv)
