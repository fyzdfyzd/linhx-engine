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

/* Thanh chuyển 3 Tab (Segmented Control chuẩn Apple) */
.seg-tabs {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
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
  font-size: 15px;
  font-weight: 600;
  min-height: 44px;
  padding: 8px 6px;
  border-radius: 10px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  white-space: nowrap;
  transition: background 0.18s ease, color 0.18s ease, box-shadow 0.18s ease;
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
.may-ranh { background: var(--idle-bg); color: var(--idle-fg); }
.tt-dung, .may-ket { background: var(--warn-bg); color: var(--warn-fg); }
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
"""

_DASHBOARD_JS = r"""
(function () {
  var REFRESH_MS = 15000;
  var appRoot = document.getElementById("bang-app");
  if (!appRoot) return;

  var state = {
    activeTab: appRoot.getAttribute("data-initial-tab") || "tong-quan",
    machineFilter: "tat-ca",
    expandedMachines: {},
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
    if (["tong-quan", "phieu", "may"].indexOf(tabName) === -1) {
      tabName = "tong-quan";
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
      var nextPath = tabName === "may" ? "/may" : (tabName === "phieu" ? "/phieu" : "/");
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
        workHtml = '<div class="may-work-box"><div class="work-top">' +
          '<div class="work-ticket"><a href="' + esc(hrefRun) + '">' + esc(m.dang_lam_phieu) + "</a>" + esc(extraTxt) + "</div>" +
          '<div class="work-time">' + phutInt + " phút / " + tranInt + "p</div></div>" +
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
        rRows.push(
          '<div class="ticket-row"><div class="ticket-row-head">' +
          '<a class="ticket-main-link" href="' + esc(it.ket_qua_url) + '">' + esc(it.phieu) + "</a>" +
          '<div class="ticket-tags"><span class="tag-chip">' + esc(it.may) + "</span>" +
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
      var bCls = (st === "xong" || st === "loi" || st === "dung") ? ("badge tt-" + st) : "badge tt-loi";
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

    var cntPhieu = (data.dang_chay || []).length + (data.dang_cho || []).length;
    var tabPhieuEl = document.getElementById("tab-lbl-phieu");
    if (tabPhieuEl) tabPhieuEl.textContent = "Phiếu (" + cntPhieu + ")";

    var nProf = (data.ho_so_may && data.ho_so_may.length) || 0;
    var nMay = (data.may && data.may.length) || 0;
    var cntMay = Math.max(nProf, nMay);
    var tabMayEl = document.getElementById("tab-lbl-may");
    if (tabMayEl) tabMayEl.textContent = "Máy (" + cntMay + ")";

    var ovEl = document.getElementById("overview-machines-slot");
    if (ovEl) ovEl.innerHTML = renderOverviewMachines(data);

    var phieuEl = document.getElementById("phieu-content-slot");
    if (phieuEl) phieuEl.innerHTML = renderTicketsTab(data);

    var mayEl = document.getElementById("may-content-slot");
    if (mayEl) mayEl.innerHTML = renderProfilesTab(data);
  }

  function findAttrEl(attr, val) {
    var list = document.querySelectorAll("[" + attr + "]");
    for (var i = 0; i < list.length; i++) {
      if (list[i].getAttribute(attr) === val) return list[i];
    }
    return null;
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
            work_html = (
                '<div class="may-work-box">'
                '<div class="work-top">'
                f'<div class="work-ticket"><a href="{_esc(href_run)}">{_esc(dang_phieu)}</a>{_esc(extra_txt)}</div>'
                f'<div class="work-time">{phut_so} phút / {tran_so}p</div>'
                "</div>"
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
            rows_run.append(
                '<div class="ticket-row">'
                '<div class="ticket-row-head">'
                f'<a class="ticket-main-link" href="{_esc(item["ket_qua_url"])}">{_esc(item["phieu"])}</a>'
                '<div class="ticket-tags">'
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
        badge_cls = f"badge tt-{st}" if st in ("xong", "loi", "dung") else "badge tt-loi"
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


def _render_profiles_section(data: dict) -> str:
    """Sinh nội dung tab Máy: hồ sơ năng lực, thanh RAM/ổ đĩa, cảnh báo ổ C < 10 GB."""
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


def render_app_html(data: dict, active_tab: str = "tong-quan") -> str:
    """Sinh giao diện bảng theo dõi chuẩn Apple tối giản, đọc trong 5 giây, tự làm mới 15s qua fetch."""
    if active_tab not in ("tong-quan", "phieu", "may"):
        active_tab = "tong-quan"

    refresh_sec = int(data.get("chu_ky_giay") or 30)
    can_linh = data.get("can_linh") or []
    running = data.get("dang_chay") or []
    waiting = data.get("dang_cho") or []
    done_list = data.get("xong_gan_nhat") or []
    machines = data.get("may") or []
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

    cnt_phieu_active = len(running) + len(waiting)
    cnt_may = max(len(data.get("ho_so_may") or []), len(machines))

    def _tab_attrs(name: str) -> str:
        is_act = active_tab == name
        cls = "seg-btn is-active" if is_act else "seg-btn"
        sel = "true" if is_act else "false"
        return f'class="{cls}" data-tab="{name}" aria-selected="{sel}"'

    hid_tq = "" if active_tab == "tong-quan" else " hidden"
    hid_ph = "" if active_tab == "phieu" else " hidden"
    hid_ma = "" if active_tab == "may" else " hidden"

    overview_html = _render_overview_machines_section(data)
    tickets_html = _render_tickets_section(data)
    profiles_html = _render_profiles_section(data)
    safe_json = _safe_inline_json(data)

    page_title = (
        "Hồ sơ máy · LINHX"
        if active_tab == "may"
        else ("Phiếu hàng đợi · LINHX" if active_tab == "phieu" else "Bảng theo dõi · LINHX")
    )

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
      <button type="button" role="tab" {_tab_attrs("tong-quan")}>Tổng quan</button>
      <button type="button" role="tab" {_tab_attrs("phieu")}><span id="tab-lbl-phieu">Phiếu ({cnt_phieu_active})</span></button>
      <button type="button" role="tab" {_tab_attrs("may")}><span id="tab-lbl-may">Máy ({cnt_may})</span></button>
    </nav>

    <main>
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
    </main>
  </div>
  <script type="application/json" id="bang-init-data">{safe_json}</script>
  <script>{_DASHBOARD_JS}</script>
</body>
</html>
"""


def render_dashboard_html(data: dict) -> str:
    """Sinh HTML trang chủ mở sẵn tab Tổng quan."""
    return render_app_html(data, active_tab="tong-quan")


def render_tickets_page_html(data: dict) -> str:
    """Sinh HTML mở sẵn tab Phiếu."""
    return render_app_html(data, active_tab="phieu")


def render_machines_html(data: dict) -> str:
    """Sinh HTML mở sẵn tab Máy (`/may`)."""
    return render_app_html(data, active_tab="may")


def render_ticket_html(detail: dict) -> str:
    """Sinh HTML hiển thị nội dung KET-QUA.md của một phiếu theo phong cách tối giản đồng bộ."""
    st = detail.get("trang_thai") or "xong"
    badge_cls = f"badge tt-{st}" if st in ("xong", "loi", "dung", "dang") else "badge may-ranh"
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

            if path == "/phieu":
                status_data = monitor.get_status()
                self._send_html(200, render_tickets_page_html(status_data), head_only=head_only)
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
