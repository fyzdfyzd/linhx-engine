"""Bảng theo dõi web chỉ đọc cho hàng đợi GitHub (nhánh hang-doi).

Chạy bằng Python stdlib trên cổng 8090:
- Mỗi 30 giây `git fetch` nhánh `hang-doi` vào clone riêng `C:\\linhx\\bang-hang-doi`.
- Đọc `hang-doi/moi`, `hang-doi/dang`, `hang-doi/xong/*/KET-QUA.md`.
- Phục vụ trang chủ `/` (tiếng Việt, tự làm mới 30 giây), `/phieu/<id>` (xem KET-QUA.md),
  `/api/trang-thai` và `/api/ket-qua/<id>` (JSON).
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import glob
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import socket
import stat
import subprocess
import sys
import threading
import time
import urllib.parse

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8090
DEFAULT_CLONE_DIR = Path(r"C:\linhx\bang-hang-doi")
DEFAULT_REPO_URL = "https://github.com/fyzdfyzd/linhx-engine.git"
DEFAULT_BRANCH = "hang-doi"
DEFAULT_REMOTE = "origin"
DEFAULT_FETCH_INTERVAL = 30.0
INACTIVE_THRESHOLD_MINUTES = 30.0
MAX_RECENT_DONE = 20
LOW_DISK_C_THRESHOLD_GB = 10.0

ALLOWED_TEP_EXTS = frozenset({".png", ".jpg", ".webp", ".webm", ".mp4", ".txt", ".log", ".json"})
IMAGE_TEP_EXTS = frozenset({".png", ".jpg", ".webp"})
LOG_TEP_EXTS = frozenset({".log", ".txt"})
MAX_TEP_BYTES = 20 * 1024 * 1024
MAX_TICKET_IMAGES = 6
MAX_STEP_LOG_LINES = 30
MAX_GHEP_IMAGES = 24
_TEP_CONTENT_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".webp": "image/webp",
    ".webm": "video/webm",
    ".mp4": "video/mp4",
    ".txt": "text/plain; charset=utf-8",
    ".log": "text/plain; charset=utf-8",
    ".json": "application/json; charset=utf-8",
}

_HEADER_LINE_RE = re.compile(r"^([a-zA-Z0-9_-]+)\s*:\s*(.*)$")
_NHIP_LINE_RE = re.compile(r"^nhip\s*:\s*(.+)$", re.IGNORECASE)
_CANH_NEN_LOG_ISO_RE = re.compile(r"\[?log_cuoi=([^\s\]]+)\]?", re.IGNORECASE)
_CANH_NEN_LOG_PHUT_RE = re.compile(r"log\s+cuối\s+(\d+)\s+phút\s+trước", re.IGNORECASE)
_CANH_NEN_NHAN_TAG_RE = re.compile(
    r"đang\s+chờ\s+nền(?:\s*·\s*log\s+cuối\s+\d+\s+phút\s+trước)?",
    re.IGNORECASE,
)
_CANH_NEN_WAITING_BG_RE = re.compile(r"waiting\s+up\s+to\b.*\bbackground\s+task", re.IGNORECASE)
_CANH_NEN_ROOT_IDLE_RE = re.compile(r"\broot\s+agent\s+idle\b", re.IGNORECASE)
_CANH_NEN_TRUE_VALUES = frozenset({"co", "có", "1", "true", "yes", "bat", "bật"})
_CANH_NEN_FALSE_VALUES = frozenset({"0", "false", "khong", "không", "no", "off", "tat", "tắt"})
_TZ_COMPACT_RE = re.compile(r"([+-]\d{2})(\d{2})$")
_TOKEN_IN_RE = re.compile(r"vao\s*=\s*(\d+)", re.IGNORECASE)
_TOKEN_OUT_RE = re.compile(r"ra\s*=\s*(\d+)", re.IGNORECASE)
_SAFE_TICKET_ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")
_DAT_LINE_RE = re.compile(r"^[*`#>\-\s]*dat\s*:\s*[*`]*\s*(.+)$", re.IGNORECASE)
_TIEU_CHI_HEADING_RE = re.compile(r"^#{1,6}\s*.*ti[eê]u\s*ch[ií]", re.IGNORECASE)
_ANY_HEADING_RE = re.compile(r"^#{1,6}\s+\S")
_TIEU_CHI_INLINE_RE = re.compile(r"ti[eê]u\s*ch[ií]", re.IGNORECASE)
_UPPER_KHONG_RE = re.compile(r"\bKH[OÔ]NG\b")
_NEG_CONCLUSION_RE = re.compile(
    r"(?::|->|=>|—)\s*\*{0,2}\s*(?:không(?:\s+đạt)?|khong(?:\s+dat)?|chưa\s+đạt|chua\s+dat|đỏ|trượt|fail)\b",
    re.IGNORECASE,
)
_SECRET_LINE_RE = re.compile(
    r"(?i)(api[_-]?key|access[_-]?token|refresh[_-]?token|secret[_-]?key|password|mat_khau|authorization)\s*([:=])\s*\S+"
)
_EMAIL_RE = re.compile(r"\b([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b")
_PHONE_RE = re.compile(r"(?<!\d)(?:\+?84|0)(?:[\s.\-]?\d){8,10}(?!\d)")
_SECRET_VAL_PATTERNS = (
    re.compile(r"\b" + "gh" + r"[pousr]_[A-Za-z0-9_]{12,}\b"),
    re.compile(r"\b" + "github" + "_pat_" + r"[A-Za-z0-9_]{12,}\b"),
    re.compile(r"\b" + "sk" + r"-[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"\b" + "AI" + "za" + r"[0-9A-Za-z_-]{12,}\b"),
    re.compile(r"\b" + "ya" + r"29\.[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"\b" + "Bea" + r"rer\s+[A-Za-z0-9._-]{10,}\b", re.IGNORECASE),
)


def _mask_email(raw_email: str) -> str:
    """Che phần giữa địa chỉ email (vd `zo***@gmail.com`), không lộ email đầy đủ."""
    text = str(raw_email or "").strip()
    if "@" not in text:
        return ""
    local, domain = text.split("@", 1)
    if not local or not domain:
        return ""
    if len(local) <= 2:
        prefix = local[:1]
    else:
        prefix = local[:2]
    return f"{prefix}***@{domain}"


def _mask_emails_in_text(text: str) -> str:
    """Che mọi địa chỉ email xuất hiện trong chuỗi trước khi đưa ra UI/API."""
    raw = str(text or "").strip()
    if not raw:
        return ""
    return _EMAIL_RE.sub(lambda m: _mask_email(m.group(0)), raw)


def _mask_sensitive_text(text: str, *, mask_phones: bool = False) -> str:
    """Che email, bí mật và tùy chọn số điện thoại trước khi hiển thị."""
    s = _mask_emails_in_text(text)
    for pat in _SECRET_VAL_PATTERNS:
        s = pat.sub("[ẩn]", s)
    if mask_phones and s:
        s = _PHONE_RE.sub("[ẩn-sđt]", s)
    return s


def _normalize_cong_cu_list(raw) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, str):
        items = re.split(r"[,;|]+", raw)
    elif isinstance(raw, (list, tuple, set)):
        items = [str(x) for x in raw]
    else:
        return []
    out: list[str] = []
    for item in items:
        s = str(item or "").strip().lower()
        if s and s not in out:
            out.append(s)
    return out


def _normalize_nonneg_int(val) -> int:
    if isinstance(val, bool) or val is None:
        return 0
    if isinstance(val, (int, float)):
        return max(0, int(val))
    try:
        return max(0, int(str(val).strip()))
    except (ValueError, TypeError):
        return 0


def _normalize_con_lai(val):
    if val is None or isinstance(val, bool):
        return "chua_ro"
    if isinstance(val, (int, float)):
        return int(val) if float(val).is_integer() else round(float(val), 2)
    s = str(val).strip()
    if not s or s.lower() == "chua_ro":
        return "chua_ro"
    if re.fullmatch(r"\d+", s):
        return int(s)
    return _mask_sensitive_text(s)[:80] or "chua_ro"


def _read_tai_khoan_ledger(qroot: Path) -> list[dict]:
    """Đọc `hang-doi/tai-khoan.json` an toàn (chỉ lấy metadata và email đã che)."""
    ledger_path = qroot / "tai-khoan.json"
    if not ledger_path.is_file():
        return []
    try:
        raw_text = ledger_path.read_text(encoding="utf-8", errors="replace").strip()
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
        for line in raw_text.splitlines():
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            try:
                obj = json.loads(s)
                if isinstance(obj, dict):
                    raw_items.append(obj)
            except ValueError:
                continue

    rows: list[dict] = []
    for item in raw_items:
        may = str(item.get("may") or "").strip().lower()
        ho_so = str(item.get("ho_so_chrome") or item.get("thu_muc") or "").strip()
        raw_email = str(item.get("email_che") or item.get("email") or "").strip()
        email_che = _mask_email(raw_email) if "@" in raw_email else _mask_sensitive_text(raw_email)
        tt = str(item.get("trang_thai") or "dung").strip().lower()
        if tt not in ("dung", "het_han_muc", "can_dang_nhap"):
            tt = "dung"
        mo_lai = str(item.get("mo_lai_luc") or "").strip()
        reset_luc = str(item.get("reset_luc") or "").strip()
        if not reset_luc:
            reset_luc = mo_lai if (tt == "het_han_muc" and mo_lai) else "chua_ro"
        nguon = str(item.get("nguon") or "").strip().lower()
        if nguon not in ("lenh", "loi-429", "uoc"):
            nguon = "uoc"
        rows.append(
            {
                "ma": str(item.get("ma") or item.get("id") or ho_so).strip(),
                "may": may,
                "ho_so_chrome": ho_so,
                "email_che": email_che,
                "cong_cu": _normalize_cong_cu_list(item.get("cong_cu")),
                "trang_thai": tt,
                "mo_lai_luc": mo_lai,
                "token_da_dung_24h": _normalize_nonneg_int(item.get("token_da_dung_24h")),
                "token_da_dung_7n": _normalize_nonneg_int(item.get("token_da_dung_7n")),
                "con_lai": _normalize_con_lai(item.get("con_lai")),
                "reset_luc": reset_luc or "chua_ro",
                "nguon": nguon,
            }
        )
    return rows


def _build_tools_ledger_groups(
    *,
    ledger_rows: list[dict],
    machine_accounts_by_may: dict[str, dict],
    current_time: datetime,
) -> list[dict]:
    """Gom sổ tài khoản theo từng công cụ tự do, sắp công cụ có cảnh báo lên đầu."""
    runtime_so: dict[str, dict] = {}
    for m_data in machine_accounts_by_may.values():
        tt_so = m_data.get("trang_thai_so")
        if isinstance(tt_so, dict):
            for k, v in tt_so.items():
                if isinstance(v, dict):
                    runtime_so[str(k).strip()] = v

    working = [dict(r) for r in ledger_rows]
    # Bổ sung thông tin máy (agy / Chrome profile) nếu chưa có trong tai-khoan.json
    for m_code in sorted(machine_accounts_by_may):
        m_data = machine_accounts_by_may[m_code] or {}
        if not any(r.get("may") == m_code and "agy" in (r.get("cong_cu") or []) for r in working):
            agy_raw = str(m_data.get("agy_tai_khoan") or "chua_ro").strip()
            agy_email = _mask_email(agy_raw) if "@" in agy_raw else (_mask_sensitive_text(agy_raw) or "chua_ro")
            hm = m_data.get("han_muc_agy") if isinstance(m_data.get("han_muc_agy"), dict) else {}
            working.append(
                {
                    "ma": f"agy-{m_code}",
                    "may": m_code,
                    "ho_so_chrome": "",
                    "email_che": agy_email,
                    "cong_cu": ["agy"],
                    "trang_thai": "dung",
                    "mo_lai_luc": "",
                    "token_da_dung_24h": 0,
                    "token_da_dung_7n": 0,
                    "con_lai": _normalize_con_lai(hm.get("con_lai")),
                    "reset_luc": str(hm.get("reset_luc") or "chua_ro").strip() or "chua_ro",
                    "nguon": str(hm.get("nguon") or "uoc").strip() or "uoc",
                }
            )
        for prof in m_data.get("ho_so_chrome") or []:
            if not isinstance(prof, dict):
                continue
            hs_dir = str(prof.get("thu_muc") or prof.get("ho_so_chrome") or "").strip()
            raw_em = str(prof.get("email_che") or prof.get("email") or "").strip()
            em_che = _mask_email(raw_em) if "@" in raw_em else _mask_sensitive_text(raw_em)
            already = any(
                r.get("may") == m_code
                and (
                    (hs_dir and (r.get("ho_so_chrome") or "").lower() == hs_dir.lower())
                    or (em_che and (r.get("email_che") or "").lower() == em_che.lower() and not r.get("ho_so_chrome"))
                )
                for r in working
            )
            if not already and em_che:
                tt_prof = str(prof.get("trang_thai") or "dung").strip().lower()
                if tt_prof not in ("dung", "het_han_muc", "can_dang_nhap"):
                    tt_prof = "dung"
                working.append(
                    {
                        "ma": f"{m_code}-{re.sub(r'[^a-z0-9_-]+', '-', hs_dir.lower()).strip('-') or 'chrome'}",
                        "may": m_code,
                        "ho_so_chrome": hs_dir,
                        "email_che": em_che,
                        "cong_cu": ["chrome"],
                        "trang_thai": tt_prof,
                        "mo_lai_luc": "",
                        "token_da_dung_24h": 0,
                        "token_da_dung_7n": 0,
                        "con_lai": "chua_ro",
                        "reset_luc": "chua_ro",
                        "nguon": "uoc",
                    }
                )

    tools_map: dict[str, list[dict]] = {}
    seen_per_tool: dict[str, set[tuple[str, str, str]]] = {}

    for row in working:
        ma = str(row.get("ma") or "").strip()
        may = str(row.get("may") or "").strip().lower()
        ho_so = str(row.get("ho_so_chrome") or "").strip()
        email_che = str(row.get("email_che") or "").strip() or "chua_ro"

        tt = str(row.get("trang_thai") or "dung").strip().lower()
        mo_lai = str(row.get("mo_lai_luc") or "").strip()
        reset_luc = str(row.get("reset_luc") or "chua_ro").strip() or "chua_ro"
        nguon = str(row.get("nguon") or "uoc").strip().lower()
        con_lai = row.get("con_lai", "chua_ro")

        ov = runtime_so.get(ma)
        if ov is not None:
            tt = str(ov.get("trang_thai") or tt).strip().lower()
            mo_lai = str(ov.get("mo_lai_luc") or mo_lai).strip()
            reset_luc = str(ov.get("reset_luc") or mo_lai or reset_luc or "chua_ro").strip()
            ov_ng = str(ov.get("nguon") or "").strip().lower()
            if ov_ng in ("lenh", "loi-429", "uoc"):
                nguon = ov_ng

        if tt == "het_han_muc":
            mo_dt = parse_iso_datetime(mo_lai or ("" if reset_luc == "chua_ro" else reset_luc))
            if mo_dt is not None and current_time >= mo_dt:
                tt = "dung"
                if nguon != "lenh":
                    reset_luc = "chua_ro"
                    con_lai = "chua_ro"

        if tt not in ("dung", "het_han_muc", "can_dang_nhap"):
            tt = "dung"

        acc_view = {
            "ma": ma,
            "email_che": email_che,
            "may": may or "bat-ky",
            "ho_so_chrome": ho_so,
            "da_dung_24h": _normalize_nonneg_int(row.get("token_da_dung_24h")),
            "da_dung_7n": _normalize_nonneg_int(row.get("token_da_dung_7n")),
            "con_lai": _normalize_con_lai(con_lai),
            "reset_luc": reset_luc or "chua_ro",
            "nguon": nguon if nguon in ("lenh", "loi-429", "uoc") else "uoc",
            "trang_thai": tt,
        }

        tool_names = row.get("cong_cu") or ["khac"]
        for tool in tool_names:
            t_key = str(tool or "khac").strip().lower() or "khac"
            dedup_key = (ma or email_che, may, ho_so.lower())
            seen_set = seen_per_tool.setdefault(t_key, set())
            if dedup_key in seen_set:
                continue
            seen_set.add(dedup_key)
            tools_map.setdefault(t_key, []).append(acc_view)

    status_rank = {"can_dang_nhap": 0, "het_han_muc": 1, "dung": 2}
    groups: list[dict] = []
    for tool_name, accs in tools_map.items():
        accs.sort(
            key=lambda a: (
                status_rank.get(a["trang_thai"], 3),
                a["may"],
                a["ho_so_chrome"].lower(),
                a["email_che"].lower(),
                a["ma"].lower(),
            )
        )
        c_ok = sum(1 for a in accs if a["trang_thai"] == "dung")
        c_hm = sum(1 for a in accs if a["trang_thai"] == "het_han_muc")
        c_dn = sum(1 for a in accs if a["trang_thai"] == "can_dang_nhap")
        groups.append(
            {
                "cong_cu": tool_name,
                "tai_khoan": accs,
                "tong": len(accs),
                "dung_duoc": c_ok,
                "het_han_muc": c_hm,
                "can_dang_nhap": c_dn,
                "can_xu_ly": c_hm + c_dn,
            }
        )

    groups.sort(
        key=lambda g: (
            0 if g["can_xu_ly"] > 0 else 1,
            -g["can_dang_nhap"],
            -g["het_han_muc"],
            g["cong_cu"],
        )
    )
    return groups


def _summarize_crawler_entries(crawler_by_may: dict[str, dict]) -> list[dict]:
    """Chuẩn hóa dữ liệu `hang-doi/may/<may>-crawler.json` để đưa lên tab Công cụ."""
    ket_qua: list[dict] = []
    for m_code in sorted(crawler_by_may):
        raw = crawler_by_may[m_code] or {}
        nguon_rows: list[dict] = []
        for item in raw.get("nguon") or []:
            if not isinstance(item, dict):
                continue
            tt = str(item.get("trang_thai") or "chua_chay").strip().lower()
            if tt not in ("ok", "loi", "bi_chan", "chua_chay"):
                tt = "chua_chay"
            nguon_rows.append(
                {
                    "nguon": _mask_sensitive_text(str(item.get("nguon") or "").strip())[:80],
                    "lan_chay_cuoi": str(item.get("lan_chay_cuoi") or "").strip(),
                    "so_trang": _normalize_nonneg_int(item.get("so_trang")),
                    "loi_gan_nhat": _mask_sensitive_text(str(item.get("loi_gan_nhat") or "").strip())[:180],
                    "thu_muc_du_lieu": _mask_sensitive_text(str(item.get("thu_muc_du_lieu") or "").strip())[:180],
                    "trang_thai": tt,
                }
            )
        da_thu = [_mask_sensitive_text(str(p).strip()) for p in (raw.get("duong_dan_da_thu") or []) if str(p).strip()]
        ket_qua.append(
            {
                "may": m_code,
                "tim_thay": bool(raw.get("tim_thay") or nguon_rows),
                "mcp_linhx_crawler": bool(raw.get("mcp_linhx_crawler")),
                "nguon": nguon_rows,
                "duong_dan_da_thu": da_thu,
                "cap_nhat_luc": str(raw.get("cap_nhat_luc") or "").strip(),
            }
        )
    return ket_qua


def _summarize_zalo_entries(zalo_by_may: dict[str, dict]) -> list[dict]:
    """Chuẩn hóa dữ liệu `hang-doi/may/<may>-zalo.json` (chỉ tên nhóm, không SĐT/thành viên/nội dung)."""
    ket_qua: list[dict] = []
    for m_code in sorted(zalo_by_may):
        raw = zalo_by_may[m_code] or {}
        listeners: list[dict] = []
        for item in raw.get("bo_nghe") or []:
            if not isinstance(item, dict):
                continue
            raw_groups = item.get("nhom") if isinstance(item.get("nhom"), list) else []
            groups = [
                _mask_sensitive_text(str(g).strip(), mask_phones=True)[:80]
                for g in raw_groups
                if str(g).strip()
            ]
            listeners.append(
                {
                    "ten": _mask_sensitive_text(str(item.get("ten") or "").strip(), mask_phones=True)[:80],
                    "duong_dan": _mask_sensitive_text(str(item.get("duong_dan") or "").strip(), mask_phones=True)[:180],
                    "dang_chay": bool(item.get("dang_chay")),
                    "nhom": groups,
                    "tin_cuoi_luc": str(item.get("tin_cuoi_luc") or "").strip(),
                    "loi_gan_nhat": _mask_sensitive_text(str(item.get("loi_gan_nhat") or "").strip(), mask_phones=True)[:180],
                }
            )
        da_thu = [_mask_sensitive_text(str(p).strip()) for p in (raw.get("duong_dan_da_thu") or []) if str(p).strip()]
        ket_qua.append(
            {
                "may": m_code,
                "tim_thay": bool(raw.get("tim_thay") or listeners),
                "bo_nghe": listeners,
                "duong_dan_da_thu": da_thu,
                "cap_nhat_luc": str(raw.get("cap_nhat_luc") or "").strip(),
            }
        )
    return ket_qua


def _summarize_machine_accounts(
    *,
    profiles_by_machine: dict[str, dict],
    machine_accounts_by_may: dict[str, dict],
    ledger_rows: list[dict],
    current_time: datetime,
) -> list[dict]:
    """Gộp thống kê tài khoản mỗi máy từ `tai-khoan.json` và `may/<may>-tai-khoan.json`."""
    ledger_machines = {
        str(r.get("may") or "").strip().lower()
        for r in ledger_rows
        if str(r.get("may") or "").strip().lower() not in ("", "bat-ky", "*", "all", "tat-ca")
    }
    all_machines = sorted(set(profiles_by_machine) | set(machine_accounts_by_may) | ledger_machines)
    summaries: list[dict] = []

    for m_code in all_machines:
        statuses: list[str] = []
        seen_profiles: set[str] = set()
        seen_emails: set[str] = set()

        for row in ledger_rows:
            if row.get("may") != m_code:
                continue
            tt = row.get("trang_thai") or "dung"
            if tt == "het_han_muc":
                mo_dt = parse_iso_datetime(row.get("mo_lai_luc"))
                if mo_dt is not None and current_time >= mo_dt:
                    tt = "dung"
            statuses.append(tt)
            hs_key = str(row.get("ho_so_chrome") or "").strip().lower()
            em_key = str(row.get("email_che") or "").strip().lower()
            if hs_key:
                seen_profiles.add(hs_key)
            if em_key:
                seen_emails.add(em_key)

        mach_acc = machine_accounts_by_may.get(m_code) or {}
        for prof in mach_acc.get("ho_so_chrome") or []:
            if not isinstance(prof, dict):
                continue
            raw_em = str(prof.get("email_che") or prof.get("email") or "").strip()
            email_che = _mask_email(raw_em) if "@" in raw_em else _mask_emails_in_text(raw_em)
            thu_muc = str(prof.get("thu_muc") or prof.get("ho_so_chrome") or "").strip()
            hs_key = thu_muc.lower()
            em_key = email_che.lower()
            if not em_key:
                continue
            if (hs_key and hs_key in seen_profiles) or (em_key and em_key in seen_emails):
                continue
            tt_prof = str(prof.get("trang_thai") or "dung").strip().lower()
            if tt_prof not in ("dung", "het_han_muc", "can_dang_nhap"):
                tt_prof = "dung"
            statuses.append(tt_prof)
            if hs_key:
                seen_profiles.add(hs_key)
            if em_key:
                seen_emails.add(em_key)

        dung_duoc = sum(1 for st in statuses if st == "dung")
        het_han_muc = sum(1 for st in statuses if st == "het_han_muc")
        can_dang_nhap = sum(1 for st in statuses if st == "can_dang_nhap")
        agy_tk = _mask_emails_in_text(str(mach_acc.get("agy_tai_khoan") or ""))
        summaries.append(
            {
                "may": m_code,
                "dung_duoc": dung_duoc,
                "het_han_muc": het_han_muc,
                "can_dang_nhap": can_dang_nhap,
                "tong": len(statuses),
                "agy_tai_khoan": agy_tk,
            }
        )
    return summaries


def get_local_tz():
    """Lấy múi giờ cục bộ của máy hiện tại."""
    return datetime.now().astimezone().tzinfo or timezone.utc


def now_local() -> datetime:
    """Trả về thời điểm hiện tại có gắn múi giờ cục bộ."""
    return datetime.now().astimezone()


def parse_iso_datetime(raw: str | None) -> datetime | None:
    """Phân tích chuỗi thời gian ISO-8601 (hỗ trợ Z, +0700, +07:00 trên Python >= 3.9)."""
    if not raw:
        return None
    text = str(raw).strip()
    if not text:
        return None
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    else:
        text = _TZ_COMPACT_RE.sub(r"\1:\2", text)
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=get_local_tz())
    return dt.astimezone(get_local_tz())


def datetime_from_epoch(epoch_seconds: float) -> datetime:
    """Chuyển đổi epoch giây sang datetime có múi giờ cục bộ."""
    return datetime.fromtimestamp(float(epoch_seconds), tz=get_local_tz())


def format_iso(dt: datetime | None) -> str:
    """Định dạng datetime sang chuỗi ISO-8601 có múi giờ."""
    if dt is None:
        return ""
    return dt.astimezone(get_local_tz()).isoformat(timespec="seconds")


def format_display_time(dt: datetime | None) -> str:
    """Định dạng thời gian ngắn gọn để hiển thị trên bảng."""
    if dt is None:
        return "—"
    local_dt = dt.astimezone(get_local_tz())
    return local_dt.strftime("%Y-%m-%d %H:%M:%S")


def format_duration_vi(seconds: float) -> str:
    """Định dạng khoảng thời gian bằng tiếng Việt dễ đọc."""
    total = max(0, int(round(seconds)))
    if total < 60:
        return f"{total} giây"
    minutes, sec = divmod(total, 60)
    if minutes < 60:
        return f"{minutes} phút {sec} giây" if sec else f"{minutes} phút"
    hours, rem_min = divmod(minutes, 60)
    if hours < 24:
        return f"{hours} giờ {rem_min} phút" if rem_min else f"{hours} giờ"
    days, rem_hours = divmod(hours, 24)
    return f"{days} ngày {rem_hours} giờ" if rem_hours else f"{days} ngày"


def is_safe_ticket_id(ticket_id: str) -> bool:
    """Kiểm tra mã phiếu an toàn, chống leo thư mục (path traversal)."""
    if not ticket_id or ".." in ticket_id:
        return False
    if ticket_id in (".", ".."):
        return False
    return bool(_SAFE_TICKET_ID_RE.match(ticket_id))


def _is_reparse_or_symlink(path_obj: Path) -> bool:
    """Kiểm tra symlink hoặc NTFS junction/reparse point trên Windows."""
    try:
        if path_obj.is_symlink():
            return True
        is_junc = getattr(path_obj, "is_junction", None)
        if callable(is_junc) and is_junc():
            return True
        st_info = os.lstat(path_obj)
        if os.name == "nt":
            attrs = getattr(st_info, "st_file_attributes", 0)
            if attrs & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400):
                return True
    except OSError:
        return False
    return False


def _has_symlink_along_path(target_abs: Path, root_dir: Path) -> bool:
    """Kiểm tra có symlink/junction nào trên đoạn từ root_dir xuống target_abs hay không."""
    if _is_reparse_or_symlink(root_dir):
        return True
    try:
        rel_str = os.path.relpath(str(target_abs), str(root_dir))
    except ValueError:
        return True
    if rel_str in (".", ""):
        return False
    cur = root_dir
    for part in Path(rel_str).parts:
        if part in ("", "."):
            continue
        if part == "..":
            return True
        cur = cur / part
        if os.path.lexists(cur) and _is_reparse_or_symlink(cur):
            return True
    return False


def _is_under_root_norm(cand_abs: str, root_abs: str) -> bool:
    """Kiểm tra cand_abs nằm nghiêm ngặt dưới root_abs và cùng ổ đĩa."""
    c_drive = os.path.splitdrive(cand_abs)[0]
    r_drive = os.path.splitdrive(root_abs)[0]
    if os.path.normcase(c_drive) != os.path.normcase(r_drive):
        return False
    c_norm = os.path.normcase(cand_abs)
    r_norm = os.path.normcase(root_abs)
    if c_norm == r_norm:
        return False
    try:
        return os.path.commonpath([c_norm, r_norm]) == r_norm
    except ValueError:
        return False


def resolve_safe_tep_path(
    raw_p: str | None,
    allowed_roots: list[Path | str],
    allowed_exts: frozenset[str] = ALLOWED_TEP_EXTS,
    max_bytes: int = MAX_TEP_BYTES,
) -> tuple[Path | None, int, str]:
    """Kiểm tra và giải quyết đường dẫn tệp an toàn nằm dưới goc_anh của dự án."""
    if raw_p is None:
        return None, 400, "Thiếu tham số p"
    raw_str = str(raw_p).strip()
    if not raw_str or "\x00" in raw_str:
        return None, 400, "Thiếu đường dẫn p hợp lệ"

    if ".." in raw_str or ".." in re.split(r"[\\/]+", raw_str):
        return None, 403, "Chặn leo thư mục (..)"

    if raw_str.startswith("\\\\") or raw_str.startswith("//"):
        return None, 403, "Chặn đường dẫn mạng UNC"

    cand = Path(raw_str)
    if os.name == "nt":
        if not cand.drive or cand.root not in ("\\", "/"):
            return None, 403, "Đường dẫn phải là đường dẫn tuyệt đối kèm ổ đĩa"
    elif not cand.is_absolute():
        return None, 403, "Đường dẫn phải tuyệt đối"

    if cand.suffix.lower() not in allowed_exts:
        return None, 403, "Đuôi tệp không được phép"

    valid_roots: list[tuple[Path, Path]] = []
    for raw_root in allowed_roots:
        r_str = str(raw_root or "").strip()
        if not r_str or r_str.startswith("\\\\") or r_str.startswith("//"):
            continue
        r_path = Path(r_str)
        if os.name == "nt" and (not r_path.drive or r_path.root not in ("\\", "/")):
            continue
        if not r_path.is_absolute() or _is_reparse_or_symlink(r_path):
            continue
        try:
            if not r_path.is_dir():
                continue
            r_real = r_path.resolve(strict=True)
        except OSError:
            continue
        valid_roots.append((Path(os.path.abspath(str(r_path))), r_real))

    if not valid_roots:
        return None, 403, "Chưa cấu hình goc_anh hợp lệ"

    cand_abs_str = os.path.abspath(str(cand))
    cand_abs = Path(cand_abs_str)
    matched_roots: list[tuple[Path, Path]] = []
    for r_abs, r_real in valid_roots:
        if _is_under_root_norm(cand_abs_str, str(r_real)) or _is_under_root_norm(cand_abs_str, str(r_abs)):
            matched_roots.append((r_abs, r_real))

    if not matched_roots:
        return None, 403, "Đường dẫn nằm ngoài goc_anh hoặc khác ổ đĩa"

    # Kiểm symlink/junction dọc đường đi trước khi đụng tới tệp đích
    for r_abs, r_real in matched_roots:
        if _is_under_root_norm(cand_abs_str, str(r_abs)) and _has_symlink_along_path(cand_abs, r_abs):
            return None, 403, "Chặn symlink hoặc junction trong đường dẫn"
        if _is_under_root_norm(cand_abs_str, str(r_real)) and _has_symlink_along_path(cand_abs, r_real):
            return None, 403, "Chặn symlink hoặc junction trong đường dẫn"

    if _is_reparse_or_symlink(cand_abs):
        return None, 403, "Chặn symlink hoặc junction ở tệp đích"
    if not os.path.lexists(cand_abs):
        return None, 404, "Không tìm thấy tệp"
    if not cand_abs.is_file():
        return None, 403, "Chỉ phục vụ tệp thường"

    try:
        cand_real = cand_abs.resolve(strict=True)
    except OSError:
        return None, 404, "Không thể đọc tệp"

    if not any(_is_under_root_norm(str(cand_real), str(r_real)) for _r_abs, r_real in matched_roots):
        return None, 403, "Đường dẫn sau resolve vượt ngoài goc_anh"

    try:
        size_bytes = cand_real.stat().st_size
    except OSError:
        return None, 404, "Không thể đọc kích thước tệp"
    if size_bytes > max_bytes:
        return None, 413, "Tệp vượt quá giới hạn 20 MB"

    return cand_real, 200, ""


def _parse_dat_token(raw_val: str) -> bool | None:
    """Chuyển đổi giá trị sau `dat:` thành True/False nếu nhận diện được."""
    cleaned = re.sub(r"[*`]+", "", str(raw_val or "")).strip().lower()
    if not cleaned:
        return None
    token = re.split(r"[\s,;(/]+", cleaned)[0]
    if token in ("khong", "không", "false", "0", "no", "fail", "do", "đỏ", "chua", "chưa"):
        return False
    if token in ("co", "có", "true", "1", "yes", "dat", "đạt", "ok", "xanh"):
        return True
    return None


def analyze_ket_qua_dat(meta: dict[str, str], body: str, status: str) -> tuple[bool, bool]:
    """Đánh giá KET-QUA.md đạt hay KHÔNG đạt: trả về (dat, co_dong_dat_tuong_minh)."""
    if (status or "").strip().lower() in ("loi", "dung"):
        return False, True

    meta_dat = (meta or {}).get("dat")
    if meta_dat is not None and str(meta_dat).strip():
        parsed = _parse_dat_token(str(meta_dat))
        if parsed is not None:
            return parsed, True

    lines = (body or "").splitlines()
    for line in lines[:30]:
        m_dat = _DAT_LINE_RE.match(line.strip())
        if m_dat:
            parsed = _parse_dat_token(m_dat.group(1))
            if parsed is not None:
                return parsed, True

    # Quét mục tiêu chí (heading chứa "tiêu chí" cho tới heading kế tiếp) và các dòng có chữ "tiêu chí"
    in_criteria = False
    criteria_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if _TIEU_CHI_HEADING_RE.match(stripped):
            in_criteria = True
            criteria_lines.append(stripped)
            continue
        if in_criteria:
            if _ANY_HEADING_RE.match(stripped):
                in_criteria = False
            else:
                criteria_lines.append(stripped)
                continue
        if _TIEU_CHI_INLINE_RE.search(stripped):
            criteria_lines.append(stripped)

    for cline in criteria_lines:
        if _UPPER_KHONG_RE.search(cline) or _NEG_CONCLUSION_RE.search(cline):
            return False, False

    return True, False


def _split_header_pairs(line: str) -> list[tuple[str, str]] | None:
    """Tách các cặp khóa: giá trị trên một dòng đầu phiếu."""
    m = _HEADER_LINE_RE.match(line.strip())
    if not m:
        return None
    parts = [p.strip() for p in line.split(";") if p.strip()]
    pairs: list[tuple[str, str]] = []
    for part in parts:
        mp = _HEADER_LINE_RE.match(part)
        if not mp:
            return [(m.group(1).lower(), m.group(2).strip())]
        pairs.append((mp.group(1).lower(), mp.group(2).strip()))
    return pairs


def parse_markdown_headers(content: str) -> tuple[dict[str, str], str]:
    """Tách phần header (hỗ trợ cả frontmatter `---` và dòng `khoa: gia_tri`) cùng phần thân."""
    text = (content or "").lstrip("\ufeff")
    lines = text.splitlines()
    meta: dict[str, str] = {}
    body_idx = 0

    if lines and lines[0].strip() == "---":
        end_idx = None
        for idx in range(1, len(lines)):
            if lines[idx].strip() == "---":
                end_idx = idx
                break
        if end_idx is not None:
            for line in lines[1:end_idx]:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                pairs = _split_header_pairs(stripped)
                if pairs:
                    for key, val in pairs:
                        meta[key] = val
            body_idx = end_idx + 1
    else:
        for idx, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                body_idx = idx + 1
                break
            pairs = _split_header_pairs(stripped)
            if not pairs:
                body_idx = idx
                break
            for key, val in pairs:
                meta[key] = val
        else:
            body_idx = len(lines)

    body = "\n".join(lines[body_idx:]).strip()
    return meta, body


def parse_tokens(token_raw: str) -> tuple[int, int, int]:
    """Phân tích dòng `token: vao=123 ra=45` thành (token_vao, token_ra, tong_token)."""
    raw = str(token_raw or "").strip()
    m_in = _TOKEN_IN_RE.search(raw)
    m_out = _TOKEN_OUT_RE.search(raw)
    if m_in or m_out:
        tok_in = int(m_in.group(1)) if m_in else 0
        tok_out = int(m_out.group(1)) if m_out else 0
        return tok_in, tok_out, tok_in + tok_out
    if raw.isdigit():
        total = int(raw)
        return total, 0, total
    return 0, 0, 0


def resolve_queue_root(clone_dir: Path) -> Path:
    """Tìm thư mục gốc `hang-doi` bên trong bản clone."""
    sub = clone_dir / "hang-doi"
    if sub.exists() or not (clone_dir / "moi").exists():
        return sub
    return clone_dir


def run_git_readonly(args: list[str], cwd: Path, check: bool = True, timeout: int = 90) -> subprocess.CompletedProcess:
    """Chạy lệnh git ẩn cửa sổ console, không hỏi mật khẩu tương tác."""
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    kwargs: dict = {}
    if os.name == "nt":
        kwargs["creationflags"] = 0x08000000  # CREATE_NO_WINDOW
    proc = subprocess.run(
        ["git"] + list(args),
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        **kwargs,
    )
    if check and proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise RuntimeError(f"git {' '.join(args)} thất bại ({proc.returncode}): {detail}")
    return proc


def load_git_file_commit_times(clone_dir: Path) -> dict[str, int]:
    """Đọc thời điểm commit mới nhất (epoch giây) cho từng file bằng 1 lệnh git log."""
    if not (clone_dir / ".git").exists():
        return {}
    proc = run_git_readonly(
        ["-c", "core.quotepath=false", "log", "--format=COMMIT|%ct", "--name-only"],
        cwd=clone_dir,
        check=False,
    )
    if proc.returncode != 0:
        return {}
    commit_times: dict[str, int] = {}
    current_ts: int | None = None
    for raw_line in proc.stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("COMMIT|"):
            ts_part = line.split("|", 1)[1].strip()
            try:
                current_ts = int(ts_part)
            except ValueError:
                current_ts = None
            continue
        if current_ts is not None and line not in commit_times:
            # git log duyệt từ mới đến cũ nên lần gặp đầu tiên là lần cập nhật mới nhất của file
            commit_times[line] = current_ts
    return commit_times


def _summarize_text(text: str, max_len: int = 120) -> str:
    """Rút gọn văn bản 1 dòng để hiển thị cột tóm tắt."""
    single = " ".join((text or "").splitlines()).strip()
    if len(single) <= max_len:
        return single
    return single[: max(0, max_len - 3)] + "..."


def _extract_nhip_and_clean_body(raw_body: str, meta: dict[str, str]) -> tuple[str, str]:
    """Tách dòng `nhip: ...` ở cuối thân phiếu đang chạy (hoặc trong header) và trả về (nhip, than_sach)."""
    nhip_val = (meta.get("nhip") or "").strip()
    kept_lines: list[str] = []
    for line in (raw_body or "").splitlines():
        m = _NHIP_LINE_RE.match(line.strip())
        if m:
            nhip_val = m.group(1).strip()
        else:
            kept_lines.append(line)
    return nhip_val, "\n".join(kept_lines).strip()


def _parse_canh_nen_status(
    meta: dict[str, str],
    nhip_line: str,
    current_time: datetime,
    fallback_dt: datetime | None,
    file_dt: datetime | None = None,
) -> tuple[bool, int | None, str, str]:
    """Nhận diện phiếu đang ở chế độ canh nền và sinh nhãn `đang chờ nền · log cuối N phút trước`."""
    raw_canh_nen = (meta.get("canh_nen") or meta.get("che_do_nen") or "").strip()
    canh_nen_flag_dt = parse_iso_datetime(raw_canh_nen)
    nhip_txt = (nhip_line or "").strip()
    nhip_lower = nhip_txt.lower()

    meta_enabled = False
    if raw_canh_nen and raw_canh_nen.lower() not in _CANH_NEN_FALSE_VALUES:
        meta_enabled = bool(canh_nen_flag_dt is not None or raw_canh_nen.lower() in _CANH_NEN_TRUE_VALUES or raw_canh_nen)

    nhip_has_marker = bool(
        "đang chờ nền" in nhip_lower
        or "[canh-nen" in nhip_lower
        or "log_cuoi=" in nhip_lower
        or _CANH_NEN_WAITING_BG_RE.search(nhip_txt)
        or _CANH_NEN_ROOT_IDLE_RE.search(nhip_txt)
    )
    if not (meta_enabled or nhip_has_marker):
        return False, None, "", nhip_txt

    m_iso = _CANH_NEN_LOG_ISO_RE.search(nhip_txt)
    log_dt = (
        parse_iso_datetime(m_iso.group(1) if m_iso else None)
        or parse_iso_datetime(meta.get("log_cuoi"))
        or canh_nen_flag_dt
    )
    if log_dt is not None:
        n_phut = max(0, int((current_time - log_dt).total_seconds() // 60.0))
    elif (meta.get("log_cuoi_phut") or "").strip():
        try:
            base_min = max(0, int(float(meta["log_cuoi_phut"].strip())))
        except ValueError:
            base_min = 0
        delta_file = (
            max(0, int((current_time - file_dt).total_seconds() // 60.0))
            if file_dt is not None and current_time > file_dt
            else 0
        )
        n_phut = base_min + delta_file
    else:
        m_phut = _CANH_NEN_LOG_PHUT_RE.search(nhip_txt)
        if m_phut:
            base_min = max(0, int(m_phut.group(1)))
            delta_file = (
                max(0, int((current_time - file_dt).total_seconds() // 60.0))
                if file_dt is not None and current_time > file_dt
                else 0
            )
            n_phut = base_min + delta_file
        elif fallback_dt is not None:
            n_phut = max(0, int((current_time - fallback_dt).total_seconds() // 60.0))
        else:
            n_phut = 0

    nhan = f"đang chờ nền · log cuối {n_phut} phút trước"
    nhip_clean = _CANH_NEN_LOG_ISO_RE.sub("", nhip_txt)
    nhip_clean = _CANH_NEN_NHAN_TAG_RE.sub(nhan, nhip_clean)
    nhip_clean = re.sub(r"\s{2,}", " ", nhip_clean).strip(" ·-")
    return True, n_phut, nhan, nhip_clean


def _extract_ket_reason(body: str, max_len: int = 90) -> str:
    """Rút lý do ngắn gọn từ thân KET-QUA.md khi phiếu kết thúc `dung` hoặc `loi`."""
    for raw_line in (body or "").splitlines():
        s = raw_line.strip()
        if not s or s.startswith("---"):
            continue
        return _summarize_text(s, max_len)
    return _summarize_text(body or "", max_len)


def _parse_claimed_info(meta: dict[str, str], fallback_machine: str) -> tuple[str, datetime | None]:
    """Tách tên máy và thời điểm nhận từ trường `nhan: <may> <thoi_gian>`."""
    claimed_raw = (meta.get("nhan") or "").strip()
    if claimed_raw:
        parts = claimed_raw.split(None, 1)
        machine = parts[0].strip().lower()
        claimed_dt = parse_iso_datetime(parts[1].strip()) if len(parts) > 1 else None
        return machine, claimed_dt
    if fallback_machine and fallback_machine != "bat-ky":
        return fallback_machine, None
    return "chua-ro", None


def _file_timestamp(
    file_path: Path,
    clone_dir: Path,
    commit_times: dict[str, int],
    explicit_iso: str | None = None,
) -> datetime | None:
    """Xác định thời điểm của file: ưu tiên trường ISO tường minh -> git log -> mtime."""
    explicit_dt = parse_iso_datetime(explicit_iso)
    if explicit_dt is not None:
        return explicit_dt
    try:
        rel_posix = file_path.relative_to(clone_dir).as_posix()
        if rel_posix in commit_times:
            return datetime_from_epoch(commit_times[rel_posix])
    except ValueError:
        pass
    try:
        return datetime_from_epoch(file_path.stat().st_mtime)
    except OSError:
        return None


def read_queue_snapshot(
    clone_dir: Path,
    now: datetime | None = None,
    commit_times: dict[str, int] | None = None,
    max_done: int = MAX_RECENT_DONE,
    inactive_minutes: float = INACTIVE_THRESHOLD_MINUTES,
) -> dict:
    """Đọc toàn bộ trạng thái hàng đợi từ `moi`, `dang`, `xong/*/KET-QUA.md`."""
    clone_dir = Path(clone_dir)
    current_time = (now or now_local()).astimezone(get_local_tz())
    git_times = load_git_file_commit_times(clone_dir) if commit_times is None else commit_times
    qroot = resolve_queue_root(clone_dir)

    machine_events: dict[str, dict] = {}
    running_count_by_machine: dict[str, int] = {}
    running_by_machine: dict[str, list[dict]] = {}
    latest_done_by_machine: dict[str, dict] = {}
    known_machines: set[str] = set()

    def record_machine_event(machine_name: str, event_type: str, ticket_id: str, event_dt: datetime | None) -> None:
        m = (machine_name or "").strip().lower()
        if not m or m in ("bat-ky", "*", "all", "tat-ca", "chua-ro", "(khong)"):
            return
        known_machines.add(m)
        if event_dt is None:
            return
        prev = machine_events.get(m)
        if prev is None or event_dt >= prev["dt"]:
            machine_events[m] = {
                "dt": event_dt,
                "su_kien": event_type,
                "phieu": ticket_id,
            }

    # 0. Đọc hang-doi/can-linh/*.md (Cần anh làm)
    can_linh_items: list[dict] = []
    dir_can_linh = qroot / "can-linh"
    if dir_can_linh.is_dir():
        for cl_file in sorted(dir_can_linh.glob("*.md"), key=lambda p: p.name):
            try:
                raw_cl = cl_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            meta_cl, body_cl = parse_markdown_headers(raw_cl)
            ticket_id = (meta_cl.get("phieu") or cl_file.stem).strip()
            machine_cl = (meta_cl.get("may") or "chua-ro").strip().lower()
            if machine_cl and machine_cl not in ("bat-ky", "*", "all", "tat-ca", "chua-ro", "(khong)"):
                known_machines.add(machine_cl)
            viec_cl = (meta_cl.get("viec") or body_cl or ticket_id).strip()
            lenh_cl = (meta_cl.get("lenh") or "").strip()
            gio_dt = _file_timestamp(cl_file, clone_dir, git_times, meta_cl.get("gio"))
            can_linh_items.append(
                {
                    "id": cl_file.stem,
                    "may": machine_cl,
                    "phieu": ticket_id,
                    "viec": viec_cl,
                    "lenh": lenh_cl,
                    "gio": format_iso(gio_dt),
                    "gio_hien_thi": format_display_time(gio_dt),
                    "ket_qua_url": f"/phieu/{urllib.parse.quote(ticket_id)}",
                    "_sort_ts": gio_dt.timestamp() if gio_dt else 0.0,
                }
            )
    can_linh_items.sort(key=lambda item: (-item["_sort_ts"], item["phieu"]))
    for item in can_linh_items:
        item.pop("_sort_ts", None)

    # 0b. Đọc hang-doi/may/*.json (Hồ sơ máy + tài khoản + crawler + zalo)
    profiles_by_machine: dict[str, dict] = {}
    machine_accounts_by_may: dict[str, dict] = {}
    crawler_by_may: dict[str, dict] = {}
    zalo_by_may: dict[str, dict] = {}
    dir_profiles = qroot / "may"
    if dir_profiles.is_dir():
        for prof_file in sorted(dir_profiles.glob("*.json"), key=lambda p: p.name):
            try:
                prof_data = json.loads(prof_file.read_text(encoding="utf-8", errors="replace"))
            except (OSError, ValueError, TypeError):
                continue
            if not isinstance(prof_data, dict):
                continue
            if prof_file.name.endswith("-tai-khoan.json"):
                raw_may = str(prof_data.get("ma_may") or prof_file.stem[: -len("-tai-khoan")]).strip().lower()
                if raw_may and raw_may not in ("bat-ky", "*", "all", "tat-ca"):
                    known_machines.add(raw_may)
                    machine_accounts_by_may[raw_may] = prof_data
                continue
            if prof_file.name.endswith("-crawler.json"):
                raw_may = str(prof_data.get("ma_may") or prof_file.stem[: -len("-crawler")]).strip().lower()
                if raw_may and raw_may not in ("bat-ky", "*", "all", "tat-ca"):
                    known_machines.add(raw_may)
                    crawler_by_may[raw_may] = prof_data
                continue
            if prof_file.name.endswith("-zalo.json"):
                raw_may = str(prof_data.get("ma_may") or prof_file.stem[: -len("-zalo")]).strip().lower()
                if raw_may and raw_may not in ("bat-ky", "*", "all", "tat-ca"):
                    known_machines.add(raw_may)
                    zalo_by_may[raw_may] = prof_data
                continue
            m_code = str(prof_data.get("ma_may") or prof_file.stem).strip().lower()
            if not m_code or m_code in ("bat-ky", "*", "all", "tat-ca"):
                continue
            known_machines.add(m_code)
            # Cảnh báo ổ C dưới 10 GB
            low_disk_c = False
            disk_c_free = None
            for od in prof_data.get("o_dia") or []:
                if isinstance(od, dict) and str(od.get("o") or "").strip().upper().rstrip("\\/") == "C:":
                    try:
                        disk_c_free = float(od.get("trong_gb"))
                        if disk_c_free < LOW_DISK_C_THRESHOLD_GB:
                            low_disk_c = True
                    except (ValueError, TypeError):
                        pass
            prof_enriched = dict(prof_data)
            prof_enriched["ma_may"] = m_code
            prof_enriched["canh_bao_o_c"] = low_disk_c
            prof_enriched["o_c_trong_gb"] = disk_c_free
            profiles_by_machine[m_code] = prof_enriched

    # 1. Đọc hang-doi/dang/*.md (Đang chạy)
    running_items: list[dict] = []
    dir_running = qroot / "dang"
    if dir_running.is_dir():
        for md_file in sorted(dir_running.glob("*.md"), key=lambda p: p.name):
            try:
                raw_text = md_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            ticket_id = md_file.stem
            meta, raw_body = parse_markdown_headers(raw_text)
            nhip_line, body = _extract_nhip_and_clean_body(raw_body, meta)
            target_machine = (meta.get("may") or "bat-ky").strip().lower()
            claimed_machine, claimed_dt = _parse_claimed_info(meta, target_machine)
            file_dt = _file_timestamp(md_file, clone_dir, git_times)
            if claimed_dt is None:
                claimed_dt = file_dt
            last_active_dt = file_dt if (nhip_line and file_dt and claimed_dt and file_dt > claimed_dt) else claimed_dt

            elapsed_sec = max(0.0, (current_time - claimed_dt).total_seconds()) if claimed_dt else 0.0
            try:
                limit_min = float(meta.get("tran_phut") or 40)
            except ValueError:
                limit_min = 40.0

            kind = (meta.get("loai") or "code").strip().lower()
            is_canh_nen, log_cuoi_phut, nhan_canh_nen, nhip_clean = _parse_canh_nen_status(
                meta=meta,
                nhip_line=nhip_line,
                current_time=current_time,
                fallback_dt=last_active_dt,
                file_dt=file_dt,
            )
            record_machine_event(claimed_machine, "nhan", ticket_id, last_active_dt)

            run_entry = {
                "phieu": ticket_id,
                "may": claimed_machine,
                "loai": kind,
                "nhan_luc": format_iso(claimed_dt),
                "nhan_luc_hien_thi": format_display_time(claimed_dt),
                "chay_giay": int(round(elapsed_sec)),
                "chay_phut": round(elapsed_sec / 60.0, 2),
                "chay_bao_lau": format_duration_vi(elapsed_sec) if claimed_dt else "—",
                "tran_phut": int(limit_min) if limit_min.is_integer() else limit_min,
                "nhip": nhip_clean,
                "canh_nen": is_canh_nen,
                "log_cuoi_phut": log_cuoi_phut,
                "nhan_canh_nen": nhan_canh_nen,
                "de": _summarize_text(body or ticket_id),
                "ket_qua_url": f"/phieu/{urllib.parse.quote(ticket_id)}",
                "_sort_ts": claimed_dt.timestamp() if claimed_dt else 0.0,
            }
            if claimed_machine not in ("bat-ky", "chua-ro"):
                running_count_by_machine[claimed_machine] = running_count_by_machine.get(claimed_machine, 0) + 1
                running_by_machine.setdefault(claimed_machine, []).append(run_entry)

            running_items.append(run_entry)
    running_items.sort(key=lambda item: (-item["_sort_ts"], item["phieu"]))
    for m_runs in running_by_machine.values():
        m_runs.sort(key=lambda item: (-item["_sort_ts"], item["phieu"]))
    for item in running_items:
        item.pop("_sort_ts", None)

    # 2. Đọc hang-doi/moi/*.md (Đang chờ)
    waiting_items: list[dict] = []
    dir_waiting = qroot / "moi"
    if dir_waiting.is_dir():
        for md_file in sorted(dir_waiting.glob("*.md"), key=lambda p: p.name):
            try:
                raw_text = md_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            ticket_id = md_file.stem
            meta, body = parse_markdown_headers(raw_text)
            target_machine = (meta.get("may") or "bat-ky").strip().lower()
            if target_machine in ("*", "all", "tat-ca"):
                target_machine = "bat-ky"
            if target_machine != "bat-ky":
                known_machines.add(target_machine)

            kind = (meta.get("loai") or "code").strip().lower()
            try:
                limit_min = float(meta.get("tran_phut") or 40)
            except ValueError:
                limit_min = 40.0
            created_dt = _file_timestamp(md_file, clone_dir, git_times, meta.get("tao_luc"))

            waiting_items.append(
                {
                    "phieu": ticket_id,
                    "may": target_machine,
                    "loai": kind,
                    "tran_phut": int(limit_min) if limit_min.is_integer() else limit_min,
                    "tao_luc": format_iso(created_dt),
                    "tao_luc_hien_thi": format_display_time(created_dt),
                    "de": _summarize_text(body or ticket_id),
                    "ket_qua_url": f"/phieu/{urllib.parse.quote(ticket_id)}",
                }
            )

    # 3. Đọc hang-doi/xong/*/KET-QUA.md (Xong gần nhất 20 phiếu)
    all_done_items: list[dict] = []
    dir_done = qroot / "xong"
    if dir_done.is_dir():
        for sub_dir in sorted(dir_done.iterdir(), key=lambda p: p.name):
            if not sub_dir.is_dir():
                continue
            kq_file = sub_dir / "KET-QUA.md"
            if not kq_file.is_file():
                continue
            try:
                raw_kq = kq_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            meta, body = parse_markdown_headers(raw_kq)
            ticket_id = sub_dir.name
            machine_name = (meta.get("may") or "chua-ro").strip().lower()
            status = (meta.get("trang_thai") or "loi").strip().lower()
            if status not in ("xong", "loi", "dung", "huy"):
                status = "loi"
            try:
                minutes_val = round(float(meta.get("phut") or 0.0), 2)
            except ValueError:
                minutes_val = 0.0
            token_raw = (meta.get("token") or "vao=0 ra=0").strip()
            tok_in, tok_out, tok_total = parse_tokens(token_raw)

            done_dt = _file_timestamp(
                kq_file,
                clone_dir,
                git_times,
                meta.get("xong_luc") or meta.get("luc"),
            )
            done_start_dt = parse_iso_datetime(meta.get("nhan_luc") or meta.get("bat_dau"))
            if done_start_dt is None and meta.get("nhan"):
                _, done_start_dt = _parse_claimed_info(meta, "")
                if done_start_dt is None:
                    done_start_dt = parse_iso_datetime(meta.get("nhan"))
            if done_start_dt is None and done_dt is not None:
                done_start_dt = done_dt - timedelta(minutes=max(0.0, minutes_val))
            record_machine_event(machine_name, "xong", ticket_id, done_dt)

            dat_ok, has_explicit_dat = analyze_ket_qua_dat(meta, body, status)
            done_entry = {
                "phieu": ticket_id,
                "may": machine_name,
                "trang_thai": status,
                "dat": dat_ok,
                "phut": minutes_val,
                "token": token_raw,
                "token_vao": tok_in,
                "token_ra": tok_out,
                "tong_token": tok_total,
                "tep_doi": (meta.get("tep_doi") or "(khong)").strip(),
                "drive": (meta.get("drive") or "(khong)").strip(),
                "nhan_luc": format_iso(done_start_dt),
                "xong_luc": format_iso(done_dt),
                "xong_luc_hien_thi": format_display_time(done_dt),
                "tom_tat": _summarize_text(body, 100),
                "ly_do_ngan": _extract_ket_reason(body, 90) if status in ("loi", "dung", "huy") else "",
                "ket_qua": raw_kq,
                "ket_qua_url": f"/phieu/{urllib.parse.quote(ticket_id)}",
                "_co_dong_dat": has_explicit_dat,
                "_sort_ts": done_dt.timestamp() if done_dt else 0.0,
            }
            all_done_items.append(done_entry)
            if machine_name and machine_name not in ("bat-ky", "chua-ro", "(khong)"):
                prev_done = latest_done_by_machine.get(machine_name)
                if prev_done is None or done_entry["_sort_ts"] >= prev_done["_sort_ts"]:
                    latest_done_by_machine[machine_name] = dict(done_entry)

    all_done_items.sort(key=lambda item: (-item["_sort_ts"], item["phieu"]))
    done_info_map: dict[str, dict] = {item["phieu"]: dict(item) for item in all_done_items}
    recent_done = [dict(item) for item in all_done_items[: max(0, int(max_done))]]
    for item in recent_done:
        item.pop("_sort_ts", None)
        item.pop("_co_dong_dat", None)

    # 4. Tổng hợp trạng thái từng máy: đang làm gì (phiếu + phút + nhip), trạng thái (chạy / rảnh / kẹt / im lặng > 30p)
    machines_list: list[dict] = []
    ho_so_list: list[dict] = []
    for machine_name in sorted(known_machines):
        ev = machine_events.get(machine_name)
        m_runs = running_by_machine.get(machine_name) or []
        run_primary = m_runs[0] if m_runs else None
        last_done = latest_done_by_machine.get(machine_name)
        prof = profiles_by_machine.get(machine_name)
        if prof is not None:
            ho_so_list.append(prof)

        nhip_may = (run_primary.get("nhip") or "") if run_primary else ""
        dang_lam_phieu = run_primary["phieu"] if run_primary else ""
        dang_lam_phut = run_primary["chay_phut"] if run_primary else 0.0
        canh_nen_may = bool(run_primary and run_primary.get("canh_nen"))
        log_cuoi_phut_may = run_primary.get("log_cuoi_phut") if run_primary else None
        nhan_canh_nen_may = (run_primary.get("nhan_canh_nen") or "") if run_primary else ""

        # Kiểm tra dừng/lỗi gần nhất của máy
        ket_phieu = ""
        ket_trang_thai = ""
        ket_ly_do = ""
        if last_done and last_done.get("trang_thai") in ("loi", "dung"):
            ket_phieu = last_done["phieu"]
            ket_trang_thai = last_done["trang_thai"]
            ket_ly_do = last_done.get("ly_do_ngan") or last_done.get("tom_tat") or ket_trang_thai

        if ev is not None:
            last_dt: datetime = ev["dt"]
            idle_sec = max(0.0, (current_time - last_dt).total_seconds())
            idle_min = idle_sec / 60.0
            is_overdue = idle_min > float(inactive_minutes)
            if run_primary is not None:
                tt_may = "im-lang" if is_overdue else "chay"
            elif ket_phieu:
                tt_may = "ket"
            elif is_overdue:
                tt_may = "im-lang"
            else:
                tt_may = "ranh"

            machines_list.append(
                {
                    "may": machine_name,
                    "trang_thai_may": tt_may,
                    "dang_lam_phieu": dang_lam_phieu,
                    "dang_lam_phut": dang_lam_phut,
                    "nhip": nhip_may,
                    "canh_nen": canh_nen_may,
                    "log_cuoi_phut": log_cuoi_phut_may,
                    "nhan_canh_nen": nhan_canh_nen_may,
                    "ket_phieu": ket_phieu,
                    "ket_trang_thai": ket_trang_thai,
                    "ket_ly_do": ket_ly_do,
                    "su_kien_cuoi": ev["su_kien"],
                    "phieu_cuoi": ev["phieu"],
                    "lan_cuoi": format_iso(last_dt),
                    "lan_cuoi_hien_thi": format_display_time(last_dt),
                    "cach_day": f"{format_duration_vi(idle_sec)} trước",
                    "khong_hoat_dong_phut": round(idle_min, 2),
                    "qua_30_phut": is_overdue,
                    "dang_chay_so_luong": running_count_by_machine.get(machine_name, 0),
                    "vai_tro": (prof or {}).get("vai_tro") or "",
                    "canh_bao_o_c": bool((prof or {}).get("canh_bao_o_c")),
                }
            )
        else:
            # Nếu máy mới đăng ký hồ sơ may/<id>.json gần đây mà chưa chạy phiếu nào
            prof_dt = parse_iso_datetime((prof or {}).get("cap_nhat_luc")) if prof else None
            if prof_dt is not None:
                idle_sec = max(0.0, (current_time - prof_dt).total_seconds())
                idle_min = idle_sec / 60.0
                is_overdue = idle_min > float(inactive_minutes)
                tt_may = "im-lang" if is_overdue else "ranh"
                lan_cuoi_iso = format_iso(prof_dt)
                lan_cuoi_ht = format_display_time(prof_dt)
                cach_day_txt = f"{format_duration_vi(idle_sec)} trước"
                khong_hd_phut = round(idle_min, 2)
            else:
                is_overdue = True
                tt_may = "im-lang"
                lan_cuoi_iso = ""
                lan_cuoi_ht = "Chưa từng hoạt động"
                cach_day_txt = "—"
                khong_hd_phut = None

            machines_list.append(
                {
                    "may": machine_name,
                    "trang_thai_may": tt_may,
                    "dang_lam_phieu": "",
                    "dang_lam_phut": 0.0,
                    "nhip": "",
                    "canh_nen": False,
                    "log_cuoi_phut": None,
                    "nhan_canh_nen": "",
                    "ket_phieu": ket_phieu,
                    "ket_trang_thai": ket_trang_thai,
                    "ket_ly_do": ket_ly_do,
                    "su_kien_cuoi": "chua-co",
                    "phieu_cuoi": "",
                    "lan_cuoi": lan_cuoi_iso,
                    "lan_cuoi_hien_thi": lan_cuoi_ht,
                    "cach_day": cach_day_txt,
                    "khong_hoat_dong_phut": khong_hd_phut,
                    "qua_30_phut": is_overdue,
                    "dang_chay_so_luong": 0,
                    "vai_tro": (prof or {}).get("vai_tro") or "",
                    "canh_bao_o_c": bool((prof or {}).get("canh_bao_o_c")),
                }
            )

    projects_list = read_projects_snapshot(
        clone_dir=clone_dir,
        current_time=current_time,
        running_items=running_items,
        waiting_items=waiting_items,
        done_info_map=done_info_map,
        can_linh_items=can_linh_items,
    )

    ledger_rows = _read_tai_khoan_ledger(qroot)
    account_summary_list = _summarize_machine_accounts(
        profiles_by_machine=profiles_by_machine,
        machine_accounts_by_may=machine_accounts_by_may,
        ledger_rows=ledger_rows,
        current_time=current_time,
    )
    account_by_machine = {item["may"]: item for item in account_summary_list}
    for prof in ho_so_list:
        m_acc = account_by_machine.get(prof.get("ma_may") or "")
        if m_acc is not None:
            prof["tai_khoan"] = m_acc

    tools_ledger = _build_tools_ledger_groups(
        ledger_rows=ledger_rows,
        machine_accounts_by_may=machine_accounts_by_may,
        current_time=current_time,
    )
    crawler_list = _summarize_crawler_entries(crawler_by_may)
    zalo_list = _summarize_zalo_entries(zalo_by_may)

    return {
        "cap_nhat_luc": format_iso(current_time),
        "cap_nhat_hien_thi": format_display_time(current_time),
        "can_linh": can_linh_items,
        "dang_chay": running_items,
        "dang_cho": waiting_items,
        "tong_xong": len(all_done_items),
        "xong_gan_nhat": recent_done,
        "may": machines_list,
        "ho_so_may": ho_so_list,
        "du_an": projects_list,
        "tai_khoan_may": account_summary_list,
        "so_cong_cu": tools_ledger,
        "crawler": crawler_list,
        "zalo": zalo_list,
    }


def _valid_goc_anh_root(raw_root: str | None) -> Path | None:
    """Kiểm tra và chuẩn hóa thư mục `goc_anh` của dự án (chặn đường dẫn tương đối, UNC, symlink)."""
    s = str(raw_root or "").strip()
    if not s or s.startswith("\\\\") or s.startswith("//"):
        return None
    p = Path(s)
    if os.name == "nt" and (not p.drive or p.root not in ("\\", "/")):
        return None
    if not p.is_absolute() or _is_reparse_or_symlink(p):
        return None
    try:
        if not p.is_dir():
            return None
        return Path(os.path.abspath(str(p)))
    except OSError:
        return None


def _collect_project_roots(clone_dir: Path) -> list[Path]:
    """Thu thập danh sách tất cả `goc_anh` hợp lệ từ `hang-doi/du-an/*.json`."""
    qroot = resolve_queue_root(Path(clone_dir))
    dir_proj = qroot / "du-an"
    if not dir_proj.is_dir():
        return []
    roots: list[Path] = []
    seen: set[str] = set()
    for proj_file in sorted(dir_proj.glob("*.json"), key=lambda p: p.name):
        try:
            proj = json.loads(proj_file.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError, TypeError):
            continue
        if not isinstance(proj, dict):
            continue
        root = _valid_goc_anh_root(proj.get("goc_anh"))
        if root is not None:
            key = os.path.normcase(str(root))
            if key not in seen:
                seen.add(key)
                roots.append(root)
    return roots


def _sanitize_log_line(line: str) -> str:
    """Ẩn giá trị bí mật nếu vô tình xuất hiện trong dòng log."""
    return _SECRET_LINE_RE.sub(lambda m: f"{m.group(1)}{m.group(2)} [DA-AN]", line)


def scan_ticket_images(
    goc_root: Path | None,
    ticket_id: str,
    max_images: int = MAX_TICKET_IMAGES,
) -> list[dict]:
    """Quét `<goc_anh>/<id phiếu>/bang-chung/**` lấy tối đa 6 ảnh mới nhất, ưu tiên `ghep-*.png`."""
    if goc_root is None or not is_safe_ticket_id(ticket_id):
        return []
    bc_dir = goc_root / ticket_id / "bang-chung"
    try:
        if not bc_dir.is_dir() or _has_symlink_along_path(bc_dir, goc_root):
            return []
    except OSError:
        return []

    found: list[dict] = []
    for dirpath, dirnames, filenames in os.walk(bc_dir, followlinks=False):
        dirnames[:] = [d for d in dirnames if not _is_reparse_or_symlink(Path(dirpath) / d)]
        for fname in filenames:
            fp = Path(dirpath) / fname
            if fp.suffix.lower() not in IMAGE_TEP_EXTS:
                continue
            real_fp, code, _msg = resolve_safe_tep_path(
                str(fp),
                [goc_root],
                allowed_exts=IMAGE_TEP_EXTS,
            )
            if code != 200 or real_fp is None:
                continue
            try:
                mtime = real_fp.stat().st_mtime
            except OSError:
                continue
            dt = datetime_from_epoch(mtime)
            lower_name = fname.lower()
            is_ghep = lower_name.startswith("ghep-") and fp.suffix.lower() == ".png"
            found.append(
                {
                    "ten": fname,
                    "phieu": ticket_id,
                    "la_ghep": is_ghep,
                    "gio": format_iso(dt),
                    "gio_hien_thi": format_display_time(dt),
                    "url": f"/tep?p={urllib.parse.quote(str(real_fp), safe='')}",
                    "_mtime": mtime,
                }
            )

    found.sort(key=lambda item: (0 if item["la_ghep"] else 1, -item["_mtime"], item["ten"].lower()))
    return found[: max(0, int(max_images))]


def _read_tail_lines(file_path: Path, max_bytes: int = 65536) -> list[str]:
    """Đọc tối đa `max_bytes` cuối file văn bản dạng UTF-8 an toàn."""
    try:
        sz = file_path.stat().st_size
    except OSError:
        return []
    if sz <= 0 or sz > MAX_TEP_BYTES:
        return []
    try:
        with file_path.open("rb") as fh:
            if sz > max_bytes:
                fh.seek(sz - max_bytes)
            chunk = fh.read(max_bytes)
    except OSError:
        return []
    text = chunk.decode("utf-8", errors="replace")
    lines = text.splitlines()
    if sz > max_bytes and len(lines) > 1:
        lines = lines[1:]
    return [_sanitize_log_line(ln) for ln in lines if ln.strip()]


def collect_step_tail_logs(
    goc_root: Path | None,
    qroot: Path,
    ticket_ids: list[str],
    running_map: dict[str, dict],
    max_lines: int = MAX_STEP_LOG_LINES,
) -> list[str]:
    """Thu thập tối đa 30 dòng cuối từ file log của các phiếu và dòng `nhip:` đang chạy."""
    log_files: list[tuple[float, str, Path]] = []
    seen_paths: set[str] = set()

    def _add_log_file(tid: str, fp: Path, root_check: Path | None) -> None:
        if fp.suffix.lower() not in LOG_TEP_EXTS:
            return
        if fp.name.upper() == "KET-QUA.MD":
            return
        if _is_reparse_or_symlink(fp):
            return
        if root_check is not None:
            real_fp, code, _ = resolve_safe_tep_path(str(fp), [root_check], allowed_exts=LOG_TEP_EXTS)
            if code != 200 or real_fp is None:
                return
            fp = real_fp
        try:
            if not fp.is_file():
                return
            mtime = fp.stat().st_mtime
        except OSError:
            return
        key = os.path.normcase(str(fp))
        if key not in seen_paths:
            seen_paths.add(key)
            log_files.append((mtime, tid, fp))

    for tid in ticket_ids:
        if not is_safe_ticket_id(tid):
            continue
        if goc_root is not None:
            for sub_name in ("bang-chung", "_bang-chung"):
                sub_dir = goc_root / tid / sub_name
                try:
                    if sub_dir.is_dir() and not _has_symlink_along_path(sub_dir, goc_root):
                        for dirpath, dirnames, filenames in os.walk(sub_dir, followlinks=False):
                            dirnames[:] = [d for d in dirnames if not _is_reparse_or_symlink(Path(dirpath) / d)]
                            for fname in filenames:
                                _add_log_file(tid, Path(dirpath) / fname, goc_root)
                except OSError:
                    pass
            tid_dir = goc_root / tid
            if tid_dir.is_dir() and not _has_symlink_along_path(tid_dir, goc_root):
                try:
                    for fp in sorted(tid_dir.iterdir(), key=lambda p: p.name):
                        if fp.is_file():
                            _add_log_file(tid, fp, goc_root)
                except OSError:
                    pass
            for direct in (goc_root / f"{tid}.log", goc_root / f"{tid}-test.log"):
                _add_log_file(tid, direct, goc_root)

        done_dir = qroot / "xong" / tid
        if done_dir.is_dir() and not _is_reparse_or_symlink(done_dir):
            for fp in sorted(done_dir.iterdir(), key=lambda p: p.name):
                _add_log_file(tid, fp, None)

    log_files.sort(key=lambda item: (item[0], item[2].name.lower()))
    collected: list[str] = []
    for _mtime, tid, fp in log_files[-6:]:
        tail = _read_tail_lines(fp)
        for line in tail[-max_lines:]:
            collected.append(f"[{tid}/{fp.name}] {line}")

    for tid in ticket_ids:
        r_item = running_map.get(tid)
        if r_item and r_item.get("nhip"):
            collected.append(f"[{tid}] nhip: {_sanitize_log_line(str(r_item['nhip']))}")

    return collected[-max(1, int(max_lines)) :]


def _normalize_muc9_row(raw_row: dict) -> dict | None:
    """Chuẩn hóa 1 dòng chỉ số đo mức 9 từ JSON (không bịa số)."""
    if not isinstance(raw_row, dict):
        return None
    ma = str(raw_row.get("ma") or "").strip()
    ten = str(raw_row.get("ten") or raw_row.get("doi_tuong") or raw_row.get("doiTuong") or raw_row.get("nhom") or "").strip()
    nguong = str(raw_row.get("nguong") or "").strip()
    val = raw_row.get("te_nhat")
    if val is None:
        val = raw_row.get("so_do_te_nhat")
    if val is None:
        val = raw_row.get("gia_tri")
    if val is None:
        val = raw_row.get("giaTri")
    te_nhat = "" if val is None else str(val).strip()
    don_vi = str(raw_row.get("don_vi") or raw_row.get("donVi") or "").strip()
    if te_nhat and don_vi and don_vi not in te_nhat:
        te_nhat = f"{te_nhat} {don_vi}".strip()

    raw_dat = raw_row.get("dat")
    if isinstance(raw_dat, bool):
        dat_val: bool | None = raw_dat
    elif raw_dat is not None:
        dat_val = _parse_dat_token(str(raw_dat))
    else:
        ket_qua = str(raw_row.get("ket_qua") or raw_row.get("ketQua") or "").strip().lower()
        if "đạt" in ket_qua or "dat" in ket_qua or ket_qua == "ok":
            dat_val = True
        elif "đỏ" in ket_qua or "trượt" in ket_qua or "khong" in ket_qua or "không" in ket_qua:
            dat_val = False
        else:
            dat_val = None

    if not (ma or ten or nguong or te_nhat):
        return None
    return {
        "ma": ma,
        "ten": ten or ma,
        "nguong": nguong or "—",
        "te_nhat": te_nhat or "—",
        "dat": dat_val,
    }


def _read_do_muc_9(raw_pattern: str | None, goc_root: Path | None) -> dict:
    """Đọc file `do-muc-9.json` mới nhất theo mẫu `chat_luong.do_muc_9`."""
    empty_res = {
        "chua_do": True,
        "tep": "",
        "tep_url": "",
        "cap_nhat_luc": "",
        "cap_nhat_hien_thi": "",
        "chi_so": [],
    }
    pattern = str(raw_pattern or "").strip()
    if not pattern:
        return empty_res

    try:
        matches = glob.glob(pattern, recursive=True)
    except OSError:
        return empty_res

    candidates: list[tuple[float, Path]] = []
    for raw_match in matches:
        if goc_root is not None:
            real_fp, code, _ = resolve_safe_tep_path(
                raw_match,
                [goc_root],
                allowed_exts=frozenset({".json"}),
            )
            if code != 200 or real_fp is None:
                continue
        else:
            p = Path(raw_match)
            if p.suffix.lower() != ".json" or _is_reparse_or_symlink(p) or not p.is_file():
                continue
            try:
                if p.stat().st_size > MAX_TEP_BYTES:
                    continue
                real_fp = p.resolve(strict=True)
            except OSError:
                continue
        try:
            candidates.append((real_fp.stat().st_mtime, real_fp))
        except OSError:
            continue

    if not candidates:
        return empty_res

    candidates.sort(key=lambda item: (-item[0], item[1].name.lower()))
    newest_mtime, newest_path = candidates[0]
    try:
        parsed = json.loads(newest_path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, ValueError, TypeError):
        return empty_res

    raw_rows = None
    if isinstance(parsed, list):
        raw_rows = parsed
    elif isinstance(parsed, dict):
        for k in ("chi_so", "muc", "bang", "items", "rows"):
            if isinstance(parsed.get(k), list):
                raw_rows = parsed[k]
                break
    if not isinstance(raw_rows, list):
        return empty_res

    chi_so: list[dict] = []
    for row in raw_rows:
        norm = _normalize_muc9_row(row)
        if norm is not None:
            chi_so.append(norm)

    if not chi_so:
        return empty_res

    dt = datetime_from_epoch(newest_mtime)
    return {
        "chua_do": False,
        "tep": newest_path.name,
        "tep_url": f"/tep?p={urllib.parse.quote(str(newest_path), safe='')}" if goc_root is not None else "",
        "cap_nhat_luc": format_iso(dt),
        "cap_nhat_hien_thi": format_display_time(dt),
        "chi_so": chi_so,
    }


def _infer_ticket_from_path(file_path: Path, goc_root: Path | None) -> str:
    """Suy ra tên phiếu từ đường dẫn ảnh ghép dưới `goc_anh`."""
    if goc_root is not None:
        try:
            rel_parts = file_path.relative_to(goc_root.resolve(strict=True)).parts
            for idx, part in enumerate(rel_parts):
                if part.lower() == "bang-chung" and idx >= 1:
                    return rel_parts[idx - 1]
            if len(rel_parts) >= 2:
                return rel_parts[0]
        except (OSError, ValueError):
            pass
    return file_path.parent.name


def _read_anh_ghep(
    raw_pattern: str | None,
    goc_root: Path | None,
    max_items: int = MAX_GHEP_IMAGES,
) -> list[dict]:
    """Đọc lưới ảnh ghép `ghep-*.png` theo mẫu `chat_luong.anh_ghep`."""
    pattern = str(raw_pattern or "").strip()
    if not pattern or goc_root is None:
        return []
    try:
        matches = glob.glob(pattern, recursive=True)
    except OSError:
        return []

    items: list[dict] = []
    seen: set[str] = set()
    for raw_match in matches:
        real_fp, code, _ = resolve_safe_tep_path(raw_match, [goc_root], allowed_exts=IMAGE_TEP_EXTS)
        if code != 200 or real_fp is None:
            continue
        key = os.path.normcase(str(real_fp))
        if key in seen:
            continue
        seen.add(key)
        try:
            mtime = real_fp.stat().st_mtime
        except OSError:
            continue
        dt = datetime_from_epoch(mtime)
        items.append(
            {
                "ten": real_fp.name,
                "phieu": _infer_ticket_from_path(real_fp, goc_root),
                "gio": format_iso(dt),
                "gio_hien_thi": format_display_time(dt),
                "gio_ngan": dt.strftime("%H:%M %d/%m"),
                "url": f"/tep?p={urllib.parse.quote(str(real_fp), safe='')}",
                "_mtime": mtime,
            }
        )

    items.sort(key=lambda x: (-x["_mtime"], x["ten"].lower()))
    trimmed = items[: max(0, int(max_items))]
    for item in trimmed:
        item.pop("_mtime", None)
    return trimmed


def _read_cham_list(raw_cham, goc_root: Path | None) -> list[dict]:
    """Đọc bảng chấm `chat_luong.cham` (chỉ đọc, không tự bịa số)."""
    if not isinstance(raw_cham, list):
        return []
    rows: list[dict] = []
    for item in raw_cham:
        if not isinstance(item, dict):
            continue
        rc = str(item.get("rc") or "").strip()
        nguoi = str(item.get("nguoi") or "").strip()
        diem_raw = item.get("diem")
        diem = "" if diem_raw is None else str(diem_raw).strip()
        ghi_chu = str(item.get("ghi_chu") or "").strip()
        tep = str(item.get("tep") or "").strip()
        tep_url = ""
        if tep and goc_root is not None:
            real_fp, code, _ = resolve_safe_tep_path(tep, [goc_root])
            if code != 200 and not Path(tep).is_absolute():
                real_fp, code, _ = resolve_safe_tep_path(str(goc_root / tep), [goc_root])
            if code == 200 and real_fp is not None:
                tep_url = f"/tep?p={urllib.parse.quote(str(real_fp), safe='')}"
        rows.append(
            {
                "rc": rc or "—",
                "nguoi": nguoi or "—",
                "diem": diem or "—",
                "ghi_chu": ghi_chu,
                "tep": tep,
                "tep_url": tep_url,
            }
        )
    return rows


_STEP_STATUS_LABELS = {
    "cho": "Chờ",
    "dang-chay": "Đang chạy",
    "xong-dat": "Xong đạt",
    "xong-khong-dat": "Xong KHÔNG đạt",
    "cho-claude": "Chờ Claude",
    "cho-linh": "Chờ Linh",
}
_SUA_VARIANT_RE = re.compile(r"^(.+)-sua-(\d+)$")
_GANTT_DELAY_THRESHOLD_MIN = 15.0


def _format_hhmm(dt: datetime | None) -> str:
    """Định dạng ngắn HH:MM theo múi giờ cục bộ."""
    if dt is None:
        return ""
    return dt.astimezone(get_local_tz()).strftime("%H:%M")


def _floor_30m(dt: datetime) -> datetime:
    """Làm tròn xuống mốc 30 phút chẵn theo múi giờ cục bộ."""
    local_dt = dt.astimezone(get_local_tz())
    minute = (local_dt.minute // 30) * 30
    return local_dt.replace(minute=minute, second=0, microsecond=0)


def _ceil_30m(dt: datetime) -> datetime:
    """Làm tròn lên mốc 30 phút chẵn theo múi giờ cục bộ."""
    local_dt = dt.astimezone(get_local_tz())
    if local_dt.minute % 30 == 0 and local_dt.second == 0 and local_dt.microsecond == 0:
        return local_dt
    return _floor_30m(local_dt) + timedelta(minutes=30)


def _build_sua_variants_index(*ticket_maps) -> dict[str, list[tuple[int, str]]]:
    """Lập bảng tra các phiếu tự sửa `<id>-sua-<n>` hiện có trên hàng đợi."""
    buckets: dict[str, dict[str, int]] = {}
    for mapping in ticket_maps:
        for tid in mapping.keys():
            m = _SUA_VARIANT_RE.match(str(tid))
            if not m:
                continue
            base_id = m.group(1)
            num = int(m.group(2))
            buckets.setdefault(base_id, {})[tid] = num
    out: dict[str, list[tuple[int, str]]] = {}
    for base_id, items in buckets.items():
        pairs = [(num, tid) for tid, num in items.items()]
        pairs.sort(key=lambda pair: (pair[0], pair[1]))
        out[base_id] = pairs
    return out


def _compute_project_gantt(
    steps_out: list[dict],
    han_dt: datetime | None,
    current_time: datetime,
) -> tuple[dict, str, str, int | None]:
    """Tính thanh GANTT dự kiến/thực tế, bước trễ > 15p, trục giờ và câu dự kiến xong."""
    # 1. Tìm bước mục tiêu cuối cùng có du_kien.xong để tính câu Dự kiến xong HH:MM (trễ/sớm N phút)
    target_idx: int | None = None
    for idx in range(len(steps_out) - 1, -1, -1):
        if steps_out[idx].get("_dk_end_dt") is not None:
            target_idx = idx
            break

    du_kien_xong_cau = ""
    du_kien_xong_luc = ""
    du_kien_lech_phut: int | None = None

    if target_idx is not None:
        shift_sec = 0.0
        chain_end_dt: datetime | None = None
        has_unfinished_before = False
        for idx in range(target_idx + 1):
            st_obj = steps_out[idx]
            dk_s: datetime | None = st_obj.get("_dk_start_dt")
            dk_e: datetime | None = st_obj.get("_dk_end_dt")
            tt_s: datetime | None = st_obj.get("_tt_start_dt")
            tt_e: datetime | None = st_obj.get("_tt_end_dt")
            tt_buoc = st_obj.get("trang_thai") or "cho"

            dur_sec = max(0.0, (dk_e - dk_s).total_seconds()) if (dk_s is not None and dk_e is not None) else 0.0
            if tt_buoc in ("xong-dat", "xong-khong-dat") and tt_e is not None:
                own_end: datetime | None = tt_e
            elif tt_s is not None:
                has_unfinished_before = True
                own_end = max(current_time, tt_s + timedelta(seconds=dur_sec))
            else:
                has_unfinished_before = True
                if dk_s is not None:
                    est_st = max(current_time, dk_s + timedelta(seconds=shift_sec))
                    own_end = est_st + timedelta(seconds=dur_sec)
                elif dk_e is not None:
                    own_end = max(current_time, dk_e + timedelta(seconds=shift_sec))
                else:
                    own_end = chain_end_dt

            if own_end is not None:
                if idx == target_idx and not has_unfinished_before:
                    chain_end_dt = own_end
                else:
                    chain_end_dt = max(chain_end_dt, own_end) if chain_end_dt is not None else own_end
                if dk_e is not None:
                    shift_sec = (chain_end_dt - dk_e).total_seconds()

        base_dk_end: datetime = steps_out[target_idx]["_dk_end_dt"]
        est_final = chain_end_dt or base_dk_end
        delta_min = int(round((est_final - base_dk_end).total_seconds() / 60.0))
        hhmm_final = _format_hhmm(est_final)
        if delta_min > 0:
            du_kien_xong_cau = f"Dự kiến xong {hhmm_final} (trễ {delta_min} phút)"
        elif delta_min < 0:
            du_kien_xong_cau = f"Dự kiến xong {hhmm_final} (sớm {abs(delta_min)} phút)"
        else:
            du_kien_xong_cau = f"Dự kiến xong {hhmm_final} (sớm 0 phút)"
        du_kien_xong_luc = format_iso(est_final)
        du_kien_lech_phut = delta_min

    # 2. Xác định miền trục giờ GANTT từ các bước (gồm hiện tại & hạn nếu gần miền bước)
    step_points: list[datetime] = []
    for st_obj in steps_out:
        for k in ("_dk_start_dt", "_dk_end_dt", "_tt_start_dt", "_tt_end_dt"):
            pt = st_obj.get(k)
            if pt is not None:
                step_points.append(pt)

    if step_points:
        min_step = min(step_points)
        max_step = max(step_points)
        pts: list[datetime] = [min_step, max_step]
        if abs((current_time - min_step).total_seconds()) <= 6 * 3600 or (
            min_step <= current_time <= max_step + timedelta(hours=6)
        ):
            pts.append(current_time)
        core_span = max(3600.0, (max_step - min_step).total_seconds())
        if han_dt is not None and (
            min_step - timedelta(hours=4)
            <= han_dt
            <= max_step + timedelta(seconds=max(4 * 3600.0, core_span * 0.8))
        ):
            pts.append(han_dt)
        raw_min = min(pts) - timedelta(minutes=15)
        raw_max = max(pts) + timedelta(minutes=15)
    else:
        raw_min = current_time - timedelta(minutes=30)
        raw_max = current_time + timedelta(minutes=150)

    axis_start = _floor_30m(raw_min)
    axis_end = _ceil_30m(raw_max)
    if (axis_end - axis_start).total_seconds() < 1800.0:
        axis_end = axis_start + timedelta(minutes=30)

    total_sec = max(1.0, (axis_end - axis_start).total_seconds())
    total_min = total_sec / 60.0
    if total_min <= 180.0:
        tick_min = 30
    elif total_min <= 420.0:
        tick_min = 60
    elif total_min <= 780.0:
        tick_min = 120
    elif total_min <= 1440.0:
        tick_min = 180
    else:
        tick_min = max(360, ((int(total_min) + 8 * 360 - 1) // (8 * 360)) * 360)

    moc_gio: list[dict] = []
    day0 = axis_start.astimezone(get_local_tz()).replace(hour=0, minute=0, second=0, microsecond=0)
    k_start = int(((axis_start - day0).total_seconds() // (tick_min * 60)))
    tick_dt = day0 + timedelta(minutes=k_start * tick_min)
    while tick_dt <= axis_end:
        if tick_dt >= axis_start:
            tick_pct = round(((tick_dt - axis_start).total_seconds() / total_sec) * 100.0, 2)
            moc_gio.append({"gio": _format_hhmm(tick_dt), "pct": tick_pct})
        tick_dt += timedelta(minutes=tick_min)

    def _pct_of(dt: datetime) -> float:
        return ((dt - axis_start).total_seconds() / total_sec) * 100.0

    now_raw = _pct_of(current_time)
    now_pct = round(min(99.0, max(1.0, now_raw)), 2)
    now_ghim = not (0.0 <= now_raw <= 100.0)

    han_co = han_dt is not None
    han_pct: float | None = None
    han_ghim = False
    han_nhan = ""
    if han_dt is not None:
        han_raw = _pct_of(han_dt)
        han_pct = round(min(99.2, max(0.8, han_raw)), 2)
        han_ghim = not (0.0 <= han_raw <= 100.0)
        han_local = han_dt.astimezone(get_local_tz())
        han_nhan = _format_hhmm(han_local) if han_local.date() == axis_start.date() else han_local.strftime("%d/%m %H:%M")

    # 3. Tính phần trăm vị trí các thanh dự kiến/thực tế cho từng bước và dọn key nội bộ
    for st_obj in steps_out:
        dk_s = st_obj.pop("_dk_start_dt", None)
        dk_e = st_obj.pop("_dk_end_dt", None)
        tt_s = st_obj.pop("_tt_start_dt", None)
        tt_e = st_obj.pop("_tt_end_dt", None)

        co_dk = dk_s is not None and dk_e is not None
        if co_dk:
            dk_l_raw = _pct_of(dk_s)
            dk_r_raw = _pct_of(dk_e)
            dk_l = round(min(98.8, max(0.0, dk_l_raw)), 2)
            dk_r = round(min(100.0, max(dk_l, dk_r_raw)), 2)
            dk_w = round(min(100.0 - dk_l, max(1.2, dk_r - dk_l)), 2)
        else:
            dk_l, dk_w = 0.0, 0.0

        co_tt = tt_s is not None and tt_e is not None
        if co_tt:
            tt_l_raw = _pct_of(tt_s)
            tt_r_raw = _pct_of(tt_e)
            tt_l = round(min(98.8, max(0.0, tt_l_raw)), 2)
            tt_r = round(min(100.0, max(tt_l, tt_r_raw)), 2)
            tt_w = round(min(100.0 - tt_l, max(1.2, tt_r - tt_l)), 2)
        else:
            tt_l_raw, tt_r_raw = 0.0, 0.0
            tt_l, tt_w = 0.0, 0.0

        st_obj["gantt"] = {
            "co_du_kien": co_dk,
            "dk_left_pct": dk_l,
            "dk_width_pct": dk_w,
            "co_thuc_te": co_tt,
            "tt_left_pct": tt_l,
            "tt_width_pct": tt_w,
            "tt_start_pct_raw": round(tt_l_raw, 3),
            "tt_end_pct_raw": round(tt_r_raw, 3),
        }

    gantt_truc = {
        "bat_dau": format_iso(axis_start),
        "xong": format_iso(axis_end),
        "bat_dau_gio": _format_hhmm(axis_start),
        "xong_gio": _format_hhmm(axis_end),
        "moc_gio": moc_gio,
        "hien_tai_gio": _format_hhmm(current_time),
        "hien_tai_pct": now_pct,
        "hien_tai_ghim": now_ghim,
        "han_co": han_co,
        "han_pct": han_pct,
        "han_ghim": han_ghim,
        "han_nhan": han_nhan,
    }
    return gantt_truc, du_kien_xong_cau, du_kien_xong_luc, du_kien_lech_phut


def read_projects_snapshot(
    clone_dir: Path,
    current_time: datetime,
    running_items: list[dict],
    waiting_items: list[dict],
    done_info_map: dict[str, dict],
    can_linh_items: list[dict],
) -> list[dict]:
    """Đọc toàn bộ `hang-doi/du-an/*.json` và tổng hợp 6 trạng thái bước + GANTT + dữ liệu Chất lượng."""
    qroot = resolve_queue_root(Path(clone_dir))
    dir_proj = qroot / "du-an"
    if not dir_proj.is_dir():
        return []

    running_map = {item["phieu"]: item for item in running_items if item.get("phieu")}
    waiting_map = {item["phieu"]: item for item in waiting_items if item.get("phieu")}
    can_linh_by_ticket: dict[str, list[dict]] = {}
    for cl in can_linh_items:
        tid = cl.get("phieu") or cl.get("id") or ""
        if tid:
            can_linh_by_ticket.setdefault(tid, []).append(cl)
    sua_variants = _build_sua_variants_index(running_map, waiting_map, done_info_map, can_linh_by_ticket)

    projects_out: list[dict] = []
    for proj_file in sorted(dir_proj.glob("*.json"), key=lambda p: p.name):
        try:
            proj = json.loads(proj_file.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError, TypeError):
            continue
        if not isinstance(proj, dict):
            continue

        ma_da = str(proj.get("ma") or proj_file.stem).strip()
        ten_da = str(proj.get("ten") or ma_da).strip()
        han_raw = str(proj.get("han") or "").strip()
        han_dt = parse_iso_datetime(han_raw) if han_raw else None
        if han_dt is None:
            han_con_lai = "Chưa đặt hạn"
            han_hien_thi = "—"
            qua_han = False
        else:
            diff_sec = (han_dt - current_time).total_seconds()
            han_hien_thi = format_display_time(han_dt)
            if diff_sec >= 0:
                han_con_lai = f"Còn {format_duration_vi(diff_sec)} tới hạn"
                qua_han = False
            else:
                han_con_lai = f"Quá hạn {format_duration_vi(-diff_sec)}"
                qua_han = True

        goc_anh_raw = str(proj.get("goc_anh") or "").strip()
        goc_root = _valid_goc_anh_root(goc_anh_raw)

        steps_out: list[dict] = []
        raw_steps = proj.get("buoc") if isinstance(proj.get("buoc"), list) else []
        for raw_step in raw_steps:
            if not isinstance(raw_step, dict):
                continue
            ma_b = str(raw_step.get("ma") or "").strip()
            ten_b = str(raw_step.get("ten") or ma_b).strip()
            phieu_ids = [str(x).strip() for x in (raw_step.get("phieu") or []) if str(x).strip()]
            cong_id = str(raw_step.get("cong") or "").strip()
            nguoi = str(raw_step.get("nguoi") or "").strip()

            expanded_phieu_ids: list[str] = []
            seen_ids: set[str] = set()
            latest_by_pid: dict[str, str] = {}
            for pid in phieu_ids:
                chain = [pid]
                for _num, var_tid in sua_variants.get(pid) or ():
                    if var_tid not in chain:
                        chain.append(var_tid)
                latest_by_pid[pid] = chain[-1]
                for cid in chain:
                    if cid not in seen_ids:
                        seen_ids.add(cid)
                        expanded_phieu_ids.append(cid)

            all_ids = list(expanded_phieu_ids)
            if cong_id and cong_id not in seen_ids:
                all_ids.append(cong_id)

            running_in_step = [running_map[tid] for tid in all_ids if tid in running_map]
            can_linh_in_step: list[dict] = []
            for tid in all_ids:
                can_linh_in_step.extend(can_linh_by_ticket.get(tid) or [])

            chay_phut = 0.0
            tran_phut: int | float = 40
            nhip_cuoi = ""
            phieu_dang_chay = ""

            def _is_pid_done(pid: str) -> bool:
                eff_id = latest_by_pid.get(pid, pid)
                return eff_id in done_info_map

            def _is_pid_dat(pid: str) -> bool:
                eff_id = latest_by_pid.get(pid, pid)
                return bool(done_info_map[eff_id]["dat"])

            if running_in_step:
                tt_buoc = "dang-chay"
                r0 = running_in_step[0]
                phieu_dang_chay = r0["phieu"]
                chay_phut = float(r0.get("chay_phut") or 0.0)
                tran_phut = r0.get("tran_phut") or 40
                nhip_cuoi = str(r0.get("nhip") or "")
            elif can_linh_in_step:
                tt_buoc = "cho-linh"
            elif nguoi:
                if all_ids and all(_is_pid_done(pid) for pid in phieu_ids) and (
                    not cong_id or cong_id in done_info_map
                ):
                    ok_all = all(_is_pid_dat(pid) for pid in phieu_ids) and (
                        not cong_id or bool(done_info_map[cong_id]["dat"])
                    )
                    tt_buoc = "xong-dat" if ok_all else "xong-khong-dat"
                else:
                    tt_buoc = "cho-linh"
            elif not phieu_ids:
                if cong_id:
                    if cong_id in done_info_map:
                        tt_buoc = "xong-dat" if done_info_map[cong_id]["dat"] else "xong-khong-dat"
                    else:
                        tt_buoc = "cho-claude"
                else:
                    tt_buoc = "cho"
            else:
                if any(not _is_pid_done(pid) for pid in phieu_ids):
                    tt_buoc = "cho"
                elif cong_id:
                    if cong_id not in done_info_map:
                        tt_buoc = "cho-claude"
                    else:
                        cd = done_info_map[cong_id]
                        if cd.get("_co_dong_dat"):
                            is_ok = bool(cd["dat"])
                        else:
                            is_ok = bool(cd["dat"]) and all(_is_pid_dat(pid) for pid in phieu_ids)
                        tt_buoc = "xong-dat" if is_ok else "xong-khong-dat"
                else:
                    is_ok = all(_is_pid_dat(pid) for pid in phieu_ids)
                    tt_buoc = "xong-dat" if is_ok else "xong-khong-dat"

            tt_nhan = (
                (f"Chờ {nguoi}" if nguoi else "Chờ Linh")
                if tt_buoc == "cho-linh"
                else _STEP_STATUS_LABELS.get(tt_buoc, tt_buoc)
            )

            # Tính mốc Dự kiến, Thực tế và độ trễ (> 15 phút tô cam) cho bước
            dk_raw = raw_step.get("du_kien") if isinstance(raw_step.get("du_kien"), dict) else {}
            dk_start_dt = parse_iso_datetime(dk_raw.get("bat_dau"))
            dk_end_dt = parse_iso_datetime(dk_raw.get("xong"))
            if dk_start_dt is not None and dk_end_dt is not None and dk_end_dt < dk_start_dt:
                dk_end_dt = dk_start_dt
            if dk_start_dt is not None and dk_end_dt is not None:
                du_kien_gio = f"{_format_hhmm(dk_start_dt)}–{_format_hhmm(dk_end_dt)}"
            elif dk_start_dt is not None:
                du_kien_gio = f"{_format_hhmm(dk_start_dt)}–?"
            elif dk_end_dt is not None:
                du_kien_gio = f"?–{_format_hhmm(dk_end_dt)}"
            else:
                du_kien_gio = "—"

            start_dts: list[datetime] = []
            end_dts: list[datetime] = []
            for tid in all_ids:
                if tid in running_map:
                    r_dt = parse_iso_datetime(running_map[tid].get("nhan_luc"))
                    if r_dt is not None:
                        start_dts.append(r_dt)
                if tid in done_info_map:
                    d_end = parse_iso_datetime(done_info_map[tid].get("xong_luc"))
                    d_start = parse_iso_datetime(done_info_map[tid].get("nhan_luc"))
                    if d_start is not None:
                        start_dts.append(d_start)
                    elif d_end is not None:
                        start_dts.append(d_end)
                    if d_end is not None:
                        end_dts.append(d_end)

            if not start_dts:
                tt_start_dt: datetime | None = None
                tt_end_dt: datetime | None = None
                thuc_te_dang_chay = False
                thuc_te_gio = "—"
            else:
                tt_start_dt = min(start_dts)
                if tt_buoc == "dang-chay":
                    tt_end_dt = max(tt_start_dt, current_time)
                    thuc_te_dang_chay = True
                    thuc_te_gio = f"{_format_hhmm(tt_start_dt)}–…"
                else:
                    tt_end_dt = max(end_dts) if end_dts else tt_start_dt
                    tt_end_dt = max(tt_start_dt, tt_end_dt)
                    thuc_te_dang_chay = False
                    if tt_buoc in ("xong-dat", "xong-khong-dat"):
                        thuc_te_gio = f"{_format_hhmm(tt_start_dt)}–{_format_hhmm(tt_end_dt)}"
                    else:
                        thuc_te_gio = f"{_format_hhmm(tt_start_dt)}–…"

            if tt_buoc in ("xong-dat", "xong-khong-dat"):
                if tt_end_dt is not None and dk_end_dt is not None:
                    delay_min = (tt_end_dt - dk_end_dt).total_seconds() / 60.0
                elif tt_start_dt is not None and dk_start_dt is not None:
                    delay_min = (tt_start_dt - dk_start_dt).total_seconds() / 60.0
                else:
                    delay_min = 0.0
            else:
                cands: list[float] = []
                if dk_end_dt is not None:
                    cands.append((current_time - dk_end_dt).total_seconds() / 60.0)
                if dk_start_dt is not None:
                    ref_st = tt_start_dt if tt_start_dt is not None else current_time
                    cands.append((ref_st - dk_start_dt).total_seconds() / 60.0)
                delay_min = max(cands) if cands else 0.0

            if delay_min > _GANTT_DELAY_THRESHOLD_MIN:
                bi_tre = True
                rounded_delay = int(round(delay_min))
                tre_phut = max(16, rounded_delay) if rounded_delay <= 15 else rounded_delay
                tre_nhan = f"trễ {tre_phut} phút"
            else:
                bi_tre = False
                tre_phut = max(0, int(round(delay_min)))
                tre_nhan = ""

            phieu_chi_tiet: list[dict] = []
            ket_qua_list: list[dict] = []
            step_images_pool: list[dict] = []
            for tid in all_ids:
                t_imgs = scan_ticket_images(goc_root, tid, max_images=MAX_TICKET_IMAGES)
                step_images_pool.extend(t_imgs)
                t_imgs_clean = [{k: v for k, v in im.items() if k != "_mtime"} for im in t_imgs]
                la_cong = bool(cong_id and tid == cong_id and tid not in expanded_phieu_ids)
                if tid in running_map:
                    ri = running_map[tid]
                    phieu_chi_tiet.append(
                        {
                            "phieu": tid,
                            "la_cong": la_cong,
                            "giai_doan": "dang",
                            "trang_thai": "dang",
                            "dat": None,
                            "may": ri.get("may") or "—",
                            "phut": ri.get("chay_phut") or 0.0,
                            "tran_phut": ri.get("tran_phut") or 40,
                            "nhip": ri.get("nhip") or "",
                            "ket_qua_url": ri.get("ket_qua_url") or f"/phieu/{urllib.parse.quote(tid)}",
                            "anh": t_imgs_clean,
                        }
                    )
                elif tid in done_info_map:
                    di = done_info_map[tid]
                    phieu_chi_tiet.append(
                        {
                            "phieu": tid,
                            "la_cong": la_cong,
                            "giai_doan": "xong",
                            "trang_thai": di.get("trang_thai") or "xong",
                            "dat": bool(di.get("dat")),
                            "may": di.get("may") or "—",
                            "phut": di.get("phut") or 0.0,
                            "xong_luc_hien_thi": di.get("xong_luc_hien_thi") or "—",
                            "ket_qua_url": di.get("ket_qua_url") or f"/phieu/{urllib.parse.quote(tid)}",
                            "anh": t_imgs_clean,
                        }
                    )
                    ket_qua_list.append(
                        {
                            "phieu": tid,
                            "trang_thai": di.get("trang_thai") or "xong",
                            "dat": bool(di.get("dat")),
                            "noi_dung": di.get("ket_qua") or "",
                            "ket_qua_url": di.get("ket_qua_url") or f"/phieu/{urllib.parse.quote(tid)}",
                        }
                    )
                elif tid in waiting_map:
                    wi = waiting_map[tid]
                    phieu_chi_tiet.append(
                        {
                            "phieu": tid,
                            "la_cong": la_cong,
                            "giai_doan": "moi",
                            "trang_thai": "moi",
                            "dat": None,
                            "may": wi.get("may") or "bat-ky",
                            "phut": 0.0,
                            "tran_phut": wi.get("tran_phut") or 40,
                            "ket_qua_url": wi.get("ket_qua_url") or f"/phieu/{urllib.parse.quote(tid)}",
                            "anh": t_imgs_clean,
                        }
                    )
                else:
                    phieu_chi_tiet.append(
                        {
                            "phieu": tid,
                            "la_cong": la_cong,
                            "giai_doan": "chua-co",
                            "trang_thai": "cho-claude" if la_cong else "cho",
                            "dat": None,
                            "may": "claude" if la_cong else "—",
                            "phut": 0.0,
                            "ket_qua_url": f"/phieu/{urllib.parse.quote(tid)}",
                            "anh": t_imgs_clean,
                        }
                    )

            step_images_pool.sort(key=lambda im: (0 if im["la_ghep"] else 1, -im["_mtime"], im["ten"].lower()))
            anh_thu_nho: list[dict] = []
            seen_img_urls: set[str] = set()
            for im in step_images_pool:
                if im["url"] in seen_img_urls:
                    continue
                seen_img_urls.add(im["url"])
                anh_thu_nho.append({k: v for k, v in im.items() if k != "_mtime"})
                if len(anh_thu_nho) >= MAX_TICKET_IMAGES:
                    break

            log_cuoi = collect_step_tail_logs(goc_root, qroot, all_ids, running_map, max_lines=MAX_STEP_LOG_LINES)

            steps_out.append(
                {
                    "ma": ma_b,
                    "ten": ten_b,
                    "trang_thai": tt_buoc,
                    "trang_thai_nhan": tt_nhan,
                    "phieu": phieu_ids,
                    "cong": cong_id,
                    "nguoi": nguoi,
                    "du_kien": dk_raw,
                    "du_kien_bat_dau": format_iso(dk_start_dt),
                    "du_kien_xong": format_iso(dk_end_dt),
                    "du_kien_gio": du_kien_gio,
                    "thuc_te_bat_dau": format_iso(tt_start_dt),
                    "thuc_te_xong": format_iso(tt_end_dt),
                    "thuc_te_dang_chay": thuc_te_dang_chay,
                    "thuc_te_gio": thuc_te_gio,
                    "bi_tre": bi_tre,
                    "tre_phut": tre_phut,
                    "tre_nhan": tre_nhan,
                    "_dk_start_dt": dk_start_dt,
                    "_dk_end_dt": dk_end_dt,
                    "_tt_start_dt": tt_start_dt,
                    "_tt_end_dt": tt_end_dt,
                    "phieu_dang_chay": phieu_dang_chay,
                    "chay_phut": chay_phut,
                    "tran_phut": tran_phut,
                    "nhip_cuoi": nhip_cuoi,
                    "phieu_chi_tiet": phieu_chi_tiet,
                    "log_cuoi": log_cuoi,
                    "ket_qua_list": ket_qua_list,
                    "anh_thu_nho": anh_thu_nho,
                }
            )

        gantt_truc, du_kien_xong_cau, du_kien_xong_luc, du_kien_lech_phut = _compute_project_gantt(
            steps_out=steps_out,
            han_dt=han_dt,
            current_time=current_time,
        )

        # Tìm bước hiện tại và câu tóm tắt "đang ở bước X, việc tiếp theo Y"
        cur_idx: int | None = None
        for target_st in ("dang-chay", "cho-claude", "xong-khong-dat", "cho-linh", "cho"):
            for idx, st_obj in enumerate(steps_out):
                if st_obj["trang_thai"] == target_st:
                    cur_idx = idx
                    break
            if cur_idx is not None:
                break

        if not steps_out:
            tom_tat_buoc = "Chưa có bước nào"
        elif cur_idx is None:
            tom_tat_buoc = "Đã hoàn tất tất cả các bước, việc tiếp theo: bàn giao"
        else:
            cur_step = steps_out[cur_idx]
            x_txt = f"{cur_step['ma']} ({cur_step['ten']})" if cur_step["ma"] and cur_step["ma"] != cur_step["ten"] else cur_step["ten"]
            if cur_step["trang_thai"] == "cho-claude" and cur_step["cong"]:
                y_txt = f"Claude duyệt {cur_step['cong']}"
            elif cur_idx + 1 < len(steps_out):
                nxt_step = steps_out[cur_idx + 1]
                y_txt = f"{nxt_step['ma']} ({nxt_step['ten']})" if nxt_step["ma"] and nxt_step["ma"] != nxt_step["ten"] else nxt_step["ten"]
            else:
                y_txt = "hoàn tất dự án"
            tom_tat_buoc = f"Đang ở bước {x_txt}, việc tiếp theo {y_txt}"

        cl_cfg = proj.get("chat_luong") if isinstance(proj.get("chat_luong"), dict) else {}
        chat_luong_obj = {
            "do_muc_9": _read_do_muc_9(cl_cfg.get("do_muc_9"), goc_root),
            "anh_ghep": _read_anh_ghep(cl_cfg.get("anh_ghep"), goc_root, max_items=MAX_GHEP_IMAGES),
            "cham": _read_cham_list(cl_cfg.get("cham"), goc_root),
        }

        projects_out.append(
            {
                "ma": ma_da,
                "ten": ten_da,
                "han": han_raw,
                "han_hien_thi": han_hien_thi,
                "han_con_lai": han_con_lai,
                "qua_han": qua_han,
                "goc_anh": goc_anh_raw,
                "tom_tat_buoc": tom_tat_buoc,
                "du_kien_xong_cau": du_kien_xong_cau,
                "du_kien_xong_luc": du_kien_xong_luc,
                "du_kien_lech_phut": du_kien_lech_phut,
                "gantt_truc": gantt_truc,
                "buoc": steps_out,
                "chat_luong": chat_luong_obj,
            }
        )

    return projects_out


def read_ticket_detail(
    clone_dir: Path,
    ticket_id: str,
    now: datetime | None = None,
    commit_times: dict[str, int] | None = None,
) -> dict | None:
    """Đọc nội dung chi tiết KET-QUA.md (hoặc phiếu đang chạy/chờ nếu chưa xong)."""
    if not is_safe_ticket_id(ticket_id):
        return None
    qroot = resolve_queue_root(Path(clone_dir))

    kq_path = qroot / "xong" / ticket_id / "KET-QUA.md"
    if kq_path.is_file():
        raw_text = kq_path.read_text(encoding="utf-8", errors="replace")
        meta, body = parse_markdown_headers(raw_text)
        tok_in, tok_out, tok_total = parse_tokens(meta.get("token", ""))
        return {
            "phieu": ticket_id,
            "nguon_tep": "hang-doi/xong/" + ticket_id + "/KET-QUA.md",
            "giai_doan": "xong",
            "may": (meta.get("may") or "chua-ro").strip(),
            "trang_thai": (meta.get("trang_thai") or "xong").strip().lower(),
            "phut": meta.get("phut", "0"),
            "token": meta.get("token", "vao=0 ra=0"),
            "token_vao": tok_in,
            "token_ra": tok_out,
            "tong_token": tok_total,
            "tep_doi": meta.get("tep_doi", "(khong)"),
            "drive": meta.get("drive", "(khong)"),
            "than": body,
            "noi_dung": raw_text,
        }

    running_path = qroot / "dang" / f"{ticket_id}.md"
    if running_path.is_file():
        raw_text = running_path.read_text(encoding="utf-8", errors="replace")
        meta, raw_body = parse_markdown_headers(raw_text)
        nhip_line, body = _extract_nhip_and_clean_body(raw_body, meta)
        machine, claimed_dt = _parse_claimed_info(meta, (meta.get("may") or "bat-ky").strip().lower())
        git_times = load_git_file_commit_times(Path(clone_dir)) if commit_times is None else commit_times
        file_dt = _file_timestamp(running_path, Path(clone_dir), git_times)
        if claimed_dt is None:
            claimed_dt = file_dt
        last_active_dt = file_dt if (nhip_line and file_dt and claimed_dt and file_dt > claimed_dt) else claimed_dt
        current_time = (now or now_local()).astimezone(get_local_tz())
        is_canh_nen, log_cuoi_phut, nhan_canh_nen, _ = _parse_canh_nen_status(
            meta=meta,
            nhip_line=nhip_line,
            current_time=current_time,
            fallback_dt=last_active_dt,
            file_dt=file_dt,
        )
        return {
            "phieu": ticket_id,
            "nguon_tep": f"hang-doi/dang/{ticket_id}.md",
            "giai_doan": "dang",
            "may": machine,
            "trang_thai": "dang",
            "canh_nen": is_canh_nen,
            "log_cuoi_phut": log_cuoi_phut,
            "nhan_canh_nen": nhan_canh_nen,
            "phut": "—",
            "token": "—",
            "token_vao": 0,
            "token_ra": 0,
            "tong_token": 0,
            "tep_doi": "(đang chạy)",
            "drive": "(chưa có)",
            "than": body,
            "noi_dung": raw_text,
        }

    waiting_path = qroot / "moi" / f"{ticket_id}.md"
    if waiting_path.is_file():
        raw_text = waiting_path.read_text(encoding="utf-8", errors="replace")
        meta, body = parse_markdown_headers(raw_text)
        return {
            "phieu": ticket_id,
            "nguon_tep": f"hang-doi/moi/{ticket_id}.md",
            "giai_doan": "moi",
            "may": (meta.get("may") or "bat-ky").strip(),
            "trang_thai": "moi",
            "phut": "—",
            "token": "—",
            "token_vao": 0,
            "token_ra": 0,
            "tong_token": 0,
            "tep_doi": "(đang chờ)",
            "drive": "(chưa có)",
            "than": body,
            "noi_dung": raw_text,
        }

    return None


class QueueMonitor:
    """Bộ quản lý clone riêng `bang-hang-doi` (chỉ đọc) và chu kỳ `git fetch` 30 giây."""

    def __init__(
        self,
        clone_dir: Path | str = DEFAULT_CLONE_DIR,
        repo_url: str | None = DEFAULT_REPO_URL,
        branch: str = DEFAULT_BRANCH,
        remote: str = DEFAULT_REMOTE,
        fetch_interval: float = DEFAULT_FETCH_INTERVAL,
        enable_git_sync: bool = True,
        clock_fn=None,
    ):
        self.clone_dir = Path(clone_dir)
        self.repo_url = str(repo_url).strip() if repo_url else ""
        self.branch = (branch or DEFAULT_BRANCH).strip()
        self.remote = (remote or DEFAULT_REMOTE).strip()
        self.fetch_interval = max(0.05, float(fetch_interval))
        self.enable_git_sync = bool(enable_git_sync and self.repo_url)
        self._clock_fn = clock_fn or now_local

        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        self._sync_thread: threading.Thread | None = None

        self._last_sync_dt: datetime | None = None
        self._last_sync_error: str = ""
        self._cached_head_sha: str | None = None
        self._cached_commit_times: dict[str, int] = {}

    def _now(self) -> datetime:
        return self._clock_fn().astimezone(get_local_tz())

    def sync_once(self) -> bool:
        """Thực hiện 1 lượt `git fetch` nhánh `hang-doi` vào `clone_dir` (chỉ đọc)."""
        if not self.enable_git_sync:
            return True
        with self._lock:
            try:
                self.clone_dir.mkdir(parents=True, exist_ok=True)
                git_dir = self.clone_dir / ".git"
                if not git_dir.exists():
                    run_git_readonly(["init"], cwd=self.clone_dir)
                    run_git_readonly(["remote", "add", self.remote, self.repo_url], cwd=self.clone_dir)
                else:
                    cur_remote = run_git_readonly(
                        ["remote", "get-url", self.remote],
                        cwd=self.clone_dir,
                        check=False,
                    )
                    if cur_remote.returncode != 0:
                        run_git_readonly(["remote", "add", self.remote, self.repo_url], cwd=self.clone_dir)
                    elif cur_remote.stdout.strip() != self.repo_url:
                        run_git_readonly(["remote", "set-url", self.remote, self.repo_url], cwd=self.clone_dir)

                remote_ref = f"refs/remotes/{self.remote}/{self.branch}"
                fetch_proc = run_git_readonly(
                    ["fetch", self.remote, f"+refs/heads/{self.branch}:{remote_ref}"],
                    cwd=self.clone_dir,
                    check=False,
                )
                if fetch_proc.returncode != 0:
                    err_txt = (fetch_proc.stderr or fetch_proc.stdout or "").strip()
                    lower_err = err_txt.lower()
                    if "couldn't find remote ref" in lower_err or "remote ref does not exist" in lower_err:
                        self._last_sync_dt = self._now()
                        self._last_sync_error = ""
                        return True
                    raise RuntimeError(err_txt or f"git fetch mã lỗi {fetch_proc.returncode}")

                remote_sha = run_git_readonly(["rev-parse", remote_ref], cwd=self.clone_dir).stdout.strip()
                head_proc = run_git_readonly(["rev-parse", "--verify", "HEAD"], cwd=self.clone_dir, check=False)
                head_sha = head_proc.stdout.strip() if head_proc.returncode == 0 else ""

                if head_sha != remote_sha:
                    run_git_readonly(["checkout", "-f", "-B", self.branch, remote_ref], cwd=self.clone_dir)
                    run_git_readonly(["clean", "-fd"], cwd=self.clone_dir)

                if self._cached_head_sha != remote_sha:
                    self._cached_commit_times = load_git_file_commit_times(self.clone_dir)
                    self._cached_head_sha = remote_sha

                self._last_sync_dt = self._now()
                self._last_sync_error = ""
                return True
            except Exception as exc:
                self._last_sync_error = str(exc)
                return False

    def _refresh_commit_cache_if_needed(self) -> dict[str, int]:
        """Nạp lại bảng thời gian commit khi HEAD đổi (hoặc khi dùng repo có sẵn)."""
        if not (self.clone_dir / ".git").exists():
            return {}
        head_proc = run_git_readonly(["rev-parse", "--verify", "HEAD"], cwd=self.clone_dir, check=False)
        if head_proc.returncode != 0:
            return {}
        sha = head_proc.stdout.strip()
        if sha != self._cached_head_sha:
            self._cached_commit_times = load_git_file_commit_times(self.clone_dir)
            self._cached_head_sha = sha
        return self._cached_commit_times

    def get_status(self) -> dict:
        """Trả về dữ liệu tổng hợp cho cả trang HTML và `/api/trang-thai`."""
        with self._lock:
            commit_times = self._refresh_commit_cache_if_needed()
            data = read_queue_snapshot(
                self.clone_dir,
                now=self._now(),
                commit_times=commit_times,
            )
            data["thu_muc_clone"] = str(self.clone_dir)
            data["nhanh"] = self.branch
            data["chu_ky_giay"] = int(self.fetch_interval) if self.fetch_interval.is_integer() else self.fetch_interval
            data["dong_bo_luc"] = format_iso(self._last_sync_dt)
            data["dong_bo_hien_thi"] = format_display_time(self._last_sync_dt)
            data["loi_dong_bo"] = self._last_sync_error
            return data

    def get_ticket(self, ticket_id: str) -> dict | None:
        """Đọc chi tiết 1 phiếu dưới khóa đồng bộ."""
        with self._lock:
            commit_times = self._refresh_commit_cache_if_needed()
            return read_ticket_detail(self.clone_dir, ticket_id, now=self._now(), commit_times=commit_times)

    def resolve_tep(self, raw_p: str | None) -> tuple[Path | None, int, str]:
        """Kiểm tra đường dẫn tệp an toàn nằm dưới `goc_anh` của các dự án đang theo dõi."""
        with self._lock:
            roots = _collect_project_roots(self.clone_dir)
            return resolve_safe_tep_path(raw_p, roots)

    def start_background_sync(self) -> None:
        """Đồng bộ ngay lập tức 1 lần và khởi chạy luồng `git fetch` định kỳ."""
        if not self.enable_git_sync:
            return
        self.sync_once()
        if self._sync_thread is not None and self._sync_thread.is_alive():
            return
        self._stop_event.clear()

        def _loop() -> None:
            while not self._stop_event.wait(self.fetch_interval):
                self.sync_once()

        self._sync_thread = threading.Thread(target=_loop, name="linhx-bang-fetch", daemon=True)
        self._sync_thread.start()

    def stop_background_sync(self) -> None:
        """Dừng luồng `git fetch` nền an toàn."""
        self._stop_event.set()
        if self._sync_thread is not None:
            self._sync_thread.join(timeout=3.0)
            self._sync_thread = None


_COMMON_CSS = """
:root {
  color-scheme: light dark;
  --bg: #f5f5f7;
  --card: #ffffff;
  --subtle: #f2f2f7;
  --subtle-hover: #e6e6eb;
  --text: #1d1d1f;
  --muted: #58585e;
  --border: rgba(0, 0, 0, 0.08);
  --divider: rgba(0, 0, 0, 0.06);
  --accent: #0066cc;
  --accent-soft: rgba(0, 102, 204, 0.10);
  --shadow-card: 0 2px 12px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02);
  --shadow-seg: 0 1px 4px rgba(0, 0, 0, 0.08);
  --radius: 16px;
  --radius-sm: 10px;
  --dot-run: #34c759;
  --run-bg: rgba(52, 199, 89, 0.14);
  --run-fg: #156f29;
  --dot-idle: #8e8e93;
  --idle-bg: rgba(142, 142, 147, 0.15);
  --idle-fg: #48484d;
  --dot-stuck: #ff9500;
  --warn-bg: rgba(255, 149, 0, 0.15);
  --warn-fg: #8a4b00;
  --dot-silent: #ff3b30;
  --err-bg: rgba(255, 59, 48, 0.12);
  --err-fg: #bf1b13;
  --ok-bg: rgba(52, 199, 89, 0.14);
  --ok-fg: #156f29;
  --dot-claude: #5856d6;
  --claude-bg: rgba(88, 86, 214, 0.13);
  --claude-fg: #3b39a8;
  --urgent-surface: #fff5f5;
  --urgent-border: rgba(255, 59, 48, 0.30);
  --code-bg: #f2f2f7;
  --code-fg: #1d1d1f;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #000000;
    --card: #1c1c1e;
    --subtle: #2c2c2e;
    --subtle-hover: #3a3a3c;
    --text: #f5f5f7;
    --muted: #a1a1a6;
    --border: rgba(255, 255, 255, 0.11);
    --divider: rgba(255, 255, 255, 0.08);
    --accent: #2997ff;
    --accent-soft: rgba(41, 151, 255, 0.18);
    --shadow-card: 0 4px 20px rgba(0, 0, 0, 0.42);
    --shadow-seg: 0 2px 6px rgba(0, 0, 0, 0.48);
    --dot-run: #30d158;
    --run-bg: rgba(48, 209, 88, 0.18);
    --run-fg: #63e682;
    --dot-idle: #8e8e93;
    --idle-bg: rgba(142, 142, 147, 0.22);
    --idle-fg: #d1d1d6;
    --dot-stuck: #ff9f0a;
    --warn-bg: rgba(255, 159, 10, 0.20);
    --warn-fg: #ffc061;
    --dot-silent: #ff453a;
    --err-bg: rgba(255, 69, 58, 0.20);
    --err-fg: #ff857d;
    --ok-bg: rgba(48, 209, 88, 0.18);
    --ok-fg: #63e682;
    --dot-claude: #7d7aff;
    --claude-bg: rgba(125, 122, 255, 0.22);
    --claude-fg: #b2b0ff;
    --urgent-surface: rgba(255, 69, 58, 0.14);
    --urgent-border: rgba(255, 69, 58, 0.40);
    --code-bg: #141416;
    --code-fg: #f5f5f7;
  }
}
*, *::before, *::after { box-sizing: border-box; }
html, body {
  margin: 0;
  padding: 0;
  max-width: 100%;
  overflow-x: hidden;
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, system-ui, sans-serif;
  font-size: 16px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}
