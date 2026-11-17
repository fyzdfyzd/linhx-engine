"""Thu thập trạng thái Crawler và bộ nghe Zalo trên máy hiện tại (không đọc/lưu cookie, nội dung tin, SĐT, thành viên)."""
from __future__ import annotations

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import time

try:
    from runner import hang_doi_git, so_tai_khoan
except ImportError:
    import hang_doi_git  # type: ignore
    import so_tai_khoan  # type: ignore

_PHONE_RE = re.compile(r"(?<!\d)(?:\+?84|0)(?:[\s.\-]?\d){8,10}(?!\d)")

_ZALO_FORBIDDEN_KEYS = frozenset(
    {
        "noi_dung",
        "content",
        "message",
        "messages",
        "tin_nhan",
        "text",
        "body",
        "so_dien_thoai",
        "sdt",
        "phone",
        "phones",
        "tel",
        "thanh_vien",
        "members",
        "member_names",
        "sender",
        "nguoi_gui",
        "author",
        "participants",
    }
)

_CRAWLER_FORBIDDEN_KEYS = frozenset(
    {
        "data",
        "items",
        "articles",
        "html",
        "raw_html",
        "body",
        "content",
        "rows",
        "records",
        "posts",
        "scraped_data",
    }
)

_DEFAULT_CRAWLER_PATHS = (
    r"D:\LINHX\CRAWLER",
    r"D:\LINHX_CRAWLER",
    r"D:\linhx\LUU-TRU",
    r"D:\linhx\mayquet",
    r"C:\linhx\CRAWLER",
    r"C:\linhx\LINHX_CRAWLER",
    r"C:\linhx\LUU-TRU",
    r"C:\linhx\mayquet",
    r"G:\My Drive\WORKFORCE\TOOL\CRAWLER",
)

_DEFAULT_ZALO_PATHS = (
    r"D:\linhx\LAB124",
    r"D:\linhx\ai-goi-hop",
    r"D:\linhx\WF20",
    r"D:\linhx\LAB083",
    r"C:\linhx\LAB124",
    r"C:\linhx\ai-goi-hop",
    r"C:\linhx\WF20",
    r"C:\linhx\LAB083",
)

_ZALO_DIR_KEYWORD_RE = re.compile(r"(?:lab124|ai[-_]?goi[-_]?hop|wf20|lab083|zalo)", re.IGNORECASE)
_CRAWLER_ERR_RE = re.compile(r"(?:\b403\b|\b429\b|captcha|cloudflare|blocked|bị chặn|bi chan|\berror\b|\bloi\b)", re.IGNORECASE)
_CRAWLER_BLOCK_RE = re.compile(r"(?:\b403\b|\b429\b|captcha|cloudflare|blocked|bị chặn|bi chan)", re.IGNORECASE)


def _lam_sach_chuoi_an_toan(text: str, *, che_sdt: bool = False) -> str:
    s = so_tai_khoan._loc_chuoi_nhay_cam(str(text or ""))
    if che_sdt and s:
        s = _PHONE_RE.sub("[ẩn-sđt]", s)
    return " ".join(s.splitlines()).strip()


def lam_sach_ban_ghi_cong_cu(obj, *, loai: str = "crawler"):
    """Làm sạch đệ quy bản ghi crawler/zalo: bỏ mọi khóa bí mật, dữ liệu quét, nội dung tin, SĐT, thành viên."""
    forbidden = _ZALO_FORBIDDEN_KEYS if loai == "zalo" else _CRAWLER_FORBIDDEN_KEYS
    che_sdt = loai == "zalo"
    san = so_tai_khoan.lam_sach_ban_ghi_tai_khoan(obj)

    def _walk(node):
        if isinstance(node, dict):
            sach = {}
            for k, v in node.items():
                k_low = str(k).strip().lower()
                if k_low in forbidden or any(tu in k_low for tu in forbidden):
                    continue
                sach[str(k)] = _walk(v)
            return sach
        if isinstance(node, list):
            return [_walk(x) for x in node]
        if isinstance(node, str):
            return _lam_sach_chuoi_an_toan(node, che_sdt=che_sdt)
        return node

    return _walk(san)


