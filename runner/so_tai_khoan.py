"""Quản lý sổ tài khoản cho đội máy và điều phối xoay vòng khi gặp hạn mức (chỉ dùng Python stdlib)."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import threading
import time

GOC = Path(__file__).resolve().parent
TEPS_MAC_DINH_TRANG_THAI = GOC / "viec" / "trang-thai-so-tai-khoan.json"

_EMAIL_RE = re.compile(r"([A-Za-z0-9._%+\-]+)@([A-Za-z0-9.\-]+\.[A-Za-z]{2,})")
_MASKED_LOCAL_RE = re.compile(r"\*{2,}")
_SENSITIVE_KEY_WORDS = (
    "cookie",
    "token",
    "password",
    "passwd",
    "secret",
    "api_key",
    "apikey",
    "credential",
    "gaia_id",
    "refresh_token",
    "access_token",
    "session",
)
_SAFE_USAGE_COUNTER_KEYS = frozenset({"token_da_dung_24h", "token_da_dung_7n"})
_SECRET_VAL_PATTERNS = (
    re.compile(r"\b" + "gh" + r"[pousr]_[A-Za-z0-9_]{12,}\b"),
    re.compile(r"\b" + "github" + "_pat_" + r"[A-Za-z0-9_]{12,}\b"),
    re.compile(r"\b" + "sk" + r"-[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"\b" + "AI" + "za" + r"[0-9A-Za-z_-]{12,}\b"),
    re.compile(r"\b" + "ya" + r"29\.[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"\b" + "Bea" + r"rer\s+[A-Za-z0-9._-]{10,}\b", re.IGNORECASE),
)

_HTTP_429_RE = re.compile(r"(?<!\d)429(?!\d)")
_NON_HTTP_429_CONTEXT_RE = re.compile(
    r"(?:\bgiay=429\b|\bline\s+429\b|[A-Za-z0-9_./\\-]+:429(?::|\b))",
    re.IGNORECASE,
)
_QUOTA_PATTERNS = (
    "quota",
    "too many requests",
    "rate limit",
    "rate_limit",
    "ratelimit",
    "resource_exhausted",
    "exhausted your capacity",
    "usage limit",
    "hết hạn mức",
    "het han muc",
)

_TZ_COMPACT_RE = re.compile(r"([+-]\d{2})(\d{2})$")
_ISO_ERR_RE = re.compile(
    r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)",
    re.IGNORECASE,
)
_REL_COMPOUND_RE = re.compile(
    r"\b(?:resets?(?:\s+(?:in|after|sau|trong))?|in|after|sau|trong)\s*[:=]?\s*"
    r"(?:(\d+(?:[.,]\d+)?)\s*(?:hours?|hrs?|h|giờ|gio))?"
    r"\s*(?:(\d+)\s*(?:minutes?|mins?|m|phút|phut))?"
    r"\s*(?:(\d+)\s*(?:seconds?|secs?|s|giây|giay))?",
    re.IGNORECASE,
)
_RETRY_AFTER_RE = re.compile(r"retry[-_ ]after\s*[:=]\s*(\d+)", re.IGNORECASE)
_RETRY_DELAY_RE = re.compile(
    r"""["']?retry[_ ]?delay["']?\s*[:=]\s*["']?(\d+(?:\.\d+)?)\s*([hms])?["']?""",
    re.IGNORECASE,
)
_CLOCK_TIME_RE = re.compile(
    r"(?:try again at|resets?(?:\s+at)?|available\s+at|until|mở lại lúc|mo lai luc|lúc|luc)\s+(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(am|pm)?",
    re.IGNORECASE,
)
_TOKEN_IN_RE = re.compile(r"vao\s*=\s*(\d+)", re.IGNORECASE)
_TOKEN_OUT_RE = re.compile(r"ra\s*=\s*(\d+)", re.IGNORECASE)
_HEADER_LINE_RE = re.compile(r"^([a-zA-Z0-9_-]+)\s*:\s*(.*)$")

_STATE_LOCK = threading.RLock()
_MEMORY_STATE: dict[str, dict] = {"con_tro": {}, "trang_thai": {}}
_AGY_QUOTA_SUBCMDS_CACHE: dict[str, list[str]] = {}


def _local_tz():
    return datetime.now().astimezone().tzinfo or timezone.utc


def _now_dt(bay_gio: datetime | float | str | None = None) -> datetime:
    if isinstance(bay_gio, datetime):
        dt = bay_gio
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=_local_tz())
        return dt.astimezone(_local_tz())
    if isinstance(bay_gio, (int, float)):
        return datetime.fromtimestamp(float(bay_gio), tz=_local_tz())
    if isinstance(bay_gio, str) and bay_gio.strip():
        parsed = _phan_tich_iso(bay_gio)
        if parsed is not None:
            return parsed
    return datetime.now().astimezone()


def _phan_tich_iso(chuoi: str | None) -> datetime | None:
    s = str(chuoi or "").strip()
    if not s:
        return None
    if s.endswith(("Z", "z")):
        s = s[:-1] + "+00:00"
    else:
        s = _TZ_COMPACT_RE.sub(r"\1:\2", s)
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_local_tz())
    return dt.astimezone(_local_tz())


def _dinh_dang_iso(dt: datetime | None) -> str:
    if dt is None:
        return ""
    return dt.astimezone(_local_tz()).isoformat(timespec="seconds")


def che_email(raw_email: str) -> str:
    """Che phần giữa địa chỉ email theo dạng `zo***@gmail.com`."""
    s = str(raw_email or "").strip()
    if not s or "@" not in s:
        return ""
    head, _, tail = s.partition("@")
    head_low = head.strip().lower()
    tail_low = tail.strip().lower()
    if (
        head_low
        and _MASKED_LOCAL_RE.search(head_low)
        and re.fullmatch(r"[a-z0-9._%+\-*]+", head_low)
        and re.fullmatch(r"[a-z0-9.\-]+\.[a-z]{2,}", tail_low)
    ):
        return f"{head_low}@{tail_low}"
    m = _EMAIL_RE.search(s)
    if not m:
        return ""
    local = m.group(1).strip().lower()
    domain = m.group(2).strip().lower()
    if not local or not domain:
        return ""
    if len(local) >= 3:
        return f"{local[:2]}***@{domain}"
    return f"{local[0]}***@{domain}"


def che_moi_email_trong_chuoi(text: str) -> str:
    """Thay thế mọi địa chỉ email xuất hiện trong chuỗi bằng dạng đã che giữa."""
    s = str(text or "")
    if not s:
        return ""
    return _EMAIL_RE.sub(lambda m: che_email(m.group(0)) or "[ẩn]", s)


def _loc_chuoi_nhay_cam(text: str) -> str:
    s = che_moi_email_trong_chuoi(str(text or ""))
    for pat in _SECRET_VAL_PATTERNS:
        s = pat.sub("[ẩn]", s)
    return s.strip()


def lam_sach_ban_ghi_tai_khoan(obj):
    """Đệ quy loại bỏ mọi khóa nhạy cảm (cookie, token, password, secret...) và che toàn bộ email."""
    if isinstance(obj, dict):
        sach = {}
        for k, v in obj.items():
            k_str = str(k)
            k_low = k_str.lower()
            if k_low in _SAFE_USAGE_COUNTER_KEYS and isinstance(v, (int, float)) and not isinstance(v, bool):
                sach[k_str] = int(v)
                continue
            if any(tu in k_low for tu in _SENSITIVE_KEY_WORDS):
                continue
            sach[k_str] = lam_sach_ban_ghi_tai_khoan(v)
        return sach
    if isinstance(obj, list):
        return [lam_sach_ban_ghi_tai_khoan(x) for x in obj]
    if isinstance(obj, str):
        return _loc_chuoi_nhay_cam(obj)
    return obj


def _doc_cau_hinh_tho_env_an_toan(tep_env: Path) -> tuple[str, Path | None]:
    """Chỉ đọc LINHX_THO và LINHX_REPO_HANG_DOI từ tho.env, tuyệt đối không đọc/lưu LINHX_TOKEN."""
    tho = ""
    repo_hd: Path | None = None
    if not tep_env.is_file():
        return tho, repo_hd
    try:
        lines = tep_env.read_text(encoding="utf-8-sig", errors="ignore").splitlines()
    except OSError:
        return tho, repo_hd
    for dong in lines:
        s = dong.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        kl = k.strip().upper()
        vl = v.strip().strip('"').strip("'")
        if kl == "LINHX_THO" and vl:
            tho = vl.lower()
        elif kl == "LINHX_REPO_HANG_DOI" and vl:
            repo_hd = Path(vl)
    return tho, repo_hd


def xac_dinh_ma_may(ma_may_override: str = "") -> tuple[str, Path | None]:
    """Xác định mã máy và đường dẫn repo hàng đợi trên máy đang chạy."""
    ma_over = str(ma_may_override or "").strip().lower()
    env_tho = os.environ.get("LINHX_THO", "").strip().lower()
    env_repo_raw = os.environ.get("LINHX_REPO_HANG_DOI", "").strip()
    env_repo = Path(env_repo_raw) if env_repo_raw else None

    ung_vien_env = [
        GOC / "tho.env",
        Path(r"C:\linhx\hang-doi\runner\tho.env"),
        Path(r"D:\linhx\hang-doi\runner\tho.env"),
        Path(r"C:\linhx\linhx-runner\tho.env"),
        Path(r"D:\linhx\linhx-runner\tho.env"),
    ]
    tho_tu_file = ""
    repo_tu_file: Path | None = None
    for p in ung_vien_env:
        t_val, r_val = _doc_cau_hinh_tho_env_an_toan(p)
        if not tho_tu_file and t_val:
            tho_tu_file = t_val
        if repo_tu_file is None and r_val is not None:
            repo_tu_file = r_val
        if tho_tu_file and repo_tu_file is not None:
            break

    ma_may = ma_over or env_tho or tho_tu_file or (platform.node() or "may").strip().lower()
    repo_hd = env_repo or repo_tu_file
    if repo_hd is None:
        if (GOC.parent / ".git").exists():
            repo_hd = GOC.parent
        elif Path(r"C:\linhx\hang-doi\.git").exists():
            repo_hd = Path(r"C:\linhx\hang-doi")
    return ma_may, repo_hd