a {
  color: var(--accent);
  text-decoration: none;
  font-weight: 500;
  overflow-wrap: anywhere;
}
a:hover { text-decoration: underline; }
code, pre {
  font-family: ui-monospace, "SF Mono", SFMono-Regular, Consolas, monospace;
  font-size: 15px;
}
.wrap {
  width: 100%;
  max-width: 1020px;
  margin: 0 auto;
  padding: 20px 16px 48px;
}
@media (min-width: 768px) {
  .wrap { padding: 36px 28px 64px; }
}

/* Đầu trang & Câu trạng thái lớn */
.hero-header {
  margin-bottom: 22px;
}
.eyebrow-row {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 8px 12px;
  margin-bottom: 10px;
}
.brand-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.01em;
  color: var(--muted);
}
.live-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--dot-run);
  flex-shrink: 0;
}
.live-indicator.is-stale { background: var(--dot-stuck); }
.sync-meta {
  font-size: 15px;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
}
.hero-headline {
  margin: 0 0 6px 0;
  font-size: 28px;
  line-height: 1.18;
  font-weight: 700;
  letter-spacing: -0.025em;
  color: var(--text);
}
@media (min-width: 768px) {
  .hero-headline { font-size: 36px; }
}
.hero-headline .need-you {
  color: var(--dot-silent);
}
.hero-subline {
  margin: 0;
  font-size: 15px;
  color: var(--muted);
}