def _tim_repo_mayquet_lan_can() -> list[Path]:
    """Quét mức 1 trong C:\\linhx và D:\\linhx tìm repo git của `fyzdfyzd/mayquet`."""
    ket_qua: list[Path] = []
    seen: set[str] = set()
    for root_str in (r"D:\linhx", r"C:\linhx", r"D:\LINHX", r"C:\LINHX"):
        root = Path(root_str)
        if not root.is_dir():
            continue
        try:
            subdirs = [p for p in root.iterdir() if p.is_dir()]
        except OSError:
            continue
        for sub in subdirs:
            git_cfg = sub / ".git" / "config"
            if not git_cfg.is_file():
                continue
            try:
                txt = git_cfg.read_text(encoding="utf-8", errors="replace").lower()
            except OSError:
                continue
            if "mayquet" in txt or "linhx-crawler" in txt or "linhx_crawler" in txt:
                norm = str(sub.resolve()).lower()
                if norm not in seen:
                    seen.add(norm)
                    ket_qua.append(sub)
    return ket_qua


def _kiem_tra_mcp_linhx_crawler(mcp_out: str | None = None) -> tuple[bool, str]:
    """Kiểm tra MCP `linhx-crawler` bằng `agy mcp list` (không đọc file cấu hình có thể chứa secret)."""
    if mcp_out is not None:
        return ("linhx-crawler" in mcp_out.lower()), "MCP: linhx-crawler (override)"
    agy_bin = so_tai_khoan._tim_thuc_thi_agy(os.environ.get("AGY_CMD", "agy"))
    if not agy_bin:
        return False, "MCP: agy mcp list (linhx-crawler) [khong tim thay agy]"
    kw = {"creationflags": 0x08000000} if os.name == "nt" else {}
    try:
        proc = subprocess.run(
            [agy_bin, "mcp", "list"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=6,
            **kw,
        )
        raw = ((proc.stdout or "") + "\n" + (proc.stderr or "")).lower()
        return ("linhx-crawler" in raw), "MCP: agy mcp list (linhx-crawler)"
    except Exception:
        return False, "MCP: agy mcp list (linhx-crawler)"


def _doc_loi_cuoi_tu_log(log_path: Path) -> str:
    """Đọc 40 dòng cuối của file log để lấy dòng lỗi/bị chặn gần nhất (không đọc toàn bộ)."""
    try:
        lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()[-40:]
    except OSError:
        return ""
    for line in reversed(lines):
        s = line.strip()
        if s and _CRAWLER_ERR_RE.search(s):
            return _lam_sach_chuoi_an_toan(s)[:180]
    return ""


def _dem_muc_trong_thu_muc_du_lieu(thu_muc: Path) -> tuple[int, str]:
    """Đếm số bài/trang và lấy thời điểm cập nhật mới nhất mà không giữ nội dung đã quét."""
    tong = 0
    max_mtime = 0.0
    try:
        for p in thu_muc.rglob("*"):
            if not p.is_file():
                continue
            ext = p.suffix.lower()
            try:
                st = p.stat()
                if st.st_mtime > max_mtime:
                    max_mtime = st.st_mtime
            except OSError:
                continue
            if ext == ".jsonl":
                try:
                    with p.open("r", encoding="utf-8", errors="replace") as fh:
                        tong += sum(1 for ln in fh if ln.strip())
                except OSError:
                    pass
            elif ext in (".md", ".json", ".html", ".htm", ".txt"):
                if p.name.lower() not in ("status.json", "trang-thai.json", "stats.json", "summary.json", "meta.json"):
                    tong += 1
    except OSError:
        pass
    iso_str = ""
    if max_mtime > 0:
        dt = datetime.fromtimestamp(max_mtime, tz=so_tai_khoan._local_tz())
        iso_str = so_tai_khoan._dinh_dang_iso(dt)
    return tong, iso_str


def _trich_nguon_crawler_tu_thu_muc(root: Path) -> list[dict]:
    """Đọc thông tin các nguồn/adapter trong 1 thư mục crawler mà không chép nội dung đã quét hay cookie."""
    nguon_list: list[dict] = []
    seen_names: set[str] = set()

    # 1. Đọc file trạng thái tổng hợp nếu có (`status.json`, `trang-thai.json`, `stats.json`, `summary.json`)
    for fname in ("status.json", "trang-thai.json", "stats.json", "summary.json"):
        st_file = root / fname
        if not st_file.is_file():
            continue
        try:
            parsed = json.loads(st_file.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            continue
        items = []
        if isinstance(parsed, dict):
            for key in ("nguon", "sources", "adapters", "items"):
                if isinstance(parsed.get(key), list):
                    items = [x for x in parsed[key] if isinstance(x, dict)]
                    break
        elif isinstance(parsed, list):
            items = [x for x in parsed if isinstance(x, dict)]
        for item in items:
            ten_ng = str(item.get("nguon") or item.get("source") or item.get("adapter") or item.get("ten") or "").strip()
            if not ten_ng or ten_ng.lower() in seen_names:
                continue
            seen_names.add(ten_ng.lower())
            loi = _lam_sach_chuoi_an_toan(str(item.get("loi_gan_nhat") or item.get("last_error") or item.get("error") or ""))[:180]
            try:
                so_trang = int(item.get("so_trang") if item.get("so_trang") is not None else (item.get("count") or item.get("articles") or 0))
            except (ValueError, TypeError):
                so_trang = 0
            lan_cuoi = str(item.get("lan_chay_cuoi") or item.get("last_run") or item.get("updated_at") or "").strip()
            data_dir = str(item.get("thu_muc_du_lieu") or item.get("data_dir") or root).strip()
            tt = str(item.get("trang_thai") or "").strip().lower()
            if tt not in ("ok", "loi", "bi_chan", "chua_chay"):
                if loi and _CRAWLER_BLOCK_RE.search(loi):
                    tt = "bi_chan"
                elif loi:
                    tt = "loi"
                elif lan_cuoi or so_trang > 0:
                    tt = "ok"
                else:
                    tt = "chua_chay"
            nguon_list.append(
                {
                    "nguon": ten_ng,
                    "lan_chay_cuoi": lan_cuoi,
                    "so_trang": max(0, so_trang),
                    "loi_gan_nhat": loi,
                    "thu_muc_du_lieu": data_dir,
                    "trang_thai": tt,
                }
            )

    # 2. Quét thư mục dữ liệu con (`data/`, `output/`, `luu-tru/`, `bai/`, `sources/`)
    for data_sub_name in ("data", "output", "luu-tru", "bai", "sources"):
        data_root = root / data_sub_name
        if not data_root.is_dir():
            continue
        try:
            children = sorted([p for p in data_root.iterdir() if p.is_dir()], key=lambda p: p.name.lower())
        except OSError:
            continue
        for ch in children:
            if ch.name.lower() in seen_names:
                continue
            seen_names.add(ch.name.lower())
            so_trang, lan_cuoi = _dem_muc_trong_thu_muc_du_lieu(ch)
            loi = ""
            for cand_log in (ch / "error.log", ch / "crawler.log", root / "logs" / f"{ch.name}.log"):
                if cand_log.is_file():
                    loi = _doc_loi_cuoi_tu_log(cand_log)
                    if loi:
                        break
            tt = "bi_chan" if (loi and _CRAWLER_BLOCK_RE.search(loi)) else ("loi" if loi else ("ok" if so_trang > 0 else "chua_chay"))
            nguon_list.append(
                {
                    "nguon": ch.name,
                    "lan_chay_cuoi": lan_cuoi,
                    "so_trang": so_trang,
                    "loi_gan_nhat": loi,
                    "thu_muc_du_lieu": str(ch),
                    "trang_thai": tt,
                }
            )

    # 3. Nếu thư mục chỉ có file adapter/*.py mà chưa có dữ liệu/status
    for ad_sub in ("adapters", "nguon", "spiders"):
        ad_dir = root / ad_sub
        if not ad_dir.is_dir():
            continue
        try:
            files = sorted([p for p in ad_dir.iterdir() if p.is_file() and p.suffix == ".py" and not p.stem.startswith("_")], key=lambda p: p.stem.lower())
        except OSError:
            continue
        for pyf in files:
            if pyf.stem.lower() in seen_names:
                continue
            seen_names.add(pyf.stem.lower())
            nguon_list.append(
                {
                    "nguon": pyf.stem,
                    "lan_chay_cuoi": "",
                    "so_trang": 0,
                    "loi_gan_nhat": "",
                    "thu_muc_du_lieu": str(root),
                    "trang_thai": "chua_chay",
                }
            )

    return nguon_list


def thu_thap_crawler_may(
    ma_may: str = "",
    *,
    duong_dan_thu: list[str | Path] | None = None,
    mcp_out: str | None = None,
) -> dict:
    """Thu thập trạng thái các nguồn crawler trên máy (không lưu dữ liệu đã quét hay cookie)."""
    ma_chuan, _ = so_tai_khoan.xac_dinh_ma_may(ma_may)
    ung_vien: list[str] = (
        [str(p) for p in duong_dan_thu]
        if duong_dan_thu is not None
        else list(_DEFAULT_CRAWLER_PATHS)
    )
    if duong_dan_thu is None:
        for repo_mq in _tim_repo_mayquet_lan_can():
            s_repo = str(repo_mq)
            if s_repo.lower() not in {x.lower() for x in ung_vien}:
                ung_vien.append(s_repo)

    da_thu: list[str] = []
    seen_lower: set[str] = set()
    thu_muc_tim_thay: list[str] = []
    nguon_list: list[dict] = []

    for raw_p in ung_vien:
        norm = raw_p.strip()
        if not norm:
            continue
        low = norm.lower()
        if low in seen_lower:
            continue
        seen_lower.add(low)
        da_thu.append(norm)
        p = Path(norm)
        if p.is_dir():
            thu_muc_tim_thay.append(str(p))
            nguon_list.extend(_trich_nguon_crawler_tu_thu_muc(p))

    co_mcp, mcp_label = _kiem_tra_mcp_linhx_crawler(mcp_out=mcp_out)
    da_thu.append(mcp_label)
    if co_mcp and not any(x.get("nguon") == "linhx-crawler" for x in nguon_list):
        nguon_list.append(
            {
                "nguon": "linhx-crawler",
                "lan_chay_cuoi": "",
                "so_trang": 0,
                "loi_gan_nhat": "",
                "thu_muc_du_lieu": "MCP linhx-crawler",
                "trang_thai": "ok",
            }
        )

    du_lieu = {
        "ma_may": ma_chuan,
        "ten_windows": platform.node() or ma_chuan,
        "tim_thay": bool(thu_muc_tim_thay or co_mcp or nguon_list),
        "thu_muc_crawler": thu_muc_tim_thay,
        "mcp_linhx_crawler": co_mcp,
        "nguon": nguon_list,
        "duong_dan_da_thu": da_thu,
        "cap_nhat_luc": so_tai_khoan._dinh_dang_iso(so_tai_khoan._now_dt()),
    }
    return lam_sach_ban_ghi_cong_cu(du_lieu, loai="crawler")


def _tim_thu_muc_zalo_mac_dinh() -> list[str]:
    ung_vien = list(_DEFAULT_ZALO_PATHS)
    seen = {x.lower() for x in ung_vien}
    for base_str in (r"D:\linhx", r"C:\linhx", r"D:\linhx\LAB", r"C:\linhx\LAB"):
        base = Path(base_str)
        if not base.is_dir():
            continue
        try:
            for sub in sorted(base.iterdir(), key=lambda p: p.name.lower()):
                if sub.is_dir() and _ZALO_DIR_KEYWORD_RE.search(sub.name):
                    s = str(sub)
                    if s.lower() not in seen:
                        seen.add(s.lower())
                        ung_vien.append(s)
        except OSError:
            continue
    return ung_vien


def _truy_van_tien_trinh_zalo_windows() -> list[dict]:
    if os.name != "nt":
        return []
    ps_cmd = (
        "Get-CimInstance Win32_Process | Where-Object { "
        "($_.Name -match 'zalo' -or "
        "($_.CommandLine -match 'ai-goi-hop|lab124|wf20|lab083|zalo.{0,40}(?:listener|cdp|bot|bridge|listen|watch)' "
        "-and $_.CommandLine -notmatch 'quet_cong_cu_may|zalo\\.ps1|pytest')) "
        "} | Select-Object Name, ProcessId, "
        "@{n='cdp';e={$_.CommandLine -match '--remote-debugging-port'}} | ConvertTo-Json -Compress"
    )
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=8,
            creationflags=0x08000000,
        )
        raw = (proc.stdout or "").strip()
        if not raw:
            return []
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return [parsed]
        if isinstance(parsed, list):
            return [x for x in parsed if isinstance(x, dict)]
    except Exception:
        pass
    return []


def _truy_van_lich_zalo_windows() -> list[dict]:
    if os.name != "nt":
        return []
    ps_cmd = (
        "Get-ScheduledTask | Where-Object { $_.TaskName -match 'zalo|ai-goi-hop|wf20|lab083|lab124' } "
        "| Select-Object TaskName, State | ConvertTo-Json -Compress"
    )
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=8,
            creationflags=0x08000000,
        )
        raw = (proc.stdout or "").strip()
        if not raw:
            return []
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return [parsed]
        if isinstance(parsed, list):
            return [x for x in parsed if isinstance(x, dict)]
    except Exception:
        pass
    return []


