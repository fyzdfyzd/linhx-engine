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
from datetime import datetime, timezone
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import socket
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

_HEADER_LINE_RE = re.compile(r"^([a-zA-Z0-9_-]+)\s*:\s*(.*)$")
_TZ_COMPACT_RE = re.compile(r"([+-]\d{2})(\d{2})$")
_TOKEN_IN_RE = re.compile(r"vao\s*=\s*(\d+)", re.IGNORECASE)
_TOKEN_OUT_RE = re.compile(r"ra\s*=\s*(\d+)", re.IGNORECASE)
_SAFE_TICKET_ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")


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
            meta, body = parse_markdown_headers(raw_text)
            target_machine = (meta.get("may") or "bat-ky").strip().lower()
            claimed_machine, claimed_dt = _parse_claimed_info(meta, target_machine)
            if claimed_dt is None:
                claimed_dt = _file_timestamp(md_file, clone_dir, git_times)

            elapsed_sec = max(0.0, (current_time - claimed_dt).total_seconds()) if claimed_dt else 0.0
            try:
                limit_min = float(meta.get("tran_phut") or 40)
            except ValueError:
                limit_min = 40.0

            kind = (meta.get("loai") or "code").strip().lower()
            if claimed_machine not in ("bat-ky", "chua-ro"):
                running_count_by_machine[claimed_machine] = running_count_by_machine.get(claimed_machine, 0) + 1
            record_machine_event(claimed_machine, "nhan", ticket_id, claimed_dt)

            running_items.append(
                {
                    "phieu": ticket_id,
                    "may": claimed_machine,
                    "loai": kind,
                    "nhan_luc": format_iso(claimed_dt),
                    "nhan_luc_hien_thi": format_display_time(claimed_dt),
                    "chay_giay": int(round(elapsed_sec)),
                    "chay_phut": round(elapsed_sec / 60.0, 2),
                    "chay_bao_lau": format_duration_vi(elapsed_sec) if claimed_dt else "—",
                    "tran_phut": int(limit_min) if limit_min.is_integer() else limit_min,
                    "de": _summarize_text(body or ticket_id),
                    "ket_qua_url": f"/phieu/{urllib.parse.quote(ticket_id)}",
                    "_sort_ts": claimed_dt.timestamp() if claimed_dt else 0.0,
                }
            )
    running_items.sort(key=lambda item: (-item["_sort_ts"], item["phieu"]))
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
            if status not in ("xong", "loi", "dung"):
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
            record_machine_event(machine_name, "xong", ticket_id, done_dt)

            all_done_items.append(
                {
                    "phieu": ticket_id,
                    "may": machine_name,
                    "trang_thai": status,
                    "phut": minutes_val,
                    "token": token_raw,
                    "token_vao": tok_in,
                    "token_ra": tok_out,
                    "tong_token": tok_total,
                    "tep_doi": (meta.get("tep_doi") or "(khong)").strip(),
                    "drive": (meta.get("drive") or "(khong)").strip(),
                    "xong_luc": format_iso(done_dt),
                    "xong_luc_hien_thi": format_display_time(done_dt),
                    "tom_tat": _summarize_text(body, 100),
                    "ket_qua": raw_kq,
                    "ket_qua_url": f"/phieu/{urllib.parse.quote(ticket_id)}",
                    "_sort_ts": done_dt.timestamp() if done_dt else 0.0,
                }
            )

    all_done_items.sort(key=lambda item: (-item["_sort_ts"], item["phieu"]))
    recent_done = all_done_items[: max(0, int(max_done))]
    for item in recent_done:
        item.pop("_sort_ts", None)

    # 4. Tổng hợp trạng thái từng máy (quá 30 phút không nhận/xong phiếu -> đỏ)
    machines_list: list[dict] = []
    for machine_name in sorted(known_machines):
        ev = machine_events.get(machine_name)
        if ev is not None:
            last_dt: datetime = ev["dt"]
            idle_sec = max(0.0, (current_time - last_dt).total_seconds())
            idle_min = idle_sec / 60.0
            is_overdue = idle_min > float(inactive_minutes)
            machines_list.append(
                {
                    "may": machine_name,
                    "su_kien_cuoi": ev["su_kien"],
                    "phieu_cuoi": ev["phieu"],
                    "lan_cuoi": format_iso(last_dt),
                    "lan_cuoi_hien_thi": format_display_time(last_dt),
                    "cach_day": f"{format_duration_vi(idle_sec)} trước",
                    "khong_hoat_dong_phut": round(idle_min, 2),
                    "qua_30_phut": is_overdue,
                    "dang_chay_so_luong": running_count_by_machine.get(machine_name, 0),
                }
            )
        else:
            machines_list.append(
                {
                    "may": machine_name,
                    "su_kien_cuoi": "chua-co",
                    "phieu_cuoi": "",
                    "lan_cuoi": "",
                    "lan_cuoi_hien_thi": "Chưa từng hoạt động",
                    "cach_day": "—",
                    "khong_hoat_dong_phut": None,
                    "qua_30_phut": True,
                    "dang_chay_so_luong": 0,
                }
            )

    return {
        "cap_nhat_luc": format_iso(current_time),
        "cap_nhat_hien_thi": format_display_time(current_time),
        "dang_chay": running_items,
        "dang_cho": waiting_items,
        "tong_xong": len(all_done_items),
        "xong_gan_nhat": recent_done,
        "may": machines_list,
    }