/* Thông báo lỗi đồng bộ */
.err-banner {
  background: var(--err-bg);
  color: var(--err-fg);
  border: 1px solid var(--urgent-border);
  padding: 12px 16px;
  border-radius: var(--radius);
  margin-bottom: 18px;
  font-size: 15px;
  overflow-wrap: anywhere;
}

/* Khối đỏ Cần anh làm */
section.can-linh-box {
  background: var(--urgent-surface);
  border: 1px solid var(--urgent-border);
  border-radius: var(--radius);
  padding: 16px 18px;
  margin-bottom: 20px;
  box-shadow: var(--shadow-card);
}
.can-linh-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
section.can-linh-box h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: var(--err-fg);
}
.can-linh-item {
  padding: 2px 0;
}
.can-linh-item + .can-linh-item {
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid var(--urgent-border);
}
.can-linh-meta {
  min-width: 0;
  font-size: 15px;
  margin-bottom: 4px;
}
.can-linh-viec {
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 10px;
  overflow-wrap: anywhere;
}
.cmd-row {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: flex-start;
}
@media (min-width: 768px) {
  .cmd-row {
    flex-direction: row;
    align-items: center;
  }
}
.cmd-paste {
  display: block;
  flex: 1 1 auto;
  width: 100%;
  min-width: 0;
  margin: 0;
  padding: 10px 12px;
  background: var(--code-bg);
  color: var(--code-fg);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 15px;
  line-height: 1.45;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  word-break: break-word;
  user-select: all;
}
.btn-copy {
  appearance: none;
  border: 1px solid var(--urgent-border);
  background: var(--card);
  color: var(--err-fg);
  font-family: inherit;
  font-size: 15px;
  font-weight: 600;
  min-height: 44px;
  padding: 8px 18px;
  border-radius: 999px;
  cursor: pointer;
  transition: background 0.16s ease, color 0.16s ease, transform 0.1s ease;
  flex-shrink: 0;
}
@media (hover: hover) {
  .btn-copy:hover {
    background: var(--err-bg);
  }
}
.btn-copy:active {
  transform: scale(0.98);
}
.btn-copy.is-copied {
  border-color: var(--dot-run);
  color: var(--run-fg);
  background: var(--run-bg);
}

