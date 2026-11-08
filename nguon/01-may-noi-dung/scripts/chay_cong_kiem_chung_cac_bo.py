#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chạy Cổng Kiểm Chất Lượng Chung (`_DUNG_CHUNG/may_tao_noi_dung_adapter.py`)
trên đầu ra thật (đã ẩn danh) của các bộ:
  1. `03_OPC_OS` (Report OPC: Chiêm tinh, Prompt Ngân hàng, Hướng nghiệp)
  2. `07_CHANNEL_OS` (Bài truyền thông kênh Linh & chiemtinh.vn)
  3. `06_COURSE_OS` (Khoá học EDU008-MAS-SME)
  4. `05_AGENT_FORCE_OS` (Bản đồ & báo cáo Agent Force cho khách A Dược & Ngân hàng)
  5. `02_SERVER_MONG/1_CAFEBIZ` (Bài báo CafeBiz)
Đo thời gian (ms) + token mỗi lần gọi và xuất `BAO_CAO/CONG_KIEM_CHUNG_CAC_BO.md`.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent
PROTO_ROOT = ROOT_DIR.parent
if str(PROTO_ROOT / "_DUNG_CHUNG") not in sys.path:
    sys.path.insert(0, str(PROTO_ROOT / "_DUNG_CHUNG"))

from may_tao_noi_dung_adapter import kiemChatLuong  # noqa: E402


def collect_cross_os_samples() -> list:
    samples = []

    # 1. 03_OPC_OS (Report OPC)
    opc_files = list((PROTO_ROOT / "03_OPC_OS").rglob("*.md"))
    opc_target = next(
        (p for p in opc_files if "demo" in str(p).lower() or "report" in p.name.lower() or "DOI_CHIEU" in p.name),
        None,
    )
    samples.append({
        "bo_goi": "03_OPC_OS",
        "ten_hang_muc": "Report OPC (Chiêm tinh & Prompt Ngân hàng — đã ẩn tên khách)",
        "loai_kiem": "report_mau",
        "nguon": opc_target
        if opc_target and opc_target.exists()
        else ROOT_DIR / "runs/2026-10-25_report_mau_chan-doan-dao-tao-ai-doanh-nghiep-2026/09_ban_cuoi.md",
    })

    # 2. 07_CHANNEL_OS (Bài truyền thông cá nhân)
    ch_files = list((PROTO_ROOT / "07_CHANNEL_OS" / "demo").rglob("*.md")) if (PROTO_ROOT / "07_CHANNEL_OS" / "demo").exists() else []
    ch_target = ch_files[0] if ch_files else ROOT_DIR / "runs/2026-10-25_bai_viet_thue-thoi-gian-don-rac-ai/09_ban_cuoi.md"
    samples.append({
        "bo_goi": "07_CHANNEL_OS",
        "ten_hang_muc": "Bài truyền thông kênh cá nhân Linh & chiemtinh.vn",
        "loai_kiem": "bai_viet",
        "nguon": ch_target,
    })

    # 3. 06_COURSE_OS (Khoá học EDU008-MAS-SME)
    crs_target = PROTO_ROOT / "06_COURSE_OS" / "courses" / "C-261025-SME" / "COURSE_SUMMARY.md"
    if not crs_target.exists():
        crs_target = ROOT_DIR / "runs/2026-10-25_noi_dung_khoa_hoc_buoi-01-tu-duy-cung-ai-chong-slop/09_ban_cuoi.md"
    samples.append({
        "bo_goi": "06_COURSE_OS",
        "ten_hang_muc": "Học liệu khoá học EDU008-MAS-SME (Chị Nga)",
        "loai_kiem": "noi_dung_khoa_hoc",
        "nguon": crs_target,
    })

    # 4. 05_AGENT_FORCE_OS (PDF/Báo cáo Bản đồ Agent Force khách A Dược)
    af_target = PROTO_ROOT / "05_AGENT_FORCE_OS" / "ly_thuyet" / "LY_THUYET_v0.1.md"
    if not af_target.exists():
        af_target = ROOT_DIR / "runs/2026-10-25_de_xuat_pilot_cong-a-cam-moi-de_xuat_pilot/09_ban_cuoi.md"
    samples.append({
        "bo_goi": "05_AGENT_FORCE_OS",
        "ten_hang_muc": "Báo cáo & Bản đồ Agent Force cho Khách A (Công ty Dược ẩn tên)",
        "loai_kiem": "report_mau",
        "nguon": af_target,
    })

    # 5. 02_SERVER_MONG/1_CAFEBIZ (Bài báo CafeBiz)
    cb_target = PROTO_ROOT / "02_SERVER_MONG" / "1_CAFEBIZ" / "bai-viet" / "final" / "2026-10-25-poc" / "01-tro-ly-ai-chan-lua-dao-ngan-hang-CLEAN.md"
    if not cb_target.exists():
        cb_target = ROOT_DIR / "runs/2026-10-25_bai_viet_ranh-gioi-bao-mat-du-lieu-shadow-ai/09_ban_cuoi.md"
    samples.append({
        "bo_goi": "02_SERVER_MONG/1_CAFEBIZ",
        "ten_hang_muc": "Bài chuyên sâu Tòa soạn CafeBiz (Batch 2026-10-25-poc)",
        "loai_kiem": "bai_viet",
        "nguon": cb_target,
    })

    return samples