def read_ticket_detail(clone_dir: Path, ticket_id: str) -> dict | None:
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
        meta, body = parse_markdown_headers(raw_text)
        machine, _ = _parse_claimed_info(meta, (meta.get("may") or "bat-ky").strip().lower())
        return {
            "phieu": ticket_id,
            "nguon_tep": f"hang-doi/dang/{ticket_id}.md",
            "giai_doan": "dang",
            "may": machine,
            "trang_thai": "dang",
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
            return read_ticket_detail(self.clone_dir, ticket_id)

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
  color-scheme: light;
  --bg: #f8fafc;
  --card: #ffffff;
  --border: #e2e8f0;
  --text: #0f172a;
  --muted: #64748b;
  --link: #1d4ed8;
  --ok-bg: #dcfce7;
  --ok-fg: #166534;
  --err-bg: #fee2e2;
  --err-fg: #991b1b;
  --warn-bg: #fef3c7;
  --warn-fg: #92400e;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  padding: 16px;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  font-size: 14px;
  line-height: 1.45;
  background: var(--bg);
  color: var(--text);
}
.wrap { max-width: 1180px; margin: 0 auto; }
header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border);
}
h1 { margin: 0; font-size: 20px; }
h2 { margin: 0 0 8px 0; font-size: 15px; }
.meta { color: var(--muted); font-size: 13px; }
.err-banner {
  background: var(--err-bg);
  color: var(--err-fg);
  border: 1px solid #fca5a5;
  padding: 8px 12px;
  border-radius: 6px;
  margin-bottom: 12px;
}
.grid-top {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
  margin-bottom: 14px;
}
@media (min-width: 900px) {
  .grid-top { grid-template-columns: 1.2fr 1fr; }
}
section.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 14px;
  margin-bottom: 14px;
}
.grid-top section.card { margin-bottom: 0; }
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13.5px;
}
th, td {
  text-align: left;
  padding: 6px 8px;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
}
th {
  color: var(--muted);
  font-weight: 600;
  font-size: 12.5px;
  white-space: nowrap;
}
tr:last-child td { border-bottom: none; }
a { color: var(--link); text-decoration: none; font-weight: 500; }
a:hover { text-decoration: underline; }
.empty { color: var(--muted); font-style: italic; padding: 6px 0; margin: 0; }
.badge {
  display: inline-block;
  padding: 1px 8px;
  border-radius: 999px;
  font-weight: 600;
  font-size: 12px;
  white-space: nowrap;
}
.tt-xong, .may-ok { background: var(--ok-bg); color: var(--ok-fg); }
.tt-loi, .may-do { background: var(--err-bg); color: var(--err-fg); }
.tt-dung { background: var(--warn-bg); color: var(--warn-fg); }
tr.qua-han td { background: #fef2f2; color: var(--err-fg); }
tr.qua-han a { color: var(--err-fg); text-decoration: underline; }
.num { font-variant-numeric: tabular-nums; white-space: nowrap; }
pre.ket-qua {
  background: #0f172a;
  color: #f8fafc;
  padding: 14px;
  border-radius: 6px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 13px;
  line-height: 1.5;
  margin: 10px 0 0 0;
}
"""


def _esc(val) -> str:
    return html.escape(str(val if val is not None else ""), quote=True)


def render_dashboard_html(data: dict) -> str:
    """Sinh HTML trang chủ tối giản bằng tiếng Việt, tự làm mới 30 giây."""
    refresh_sec = int(data.get("chu_ky_giay") or 30)
    running = data.get("dang_chay") or []
    waiting = data.get("dang_cho") or []
    done_list = data.get("xong_gan_nhat") or []
    machines = data.get("may") or []
    sync_err = data.get("loi_dong_bo") or ""

    err_html = (
        f'<div class="err-banner">Lỗi đồng bộ git gần nhất: {_esc(sync_err)}</div>'
        if sync_err
        else ""
    )

    # (1) Đang chạy
    if running:
        rows_run = []
        for item in running:
            rows_run.append(
                "<tr>"
                f'<td><a href="{_esc(item["ket_qua_url"])}">{_esc(item["phieu"])}</a></td>'
                f"<td><code>{_esc(item['may'])}</code></td>"
                f"<td>{_esc(item['loai'])}</td>"
                f'<td class="num">{_esc(item["chay_bao_lau"])}</td>'
                f'<td class="num">{_esc(item["nhan_luc_hien_thi"])}</td>'
                "</tr>"
            )
        running_html = (
            "<table><thead><tr>"
            "<th>Phiếu</th><th>Máy</th><th>Loại</th><th>Chạy bao lâu</th><th>Nhận lúc</th>"
            "</tr></thead><tbody>" + "".join(rows_run) + "</tbody></table>"
        )
    else:
        running_html = '<p class="empty">Không có phiếu đang chạy.</p>'

    # (4) Mỗi máy
    if machines:
        rows_machine = []
        for m in machines:
            is_red = bool(m.get("qua_30_phut"))
            row_cls = ' class="qua-han"' if is_red else ""
            badge_cls = "badge may-do" if is_red else "badge may-ok"
            status_label = "Quá 30 phút không hoạt động" if is_red else "Hoạt động"
            ev_kind = m.get("su_kien_cuoi") or ""
            ev_ticket = m.get("phieu_cuoi") or ""
            if ev_kind in ("nhan", "xong") and ev_ticket:
                verb = "nhận" if ev_kind == "nhan" else "xong"
                ticket_href = f"/phieu/{urllib.parse.quote(ev_ticket)}"
                ev_html = f'{verb} <a href="{_esc(ticket_href)}">{_esc(ev_ticket)}</a>'
            else:
                ev_html = "—"
            last_txt = _esc(m.get("lan_cuoi_hien_thi") or "—")
            ago_txt = m.get("cach_day") or ""
            if ago_txt and ago_txt != "—":
                last_txt = f"{last_txt} ({_esc(ago_txt)})"
            rows_machine.append(
                f"<tr{row_cls}>"
                f"<td><strong>{_esc(m['may'])}</strong></td>"
                f'<td class="num">{last_txt}</td>'
                f"<td>{ev_html}</td>"
                f'<td><span class="{badge_cls}">{status_label}</span></td>'
                "</tr>"
            )
        machines_html = (
            "<table><thead><tr>"
            "<th>Máy</th><th>Lần cuối nhận/xong</th><th>Sự kiện</th><th>Trạng thái</th>"
            "</tr></thead><tbody>" + "".join(rows_machine) + "</tbody></table>"
        )
    else:
        machines_html = '<p class="empty">Chưa ghi nhận máy nào.</p>'

    # (2) Đang chờ
    if waiting:
        rows_wait = []
        for item in waiting:
            rows_wait.append(
                "<tr>"
                f'<td><a href="{_esc(item["ket_qua_url"])}">{_esc(item["phieu"])}</a></td>'
                f"<td><code>{_esc(item['may'])}</code></td>"
                f"<td>{_esc(item['loai'])}</td>"
                f'<td class="num">{_esc(item["tran_phut"])} phút</td>'
                f"<td>{_esc(item['de'])}</td>"
                "</tr>"
            )
        waiting_html = (
            "<table><thead><tr>"
            "<th>Phiếu</th><th>Máy đích</th><th>Loại</th><th>Trần</th><th>Đề tóm tắt</th>"
            "</tr></thead><tbody>" + "".join(rows_wait) + "</tbody></table>"
        )
    else:
        waiting_html = '<p class="empty">Không có phiếu đang chờ.</p>'

    # (3) Xong gần nhất 20 phiếu
    if done_list:
        rows_done = []
        for item in done_list:
            st = item.get("trang_thai") or "loi"
            badge_cls = f"badge tt-{st}" if st in ("xong", "loi", "dung") else "badge tt-loi"
            tok_str = f"{item['tong_token']:,} (vào {item['token_vao']:,} / ra {item['token_ra']:,})"
            rows_done.append(
                "<tr>"
                f'<td><a href="{_esc(item["ket_qua_url"])}">{_esc(item["phieu"])}</a></td>'
                f"<td><code>{_esc(item['may'])}</code></td>"
                f'<td><span class="{_esc(badge_cls)}">{_esc(st)}</span></td>'
                f'<td class="num">{item["phut"]:.2f}</td>'
                f'<td class="num">{_esc(tok_str)}</td>'
                f'<td class="num">{_esc(item["xong_luc_hien_thi"])}</td>'
                "</tr>"
            )
        done_html = (
            "<table><thead><tr>"
            "<th>Phiếu (bấm xem KET-QUA)</th><th>Máy</th><th>Trạng thái</th>"
            "<th>Phút</th><th>Token</th><th>Xong lúc</th>"
            "</tr></thead><tbody>" + "".join(rows_done) + "</tbody></table>"
        )
    else:
        done_html = '<p class="empty">Chưa có phiếu hoàn thành.</p>'

    sync_disp = _esc(data.get("dong_bo_hien_thi") or "—")
    updated_disp = _esc(data.get("cap_nhat_hien_thi") or "—")

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="{refresh_sec}">
  <title>Bảng theo dõi hàng đợi LINHX</title>
  <style>{_COMMON_CSS}</style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>Bảng theo dõi hàng đợi LINHX</h1>
      <div class="meta">
        Cập nhật: {updated_disp} · Đồng bộ git: {sync_disp} · Tự làm mới {refresh_sec} giây ·
        <a href="/api/trang-thai">JSON</a>
      </div>
    </header>
    {err_html}
    <div class="grid-top">
      <section class="card">
        <h2>1. Đang chạy ({len(running)})</h2>
        {running_html}
      </section>
      <section class="card">
        <h2>4. Trạng thái máy ({len(machines)})</h2>
        {machines_html}
      </section>
    </div>
    <section class="card">
      <h2>2. Đang chờ ({len(waiting)})</h2>
      {waiting_html}
    </section>
    <section class="card">
      <h2>3. Xong gần nhất ({len(done_list)}/{int(data.get("tong_xong") or len(done_list))} phiếu)</h2>
      {done_html}
    </section>
  </div>
</body>
</html>
"""


def render_ticket_html(detail: dict) -> str:
    """Sinh HTML hiển thị nội dung KET-QUA.md của một phiếu."""
    st = detail.get("trang_thai") or "xong"
    badge_cls = f"badge tt-{st}" if st in ("xong", "loi", "dung") else "badge"
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Phiếu {_esc(detail["phieu"])} - KET-QUA</title>
  <style>{_COMMON_CSS}</style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>Phiếu: {_esc(detail["phieu"])}</h1>
      <div class="meta"><a href="/">← Quay lại bảng theo dõi</a></div>
    </header>
    <section class="card">
      <div>
        Trạng thái: <span class="{_esc(badge_cls)}">{_esc(st)}</span> ·
        Máy: <code>{_esc(detail["may"])}</code> ·
        Phút: <strong>{_esc(detail["phut"])}</strong> ·
        Token: <strong>{_esc(detail["token"])}</strong> ·
        Nguồn: <code>{_esc(detail["nguon_tep"])}</code>
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
        ) -> None:
            self.send_response(status_code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
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

            if path == "/":
                status_data = monitor.get_status()
                self._send_html(200, render_dashboard_html(status_data), head_only=head_only)
                return

            if path == "/api/trang-thai":
                status_data = monitor.get_status()
                self._send_json(200, status_data, head_only=head_only)
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

        def _reject_write(self) -> None:
            self._send_json(405, {"loi": "Bảng chỉ đọc (chỉ hỗ trợ GET/HEAD)"})

        def do_POST(self) -> None:
            self._reject_write()

        def do_PUT(self) -> None:
            self._reject_write()

        def do_DELETE(self) -> None:
            self._reject_write()

        def do_PATCH(self) -> None:
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