/* Thanh chuyển 5 Tab (Segmented Control chuẩn Apple, tự xếp 2 hàng gọn trên 390px) */
.seg-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 4px;
  background: var(--subtle);
  border-radius: 14px;
  margin-bottom: 22px;
}
.seg-btn {
  appearance: none;
  border: none;
  background: transparent;
  color: var(--muted);
  font-family: inherit;
  font-size: 14px;
  font-weight: 600;
  flex: 1 1 calc(33.333% - 4px);
  min-width: 0;
  min-height: 40px;
  padding: 6px 6px;
  border-radius: 10px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  white-space: nowrap;
  transition: background 0.18s ease, color 0.18s ease, box-shadow 0.18s ease;
}
@media (min-width: 680px) {
  .seg-tabs {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
  }
  .seg-btn {
    flex: initial;
    font-size: 15px;
    min-height: 44px;
    padding: 8px 6px;
  }
}
.seg-btn:hover {
  color: var(--text);
}
.seg-btn.is-active {
  background: var(--card);
  color: var(--text);
  box-shadow: var(--shadow-seg);
}
.tab-panel[hidden] {
  display: none !important;
}

/* Chấm trạng thái & Nhãn trạng thái */
.status-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.dot-chay {
  background: var(--dot-run);
  box-shadow: 0 0 0 3px var(--run-bg);
}
.dot-ranh { background: var(--dot-idle); }
.dot-ket {
  background: var(--dot-stuck);
  box-shadow: 0 0 0 3px var(--warn-bg);
}
.dot-im-lang {
  background: var(--dot-silent);
  box-shadow: 0 0 0 3px var(--err-bg);
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 10px;
  border-radius: 999px;
  font-weight: 600;
  font-size: 15px;
  line-height: 1.3;
  white-space: nowrap;
}
.tt-xong, .may-ok { background: var(--ok-bg); color: var(--ok-fg); }
.tt-chay { background: var(--accent-soft); color: var(--accent); }
.may-chay { background: var(--run-bg); color: var(--run-fg); }
.may-ranh, .tt-huy { background: var(--idle-bg); color: var(--idle-fg); }
.tt-dung, .may-ket { background: var(--warn-bg); color: var(--warn-fg); }
.badge-canh-nen { white-space: normal; }
.tt-loi, .may-do { background: var(--err-bg); color: var(--err-fg); }
.qua-han {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 999px;
  font-weight: 600;
  font-size: 15px;
  background: var(--err-bg);
  color: var(--err-fg);
}

/* Lưới thẻ máy (Tab Tổng quan & Tab Máy) */
.cards-may {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 16px;
  align-items: start;
}
@media (min-width: 768px) {
  .cards-may {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 20px;
  }
}

.may-card, section.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px;
  box-shadow: var(--shadow-card);
  min-width: 0;
}
section.card {
  margin-bottom: 18px;
}
@media (min-width: 768px) {
  .may-card, section.card { padding: 20px 22px; }
}
.may-card.is-clickable {
  cursor: pointer;
  transition: transform 0.15s ease, border-color 0.15s ease;
}
@media (hover: hover) {
  .may-card.is-clickable:hover {
    border-color: var(--accent);
  }
}
.may-card.warn-disk {
  border-color: var(--urgent-border);
}

.may-card-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 4px;
}
.may-title-group {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
  flex-wrap: wrap;
}
.may-name {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.015em;
  color: var(--text);
}
.vai-tro {
  color: var(--muted);
  font-size: 15px;
  margin: 0 0 14px 0;
  overflow-wrap: anywhere;
}

.may-work-box {
  background: var(--subtle);
  border-radius: 12px;
  padding: 12px 14px;
  min-width: 0;
}
.work-top {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: baseline;
  gap: 6px 10px;
  margin-bottom: 8px;
}
.work-ticket {
  font-size: 16px;
  font-weight: 600;
  min-width: 0;
  overflow-wrap: anywhere;
}
.work-time {
  font-size: 15px;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
.progress-track, .bar-track {
  height: 8px;
  background: rgba(120, 120, 128, 0.18);
  border-radius: 999px;
  overflow: hidden;
}
.progress-fill, .bar-fill {
  height: 100%;
  background: var(--accent);
  border-radius: 999px;
  transition: width 0.35s ease;
}
.progress-fill.near-limit { background: var(--dot-stuck); }
.progress-fill.over-limit, .bar-fill.warn { background: var(--dot-silent); }

.nhip-line {
  margin-top: 10px;
  color: var(--muted);
  font-family: ui-monospace, "SF Mono", SFMono-Regular, Consolas, monospace;
  font-size: 15px;
  line-height: 1.45;
  overflow-wrap: anywhere;
  word-break: break-word;
}
.ket-note {
  color: var(--warn-fg);
  font-size: 15px;
  line-height: 1.45;
  overflow-wrap: anywhere;
}
.idle-note {
  color: var(--muted);
  font-size: 15px;
  overflow-wrap: anywhere;
}

.may-card-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid var(--divider);
}
.meta {
  color: var(--muted);
  font-size: 15px;
}
.num {
  font-variant-numeric: tabular-nums;
}
.expand-btn {
  appearance: none;
  border: none;
  background: transparent;
  color: var(--accent);
  font-family: inherit;
  font-size: 15px;
  font-weight: 600;
  min-height: 44px;
  padding: 6px 10px;
  margin: -6px -10px;
  border-radius: 8px;
  cursor: pointer;
}
@media (hover: hover) {
  .expand-btn:hover {
    background: var(--accent-soft);
  }
}
.may-detail {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--divider);
  font-size: 15px;
}
.may-detail[hidden] {
  display: none !important;
}
.detail-grid {
  display: grid;
  gap: 6px;
  margin-bottom: 12px;
}
.detail-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}
.detail-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.btn-subtle {
  appearance: none;
  border: 1px solid var(--border);
  background: var(--subtle);
  color: var(--text);
  font-family: inherit;
  font-size: 15px;
  font-weight: 600;
  min-height: 44px;
  padding: 8px 14px;
  border-radius: 999px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
}
.btn-subtle:hover {
  background: var(--subtle-hover);
  text-decoration: none;
}

/* Hàng chờ nhanh ở Tổng quan */
.quick-queue-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
section.card h2 {
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.015em;
}
.quick-queue-head h2 { margin: 0; }
.sub-heading {
  font-weight: 500;
  font-size: 15px;
  color: var(--muted);
}

/* Bộ lọc theo máy ở Tab Phiếu */
.filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 18px;
}
.filter-pill {
  appearance: none;
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--muted);
  font-family: inherit;
  font-size: 15px;
  font-weight: 600;
  min-height: 44px;
  padding: 8px 16px;
  border-radius: 999px;
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}
.filter-pill:hover {
  color: var(--text);
}
.filter-pill.is-active {
  background: var(--accent);
  border-color: var(--accent);
  color: #ffffff;
}

/* Danh sách phiếu phẳng chuẩn iOS */
.ticket-list {
  display: flex;
  flex-direction: column;
}
.ticket-row {
  padding: 14px 0;
  border-top: 1px solid var(--divider);
  min-width: 0;
}
.ticket-row:first-child {
  border-top: none;
  padding-top: 2px;
}
.ticket-row:last-child {
  padding-bottom: 2px;
}
.ticket-row-head {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 6px 12px;
  margin-bottom: 4px;
}
.ticket-main-link {
  font-size: 16px;
  font-weight: 600;
  overflow-wrap: anywhere;
}
.ticket-tags {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  color: var(--muted);
}
.tag-chip {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 999px;
  background: var(--subtle);
  color: var(--text);
  font-size: 15px;
  font-weight: 500;
}
.ticket-desc {
  font-size: 15px;
  color: var(--text);
  margin-top: 4px;
  overflow-wrap: anywhere;
}
.ticket-sub {
  font-size: 15px;
  color: var(--muted);
  margin-top: 4px;
  overflow-wrap: anywhere;
}
.older-details {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--divider);
}
.older-details summary {
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  color: var(--muted);
  min-height: 44px;
  display: flex;
  align-items: center;
}
.empty {
  color: var(--muted);
  font-size: 15px;
  margin: 0;
  padding: 6px 0;
}

/* Hồ sơ năng lực máy (Tab Máy) */
.disk-alert {
  background: var(--err-bg);
  color: var(--err-fg);
  border: 1px solid var(--urgent-border);
  border-radius: 12px;
  padding: 10px 14px;
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 14px;
}
.bar-row {
  margin: 12px 0;
  font-size: 15px;
}
.bar-label-row {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 6px;
}
.spec-list {
  margin: 14px 0 0 0;
  padding: 0;
  list-style: none;
  font-size: 15px;
}
.spec-list li {
  padding: 8px 0;
  border-top: 1px solid var(--divider);
  overflow-wrap: anywhere;
}
.spec-list code {
  font-size: 15px;
  background: var(--subtle);
  padding: 1px 6px;
  border-radius: 6px;
  overflow-wrap: anywhere;
  word-break: break-word;
}
.accounts-card {
  margin-bottom: 18px;
}
.acc-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 10px;
}
.acc-item {
  background: var(--subtle);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 10px 14px;
}
.acc-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 15px;
}
.acc-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 12px;
  font-size: 14px;
  font-variant-numeric: tabular-nums;
}
.acc-ok { color: var(--run-fg); font-weight: 600; }
.acc-warn { color: var(--warn-fg); font-weight: 600; }
.acc-err { color: var(--err-fg); font-weight: 600; }

/* Tab Công cụ: Sổ công cụ + Crawler + Zalo */
.tool-block.has-alert {
  border-color: var(--urgent-border);
}
.tool-head {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 8px 12px;
  margin-bottom: 10px;
}
.tool-head h2 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}
.tool-counts {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
  font-size: 14px;
}
.table-scroll {
  width: 100%;
  overflow-x: auto;
}
.tool-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
.tool-table th,
.tool-table td {
  text-align: left;
  padding: 9px 10px;
  border-top: 1px solid var(--divider);
  vertical-align: top;
}
.tool-table thead th {
  border-top: none;
  color: var(--muted);
  font-weight: 600;
  font-size: 13px;
  white-space: nowrap;
}
.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
  font-weight: 600;
}
.status-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}
.status-dot.dot-ok { background: var(--dot-run); }
.status-dot.dot-warn { background: var(--dot-stuck); }
.status-dot.dot-err { background: var(--dot-silent); }
.status-dot.dot-idle { background: var(--dot-idle); }
.tried-paths {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--divider);
  font-size: 14px;
}
.tried-paths summary {
  cursor: pointer;
  color: var(--muted);
  font-weight: 600;
}
.tried-list {
  margin: 8px 0 0 18px;
  padding: 0;
  color: var(--muted);
  font-size: 13px;
}

/* Trang xem chi tiết phiếu KET-QUA.md */
.detail-top-bar {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
}
.detail-meta-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
  font-size: 15px;
  color: var(--muted);
  margin-bottom: 14px;
}
pre.ket-qua {
  background: var(--code-bg);
  color: var(--code-fg);
  border: 1px solid var(--border);
  padding: 16px;
  border-radius: 12px;
  overflow-x: auto;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  word-break: break-word;
  font-size: 15px;
  line-height: 1.55;
  margin: 0;
}

/* Tab Dự án */
.du-an-card, .chat-luong-card {
  margin-bottom: 20px;
}
.du-an-head {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px 12px;
  margin-bottom: 10px;
}
.du-an-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text);
  overflow-wrap: anywhere;
}
.du-an-summary {
  background: var(--subtle);
  border-radius: 12px;
  padding: 10px 14px;
  font-size: 15px;
  font-weight: 500;
  color: var(--text);
  margin-bottom: 14px;
  overflow-wrap: anywhere;
}
.du-an-eta {
  margin-bottom: 10px;
  padding: 9px 14px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  border: 1px solid var(--border);
  background: var(--subtle);
  color: var(--text);
  overflow-wrap: anywhere;
}
.du-an-eta.is-late {
  background: var(--warn-bg);
  color: var(--warn-fg);
  border-color: rgba(255, 149, 0, 0.45);
}
.du-an-eta.is-slightly-late {
  background: var(--subtle);
  color: var(--text);
  border-color: var(--border);
}
.du-an-eta.is-on-time {
  background: var(--ok-bg);
  color: var(--ok-fg);
  border-color: rgba(52, 199, 89, 0.35);
}
.gantt-table {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}
.gantt-head-row {
  display: none;
}
.gantt-legend {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 5px 10px;
  padding: 2px 12px 6px;
  font-size: 11.5px;
  color: var(--muted);
  min-width: 0;
}
.gantt-leg-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  white-space: nowrap;
}
.gantt-swatch-dk {
  display: inline-block;
  width: 14px;
  height: 7px;
  border-radius: 3px;
  background: rgba(142, 142, 147, 0.28);
  border: 1px solid rgba(142, 142, 147, 0.55);
}
.gantt-swatch-tt {
  display: inline-block;
  width: 14px;
  height: 8px;
  border-radius: 3px;
  background: var(--dot-run);
}
.gantt-swatch-tre {
  display: inline-block;
  width: 14px;
  height: 8px;
  border-radius: 3px;
  background: var(--dot-stuck);
}
.gantt-swatch-now {
  display: inline-block;
  width: 0;
  height: 11px;
  border-left: 2px dashed var(--accent);
}
.gantt-swatch-han {
  display: inline-block;
  width: 2px;
  height: 11px;
  background: var(--dot-silent);
}
.gantt-leg-now {
  color: var(--accent);
  font-weight: 600;
}
.gantt-leg-han {
  color: var(--err-fg);
  font-weight: 600;
}
.gantt-axis {
  position: relative;
  height: 30px;
  border-bottom: 1px solid var(--border);
  min-width: 0;
}
.gantt-tick {
  position: absolute;
  top: 1px;
  transform: translateX(-50%);
  font-size: 11px;
  line-height: 14px;
  font-weight: 600;
  color: var(--muted);
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
  z-index: 2;
}
.gantt-tick::after {
  content: "";
  position: absolute;
  left: 50%;
  top: 23px;
  width: 1px;
  height: 6px;
  background: var(--border);
}
.gantt-tick.is-left {
  transform: none;
}
.gantt-tick.is-left::after {
  left: 1px;
}
.gantt-tick.is-right {
  transform: translateX(-100%);
}
.gantt-tick.is-right::after {
  left: auto;
  right: 1px;
}
.gantt-axis-now,
.gantt-axis-han {
  position: absolute;
  bottom: 0;
  height: 9px;
  width: 2px;
  transform: translateX(-1px);
  pointer-events: none;
}
.gantt-axis-now {
  background: var(--accent);
  z-index: 3;
}
.gantt-axis-now::after {
  content: "";
  position: absolute;
  top: -3px;
  left: -2px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent);
}
.gantt-axis-han {
  background: var(--dot-silent);
  z-index: 4;
}
.gantt-axis-han::after {
  content: "";
  position: absolute;
  top: -3px;
  left: -2px;
  width: 6px;
  height: 6px;
  border-radius: 1px;
  background: var(--dot-silent);
}
.timeline-list {
  display: flex;
  flex-direction: column;
}
.tl-step {
  position: relative;
  padding-left: 26px;
  padding-bottom: 12px;
  min-width: 0;
}
.tl-step.gantt-step {
  padding-left: 0;
  padding-bottom: 0;
}
.tl-step:last-child {
  padding-bottom: 0;
}
.tl-step::before {
  content: "";
  position: absolute;
  left: 6px;
  top: 22px;
  bottom: 0;
  width: 2px;
  background: var(--divider);
}
.tl-step:last-child::before,
.tl-step.gantt-step::before {
  display: none;
}
.tl-dot {
  position: absolute;
  left: 1px;
  top: 15px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--dot-idle);
}
.gantt-step .tl-dot {
  position: static;
  display: inline-block;
  flex-shrink: 0;
  vertical-align: middle;
  width: 10px;
  height: 10px;
  margin-right: 7px;
}
.gantt-row-main {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  min-width: 0;
}
.gantt-step .tl-step-toggle {
  flex-direction: column;
  align-items: stretch;
  justify-content: center;
  gap: 5px;
  padding: 10px 12px;
}
.gantt-step-top {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 6px 8px;
  width: 100%;
  min-width: 0;
}
.step-hours-line {
  display: block;
  font-size: 12.5px;
  line-height: 1.35;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
  overflow-wrap: anywhere;
}
.gantt-lane {
  display: none;
  position: relative;
  min-height: 54px;
  overflow: hidden;
  min-width: 0;
}
.gantt-grid-line {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 1px;
  background: var(--divider);
  pointer-events: none;
  z-index: 1;
}
.gantt-bar-dk {
  position: absolute;
  top: 13px;
  height: 11px;
  border-radius: 4px;
  background: rgba(142, 142, 147, 0.24);
  border: 1px solid rgba(142, 142, 147, 0.45);
  z-index: 2;
  pointer-events: none;
}
.gantt-bar-tt {
  position: absolute;
  top: 28px;
  height: 15px;
  border-radius: 5px;
  background: var(--dot-run);
  z-index: 3;
  pointer-events: none;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.14);
}
.gantt-bar-tt.st-dang-chay { background: var(--accent); }
.gantt-bar-tt.st-xong-dat { background: var(--dot-run); }
.gantt-bar-tt.st-xong-khong-dat { background: var(--dot-silent); }
.gantt-bar-tt.st-cho-claude { background: var(--dot-claude); }
.gantt-bar-tt.st-cho-linh { background: var(--dot-stuck); }
.gantt-bar-tt.is-late { background: var(--dot-stuck); }
.gantt-vline-now {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 0;
  border-left: 2px dashed var(--accent);
  z-index: 4;
  pointer-events: none;
}
.gantt-vline-han {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 2px;
  transform: translateX(-1px);
  background: var(--dot-silent);
  z-index: 5;
  pointer-events: none;
}
.tl-step.gantt-step.is-step-late .tl-step-box {
  border-color: var(--dot-stuck);
  box-shadow: inset 4px 0 0 var(--dot-stuck);
}
.tl-step.gantt-step.is-step-late .gantt-row-main {
  background: var(--warn-bg);
}
.badge-step-late {
  background: var(--warn-bg);
  color: var(--warn-fg);
  border: 1px solid rgba(255, 149, 0, 0.45);
}
@media (min-width: 680px) {
  .gantt-head-row {
    display: grid;
    grid-template-columns: minmax(255px, 330px) minmax(0, 1fr);
    align-items: end;
    border: 1px solid transparent;
    border-bottom: 1px solid var(--divider);
    padding-bottom: 4px;
  }
  .gantt-row-main {
    grid-template-columns: minmax(255px, 330px) minmax(0, 1fr);
    align-items: stretch;
  }
  .gantt-step .tl-step-toggle {
    border-right: 1px solid var(--divider);
  }
  .gantt-lane {
    display: block;
  }
}
.dot-buoc-cho { background: var(--dot-idle); }
.dot-buoc-dang-chay {
  background: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-soft);
}
.dot-buoc-xong-dat {
  background: var(--dot-run);
  box-shadow: 0 0 0 3px var(--run-bg);
}
.dot-buoc-xong-khong-dat {
  background: var(--dot-silent);
  box-shadow: 0 0 0 3px var(--err-bg);
}
.dot-buoc-cho-claude {
  background: var(--dot-claude);
  box-shadow: 0 0 0 3px var(--claude-bg);
}
.dot-buoc-cho-linh {
  background: var(--dot-stuck);
  box-shadow: 0 0 0 3px var(--warn-bg);
}
.badge-buoc-cho { background: var(--idle-bg); color: var(--idle-fg); }
.badge-buoc-dang-chay { background: var(--accent-soft); color: var(--accent); }
.badge-buoc-xong-dat { background: var(--ok-bg); color: var(--ok-fg); }
.badge-buoc-xong-khong-dat { background: var(--err-bg); color: var(--err-fg); }
.badge-buoc-cho-claude { background: var(--claude-bg); color: var(--claude-fg); }
.badge-buoc-cho-linh { background: var(--warn-bg); color: var(--warn-fg); }