def _doi_thoi_gian_chrome(raw_val) -> str:
    """Chuyển trường active_time của Chrome Local State sang ISO-8601."""
    if raw_val is None or isinstance(raw_val, bool):
        return ""
    if isinstance(raw_val, str):
        s = raw_val.strip()
        if not s:
            return ""
        dt_iso = _phan_tich_iso(s)
        if dt_iso is not None:
            return _dinh_dang_iso(dt_iso)
        try:
            num = float(s)
        except ValueError:
            return ""
    elif isinstance(raw_val, (int, float)):
        num = float(raw_val)
    else:
        return ""

    if num <= 0:
        return ""
    # WebKit timestamp: micro giây tính từ 1601-01-01
    if num > 1e14:
        unix_sec = (num / 1_000_000.0) - 11644473600.0
    elif num > 1e11:
        unix_sec = num / 1000.0
    else:
        unix_sec = num
    if unix_sec <= 0 or unix_sec > 4_102_444_800:  # sau năm 2100 thì bỏ qua
        return ""
    try:
        dt = datetime.fromtimestamp(unix_sec, tz=timezone.utc).astimezone(_local_tz())
        return dt.isoformat(timespec="seconds")
    except (OSError, OverflowError, ValueError):
        return ""


def _trich_thong_tin_goi(entry: dict) -> tuple[bool | None, object]:
    """Kiểm tra xem info_cache của hồ sơ Chrome có trường gói hay không."""
    cac_khoa_goi = (
        "ai_subscription_tier",
        "subscription_tier",
        "co_goi",
        "has_subscription",
        "goi",
        "is_subscribed",
        "subscription_status",
    )
    for khoa in cac_khoa_goi:
        if khoa not in entry:
            continue
        val = entry.get(khoa)
        if isinstance(val, bool):
            return val, None
        if isinstance(val, (int, float)):
            co = bool(val > 0)
            muc = int(val) if float(val).is_integer() else val
            return co, muc
        if isinstance(val, str):
            s = _loc_chuoi_nhay_cam(val)
            low = s.lower()
            if not s or low in ("0", "false", "none", "null", "free", "khong"):
                return False, s or None
            return True, s[:40]
        if val is not None:
            return True, None
    return None, None


def _duong_dan_local_state_mac_dinh() -> Path:
    if os.name == "nt" and os.environ.get("LOCALAPPDATA", "").strip():
        return Path(os.environ["LOCALAPPDATA"].strip()) / "Google" / "Chrome" / "User Data" / "Local State"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Google" / "Chrome" / "Local State"
    return Path.home() / ".config" / "google-chrome" / "Local State"


def doc_ho_so_chrome_tai_khoan(local_state_path: Path | str | None = None) -> list[dict]:
    """Chỉ đọc `profile.info_cache` từ Chrome Local State (không đọc Cookies/Login Data)."""
    tep = Path(local_state_path) if local_state_path is not None else _duong_dan_local_state_mac_dinh()
    if not tep.is_file():
        return []
    try:
        du_lieu = json.loads(tep.read_text(encoding="utf-8", errors="ignore"))
    except (OSError, ValueError, TypeError):
        return []
    if not isinstance(du_lieu, dict):
        return []
    info_cache = (du_lieu.get("profile") or {}).get("info_cache") or {}
    if not isinstance(info_cache, dict):
        return []

    ket_qua: list[dict] = []
    for thu_muc in sorted(info_cache.keys()):
        muc = info_cache.get(thu_muc)
        if not isinstance(muc, dict):
            continue
        ten_sach = che_moi_email_trong_chuoi(" ".join(str(muc.get("name") or "").strip().split()))[:80]
        email_che = che_email(str(muc.get("user_name") or ""))
        co_goi, muc_goi = _trich_thong_tin_goi(muc)
        lan_dung_cuoi = _doi_thoi_gian_chrome(muc.get("active_time"))
        ban_ghi: dict = {
            "thu_muc": str(thu_muc),
            "ten": ten_sach or str(thu_muc),
            "email_che": email_che,
            "co_goi": co_goi,
            "lan_dung_cuoi": lan_dung_cuoi,
        }
        if muc_goi is not None:
            ban_ghi["muc_goi"] = muc_goi
        ket_qua.append(lam_sach_ban_ghi_tai_khoan(ban_ghi))
    return ket_qua


def _tim_thuc_thi_agy(agy_cmd: str = "agy") -> str:
    lenh = (agy_cmd or os.environ.get("AGY_CMD") or "agy").strip() or "agy"
    p = Path(lenh)
    if p.is_file():
        return str(p)
    found = shutil.which(lenh)
    if found:
        return str(found)
    if os.name == "nt":
        for cand in (
            Path(os.environ.get("LOCALAPPDATA", "")) / "agy" / "bin" / "agy.exe",
            Path.home() / ".gemini" / "bin" / "agy.exe",
        ):
            if str(cand) and cand.is_file():
                return str(cand)
    else:
        cand = Path.home() / ".gemini" / "bin" / "agy"
        if cand.is_file():
            return str(cand)
    return ""


