"""Sinh wiki/trang/tinh-nang.md từ mọi features-dot*.json ở gốc repo.

Dùng: python scripts/wiki_tu_features.py          (ghi trang)
      python scripts/wiki_tu_features.py --kiem   (chỉ kiểm trang đã khớp chưa, thoát 1 nếu lệch)
Chạy sau mỗi lần thêm/sửa features hoặc khi một feature đổi passes. Chỉ dùng stdlib.
"""
import json, sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
TRANG = GOC / "wiki" / "trang" / "tinh-nang.md"


def sinh():
    tep = sorted(GOC.glob("features-dot*.json"))
    s = ["---", "tieu_de: Tính năng engine theo đợt", "loai: danh-muc", "trang_thai: dang-chay",
         "cap_nhat: (theo git)", "nguon: [" + ", ".join(p.name for p in tep) + "]",
         "sinh_tu_dong: scripts/wiki_tu_features.py (sửa features rồi chạy lại, đừng sửa tay)", "---",
         "# Tính năng engine theo đợt", "",
         "Mỗi đợt một file `features-dotN.json` ở gốc repo. Có file `.khoa` là đã khoá, ý mới sang đợt sau. Cách viết đề: [[danh-muc-de-bai]], [[he-du-an-tu-chay]].", ""]
    for p in tep:
        d = json.loads(p.read_text(encoding="utf-8"))
        fs = d.get("features", [])
        dat = sum(1 for f in fs if f.get("passes"))
        khoa = "đã khoá" if Path(str(p) + ".khoa").exists() else "chưa khoá"
        s += [f"## {p.name} · {khoa} · đạt {dat}/{len(fs)}", "",
              f"**Đích:** {d.get('dich', '')}", "", f"Trạng thái: {d.get('trang_thai', '')}", "",
              "| Mã | Cần trước | Mô tả | Đạt |", "|---|---|---|---|"]
        for f in fs:
            mo = str(f.get("mo_ta", "")).replace("|", "/").replace("\n", " ")
            s.append(f"| {f.get('id')} | {', '.join(f.get('phu_thuoc') or []) or '-'} | {mo} | {'✓' if f.get('passes') else '-'} |")
        s.append("")
    s += ["Liên quan: [[loi-engine]] [[lo-trinh]] [[hop-nhat]]", ""]
    return "\n".join(s)


if __name__ == "__main__":
    moi = sinh()
    if "--kiem" in sys.argv:
        cu = TRANG.read_text(encoding="utf-8") if TRANG.exists() else ""
        if cu != moi:
            print("LỖI  wiki/trang/tinh-nang.md lệch features-dot*.json: chạy python scripts/wiki_tu_features.py")
            sys.exit(1)
        print("tinh-nang.md khớp features")
    else:
        TRANG.write_text(moi, encoding="utf-8")
        print("đã ghi", TRANG.relative_to(GOC))