.tl-step-box {
  border: 1px solid var(--border);
  border-radius: 12px;
  background: var(--card);
  overflow: hidden;
  min-width: 0;
}
.tl-step-toggle {
  appearance: none;
  border: none;
  background: transparent;
  width: 100%;
  text-align: left;
  font-family: inherit;
  color: var(--text);
  padding: 10px 12px;
  min-height: 44px;
  cursor: pointer;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 8px 10px;
}
@media (hover: hover) {
  .tl-step-toggle:hover {
    background: var(--subtle);
  }
}
.tl-step-name {
  font-size: 15px;
  font-weight: 600;
  min-width: 0;
  overflow-wrap: anywhere;
}
.tl-step-code {
  color: var(--muted);
  font-weight: 700;
  margin-right: 4px;
}
.tl-step-right {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.tl-step-run {
  padding: 0 12px 12px;
}
.tl-step-detail {
  border-top: 1px solid var(--divider);
  padding: 12px;
  background: var(--subtle);
  min-width: 0;
}
.tl-step-detail[hidden] {
  display: none !important;
}
.step-subhead {
  margin: 12px 0 6px 0;
  font-size: 14px;
  font-weight: 700;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.step-subhead:first-child {
  margin-top: 0;
}
.step-ticket-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.step-ticket-item {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 8px 10px;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 6px 10px;
  font-size: 14px;
  min-width: 0;
}
pre.step-log {
  font-size: 13px;
  line-height: 1.45;
  padding: 10px 12px;
  max-height: 280px;
  overflow-y: auto;
}
.kq-details {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 8px 10px;
  margin-top: 6px;
}
.kq-details summary {
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  min-height: 32px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.kq-details pre.ket-qua {
  margin-top: 8px;
  font-size: 13px;
  max-height: 260px;
  overflow-y: auto;
}
.thumb-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 6px;
}
@media (min-width: 680px) {
  .thumb-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
.thumb-card {
  display: flex;
  flex-direction: column;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  min-width: 0;
}
.thumb-card img {
  display: block;
  width: 100%;
  height: 110px;
  object-fit: cover;
  background: var(--code-bg);
}
.thumb-cap {
  padding: 6px 8px;
  font-size: 13px;
  color: var(--muted);
  overflow-wrap: anywhere;
}

/* Tab Chất lượng */
.cl-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--divider);
  min-width: 0;
}
.cl-section:first-of-type {
  margin-top: 8px;
  padding-top: 8px;
  border-top: none;
}
.cl-section h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
  font-weight: 700;
  color: var(--text);
}
.cl-chua-do {
  background: var(--subtle);
  border-radius: 10px;
  padding: 12px 14px;
  color: var(--muted);
  font-size: 15px;
}
.muc9-table, .cham-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
.muc9-table th, .muc9-table td,
.cham-table th, .cham-table td {
  text-align: left;
  padding: 9px 8px;
  border-bottom: 1px solid var(--divider);
  vertical-align: top;
  overflow-wrap: anywhere;
  word-break: break-word;
}
.muc9-table th, .cham-table th {
  color: var(--muted);
  font-size: 13px;
  font-weight: 600;
}
@media (min-width: 680px) {
  .cham-table th:nth-child(-n+3),
  .cham-table td:nth-child(-n+3) {
    white-space: nowrap;
    overflow-wrap: normal;
    word-break: normal;
  }
}
@media (max-width: 679px) {
  .muc9-table {
    table-layout: fixed;
    font-size: 13px;
  }
  .muc9-table th, .muc9-table td {
    padding: 8px 4px;
  }
  .muc9-table .col-ten { width: 36%; }
  .muc9-table .col-nguong { width: 22%; }
  .muc9-table .col-do { width: 22%; }
  .muc9-table .col-kq { width: 20%; }
  .muc9-table .badge {
    font-size: 13px;
    padding: 2px 7px;
  }

  .cham-table thead { display: none; }
  .cham-table, .cham-table tbody, .cham-table tr, .cham-table td {
    display: block;
    width: 100%;
  }
  .cham-table tr {
    background: var(--subtle);
    border-radius: 10px;
    padding: 8px 10px;
    margin-bottom: 8px;
    border-bottom: none;
  }
  .cham-table td {
    border-bottom: none;
    padding: 3px 0;
    font-size: 14px;
  }
  .cham-table td::before {
    content: attr(data-label) ": ";
    font-weight: 600;
    color: var(--muted);
  }
}
.ghep-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}
@media (min-width: 680px) {
  .ghep-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
.ghep-card {
  display: flex;
  flex-direction: column;
  background: var(--subtle);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  min-width: 0;
}
.ghep-card img {
  display: block;
  width: 100%;
  aspect-ratio: 16 / 10;
  object-fit: contain;
  background: var(--code-bg);
}
.ghep-meta {
  padding: 8px 10px;
  font-size: 13px;
  line-height: 1.35;
  overflow-wrap: anywhere;
}
.ghep-phieu {
  font-weight: 600;
  color: var(--text);
}
.ghep-gio {
  color: var(--muted);
  font-variant-numeric: tabular-nums;
}
"""

_DASHBOARD_JS = r"""
(function () {
  var REFRESH_MS = 15000;
  var appRoot = document.getElementById("bang-app");
  if (!appRoot) return;

  var state = {
    activeTab: appRoot.getAttribute("data-initial-tab") || "du-an",
    machineFilter: "tat-ca",
    expandedMachines: {},
    expandedSteps: {},
    olderOpen: false,
    data: null
  };

  var initEl = document.getElementById("bang-init-data");
  if (initEl) {
    try {
      state.data = JSON.parse(initEl.textContent || "{}");
    } catch (_e) {
      state.data = null;
    }
  }

  function esc(val) {
    var s = val === null || val === undefined ? "" : String(val);
    return s
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#x27;");
  }

  function copyText(text, btn) {
    var done = function () {
      if (!btn) return;
      var orig = btn.getAttribute("data-label") || "Chép lệnh";
      btn.textContent = "Đã chép";
      btn.classList.add("is-copied");
      setTimeout(function () {
        btn.textContent = orig;
        btn.classList.remove("is-copied");
      }, 1800);
    };
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done).catch(function () {
        fallbackCopy(text, done);
      });
    } else {
      fallbackCopy(text, done);
    }
  }

  function fallbackCopy(text, cb) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.top = "-9999px";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.focus();
    ta.select();
    try {
      document.execCommand("copy");
      if (cb) cb();
    } catch (_e) {}
    document.body.removeChild(ta);
  }

  function setTab(tabName, pushUrl) {
    if (["du-an", "chat-luong", "tong-quan", "phieu", "may", "cong-cu"].indexOf(tabName) === -1) {
      tabName = "du-an";
    }
    state.activeTab = tabName;
    var btns = document.querySelectorAll(".seg-btn[data-tab]");
    for (var i = 0; i < btns.length; i++) {
      var b = btns[i];
      var isAct = b.getAttribute("data-tab") === tabName;
      b.classList.toggle("is-active", isAct);
      b.setAttribute("aria-selected", isAct ? "true" : "false");
    }
    var panels = document.querySelectorAll(".tab-panel[data-panel]");
    for (var j = 0; j < panels.length; j++) {
      var p = panels[j];
      var show = p.getAttribute("data-panel") === tabName;
      if (show) {
        p.removeAttribute("hidden");
      } else {
        p.setAttribute("hidden", "");
      }
    }
    if (pushUrl && window.history && window.history.replaceState) {
      var pathMap = {
        "du-an": "/",
        "chat-luong": "/chat-luong",
        "tong-quan": "/tong-quan",
        "phieu": "/phieu",
        "may": "/may",
        "cong-cu": "/cong-cu"
      };
      var nextPath = pathMap[tabName] || "/";
      if (window.location.pathname !== nextPath) {
        window.history.replaceState(null, "", nextPath);
      }
    }
  }

  function parseIsoMs(isoStr) {
    if (!isoStr) return NaN;
    var t = Date.parse(isoStr);
    return isNaN(t) ? NaN : t;
  }

  function splitDone24h(doneList, nowIso) {
    var nowMs = parseIsoMs(nowIso);
    if (isNaN(nowMs)) nowMs = Date.now();
    var d24 = [];
    var older = [];
    for (var i = 0; i < doneList.length; i++) {
      var item = doneList[i];
      var dMs = parseIsoMs(item.xong_luc);
      if (isNaN(dMs) || (nowMs - dMs) <= 86400000) {
        d24.push(item);
      } else {
        older.push(item);
      }
    }
    return { d24: d24, older: older };
  }

  function buildHeroHtml(data) {
    var machines = data.may || [];
    var canLinh = data.can_linh || [];
    var cntRun = 0, cntIdle = 0, cntStuck = 0, cntSilent = 0;
    for (var i = 0; i < machines.length; i++) {
      var m = machines[i];
      if (m.qua_30_phut || m.trang_thai_may === "im-lang") cntSilent++;
      else if (m.trang_thai_may === "chay") cntRun++;
      else if (m.trang_thai_may === "ket") cntStuck++;
      else cntIdle++;
    }
    if (canLinh.length > 0) {
      return esc(cntRun + " máy chạy, ") + '<span class="need-you">' + esc(canLinh.length + " cần anh") + "</span>";
    }
    if (machines.length === 0) {
      return "Chưa ghi nhận máy hoạt động";
    }
    if (cntStuck > 0 && cntSilent > 0) {
      return esc(cntRun + " máy chạy, " + cntStuck + " kẹt · " + cntSilent + " im lặng");
    }
    if (cntStuck > 0) {
      return esc(cntRun + " máy chạy, " + cntStuck + " máy kẹt");
    }
    if (cntSilent > 0) {
      return esc(cntRun + " máy chạy, " + cntSilent + " im lặng");
    }
    if (cntIdle > 0) {
      return esc(cntRun + " máy chạy, " + cntIdle + " máy rảnh");
    }
    return esc(cntRun + " máy đang chạy");
  }

  function renderCanLinh(canLinh) {
    if (!canLinh || canLinh.length === 0) return "";
    var boxCls = "can-linh" + "-box";
    var html = '<section class="' + boxCls + '"><div class="can-linh-head">' +
      '<span class="status-dot dot-im-lang" aria-hidden="true"></span>' +
      "<h2>Cần anh làm (" + canLinh.length + ")</h2></div>";
    for (var i = 0; i < canLinh.length; i++) {
      var cl = canLinh[i];
      var phieu = cl.phieu || cl.id || "";
      var href = cl.ket_qua_url || ("/phieu/" + encodeURIComponent(phieu));
      var lenh = (cl.lenh || "").trim();
      var copyPayload = lenh || cl.viec || phieu;
      html += '<div class="can-linh-item"><div class="can-linh-meta">' +
        "<strong>" + esc(cl.may || "máy") + "</strong> · " +
        '<a href="' + esc(href) + '">' + esc(phieu) + "</a>" +
        (cl.gio_hien_thi ? ' <span class="meta">· ' + esc(cl.gio_hien_thi) + "</span>" : "") +
        "</div>" +
        '<div class="can-linh-viec">' + esc(cl.viec || "") + "</div>" +
        '<div class="cmd-row">' +
        (lenh ? '<code class="cmd-paste">' + esc(lenh) + "</code>" : "") +
        '<button type="button" class="btn-copy" data-label="Chép lệnh" data-copy="' + esc(copyPayload) + '">Chép lệnh</button>' +
        "</div></div>";
    }
    html += "</section>";
    return html;
  }

  function renderUsageBar(label, totalGb, freeGb, warnLow) {
    var tot = Math.max(0, Number(totalGb || 0));
    var free = Math.max(0, Number(freeGb || 0));
    var used = Math.max(0, tot - free);
    var pct = tot > 0 ? Math.min(100, Math.max(0, Math.round((used / tot) * 100))) : 0;
    var fillCls = (warnLow || pct >= 90) ? "bar-fill warn" : "bar-fill";
    return '<div class="bar-row"><div class="bar-label-row">' +
      "<strong>" + esc(label) + "</strong>" +
      '<span class="meta num">trống ' + free.toFixed(1) + " / " + tot.toFixed(1) + " GB (" + pct + "%)</span></div>" +
      '<div class="bar-track"><div class="' + fillCls + '" style="width:' + pct + '%"></div></div></div>';
  }

  function renderOverviewMachines(data) {
    var machines = data.may || [];
    if (machines.length === 0) {
      return '<section class="card"><p class="empty">Chưa ghi nhận máy nào.</p></section>';
    }
    var runByTicket = {};
    var running = data.dang_chay || [];
    for (var r = 0; r < running.length; r++) {
      runByTicket[running[r].phieu] = running[r];
    }
    var profByMay = {};
    var profs = data.ho_so_may || [];
    for (var p = 0; p < profs.length; p++) {
      profByMay[profs[p].ma_may] = profs[p];
    }

    var cards = [];
    for (var i = 0; i < machines.length; i++) {
      var m = machines[i];
      var ma = m.may || "may";
      var isRed = Boolean(m.qua_30_phut) || m.trang_thai_may === "im-lang";
      var tt = isRed ? "im-lang" : (m.trang_thai_may || "ranh");
      var dotCls = tt === "chay" ? "dot-chay" : (tt === "ket" ? "dot-ket" : (tt === "im-lang" ? "dot-im-lang" : "dot-ranh"));
      var statusBadge = "";
      if (isRed) statusBadge = '<span class="qua-han">Im lặng &gt; 30 phút</span>';
      else if (tt === "chay") statusBadge = '<span class="badge may-chay">Đang chạy</span>';
      else if (tt === "ket") statusBadge = '<span class="badge may-ket">Kẹt (' + esc(m.ket_trang_thai || "lỗi") + ")</span>";
      else statusBadge = '<span class="badge may-ranh">Rảnh</span>';

      var diskWarn = m.canh_bao_o_c ? ' <span class="badge may-do">Ổ C &lt; 10GB</span>' : "";
      var prof = profByMay[ma] || null;
      var vaiTro = m.vai_tro || (prof && prof.vai_tro) || "Máy thợ hàng đợi";

      var workHtml = "";
      if (m.dang_lam_phieu) {
        var rItem = runByTicket[m.dang_lam_phieu] || {};
        var phut = Number(m.dang_lam_phut || rItem.chay_phut || 0);
        var phutInt = Math.round(phut);
        var tran = Number(rItem.tran_phut || 40);
        var tranInt = Math.round(tran);
        var pct = tran > 0 ? Math.min(100, Math.max(4, Math.round((phut / tran) * 100))) : 0;
        var pFillCls = pct >= 95 ? "progress-fill over-limit" : (pct >= 80 ? "progress-fill near-limit" : "progress-fill");
        var extraCnt = Number(m.dang_chay_so_luong || 1);
        var extraTxt = extraCnt > 1 ? " (+" + (extraCnt - 1) + ")" : "";
        var hrefRun = "/phieu/" + encodeURIComponent(m.dang_lam_phieu);
        var nhipTxt = m.nhip || "Mới nhận phiếu, đang chờ nhịp báo cáo…";
        var canhNenTxt = m.nhan_canh_nen || rItem.nhan_canh_nen || "";
        var canhNenRow = canhNenTxt ? ('<div style="margin:6px 0 4px"><span class="badge tt-dung badge-canh-nen">' + esc(canhNenTxt) + "</span></div>") : "";
        workHtml = '<div class="may-work-box"><div class="work-top">' +
          '<div class="work-ticket"><a href="' + esc(hrefRun) + '">' + esc(m.dang_lam_phieu) + "</a>" + esc(extraTxt) + "</div>" +
          '<div class="work-time">' + phutInt + " phút / " + tranInt + "p</div></div>" +
          canhNenRow +
          '<div class="progress-track"><div class="' + pFillCls + '" style="width:' + pct + '%"></div></div>' +
          '<div class="nhip-line">' + esc(nhipTxt) + "</div></div>";
      } else if (m.ket_phieu) {
        var ketHref = "/phieu/" + encodeURIComponent(m.ket_phieu);
        workHtml = '<div class="may-work-box"><div class="ket-note">Kẹt (' + esc(m.ket_trang_thai || "lỗi") + ") " +
          '<a href="' + esc(ketHref) + '">' + esc(m.ket_phieu) + "</a>: " + esc(m.ket_ly_do || "") + "</div>" +
          '<div class="nhip-line">Nhịp cuối: ' + esc(m.cach_day || "—") + "</div></div>";
      } else {
        var idleBody = "Chưa nhận việc";
        if ((m.su_kien_cuoi === "nhan" || m.su_kien_cuoi === "xong") && m.phieu_cuoi) {
          var verb = m.su_kien_cuoi === "nhan" ? "nhận" : "xong";
          var tHref = "/phieu/" + encodeURIComponent(m.phieu_cuoi);
          var ago = (m.cach_day && m.cach_day !== "—") ? " · " + esc(m.cach_day) : "";
          idleBody = "Mới " + verb + ' <a href="' + esc(tHref) + '">' + esc(m.phieu_cuoi) + "</a>" + ago;
        }
        workHtml = '<div class="may-work-box"><div class="idle-note">' + idleBody + "</div></div>";
      }

      var isExpanded = Boolean(state.expandedMachines[ma]);
      var ramSummary = "Chưa có hồ sơ RAM/ổ";
      if (prof && prof.ram) {
        ramSummary = "RAM trống " + Number(prof.ram.trong_gb || 0).toFixed(1) + "/" + Number(prof.ram.tong_gb || 0).toFixed(1) + " GB";
        if (prof.o_c_trong_gb !== null && prof.o_c_trong_gb !== undefined) {
          ramSummary += " · Ổ C trống " + Number(prof.o_c_trong_gb).toFixed(1) + " GB";
        }
      }
      var tk24 = (prof && prof.thong_ke_24h) || null;
      var tkLine = tk24 ? ("Xong " + Number(tk24.xong || 0) + " · Lỗi " + Number(tk24.loi || 0)) : "—";
      var focusTicket = m.dang_lam_phieu || m.ket_phieu || m.phieu_cuoi || "";
      var cardCls = "may-card is-clickable" + (m.canh_bao_o_c ? " warn-disk" : "");

      cards.push(
        '<article class="' + cardCls + '" data-may-card="' + esc(ma) + '">' +
        '<div class="may-card-head"><div class="may-title-group">' +
        '<span class="status-dot ' + dotCls + '" aria-hidden="true"></span>' +
        '<h3 class="may-name">' + esc(ma) + "</h3>" + diskWarn +
        "</div>" + statusBadge + "</div>" +
        '<p class="vai-tro">' + esc(vaiTro) + "</p>" +
        workHtml +
        '<div class="may-card-foot"><span class="meta">' + esc(m.cach_day || "—") + "</span>" +
        '<button type="button" class="expand-btn" data-toggle-may="' + esc(ma) + '" aria-expanded="' + (isExpanded ? "true" : "false") + '">' +
        (isExpanded ? "Thu gọn" : "Chi tiết") + "</button></div>" +
        '<div class="may-detail" data-detail-may="' + esc(ma) + '"' + (isExpanded ? "" : " hidden") + ">" +
        '<div class="detail-grid">' +
        '<div class="detail-row"><span class="meta">Lần cuối</span><span class="num">' + esc(m.lan_cuoi_hien_thi || "—") + "</span></div>" +
        '<div class="detail-row"><span class="meta">Tài nguyên</span><span>' + esc(ramSummary) + "</span></div>" +
        '<div class="detail-row"><span class="meta">24h qua</span><span>' + esc(tkLine) + "</span></div>" +
        (prof && prof.ten_windows ? '<div class="detail-row"><span class="meta">Windows</span><code>' + esc(prof.ten_windows) + "</code></div>" : "") +
        "</div>" +
        '<div class="detail-actions">' +
        '<button type="button" class="btn-subtle" data-jump-filter="' + esc(ma) + '">Lọc phiếu ' + esc(ma) + "</button>" +
        (focusTicket ? '<a class="btn-subtle" href="/phieu/' + encodeURIComponent(focusTicket) + '">Xem phiếu ' + esc(focusTicket) + "</a>" : "") +
        "</div></div></article>"
      );
    }
    return '<div class="cards-may">' + cards.join("") + "</div>";
  }

  function collectFilterMachines(data) {
    var seen = {};
    var list = [];
    function add(name) {
      if (!name || seen[name]) return;
      seen[name] = true;
      list.push(name);
    }
    var ms = data.may || [];
    for (var i = 0; i < ms.length; i++) add(ms[i].may);
    var wt = data.dang_cho || [];
    for (var j = 0; j < wt.length; j++) add(wt[j].may);
    return list;
  }

  function renderTicketsTab(data) {
    var filter = state.machineFilter || "tat-ca";
    var mNames = collectFilterMachines(data);
    if (filter !== "tat-ca" && mNames.indexOf(filter) === -1) {
      filter = "tat-ca";
      state.machineFilter = "tat-ca";
    }

    var pills = ['<button type="button" class="filter-pill' + (filter === "tat-ca" ? " is-active" : "") + '" data-filter-may="tat-ca">Tất cả</button>'];
    for (var i = 0; i < mNames.length; i++) {
      var mn = mNames[i];
      pills.push('<button type="button" class="filter-pill' + (filter === mn ? " is-active" : "") + '" data-filter-may="' + esc(mn) + '">' + esc(mn) + "</button>");
    }

    var matchMay = function (item) {
      return filter === "tat-ca" || item.may === filter;
    };
    var running = (data.dang_chay || []).filter(matchMay);
    var waiting = (data.dang_cho || []).filter(matchMay);
    var allDone = (data.xong_gan_nhat || []).filter(matchMay);
    var split = splitDone24h(allDone, data.cap_nhat_luc);

    var runHtml = "";
    if (running.length > 0) {
      var rRows = [];
      for (var r = 0; r < running.length; r++) {
        var it = running[r];
        var tran = Number(it.tran_phut || 40);
        var phut = Number(it.chay_phut || 0);
        var pct = tran > 0 ? Math.min(100, Math.max(4, Math.round((phut / tran) * 100))) : 0;
        var canhNenBadge = it.nhan_canh_nen ? ('<span class="badge tt-dung badge-canh-nen">' + esc(it.nhan_canh_nen) + "</span>") : "";
        rRows.push(
          '<div class="ticket-row"><div class="ticket-row-head">' +
          '<a class="ticket-main-link" href="' + esc(it.ket_qua_url) + '">' + esc(it.phieu) + "</a>" +
          '<div class="ticket-tags">' + canhNenBadge + '<span class="tag-chip">' + esc(it.may) + "</span>" +
          '<span class="tag-chip">' + esc(it.loai) + "</span>" +
          '<span class="num">' + esc(it.chay_bao_lau) + " / " + esc(it.tran_phut) + "p</span></div></div>" +
          '<div class="progress-track" style="margin:8px 0 4px"><div class="progress-fill" style="width:' + pct + '%"></div></div>' +
          (it.de ? '<div class="ticket-desc">' + esc(it.de) + "</div>" : "") +
          (it.nhip ? '<div class="nhip-line">' + esc(it.nhip) + "</div>" : "") +
          "</div>"
        );
      }
      runHtml = '<div class="ticket-list">' + rRows.join("") + "</div>";
    } else {
      runHtml = '<p class="empty">Không có phiếu đang chạy.</p>';
    }

    var waitHtml = "";
    if (waiting.length > 0) {
      var wRows = [];
      for (var w = 0; w < waiting.length; w++) {
        var wt = waiting[w];
        wRows.push(
          '<div class="ticket-row"><div class="ticket-row-head">' +
          '<a class="ticket-main-link" href="' + esc(wt.ket_qua_url) + '">' + esc(wt.phieu) + "</a>" +
          '<div class="ticket-tags"><span class="tag-chip">' + esc(wt.may) + "</span>" +
          '<span class="tag-chip">' + esc(wt.loai) + "</span>" +
          '<span class="num">trần ' + esc(wt.tran_phut) + " phút</span></div></div>" +
          '<div class="ticket-desc">' + esc(wt.de || "") + "</div></div>"
        );
      }
      waitHtml = '<div class="ticket-list">' + wRows.join("") + "</div>";
    } else {
      waitHtml = '<p class="empty">Không có phiếu đang chờ.</p>';
    }

    var renderDoneRow = function (d) {
      var st = d.trang_thai || "loi";
      var bCls = (st === "xong" || st === "loi" || st === "dung" || st === "huy") ? ("badge tt-" + st) : "badge tt-loi";
      var tok = Number(d.tong_token || 0).toLocaleString("en-US");
      var extraReason = d.ly_do_ngan ? ('<div class="ket-note">' + esc(d.ly_do_ngan) + "</div>") : (d.tom_tat ? ('<div class="ticket-sub">' + esc(d.tom_tat) + "</div>") : "");
      return '<div class="ticket-row"><div class="ticket-row-head">' +
        '<a class="ticket-main-link" href="' + esc(d.ket_qua_url) + '">' + esc(d.phieu) + "</a>" +
        '<div class="ticket-tags"><span class="' + bCls + '">' + esc(st) + "</span>" +
        '<span class="tag-chip">' + esc(d.may) + "</span>" +
        '<span class="num">' + Number(d.phut || 0).toFixed(2) + " phút · " + esc(tok) + " tok</span></div></div>" +
        '<div class="ticket-sub num">' + esc(d.xong_luc_hien_thi || "—") + "</div>" +
        extraReason + "</div>";
    };

    var done24Html = split.d24.length > 0
      ? ('<div class="ticket-list">' + split.d24.map(renderDoneRow).join("") + "</div>")
      : '<p class="empty">Chưa có phiếu hoàn thành trong 24h qua.</p>';

    var olderBlock = "";
    if (split.older.length > 0) {
      olderBlock = '<details class="older-details"' + (state.olderOpen ? " open" : "") + ">" +
        "<summary>Trước 24h (" + split.older.length + ")</summary>" +
        '<div class="ticket-list">' + split.older.map(renderDoneRow).join("") + "</div></details>";
    }

    var totalDone = Number(data.tong_xong || allDone.length);
    return '<div class="filter-bar" role="group" aria-label="Lọc theo máy">' + pills.join("") + "</div>" +
      '<section class="card"><h2>Đang chạy (' + running.length + ")</h2>" + runHtml + "</section>" +
      '<section class="card"><h2>Đang chờ (' + waiting.length + ")</h2>" + waitHtml + "</section>" +
      '<section class="card"><h2>Xong 24h (' + split.d24.length + ') <span class="sub-heading">· Xong gần nhất (' + allDone.length + "/" + totalDone + " phiếu)</span></h2>" +
      done24Html + olderBlock + "</section>";
  }

  function renderAccountsCardHtml(data) {
    var rows = data.tai_khoan_may || [];
    if (rows.length === 0) {
      return '<section class="card accounts-card"><h2>Tài khoản</h2><p class="empty">Chưa có dữ liệu tài khoản.</p></section>';
    }
    var items = [];
    for (var i = 0; i < rows.length; i++) {
      var r = rows[i];
      var agyTag = (r.agy_tai_khoan && r.agy_tai_khoan !== "chua_ro")
        ? ('<span class="meta">agy: <code>' + esc(r.agy_tai_khoan) + "</code></span>")
        : "";
      items.push(
        '<div class="acc-item">' +
        '<div class="acc-head"><strong>' + esc(r.may || "may") + "</strong>" + agyTag + "</div>" +
        '<div class="acc-stats">' +
        '<span class="acc-ok">' + Number(r.dung_duoc || 0) + " dùng được</span>" +
        '<span class="acc-warn">' + Number(r.het_han_muc || 0) + " hết hạn mức</span>" +
        '<span class="acc-err">' + Number(r.can_dang_nhap || 0) + " cần đăng nhập</span>" +
        "</div></div>"
      );
    }
    return '<section class="card accounts-card"><h2>Tài khoản</h2><div class="acc-grid">' + items.join("") + "</div></section>";
  }

  function fmtNum(val) {
    var n = Number(val);
    if (!isFinite(n)) return esc(val);
    try {
      return n.toLocaleString("en-US");
    } catch (_e) {
      return String(n);
    }
  }

  function renderAccountStatusPill(tt) {
    if (tt === "can_dang_nhap") {
      return '<span class="status-pill acc-err"><span class="status-dot dot-err"></span>Cần đăng nhập</span>';
    }
    if (tt === "het_han_muc") {
      return '<span class="status-pill acc-warn"><span class="status-dot dot-warn"></span>Hết hạn mức</span>';
    }
    return '<span class="status-pill acc-ok"><span class="status-dot dot-ok"></span>Dùng được</span>';
  }

  function renderToolsTab(data) {
    var htmlParts = [renderAccountsCardHtml(data)];
    var tools = data.so_cong_cu || [];
    if (tools.length === 0) {
      htmlParts.push('<section class="card"><h2>Sổ công cụ</h2><p class="empty">Chưa có mục nào trong hang-doi/tai-khoan.json.</p></section>');
    } else {
      for (var t = 0; t < tools.length; t++) {
        var grp = tools[t];
        var cls = (Number(grp.can_xu_ly || 0) > 0) ? "card tool-block has-alert" : "card tool-block";
        var rowsHtml = [];
        var accs = grp.tai_khoan || [];
        for (var a = 0; a < accs.length; a++) {
          var row = accs[a];
          var conLaiTxt = (row.con_lai === "chua_ro" || row.con_lai === null || row.con_lai === undefined)
            ? '<span class="meta">chua_ro</span>'
            : fmtNum(row.con_lai);
          var resetRaw = row.reset_luc && row.reset_luc !== "chua_ro" ? esc(row.reset_luc) : '<span class="meta">chua_ro</span>';
          var nguonTag = row.nguon ? (' <span class="meta">(' + esc(row.nguon) + ")</span>") : "";
          rowsHtml.push(
            "<tr>" +
            "<td><code>" + esc(row.email_che || "chua_ro") + "</code></td>" +
            "<td><code>" + esc(row.may || "bat-ky") + "</code></td>" +
            "<td>" + (row.ho_so_chrome ? ("<code>" + esc(row.ho_so_chrome) + "</code>") : '<span class="meta">—</span>') + "</td>" +
            '<td class="num">' + fmtNum(row.da_dung_24h || 0) + "</td>" +
            '<td class="num">' + conLaiTxt + "</td>" +
            '<td class="num">' + resetRaw + nguonTag + "</td>" +
            "<td>" + renderAccountStatusPill(row.trang_thai) + "</td>" +
            "</tr>"
          );
        }
        htmlParts.push(
          '<section class="' + cls + '">' +
          '<div class="tool-head">' +
          "<h2><code>" + esc(grp.cong_cu || "khac") + "</code></h2>" +
          '<div class="tool-counts">' +
          '<span class="acc-ok">' + Number(grp.dung_duoc || 0) + " dùng được</span>" +
          '<span class="acc-warn">' + Number(grp.het_han_muc || 0) + " hết hạn mức</span>" +
          '<span class="acc-err">' + Number(grp.can_dang_nhap || 0) + " cần đăng nhập</span>" +
          "</div></div>" +
          '<div class="table-scroll"><table class="tool-table">' +
          "<thead><tr><th>Tài khoản</th><th>Máy</th><th>Hồ sơ Chrome</th><th>Đã dùng 24h</th><th>Còn lại</th><th>Reset lúc</th><th>Trạng thái</th></tr></thead>" +
          "<tbody>" + rowsHtml.join("") + "</tbody></table></div></section>"
        );
      }
    }

    // Khối Crawler
    var crawlerMachines = data.crawler || [];
    var cRows = [];
    var cTried = [];
    for (var c = 0; c < crawlerMachines.length; c++) {
      var cm = crawlerMachines[c];
      var nguons = cm.nguon || [];
      for (var n = 0; n < nguons.length; n++) {
        var ng = nguons[n];
        var dotCls = "dot-idle";
        var lbl = "Chưa chạy";
        if (ng.trang_thai === "ok") { dotCls = "dot-ok"; lbl = "Ổn định"; }
        else if (ng.trang_thai === "bi_chan") { dotCls = "dot-err"; lbl = "Bị chặn"; }
        else if (ng.trang_thai === "loi") { dotCls = "dot-err"; lbl = "Lỗi"; }
        cRows.push(
          "<tr>" +
          '<td><span class="status-pill"><span class="status-dot ' + dotCls + '"></span>' + esc(lbl) + "</span></td>" +
          "<td><strong>" + esc(ng.nguon || "—") + "</strong></td>" +
          "<td><code>" + esc(cm.may || "—") + "</code></td>" +
          '<td class="num">' + esc(ng.lan_chay_cuoi || "—") + "</td>" +
          '<td class="num">' + fmtNum(ng.so_trang || 0) + "</td>" +
          "<td>" + esc(ng.loi_gan_nhat || "—") + "</td>" +
          "<td><code>" + esc(ng.thu_muc_du_lieu || "—") + "</code></td>" +
          "</tr>"
        );
      }
      if (!cm.tim_thay || nguons.length === 0) {
        var cpList = (cm.duong_dan_da_thu || []).map(function (p) { return "<li><code>" + esc(p) + "</code></li>"; }).join("");
        cTried.push(
          '<div class="tried-paths"><strong>Máy <code>' + esc(cm.may) + "</code>:</strong> chưa tìm thấy crawler." +
          (cpList ? ('<details><summary>Đường dẫn đã thử (' + (cm.duong_dan_da_thu || []).length + ')</summary><ul class="tried-list">' + cpList + "</ul></details>") : "") +
          "</div>"
        );
      }
    }
    var crawlerBody = "";
    if (cRows.length > 0) {
      crawlerBody += '<div class="table-scroll"><table class="tool-table"><thead><tr><th>Trạng thái</th><th>Nguồn / Adapter</th><th>Máy</th><th>Lần chạy cuối</th><th>Số trang/bài</th><th>Lỗi / bị chặn</th><th>Thư mục dữ liệu</th></tr></thead><tbody>' + cRows.join("") + "</tbody></table></div>";
    } else if (crawlerMachines.length === 0) {
      crawlerBody += '<p class="empty">Chưa có báo cáo từ <code>runner/lenh/crawler.ps1</code>.</p>';
    }
    crawlerBody += cTried.join("");
    htmlParts.push('<section class="card crawler-card"><h2>Crawler</h2>' + crawlerBody + "</section>");

    // Khối Zalo
    var zaloMachines = data.zalo || [];
    var zRows = [];
    var zTried = [];
    for (var z = 0; z < zaloMachines.length; z++) {
      var zm = zaloMachines[z];
      var bns = zm.bo_nghe || [];
      for (var b = 0; b < bns.length; b++) {
        var bn = bns[b];
        var zDot = bn.dang_chay ? "dot-ok" : "dot-err";
        var zLbl = bn.dang_chay ? "Đang chạy" : "Dừng";
        var grps = (bn.nhom || []).map(function (g) { return '<span class="tag-chip">' + esc(g) + "</span>"; }).join(" ") || '<span class="meta">—</span>';
        zRows.push(
          "<tr>" +
          '<td><span class="status-pill"><span class="status-dot ' + zDot + '"></span>' + esc(zLbl) + "</span></td>" +
          "<td><strong>" + esc(bn.ten || "—") + "</strong></td>" +
          "<td><code>" + esc(zm.may || "—") + "</code></td>" +
          "<td>" + grps + "</td>" +
          '<td class="num">' + esc(bn.tin_cuoi_luc || "—") + "</td>" +
          "<td>" + esc(bn.loi_gan_nhat || "—") + "</td>" +
          "</tr>"
        );
      }
      if (!zm.tim_thay || bns.length === 0) {
        var zpList = (zm.duong_dan_da_thu || []).map(function (p) { return "<li><code>" + esc(p) + "</code></li>"; }).join("");
        zTried.push(
          '<div class="tried-paths"><strong>Máy <code>' + esc(zm.may) + "</code>:</strong> chưa tìm thấy bộ nghe Zalo." +
          (zpList ? ('<details><summary>Đường dẫn đã thử (' + (zm.duong_dan_da_thu || []).length + ')</summary><ul class="tried-list">' + zpList + "</ul></details>") : "") +
          "</div>"
        );
      }
    }
    var zaloBody = "";
    if (zRows.length > 0) {
      zaloBody += '<div class="table-scroll"><table class="tool-table"><thead><tr><th>Trạng thái</th><th>Bộ nghe</th><th>Máy</th><th>Nhóm đang nghe</th><th>Tin cuối lúc</th><th>Lỗi gần nhất</th></tr></thead><tbody>' + zRows.join("") + "</tbody></table></div>";
    } else if (zaloMachines.length === 0) {
      zaloBody += '<p class="empty">Chưa có báo cáo từ <code>runner/lenh/zalo.ps1</code>.</p>';
    }
    zaloBody += zTried.join("");
    htmlParts.push('<section class="card zalo-card"><h2>Zalo</h2>' + zaloBody + "</section>");
    return htmlParts.join("");
  }

  function renderProfilesTab(data) {
    var profs = data.ho_so_may || [];
    if (profs.length === 0) {
      return '<section class="card"><p class="empty">Chưa có hồ sơ máy trong hang-doi/may/*.json.</p></section>';
    }
    var cards = [];
    for (var i = 0; i < profs.length; i++) {
      var p = profs[i];
      var ma = p.ma_may || "may";
      var warnC = Boolean(p.canh_bao_o_c);
      var cardCls = warnC ? "may-card warn-disk" : "may-card";
      var alertHtml = warnC
        ? ('<div class="disk-alert">Cảnh báo: Ổ C: chỉ còn trống ' + Number(p.o_c_trong_gb || 0).toFixed(1) + " GB (&lt; 10 GB)!</div>")
        : "";
      var ram = p.ram || {};
      var bars = [renderUsageBar("RAM", ram.tong_gb || 0, ram.trong_gb || 0, false)];
      var disks = p.o_dia || [];
      for (var d = 0; d < disks.length; d++) {
        var od = disks[d];
        if (!od) continue;
        var oName = String(od.o || "Ổ");
        var lowC = oName.trim().toUpperCase().replace(/[\\/]+$/, "") === "C:" && Number(od.trong_gb || 0) < 10.0;
        bars.push(renderUsageBar("Ổ " + oName, od.tong_gb || 0, od.trong_gb || 0, lowC));
      }
      var gpus = p.gpu || [];
      var gpuTxt = "Không rõ / Onboard";
      if (gpus.length > 0) {
        gpuTxt = gpus.map(function (g) {
          return (g.ten || "GPU") + (g.vram_gb ? (" (" + g.vram_gb + " GB)") : "");
        }).join(", ");
      }
      var chrome = p.chrome || {};
      var chromeTxt = "Không";
      if (chrome.co) {
        var prList = (chrome.profiles || []).slice(0, 8);
        var more = (chrome.profiles || []).length > 8 ? (" (+" + (chrome.profiles.length - 8) + ")") : "";
        chromeTxt = prList.length > 0 ? ("Có (" + prList.join(", ") + more + ")") : "Có";
      }
      var nhanCfg = p.nhan_phieu || {};
      var cheDo = nhanCfg.nhan_bat_ky === false ? "Chỉ nhận đích danh" : "Nhận cả bat-ky";
      var cpu = p.cpu || {};
      var agy = p.agy || {};
      var tk24 = p.thong_ke_24h || {};

      cards.push(
        '<article class="' + cardCls + '"><div class="may-card-head">' +
        '<h3 class="may-name">' + esc(ma) + " · <code>" + esc(p.ten_windows || "—") + "</code></h3>" +
        '<span class="meta num">24h: xong ' + Number(tk24.xong || 0) + " / lỗi " + Number(tk24.loi || 0) + "</span></div>" +
        '<p class="vai-tro">' + esc(p.vai_tro || "Chưa đặt LINHX_VAI trong tho.env") + "</p>" +
        alertHtml + bars.join("") +
        '<ul class="spec-list">' +
        "<li><strong>CPU:</strong> " + esc(cpu.ten || "—") + " (" + esc(cpu.nhan || "?") + " nhân / " + esc(cpu.luong || "?") + " luồng)</li>" +
        "<li><strong>GPU:</strong> " + esc(gpuTxt) + "</li>" +
        "<li><strong>Nhận phiếu:</strong> tối đa <strong>" + esc(nhanCfg.so_phieu !== undefined ? nhanCfg.so_phieu : 1) + "</strong> phiếu code · " + esc(cheDo) + "</li>" +
        "<li><strong>agy:</strong> <code>" + esc(agy.duong_dan || "agy") + "</code> (" + esc(agy.phien_ban || "chưa rõ") + ") · Python " + esc(p.python || "—") + "</li>" +
        "<li><strong>Chrome:</strong> " + esc(chromeTxt) + "</li>" +
        "</ul></article>"
      );
    }
    return '<div class="cards-may">' + cards.join("") + "</div>";
  }

  function renderStepStatusBadge(step) {
    var st = step.trang_thai || "cho";
    var known = {
      "cho": "badge badge-buoc-cho",
      "dang-chay": "badge badge-buoc-dang-chay",
      "xong-dat": "badge badge-buoc-xong-dat",
      "xong-khong-dat": "badge badge-buoc-xong-khong-dat",
      "cho-claude": "badge badge-buoc-cho-claude",
      "cho-linh": "badge badge-buoc-cho-linh"
    };
    var cls = known[st] || "badge badge-buoc-cho";
    var lbl = step.trang_thai_nhan || st;
    return '<span class="' + cls + '">' + esc(lbl) + "</span>";
  }

  function renderProjectStep(maDa, step, idx, ganttTruc) {
    var st = step.trang_thai || "cho";
    var dotKnown = {
      "cho": "dot-buoc-cho",
      "dang-chay": "dot-buoc-dang-chay",
      "xong-dat": "dot-buoc-xong-dat",
      "xong-khong-dat": "dot-buoc-xong-khong-dat",
      "cho-claude": "dot-buoc-cho-claude",
      "cho-linh": "dot-buoc-cho-linh"
    };
    var dotCls = "tl-dot " + (dotKnown[st] || "dot-buoc-cho");
    var maBuoc = step.ma || ("b" + idx);
    var stepKey = (maDa || "du-an") + ":" + maBuoc;
    var isOpen = Boolean(state.expandedSteps[stepKey]);
    var isLate = Boolean(step.bi_tre);

    var codePart = (step.ma && step.ma !== step.ten)
      ? ('<span class="tl-step-code">' + esc(step.ma) + "</span> ")
      : "";
    var rightChips = [];
    if (step.cong) {
      rightChips.push('<span class="tag-chip">Cổng ' + esc(step.cong) + "</span>");
    }
    if (step.nguoi) {
      rightChips.push('<span class="tag-chip">Người: ' + esc(step.nguoi) + "</span>");
    }
    if (isLate && step.tre_nhan) {
      rightChips.push('<span class="badge badge-step-late">' + esc(step.tre_nhan) + "</span>");
    }
    rightChips.push(renderStepStatusBadge(step));

    var dkTxt = step.du_kien_gio || "—";
    var ttTxt = step.thuc_te_gio || "—";
    var hoursLine = '<span class="step-hours-line">dự kiến <span class="num">' + esc(dkTxt) +
      '</span> · thực tế <span class="num">' + esc(ttTxt) + "</span></span>";

    var truc = ganttTruc || {};
    var moc = truc.moc_gio || [];
    var gridHtml = "";
    for (var m = 0; m < moc.length; m++) {
      var mp = Number(moc[m].pct || 0);
      if (mp > 0 && mp < 100) {
        gridHtml += '<span class="gantt-grid-line" style="left:' + mp + '%"></span>';
      }
    }
    var g = step.gantt || {};
    var dkBarHtml = g.co_du_kien
      ? ('<div class="gantt-bar-dk" style="left:' + Number(g.dk_left_pct || 0) + "%;width:" + Number(g.dk_width_pct || 0) + '%"></div>')
      : "";
    var ttBarCls = "gantt-bar-tt st-" + esc(st) + (isLate ? " is-late" : "");
    var ttBarHtml = g.co_thuc_te
      ? ('<div class="' + ttBarCls + '" style="left:' + Number(g.tt_left_pct || 0) + "%;width:" + Number(g.tt_width_pct || 0) + '%"></div>')
      : "";
    var nowLineHtml = (truc.hien_tai_pct !== undefined && truc.hien_tai_pct !== null)
      ? ('<span class="gantt-vline-now" style="left:' + Number(truc.hien_tai_pct) + '%"></span>')
      : "";
    var hanLineHtml = (truc.han_co && truc.han_pct !== undefined && truc.han_pct !== null)
      ? ('<span class="gantt-vline-han" style="left:' + Number(truc.han_pct) + '%"></span>')
      : "";
    var laneHtml = '<div class="gantt-lane" aria-hidden="true">' +
      gridHtml + dkBarHtml + ttBarHtml + nowLineHtml + hanLineHtml + "</div>";

    var runBox = "";
    if (st === "dang-chay") {
      var tranVal = Number(step.tran_phut || 40);
      var phutVal = Number(step.chay_phut || 0);
      var phutInt = Math.round(phutVal);
      var tranInt = Math.round(tranVal);
      var pct = tranVal > 0 ? Math.min(100, Math.max(4, Math.round((phutVal / tranVal) * 100))) : 0;
      var fillCls = pct >= 95 ? "progress-fill over-limit" : (pct >= 80 ? "progress-fill near-limit" : "progress-fill");
      var runTicket = step.phieu_dang_chay || "";
      var ticketHtml = runTicket
        ? ('<a href="/phieu/' + encodeURIComponent(runTicket) + '">' + esc(runTicket) + "</a>")
        : "Đang chạy";
      var nhipTxt = step.nhip_cuoi || "Đang chạy, chưa có nhịp mới…";
      runBox =
        '<div class="tl-step-run">' +
        '<div class="work-top">' +
        '<div class="work-ticket">' + ticketHtml + "</div>" +
        '<div class="work-time">' + phutInt + " phút / " + tranInt + "p</div>" +
        "</div>" +
        '<div class="progress-track"><div class="' + fillCls + '" style="width:' + pct + '%"></div></div>' +
        '<div class="nhip-line">' + esc(nhipTxt) + "</div>" +
        "</div>";
    }

    var tickets = step.phieu_chi_tiet || [];
    var ticketsHtml = tickets.length === 0
      ? '<p class="empty" style="margin:4px 0 0">Chưa gắn phiếu.</p>'
      : ('<div class="step-ticket-list">' + tickets.map(function (t) {
          var gd = t.giai_doan || "";
          var bHtml = "";
          if (gd === "xong") {
            bHtml = t.dat
              ? ('<span class="badge tt-xong">đạt (' + esc(t.trang_thai || "xong") + ")</span>")
              : ('<span class="badge tt-loi">không đạt (' + esc(t.trang_thai || "loi") + ")</span>");
          } else if (gd === "dang") {
            bHtml = '<span class="badge tt-chay">đang chạy</span>';
          } else if (gd === "moi") {
            bHtml = '<span class="badge may-ranh">đang chờ</span>';
          } else {
            bHtml = '<span class="badge may-ranh">' + esc(t.trang_thai === "cho-claude" ? "chờ Claude" : "chưa tạo") + "</span>";
          }
          var extraTime = "";
          if (gd === "dang") {
            extraTime = '<span class="num">' + Math.round(Number(t.phut || 0)) + "p / " + Math.round(Number(t.tran_phut || 40)) + "p</span>";
          } else if (gd === "xong") {
            extraTime = '<span class="num">' + Number(t.phut || 0).toFixed(1) + "p</span>";
          }
          var gateTag = t.la_cong ? ' <span class="tag-chip">cổng</span>' : "";
          var nhipLine = t.nhip ? ('<div class="nhip-line" style="width:100%">' + esc(t.nhip) + "</div>") : "";
          return '<div class="step-ticket-item">' +
            '<div><a class="ticket-main-link" href="' + esc(t.ket_qua_url || ("/phieu/" + encodeURIComponent(t.phieu || ""))) + '">' + esc(t.phieu || "") + "</a>" + gateTag + "</div>" +
            '<div class="ticket-tags">' + bHtml + '<span class="tag-chip">' + esc(t.may || "—") + "</span>" + extraTime + "</div>" +
            nhipLine +
            "</div>";
        }).join("") + "</div>");

    var logs = step.log_cuoi || [];
    var logHtml = logs.length === 0
      ? '<p class="empty" style="margin:4px 0 0">Chưa có log hay dòng nhịp.</p>'
      : ('<pre class="ket-qua step-log">' + esc(logs.join("\n")) + "</pre>");

    var kqList = step.ket_qua_list || [];
    var kqHtml = kqList.length === 0
      ? '<p class="empty" style="margin:4px 0 0">Chưa có KET-QUA.md.</p>'
      : kqList.map(function (kq) {
          var badgeKq = kq.dat
            ? '<span class="badge tt-xong">Đạt</span>'
            : '<span class="badge tt-loi">KHÔNG đạt</span>';
          return '<details class="kq-details"><summary><span>' + esc(kq.phieu || "") + "</span>" + badgeKq + "</summary>" +
            '<pre class="ket-qua">' + esc(kq.noi_dung || "") + "</pre></details>";
        }).join("");

    var imgs = step.anh_thu_nho || [];
    var imgHtml = imgs.length === 0
      ? '<p class="empty" style="margin:4px 0 0">Chưa có ảnh bằng chứng.</p>'
      : ('<div class="thumb-grid">' + imgs.map(function (im) {
          return '<a class="thumb-card" href="' + esc(im.url || "") + '" target="_blank" rel="noopener">' +
            '<img src="' + esc(im.url || "") + '" alt="' + esc((im.phieu || "") + " " + (im.ten || "")) + '" loading="lazy">' +
            '<div class="thumb-cap">' + esc((im.phieu ? (im.phieu + " · ") : "") + (im.ten || "")) + "</div>" +
            "</a>";
        }).join("") + "</div>");

    var stepCls = "tl-step gantt-step" + (isLate ? " is-step-late" : "");
    return '<div class="' + stepCls + '">' +
      '<div class="tl-step-box">' +
      '<div class="gantt-row-main">' +
      '<button type="button" class="tl-step-toggle" data-toggle-step="' + esc(stepKey) + '" aria-expanded="' + (isOpen ? "true" : "false") + '">' +
      '<span class="gantt-step-top">' +
      '<span class="tl-step-name"><span class="' + dotCls + '" aria-hidden="true"></span>' + codePart + esc(step.ten || maBuoc) + "</span>" +
      '<span class="tl-step-right">' + rightChips.join("") + "</span>" +
      "</span>" +
      hoursLine +
      "</button>" +
      laneHtml +
      "</div>" +
      runBox +
      '<div class="tl-step-detail" data-detail-step="' + esc(stepKey) + '"' + (isOpen ? "" : " hidden") + ">" +
      '<div class="step-subhead">Các phiếu (' + tickets.length + ")</div>" + ticketsHtml +
      '<div class="step-subhead">30 dòng cuối log / nhịp (' + logs.length + ")</div>" + logHtml +
      '<div class="step-subhead">KET-QUA (' + kqList.length + ")</div>" + kqHtml +
      '<div class="step-subhead">Ảnh thu nhỏ (' + imgs.length + ")</div>" + imgHtml +
      "</div></div></div>";
  }

  function renderGanttHead(truc) {
    var t = truc || {};
    var leg = [
      '<span class="gantt-leg-item"><span class="gantt-swatch-dk" aria-hidden="true"></span>dự kiến</span>',
      '<span class="gantt-leg-item"><span class="gantt-swatch-tt" aria-hidden="true"></span>thực tế</span>',
      '<span class="gantt-leg-item"><span class="gantt-swatch-tre" aria-hidden="true"></span>trễ &gt;15p</span>'
    ];
    if (t.hien_tai_gio) {
      leg.push(
        '<span class="gantt-leg-item gantt-leg-now"><span class="gantt-swatch-now" aria-hidden="true"></span>Hiện tại <span class="num">' +
        esc(t.hien_tai_gio) + "</span>" + (t.hien_tai_ghim ? " (ngoài khung)" : "") + "</span>"
      );
    }
    if (t.han_co) {
      leg.push(
        '<span class="gantt-leg-item gantt-leg-han"><span class="gantt-swatch-han" aria-hidden="true"></span>Hạn <span class="num">' +
        esc(t.han_nhan || "") + "</span>" + (t.han_ghim ? " (ghim mép)" : "") + "</span>"
      );
    }
    var ticks = t.moc_gio || [];
    var tickHtml = "";
    for (var k = 0; k < ticks.length; k++) {
      var tk = ticks[k];
      var pct = Number(tk.pct || 0);
      var tCls = "gantt-tick" + (pct <= 5 ? " is-left" : (pct >= 95 ? " is-right" : ""));
      tickHtml += '<span class="' + tCls + '" style="left:' + pct + '%">' + esc(tk.gio || "") + "</span>";
    }
    var nowMk = (t.hien_tai_pct !== undefined && t.hien_tai_pct !== null)
      ? ('<span class="gantt-axis-now" style="left:' + Number(t.hien_tai_pct) + '%" title="Hiện tại ' + esc(t.hien_tai_gio || "") + '"></span>')
      : "";
    var hanMk = (t.han_co && t.han_pct !== undefined && t.han_pct !== null)
      ? ('<span class="gantt-axis-han" style="left:' + Number(t.han_pct) + '%" title="Hạn ' + esc(t.han_nhan || "") + '"></span>')
      : "";
    return '<div class="gantt-head-row">' +
      '<div class="gantt-legend">' + leg.join("") + "</div>" +
      '<div class="gantt-axis" aria-hidden="true">' + tickHtml + nowMk + hanMk + "</div>" +
      "</div>";
  }

  function renderProjectsTab(data) {
    var projects = data.du_an || [];
    if (projects.length === 0) {
      return '<section class="card"><p class="empty">Chưa có dự án nào trong hang-doi/du-an/*.json.</p></section>';
    }
    var out = [];
    for (var i = 0; i < projects.length; i++) {
      var p = projects[i];
      var maDa = p.ma || ("du-an-" + i);
      var hanCls = p.qua_han ? "badge may-do" : "badge may-ranh";
      var hanTxt = p.han_con_lai || "Chưa đặt hạn";
      var metaLine = p.han_hien_thi && p.han_hien_thi !== "—"
        ? ('<div class="meta" style="margin-bottom:10px">Mã: <code>' + esc(maDa) + '</code> · Hạn: <span class="num">' + esc(p.han_hien_thi) + "</span></div>")
        : ('<div class="meta" style="margin-bottom:10px">Mã: <code>' + esc(maDa) + "</code></div>");
      var etaHtml = "";
      if (p.du_kien_xong_cau) {
        var lech = Number(p.du_kien_lech_phut || 0);
        var etaCls = "du-an-eta " + (lech > 15 ? "is-late" : (lech > 0 ? "is-slightly-late" : "is-on-time"));
        etaHtml = '<div class="' + etaCls + '">' + esc(p.du_kien_xong_cau) + "</div>";
      }
      var steps = p.buoc || [];
      var truc = p.gantt_truc || {};
      var stepsHtml = steps.length === 0
        ? '<p class="empty">Chưa khai báo các bước.</p>'
        : ('<div class="gantt-table">' + renderGanttHead(truc) +
           '<div class="timeline-list" style="gap:8px">' + steps.map(function (s, idx) {
             return renderProjectStep(maDa, s, idx, truc);
           }).join("") + "</div></div>");
      out.push(
        '<section class="card du-an-card">' +
        '<div class="du-an-head">' +
        '<h2 class="du-an-title">' + esc(p.ten || maDa) + "</h2>" +
        '<span class="' + hanCls + '">' + esc(hanTxt) + "</span>" +
        "</div>" +
        metaLine +
        etaHtml +
        '<div class="du-an-summary">' + esc(p.tom_tat_buoc || "") + "</div>" +
        stepsHtml +
        "</section>"
      );
    }
    return out.join("");
  }

  function renderQualityTab(data) {
    var projects = data.du_an || [];
    if (projects.length === 0) {
      return '<section class="card"><p class="empty">Chưa có dự án nào trong hang-doi/du-an/*.json.</p></section>';
    }
    var out = [];
    for (var i = 0; i < projects.length; i++) {
      var p = projects[i];
      var cl = p.chat_luong || {};
      var dm9 = cl.do_muc_9 || {};
      var chiSo = dm9.chi_so || [];

      var muc9HeadMeta = "";
      if (!dm9.chua_do && dm9.tep) {
        var linkTep = dm9.tep_url
          ? ('<a href="' + esc(dm9.tep_url) + '" target="_blank" rel="noopener">' + esc(dm9.tep) + "</a>")
          : esc(dm9.tep);
        muc9HeadMeta = '<div class="meta" style="margin-bottom:8px">Tệp mới nhất: ' + linkTep + " · " + esc(dm9.cap_nhat_hien_thi || "—") + "</div>";
      }

      var muc9Body = "";
      if (dm9.chua_do || chiSo.length === 0) {
        muc9Body = '<div class="cl-chua-do">Chưa đo</div>';
      } else {
        muc9Body = muc9HeadMeta +
          '<table class="muc9-table"><thead><tr>' +
          '<th class="col-ten">Tên</th><th class="col-nguong">Ngưỡng</th><th class="col-do">Số đo tệ nhất</th><th class="col-kq">Đạt / Đỏ</th>' +
          "</tr></thead><tbody>" +
          chiSo.map(function (r) {
            var tenTxt = (r.ma ? (r.ma + " · ") : "") + (r.ten || "");
            var badgeKq = r.dat === true
              ? '<span class="badge tt-xong">Đạt</span>'
              : (r.dat === false ? '<span class="badge tt-loi">Đỏ</span>' : '<span class="badge may-ranh">—</span>');
            return "<tr>" +
              '<td class="col-ten">' + esc(tenTxt) + "</td>" +
              '<td class="col-nguong num">' + esc(r.nguong || "—") + "</td>" +
              '<td class="col-do num">' + esc(r.te_nhat || "—") + "</td>" +
              '<td class="col-kq">' + badgeKq + "</td>" +
              "</tr>";
          }).join("") +
          "</tbody></table>";
      }

      var anhGhep = cl.anh_ghep || [];
      var ghepBody = anhGhep.length === 0
        ? '<p class="empty">Chưa có ảnh ghép khung | bản dựng.</p>'
        : ('<div class="ghep-grid">' + anhGhep.map(function (im) {
            return '<a class="ghep-card" href="' + esc(im.url || "") + '" target="_blank" rel="noopener">' +
              '<img src="' + esc(im.url || "") + '" alt="' + esc((im.phieu || "") + " " + (im.ten || "")) + '" loading="lazy">' +
              '<div class="ghep-meta"><div class="ghep-phieu">' + esc(im.phieu || im.ten || "") + "</div>" +
              '<div class="ghep-gio">' + esc(im.gio_ngan || im.gio_hien_thi || "—") + "</div></div>" +
              "</a>";
          }).join("") + "</div>");

      var cham = cl.cham || [];
      var chamBody = cham.length === 0
        ? '<p class="empty">Chưa có dữ liệu chấm.</p>'
        : ('<table class="cham-table"><thead><tr>' +
          "<th>RC</th><th>Người</th><th>Điểm</th><th>Ghi chú</th><th>Tệp</th>" +
          "</tr></thead><tbody>" +
          cham.map(function (c) {
            var tepCell = c.tep_url
              ? ('<a href="' + esc(c.tep_url) + '" target="_blank" rel="noopener">' + esc(c.tep || "Xem tệp") + "</a>")
              : (c.tep ? ("<code>" + esc(c.tep) + "</code>") : "—");
            return "<tr>" +
              '<td data-label="RC">' + esc(c.rc || "—") + "</td>" +
              '<td data-label="Người">' + esc(c.nguoi || "—") + "</td>" +
              '<td data-label="Điểm" class="num"><strong>' + esc(c.diem || "—") + "</strong></td>" +
              '<td data-label="Ghi chú">' + esc(c.ghi_chu || "—") + "</td>" +
              '<td data-label="Tệp">' + tepCell + "</td>" +
              "</tr>";
          }).join("") +
          "</tbody></table>");

      out.push(
        '<section class="card chat-luong-card">' +
        '<div class="du-an-head"><h2 class="du-an-title">' + esc(p.ten || p.ma || "Dự án") + "</h2>" +
        '<span class="meta"><code>' + esc(p.ma || "") + "</code></span></div>" +
        '<div class="cl-section"><h3>Bảng mức 9</h3>' + muc9Body + "</div>" +
        '<div class="cl-section"><h3>Ảnh ghép khung | bản dựng (' + anhGhep.length + ")</h3>" + ghepBody + "</div>" +
        '<div class="cl-section"><h3>Bảng chấm (' + cham.length + ")</h3>" + chamBody + "</div>" +
        "</section>"
      );
    }
    return out.join("");
  }

  function applyDataToDom(data) {
    state.data = data;
    var olderEl = document.querySelector("#panel-phieu .older-details");
    if (olderEl) state.olderOpen = olderEl.open;

    var heroEl = document.getElementById("hero-headline");
    if (heroEl) heroEl.innerHTML = buildHeroHtml(data);

    var split = splitDone24h(data.xong_gan_nhat || [], data.cap_nhat_luc);
    var subEl = document.getElementById("hero-subline");
    if (subEl) {
      subEl.textContent =
        (data.may || []).length + " máy · " +
        (data.dang_chay || []).length + " đang chạy · " +
        (data.dang_cho || []).length + " đang chờ · " +
        split.d24.length + " xong 24h";
    }

    var syncEl = document.getElementById("sync-meta-text");
    if (syncEl) {
      var rawT = String(data.cap_nhat_hien_thi || "—");
      var shortT = rawT.length >= 19 ? rawT.slice(11, 19) : rawT;
      syncEl.textContent = shortT + " · 15s";
    }
    var dotEl = document.getElementById("live-dot");
    if (dotEl) dotEl.classList.remove("is-stale");

    var errSlot = document.getElementById("sync-err-slot");
    if (errSlot) {
      errSlot.innerHTML = data.loi_dong_bo
        ? ('<div class="err-banner">Lỗi đồng bộ git gần nhất: ' + esc(data.loi_dong_bo) + "</div>")
        : "";
    }

    var clSlot = document.getElementById("can-linh-slot");
    if (clSlot) clSlot.innerHTML = renderCanLinh(data.can_linh || []);

    var cntDuAn = (data.du_an && data.du_an.length) || 0;
    var tabDuAnEl = document.getElementById("tab-lbl-du-an");
    if (tabDuAnEl) tabDuAnEl.textContent = cntDuAn > 0 ? ("Dự án (" + cntDuAn + ")") : "Dự án";

    var cntPhieu = (data.dang_chay || []).length + (data.dang_cho || []).length;
    var tabPhieuEl = document.getElementById("tab-lbl-phieu");
    if (tabPhieuEl) tabPhieuEl.textContent = "Phiếu (" + cntPhieu + ")";

    var nProf = (data.ho_so_may && data.ho_so_may.length) || 0;
    var nMay = (data.may && data.may.length) || 0;
    var cntMay = Math.max(nProf, nMay);
    var tabMayEl = document.getElementById("tab-lbl-may");
    if (tabMayEl) tabMayEl.textContent = "Máy (" + cntMay + ")";

    var duAnEl = document.getElementById("du-an-content-slot");
    if (duAnEl) duAnEl.innerHTML = renderProjectsTab(data);

    var chatLuongEl = document.getElementById("chat-luong-content-slot");
    if (chatLuongEl) chatLuongEl.innerHTML = renderQualityTab(data);

    var cntCc = (data.so_cong_cu && data.so_cong_cu.length) || 0;
    var tabCcEl = document.getElementById("tab-lbl-cong-cu");
    if (tabCcEl) tabCcEl.textContent = "Công cụ (" + cntCc + ")";

    var ovEl = document.getElementById("overview-machines-slot");
    if (ovEl) ovEl.innerHTML = renderOverviewMachines(data);

    var phieuEl = document.getElementById("phieu-content-slot");
    if (phieuEl) phieuEl.innerHTML = renderTicketsTab(data);

    var mayEl = document.getElementById("may-content-slot");
    if (mayEl) mayEl.innerHTML = renderProfilesTab(data);

    var ccEl = document.getElementById("cong-cu-content-slot");
    if (ccEl) ccEl.innerHTML = renderToolsTab(data);
  }

  function findAttrEl(attr, val) {
    var list = document.querySelectorAll("[" + attr + "]");
    for (var i = 0; i < list.length; i++) {
      if (list[i].getAttribute(attr) === val) return list[i];
    }
    return null;
  }

  function toggleStepDetail(stepKey) {
    if (!stepKey) return;
    state.expandedSteps[stepKey] = !state.expandedSteps[stepKey];
    var open = Boolean(state.expandedSteps[stepKey]);
    var detail = findAttrEl("data-detail-step", stepKey);
    var btn = findAttrEl("data-toggle-step", stepKey);
    if (detail) {
      if (open) detail.removeAttribute("hidden");
      else detail.setAttribute("hidden", "");
    }
    if (btn) {
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    }
  }

  function toggleMachineDetail(ma) {
    if (!ma) return;
    state.expandedMachines[ma] = !state.expandedMachines[ma];
    var open = Boolean(state.expandedMachines[ma]);
    var detail = findAttrEl("data-detail-may", ma);
    var btn = findAttrEl("data-toggle-may", ma);
    if (detail) {
      if (open) detail.removeAttribute("hidden");
      else detail.setAttribute("hidden", "");
    }
    if (btn) {
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      btn.textContent = open ? "Thu gọn" : "Chi tiết";
    }
  }

  document.addEventListener("click", function (ev) {
    var target = ev.target;
    if (!target || !target.closest) return;

    var copyBtn = target.closest(".btn-copy");
    if (copyBtn) {
      ev.preventDefault();
      copyText(copyBtn.getAttribute("data-copy") || "", copyBtn);
      return;
    }

    var tabBtn = target.closest(".seg-btn[data-tab]");
    if (tabBtn) {
      ev.preventDefault();
      setTab(tabBtn.getAttribute("data-tab"), true);
      return;
    }

    var stepBtn = target.closest("[data-toggle-step]");
    if (stepBtn) {
      ev.preventDefault();
      toggleStepDetail(stepBtn.getAttribute("data-toggle-step"));
      return;
    }

    var jumpBtn = target.closest("[data-jump-filter]");
    if (jumpBtn) {
      ev.preventDefault();
      state.machineFilter = jumpBtn.getAttribute("data-jump-filter") || "tat-ca";
      if (state.data) {
        var phieuEl = document.getElementById("phieu-content-slot");
        if (phieuEl) phieuEl.innerHTML = renderTicketsTab(state.data);
      }
      setTab("phieu", true);
      return;
    }

    var filterBtn = target.closest("[data-filter-may]");
    if (filterBtn) {
      ev.preventDefault();
      state.machineFilter = filterBtn.getAttribute("data-filter-may") || "tat-ca";
      if (state.data) {
        var slot = document.getElementById("phieu-content-slot");
        if (slot) slot.innerHTML = renderTicketsTab(state.data);
      }
      return;
    }

    var toggleBtn = target.closest("[data-toggle-may]");
    if (toggleBtn) {
      ev.preventDefault();
      toggleMachineDetail(toggleBtn.getAttribute("data-toggle-may"));
      return;
    }

    var card = target.closest("[data-may-card]");
    if (card && !target.closest("a, button, code, .may-detail")) {
      toggleMachineDetail(card.getAttribute("data-may-card"));
    }
  });

  var inFlight = false;
  function fetchLatest() {
    if (inFlight) return;
    inFlight = true;
    fetch("/api/trang-thai", { cache: "no-store", headers: { Accept: "application/json" } })
      .then(function (resp) {
        if (!resp.ok) throw new Error("HTTP " + resp.status);
        return resp.json();
      })
      .then(function (fresh) {
        applyDataToDom(fresh);
      })
      .catch(function () {
        var dotEl = document.getElementById("live-dot");
        if (dotEl) dotEl.classList.add("is-stale");
      })
      .finally(function () {
        inFlight = false;
      });
  }

  setInterval(fetchLatest, REFRESH_MS);
  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "visible") fetchLatest();
  });
})();
"""


def _esc(val) -> str:
    return html.escape(str(val if val is not None else ""), quote=True)


def _safe_inline_json(data: dict) -> str:
    """Chuyển dữ liệu sang JSON an toàn để nhúng vào thẻ script (lược bỏ trường ket_qua nặng và chống đóng thẻ sớm)."""
    slim = dict(data)
    slim_done = []
    for item in data.get("xong_gan_nhat") or []:
        d = dict(item)
        d.pop("ket_qua", None)
        slim_done.append(d)
    slim["xong_gan_nhat"] = slim_done
    raw = json.dumps(slim, ensure_ascii=False)
    return raw.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")


def _split_done_24h(done_list: list[dict], now_iso: str | None) -> tuple[list[dict], list[dict]]:
    """Tách danh sách phiếu đã xong thành nhóm trong 24h qua và nhóm trước 24h."""
    now_dt = parse_iso_datetime(now_iso) or now_local()
    within_24h: list[dict] = []
    older: list[dict] = []
    for item in done_list:
        done_dt = parse_iso_datetime(item.get("xong_luc"))
        if done_dt is None or (now_dt - done_dt).total_seconds() <= 86400.0:
            within_24h.append(item)
        else:
            older.append(item)
    return within_24h, older


def _build_hero_headline_html(machines: list[dict], can_linh: list[dict]) -> str:
    """Sinh câu trạng thái lớn trên cùng trang để đọc nhanh trong 5 giây (vd: '3 máy chạy, 1 cần anh')."""
    cnt_run = 0
    cnt_idle = 0
    cnt_stuck = 0
    cnt_silent = 0
    for m in machines:
        if m.get("qua_30_phut") or m.get("trang_thai_may") == "im-lang":
            cnt_silent += 1
        elif m.get("trang_thai_may") == "chay":
            cnt_run += 1
        elif m.get("trang_thai_may") == "ket":
            cnt_stuck += 1
        else:
            cnt_idle += 1

    if can_linh:
        return f'{_esc(f"{cnt_run} máy chạy, ")}<span class="need-you">{_esc(f"{len(can_linh)} cần anh")}</span>'
    if not machines:
        return "Chưa ghi nhận máy hoạt động"
    if cnt_stuck > 0 and cnt_silent > 0:
        return _esc(f"{cnt_run} máy chạy, {cnt_stuck} kẹt · {cnt_silent} im lặng")
    if cnt_stuck > 0:
        return _esc(f"{cnt_run} máy chạy, {cnt_stuck} máy kẹt")
    if cnt_silent > 0:
        return _esc(f"{cnt_run} máy chạy, {cnt_silent} im lặng")
    if cnt_idle > 0:
        return _esc(f"{cnt_run} máy chạy, {cnt_idle} máy rảnh")
    return _esc(f"{cnt_run} máy đang chạy")


def _render_can_linh_block(can_linh: list[dict]) -> str:
    """Sinh khối đỏ 'Cần anh làm' trên cùng trang kèm nút chép lệnh (ẩn hoàn toàn khi rỗng)."""
    if not can_linh:
        return ""
    items_html = []
    for cl in can_linh:
        phieu = cl.get("phieu") or cl.get("id") or ""
        href = cl.get("ket_qua_url") or f"/phieu/{urllib.parse.quote(phieu)}"
        lenh = (cl.get("lenh") or "").strip()
        viec = cl.get("viec") or ""
        copy_payload = lenh or viec or phieu
        gio_txt = cl.get("gio_hien_thi") or ""
        gio_html = f' <span class="meta">· {_esc(gio_txt)}</span>' if gio_txt else ""
        lenh_html = f'<code class="cmd-paste">{_esc(lenh)}</code>' if lenh else ""
        items_html.append(
            '<div class="can-linh-item">'
            '<div class="can-linh-meta">'
            f'<strong>{_esc(cl.get("may") or "máy")}</strong> · '
            f'<a href="{_esc(href)}">{_esc(phieu)}</a>'
            f"{gio_html}"
            "</div>"
            f'<div class="can-linh-viec">{_esc(viec)}</div>'
            '<div class="cmd-row">'
            f"{lenh_html}"
            f'<button type="button" class="btn-copy" data-label="Chép lệnh" data-copy="{_esc(copy_payload)}">Chép lệnh</button>'
            "</div>"
            "</div>"
        )
    return (
        '<section class="can-linh-box">'
        '<div class="can-linh-head">'
        '<span class="status-dot dot-im-lang" aria-hidden="true"></span>'
        f"<h2>Cần anh làm ({len(can_linh)})</h2>"
        "</div>"
        + "".join(items_html)
        + "</section>"
    )


def _render_usage_bar(label: str, total_gb: float, free_gb: float, warn_low_free: bool = False) -> str:
    """Sinh thanh tiến độ dung lượng RAM / ổ đĩa."""
    tot = max(0.0, float(total_gb or 0.0))
    free = max(0.0, float(free_gb or 0.0))
    used = max(0.0, tot - free)
    pct = min(100, max(0, int(round((used / tot) * 100.0)))) if tot > 0 else 0
    fill_cls = "bar-fill warn" if (warn_low_free or pct >= 90) else "bar-fill"
    return (
        '<div class="bar-row">'
        '<div class="bar-label-row">'
        f"<strong>{_esc(label)}</strong>"
        f'<span class="meta num">trống {free:.1f} / {tot:.1f} GB ({pct}%)</span>'
        "</div>"
        f'<div class="bar-track"><div class="{fill_cls}" style="width:{pct}%"></div></div>'
        "</div>"
    )


def _render_overview_machines_section(data: dict) -> str:
    """Sinh lưới thẻ máy cho tab Tổng quan (chấm 4 màu, thanh phút/trần, nhịp cuối, bấm mở chi tiết)."""
    machines = data.get("may") or []
    if not machines:
        return '<section class="card"><p class="empty">Chưa ghi nhận máy nào.</p></section>'

    run_by_ticket = {item["phieu"]: item for item in (data.get("dang_chay") or []) if item.get("phieu")}
    prof_by_may = {p["ma_may"]: p for p in (data.get("ho_so_may") or []) if p.get("ma_may")}

    cards_html = []
    for m in machines:
        ma = m.get("may") or "may"
        is_red = bool(m.get("qua_30_phut")) or m.get("trang_thai_may") == "im-lang"
        tt_may = "im-lang" if is_red else (m.get("trang_thai_may") or "ranh")
        dot_cls = (
            "dot-chay"
            if tt_may == "chay"
            else ("dot-ket" if tt_may == "ket" else ("dot-im-lang" if tt_may == "im-lang" else "dot-ranh"))
        )
        if is_red:
            badge_html = '<span class="qua-han">Im lặng &gt; 30 phút</span>'
        elif tt_may == "chay":
            badge_html = '<span class="badge may-chay">Đang chạy</span>'
        elif tt_may == "ket":
            badge_html = f'<span class="badge may-ket">Kẹt ({_esc(m.get("ket_trang_thai") or "lỗi")})</span>'
        else:
            badge_html = '<span class="badge may-ranh">Rảnh</span>'

        disk_badge = ' <span class="badge may-do">Ổ C &lt; 10GB</span>' if m.get("canh_bao_o_c") else ""
        prof = prof_by_may.get(ma)
        vai_tro = m.get("vai_tro") or (prof or {}).get("vai_tro") or "Máy thợ hàng đợi"

        dang_phieu = m.get("dang_lam_phieu") or ""
        ket_phieu = m.get("ket_phieu") or ""
        if dang_phieu:
            r_item = run_by_ticket.get(dang_phieu) or {}
            phut_val = float(m.get("dang_lam_phut") or r_item.get("chay_phut") or 0.0)
            phut_so = int(round(phut_val))
            tran_val = float(r_item.get("tran_phut") or 40.0)
            tran_so = int(round(tran_val))
            pct = min(100, max(4, int(round((phut_val / tran_val) * 100.0)))) if tran_val > 0 else 0
            pfill_cls = (
                "progress-fill over-limit"
                if pct >= 95
                else ("progress-fill near-limit" if pct >= 80 else "progress-fill")
            )
            extra_cnt = int(m.get("dang_chay_so_luong") or 1)
            extra_txt = f" (+{extra_cnt - 1})" if extra_cnt > 1 else ""
            href_run = f"/phieu/{urllib.parse.quote(dang_phieu)}"
            nhip_txt = m.get("nhip") or "Mới nhận phiếu, đang chờ nhịp báo cáo…"
            canh_nen_txt = m.get("nhan_canh_nen") or r_item.get("nhan_canh_nen") or ""
            canh_nen_row = (
                f'<div style="margin:6px 0 4px"><span class="badge tt-dung badge-canh-nen">{_esc(canh_nen_txt)}</span></div>'
                if canh_nen_txt
                else ""
            )
            work_html = (
                '<div class="may-work-box">'
                '<div class="work-top">'
                f'<div class="work-ticket"><a href="{_esc(href_run)}">{_esc(dang_phieu)}</a>{_esc(extra_txt)}</div>'
                f'<div class="work-time">{phut_so} phút / {tran_so}p</div>'
                "</div>"
                f"{canh_nen_row}"
                f'<div class="progress-track"><div class="{pfill_cls}" style="width:{pct}%"></div></div>'
                f'<div class="nhip-line">{_esc(nhip_txt)}</div>'
                "</div>"
            )
        elif ket_phieu:
            ket_href = f"/phieu/{urllib.parse.quote(ket_phieu)}"
            ket_tt = m.get("ket_trang_thai") or "lỗi"
            ket_ly_do = m.get("ket_ly_do") or ""
            work_html = (
                '<div class="may-work-box">'
                f'<div class="ket-note">Kẹt ({_esc(ket_tt)}) '
                f'<a href="{_esc(ket_href)}">{_esc(ket_phieu)}</a>: {_esc(ket_ly_do)}</div>'
                f'<div class="nhip-line">Nhịp cuối: {_esc(m.get("cach_day") or "—")}</div>'
                "</div>"
            )
        else:
            ev_kind = m.get("su_kien_cuoi") or ""
            ev_ticket = m.get("phieu_cuoi") or ""
            if ev_kind in ("nhan", "xong") and ev_ticket:
                verb = "nhận" if ev_kind == "nhan" else "xong"
                t_href = f"/phieu/{urllib.parse.quote(ev_ticket)}"
                ago = m.get("cach_day") or ""
                ago_part = f" · {_esc(ago)}" if ago and ago != "—" else ""
                idle_body = f'Mới {verb} <a href="{_esc(t_href)}">{_esc(ev_ticket)}</a>{ago_part}'
            else:
                idle_body = "Chưa nhận việc"
            work_html = f'<div class="may-work-box"><div class="idle-note">{idle_body}</div></div>'

        if prof and isinstance(prof.get("ram"), dict):
            ram_info = prof["ram"]
            res_txt = f"RAM trống {float(ram_info.get('trong_gb') or 0):.1f}/{float(ram_info.get('tong_gb') or 0):.1f} GB"
            if prof.get("o_c_trong_gb") is not None:
                res_txt += f" · Ổ C trống {float(prof['o_c_trong_gb']):.1f} GB"
        else:
            res_txt = "Chưa có hồ sơ RAM/ổ"

        tk24 = (prof or {}).get("thong_ke_24h")
        tk_txt = f"Xong {int(tk24.get('xong') or 0)} · Lỗi {int(tk24.get('loi') or 0)}" if isinstance(tk24, dict) else "—"
        win_row = (
            f'<div class="detail-row"><span class="meta">Windows</span><code>{_esc(prof["ten_windows"])}</code></div>'
            if prof and prof.get("ten_windows")
            else ""
        )
        focus_ticket = dang_phieu or ket_phieu or (m.get("phieu_cuoi") or "")
        focus_link = (
            f'<a class="btn-subtle" href="/phieu/{urllib.parse.quote(focus_ticket)}">Xem phiếu {_esc(focus_ticket)}</a>'
            if focus_ticket
            else ""
        )
        card_cls = "may-card is-clickable warn-disk" if m.get("canh_bao_o_c") else "may-card is-clickable"

        cards_html.append(
            f'<article class="{card_cls}" data-may-card="{_esc(ma)}">'
            '<div class="may-card-head">'
            '<div class="may-title-group">'
            f'<span class="status-dot {dot_cls}" aria-hidden="true"></span>'
            f'<h3 class="may-name">{_esc(ma)}</h3>{disk_badge}'
            "</div>"
            f"{badge_html}"
            "</div>"
            f'<p class="vai-tro">{_esc(vai_tro)}</p>'
            f"{work_html}"
            '<div class="may-card-foot">'
            f'<span class="meta">{_esc(m.get("cach_day") or "—")}</span>'
            f'<button type="button" class="expand-btn" data-toggle-may="{_esc(ma)}" aria-expanded="false">Chi tiết</button>'
            "</div>"
            f'<div class="may-detail" data-detail-may="{_esc(ma)}" hidden>'
            '<div class="detail-grid">'
            f'<div class="detail-row"><span class="meta">Lần cuối</span><span class="num">{_esc(m.get("lan_cuoi_hien_thi") or "—")}</span></div>'
            f'<div class="detail-row"><span class="meta">Tài nguyên</span><span>{_esc(res_txt)}</span></div>'
            f'<div class="detail-row"><span class="meta">24h qua</span><span>{_esc(tk_txt)}</span></div>'
            f"{win_row}"
            "</div>"
            '<div class="detail-actions">'
            f'<button type="button" class="btn-subtle" data-jump-filter="{_esc(ma)}">Lọc phiếu {_esc(ma)}</button>'
            f"{focus_link}"
            "</div>"
            "</div>"
            "</article>"
        )

    return '<div class="cards-may">' + "".join(cards_html) + "</div>"


def _render_tickets_section(data: dict) -> str:
    """Sinh nội dung tab Phiếu: thanh lọc theo máy + Đang chạy + Đang chờ + Xong 24h."""
    running = data.get("dang_chay") or []
    waiting = data.get("dang_cho") or []
    done_list = data.get("xong_gan_nhat") or []
    done_24h, done_older = _split_done_24h(done_list, data.get("cap_nhat_luc"))

    seen_m: list[str] = []
    for m in data.get("may") or []:
        if m.get("may") and m["may"] not in seen_m:
            seen_m.append(m["may"])
    for w in waiting:
        if w.get("may") and w["may"] not in seen_m:
            seen_m.append(w["may"])

    pills = ['<button type="button" class="filter-pill is-active" data-filter-may="tat-ca">Tất cả</button>']
    for mn in seen_m:
        pills.append(f'<button type="button" class="filter-pill" data-filter-may="{_esc(mn)}">{_esc(mn)}</button>')
    filter_html = '<div class="filter-bar" role="group" aria-label="Lọc theo máy">' + "".join(pills) + "</div>"

    if running:
        rows_run = []
        for item in running:
            tran_val = float(item.get("tran_phut") or 40.0)
            phut_val = float(item.get("chay_phut") or 0.0)
            pct = min(100, max(4, int(round((phut_val / tran_val) * 100.0)))) if tran_val > 0 else 0
            de_div = f'<div class="ticket-desc">{_esc(item["de"])}</div>' if item.get("de") else ""
            nhip_div = f'<div class="nhip-line">{_esc(item["nhip"])}</div>' if item.get("nhip") else ""
            canh_nen_badge = (
                f'<span class="badge tt-dung badge-canh-nen">{_esc(item["nhan_canh_nen"])}</span>'
                if item.get("nhan_canh_nen")
                else ""
            )
            rows_run.append(
                '<div class="ticket-row">'
                '<div class="ticket-row-head">'
                f'<a class="ticket-main-link" href="{_esc(item["ket_qua_url"])}">{_esc(item["phieu"])}</a>'
                '<div class="ticket-tags">'
                f"{canh_nen_badge}"
                f'<span class="tag-chip">{_esc(item["may"])}</span>'
                f'<span class="tag-chip">{_esc(item["loai"])}</span>'
                f'<span class="num">{_esc(item["chay_bao_lau"])} / {_esc(item["tran_phut"])}p</span>'
                "</div></div>"
                f'<div class="progress-track" style="margin:8px 0 4px"><div class="progress-fill" style="width:{pct}%"></div></div>'
                f"{de_div}{nhip_div}"
                "</div>"
            )
        running_html = '<div class="ticket-list">' + "".join(rows_run) + "</div>"
    else:
        running_html = '<p class="empty">Không có phiếu đang chạy.</p>'

    if waiting:
        rows_wait = []
        for item in waiting:
            rows_wait.append(
                '<div class="ticket-row">'
                '<div class="ticket-row-head">'
                f'<a class="ticket-main-link" href="{_esc(item["ket_qua_url"])}">{_esc(item["phieu"])}</a>'
                '<div class="ticket-tags">'
                f'<span class="tag-chip">{_esc(item["may"])}</span>'
                f'<span class="tag-chip">{_esc(item["loai"])}</span>'
                f'<span class="num">trần {_esc(item["tran_phut"])} phút</span>'
                "</div></div>"
                f'<div class="ticket-desc">{_esc(item.get("de") or "")}</div>'
                "</div>"
            )
        waiting_html = '<div class="ticket-list">' + "".join(rows_wait) + "</div>"
    else:
        waiting_html = '<p class="empty">Không có phiếu đang chờ.</p>'

    def _done_row(item: dict) -> str:
        st = item.get("trang_thai") or "loi"
        badge_cls = f"badge tt-{st}" if st in ("xong", "loi", "dung", "huy") else "badge tt-loi"
        tok_str = f"{int(item.get('tong_token') or 0):,}"
        ly_do = item.get("ly_do_ngan") or ""
        tom_tat = item.get("tom_tat") or ""
        extra = (
            f'<div class="ket-note">{_esc(ly_do)}</div>'
            if ly_do
            else (f'<div class="ticket-sub">{_esc(tom_tat)}</div>' if tom_tat else "")
        )
        return (
            '<div class="ticket-row">'
            '<div class="ticket-row-head">'
            f'<a class="ticket-main-link" href="{_esc(item["ket_qua_url"])}">{_esc(item["phieu"])}</a>'
            '<div class="ticket-tags">'
            f'<span class="{_esc(badge_cls)}">{_esc(st)}</span>'
            f'<span class="tag-chip">{_esc(item["may"])}</span>'
            f'<span class="num">{float(item.get("phut") or 0):.2f} phút · {_esc(tok_str)} tok</span>'
            "</div></div>"
            f'<div class="ticket-sub num">{_esc(item.get("xong_luc_hien_thi") or "—")}</div>'
            f"{extra}"
            "</div>"
        )

    if done_24h:
        done_24_html = '<div class="ticket-list">' + "".join(_done_row(d) for d in done_24h) + "</div>"
    else:
        done_24_html = '<p class="empty">Chưa có phiếu hoàn thành trong 24h qua.</p>'

    older_html = ""
    if done_older:
        older_html = (
            '<details class="older-details">'
            f"<summary>Trước 24h ({len(done_older)})</summary>"
            '<div class="ticket-list">' + "".join(_done_row(d) for d in done_older) + "</div>"
            "</details>"
        )

    tong_xong = int(data.get("tong_xong") or len(done_list))
    return (
        f"{filter_html}"
        f'<section class="card"><h2>Đang chạy ({len(running)})</h2>{running_html}</section>'
        f'<section class="card"><h2>Đang chờ ({len(waiting)})</h2>{waiting_html}</section>'
        '<section class="card">'
        f'<h2>Xong 24h ({len(done_24h)}) <span class="sub-heading">· Xong gần nhất ({len(done_list)}/{tong_xong} phiếu)</span></h2>'
        f"{done_24_html}{older_html}"
        "</section>"
    )


def _render_accounts_card(data: dict) -> str:
    """Sinh thẻ nhỏ 'Tài khoản' ở tab Máy: đếm tài khoản dùng được / hết hạn mức / cần đăng nhập."""
    rows = data.get("tai_khoan_may") or []
    if not rows:
        return '<section class="card accounts-card"><h2>Tài khoản</h2><p class="empty">Chưa có dữ liệu tài khoản.</p></section>'
    items_html = []
    for row in rows:
        ma = _esc(row.get("may") or "may")
        agy_tk = _mask_emails_in_text(str(row.get("agy_tai_khoan") or ""))
        agy_tag = (
            f'<span class="meta">agy: <code>{_esc(agy_tk)}</code></span>'
            if agy_tk and agy_tk != "chua_ro"
            else ""
        )
        dung_duoc = int(row.get("dung_duoc") or 0)
        het_han_muc = int(row.get("het_han_muc") or 0)
        can_dang_nhap = int(row.get("can_dang_nhap") or 0)
        items_html.append(
            '<div class="acc-item">'
            f'<div class="acc-head"><strong>{ma}</strong>{agy_tag}</div>'
            '<div class="acc-stats">'
            f'<span class="acc-ok">{dung_duoc} dùng được</span>'
            f'<span class="acc-warn">{het_han_muc} hết hạn mức</span>'
            f'<span class="acc-err">{can_dang_nhap} cần đăng nhập</span>'
            "</div></div>"
        )
    return '<section class="card accounts-card"><h2>Tài khoản</h2><div class="acc-grid">' + "".join(items_html) + "</div></section>"


def _fmt_int(val) -> str:
    try:
        return f"{int(val):,}"
    except (ValueError, TypeError):
        return _esc(val)


def _render_account_status_pill(tt: str) -> str:
    if tt == "can_dang_nhap":
        return '<span class="status-pill acc-err"><span class="status-dot dot-err"></span>Cần đăng nhập</span>'
    if tt == "het_han_muc":
        return '<span class="status-pill acc-warn"><span class="status-dot dot-warn"></span>Hết hạn mức</span>'
    return '<span class="status-pill acc-ok"><span class="status-dot dot-ok"></span>Dùng được</span>'


def _render_tools_section(data: dict) -> str:
    """Sinh nội dung tab Công cụ: thẻ Tài khoản, Sổ công cụ (sắp cảnh báo lên đầu), Crawler và Zalo."""
    parts = [_render_accounts_card(data)]

    tools = data.get("so_cong_cu") or []
    if not tools:
        parts.append('<section class="card"><h2>Sổ công cụ</h2><p class="empty">Chưa có mục nào trong hang-doi/tai-khoan.json.</p></section>')
    else:
        for grp in tools:
            has_alert = int(grp.get("can_xu_ly") or 0) > 0
            cls = "card tool-block has-alert" if has_alert else "card tool-block"
            rows_html = []
            for row in grp.get("tai_khoan") or []:
                con_lai = row.get("con_lai", "chua_ro")
                con_lai_html = (
                    '<span class="meta">chua_ro</span>'
                    if con_lai == "chua_ro" or con_lai is None
                    else _esc(f"{int(con_lai):,}" if isinstance(con_lai, int) else con_lai)
                )
                reset_val = str(row.get("reset_luc") or "chua_ro").strip()
                reset_html = '<span class="meta">chua_ro</span>' if reset_val == "chua_ro" else _esc(reset_val)
                nguon_val = str(row.get("nguon") or "").strip()
                nguon_html = f' <span class="meta">({_esc(nguon_val)})</span>' if nguon_val else ""
                hs_val = str(row.get("ho_so_chrome") or "").strip()
                hs_html = f"<code>{_esc(hs_val)}</code>" if hs_val else '<span class="meta">—</span>'
                rows_html.append(
                    "<tr>"
                    f"<td><code>{_esc(row.get('email_che') or 'chua_ro')}</code></td>"
                    f"<td><code>{_esc(row.get('may') or 'bat-ky')}</code></td>"
                    f"<td>{hs_html}</td>"
                    f'<td class="num">{_fmt_int(row.get("da_dung_24h") or 0)}</td>'
                    f'<td class="num">{con_lai_html}</td>'
                    f'<td class="num">{reset_html}{nguon_html}</td>'
                    f"<td>{_render_account_status_pill(str(row.get('trang_thai') or 'dung'))}</td>"
                    "</tr>"
                )
            parts.append(
                f'<section class="{cls}">'
                '<div class="tool-head">'
                f"<h2><code>{_esc(grp.get('cong_cu') or 'khac')}</code></h2>"
                '<div class="tool-counts">'
                f'<span class="acc-ok">{int(grp.get("dung_duoc") or 0)} dùng được</span>'
                f'<span class="acc-warn">{int(grp.get("het_han_muc") or 0)} hết hạn mức</span>'
                f'<span class="acc-err">{int(grp.get("can_dang_nhap") or 0)} cần đăng nhập</span>'
                "</div></div>"
                '<div class="table-scroll"><table class="tool-table">'
                "<thead><tr><th>Tài khoản</th><th>Máy</th><th>Hồ sơ Chrome</th><th>Đã dùng 24h</th><th>Còn lại</th><th>Reset lúc</th><th>Trạng thái</th></tr></thead>"
                f"<tbody>{''.join(rows_html)}</tbody></table></div></section>"
            )

    # Khối Crawler
    crawler_machines = data.get("crawler") or []
    c_rows: list[str] = []
    c_tried: list[str] = []
    for cm in crawler_machines:
        may_c = str(cm.get("may") or "may")
        nguons = cm.get("nguon") or []
        for ng in nguons:
            st = str(ng.get("trang_thai") or "chua_chay").lower()
            if st == "ok":
                dot_cls, lbl = "dot-ok", "Ổn định"
            elif st == "bi_chan":
                dot_cls, lbl = "dot-err", "Bị chặn"
            elif st == "loi":
                dot_cls, lbl = "dot-err", "Lỗi"
            else:
                dot_cls, lbl = "dot-idle", "Chưa chạy"
            c_rows.append(
                "<tr>"
                f'<td><span class="status-pill"><span class="status-dot {dot_cls}"></span>{_esc(lbl)}</span></td>'
                f"<td><strong>{_esc(ng.get('nguon') or '—')}</strong></td>"
                f"<td><code>{_esc(may_c)}</code></td>"
                f'<td class="num">{_esc(ng.get("lan_chay_cuoi") or "—")}</td>'
                f'<td class="num">{_fmt_int(ng.get("so_trang") or 0)}</td>'
                f"<td>{_esc(ng.get('loi_gan_nhat') or '—')}</td>"
                f"<td><code>{_esc(ng.get('thu_muc_du_lieu') or '—')}</code></td>"
                "</tr>"
            )
        if not cm.get("tim_thay") or not nguons:
            paths = cm.get("duong_dan_da_thu") or []
            p_items = "".join(f"<li><code>{_esc(p)}</code></li>" for p in paths)
            details = f'<details><summary>Đường dẫn đã thử ({len(paths)})</summary><ul class="tried-list">{p_items}</ul></details>' if p_items else ""
            c_tried.append(f'<div class="tried-paths"><strong>Máy <code>{_esc(may_c)}</code>:</strong> chưa tìm thấy crawler.{details}</div>')

    crawler_body = ""
    if c_rows:
        crawler_body += (
            '<div class="table-scroll"><table class="tool-table">'
            "<thead><tr><th>Trạng thái</th><th>Nguồn / Adapter</th><th>Máy</th><th>Lần chạy cuối</th><th>Số trang/bài</th><th>Lỗi / bị chặn</th><th>Thư mục dữ liệu</th></tr></thead>"
            f"<tbody>{''.join(c_rows)}</tbody></table></div>"
        )
    elif not crawler_machines:
        crawler_body += '<p class="empty">Chưa có báo cáo từ <code>runner/lenh/crawler.ps1</code>.</p>'
    crawler_body += "".join(c_tried)
    parts.append(f'<section class="card crawler-card"><h2>Crawler</h2>{crawler_body}</section>')

    # Khối Zalo
    zalo_machines = data.get("zalo") or []
    z_rows: list[str] = []
    z_tried: list[str] = []
    for zm in zalo_machines:
        may_z = str(zm.get("may") or "may")
        bns = zm.get("bo_nghe") or []
        for bn in bns:
            is_run = bool(bn.get("dang_chay"))
            z_dot = "dot-ok" if is_run else "dot-err"
            z_lbl = "Đang chạy" if is_run else "Dừng"
            grps = " ".join(f'<span class="tag-chip">{_esc(g)}</span>' for g in (bn.get("nhom") or [])) or '<span class="meta">—</span>'
            z_rows.append(
                "<tr>"
                f'<td><span class="status-pill"><span class="status-dot {z_dot}"></span>{z_lbl}</span></td>'
                f"<td><strong>{_esc(bn.get('ten') or '—')}</strong></td>"
                f"<td><code>{_esc(may_z)}</code></td>"
                f"<td>{grps}</td>"
                f'<td class="num">{_esc(bn.get("tin_cuoi_luc") or "—")}</td>'
                f"<td>{_esc(bn.get('loi_gan_nhat') or '—')}</td>"
                "</tr>"
            )
        if not zm.get("tim_thay") or not bns:
            paths = zm.get("duong_dan_da_thu") or []
            p_items = "".join(f"<li><code>{_esc(p)}</code></li>" for p in paths)
            details = f'<details><summary>Đường dẫn đã thử ({len(paths)})</summary><ul class="tried-list">{p_items}</ul></details>' if p_items else ""
            z_tried.append(f'<div class="tried-paths"><strong>Máy <code>{_esc(may_z)}</code>:</strong> chưa tìm thấy bộ nghe Zalo.{details}</div>')

    zalo_body = ""
    if z_rows:
        zalo_body += (
            '<div class="table-scroll"><table class="tool-table">'
            "<thead><tr><th>Trạng thái</th><th>Bộ nghe</th><th>Máy</th><th>Nhóm đang nghe</th><th>Tin cuối lúc</th><th>Lỗi gần nhất</th></tr></thead>"
            f"<tbody>{''.join(z_rows)}</tbody></table></div>"
        )
    elif not zalo_machines:
        zalo_body += '<p class="empty">Chưa có báo cáo từ <code>runner/lenh/zalo.ps1</code>.</p>'
    zalo_body += "".join(z_tried)
    parts.append(f'<section class="card zalo-card"><h2>Zalo</h2>{zalo_body}</section>')
    return "".join(parts)


def _render_profiles_section(data: dict) -> str:
    """Sinh nội dung tab Máy: hồ sơ năng lực, thanh RAM/ổ đĩa (thẻ Tài khoản đã chuyển sang tab Công cụ)."""
    profiles = data.get("ho_so_may") or []
    if not profiles:
        return '<section class="card"><p class="empty">Chưa có hồ sơ máy trong hang-doi/may/*.json.</p></section>'

    cards = []
    for p in profiles:
        ma = p.get("ma_may") or "may"
        ten_win = p.get("ten_windows") or "—"
        vai_tro = p.get("vai_tro") or "Chưa đặt LINHX_VAI trong tho.env"
        cpu = p.get("cpu") or {}
        ram = p.get("ram") or {}
        gpus = p.get("gpu") or []
        disks = p.get("o_dia") or []
        agy = p.get("agy") or {}
        chrome = p.get("chrome") or {}
        nhan_cfg = p.get("nhan_phieu") or {}
        tk24 = p.get("thong_ke_24h") or {}
        warn_c = bool(p.get("canh_bao_o_c"))
        c_free = p.get("o_c_trong_gb")

        card_cls = "may-card warn-disk" if warn_c else "may-card"
        alert_html = (
            f'<div class="disk-alert">Cảnh báo: Ổ C: chỉ còn trống {float(c_free or 0):.1f} GB (&lt; 10 GB)!</div>'
            if warn_c
            else ""
        )

        ram_bar = _render_usage_bar("RAM", ram.get("tong_gb") or 0, ram.get("trong_gb") or 0)
        disk_bars = []
        for od in disks:
            if not isinstance(od, dict):
                continue
            o_name = str(od.get("o") or "Ổ")
            is_c_low = (
                o_name.strip().upper().rstrip("\\/") == "C:"
                and float(od.get("trong_gb") or 0) < LOW_DISK_C_THRESHOLD_GB
            )
            disk_bars.append(
                _render_usage_bar(f"Ổ {o_name}", od.get("tong_gb") or 0, od.get("trong_gb") or 0, warn_low_free=is_c_low)
            )

        if gpus:
            gpu_parts = []
            for g in gpus:
                if isinstance(g, dict):
                    vram = f" ({g['vram_gb']} GB)" if g.get("vram_gb") else ""
                    gpu_parts.append(f"{g.get('ten', 'GPU')}{vram}")
            gpu_txt = ", ".join(gpu_parts)
        else:
            gpu_txt = "Không rõ / Onboard"

        if chrome.get("co"):
            profs = chrome.get("profiles") or []
            prof_preview = ", ".join(str(x) for x in profs[:8])
            if len(profs) > 8:
                prof_preview += f" (+{len(profs) - 8})"
            chrome_txt = f"Có ({prof_preview})" if prof_preview else "Có"
        else:
            chrome_txt = "Không"

        che_do_nhan = "Nhận cả bat-ky" if nhan_cfg.get("nhan_bat_ky", True) else "Chỉ nhận đích danh"
        so_phieu = nhan_cfg.get("so_phieu", 1)

        cards.append(
            f'<article class="{card_cls}">'
            '<div class="may-card-head">'
            f'<h3 class="may-name">{_esc(ma)} · <code>{_esc(ten_win)}</code></h3>'
            f'<span class="meta num">24h: xong {int(tk24.get("xong") or 0)} / lỗi {int(tk24.get("loi") or 0)}</span>'
            "</div>"
            f'<p class="vai-tro">{_esc(vai_tro)}</p>'
            f"{alert_html}"
            f"{ram_bar}"
            f"{''.join(disk_bars)}"
            '<ul class="spec-list">'
            f"<li><strong>CPU:</strong> {_esc(cpu.get('ten') or '—')} ({_esc(cpu.get('nhan') or '?')} nhân / {_esc(cpu.get('luong') or '?')} luồng)</li>"
            f"<li><strong>GPU:</strong> {_esc(gpu_txt)}</li>"
            f"<li><strong>Nhận phiếu:</strong> tối đa <strong>{_esc(so_phieu)}</strong> phiếu code · {_esc(che_do_nhan)}</li>"
            f"<li><strong>agy:</strong> <code>{_esc(agy.get('duong_dan') or 'agy')}</code> ({_esc(agy.get('phien_ban') or 'chưa rõ')}) · Python {_esc(p.get('python') or '—')}</li>"
            f"<li><strong>Chrome:</strong> {_esc(chrome_txt)}</li>"
            "</ul>"
            "</article>"
        )
    return '<div class="cards-may">' + "".join(cards) + "</div>"


def _render_project_step_html(ma_da: str, step: dict, idx: int, gantt_truc: dict | None = None) -> str:
    """Sinh HTML cho một bước trên bảng GANTT dự án (mặc định thu gọn chi tiết)."""
    st = step.get("trang_thai") or "cho"
    known_dots = {
        "cho": "dot-buoc-cho",
        "dang-chay": "dot-buoc-dang-chay",
        "xong-dat": "dot-buoc-xong-dat",
        "xong-khong-dat": "dot-buoc-xong-khong-dat",
        "cho-claude": "dot-buoc-cho-claude",
        "cho-linh": "dot-buoc-cho-linh",
    }
    dot_cls = "tl-dot " + known_dots.get(st, "dot-buoc-cho")
    badge_cls = f"badge badge-buoc-{st}" if st in known_dots else "badge badge-buoc-cho"
    ma_buoc = str(step.get("ma") or f"b{idx}")
    ten_buoc = str(step.get("ten") or ma_buoc)
    step_key = f"{ma_da or 'du-an'}:{ma_buoc}"
    nhan = str(step.get("trang_thai_nhan") or _STEP_STATUS_LABELS.get(st, st))
    is_late = bool(step.get("bi_tre"))

    code_part = f'<span class="tl-step-code">{_esc(ma_buoc)}</span> ' if ma_buoc and ma_buoc != ten_buoc else ""
    right_chips: list[str] = []
    if step.get("cong"):
        right_chips.append(f'<span class="tag-chip">Cổng {_esc(step["cong"])}</span>')
    if step.get("nguoi"):
        right_chips.append(f'<span class="tag-chip">Người: {_esc(step["nguoi"])}</span>')
    if is_late and step.get("tre_nhan"):
        right_chips.append(f'<span class="badge badge-step-late">{_esc(step["tre_nhan"])}</span>')
    right_chips.append(f'<span class="{_esc(badge_cls)}">{_esc(nhan)}</span>')

    dk_txt = str(step.get("du_kien_gio") or "—")
    tt_txt = str(step.get("thuc_te_gio") or "—")
    hours_line = (
        f'<span class="step-hours-line">dự kiến <span class="num">{_esc(dk_txt)}</span> · '
        f'thực tế <span class="num">{_esc(tt_txt)}</span></span>'
    )

    truc = gantt_truc or {}
    grid_parts: list[str] = []
    for tick in truc.get("moc_gio") or ():
        mp = float(tick.get("pct") or 0.0)
        if 0.0 < mp < 100.0:
            grid_parts.append(f'<span class="gantt-grid-line" style="left:{mp}%"></span>')
    g = step.get("gantt") if isinstance(step.get("gantt"), dict) else {}
    dk_bar = (
        f'<div class="gantt-bar-dk" style="left:{float(g.get("dk_left_pct") or 0)}%;width:{float(g.get("dk_width_pct") or 0)}%"></div>'
        if g.get("co_du_kien")
        else ""
    )
    tt_bar_cls = f"gantt-bar-tt st-{_esc(st)}" + (" is-late" if is_late else "")
    tt_bar = (
        f'<div class="{tt_bar_cls}" style="left:{float(g.get("tt_left_pct") or 0)}%;width:{float(g.get("tt_width_pct") or 0)}%"></div>'
        if g.get("co_thuc_te")
        else ""
    )
    now_pct = truc.get("hien_tai_pct")
    now_line = f'<span class="gantt-vline-now" style="left:{float(now_pct)}%"></span>' if now_pct is not None else ""
    han_pct = truc.get("han_pct")
    han_line = (
        f'<span class="gantt-vline-han" style="left:{float(han_pct)}%"></span>'
        if truc.get("han_co") and han_pct is not None
        else ""
    )
    lane_html = (
        '<div class="gantt-lane" aria-hidden="true">'
        f'{"".join(grid_parts)}{dk_bar}{tt_bar}{now_line}{han_line}'
        "</div>"
    )

    run_html = ""
    if st == "dang-chay":
        tran_val = float(step.get("tran_phut") or 40)
        phut_val = float(step.get("chay_phut") or 0)
        phut_int = int(round(phut_val))
        tran_int = int(round(tran_val))
        pct = min(100, max(4, int(round((phut_val / tran_val) * 100.0)))) if tran_val > 0 else 0
        fill_cls = (
            "progress-fill over-limit"
            if pct >= 95
            else ("progress-fill near-limit" if pct >= 80 else "progress-fill")
        )
        run_tid = str(step.get("phieu_dang_chay") or "").strip()
        ticket_link = (
            f'<a href="/phieu/{urllib.parse.quote(run_tid)}">{_esc(run_tid)}</a>' if run_tid else "Đang chạy"
        )
        nhip_txt = str(step.get("nhip_cuoi") or "Đang chạy, chưa có nhịp mới…")
        run_html = (
            '<div class="tl-step-run">'
            '<div class="work-top">'
            f'<div class="work-ticket">{ticket_link}</div>'
            f'<div class="work-time">{phut_int} phút / {tran_int}p</div>'
            "</div>"
            f'<div class="progress-track"><div class="{fill_cls}" style="width:{pct}%"></div></div>'
            f'<div class="nhip-line">{_esc(nhip_txt)}</div>'
            "</div>"
        )

    tickets = step.get("phieu_chi_tiet") or []
    if not tickets:
        tickets_html = '<p class="empty" style="margin:4px 0 0">Chưa gắn phiếu.</p>'
    else:
        t_rows: list[str] = []
        for t in tickets:
            gd = t.get("giai_doan") or ""
            tt = t.get("trang_thai") or ""
            if gd == "xong":
                t_badge = (
                    f'<span class="badge tt-xong">đạt ({_esc(tt or "xong")})</span>'
                    if t.get("dat")
                    else f'<span class="badge tt-loi">không đạt ({_esc(tt or "loi")})</span>'
                )
            elif gd == "dang":
                t_badge = '<span class="badge tt-chay">đang chạy</span>'
            elif gd == "moi":
                t_badge = '<span class="badge may-ranh">đang chờ</span>'
            else:
                t_badge = f'<span class="badge may-ranh">{"chờ Claude" if tt == "cho-claude" else "chưa tạo"}</span>'

            extra_time = ""
            if gd == "dang":
                extra_time = (
                    f'<span class="num">{int(round(float(t.get("phut") or 0)))}p / '
                    f'{int(round(float(t.get("tran_phut") or 40)))}p</span>'
                )
            elif gd == "xong":
                extra_time = f'<span class="num">{float(t.get("phut") or 0):.1f}p</span>'

            gate_tag = ' <span class="tag-chip">cổng</span>' if t.get("la_cong") else ""
            nhip_line = f'<div class="nhip-line" style="width:100%">{_esc(t["nhip"])}</div>' if t.get("nhip") else ""
            t_id = str(t.get("phieu") or "")
            t_url = str(t.get("ket_qua_url") or f"/phieu/{urllib.parse.quote(t_id)}")
            t_rows.append(
                '<div class="step-ticket-item">'
                f'<div><a class="ticket-main-link" href="{_esc(t_url)}">{_esc(t_id)}</a>{gate_tag}</div>'
                f'<div class="ticket-tags">{t_badge}<span class="tag-chip">{_esc(t.get("may") or "—")}</span>{extra_time}</div>'
                f"{nhip_line}"
                "</div>"
            )
        tickets_html = '<div class="step-ticket-list">' + "".join(t_rows) + "</div>"

    logs = step.get("log_cuoi") or []
    log_html = (
        f'<pre class="ket-qua step-log">{_esc(chr(10).join(str(x) for x in logs))}</pre>'
        if logs
        else '<p class="empty" style="margin:4px 0 0">Chưa có log hay dòng nhịp.</p>'
    )

    kq_list = step.get("ket_qua_list") or []
    if not kq_list:
        kq_html = '<p class="empty" style="margin:4px 0 0">Chưa có KET-QUA.md.</p>'
    else:
        kq_blocks: list[str] = []
        for kq in kq_list:
            badge_kq = (
                '<span class="badge tt-xong">Đạt</span>'
                if kq.get("dat")
                else '<span class="badge tt-loi">KHÔNG đạt</span>'
            )
            kq_blocks.append(
                "<details class=\"kq-details\">"
                f"<summary><span>{_esc(kq.get('phieu') or '')}</span>{badge_kq}</summary>"
                f'<pre class="ket-qua">{_esc(kq.get("noi_dung") or "")}</pre>'
                "</details>"
            )
        kq_html = "".join(kq_blocks)

    imgs = step.get("anh_thu_nho") or []
    if not imgs:
        imgs_html = '<p class="empty" style="margin:4px 0 0">Chưa có ảnh bằng chứng.</p>'
    else:
        im_cards: list[str] = []
        for im in imgs:
            im_url = str(im.get("url") or "")
            im_phieu = str(im.get("phieu") or "")
            im_ten = str(im.get("ten") or "")
            cap = f"{im_phieu} · {im_ten}" if im_phieu else im_ten
            im_cards.append(
                f'<a class="thumb-card" href="{_esc(im_url)}" target="_blank" rel="noopener">'
                f'<img src="{_esc(im_url)}" alt="{_esc(cap)}" loading="lazy">'
                f'<div class="thumb-cap">{_esc(cap)}</div>'
                "</a>"
            )
        imgs_html = '<div class="thumb-grid">' + "".join(im_cards) + "</div>"

    step_cls = "tl-step gantt-step" + (" is-step-late" if is_late else "")
    return (
        f'<div class="{step_cls}">'
        '<div class="tl-step-box">'
        '<div class="gantt-row-main">'
        f'<button type="button" class="tl-step-toggle" data-toggle-step="{_esc(step_key)}" aria-expanded="false">'
        '<span class="gantt-step-top">'
        f'<span class="tl-step-name"><span class="{_esc(dot_cls)}" aria-hidden="true"></span>{code_part}{_esc(ten_buoc)}</span>'
        f'<span class="tl-step-right">{"".join(right_chips)}</span>'
        "</span>"
        f"{hours_line}"
        "</button>"
        f"{lane_html}"
        "</div>"
        f"{run_html}"
        f'<div class="tl-step-detail" data-detail-step="{_esc(step_key)}" hidden>'
        f'<div class="step-subhead">Các phiếu ({len(tickets)})</div>{tickets_html}'
        f'<div class="step-subhead">30 dòng cuối log / nhịp ({len(logs)})</div>{log_html}'
        f'<div class="step-subhead">KET-QUA ({len(kq_list)})</div>{kq_html}'
        f'<div class="step-subhead">Ảnh thu nhỏ ({len(imgs)})</div>{imgs_html}'
        "</div></div></div>"
    )


def _render_gantt_head_html(gantt_truc: dict | None) -> str:
    """Sinh phần đầu GANTT (chú giải + trục giờ, vạch hiện tại và vạch hạn)."""
    t = gantt_truc or {}
    leg: list[str] = [
        '<span class="gantt-leg-item"><span class="gantt-swatch-dk" aria-hidden="true"></span>dự kiến</span>',
        '<span class="gantt-leg-item"><span class="gantt-swatch-tt" aria-hidden="true"></span>thực tế</span>',
        '<span class="gantt-leg-item"><span class="gantt-swatch-tre" aria-hidden="true"></span>trễ &gt;15p</span>',
    ]
    if t.get("hien_tai_gio"):
        ghim_now = " (ngoài khung)" if t.get("hien_tai_ghim") else ""
        leg.append(
            f'<span class="gantt-leg-item gantt-leg-now"><span class="gantt-swatch-now" aria-hidden="true"></span>'
            f'Hiện tại <span class="num">{_esc(t["hien_tai_gio"])}</span>{ghim_now}</span>'
        )
    if t.get("han_co"):
        ghim_han = " (ghim mép)" if t.get("han_ghim") else ""
        leg.append(
            f'<span class="gantt-leg-item gantt-leg-han"><span class="gantt-swatch-han" aria-hidden="true"></span>'
            f'Hạn <span class="num">{_esc(t.get("han_nhan") or "")}</span>{ghim_han}</span>'
        )
    tick_parts: list[str] = []
    for tick in t.get("moc_gio") or ():
        pct = float(tick.get("pct") or 0.0)
        t_cls = "gantt-tick" + (" is-left" if pct <= 5.0 else (" is-right" if pct >= 95.0 else ""))
        tick_parts.append(f'<span class="{t_cls}" style="left:{pct}%">{_esc(tick.get("gio") or "")}</span>')
    now_pct = t.get("hien_tai_pct")
    now_mk = (
        f'<span class="gantt-axis-now" style="left:{float(now_pct)}%" title="Hiện tại {_esc(t.get("hien_tai_gio") or "")}"></span>'
        if now_pct is not None
        else ""
    )
    han_pct = t.get("han_pct")
    han_mk = (
        f'<span class="gantt-axis-han" style="left:{float(han_pct)}%" title="Hạn {_esc(t.get("han_nhan") or "")}"></span>'
        if t.get("han_co") and han_pct is not None
        else ""
    )
    return (
        '<div class="gantt-head-row">'
        f'<div class="gantt-legend">{"".join(leg)}</div>'
        f'<div class="gantt-axis" aria-hidden="true">{"".join(tick_parts)}{now_mk}{han_mk}</div>'
        "</div>"
    )


def _render_projects_section(data: dict) -> str:
    """Sinh nội dung tab Dự án: tên, hạn, câu dự kiến xong, tóm tắt bước và GANTT rút gọn theo giờ."""
    projects = data.get("du_an") or []
    if not projects:
        return '<section class="card"><p class="empty">Chưa có dự án nào trong hang-doi/du-an/*.json.</p></section>'

    cards: list[str] = []
    for idx, proj in enumerate(projects):
        ma_da = str(proj.get("ma") or f"du-an-{idx}")
        ten_da = str(proj.get("ten") or ma_da)
        han_cls = "badge may-do" if proj.get("qua_han") else "badge may-ranh"
        han_txt = str(proj.get("han_con_lai") or "Chưa đặt hạn")
        han_disp = str(proj.get("han_hien_thi") or "")
        meta_line = (
            f'<div class="meta" style="margin-bottom:10px">Mã: <code>{_esc(ma_da)}</code> · Hạn: <span class="num">{_esc(han_disp)}</span></div>'
            if han_disp and han_disp != "—"
            else f'<div class="meta" style="margin-bottom:10px">Mã: <code>{_esc(ma_da)}</code></div>'
        )
        eta_cau = str(proj.get("du_kien_xong_cau") or "")
        eta_html = ""
        if eta_cau:
            lech = int(proj.get("du_kien_lech_phut") or 0)
            eta_cls = "du-an-eta " + ("is-late" if lech > 15 else ("is-slightly-late" if lech > 0 else "is-on-time"))
            eta_html = f'<div class="{eta_cls}">{_esc(eta_cau)}</div>'

        steps = proj.get("buoc") or []
        truc = proj.get("gantt_truc") if isinstance(proj.get("gantt_truc"), dict) else {}
        steps_html = (
            '<div class="gantt-table">'
            + _render_gantt_head_html(truc)
            + '<div class="timeline-list" style="gap:8px">'
            + "".join(_render_project_step_html(ma_da, step, s_idx, truc) for s_idx, step in enumerate(steps))
            + "</div></div>"
            if steps
            else '<p class="empty">Chưa khai báo các bước.</p>'
        )
        cards.append(
            '<section class="card du-an-card">'
            '<div class="du-an-head">'
            f'<h2 class="du-an-title">{_esc(ten_da)}</h2>'
            f'<span class="{han_cls}">{_esc(han_txt)}</span>'
            "</div>"
            f"{meta_line}"
            f"{eta_html}"
            f'<div class="du-an-summary">{_esc(proj.get("tom_tat_buoc") or "")}</div>'
            f"{steps_html}"
            "</section>"
        )
    return "".join(cards)


def _render_quality_section(data: dict) -> str:
    """Sinh nội dung tab Chất lượng: bảng mức 9, lưới ảnh ghép và bảng chấm đọc từ JSON."""
    projects = data.get("du_an") or []
    if not projects:
        return '<section class="card"><p class="empty">Chưa có dự án nào trong hang-doi/du-an/*.json.</p></section>'

    cards: list[str] = []
    for proj in projects:
        ma_da = str(proj.get("ma") or "")
        ten_da = str(proj.get("ten") or ma_da or "Dự án")
        cl = proj.get("chat_luong") if isinstance(proj.get("chat_luong"), dict) else {}
        dm9 = cl.get("do_muc_9") if isinstance(cl.get("do_muc_9"), dict) else {}
        chi_so = dm9.get("chi_so") or []

        if dm9.get("chua_do", True) or not chi_so:
            muc9_body = '<div class="cl-chua-do">Chưa đo</div>'
        else:
            tep_name = str(dm9.get("tep") or "")
            tep_url = str(dm9.get("tep_url") or "")
            tep_link = (
                f'<a href="{_esc(tep_url)}" target="_blank" rel="noopener">{_esc(tep_name)}</a>'
                if tep_url
                else _esc(tep_name)
            )
            meta_row = (
                f'<div class="meta" style="margin-bottom:8px">Tệp mới nhất: {tep_link} · {_esc(dm9.get("cap_nhat_hien_thi") or "—")}</div>'
                if tep_name
                else ""
            )
            m_rows: list[str] = []
            for row in chi_so:
                ten_full = (f"{row['ma']} · " if row.get("ma") else "") + str(row.get("ten") or "")
                dat_val = row.get("dat")
                if dat_val is True:
                    kq_badge = '<span class="badge tt-xong">Đạt</span>'
                elif dat_val is False:
                    kq_badge = '<span class="badge tt-loi">Đỏ</span>'
                else:
                    kq_badge = '<span class="badge may-ranh">—</span>'
                m_rows.append(
                    "<tr>"
                    f'<td class="col-ten">{_esc(ten_full)}</td>'
                    f'<td class="col-nguong num">{_esc(row.get("nguong") or "—")}</td>'
                    f'<td class="col-do num">{_esc(row.get("te_nhat") or "—")}</td>'
                    f'<td class="col-kq">{kq_badge}</td>'
                    "</tr>"
                )
            muc9_body = (
                meta_row
                + '<table class="muc9-table"><thead><tr>'
                + '<th class="col-ten">Tên</th><th class="col-nguong">Ngưỡng</th>'
                + '<th class="col-do">Số đo tệ nhất</th><th class="col-kq">Đạt / Đỏ</th>'
                + "</tr></thead><tbody>"
                + "".join(m_rows)
                + "</tbody></table>"
            )

        anh_ghep = cl.get("anh_ghep") or []
        if not anh_ghep:
            ghep_body = '<p class="empty">Chưa có ảnh ghép khung | bản dựng.</p>'
        else:
            g_cards = [
                f'<a class="ghep-card" href="{_esc(im.get("url") or "")}" target="_blank" rel="noopener">'
                f'<img src="{_esc(im.get("url") or "")}" alt="{_esc((im.get("phieu") or "") + " " + (im.get("ten") or ""))}" loading="lazy">'
                '<div class="ghep-meta">'
                f'<div class="ghep-phieu">{_esc(im.get("phieu") or im.get("ten") or "")}</div>'
                f'<div class="ghep-gio">{_esc(im.get("gio_ngan") or im.get("gio_hien_thi") or "—")}</div>'
                "</div></a>"
                for im in anh_ghep
            ]
            ghep_body = '<div class="ghep-grid">' + "".join(g_cards) + "</div>"

        cham = cl.get("cham") or []
        if not cham:
            cham_body = '<p class="empty">Chưa có dữ liệu chấm.</p>'
        else:
            c_rows: list[str] = []
            for row in cham:
                tep_val = str(row.get("tep") or "")
                tep_url = str(row.get("tep_url") or "")
                if tep_url:
                    tep_cell = f'<a href="{_esc(tep_url)}" target="_blank" rel="noopener">{_esc(tep_val or "Xem tệp")}</a>'
                elif tep_val:
                    tep_cell = f"<code>{_esc(tep_val)}</code>"
                else:
                    tep_cell = "—"
                c_rows.append(
                    "<tr>"
                    f'<td data-label="RC">{_esc(row.get("rc") or "—")}</td>'
                    f'<td data-label="Người">{_esc(row.get("nguoi") or "—")}</td>'
                    f'<td data-label="Điểm" class="num"><strong>{_esc(row.get("diem") or "—")}</strong></td>'
                    f'<td data-label="Ghi chú">{_esc(row.get("ghi_chu") or "—")}</td>'
                    f'<td data-label="Tệp">{tep_cell}</td>'
                    "</tr>"
                )
            cham_body = (
                '<table class="cham-table"><thead><tr>'
                "<th>RC</th><th>Người</th><th>Điểm</th><th>Ghi chú</th><th>Tệp</th>"
                "</tr></thead><tbody>"
                + "".join(c_rows)
                + "</tbody></table>"
            )

        cards.append(
            '<section class="card chat-luong-card">'
            '<div class="du-an-head">'
            f'<h2 class="du-an-title">{_esc(ten_da)}</h2>'
            f'<span class="meta"><code>{_esc(ma_da)}</code></span>'
            "</div>"
            f'<div class="cl-section"><h3>Bảng mức 9</h3>{muc9_body}</div>'
            f'<div class="cl-section"><h3>Ảnh ghép khung | bản dựng ({len(anh_ghep)})</h3>{ghep_body}</div>'
            f'<div class="cl-section"><h3>Bảng chấm ({len(cham)})</h3>{cham_body}</div>'
            "</section>"
        )
    return "".join(cards)


def render_app_html(data: dict, active_tab: str = "du-an") -> str:
    """Sinh giao diện bảng theo dõi chuẩn Apple tối giản, đọc trong 5 giây, tự làm mới 15s qua fetch."""
    if active_tab not in ("du-an", "chat-luong", "tong-quan", "phieu", "may", "cong-cu"):
        active_tab = "du-an"

    refresh_sec = int(data.get("chu_ky_giay") or 30)
    can_linh = data.get("can_linh") or []
    running = data.get("dang_chay") or []
    waiting = data.get("dang_cho") or []
    done_list = data.get("xong_gan_nhat") or []
    machines = data.get("may") or []
    projects = data.get("du_an") or []
    sync_err = data.get("loi_dong_bo") or ""

    done_24h, _ = _split_done_24h(done_list, data.get("cap_nhat_luc"))
    hero_html = _build_hero_headline_html(machines, can_linh)
    subline_txt = f"{len(machines)} máy · {len(running)} đang chạy · {len(waiting)} đang chờ · {len(done_24h)} xong 24h"
    raw_upd = str(data.get("cap_nhat_hien_thi") or "—")
    short_upd = raw_upd[11:19] if len(raw_upd) >= 19 else raw_upd
    updated_disp = _esc(short_upd)

    err_html = (
        f'<div class="err-banner">Lỗi đồng bộ git gần nhất: {_esc(sync_err)}</div>'
        if sync_err
        else ""
    )
    can_linh_html = _render_can_linh_block(can_linh)

    cnt_du_an_txt = f"Dự án ({len(projects)})" if projects else "Dự án"
    cnt_phieu_active = len(running) + len(waiting)
    cnt_may = max(len(data.get("ho_so_may") or []), len(machines))
    cnt_cong_cu = len(data.get("so_cong_cu") or [])

    def _tab_attrs(name: str) -> str:
        is_act = active_tab == name
        cls = "seg-btn is-active" if is_act else "seg-btn"
        sel = "true" if is_act else "false"
        return f'class="{cls}" data-tab="{name}" aria-selected="{sel}"'

    hid_da = "" if active_tab == "du-an" else " hidden"
    hid_cl = "" if active_tab == "chat-luong" else " hidden"
    hid_tq = "" if active_tab == "tong-quan" else " hidden"
    hid_ph = "" if active_tab == "phieu" else " hidden"
    hid_ma = "" if active_tab == "may" else " hidden"
    hid_cc = "" if active_tab == "cong-cu" else " hidden"

    projects_html = _render_projects_section(data)
    quality_html = _render_quality_section(data)
    overview_html = _render_overview_machines_section(data)
    tickets_html = _render_tickets_section(data)
    profiles_html = _render_profiles_section(data)
    tools_html = _render_tools_section(data)
    safe_json = _safe_inline_json(data)

    title_map = {
        "du-an": "Dự án · LINHX",
        "chat-luong": "Chất lượng · LINHX",
        "tong-quan": "Tổng quan · LINHX",
        "phieu": "Phiếu hàng đợi · LINHX",
        "may": "Hồ sơ máy · LINHX",
        "cong-cu": "Công cụ & Hạn mức · LINHX",
    }
    page_title = title_map.get(active_tab, "Bảng theo dõi · LINHX")

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <noscript><meta http-equiv="refresh" content="{refresh_sec}"></noscript>
  <title>{page_title}</title>
  <style>{_COMMON_CSS}</style>
</head>
<body>
  <div class="wrap" id="bang-app" data-initial-tab="{active_tab}">
    <header class="hero-header">
      <div class="eyebrow-row">
        <div class="brand-label">
          <span class="live-indicator" id="live-dot" aria-hidden="true"></span>
          <span>LINHX · Hàng đợi</span>
        </div>
        <div class="sync-meta">
          <span id="sync-meta-text">{updated_disp} · 15s</span> ·
          <a href="/api/trang-thai">JSON</a>
        </div>
      </div>
      <h1 class="hero-headline" id="hero-headline">{hero_html}</h1>
      <p class="hero-subline" id="hero-subline">{_esc(subline_txt)}</p>
    </header>

    <div id="sync-err-slot">{err_html}</div>
    <div id="can-linh-slot">{can_linh_html}</div>

    <nav class="seg-tabs" role="tablist" aria-label="Chế độ xem">
      <button type="button" role="tab" {_tab_attrs("du-an")}><span id="tab-lbl-du-an">{_esc(cnt_du_an_txt)}</span></button>
      <button type="button" role="tab" {_tab_attrs("chat-luong")}><span id="tab-lbl-chat-luong">Chất lượng</span></button>
      <button type="button" role="tab" {_tab_attrs("tong-quan")}>Tổng quan</button>
      <button type="button" role="tab" {_tab_attrs("phieu")}><span id="tab-lbl-phieu">Phiếu ({cnt_phieu_active})</span></button>
      <button type="button" role="tab" {_tab_attrs("may")}><span id="tab-lbl-may">Máy ({cnt_may})</span></button>
      <button type="button" role="tab" {_tab_attrs("cong-cu")}><span id="tab-lbl-cong-cu">Công cụ ({cnt_cong_cu})</span></button>
    </nav>

    <main>
      <section class="tab-panel" id="panel-du-an" data-panel="du-an" role="tabpanel"{hid_da}>
        <div id="du-an-content-slot">{projects_html}</div>
      </section>

      <section class="tab-panel" id="panel-chat-luong" data-panel="chat-luong" role="tabpanel"{hid_cl}>
        <div id="chat-luong-content-slot">{quality_html}</div>
      </section>

      <section class="tab-panel" id="panel-tong-quan" data-panel="tong-quan" role="tabpanel"{hid_tq}>
        <template data-schema="machines"><th>Đang làm gì</th></template>
        <div id="overview-machines-slot">{overview_html}</div>
      </section>

      <section class="tab-panel" id="panel-phieu" data-panel="phieu" role="tabpanel"{hid_ph}>
        <div id="phieu-content-slot">{tickets_html}</div>
      </section>

      <section class="tab-panel" id="panel-may" data-panel="may" role="tabpanel"{hid_ma}>
        <div id="may-content-slot">{profiles_html}</div>
      </section>

      <section class="tab-panel" id="panel-cong-cu" data-panel="cong-cu" role="tabpanel"{hid_cc}>
        <div id="cong-cu-content-slot">{tools_html}</div>
      </section>
    </main>
  </div>
  <script type="application/json" id="bang-init-data">{safe_json}</script>
  <script>{_DASHBOARD_JS}</script>
</body>
</html>
"""