def doc_tai_khoan_agy(agy_cmd: str = "agy", run_fn=None) -> str:
    """Đọc tên tài khoản/email agy đang dùng nếu có lệnh hiện; không có thì trả `'chua_ro'`."""
    thuc_thi = _tim_thuc_thi_agy(agy_cmd)
    if not thuc_thi and run_fn is None:
        return "chua_ro"
    cmd_bin = thuc_thi or (agy_cmd or "agy")
    ham_chay = run_fn or subprocess.run
    kw = {"creationflags": 0x08000000} if os.name == "nt" else {}

    cac_lenh_thu: list[list[str]] = []
    if run_fn is not None:
        cac_lenh_thu = [[cmd_bin, "whoami"], [cmd_bin, "auth", "status"]]
    else:
        try:
            p_help = ham_chay(
                [cmd_bin, "--help"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=5,
                **kw,
            )
            help_txt = ((p_help.stdout or "") + "\n" + (p_help.stderr or "")).lower()
            if re.search(r"^\s*whoami\b", help_txt, re.MULTILINE):
                cac_lenh_thu.append([cmd_bin, "whoami"])
            if re.search(r"^\s*auth\b", help_txt, re.MULTILINE):
                cac_lenh_thu.append([cmd_bin, "auth", "status"])
        except Exception:
            return "chua_ro"

    for args in cac_lenh_thu:
        try:
            proc = ham_chay(
                args,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=5,
                **kw,
            )
        except Exception:
            continue
        if getattr(proc, "returncode", 1) != 0:
            continue
        raw_out = ((getattr(proc, "stdout", "") or "") + "\n" + (getattr(proc, "stderr", "") or "")).strip()
        if not raw_out:
            continue
        # Chỉ lấy email/tên tài khoản hiển thị, che toàn bộ email và lọc bí mật
        m_email = _EMAIL_RE.search(raw_out)
        if m_email:
            masked = che_email(m_email.group(0))
            if masked:
                return masked
        for dong in raw_out.splitlines():
            sach = _loc_chuoi_nhay_cam(" ".join(dong.strip().split()))
            if sach and "chua_ro" not in sach.lower() and not sach.lower().startswith("usage:"):
                return sach[:120]
    return "chua_ro"


def _phan_tich_han_muc_tu_text(raw_out: str, now_dt: datetime) -> dict | None:
    """Trích xuất hạn mức còn lại / giờ reset từ output lệnh chỉ đọc của agy (không bịa số)."""
    text = str(raw_out or "").strip()
    if not text:
        return None
    con_lai: int | float | str = "chua_ro"
    reset_luc = "chua_ro"

    # 1. Thử parse JSON nếu CLI trả JSON
    try:
        parsed = json.loads(text)
    except ValueError:
        parsed = None

    if isinstance(parsed, dict):
        for k in ("con_lai", "remaining", "remaining_tokens", "remaining_credits", "credits_left", "quota_remaining"):
            val = parsed.get(k)
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                con_lai = int(val) if float(val).is_integer() else round(float(val), 2)
                break
            if isinstance(val, str) and val.strip() and val.strip().lower() != "chua_ro":
                con_lai = _loc_chuoi_nhay_cam(val.strip())[:60]
                break
        for k in ("reset_luc", "resets_at", "reset_at", "reset_time", "resets_in"):
            val = parsed.get(k)
            if isinstance(val, str) and val.strip():
                chuoi_v = val.strip()
                dt_iso = _phan_tich_iso(chuoi_v)
                if dt_iso is not None:
                    reset_luc = _dinh_dang_iso(dt_iso)
                else:
                    chuoi_kt = f"resets {chuoi_v}" if k == "resets_in" and not chuoi_v.lower().startswith(("in ", "after ", "reset")) else chuoi_v
                    dt_rel, _ = trich_gio_reset_429(chuoi_kt, bay_gio=now_dt)
                    if dt_rel is not None:
                        reset_luc = _dinh_dang_iso(dt_rel)
                if reset_luc != "chua_ro":
                    break
        if con_lai != "chua_ro" or reset_luc != "chua_ro":
            return {"con_lai": con_lai, "reset_luc": reset_luc, "nguon": "lenh"}

    # 2. Thử bắt các cặp remaining / credits / quota left trong text
    m_rem = re.search(
        r"(?:remaining|con[_\s]*lai|credits?\s+left|quota\s+remaining)\s*[:=]\s*([\d.,]+(?:\s*(?:k|m|%|credits?|tokens?))?)",
        text,
        re.IGNORECASE,
    )
    if m_rem:
        raw_num = m_rem.group(1).strip()
        so_sach = raw_num.replace(",", "").strip()
        if re.fullmatch(r"\d+", so_sach):
            con_lai = int(so_sach)
        else:
            con_lai = _loc_chuoi_nhay_cam(raw_num)[:60]

    dt_reset, nguon_dt = trich_gio_reset_429(text, bay_gio=now_dt)
    if dt_reset is not None and nguon_dt == "loi-429":
        reset_luc = _dinh_dang_iso(dt_reset)

    if con_lai != "chua_ro" or reset_luc != "chua_ro":
        return {"con_lai": con_lai, "reset_luc": reset_luc, "nguon": "lenh"}
    return None


def doc_han_muc_agy(agy_cmd: str = "agy", run_fn=None, *, bay_gio=None) -> dict | None:
    """Chỉ gọi lệnh đọc hạn mức của `agy` nếu `--help` thật sự có subcommand đó; ngược lại trả `None`."""
    thuc_thi = _tim_thuc_thi_agy(agy_cmd)
    if not thuc_thi and run_fn is None:
        return None
    cmd_bin = thuc_thi or (agy_cmd or "agy")
    ham_chay = run_fn or subprocess.run
    kw = {"creationflags": 0x08000000} if os.name == "nt" else {}
    now_dt = _now_dt(bay_gio)

    cac_lenh_thu: list[list[str]] = []
    if run_fn is not None:
        cac_lenh_thu = [[cmd_bin, "quota"], [cmd_bin, "usage"], [cmd_bin, "limits"]]
    else:
        cached = _AGY_QUOTA_SUBCMDS_CACHE.get(cmd_bin)
        if cached is not None:
            cac_lenh_thu = [[cmd_bin, *parts.split()] for parts in cached]
        else:
            phat_hien: list[str] = []
            try:
                p_help = ham_chay(
                    [cmd_bin, "--help"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=5,
                    **kw,
                )
                help_txt = ((p_help.stdout or "") + "\n" + (p_help.stderr or "")).lower()
                for cand in ("quota", "usage", "limits"):
                    if re.search(rf"^\s*{cand}\b", help_txt, re.MULTILINE):
                        phat_hien.append(cand)
            except Exception:
                phat_hien = []
            _AGY_QUOTA_SUBCMDS_CACHE[cmd_bin] = phat_hien
            cac_lenh_thu = [[cmd_bin, *parts.split()] for parts in phat_hien]

    if not cac_lenh_thu:
        return None

    for args in cac_lenh_thu:
        try:
            proc = ham_chay(
                args,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=5,
                **kw,
            )
        except Exception:
            continue
        if getattr(proc, "returncode", 1) != 0:
            continue
        raw_out = ((getattr(proc, "stdout", "") or "") + "\n" + (getattr(proc, "stderr", "") or "")).strip()
        kq = _phan_tich_han_muc_tu_text(raw_out, now_dt)
        if kq is not None:
            return kq
    return None


def thu_thap_tai_khoan_may(
    ma_may: str = "",
    local_state_path: Path | str | None = None,
    agy_cmd: str = "agy",
    run_fn=None,
) -> dict:
    """Thu thập danh sách hồ sơ Chrome (email đã che), tài khoản và hạn mức agy trên máy."""
    ma_chuan, _ = xac_dinh_ma_may(ma_may)
    han_muc_agy = doc_han_muc_agy(agy_cmd=agy_cmd, run_fn=run_fn)
    du_lieu = {
        "ma_may": ma_chuan,
        "ten_windows": platform.node() or ma_chuan,
        "agy_tai_khoan": doc_tai_khoan_agy(agy_cmd=agy_cmd, run_fn=run_fn),
        "ho_so_chrome": doc_ho_so_chrome_tai_khoan(local_state_path=local_state_path),
        "cap_nhat_luc": _dinh_dang_iso(_now_dt()),
    }
    if han_muc_agy is not None:
        du_lieu["han_muc_agy"] = han_muc_agy
    return lam_sach_ban_ghi_tai_khoan(du_lieu)


def _ban_so_sanh_tai_khoan(du_lieu: dict) -> dict:
    ban = json.loads(json.dumps(du_lieu, ensure_ascii=False))
    ban.pop("cap_nhat_luc", None)
    return ban


def cap_nhat_tai_khoan_may_git(
    cfg: dict,
    *,
    local_state_path: Path | str | None = None,
    run_fn=None,
    ep_ghi: bool = False,
) -> tuple[bool, Path | None, dict]:
    """Ghi `hang-doi/may/<ma_may>-tai-khoan.json` và đồng bộ `hang-doi/tai-khoan.json`, commit và push lên nhánh `hang-doi`."""
    try:
        from runner import hang_doi_git
    except ImportError:
        import hang_doi_git

    ma_may = str(cfg.get("tho") or "may").strip().lower()
    ten_tep = hang_doi_git._ten_phieu_an_toan(ma_may)
    du_lieu_moi = thu_thap_tai_khoan_may(
        ma_may=ma_may,
        local_state_path=local_state_path,
        agy_cmd=str(cfg.get("agy") or "agy"),
        run_fn=run_fn,
    )
    _, _, remote, nhanh = hang_doi_git._duong_dan_wt(cfg)

    with hang_doi_git._khoa_tep(hang_doi_git._duong_dan_khoa_wt(cfg), timeout=20.0):
        for lan in range(hang_doi_git.SO_LAN_THU_PUSH_NHIP):
            wt = hang_doi_git.dam_bao_worktree(cfg)
            if wt is None:
                return False, None, du_lieu_moi
            goc_hd = hang_doi_git.thu_muc_hang_doi(wt)
            tm_may = goc_hd / "may"
            tep_json = tm_may / f"{ten_tep}-tai-khoan.json"

            du_lieu_cu = None
            if tep_json.is_file():
                try:
                    du_lieu_cu = json.loads(tep_json.read_text(encoding="utf-8", errors="replace"))
                except (OSError, ValueError):
                    du_lieu_cu = None

            if isinstance(du_lieu_cu, dict) and isinstance(du_lieu_cu.get("trang_thai_so"), dict):
                du_lieu_moi["trang_thai_so"] = lam_sach_ban_ghi_tai_khoan(du_lieu_cu["trang_thai_so"])

            du_lieu_moi = lam_sach_ban_ghi_tai_khoan(du_lieu_moi)
            may_khong_doi = (
                isinstance(du_lieu_cu, dict)
                and _ban_so_sanh_tai_khoan(du_lieu_cu) == _ban_so_sanh_tai_khoan(du_lieu_moi)
            )
            if ep_ghi or not may_khong_doi:
                tm_may.mkdir(parents=True, exist_ok=True)
                tep_json.write_text(json.dumps(du_lieu_moi, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            so_doi, _, _ = dong_bo_va_ghi_so_tai_khoan(
                goc_hd,
                tep_trang_thai=cfg.get("tep_trang_thai_tai_khoan"),
                bo_sung_tu_may=True,
                ep_ghi=ep_ghi,
            )
            if not ep_ghi and may_khong_doi and not so_doi:
                return False, tep_json, du_lieu_moi

            hang_doi_git._commit_git(wt, ma_may, f"may: cap nhat tai khoan {ma_may}")
            pull_rb = hang_doi_git.chay_git(["pull", "--rebase", remote, nhanh], cwd=wt, check=False, timeout=45)
            if pull_rb.returncode != 0:
                hang_doi_git.chay_git(["rebase", "--abort"], cwd=wt, check=False, timeout=15)
                continue
            push = hang_doi_git.chay_git(["push", remote, f"HEAD:refs/heads/{nhanh}"], cwd=wt, check=False, timeout=45)
            if push.returncode == 0:
                return True, tep_json, du_lieu_moi
            time.sleep(0.05 * (lan + 1))
    return False, None, du_lieu_moi


def _chuan_hoa_ds_cong_cu(raw) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, str):
        items = re.split(r"[,;|]+", raw)
    elif isinstance(raw, (list, tuple, set)):
        items = [str(x) for x in raw]
    else:
        return []
    ket_qua: list[str] = []
    for item in items:
        s = str(item or "").strip().lower()
        if s and s not in ket_qua:
            ket_qua.append(s)
    return ket_qua


def _chuan_hoa_con_lai(val) -> int | float | str:
    if val is None or isinstance(val, bool):
        return "chua_ro"
    if isinstance(val, (int, float)):
        return int(val) if float(val).is_integer() else round(float(val), 2)
    s = str(val).strip()
    if not s or s.lower() == "chua_ro":
        return "chua_ro"
    if re.fullmatch(r"\d+", s):
        return int(s)
    return _loc_chuoi_nhay_cam(s)[:80] or "chua_ro"


def _chuan_hoa_so_token(val) -> int:
    if isinstance(val, bool) or val is None:
        return 0
    if isinstance(val, (int, float)):
        return max(0, int(val))
    try:
        return max(0, int(str(val).strip()))
    except (ValueError, TypeError):
        return 0


def _chuan_hoa_dong_tai_khoan(muc: dict) -> dict:
    raw_email = str(muc.get("email_che") or muc.get("email") or "").strip()
    email_da_che = che_email(raw_email) if "@" in raw_email else _loc_chuoi_nhay_cam(raw_email)
    tt = str(muc.get("trang_thai") or "dung").strip().lower()
    if tt not in ("dung", "het_han_muc", "can_dang_nhap"):
        tt = "dung"
    mo_lai = str(muc.get("mo_lai_luc") or "").strip()
    reset_luc = str(muc.get("reset_luc") or "").strip()
    if not reset_luc:
        reset_luc = mo_lai if (tt == "het_han_muc" and mo_lai) else "chua_ro"
    nguon = str(muc.get("nguon") or "").strip().lower()
    if nguon not in ("lenh", "loi-429", "uoc"):
        nguon = "uoc"
    ban = {
        "ma": str(muc.get("ma") or muc.get("id") or muc.get("ho_so_chrome") or "").strip(),
        "email_che": email_da_che,
        "may": str(muc.get("may") or "").strip().lower(),
        "ho_so_chrome": str(muc.get("ho_so_chrome") or muc.get("thu_muc") or "").strip(),
        "cong_cu": _chuan_hoa_ds_cong_cu(muc.get("cong_cu")),
        "trang_thai": tt,
        "mo_lai_luc": mo_lai,
        "token_da_dung_24h": _chuan_hoa_so_token(muc.get("token_da_dung_24h")),
        "token_da_dung_7n": _chuan_hoa_so_token(muc.get("token_da_dung_7n")),
        "con_lai": _chuan_hoa_con_lai(muc.get("con_lai")),
        "reset_luc": reset_luc,
        "nguon": nguon,
    }
    return lam_sach_ban_ghi_tai_khoan(ban)


def _tim_tep_so_mac_dinh(cfg: dict | None = None) -> Path | None:
    if cfg and cfg.get("tep_so_tai_khoan"):
        p = Path(cfg["tep_so_tai_khoan"])
        if p.is_file():
            return p
    env_p = os.environ.get("LINHX_SO_TAI_KHOAN", "").strip()
    if env_p and Path(env_p).is_file():
        return Path(env_p)

    ung_vien: list[Path] = []
    if cfg:
        try:
            from runner import hang_doi_git
        except ImportError:
            import hang_doi_git
        try:
            repo, wt, _, _ = hang_doi_git._duong_dan_wt(cfg)
            ung_vien.extend([
                wt / "hang-doi" / "tai-khoan.json",
                wt / "tai-khoan.json",
                repo / "hang-doi" / "tai-khoan.json",
            ])
        except Exception:
            pass

    ung_vien.extend([
        GOC.parent / "hang-doi" / "tai-khoan.json",
        GOC.parent.parent / ".hang-doi-hang-doi" / "hang-doi" / "tai-khoan.json",
    ])
    for cand in ung_vien:
        if cand.is_file():
            return cand
    return None


def doc_so_tai_khoan(tep_so: Path | str | None = None, cfg: dict | None = None) -> list[dict]:
    """Chỉ đọc file sổ chung `hang-doi/tai-khoan.json` (hỗ trợ JSON array, object hoặc JSONL)."""
    tep = Path(tep_so) if tep_so else _tim_tep_so_mac_dinh(cfg)
    if tep is None or not tep.is_file():
        return []
    try:
        raw_text = tep.read_text(encoding="utf-8-sig", errors="replace").strip()
    except OSError:
        return []
    if not raw_text:
        return []

    raw_items: list[dict] = []
    try:
        parsed = json.loads(raw_text)
        if isinstance(parsed, list):
            raw_items = [x for x in parsed if isinstance(x, dict)]
        elif isinstance(parsed, dict):
            if isinstance(parsed.get("tai_khoan"), list):
                raw_items = [x for x in parsed["tai_khoan"] if isinstance(x, dict)]
            elif isinstance(parsed.get("items"), list):
                raw_items = [x for x in parsed["items"] if isinstance(x, dict)]
            else:
                raw_items = [parsed]
    except ValueError:
        # Hỗ trợ thêm định dạng JSONL (mỗi dòng 1 object)
        for dong in raw_text.splitlines():
            s = dong.strip()
            if not s or s.startswith("#"):
                continue
            try:
                item = json.loads(s)
                if isinstance(item, dict):
                    raw_items.append(item)
            except ValueError:
                continue

    return [_chuan_hoa_dong_tai_khoan(item) for item in raw_items]


def _doc_trang_thai_runtime(tep_trang_thai: Path | str | None = None) -> dict:
    with _STATE_LOCK:
        if tep_trang_thai is None:
            return {
                "con_tro": dict(_MEMORY_STATE["con_tro"]),
                "trang_thai": {k: dict(v) for k, v in _MEMORY_STATE["trang_thai"].items()},
            }
        p = Path(tep_trang_thai)
        if not p.is_file():
            return {"con_tro": {}, "trang_thai": {}}
        try:
            data = json.loads(p.read_text(encoding="utf-8", errors="replace"))
            if isinstance(data, dict):
                return {
                    "con_tro": dict(data.get("con_tro") or {}),
                    "trang_thai": {k: dict(v) for k, v in (data.get("trang_thai") or {}).items() if isinstance(v, dict)},
                }
        except (OSError, ValueError, TypeError):
            pass
        return {"con_tro": {}, "trang_thai": {}}


def _ghi_trang_thai_runtime(state: dict, tep_trang_thai: Path | str | None = None) -> None:
    with _STATE_LOCK:
        if tep_trang_thai is None:
            _MEMORY_STATE["con_tro"] = dict(state.get("con_tro") or {})
            _MEMORY_STATE["trang_thai"] = {k: dict(v) for k, v in (state.get("trang_thai") or {}).items()}
            return
        p = Path(tep_trang_thai)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def dat_lai_bo_nho_xoay_vong() -> None:
    """Đặt lại con trỏ và trạng thái runtime trong bộ nhớ (tiện cho unit test)."""
    with _STATE_LOCK:
        _MEMORY_STATE["con_tro"].clear()
        _MEMORY_STATE["trang_thai"].clear()


def _trang_thai_hieu_luc(dong: dict, runtime_state: dict, now_dt: datetime) -> tuple[str, str]:
    ma = str(dong.get("ma") or "").strip()
    ov = (runtime_state.get("trang_thai") or {}).get(ma) if ma else None
    tt = str((ov or {}).get("trang_thai") or dong.get("trang_thai") or "dung").strip().lower()
    mo_lai = str((ov or {}).get("mo_lai_luc") or dong.get("mo_lai_luc") or "").strip()

    if tt == "het_han_muc":
        mo_dt = _phan_tich_iso(mo_lai)
        if mo_dt is not None and now_dt >= mo_dt:
            return "dung", ""
    return tt, mo_lai


def _khop_may_va_cong_cu(dong: dict, may: str, cong_cu: str) -> bool:
    may_can = str(may or "").strip().lower()
    may_dong = str(dong.get("may") or "").strip().lower()
    if may_can and may_dong and may_dong not in ("bat-ky", "*") and may_dong != may_can:
        return False
    if may_can and not may_dong:
        return False

    cc_can = str(cong_cu or "").strip().lower()
    if cc_can:
        ds_cc = _chuan_hoa_ds_cong_cu(dong.get("cong_cu"))
        if cc_can not in ds_cc:
            return False
    return True


def chon_tai_khoan(
    may: str,
    cong_cu: str,
    *,
    danh_sach: list[dict] | None = None,
    tep_so: Path | str | None = None,
    tep_trang_thai: Path | str | None = None,
    bay_gio: datetime | float | str | None = None,
    bo_qua_ma: set[str] | list[str] | tuple[str, ...] | None = None,
    cfg: dict | None = None,
) -> dict | None:
    """Chọn 1 dòng tài khoản còn dùng được cho `(may, cong_cu)`, xoay vòng và bỏ qua dòng `het_han_muc` chưa tới giờ mở lại."""
    with _STATE_LOCK:
        nguon_ds = danh_sach if danh_sach is not None else doc_so_tai_khoan(tep_so=tep_so, cfg=cfg)
        ds_chuan = [_chuan_hoa_dong_tai_khoan(x) for x in nguon_ds if isinstance(x, dict)]
        phu_hop = [d for d in ds_chuan if _khop_may_va_cong_cu(d, may, cong_cu)]
        if not phu_hop:
            return None

        now_dt = _now_dt(bay_gio)
        state = _doc_trang_thai_runtime(tep_trang_thai)
        bo_qua = {str(x).strip() for x in (bo_qua_ma or ()) if str(x).strip()}

        khoa_rr = f"{str(may or '').strip().lower()}::{str(cong_cu or '').strip().lower()}"
        ma_cuoi = str((state.get("con_tro") or {}).get(khoa_rr) or "").strip()

        vi_tri_bat_dau = 0
        if ma_cuoi:
            for idx, muc in enumerate(phu_hop):
                if muc["ma"] == ma_cuoi:
                    vi_tri_bat_dau = (idx + 1) % len(phu_hop)
                    break

        so_luong = len(phu_hop)
        for buoc in range(so_luong):
            idx = (vi_tri_bat_dau + buoc) % so_luong
            ung_vien = phu_hop[idx]
            ma_uv = ung_vien["ma"]
            if ma_uv and ma_uv in bo_qua:
                continue
            tt_hieu_luc, mo_lai_hieu_luc = _trang_thai_hieu_luc(ung_vien, state, now_dt)
            if tt_hieu_luc != "dung":
                continue

            ket_qua = dict(ung_vien)
            ket_qua["trang_thai"] = "dung"
            ket_qua["mo_lai_luc"] = mo_lai_hieu_luc
            if ma_uv:
                state.setdefault("con_tro", {})[khoa_rr] = ma_uv
                _ghi_trang_thai_runtime(state, tep_trang_thai)
            return ket_qua
        return None


def la_loi_han_muc(trang_thai: str, ket_qua, nhat_ky: str = "") -> bool:
    """Nhận diện lỗi 429 hoặc thông báo hết hạn mức (`quota`, `rate limit`, ...)."""
    if str(trang_thai or "").strip().lower() not in ("loi", "dung"):
        return False
    combined = f"{ket_qua or ''}\n{nhat_ky or ''}"
    lowered = combined.lower()
    for pat in _QUOTA_PATTERNS:
        if pat in lowered:
            return True
    scrubbed = _NON_HTTP_429_CONTEXT_RE.sub("", combined)
    return bool(_HTTP_429_RE.search(scrubbed))


def trich_gio_reset_429(
    van_ban_loi: str = "",
    bay_gio: datetime | float | str | None = None,
) -> tuple[datetime | None, str]:
    """Trích giờ reset từ thông báo lỗi 429/quota.

    Trả về `(thoi_diem, nguon)` với `nguon` là `'loi-429'` nếu đọc được từ lỗi,
    hoặc `(now + 5h, 'uoc')` nếu chỉ báo hết hạn mức mà không ghi giờ,
    hoặc `(None, 'uoc')` nếu chuỗi lỗi không liên quan hạn mức.
    """
    now_dt = _now_dt(bay_gio)
    van_ban = str(van_ban_loi or "")

    # 1. Tìm timestamp ISO tường minh trong thông báo lỗi
    for m in _ISO_ERR_RE.finditer(van_ban):
        dt = _phan_tich_iso(m.group(1))
        if dt is not None and dt > now_dt:
            return dt, "loi-429"

    # 2. Tìm Retry-After: <giây>
    m_retry = _RETRY_AFTER_RE.search(van_ban)
    if m_retry:
        try:
            giay = int(m_retry.group(1))
            if giay > 0:
                return now_dt + timedelta(seconds=giay), "loi-429"
        except ValueError:
            pass

    # 3. Tìm retryDelay (vd: "retryDelay": "42s", retry_delay=1.5h)
    m_delay = _RETRY_DELAY_RE.search(van_ban)
    if m_delay:
        try:
            val = float(m_delay.group(1))
            don_vi = (m_delay.group(2) or "s").lower()
            he_so = 3600 if don_vi == "h" else (60 if don_vi == "m" else 1)
            giay = round(val * he_so)
            if giay > 0:
                return now_dt + timedelta(seconds=giay), "loi-429"
        except ValueError:
            pass

    # 4. Tìm khoảng thời gian tương đối (vd: resets 5h, resets in 2h 30m, after 45m, sau 3 giờ)
    for m_rel in _REL_COMPOUND_RE.finditer(van_ban):
        raw_h = (m_rel.group(1) or "").replace(",", ".").strip()
        h_val = float(raw_h) if raw_h else 0.0
        m_val = int(m_rel.group(2) or 0)
        s_val = int(m_rel.group(3) or 0)
        tong = round(h_val * 3600) + m_val * 60 + s_val
        if tong > 0:
            return now_dt + timedelta(seconds=tong), "loi-429"

    # 5. Tìm giờ HH:MM (kèm AM/PM nếu có)
    m_clk = _CLOCK_TIME_RE.search(van_ban)
    if m_clk:
        try:
            gio = int(m_clk.group(1))
            phut = int(m_clk.group(2))
            giay = int(m_clk.group(3) or 0)
            ampm = (m_clk.group(4) or "").lower()
            if ampm == "pm" and gio < 12:
                gio += 12
            elif ampm == "am" and gio == 12:
                gio = 0
            if 0 <= gio <= 23 and 0 <= phut <= 59 and 0 <= giay <= 59:
                ung_vien = now_dt.replace(hour=gio, minute=phut, second=giay, microsecond=0)
                if ung_vien <= now_dt:
                    ung_vien += timedelta(days=1)
                return ung_vien, "loi-429"
        except ValueError:
            pass

    if la_loi_han_muc("loi", van_ban, ""):
        return now_dt + timedelta(hours=5), "uoc"
    return None, "uoc"


def trich_gio_mo_lai(van_ban_loi: str = "", bay_gio: datetime | float | str | None = None) -> datetime:
    """Lấy thời điểm mở lại từ chuỗi lỗi; nếu không có giờ trong lỗi thì cộng +5 giờ."""
    dt, _ = trich_gio_reset_429(van_ban_loi, bay_gio=bay_gio)
    if dt is not None:
        return dt
    return _now_dt(bay_gio) + timedelta(hours=5)


def danh_dau_het_han_muc(
    ma_tai_khoan: str,
    van_ban_loi: str = "",
    *,
    bay_gio: datetime | float | str | None = None,
    danh_sach: list[dict] | None = None,
    tep_trang_thai: Path | str | None = None,
    tep_so: Path | str | None = None,
    cfg: dict | None = None,
) -> dict:
    """Đánh dấu tài khoản `het_han_muc` + `reset_luc` (mặc định +5 giờ nếu lỗi không ghi giờ)."""
    ma = str(ma_tai_khoan or "").strip()
    mo_lai_dt, nguon_reset = trich_gio_reset_429(van_ban_loi, bay_gio=bay_gio)
    if mo_lai_dt is None:
        mo_lai_dt = _now_dt(bay_gio) + timedelta(hours=5)
        nguon_reset = "uoc"
    mo_lai_iso = _dinh_dang_iso(mo_lai_dt)

    with _STATE_LOCK:
        state = _doc_trang_thai_runtime(tep_trang_thai)
        if ma:
            state.setdefault("trang_thai", {})[ma] = {
                "trang_thai": "het_han_muc",
                "mo_lai_luc": mo_lai_iso,
                "reset_luc": mo_lai_iso,
                "nguon": nguon_reset,
                "con_lai": "chua_ro",
            }
            _ghi_trang_thai_runtime(state, tep_trang_thai)

        if isinstance(danh_sach, list) and ma:
            for item in danh_sach:
                if isinstance(item, dict) and str(item.get("ma") or "").strip() == ma:
                    item["trang_thai"] = "het_han_muc"
                    item["mo_lai_luc"] = mo_lai_iso
                    item["reset_luc"] = mo_lai_iso
                    item["nguon"] = nguon_reset
                    if item.get("nguon") != "lenh":
                        item["con_lai"] = "chua_ro"

    tep_so_thuc = Path(tep_so) if tep_so else (_tim_tep_so_mac_dinh(cfg) if cfg else None)
    if tep_so_thuc is not None and tep_so_thuc.is_file():
        goc_hd_tu_so = tep_so_thuc.parent
        dong_bo_va_ghi_so_tai_khoan(
            goc_hd_tu_so,
            tep_so=tep_so_thuc,
            tep_trang_thai=tep_trang_thai,
            runtime_bo_sung=state,
            bay_gio=bay_gio,
        )

    if cfg and ma and cfg.get("ghi_trang_thai_may_git"):
        _cap_nhat_trang_thai_so_len_may_git(
            cfg,
            ma,
            mo_lai_iso,
            nguon=nguon_reset,
            tep_trang_thai=tep_trang_thai,
            bay_gio=bay_gio,
        )

    return {
        "ma": ma,
        "trang_thai": "het_han_muc",
        "mo_lai_luc": mo_lai_iso,
        "reset_luc": mo_lai_iso,
        "nguon": nguon_reset,
        "con_lai": "chua_ro",
    }


def _cap_nhat_trang_thai_so_len_may_git(
    cfg: dict,
    ma_tk: str,
    mo_lai_iso: str,
    *,
    nguon: str = "uoc",
    tep_trang_thai: Path | str | None = None,
    bay_gio=None,
) -> None:
    try:
        from runner import hang_doi_git
    except ImportError:
        import hang_doi_git

    ma_may = str(cfg.get("tho") or "may").strip().lower()
    ten_tep = hang_doi_git._ten_phieu_an_toan(ma_may)
    _, _, remote, nhanh = hang_doi_git._duong_dan_wt(cfg)
    nguon_sach = nguon if nguon in ("lenh", "loi-429", "uoc") else "uoc"
    try:
        with hang_doi_git._khoa_tep(hang_doi_git._duong_dan_khoa_wt(cfg), timeout=10.0):
            wt = hang_doi_git.dam_bao_worktree(cfg)
            if wt is None:
                return
            goc_hd = hang_doi_git.thu_muc_hang_doi(wt)
            tep_json = goc_hd / "may" / f"{ten_tep}-tai-khoan.json"
            if tep_json.is_file():
                du_lieu = json.loads(tep_json.read_text(encoding="utf-8", errors="replace"))
            else:
                du_lieu = {"ma_may": ma_may, "agy_tai_khoan": "chua_ro", "ho_so_chrome": []}
            if not isinstance(du_lieu, dict):
                return
            tt_so = du_lieu.get("trang_thai_so")
            if not isinstance(tt_so, dict):
                tt_so = {}
            tt_so[ma_tk] = {
                "trang_thai": "het_han_muc",
                "mo_lai_luc": mo_lai_iso,
                "reset_luc": mo_lai_iso,
                "nguon": nguon_sach,
                "con_lai": "chua_ro",
            }
            du_lieu["trang_thai_so"] = tt_so
            du_lieu = lam_sach_ban_ghi_tai_khoan(du_lieu)
            tep_json.parent.mkdir(parents=True, exist_ok=True)
            tep_json.write_text(json.dumps(du_lieu, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            if (goc_hd / "tai-khoan.json").is_file():
                dong_bo_va_ghi_so_tai_khoan(
                    goc_hd,
                    tep_trang_thai=tep_trang_thai,
                    bay_gio=bay_gio,
                )
            hang_doi_git._commit_git(wt, ma_may, f"may: het han muc {ma_tk}")
            hang_doi_git.chay_git(["pull", "--rebase", remote, nhanh], cwd=wt, check=False, timeout=30)
            hang_doi_git.chay_git(["push", remote, f"HEAD:refs/heads/{nhanh}"], cwd=wt, check=False, timeout=30)
    except Exception:
        pass


def _tim_git_root_va_ts_xong(xong_dir: Path) -> dict[str, int]:
    """Lấy timestamp commit git cho các file `xong/*/KET-QUA.md` chỉ bằng 1 lần gọi git log."""
    git_root: Path | None = None
    for cand in (xong_dir, xong_dir.parent, xong_dir.parent.parent):
        if (cand / ".git").exists():
            git_root = cand
            break
    if git_root is None:
        return {}
    try:
        rel_xong = xong_dir.resolve().relative_to(git_root.resolve()).as_posix()
    except ValueError:
        return {}
    try:
        kw = {"creationflags": 0x08000000} if os.name == "nt" else {}
        proc = subprocess.run(
            ["git", "log", "--format=COMMIT|%ct", "--name-only", "--", rel_xong],
            cwd=str(git_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            **kw,
        )
    except Exception:
        return {}
    if proc.returncode != 0 or not proc.stdout:
        return {}

    ts_map: dict[str, int] = {}
    cur_ts = 0
    for line in proc.stdout.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("COMMIT|"):
            try:
                cur_ts = int(s.split("|", 1)[1].strip())
            except ValueError:
                cur_ts = 0
            continue
        if cur_ts <= 0:
            continue
        norm = s.replace("\\", "/")
        if norm.endswith("/KET-QUA.md") and norm not in ts_map:
            ts_map[norm] = cur_ts
    return ts_map


def tinh_token_tu_ket_qua(
    goc_hd: Path | str,
    *,
    bay_gio: datetime | float | str | None = None,
) -> dict:
    """Cộng `token: vao=.. ra=..` và dấu vết lỗi 429 từ `xong/*/KET-QUA.md` theo `(tai_khoan, may)` trong 24h & 7 ngày."""
    goc = Path(goc_hd)
    now_dt = _now_dt(bay_gio)
    moc_24h = now_dt - timedelta(hours=24)
    moc_7n = now_dt - timedelta(days=7)

    theo_tai_khoan: dict[tuple[str, str], dict[str, int]] = {}
    khong_tk_theo_may: dict[str, dict[str, int]] = {}
    theo_may: dict[str, dict[str, int]] = {}
    loi_429_theo_tk: dict[tuple[str, str], dict] = {}
    loi_429_theo_may: dict[str, dict] = {}

    xong_dir: Path | None = None
    for cand in (goc / "xong", goc / "hang-doi" / "xong"):
        if cand.is_dir():
            xong_dir = cand
            break

    if xong_dir is None:
        return {
            "theo_tai_khoan": theo_tai_khoan,
            "khong_tk_theo_may": khong_tk_theo_may,
            "theo_may": theo_may,
            "loi_429_theo_tk": loi_429_theo_tk,
            "loi_429_theo_may": loi_429_theo_may,
        }

    git_ts_map = _tim_git_root_va_ts_xong(xong_dir)
    git_root: Path | None = None
    if git_ts_map:
        for cand in (xong_dir, xong_dir.parent, xong_dir.parent.parent):
            if (cand / ".git").exists():
                git_root = cand.resolve()
                break

    def _cong_vao_muc(bucket: dict, key, vao: int, ra: int, in_24h: bool, in_7n: bool) -> None:
        muc = bucket.setdefault(key, {"vao_24h": 0, "ra_24h": 0, "tong_24h": 0, "vao_7n": 0, "ra_7n": 0, "tong_7n": 0})
        if in_7n:
            muc["vao_7n"] += vao
            muc["ra_7n"] += ra
            muc["tong_7n"] += vao + ra
        if in_24h:
            muc["vao_24h"] += vao
            muc["ra_24h"] += ra
            muc["tong_24h"] += vao + ra

    for tep_kq in sorted(xong_dir.glob("*/KET-QUA.md")):
        try:
            text = tep_kq.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        headers: dict[str, str] = {}
        for dong in text.splitlines()[:30]:
            s = dong.strip()
            if not s:
                if headers:
                    break
                continue
            m_hdr = _HEADER_LINE_RE.match(s)
            if m_hdr:
                headers[m_hdr.group(1).strip().lower()] = m_hdr.group(2).strip()

        may = headers.get("may", "").strip().lower()
        tai_khoan = headers.get("tai_khoan", "").strip()
        trang_thai = headers.get("trang_thai", "").strip().lower()

        token_line = headers.get("token", "")
        if not token_line:
            for dong in text.splitlines()[:30]:
                if dong.lower().lstrip().startswith("token:"):
                    token_line = dong.split(":", 1)[1].strip()
                    break
        m_in = _TOKEN_IN_RE.search(token_line)
        m_out = _TOKEN_OUT_RE.search(token_line)
        vao = int(m_in.group(1)) if m_in else 0
        ra = int(m_out.group(1)) if m_out else 0

        ts_dt: datetime | None = None
        for k_time in ("xong_luc", "luc", "thoi_diem"):
            if headers.get(k_time):
                ts_dt = _phan_tich_iso(headers[k_time])
                if ts_dt is not None:
                    break
        if ts_dt is None and git_root is not None:
            try:
                rel_p = tep_kq.resolve().relative_to(git_root).as_posix()
                if rel_p in git_ts_map:
                    ts_dt = datetime.fromtimestamp(git_ts_map[rel_p], tz=_local_tz())
            except ValueError:
                pass
        if ts_dt is None:
            try:
                ts_dt = datetime.fromtimestamp(tep_kq.stat().st_mtime, tz=_local_tz())
            except OSError:
                ts_dt = now_dt

        in_7n = ts_dt >= moc_7n
        in_24h = ts_dt >= moc_24h

        if may:
            _cong_vao_muc(theo_may, may, vao, ra, in_24h, in_7n)
        if tai_khoan:
            _cong_vao_muc(theo_tai_khoan, (tai_khoan, may), vao, ra, in_24h, in_7n)
        elif may:
            _cong_vao_muc(khong_tk_theo_may, may, vao, ra, in_24h, in_7n)

        if trang_thai in ("loi", "dung") and la_loi_han_muc(trang_thai, "", text):
            reset_dt, nguon_429 = trich_gio_reset_429(text, bay_gio=ts_dt)
            if reset_dt is not None and reset_dt > now_dt:
                info_429 = {
                    "ts_epoch": ts_dt.timestamp(),
                    "reset_luc": _dinh_dang_iso(reset_dt),
                    "nguon": nguon_429,
                }
                if tai_khoan:
                    prev = loi_429_theo_tk.get((tai_khoan, may))
                    if prev is None or info_429["ts_epoch"] >= prev["ts_epoch"]:
                        loi_429_theo_tk[(tai_khoan, may)] = info_429
                elif may:
                    prev_m = loi_429_theo_may.get(may)
                    if prev_m is None or info_429["ts_epoch"] >= prev_m["ts_epoch"]:
                        loi_429_theo_may[may] = info_429

    return {
        "theo_tai_khoan": theo_tai_khoan,
        "khong_tk_theo_may": khong_tk_theo_may,
        "theo_may": theo_may,
        "loi_429_theo_tk": loi_429_theo_tk,
        "loi_429_theo_may": loi_429_theo_may,
    }


def _doc_may_tai_khoan_trong_hang_doi(goc_hd: Path) -> dict[str, dict]:
    """Đọc toàn bộ `hang-doi/may/*-tai-khoan.json` một cách an toàn."""
    tm_may = goc_hd / "may"
    if not tm_may.is_dir():
        return {}
    ket_qua: dict[str, dict] = {}
    for tep in sorted(tm_may.glob("*-tai-khoan.json")):
        try:
            data = json.loads(tep.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        ma_may = str(data.get("ma_may") or tep.name[:-len("-tai-khoan.json")]).strip().lower()
        if ma_may:
            ket_qua[ma_may] = data
    return ket_qua


def dong_bo_va_ghi_so_tai_khoan(
    goc_hd: Path | str,
    *,
    tep_so: Path | str | None = None,
    tep_trang_thai: Path | str | None = None,
    runtime_bo_sung: dict | None = None,
    bo_sung_tu_may: bool = False,
    han_muc_moi: dict | None = None,
    bay_gio: datetime | float | str | None = None,
    ep_ghi: bool = False,
) -> tuple[bool, Path, list[dict]]:
    """Tổng hợp token 24h/7n, hạn mức và reset_luc rồi cập nhật `hang-doi/tai-khoan.json`."""
    goc = Path(goc_hd)
    so_path = Path(tep_so) if tep_so else (goc / "tai-khoan.json")
    now_dt = _now_dt(bay_gio)

    raw_parsed = None
    raw_text_cu = ""
    raw_items: list[dict] = []
    if so_path.is_file():
        try:
            raw_text_cu = so_path.read_text(encoding="utf-8-sig", errors="replace")
            if raw_text_cu.strip():
                raw_parsed = json.loads(raw_text_cu)
                if isinstance(raw_parsed, list):
                    raw_items = [x for x in raw_parsed if isinstance(x, dict)]
                elif isinstance(raw_parsed, dict):
                    if isinstance(raw_parsed.get("tai_khoan"), list):
                        raw_items = [x for x in raw_parsed["tai_khoan"] if isinstance(x, dict)]
                    elif isinstance(raw_parsed.get("items"), list):
                        raw_items = [x for x in raw_parsed["items"] if isinstance(x, dict)]
        except (OSError, ValueError):
            raw_items = []

    rows = [_chuan_hoa_dong_tai_khoan(x) for x in raw_items]
    may_info_map = _doc_may_tai_khoan_trong_hang_doi(goc)

    # Cập nhật email cho hồ sơ Chrome đã có hoặc bổ sung hàng mới từ từng máy nếu yêu cầu
    for m_code, m_data in sorted(may_info_map.items()):
        for hs in m_data.get("ho_so_chrome") or []:
            if not isinstance(hs, dict):
                continue
            hs_dir = str(hs.get("thu_muc") or "").strip()
            hs_email = che_email(str(hs.get("email_che") or "")) or _loc_chuoi_nhay_cam(str(hs.get("email_che") or ""))
            for row in rows:
                if row["may"] == m_code and row["ho_so_chrome"].lower() == hs_dir.lower() and hs_dir:
                    if not row["email_che"] and hs_email:
                        row["email_che"] = hs_email
                    if not row["email_che"] and row["trang_thai"] == "dung":
                        row["trang_thai"] = "can_dang_nhap"

    if bo_sung_tu_may:
        for m_code, m_data in sorted(may_info_map.items()):
            da_co_agy = any(row["may"] == m_code and "agy" in row["cong_cu"] for row in rows)
            if not da_co_agy:
                agy_raw = str(m_data.get("agy_tai_khoan") or "chua_ro").strip()
                agy_email = che_email(agy_raw) if "@" in agy_raw else (_loc_chuoi_nhay_cam(agy_raw) or "chua_ro")
                hm = m_data.get("han_muc_agy") if isinstance(m_data.get("han_muc_agy"), dict) else {}
                rows.append(
                    _chuan_hoa_dong_tai_khoan(
                        {
                            "ma": f"agy-{m_code}",
                            "email_che": agy_email,
                            "may": m_code,
                            "ho_so_chrome": "",
                            "cong_cu": ["agy"],
                            "trang_thai": "dung",
                            "con_lai": hm.get("con_lai", "chua_ro"),
                            "reset_luc": hm.get("reset_luc", "chua_ro"),
                            "nguon": hm.get("nguon", "uoc"),
                        }
                    )
                )

            for hs in m_data.get("ho_so_chrome") or []:
                if not isinstance(hs, dict):
                    continue
                hs_dir = str(hs.get("thu_muc") or "").strip()
                hs_email = che_email(str(hs.get("email_che") or "")) or _loc_chuoi_nhay_cam(str(hs.get("email_che") or ""))
                da_co_hs = any(
                    row["may"] == m_code
                    and (
                        (hs_dir and row["ho_so_chrome"].lower() == hs_dir.lower())
                        or (hs_email and row["email_che"].lower() == hs_email.lower() and not row["ho_so_chrome"])
                    )
                    for row in rows
                )
                if not da_co_hs and (hs_dir or hs_email):
                    hs_slug = re.sub(r"[^a-z0-9_-]+", "-", hs_dir.lower()).strip("-") or "mac-dinh"
                    ma_moi = f"{m_code}-{hs_slug}"
                    so_hieu = 2
                    ma_goc = ma_moi
                    cac_ma = {r["ma"] for r in rows}
                    while ma_moi in cac_ma:
                        ma_moi = f"{ma_goc}-{so_hieu}"
                        so_hieu += 1
                    rows.append(
                        _chuan_hoa_dong_tai_khoan(
                            {
                                "ma": ma_moi,
                                "email_che": hs_email,
                                "may": m_code,
                                "ho_so_chrome": hs_dir,
                                "cong_cu": ["chrome"],
                                "trang_thai": "dung" if hs_email else "can_dang_nhap",
                                "con_lai": "chua_ro",
                                "reset_luc": "chua_ro",
                                "nguon": "uoc",
                            }
                        )
                    )

    token_info = tinh_token_tu_ket_qua(goc, bay_gio=now_dt)
    theo_tk = token_info["theo_tai_khoan"]
    khong_tk_may = token_info["khong_tk_theo_may"]
    loi_429_tk = token_info["loi_429_theo_tk"]
    loi_429_may = token_info["loi_429_theo_may"]

    # Đếm số tài khoản chạy `agy` trên mỗi máy để gán token lịch sử chưa ghi `tai_khoan:` khi không mơ hồ
    agy_theo_may: dict[str, int] = {}
    for row in rows:
        if "agy" in row["cong_cu"] and row["may"]:
            agy_theo_may[row["may"]] = agy_theo_may.get(row["may"], 0) + 1

    runtime_overrides: dict[str, dict] = {}
    if tep_trang_thai is not None:
        rt = _doc_trang_thai_runtime(tep_trang_thai)
        for ma_k, v_k in (rt.get("trang_thai") or {}).items():
            if isinstance(v_k, dict):
                runtime_overrides[ma_k] = dict(v_k)
    if isinstance(runtime_bo_sung, dict):
        for ma_k, v_k in (runtime_bo_sung.get("trang_thai") or {}).items():
            if isinstance(v_k, dict):
                runtime_overrides[ma_k] = dict(v_k)
    for m_data in may_info_map.values():
        tt_so = m_data.get("trang_thai_so")
        if isinstance(tt_so, dict):
            for ma_k, v_k in tt_so.items():
                if isinstance(v_k, dict) and ma_k not in runtime_overrides:
                    runtime_overrides[ma_k] = dict(v_k)

    for row in rows:
        ma = row["ma"]
        may = row["may"]

        # 1. Cộng token 24h & 7n theo tài khoản + máy
        tong_24h = 0
        tong_7n = 0
        if may in ("", "bat-ky", "*", "all", "tat-ca"):
            for (tk_k, _m_k), val in theo_tk.items():
                if tk_k == ma:
                    tong_24h += val["tong_24h"]
                    tong_7n += val["tong_7n"]
        else:
            trung = theo_tk.get((ma, may))
            if trung:
                tong_24h += trung["tong_24h"]
                tong_7n += trung["tong_7n"]
            trung_rong = theo_tk.get((ma, ""))
            if trung_rong:
                tong_24h += trung_rong["tong_24h"]
                tong_7n += trung_rong["tong_7n"]
            if "agy" in row["cong_cu"] and agy_theo_may.get(may, 0) == 1:
                fallback_m = khong_tk_may.get(may)
                if fallback_m:
                    tong_24h += fallback_m["tong_24h"]
                    tong_7n += fallback_m["tong_7n"]

        row["token_da_dung_24h"] = tong_24h
        row["token_da_dung_7n"] = tong_7n

        # 2. Áp kết quả từ lệnh đọc hạn mức agy nếu có
        hm_ap_dung = None
        if isinstance(han_muc_moi, dict) and han_muc_moi.get("ma") == ma:
            hm_ap_dung = han_muc_moi
        elif "agy" in row["cong_cu"] and may in may_info_map:
            hm_may = may_info_map[may].get("han_muc_agy")
            if isinstance(hm_may, dict):
                hm_ap_dung = hm_may

        if hm_ap_dung is not None:
            row["con_lai"] = _chuan_hoa_con_lai(hm_ap_dung.get("con_lai"))
            if hm_ap_dung.get("reset_luc") and str(hm_ap_dung.get("reset_luc")).strip() != "chua_ro":
                row["reset_luc"] = str(hm_ap_dung["reset_luc"]).strip()
            row["nguon"] = "lenh"

        # 3. Áp trạng thái 429 / mở lại
        ov = runtime_overrides.get(ma)
        if ov is None:
            ev_429 = loi_429_tk.get((ma, may))
            if ev_429 is None and "agy" in row["cong_cu"] and agy_theo_may.get(may, 0) == 1:
                ev_429 = loi_429_may.get(may)
            if ev_429 is not None:
                ov = {
                    "trang_thai": "het_han_muc",
                    "mo_lai_luc": ev_429["reset_luc"],
                    "reset_luc": ev_429["reset_luc"],
                    "nguon": ev_429["nguon"],
                }

        tt_hieu_luc = row["trang_thai"]
        mo_lai_hi = row["mo_lai_luc"]
        reset_hi = row["reset_luc"]
        nguon_hi = row["nguon"]
        if ov is not None:
            tt_hieu_luc = str(ov.get("trang_thai") or tt_hieu_luc).strip().lower()
            mo_lai_hi = str(ov.get("mo_lai_luc") or mo_lai_hi).strip()
            reset_hi = str(ov.get("reset_luc") or mo_lai_hi or reset_hi or "chua_ro").strip()
            nguon_ov = str(ov.get("nguon") or "").strip().lower()
            if nguon_ov in ("lenh", "loi-429", "uoc"):
                nguon_hi = nguon_ov

        if tt_hieu_luc == "het_han_muc":
            mo_dt = _phan_tich_iso(mo_lai_hi or ("" if reset_hi == "chua_ro" else reset_hi))
            if mo_dt is not None and now_dt >= mo_dt:
                tt_hieu_luc = "dung"
                mo_lai_hi = ""
                if nguon_hi != "lenh":
                    reset_hi = "chua_ro"
                    row["con_lai"] = "chua_ro"
            else:
                if not reset_hi:
                    reset_hi = mo_lai_hi or "chua_ro"
                if nguon_hi != "lenh":
                    row["con_lai"] = "chua_ro"
        else:
            if nguon_hi != "lenh":
                row["con_lai"] = "chua_ro"
                if reset_hi and reset_hi != "chua_ro":
                    r_dt = _phan_tich_iso(reset_hi)
                    if r_dt is not None and now_dt >= r_dt:
                        reset_hi = "chua_ro"

        row["trang_thai"] = tt_hieu_luc if tt_hieu_luc in ("dung", "het_han_muc", "can_dang_nhap") else "dung"
        row["mo_lai_luc"] = mo_lai_hi
        row["reset_luc"] = reset_hi or "chua_ro"
        row["nguon"] = nguon_hi if nguon_hi in ("lenh", "loi-429", "uoc") else "uoc"

    rows_sach = [lam_sach_ban_ghi_tai_khoan(_chuan_hoa_dong_tai_khoan(r)) for r in rows]

    if isinstance(raw_parsed, dict) and "tai_khoan" in raw_parsed:
        payload_out = dict(raw_parsed)
        payload_out["tai_khoan"] = rows_sach
    else:
        payload_out = rows_sach

    noi_dung_moi = json.dumps(payload_out, ensure_ascii=False, indent=2) + "\n"
    if not ep_ghi and raw_text_cu == noi_dung_moi:
        return False, so_path, rows_sach

    so_path.parent.mkdir(parents=True, exist_ok=True)
    so_path.write_text(noi_dung_moi, encoding="utf-8")
    return True, so_path, rows_sach


def _lay_cong_cu_tu_viec(viec: dict | None) -> str:
    if not isinstance(viec, dict):
        return ""
    meta = viec.get("meta") if isinstance(viec.get("meta"), dict) else {}
    raw = meta.get("cong_cu") if "cong_cu" in meta else viec.get("cong_cu")
    return str(raw or "").split("#", 1)[0].strip().lower()


def _cap_nhat_han_muc_lenh_sau_phieu(
    cfg: dict,
    ma_tk: str,
    tep_so: Path | str | None,
    tep_trang_thai: Path | str | None,
    bay_gio=None,
) -> None:
    """Sau mỗi phiếu dùng `agy`, gọi lệnh chỉ đọc hạn mức nếu CLI có hỗ trợ và ghi vào sổ."""
    doc_fn = (cfg or {}).get("_doc_han_muc_agy_fn")
    if callable(doc_fn):
        hm = doc_fn()
    else:
        hm = doc_han_muc_agy(agy_cmd=str((cfg or {}).get("agy") or "agy"), bay_gio=bay_gio)
    if not isinstance(hm, dict):
        return

    hm_ban = dict(hm)
    hm_ban["ma"] = ma_tk
    hm_ban["nguon"] = "lenh"

    with _STATE_LOCK:
        state = _doc_trang_thai_runtime(tep_trang_thai)
        cur = dict((state.get("trang_thai") or {}).get(ma_tk) or {})
        cur["con_lai"] = _chuan_hoa_con_lai(hm_ban.get("con_lai"))
        if hm_ban.get("reset_luc") and str(hm_ban.get("reset_luc")).strip() != "chua_ro":
            cur["reset_luc"] = str(hm_ban["reset_luc"]).strip()
        cur["nguon"] = "lenh"
        cur.setdefault("trang_thai", "dung")
        state.setdefault("trang_thai", {})[ma_tk] = cur
        _ghi_trang_thai_runtime(state, tep_trang_thai)

    tep_so_thuc = Path(tep_so) if tep_so else _tim_tep_so_mac_dinh(cfg)
    if tep_so_thuc is not None and tep_so_thuc.is_file():
        dong_bo_va_ghi_so_tai_khoan(
            tep_so_thuc.parent,
            tep_so=tep_so_thuc,
            tep_trang_thai=tep_trang_thai,
            han_muc_moi=hm_ban,
            bay_gio=bay_gio,
        )


def chay_voi_tai_khoan(
    cfg: dict,
    viec: dict,
    ham_agy,
    *,
    tep_so: Path | str | None = None,
    tep_trang_thai: Path | str | None = None,
    bay_gio: datetime | float | str | None = None,
):
    """Nếu phiếu có header `cong_cu`, chọn tài khoản từ sổ, gắn `LINHX_HO_SO_CHROME` và xoay vòng khi gặp 429/quota."""
    cong_cu = _lay_cong_cu_tu_viec(viec)
    if not cong_cu:
        return ham_agy(cfg, viec)

    may = str((cfg or {}).get("tho") or platform.node() or "").strip().lower()
    tep_so_thuc = tep_so if tep_so is not None else (cfg or {}).get("tep_so_tai_khoan")
    tep_tt_thuc = tep_trang_thai if tep_trang_thai is not None else (cfg or {}).get("tep_trang_thai_tai_khoan")

    da_thu: set[str] = set()
    tong_tv = 0
    tong_tr = 0
    ket_qua_cuoi = None

    while True:
        tk = chon_tai_khoan(
            may,
            cong_cu,
            tep_so=tep_so_thuc,
            tep_trang_thai=tep_tt_thuc,
            bay_gio=bay_gio,
            bo_qua_ma=da_thu,
            cfg=cfg,
        )
        if tk is None:
            if not da_thu:
                return ham_agy(cfg, viec)
            tt_c, kq_c, nk_c, _, _ = ket_qua_cuoi
            ghi_chu = f"hết hạn mức toàn bộ tài khoản đã thử ({', '.join(sorted(da_thu))})"
            nk_moi = f"{nk_c}\n{ghi_chu}".strip() if nk_c else ghi_chu
            return tt_c, kq_c, nk_moi, tong_tv, tong_tr

        ma_tk = tk["ma"]
        da_thu.add(ma_tk)
        ho_so_chrome = str(tk.get("ho_so_chrome") or "").strip()

        if isinstance(viec, dict):
            viec["_tai_khoan_da_dung"] = ma_tk
            viec["_ho_so_chrome_da_dung"] = ho_so_chrome

        cfg_lan = dict(cfg or {})
        if ho_so_chrome:
            cfg_lan["ho_so_chrome"] = ho_so_chrome

        env_cu = os.environ.get("LINHX_HO_SO_CHROME")
        try:
            if ho_so_chrome:
                os.environ["LINHX_HO_SO_CHROME"] = ho_so_chrome
            else:
                os.environ.pop("LINHX_HO_SO_CHROME", None)
            tt, kq, nk, tv, tr = ham_agy(cfg_lan, viec)
        finally:
            if env_cu is None:
                os.environ.pop("LINHX_HO_SO_CHROME", None)
            else:
                os.environ["LINHX_HO_SO_CHROME"] = env_cu

        tong_tv += int(tv or 0)
        tong_tr += int(tr or 0)
        ket_qua_cuoi = (tt, kq, nk, tong_tv, tong_tr)

        if la_loi_han_muc(tt, kq, nk):
            danh_dau_het_han_muc(
                ma_tk,
                f"{kq or ''}\n{nk or ''}",
                bay_gio=bay_gio,
                tep_trang_thai=tep_tt_thuc,
                tep_so=tep_so_thuc,
                cfg=cfg,
            )
            continue

        if cong_cu == "agy":
            _cap_nhat_han_muc_lenh_sau_phieu(cfg, ma_tk, tep_so_thuc, tep_tt_thuc, bay_gio=bay_gio)

        return tt, kq, nk, tong_tv, tong_tr


def _in_tom_tat(du_lieu: dict, tep_git: Path | None = None, da_push: bool | None = None) -> None:
    print(f"may: {du_lieu.get('ma_may')}")
    print(f"agy_tai_khoan: {du_lieu.get('agy_tai_khoan', 'chua_ro')}")
    ds = du_lieu.get("ho_so_chrome") or []
    print(f"ho_so_chrome ({len(ds)}):")
    for hs in ds:
        goi = hs.get("co_goi")
        goi_txt = f" | goi={goi}" if goi is not None else ""
        muc_txt = f" ({hs.get('muc_goi')})" if hs.get("muc_goi") is not None else ""
        email_txt = hs.get("email_che") or "(chua_dang_nhap)"
        lan_txt = hs.get("lan_dung_cuoi") or "-"
        print(f"  - {hs.get('thu_muc')} | {hs.get('ten')} | {email_txt}{goi_txt}{muc_txt} | {lan_txt}")
    if tep_git is not None:
        print(f"tep_json: {tep_git}")
    if da_push is not None:
        print(f"da_commit_push: {'co' if da_push else 'khong_doi_hoac_bo_qua'}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Thu thập danh sách tài khoản trên máy cho linhx-runner.")
    parser.add_argument("--may", default="", help="Mã máy (mặc định đọc từ tho.env / LINHX_THO).")
    parser.add_argument("--local-state", default="", help="Đường dẫn Chrome Local State (tùy chọn).")
    parser.add_argument("--repo-hang-doi", default="", help="Đường dẫn repo chứa nhánh hang-doi.")
    parser.add_argument("--xuat-json", default="", help="Ghi bản sao JSON ra đường dẫn chỉ định.")
    parser.add_argument("--cap-nhat-git", action="store_true", help="Ghi và push lên nhánh hang-doi.")
    parser.add_argument("--dong-bo-han-muc", action="store_true", help="Chỉ đồng bộ token & hạn mức vào hang-doi/tai-khoan.json.")
    parser.add_argument("--ep-ghi", action="store_true", help="Ép commit kể cả khi dữ liệu không đổi.")
    args = parser.parse_args(argv)

    ma_may, repo_tu_env = xac_dinh_ma_may(args.may)
    repo_hd = Path(args.repo_hang_doi) if args.repo_hang_doi else repo_tu_env
    ls_path = Path(args.local_state) if args.local_state else None
    agy_cmd = os.environ.get("AGY_CMD", "agy")

    if args.cap_nhat_git:
        if repo_hd is None:
            print("Khong xac dinh duoc repo hang-doi de commit.", file=sys.stderr)
            return 1
        cfg = {
            "tho": ma_may,
            "agy": agy_cmd,
            "repo_hang_doi": str(repo_hd),
            "nhanh_hang_doi": os.environ.get("LINHX_NHANH_HANG_DOI", "hang-doi"),
            "remote_hang_doi": os.environ.get("LINHX_REMOTE_HANG_DOI", "origin"),
            "wt_hang_doi": os.environ.get("LINHX_WT_HANG_DOI", ""),
        }
        da_push, tep_git, du_lieu = cap_nhat_tai_khoan_may_git(
            cfg,
            local_state_path=ls_path,
            ep_ghi=bool(args.ep_ghi),
        )
        if args.xuat_json:
            p_out = Path(args.xuat_json)
            p_out.parent.mkdir(parents=True, exist_ok=True)
            p_out.write_text(json.dumps(du_lieu, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        _in_tom_tat(du_lieu, tep_git=tep_git, da_push=da_push)
        return 0

    if args.dong_bo_han_muc:
        if repo_hd is None:
            print("Khong xac dinh duoc repo hang-doi de dong bo han muc.", file=sys.stderr)
            return 1
        goc_sync = (Path(repo_hd) / "hang-doi") if (Path(repo_hd) / "hang-doi").is_dir() else Path(repo_hd)
        da_ghi, tep_so, rows_so = dong_bo_va_ghi_so_tai_khoan(
            goc_sync,
            bo_sung_tu_may=True,
            ep_ghi=bool(args.ep_ghi),
        )
        print(f"so_tai_khoan: {tep_so} | so_dong={len(rows_so)} | da_ghi={'co' if da_ghi else 'khong_doi'}")
        return 0

    du_lieu = thu_thap_tai_khoan_may(ma_may=ma_may, local_state_path=ls_path, agy_cmd=agy_cmd)
    if args.xuat_json:
        p_out = Path(args.xuat_json)
        p_out.parent.mkdir(parents=True, exist_ok=True)
        p_out.write_text(json.dumps(du_lieu, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _in_tom_tat(du_lieu)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