def _doc_bo_nghe_zalo_tu_thu_muc(root: Path, running_procs: list[dict], tasks: list[dict]) -> dict:
    """Trích thông tin an toàn (đang chạy, danh sách tên nhóm, giờ tin cuối, lỗi) từ 1 thư mục bộ nghe Zalo."""
    nhom_set: list[str] = []
    seen_nhom: set[str] = set()
    tin_cuoi = ""
    loi_gan_nhat = ""
    dang_chay: bool | None = None

    def _them_nhom(val) -> None:
        if isinstance(val, str):
            parts = [val]
        elif isinstance(val, list):
            parts = [str(x.get("ten") or x.get("name") or x) if isinstance(x, dict) else str(x) for x in val]
        else:
            return
        for raw_n in parts:
            ten_n = _lam_sach_chuoi_an_toan(raw_n, che_sdt=True)[:80]
            if ten_n and ten_n.lower() not in seen_nhom:
                seen_nhom.add(ten_n.lower())
                nhom_set.append(ten_n)

    for fname in ("status.json", "trang-thai.json", "state.json", "groups.json", "nhom.json", "config.json"):
        f_path = root / fname
        if not f_path.is_file():
            continue
        try:
            obj = json.loads(f_path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            continue
        if isinstance(obj, dict):
            if isinstance(obj.get("dang_chay"), bool):
                dang_chay = obj["dang_chay"]
            elif isinstance(obj.get("running"), bool):
                dang_chay = obj["running"]
            for k in ("nhom", "groups", "group_names", "watched_groups"):
                if k in obj:
                    _them_nhom(obj[k])
            if not tin_cuoi:
                tin_cuoi = str(obj.get("tin_cuoi_luc") or obj.get("last_message_at") or obj.get("last_msg_at") or "").strip()
            if not loi_gan_nhat:
                loi_gan_nhat = _lam_sach_chuoi_an_toan(
                    str(obj.get("loi_gan_nhat") or obj.get("last_error") or obj.get("error") or ""),
                    che_sdt=True,
                )[:180]
        elif isinstance(obj, list) and fname in ("groups.json", "nhom.json"):
            _them_nhom(obj)

    if dang_chay is None:
        name_low = root.name.lower()
        dang_chay = any(
            name_low in str(pr.get("Name") or "").lower()
            or (name_low in ("lab124", "ai-goi-hop") and bool(pr.get("cdp")))
            for pr in running_procs
        ) or any(
            name_low in str(tk.get("TaskName") or "").lower()
            and str(tk.get("State") or "").lower() in ("running", "ready", "3", "4")
            for tk in tasks
        )

    return {
        "ten": root.name,
        "duong_dan": str(root),
        "dang_chay": bool(dang_chay),
        "nhom": nhom_set,
        "tin_cuoi_luc": tin_cuoi,
        "loi_gan_nhat": loi_gan_nhat,
    }


def thu_thap_zalo_may(
    ma_may: str = "",
    *,
    duong_dan_thu: list[str | Path] | None = None,
    processes: list[dict] | None = None,
    tasks: list[dict] | None = None,
) -> dict:
    """Thu thập danh sách bộ nghe Zalo trên máy (chỉ tên nhóm, trạng thái chạy, giờ tin cuối, lỗi)."""
    ma_chuan, _ = so_tai_khoan.xac_dinh_ma_may(ma_may)
    ung_vien = [str(p) for p in duong_dan_thu] if duong_dan_thu is not None else _tim_thu_muc_zalo_mac_dinh()

    proc_list = processes if processes is not None else _truy_van_tien_trinh_zalo_windows()
    task_list = tasks if tasks is not None else _truy_van_lich_zalo_windows()

    da_thu: list[str] = []
    seen_lower: set[str] = set()
    bo_nghe_list: list[dict] = []

    for raw_p in ung_vien:
        norm = raw_p.strip()
        if not norm or norm.lower() in seen_lower:
            continue
        seen_lower.add(norm.lower())
        da_thu.append(norm)
        p = Path(norm)
        if p.is_dir():
            bo_nghe_list.append(_doc_bo_nghe_zalo_tu_thu_muc(p, proc_list, task_list))

    da_thu.extend(
        [
            "Win32_Process (*zalo*)",
            "ScheduledTask (*zalo*)",
            "Zalo PC CDP (LAB124 ai-goi-hop)",
        ]
    )

    for pr in proc_list:
        p_name = str(pr.get("Name") or pr.get("ten") or "").strip()
        if not p_name:
            continue
        if not any(bn["ten"].lower() in p_name.lower() or p_name.lower() in bn["ten"].lower() for bn in bo_nghe_list):
            bo_nghe_list.append(
                {
                    "ten": p_name + (" (CDP)" if pr.get("cdp") else ""),
                    "duong_dan": f"Process:{p_name}",
                    "dang_chay": True,
                    "nhom": list(pr.get("nhom") or []) if isinstance(pr.get("nhom"), list) else [],
                    "tin_cuoi_luc": str(pr.get("tin_cuoi_luc") or ""),
                    "loi_gan_nhat": _lam_sach_chuoi_an_toan(str(pr.get("loi_gan_nhat") or ""), che_sdt=True),
                }
            )

    for tk in task_list:
        t_name = str(tk.get("TaskName") or tk.get("ten") or "").strip()
        if not t_name:
            continue
        st_raw = str(tk.get("State") or "").lower()
        is_run = st_raw in ("running", "4")
        if not any(bn["ten"].lower() in t_name.lower() or t_name.lower() in bn["ten"].lower() for bn in bo_nghe_list):
            bo_nghe_list.append(
                {
                    "ten": t_name,
                    "duong_dan": f"Task:{t_name}",
                    "dang_chay": is_run,
                    "nhom": [],
                    "tin_cuoi_luc": "",
                    "loi_gan_nhat": "",
                }
            )

    du_lieu = {
        "ma_may": ma_chuan,
        "ten_windows": platform.node() or ma_chuan,
        "tim_thay": bool(bo_nghe_list),
        "bo_nghe": bo_nghe_list,
        "duong_dan_da_thu": da_thu,
        "cap_nhat_luc": so_tai_khoan._dinh_dang_iso(so_tai_khoan._now_dt()),
    }
    return lam_sach_ban_ghi_cong_cu(du_lieu, loai="zalo")


def _ban_so_sanh_json(du_lieu: dict) -> dict:
    ban = json.loads(json.dumps(du_lieu, ensure_ascii=False))
    ban.pop("cap_nhat_luc", None)
    return ban


def cap_nhat_cong_cu_may_git(
    loai: str,
    cfg: dict,
    du_lieu_moi: dict,
    *,
    ep_ghi: bool = False,
) -> tuple[bool, Path | None, dict]:
    """Ghi `hang-doi/may/<ma_may>-<loai>.json`, commit và push lên nhánh `hang-doi`."""
    ma_may = str(cfg.get("tho") or "may").strip().lower()
    ten_tep = hang_doi_git._ten_phieu_an_toan(ma_may)
    du_lieu_sach = lam_sach_ban_ghi_cong_cu(du_lieu_moi, loai=loai)
    _, _, remote, nhanh = hang_doi_git._duong_dan_wt(cfg)

    with hang_doi_git._khoa_tep(hang_doi_git._duong_dan_khoa_wt(cfg), timeout=20.0):
        for lan in range(hang_doi_git.SO_LAN_THU_PUSH_NHIP):
            wt = hang_doi_git.dam_bao_worktree(cfg)
            if wt is None:
                return False, None, du_lieu_sach
            goc_hd = hang_doi_git.thu_muc_hang_doi(wt)
            tm_may = goc_hd / "may"
            tep_json = tm_may / f"{ten_tep}-{loai}.json"

            du_lieu_cu = None
            if tep_json.is_file():
                try:
                    du_lieu_cu = json.loads(tep_json.read_text(encoding="utf-8", errors="replace"))
                except (OSError, ValueError):
                    du_lieu_cu = None

            if not ep_ghi and isinstance(du_lieu_cu, dict) and _ban_so_sanh_json(du_lieu_cu) == _ban_so_sanh_json(du_lieu_sach):
                return False, tep_json, du_lieu_sach

            tm_may.mkdir(parents=True, exist_ok=True)
            tep_json.write_text(json.dumps(du_lieu_sach, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            hang_doi_git._commit_git(wt, ma_may, f"may: cap nhat {loai} {ma_may}")
            pull_rb = hang_doi_git.chay_git(["pull", "--rebase", remote, nhanh], cwd=wt, check=False, timeout=45)
            if pull_rb.returncode != 0:
                hang_doi_git.chay_git(["rebase", "--abort"], cwd=wt, check=False, timeout=15)
                continue
            push = hang_doi_git.chay_git(["push", remote, f"HEAD:refs/heads/{nhanh}"], cwd=wt, check=False, timeout=45)
            if push.returncode == 0:
                return True, tep_json, du_lieu_sach
            time.sleep(0.05 * (lan + 1))
    return False, None, du_lieu_sach


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Thu thập trạng thái crawler hoặc Zalo listener trên máy.")
    parser.add_argument("--loai", choices=("crawler", "zalo"), required=True, help="Loại công cụ cần kiểm tra.")
    parser.add_argument("--may", default="", help="Mã máy (mặc định đọc từ tho.env / LINHX_THO).")
    parser.add_argument("--repo-hang-doi", default="", help="Đường dẫn repo chứa nhánh hang-doi.")
    parser.add_argument("--xuat-json", default="", help="Ghi bản sao JSON ra đường dẫn chỉ định.")
    parser.add_argument("--thu-muc-thu", action="append", default=[], help="Đường dẫn cần thử (lặp nhiều lần nếu muốn).")
    parser.add_argument("--cap-nhat-git", action="store_true", help="Ghi và push lên nhánh hang-doi.")
    parser.add_argument("--ep-ghi", action="store_true", help="Ép commit kể cả khi dữ liệu không đổi.")
    args = parser.parse_args(argv)

    ma_may, repo_tu_env = so_tai_khoan.xac_dinh_ma_may(args.may)
    repo_hd = Path(args.repo_hang_doi) if args.repo_hang_doi else repo_tu_env
    ds_thu = args.thu_muc_thu if args.thu_muc_thu else None

    if args.loai == "crawler":
        du_lieu = thu_thap_crawler_may(ma_may=ma_may, duong_dan_thu=ds_thu)
    else:
        du_lieu = thu_thap_zalo_may(ma_may=ma_may, duong_dan_thu=ds_thu)

    tep_git = None
    da_push = None
    if args.cap_nhat_git:
        if repo_hd is None:
            print("Khong xac dinh duoc repo hang-doi de commit.", file=sys.stderr)
            return 1
        cfg = {
            "tho": ma_may,
            "repo_hang_doi": str(repo_hd),
            "nhanh_hang_doi": os.environ.get("LINHX_NHANH_HANG_DOI", "hang-doi"),
            "remote_hang_doi": os.environ.get("LINHX_REMOTE_HANG_DOI", "origin"),
            "wt_hang_doi": os.environ.get("LINHX_WT_HANG_DOI", ""),
        }
        da_push, tep_git, du_lieu = cap_nhat_cong_cu_may_git(
            args.loai,
            cfg,
            du_lieu,
            ep_ghi=bool(args.ep_ghi),
        )

    if args.xuat_json:
        p_out = Path(args.xuat_json)
        p_out.parent.mkdir(parents=True, exist_ok=True)
        p_out.write_text(json.dumps(du_lieu, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"loai: {args.loai} | may: {du_lieu.get('ma_may')} | tim_thay: {du_lieu.get('tim_thay')}")
    if tep_git is not None:
        print(f"tep_json: {tep_git}")
    if da_push is not None:
        print(f"da_commit_push: {'co' if da_push else 'khong_doi_hoac_bo_qua'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
