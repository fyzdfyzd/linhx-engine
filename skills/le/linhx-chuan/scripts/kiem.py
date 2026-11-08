#!/usr/bin/env python3
"""kiem.py · máy kiểm rẻ của linhx-chuan (LAB106).

Dùng:
  python kiem.py <thu-muc-viec> --pha dau|cuoi [--loai chien-luoc]
In DAT hoặc CHUA_DAT và danh sách lỗi. Mã thoát 0 khi DAT.
Chỉ kiểm cấu trúc và truy nguồn; chất lượng do người chấm theo cham.md.
"""
import argparse, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SO_DAU = ["STATUS.md", "HANH-TRINH-NGUOI-XEM.md", "THAM-CHIEU.md", "DATA_GAPS.md"]
CAU_HANH_TRINH = ["Ai xem", "Xem ở đâu", "Thứ tự xem", "Xem xong làm gì"]
TRICH = re.compile(r"[\"“]([^\"”\n]{30,})[\"”]")
BC = re.compile(r"\[(BC-\d+)\]")
LINK = re.compile(r"https?://\S+")


def doc(p):
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return ""


def chuan_hoa(s):
    # Bỏ dấu nhấn markdown (** __ ` >) để câu trích in đậm trong nguồn vẫn khớp nguyên văn.
    s = re.sub(r"\*\*|__|`|^\s*>\s?", "", s, flags=re.M)
    return re.sub(r"\s+", " ", s).strip().lower()


def kiem_dau(goc, loi):
    for f in SO_DAU:
        if not (goc / f).is_file():
            loi.append(f"thiếu sổ {f}")
    ht = doc(goc / "HANH-TRINH-NGUOI-XEM.md")
    for c in CAU_HANH_TRINH:
        m = re.search(r"\*\*" + re.escape(c) + r":\*\*[ \t]*(.*)", ht)
        gia_tri = re.sub(r"\(.*?\)", "", m.group(1)).strip() if m else ""
        if not gia_tri:
            loi.append(f"hành trình người xem chưa điền '{c}'")
    tc = doc(goc / "THAM-CHIEU.md")
    dong = [d for d in tc.splitlines() if LINK.search(d)]
    if len(dong) < 5:
        loi.append(f"THAM-CHIEU.md có {len(dong)} link, cần ≥5")
    thieu_hoc = [d for d in dong if not re.search(r"học:\s*\S{2,}", d)]
    if thieu_hoc:
        loi.append(f"{len(thieu_hoc)} tham chiếu chưa ghi 'học:'")


def file_bai(goc):
    """Các file nội dung (không tính sổ và bằng chứng)."""
    bo_qua = set(SO_DAU) | {"DUYET-E2E.md", "BAI-HOC.md", "ANCHOR.md"}
    for p in sorted(goc.rglob("*.md")):
        rel = p.relative_to(goc)
        if rel.parts[0] in ("bang-chung", "dau-vao", ".vong") or p.name in bo_qua:
            continue
        yield p


def kiem_cuoi(goc, loi):
    kiem_dau(goc, loi)
    e2e = doc(goc / "DUYET-E2E.md")
    if not e2e:
        loi.append("thiếu DUYET-E2E.md (luật 1: chưa duyệt như khán giả)")
    else:
        anh = re.findall(r"([\w./\\-]+\.(?:png|jpg|jpeg|webp))", e2e, re.I)
        if not anh:
            loi.append("DUYET-E2E.md không có ảnh chặng nào")
        for a in anh:
            if not (goc / a).is_file():
                loi.append(f"ảnh E2E không tồn tại: {a}")
        if re.search(r"\|\s*CHUA_DAT\s*\|", e2e):
            loi.append("DUYET-E2E.md còn chặng CHUA_DAT")
    bh = [d for d in doc(goc / "BAI-HOC.md").splitlines() if d.strip().startswith(("-", "*", "1", "2", "3", "4", "5"))]
    if len(bh) < 3:
        loi.append(f"BAI-HOC.md có {len(bh)} dòng, cần ≥3")

    bcdir = goc / "bang-chung"
    idx = doc(bcdir / "INDEX.md")
    co_bc = set(BC.findall(idx))
    # Trích nguyên văn được đối chiếu với bang-chung/ và dau-vao/ (tài liệu người ra lệnh giao).
    nguon = [p for d in (bcdir, goc / "dau-vao") if d.is_dir() for p in d.rglob("*") if p.is_file() and p.name != "INDEX.md"]
    kho = chuan_hoa(" ".join(doc(p) for p in nguon))
    status = doc(goc / "STATUS.md")
    for p in file_bai(goc):
        t = doc(p)
        rel = p.relative_to(goc).as_posix()
        for b in sorted(set(BC.findall(t)) - co_bc):
            loi.append(f"{rel}: {b} không có trong bang-chung/INDEX.md")
        for q in TRICH.findall(t):
            if chuan_hoa(q) not in kho:
                loi.append(f"{rel}: trích không thấy nguyên văn trong bang-chung/ hay dau-vao/: \"{q[:50]}…\"")
        if p.name not in status:
            loi.append(f"STATUS.md chưa nhắc {rel} (luật 4: làm tới đâu lưu tới đó)")


def kiem_loai(goc, loai, loi):
    cau_hinh = json.loads((HERE / "loai.json").read_text(encoding="utf-8"))
    if loai not in cau_hinh:
        loi.append(f"không biết loại '{loai}', có: {', '.join(cau_hinh)}")
        return
    for mau, muc in cau_hinh[loai]["file"].items():
        khop = sorted(goc.glob(mau))
        if not khop:
            loi.append(f"[{loai}] thiếu file {mau}")
            continue
        t = doc(khop[-1])
        for m in muc:
            if m.lower() not in t.lower():
                loi.append(f"[{loai}] {khop[-1].name} thiếu mục '{m}'")
    toi_thieu = cau_hinh[loai].get("so_nc_toi_thieu", 0)
    nc = list(goc.glob("NC*.md"))
    if len(nc) < toi_thieu:
        loi.append(f"[{loai}] có {len(nc)} file NC, cần ≥{toi_thieu}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("thu_muc")
    ap.add_argument("--pha", choices=["dau", "cuoi"], default="dau")
    ap.add_argument("--loai")
    a = ap.parse_args(argv)
    goc = Path(a.thu_muc)
    loi = []
    if not goc.is_dir():
        loi.append(f"không có thư mục {goc}")
    else:
        (kiem_cuoi if a.pha == "cuoi" else kiem_dau)(goc, loi)
        if a.loai and a.pha == "cuoi":
            kiem_loai(goc, a.loai, loi)
    print("DAT" if not loi else "CHUA_DAT")
    for l in loi:
        print(" -", l)
    return 0 if not loi else 1


if __name__ == "__main__":
    sys.exit(main())
