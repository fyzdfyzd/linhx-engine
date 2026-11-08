#!/usr/bin/env python3
"""kiem_thiet_ke.py · kiểm máy cho workflow thiet-ke (stdlib).

  python kiem_thiet_ke.py <thu-muc-viec> --nhanh an-pham|landing --pha d1|d2|d4
Trả 0 khi DAT, 1 khi CHUA_DAT (in từng lỗi).
"""
import argparse, json, re, sys
from pathlib import Path

ANH = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".pdf"}
SO = ["BRIEF.md", "ANCHOR.md", "STATUS.md", "HANH-TRINH-NGUOI-XEM.md", "THAM-CHIEU.md", "DATA_GAPS.md"]


def doc(p):
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def anh_trong(d):
    return [f for f in d.rglob("*") if f.suffix.lower() in ANH] if d.is_dir() else []


def d1(g, loi):
    for s in SO:
        if not (g / s).is_file():
            loi.append(f"thiếu {s}")
    tc = g / "tham-chieu"
    nguon = []
    try:
        nguon = json.loads(doc(tc / "nguon.json") or "[]")
    except json.JSONDecodeError:
        loi.append("tham-chieu/nguon.json hỏng")
    if len(nguon) < 8:
        loi.append(f"tham chiếu {len(nguon)} < 8 trong tham-chieu/nguon.json")
    for i, n in enumerate(nguon):
        if not (tc / str(n.get("file", ""))).is_file():
            loi.append(f"tham chiếu #{i+1}: không có file ảnh {n.get('file')}")
        if not n.get("tac_gia") or not n.get("link"):
            loi.append(f"tham chiếu #{i+1}: thiếu tac_gia hoặc link")
        if not str(n.get("hoc", "")).strip():
            loi.append(f"tham chiếu #{i+1}: thiếu 'hoc'")
        if re.search(r"midjourney|dall-?e|ai[- ]generated|lexica|stable diffusion", json.dumps(n, ensure_ascii=False), re.I):
            loi.append(f"tham chiếu #{i+1}: có vẻ là ảnh AI")
    if (g / "BAN-CU").exists() and not (g / "CHAN-DOAN.md").is_file():
        loi.append("có BAN-CU/ (đang sửa bản cũ) mà thiếu CHAN-DOAN.md")


def d2(g, loi):
    t = doc(g / "PHUONG-AN.md")
    huong = re.findall(r"^##\s+(?:Hướng|PA)\s*([A-Z])", t, re.M)
    if len(set(huong)) < 3:
        loi.append(f"PHUONG-AN.md có {len(set(huong))} hướng (## Hướng A...), cần ≥3")
    for h in set(huong):
        if not anh_trong(g / "pa" / h):
            loi.append(f"hướng {h}: không có ảnh phác trong pa/{h}/")
    if not (g / "MOODBOARD.md").is_file():
        loi.append("thiếu MOODBOARD.md")


def d4(g, nhanh, loi):
    phieu = sorted((g / "cham").glob("*.json")) if (g / "cham").is_dir() else []
    tho = ""
    m = re.search(r"thợ:\s*(\S+)", doc(g / "STATUS.md"))
    if m:
        tho = m.group(1).lower()
    nguoi = set()
    for p in phieu:
        try:
            j = json.loads(doc(p))
        except json.JSONDecodeError:
            loi.append(f"{p.name} hỏng"); continue
        n = str(j.get("nguoi_cham", "")).lower()
        if n and n != tho:
            nguoi.add(n)
    if len(phieu) < 3 or len(nguoi) < 2:
        loi.append(f"cần ≥3 phiếu chấm từ ≥2 người khác thợ, có {len(phieu)} phiếu / {len(nguoi)} người")
    mu = doc(g / "CHAM-MU.md")
    m = re.search(r"đoán AI:\s*(\d+)\s*/\s*(\d+)", mu)
    if not m:
        loi.append("CHAM-MU.md thiếu dòng 'đoán AI: x/y'")
    elif int(m.group(1)) * 3 > int(m.group(2)):
        loi.append(f"mùi AI: {m.group(1)}/{m.group(2)} người đoán AI (> 1/3)")
    ts = doc(g / "THAY-SAU.md")
    if not (g / "THAY-SAU.md").is_file():
        loi.append("thiếu THAY-SAU.md (ghi 'không có' nếu không có chỗ AI vẽ tạm)")
    elif re.search(r"Bộ design gốc:\s*không", doc(g / "BRIEF.md"), re.I):
        dong = [l for l in ts.splitlines() if l.startswith("|") and not re.match(r"^\|\s*(-|Vị trí)", l)]
        if not dong:
            loi.append("không có bộ design gốc mà THAY-SAU.md chưa ghi chỗ AI vẽ nào")
        for l in dong:
            o = [c.strip() for c in l.strip().strip("|").split("|")]
            if len(o) < 4 or not all(o[:4]):
                loi.append(f"THAY-SAU.md dòng thiếu cột: {l[:60]}")
    if not anh_trong(g / "kiem"):
        loi.append("kiem/ chưa có ảnh kiểm khổ thật")
    if nhanh == "landing":
        try:
            do = json.loads(doc(g / "kiem" / "do.json") or "{}")
        except json.JSONDecodeError:
            do = {}
        for kho in ("360", "1280"):
            k = do.get(kho)
            if not k:
                loi.append(f"kiem/do.json thiếu khổ {kho}")
            elif k.get("scrollWidth", 0) > k.get("innerWidth", 0):
                loi.append(f"khổ {kho}: tràn ngang {k['scrollWidth']} > {k['innerWidth']}")
        if do.get("cham_toi_tra_tien", 99) > 3:
            loi.append(f"đường mua {do.get('cham_toi_tra_tien')} chạm > 3")


def main(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument("thu_muc"); a.add_argument("--nhanh", choices=["an-pham", "landing"], required=True)
    a.add_argument("--pha", choices=["d1", "d2", "d4"], required=True)
    a = a.parse_args(argv)
    g, loi = Path(a.thu_muc), []
    d1(g, loi)
    if a.pha in ("d2", "d4"):
        d2(g, loi)
    if a.pha == "d4":
        d4(g, a.nhanh, loi)
    print("DAT" if not loi else "CHUA_DAT")
    for l in loi:
        print(" -", l)
    return 1 if loi else 0


if __name__ == "__main__":
    sys.exit(main())
