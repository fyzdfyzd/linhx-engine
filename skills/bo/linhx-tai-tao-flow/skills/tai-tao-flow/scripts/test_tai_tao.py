#!/usr/bin/env python3
"""Kiểm tai_tao.py trên ví dụ Kudo. Chạy: python test_tai_tao.py [thu_muc_vi_du]"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import tai_tao

vd = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[5] / "vi-du" / "kudo"
loi = []

dan = (vd / "bai-dan.txt").read_text(encoding="utf-8")
sach = tai_tao.sach(dan)
if dan.count("Ngày này đã đến") != 4 or sach.count("Ngày này đã đến") != 1:
    loi.append("sach: không bỏ được 3 bản lặp")

flow = json.loads((vd / "flow.json").read_text(encoding="utf-8"))
for c in flow["claims"]:
    if c["loai"] == "chuc-nang" and not c["prior_art"] and c["kha_thi"] > 1:
        loi.append(f"{c['id']}: chấm khả thi {c['kha_thi']} mà không có prior art")
    if not c["ly_do"]:
        loi.append(f"{c['id']}: thiếu lý do")

kha_thi, kd, kq = tai_tao.ket_luan(flow)
if kq != "THỬ NHỎ":
    loi.append(f"kết luận Kudo là {kq}, mong đợi THỬ NHỎ (khả thi {kha_thi}, kinh doanh {kd})")
if "C3" not in tai_tao.cham(flow):
    loi.append("cham: bảng thiếu claim")

with tempfile.TemporaryDirectory() as t:
    p = tai_tao.pack(flow, Path(t) / "pack")
    json.loads((p / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    for m in flow["pack"]["modules"]:
        if not (p / "skills" / m["ten"] / "SKILL.md").exists():
            loi.append(f"pack: thiếu {m['ten']}")

print("\n".join(loi) if loi else f"ĐẠT: {kq}, khả thi {kha_thi}/3, kinh doanh {kd}/18")
sys.exit(1 if loi else 0)