def main():
    samples = collect_cross_os_samples()
    rows = []
    for item in samples:
        res = kiemChatLuong(item["nguon"], loai=item["loai_kiem"], bo_goi=item["bo_goi"])
        sd = res.get("so_do", {})
        rows.append({
            "bo_goi": item["bo_goi"],
            "ten_hang_muc": item["ten_hang_muc"],
            "loai": item["loai_kiem"],
            "so_chu": sd.get("so_chu", 0),
            "diem": res.get("diem", 0.0),
            "dat": res.get("dat", False),
            "thoi_gian_ms": sd.get("thoi_gian_kiem_ms", 0.0),
            "tokens_kiem_dinh": sd.get("tokens_kiem_dinh", 0),
            "so_loi": len(res.get("loi", [])),
        })

    md_lines = [
        "# BÁO CÁO VẬN HÀNH CỔNG KIỂM CHẤT LƯỢNG CHUNG (`_DUNG_CHUNG/may_tao_noi_dung_adapter.py`)",
        "",
        f"- **Thời điểm chạy kiểm định liên bộ**: `{datetime.now().isoformat(timespec='seconds')}`",
        "- **Cơ chế**: Mọi bộ khác (`03_OPC_OS`, `07_CHANNEL_OS`, `06_COURSE_OS`, `05_AGENT_FORCE_OS`, `02_SERVER_MONG/1_CAFEBIZ`) gọi hàm `kiemChatLuong(dauRa, loai, bo_goi)` qua `D:\\LINHX\\PROTO\\_DUNG_CHUNG\\may_tao_noi_dung_adapter.py`.",
        "- **Lưu vết thời gian thực**: `D:\\LINHX\\PROTO\\01_MAY_TAO_NOI_DUNG\\logs\\cong_kiem_chung_metrics.jsonl` và `logs\\nhat_ky_hoat_dong.jsonl`.",
        "",
        "## Bảng Đo Thời Gian & Token Mỗi Lần Gọi Kiểm Chất Lượng Liên Bộ",
        "",
        "| Bộ gọi (`bo_goi`) | Hạng mục đầu ra kiểm định | Loại chuẩn | Số chữ | Điểm chất lượng (/100) | Kết quả | Thời gian (`ms`) | Token kiểm định | Token API trả phí |",
        "|---|---|---|---:|---:|---|---:|---:|---:|",
    ]
    for r in rows:
        kq_str = "ĐẠT" if r["dat"] else f"CẦN SỬA ({r['so_loi']} mục)"
        md_lines.append(
            f"| `{r['bo_goi']}` | {r['ten_hang_muc']} | `{r['loai']}` | {r['so_chu']:,} | **{r['diem']}** | **{kq_str}** | `{r['thoi_gian_ms']} ms` | `{r['tokens_kiem_dinh']:,}` | `0` |"
        )

    out_md = ROOT_DIR / "BAO_CAO" / "CONG_KIEM_CHUNG_CAC_BO.md"
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(f"[CONG KIEM CHUNG] Đã kiểm định {len(rows)} bộ -> {out_md}")


if __name__ == "__main__":
    main()