def render_dashboard_html(data: dict) -> str:
    """Sinh HTML trang chủ mở sẵn tab Dự án (đặt đầu, mặc định)."""
    return render_app_html(data, active_tab="du-an")


def render_projects_html(data: dict) -> str:
    """Sinh HTML mở sẵn tab Dự án."""
    return render_app_html(data, active_tab="du-an")


def render_quality_html(data: dict) -> str:
    """Sinh HTML mở sẵn tab Chất lượng."""
    return render_app_html(data, active_tab="chat-luong")


def render_overview_html(data: dict) -> str:
    """Sinh HTML mở sẵn tab Tổng quan."""
    return render_app_html(data, active_tab="tong-quan")


def render_tickets_page_html(data: dict) -> str:
    """Sinh HTML mở sẵn tab Phiếu."""
    return render_app_html(data, active_tab="phieu")


def render_machines_html(data: dict) -> str:
    """Sinh HTML mở sẵn tab Máy (`/may`)."""
    return render_app_html(data, active_tab="may")


def render_tools_html(data: dict) -> str:
    """Sinh HTML mở sẵn tab Công cụ (`/cong-cu`)."""
    return render_app_html(data, active_tab="cong-cu")


def render_ticket_html(detail: dict) -> str:
    """Sinh HTML hiển thị nội dung KET-QUA.md của một phiếu theo phong cách tối giản đồng bộ."""
    st = detail.get("trang_thai") or "xong"
    badge_cls = f"badge tt-{st}" if st in ("xong", "loi", "dung", "dang") else "badge may-ranh"
    canh_nen_html = (
        f'<span>Chế độ: <span class="badge tt-dung badge-canh-nen">{_esc(detail["nhan_canh_nen"])}</span></span>'
        if detail.get("nhan_canh_nen")
        else ""
    )
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Phiếu {_esc(detail["phieu"])} · LINHX</title>
  <style>{_COMMON_CSS}</style>
