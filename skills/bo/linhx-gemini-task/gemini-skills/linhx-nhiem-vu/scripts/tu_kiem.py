"""Tự kiểm kết quả nhiệm vụ LINHX. Chỉ dùng thư viện chuẩn, không cần mạng.

Dùng: python3 tu_kiem.py <thu-muc> [--cot-van-ban cot1,cot2]
"""
import csv
import sqlite3
import sys
from pathlib import Path

CAU_KET = tuple(".!?…:;)\"'”»*")
TEN_THU_VIEN = {"pytest", "unittest", "json", "csv", "re", "os", "sys", "pandas", "numpy", "requests",
                "sqlite3", "random", "math", "typing", "datetime", "pathlib", "logging", "string", "test"}


def main() -> int:
    goc = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    cot_vb = set()
    if "--cot-van-ban" in sys.argv:
        cot_vb = set(sys.argv[sys.argv.index("--cot-van-ban") + 1].split(","))
    files = [p for p in goc.rglob("*") if p.is_file() and p.suffix != ".zip"]
    print(f"python {sys.version.split()[0]}; {len(files)} file trong {goc}")
    loi = 0
    for p in sorted(files):
        if p.suffix.lower() == ".csv":
            with open(p, encoding="utf-8-sig", newline="") as f:
                r = csv.DictReader(f)
                rows = list(r)
            cut = sum(1 for row in rows for k, v in row.items()
                      if k in cot_vb and v and len(v.strip()) > 40 and not v.strip().endswith(CAU_KET))
            gg = sum(1 for row in rows for v in row.values() if v and "google.com/search" in v)
            trong = sum(1 for row in rows if not any((v or "").strip() for v in row.values()))
            loi += cut + gg
            print(f"CSV {p.relative_to(goc)}: {len(rows)} dòng, cột {r.fieldnames}; "
                  f"cắt cứng {cut}, URL bọc google {gg}, dòng trống {trong}")
        elif p.suffix.lower() in (".db", ".sqlite", ".sqlite3"):
            con = sqlite3.connect(p)
            for (t,) in con.execute("select name from sqlite_master where type='table'"):
                n = con.execute(f'select count(*) from "{t}"').fetchone()[0]
                print(f"DB {p.relative_to(goc)}.{t}: {n} dòng")
            con.close()
        elif p.suffix == ".py" and p.stem in TEN_THU_VIEN:
            loi += 1
            print(f"LỖI file trùng tên thư viện: {p.relative_to(goc)}")
    for can in ("TIEN-DO.md", "TONG-KET.md"):
        if not (goc / can).exists():
            print(f"THIẾU {can}")
            loi += 1
    print(f"KẾT LUẬN: {loi} lỗi" if loi else "KẾT LUẬN: đạt")
    return 1 if loi else 0


if __name__ == "__main__":
    sys.exit(main())
