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
LOW_DISK_C_THRESHOLD_GB = 10.0

_HEADER_LINE_RE = re.compile(r"^([a-zA-Z0-9_-]+)\s*:\s*(.*)$")
_NHIP_LINE_RE = re.compile(r"^nhip\s*:\s*(.+)$", re.IGNORECASE)
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

    # 0b. Đọc hang-doi/may/*.json (Hồ sơ máy)
    profiles_by_machine: dict[str, dict] = {}
    dir_profiles = qroot / "may"
    if dir_profiles.is_dir():
        for prof_file in sorted(dir_profiles.glob("*.json"), key=lambda p: p.name):
            try:
                prof_data = json.loads(prof_file.read_text(encoding="utf-8", errors="replace"))
            except (OSError, ValueError, TypeError):
                continue
            if not isinstance(prof_data, dict):
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
                "nhip": nhip_line,
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

            done_entry = {
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
                "ly_do_ngan": _extract_ket_reason(body, 90) if status in ("loi", "dung") else "",
                "ket_qua": raw_kq,
                "ket_qua_url": f"/phieu/{urllib.parse.quote(ticket_id)}",
                "_sort_ts": done_dt.timestamp() if done_dt else 0.0,
            }
            all_done_items.append(done_entry)
            if machine_name and machine_name not in ("bat-ky", "chua-ro", "(khong)"):
                prev_done = latest_done_by_machine.get(machine_name)
                if prev_done is None or done_entry["_sort_ts"] >= prev_done["_sort_ts"]:
                    latest_done_by_machine[machine_name] = dict(done_entry)

    all_done_items.sort(key=lambda item: (-item["_sort_ts"], item["phieu"]))
    recent_done = all_done_items[: max(0, int(max_done))]
    for item in recent_done:
        item.pop("_sort_ts", None)

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
  --run-bg: #dbeafe;
  --run-fg: #1e40af;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  padding: 12px;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  font-size: 14px;
  line-height: 1.45;
  background: var(--bg);
  color: var(--text);
}
.wrap { max-width: 1120px; margin: 0 auto; }
header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}
h1 { margin: 0; font-size: 18px; }
h2 { margin: 0 0 8px 0; font-size: 15px; }
.meta { color: var(--muted); font-size: 12.5px; }
nav.tabs { display: flex; gap: 6px; align-items: center; }
nav.tabs a {
  padding: 4px 12px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--text);
  font-weight: 600;
  font-size: 13px;
}
nav.tabs a.active {
  background: var(--text);
  color: #ffffff;
  border-color: var(--text);
}
.err-banner {
  background: var(--err-bg);
  color: var(--err-fg);
  border: 1px solid #fca5a5;
  padding: 8px 12px;
  border-radius: 6px;
  margin-bottom: 12px;
}
section.can-linh-box {
  background: #fef2f2;
  border: 2px solid #dc2626;
  border-radius: 8px;
  padding: 10px 12px;
  margin-bottom: 12px;
}
section.can-linh-box h2 {
  color: #991b1b;
  margin: 0 0 6px 0;
  font-size: 15px;
}
.can-linh-item {
  padding: 6px 0;
  border-top: 1px solid #fecaca;
}
.can-linh-item:first-of-type { border-top: none; padding-top: 2px; }
.cmd-paste {
  display: block;
  margin-top: 4px;
  padding: 5px 8px;
  background: #1e293b;
  color: #f8fafc;
  border-radius: 4px;
  font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
  font-size: 12.5px;
  overflow-x: auto;
  user-select: all;
}
section.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 12px;
  margin-bottom: 12px;
}
.table-wrap { overflow-x: auto; }
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
  font-size: 12px;
  white-space: nowrap;
}
tr:last-child td { border-bottom: none; }
a { color: var(--link); text-decoration: none; font-weight: 500; }
a:hover { text-decoration: underline; }
.empty { color: var(--muted); font-style: italic; padding: 4px 0; margin: 0; }
.badge {
  display: inline-block;
  padding: 1px 8px;
  border-radius: 999px;
  font-weight: 600;
  font-size: 12px;
  white-space: nowrap;
}
.tt-xong, .may-ok { background: var(--ok-bg); color: var(--ok-fg); }
.tt-chay { background: var(--run-bg); color: var(--run-fg); }
.tt-loi, .may-do { background: var(--err-bg); color: var(--err-fg); }
.tt-dung, .may-ket { background: var(--warn-bg); color: var(--warn-fg); }
tr.qua-han td { background: #fef2f2; color: var(--err-fg); }
tr.qua-han a { color: var(--err-fg); text-decoration: underline; }
.nhip-line {
  color: var(--muted);
  font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
  font-size: 12px;
  margin-top: 2px;
  word-break: break-word;
}
.ket-note { color: var(--err-fg); font-size: 12.5px; margin-top: 2px; }
.num { font-variant-numeric: tabular-nums; white-space: nowrap; }
.cards-may {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}
@media (min-width: 760px) {
  .cards-may { grid-template-columns: repeat(2, 1fr); }
}
.may-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 14px;
}
.may-card.warn-disk { border-color: #dc2626; }
.may-card-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 6px;
}
.vai-tro { color: #0f172a; font-weight: 500; font-size: 13px; margin-bottom: 8px; }
.spec-list { margin: 0; padding: 0; list-style: none; font-size: 13px; }
.spec-list li { padding: 3px 0; border-bottom: 1px dashed var(--border); }
.spec-list li:last-child { border-bottom: none; }
.bar-row { margin: 6px 0; font-size: 12.5px; }
.bar-track {
  height: 8px;
  background: #e2e8f0;
  border-radius: 999px;
  overflow: hidden;
  margin-top: 3px;
}
.bar-fill { height: 100%; background: #2563eb; }
.bar-fill.warn { background: #dc2626; }
.disk-alert {
  background: var(--err-bg);
  color: var(--err-fg);
  border: 1px solid #fca5a5;
  border-radius: 6px;
  padding: 5px 8px;
  font-weight: 600;
  font-size: 12.5px;
  margin-bottom: 8px;
}
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


def _render_can_linh_block(can_linh: list[dict]) -> str:
    """Sinh khối đỏ 'Cần anh làm' trên cùng trang (ẩn hoàn toàn khi rỗng)."""
    if not can_linh:
        return ""
    items_html = []
    for cl in can_linh:
        phieu = cl.get("phieu") or cl.get("id") or ""
        href = cl.get("ket_qua_url") or f"/phieu/{urllib.parse.quote(phieu)}"
        lenh = (cl.get("lenh") or "").strip()
        lenh_html = f'<code class="cmd-paste">{_esc(lenh)}</code>' if lenh else ""
        items_html.append(
            '<div class="can-linh-item">'
            f'<strong>{_esc(cl.get("may") or "máy")}</strong> · '
            f'<a href="{_esc(href)}">{_esc(phieu)}</a>: '
            f'<span>{_esc(cl.get("viec") or "")}</span> '
            f'<span class="meta">({_esc(cl.get("gio_hien_thi") or "")})</span>'
            f"{lenh_html}"
            "</div>"
        )
    return (
        '<section class="can-linh-box">'
        f"<h2>Cần anh làm ({len(can_linh)})</h2>"
        + "".join(items_html)
        + "</section>"
    )


def _render_header_nav(active_tab: str, data: dict) -> str:
    refresh_sec = int(data.get("chu_ky_giay") or 30)
    sync_disp = _esc(data.get("dong_bo_hien_thi") or "—")
    updated_disp = _esc(data.get("cap_nhat_hien_thi") or "—")
    cls_home = ' class="active"' if active_tab == "bang" else ""
    cls_may = ' class="active"' if active_tab == "may" else ""
    cnt_may = len(data.get("ho_so_may") or data.get("may") or [])
    return f"""<header>
      <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
        <h1>LINHX Hàng đợi</h1>
        <nav class="tabs">
          <a href="/"{cls_home}>Bảng trực</a>
          <a href="/may"{cls_may}>Máy ({cnt_may})</a>
        </nav>
      </div>
      <div class="meta">
        Cập nhật: {updated_disp} · Git: {sync_disp} · {refresh_sec}s ·
        <a href="/api/trang-thai">JSON</a>
      </div>
    </header>"""


def render_dashboard_html(data: dict) -> str:
    """Sinh HTML trang chủ tối giản đọc trong 5 giây trên điện thoại, tự làm mới 30 giây."""
    refresh_sec = int(data.get("chu_ky_giay") or 30)
    can_linh = data.get("can_linh") or []
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
    can_linh_html = _render_can_linh_block(can_linh)

    # Bảng chính: mỗi máy 1 dòng (đang làm gì + trạng thái chạy / rảnh / kẹt / im lặng > 30p)
    if machines:
        rows_machine = []
        for m in machines:
            is_red = bool(m.get("qua_30_phut"))
            tt_may = m.get("trang_thai_may") or ("im-lang" if is_red else "ranh")
            row_cls = ' class="qua-han"' if is_red else ""

            # Cột Đang làm gì: phiếu + phút + dòng nhip
            dang_phieu = m.get("dang_lam_phieu") or ""
            nhip_txt = m.get("nhip") or ""
            if dang_phieu:
                phut_so = int(round(float(m.get("dang_lam_phut") or 0)))
                href_run = f"/phieu/{urllib.parse.quote(dang_phieu)}"
                extra_cnt = int(m.get("dang_chay_so_luong") or 1)
                extra_txt = f" (+{extra_cnt - 1})" if extra_cnt > 1 else ""
                nhip_div = f'<div class="nhip-line">{_esc(nhip_txt)}</div>' if nhip_txt else ""
                doing_html = (
                    f'<a href="{_esc(href_run)}">{_esc(dang_phieu)}</a>'
                    f'{_esc(extra_txt)} · <span class="num">{phut_so} phút</span>'
                    f"{nhip_div}"
                )
            else:
                ev_kind = m.get("su_kien_cuoi") or ""
                ev_ticket = m.get("phieu_cuoi") or ""
                if ev_kind in ("nhan", "xong") and ev_ticket:
                    verb = "nhận" if ev_kind == "nhan" else "xong"
                    ticket_href = f"/phieu/{urllib.parse.quote(ev_ticket)}"
                    ago = m.get("cach_day") or ""
                    ago_part = f" ({_esc(ago)})" if ago and ago != "—" else ""
                    doing_html = f'<span class="meta">Rảnh · mới {verb} <a href="{_esc(ticket_href)}">{_esc(ev_ticket)}</a>{ago_part}</span>'
                else:
                    doing_html = '<span class="meta">Chưa nhận việc</span>'

            # Cột Trạng thái: chạy / rảnh / kẹt (dừng-lỗi kèm lý do) / im lặng > 30 phút đỏ
            ket_phieu = m.get("ket_phieu") or ""
            ket_tt = m.get("ket_trang_thai") or ""
            ket_ly_do = m.get("ket_ly_do") or ""
            ket_extra = ""
            if ket_phieu:
                ket_href = f"/phieu/{urllib.parse.quote(ket_phieu)}"
                ket_extra = (
                    f'<div class="ket-note">Kẹt ({_esc(ket_tt)}) '
                    f'<a href="{_esc(ket_href)}">{_esc(ket_phieu)}</a>: {_esc(ket_ly_do)}</div>'
                )

            if is_red:
                badge_html = '<span class="badge may-do">Im lặng &gt; 30 phút</span>'
            elif tt_may == "chay":
                badge_html = '<span class="badge tt-chay">Chạy</span>'
            elif tt_may == "ket":
                badge_html = f'<span class="badge may-ket">Kẹt ({_esc(ket_tt or "lỗi")})</span>'
            else:
                badge_html = '<span class="badge may-ok">Rảnh</span>'

            disk_badge = ' <span class="badge may-do">Ổ C &lt; 10GB</span>' if m.get("canh_bao_o_c") else ""
            vai_html = f'<div class="meta">{_esc(m["vai_tro"])}</div>' if m.get("vai_tro") else ""

            rows_machine.append(
                f"<tr{row_cls}>"
                f"<td><strong>{_esc(m['may'])}</strong>{disk_badge}{vai_html}</td>"
                f"<td>{doing_html}</td>"
                f"<td>{badge_html}{ket_extra}</td>"
                "</tr>"
            )
        machines_html = (
            '<div class="table-wrap"><table><thead><tr>'
            "<th>Máy</th><th>Đang làm gì</th><th>Trạng thái</th>"
            "</tr></thead><tbody>" + "".join(rows_machine) + "</tbody></table></div>"
        )
    else:
        machines_html = '<p class="empty">Chưa ghi nhận máy nào.</p>'

    # Đang chạy chi tiết
    if running:
        rows_run = []
        for item in running:
            nhip_cell = f'<div class="nhip-line">{_esc(item["nhip"])}</div>' if item.get("nhip") else ""
            rows_run.append(
                "<tr>"
                f'<td><a href="{_esc(item["ket_qua_url"])}">{_esc(item["phieu"])}</a>{nhip_cell}</td>'
                f"<td><code>{_esc(item['may'])}</code></td>"
                f"<td>{_esc(item['loai'])}</td>"
                f'<td class="num">{_esc(item["chay_bao_lau"])}</td>'
                f'<td class="num">{_esc(item["nhan_luc_hien_thi"])}</td>'
                "</tr>"
            )
        running_html = (
            '<div class="table-wrap"><table><thead><tr>'
            "<th>Phiếu</th><th>Máy</th><th>Loại</th><th>Chạy bao lâu</th><th>Nhận lúc</th>"
            "</tr></thead><tbody>" + "".join(rows_run) + "</tbody></table></div>"
        )
    else:
        running_html = '<p class="empty">Không có phiếu đang chạy.</p>'

    # Đang chờ
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
            '<div class="table-wrap"><table><thead><tr>'
            "<th>Phiếu</th><th>Máy đích</th><th>Loại</th><th>Trần</th><th>Đề tóm tắt</th>"
            "</tr></thead><tbody>" + "".join(rows_wait) + "</tbody></table></div>"
        )
    else:
        waiting_html = '<p class="empty">Không có phiếu đang chờ.</p>'

    # Xong gần nhất 20 phiếu
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
            '<div class="table-wrap"><table><thead><tr>'
            "<th>Phiếu (bấm xem KET-QUA)</th><th>Máy</th><th>Trạng thái</th>"
            "<th>Phút</th><th>Token</th><th>Xong lúc</th>"
            "</tr></thead><tbody>" + "".join(rows_done) + "</tbody></table></div>"
        )
    else:
        done_html = '<p class="empty">Chưa có phiếu hoàn thành.</p>'

    header_html = _render_header_nav("bang", data)

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
    {header_html}
    {err_html}
    {can_linh_html}
    <section class="card">
      <h2>Máy ({len(machines)})</h2>
      {machines_html}
    </section>
    <section class="card">
      <h2>Đang chạy ({len(running)}) · Đang chờ ({len(waiting)})</h2>
      {running_html}
      {waiting_html if waiting else ""}
    </section>
    <section class="card">
      <h2>Xong gần nhất ({len(done_list)}/{int(data.get("tong_xong") or len(done_list))} phiếu)</h2>
      {done_html}
    </section>
  </div>
</body>
</html>
"""


def _render_usage_bar(label: str, total_gb: float, free_gb: float, warn_low_free: bool = False) -> str:
    """Sinh thanh tiến độ dung lượng RAM / ổ đĩa."""
    tot = max(0.0, float(total_gb or 0.0))
    free = max(0.0, float(free_gb or 0.0))
    used = max(0.0, tot - free)
    pct = min(100, max(0, int(round((used / tot) * 100.0)))) if tot > 0 else 0
    fill_cls = "bar-fill warn" if (warn_low_free or pct >= 90) else "bar-fill"
    return (
        '<div class="bar-row">'
        f"<div><strong>{_esc(label)}</strong>: trống {free:.1f} GB / {tot:.1f} GB (đã dùng {pct}%)</div>"
        f'<div class="bar-track"><div class="{fill_cls}" style="width:{pct}%"></div></div>'
        "</div>"
    )


def render_machines_html(data: dict) -> str:
    """Sinh trang/tab `/may`: mỗi máy 1 thẻ hồ sơ + năng lực, thanh RAM/ổ đĩa, cảnh báo ổ C < 10 GB."""
    refresh_sec = int(data.get("chu_ky_giay") or 30)
    profiles = data.get("ho_so_may") or []
    can_linh = data.get("can_linh") or []
    header_html = _render_header_nav("may", data)
    can_linh_html = _render_can_linh_block(can_linh)

    if profiles:
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
                is_c_low = o_name.strip().upper().rstrip("\\/") == "C:" and float(od.get("trong_gb") or 0) < LOW_DISK_C_THRESHOLD_GB
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
                f"<h2>{_esc(ma)} · <code>{_esc(ten_win)}</code></h2>"
                f'<span class="meta">24h: xong {int(tk24.get("xong") or 0)} / lỗi {int(tk24.get("loi") or 0)}</span>'
                "</div>"
                f'<div class="vai-tro">{_esc(vai_tro)}</div>'
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
        body_html = '<div class="cards-may">' + "".join(cards) + "</div>"
    else:
        body_html = '<section class="card"><p class="empty">Chưa có hồ sơ máy trong hang-doi/may/*.json.</p></section>'

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="{refresh_sec}">
  <title>Hồ sơ máy - LINHX</title>
  <style>{_COMMON_CSS}</style>
</head>
<body>
  <div class="wrap">
    {header_html}
    {can_linh_html}
    {body_html}
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

            if path == "/may":
                status_data = monitor.get_status()
                self._send_html(200, render_machines_html(status_data), head_only=head_only)
                return

            if path == "/api/trang-thai":
                status_data = monitor.get_status()
                self._send_json(200, status_data, head_only=head_only)
                return

            if path == "/api/may":
                status_data = monitor.get_status()
                self._send_json(200, {"may": status_data.get("ho_so_may") or []}, head_only=head_only)
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
