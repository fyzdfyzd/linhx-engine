"""Rà wiki: link [[...]] gãy, trang không có trong INDEX, trang thiếu khung, trang cũ, bí mật lộ.

Dùng: python scripts/ra_wiki.py [--ngay-cu 14]   (thoát 1 nếu có lỗi chặn)
"""
import re, sys, datetime
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent / "wiki"
TRUONG = ("tieu_de", "loai", "trang_thai", "cap_nhat")
BI_MAT = re.compile(r"(api[_-]?key|secret|token|mat_?khau|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{12,}", re.I)


def main():
    ngay_cu = int(sys.argv[sys.argv.index("--ngay-cu") + 1]) if "--ngay-cu" in sys.argv else 14
    trang = {p.stem: p for p in (GOC / "trang").glob("*.md")}
    index = (GOC / "INDEX.md").read_text(encoding="utf-8")
    loi, nhac = [], []
    duoc_tro = set()
    for ten, p in trang.items():
        s = p.read_text(encoding="utf-8")
        for l in re.findall(r"\[\[([^\]|#]+)", s):
            l = l.strip()
            duoc_tro.add(l)
            if l not in trang:
                loi.append(f"{p.relative_to(GOC)}: link gãy [[{l}]]")
        if f"trang/{ten}.md" not in index:
            loi.append(f"{p.relative_to(GOC)}: chưa có trong INDEX.md")
        dau = s.split("---")[1] if s.startswith("---") else ""
        for t in TRUONG:
            if f"{t}:" not in dau:
                loi.append(f"{p.relative_to(GOC)}: thiếu trường {t}")
        m = re.search(r"cap_nhat:\s*(\d{4}-\d{2}-\d{2})", dau)
        if m and (datetime.date.today() - datetime.date.fromisoformat(m.group(1))).days > ngay_cu:
            nhac.append(f"{p.relative_to(GOC)}: cập nhật {m.group(1)}, cũ hơn {ngay_cu} ngày")
    for p in GOC.rglob("*"):
        if p.is_file() and p.suffix in (".md", ".json") and BI_MAT.search(p.read_text(encoding="utf-8", errors="ignore")):
            loi.append(f"{p.relative_to(GOC)}: nghi có bí mật")
    for ten in trang:
        if ten not in duoc_tro and ten != "tong-quan":
            nhac.append(f"trang/{ten}.md: mồ côi (không trang nào trỏ tới)")
    for x in loi:
        print("LỖI ", x)
    for x in nhac:
        print("NHẮC", x)
    print(f"{len(trang)} trang, {len(loi)} lỗi, {len(nhac)} nhắc")
    sys.exit(1 if loi else 0)


if __name__ == "__main__":
    main()