</head>
<body>
  <div class="wrap">
    <div class="detail-top-bar">
      <div>
        <div class="brand-label">LINHX · Chi tiết phiếu</div>
        <h1 class="hero-headline" style="font-size:26px;margin-top:4px">{_esc(detail["phieu"])}</h1>
      </div>
      <a class="btn-subtle" href="/">← Quay lại bảng</a>
    </div>
    <section class="card">
      <div class="detail-meta-grid">
        <span>Trạng thái: <span class="{_esc(badge_cls)}">{_esc(st)}</span></span>
        {canh_nen_html}
        <span>Máy: <code>{_esc(detail["may"])}</code></span>
        <span class="num">Phút: <strong>{_esc(detail["phut"])}</strong></span>
        <span class="num">Token: <strong>{_esc(detail["token"])}</strong></span>
        <span>Nguồn: <code>{_esc(detail["nguon_tep"])}</code></span>
      </div>
      <pre class="ket-qua">{_esc(detail["noi_dung"])}</pre>
    </section>
  </div>
</body>
</html>
"""


def create_http_server(
    monitor: QueueMonitor,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
) -> ThreadingHTTPServer:
    """Tạo đối tượng ThreadingHTTPServer chỉ đọc (GET/HEAD) cho bảng theo dõi."""

    class BangRequestHandler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args) -> None:
            # Ghi log gọn ra stdout để theo dõi trong file log nếu cần
            pass

        def _send_bytes(
            self,
            status_code: int,
            body: bytes,
            content_type: str,
            head_only: bool = False,
            extra_headers: dict[str, str] | None = None,
        ) -> None:
            self.send_response(status_code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            if extra_headers:
                for h_name, h_val in extra_headers.items():
                    self.send_header(h_name, h_val)
            self.end_headers()
            if not head_only:
                self.wfile.write(body)

        def _send_json(self, status_code: int, payload: dict, head_only: bool = False) -> None:
            raw = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
            self._send_bytes(status_code, raw, "application/json; charset=utf-8", head_only=head_only)

        def _send_html(self, status_code: int, html_text: str, head_only: bool = False) -> None:
            raw = html_text.encode("utf-8")
            self._send_bytes(status_code, raw, "text/html; charset=utf-8", head_only=head_only)

        def _handle_read(self, head_only: bool) -> None:
            parsed = urllib.parse.urlsplit(self.path)
            path = parsed.path.rstrip("/") or "/"

            if path == "/tep":
                # Đường dẫn /tep chỉ hỗ trợ phương thức GET
                if head_only:
                    self._send_json(405, {"loi": "Đường dẫn /tep chỉ hỗ trợ GET"}, head_only=True)
                    return
                if ".." in parsed.query:
                    self._send_json(403, {"loi": "Chặn leo thư mục (..)"})
                    return
                qs = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
                p_vals = qs.get("p")
                if not p_vals:
                    self._send_json(400, {"loi": "Thiếu tham số p"})
                    return
                raw_p = p_vals[0]
                real_fp, code, err_msg = monitor.resolve_tep(raw_p)
                if code != 200 or real_fp is None:
                    self._send_json(code, {"loi": err_msg or "Không thể truy cập tệp"})
                    return
                try:
                    raw_bytes = real_fp.read_bytes()
                except OSError:
                    self._send_json(404, {"loi": "Không đọc được tệp"})
                    return
                if len(raw_bytes) > MAX_TEP_BYTES:
                    self._send_json(413, {"loi": "Tệp vượt quá giới hạn 20 MB"})
                    return
                ct = _TEP_CONTENT_TYPES.get(real_fp.suffix.lower(), "application/octet-stream")
                self._send_bytes(
                    200,
                    raw_bytes,
                    ct,
                    head_only=False,
                    extra_headers={"X-Content-Type-Options": "nosniff"},
                )
                return

            if path == "/" or path == "/du-an":
                status_data = monitor.get_status()
                self._send_html(200, render_dashboard_html(status_data), head_only=head_only)
                return

            if path == "/chat-luong":
                status_data = monitor.get_status()
                self._send_html(200, render_quality_html(status_data), head_only=head_only)
                return

            if path == "/tong-quan":
                status_data = monitor.get_status()
                self._send_html(200, render_overview_html(status_data), head_only=head_only)
                return

            if path == "/phieu":
                status_data = monitor.get_status()
                self._send_html(200, render_tickets_page_html(status_data), head_only=head_only)
                return

            if path == "/may":
                status_data = monitor.get_status()
                self._send_html(200, render_machines_html(status_data), head_only=head_only)
                return

            if path == "/cong-cu":
                status_data = monitor.get_status()
                self._send_html(200, render_tools_html(status_data), head_only=head_only)
                return

            if path == "/api/trang-thai":
                status_data = monitor.get_status()
                self._send_json(200, status_data, head_only=head_only)
                return

            if path == "/api/may":
                status_data = monitor.get_status()
                self._send_json(200, {"may": status_data.get("ho_so_may") or []}, head_only=head_only)
                return

            if path == "/api/cong-cu":
                status_data = monitor.get_status()
                self._send_json(
                    200,
                    {
                        "tai_khoan_may": status_data.get("tai_khoan_may") or [],
                        "so_cong_cu": status_data.get("so_cong_cu") or [],
                        "crawler": status_data.get("crawler") or [],
                        "zalo": status_data.get("zalo") or [],
                    },
                    head_only=head_only,
                )
                return

            if path.startswith("/api/ket-qua/"):
                raw_id = urllib.parse.unquote(path[len("/api/ket-qua/") :])
                if not is_safe_ticket_id(raw_id):
                    self._send_json(400, {"loi": "Mã phiếu không hợp lệ"}, head_only=head_only)
                    return
                detail = monitor.get_ticket(raw_id)
                if detail is None:
                    self._send_json(404, {"loi": "Không tìm thấy phiếu", "phieu": raw_id}, head_only=head_only)
                    return
                self._send_json(200, detail, head_only=head_only)
                return

            if path.startswith("/phieu/") or path.startswith("/ket-qua/"):
                prefix = "/phieu/" if path.startswith("/phieu/") else "/ket-qua/"
                raw_id = urllib.parse.unquote(path[len(prefix) :])
                if not is_safe_ticket_id(raw_id):
                    self._send_html(400, "<h1>400 - Mã phiếu không hợp lệ</h1>", head_only=head_only)
                    return
                detail = monitor.get_ticket(raw_id)
                if detail is None:
                    self._send_html(
                        404,
                        f'<h1>404 - Không tìm thấy phiếu {_esc(raw_id)}</h1><p><a href="/">Về bảng</a></p>',
                        head_only=head_only,
                    )
                    return
                self._send_html(200, render_ticket_html(detail), head_only=head_only)
                return

            self._send_json(404, {"loi": "Không tìm thấy đường dẫn"}, head_only=head_only)

        def do_GET(self) -> None:
            self._handle_read(head_only=False)

        def do_HEAD(self) -> None:
            self._handle_read(head_only=True)

        def _discard_request_body(self) -> None:
            try:
                raw_len = self.headers.get("Content-Length")
                if raw_len:
                    nbytes = int(raw_len)
                    if 0 < nbytes <= 1048576:
                        self.rfile.read(nbytes)
            except (ValueError, OSError):
                pass

        def _reject_write(self) -> None:
            self._discard_request_body()
            self._send_json(405, {"loi": "Bảng chỉ đọc (chỉ hỗ trợ GET/HEAD)"})

        def do_POST(self) -> None:
            self._reject_write()

        def do_PUT(self) -> None:
            self._reject_write()

        def do_DELETE(self) -> None:
            self._reject_write()

        def do_PATCH(self) -> None:
            self._reject_write()

        def do_OPTIONS(self) -> None:
            self._reject_write()

    class ReusableThreadingHTTPServer(ThreadingHTTPServer):
        allow_reuse_address = True
        daemon_threads = True

    return ReusableThreadingHTTPServer((host, int(port)), BangRequestHandler)


@contextmanager
def single_instance_lock(lock_file: Path):
    """Khóa mức hệ điều hành không chặn để tránh chạy trùng 2 tiến trình bảng trên cùng cổng."""
    lock_file = Path(lock_file)
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    fh = open(lock_file, "a+b")
    locked = False
    try:
        fh.seek(0)
        if fh.read(1) == b"":
            fh.write(b"0")
            fh.flush()
        fh.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        locked = True
    except OSError:
        fh.close()
        yield False
        return

    try:
        yield True
    finally:
        if locked:
            try:
                fh.seek(0)
                if os.name == "nt":
                    import msvcrt

                    msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass
        fh.close()


def detect_lan_ip() -> str:
    """Lấy địa chỉ IPv4 mạng nội bộ của máy (không gửi gói tin ra ngoài)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("192.168.255.254", 80))
            ip = sock.getsockname()[0]
            if ip and not ip.startswith("127."):
                return ip
    except OSError:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if ip and not ip.startswith("127.") and not ip.startswith("169.254."):
                return ip
    except OSError:
        pass
    return "127.0.0.1"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bảng theo dõi web cho hàng đợi LINHX (chỉ đọc).")
    parser.add_argument("--host", default=os.environ.get("LINHX_BANG_HOST", DEFAULT_HOST))
    parser.add_argument("--cong", type=int, default=int(os.environ.get("LINHX_BANG_CONG", str(DEFAULT_PORT))))
    parser.add_argument("--clone", default=os.environ.get("LINHX_BANG_CLONE", str(DEFAULT_CLONE_DIR)))
    parser.add_argument("--repo", default=os.environ.get("LINHX_BANG_REPO_URL", DEFAULT_REPO_URL))
    parser.add_argument("--nhanh", default=os.environ.get("LINHX_NHANH_HANG_DOI", DEFAULT_BRANCH))
    parser.add_argument("--chu-ky", type=float, default=float(os.environ.get("LINHX_BANG_CHU_KY", str(DEFAULT_FETCH_INTERVAL))))
    parser.add_argument("--khong-fetch", action="store_true", help="Chỉ đọc thư mục sẵn có, không gọi git fetch.")
    parser.add_argument("--log", default="", help="Đường dẫn file log ghi đầu ra.")
    parser.add_argument("--tep-khoa", default="", help="Đường dẫn file khóa chống chạy chồng.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    clone_path = Path(args.clone)

    log_handle = None
    if args.log:
        log_path = Path(args.log)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_handle = open(log_path, "a", encoding="utf-8", buffering=1)
        sys.stdout = log_handle
        sys.stderr = log_handle

    lock_path = Path(args.tep_khoa) if args.tep_khoa else (clone_path.parent / f".{clone_path.name}-{args.cong}.lock")
    try:
        with single_instance_lock(lock_path) as acquired:
            if not acquired:
                print(time.strftime("%Y-%m-%d %H:%M:%S"), f"Bảng đã chạy sẵn (khóa {lock_path}), thoát.", flush=True)
                return 0

            monitor = QueueMonitor(
                clone_dir=clone_path,
                repo_url=args.repo,
                branch=args.nhanh,
                fetch_interval=args.chu_ky,
                enable_git_sync=not args.khong_fetch,
            )
            monitor.start_background_sync()
            server = create_http_server(monitor, host=args.host, port=args.cong)
            lan_ip = detect_lan_ip()
            print(
                time.strftime("%Y-%m-%d %H:%M:%S"),
                f"Bảng hàng đợi lắng nghe tại http://localhost:{args.cong} (LAN: http://{lan_ip}:{args.cong})",
                flush=True,
            )
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
            finally:
                server.server_close()
                monitor.stop_background_sync()
        return 0
    finally:
        if log_handle is not None:
            log_handle.close()


if __name__ == "__main__":
    raise SystemExit(main())
