#!/usr/bin/env python3
"""Máy đo phiếu "chỉ vá" (lỗi NCT: agy "gộp" làm mất 241 số, sinh 89 số không nguồn).

So hai bản trước/sau của một tệp Markdown: số nào biến mất, số nào mới sinh.
Số mới phải có trong kho bằng chứng (03-bang-chung.jsonl, trường "so" hoặc "trich");
số mất phải nằm trong danh sách được phép đổi (--cho-doi "12,5;2019").

Dùng: python kiem_mat_so.py truoc.md sau.md [--bang-chung 03-bang-chung.jsonl] [--cho-doi "a;b"]
Thoát 0 = DAT, 1 = CHUA_DAT.
"""
import argparse, json, re, sys
from collections import Counter
from pathlib import Path

SO = re.compile(r"(?<![\w.,])\d{1,3}(?:[.,]\d{3})+(?:,\d+)?(?![\w])|(?<![\w.,])\d+(?:[.,]\d+)?(?![\w])")


def chuan_so(s):
    s = s.strip()
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+(?:,\d+)?", s):   # 1.234.567,8 kiểu Việt
        s = s.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?", s):  # 1,234,567.8 kiểu Anh
        s = s.replace(",", "")
    else:
        s = s.replace(",", ".")
    try:
        f = float(s)
    except ValueError:
        return None
    return str(int(f)) if f.is_integer() else str(f)


def dem(txt):
    c = Counter()
    for m in SO.findall(txt):
        k = chuan_so(m)
        if k is not None and k not in {"0", "1", "2", "3"}:  # bỏ số thứ tự quá ngắn
            c[k] += 1
    return c


def kho(path):
    s = set()
    if path and Path(path).exists():
        for l in open(path, encoding="utf-8"):
            if not l.strip():
                continue
            o = json.loads(l)
            for x in o.get("so") or []:
                k = chuan_so(str(x))
                if k:
                    s.add(k)
            s |= set(dem(o.get("trich", "")))
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("truoc"); ap.add_argument("sau")
    ap.add_argument("--bang-chung"); ap.add_argument("--cho-doi", default="")
    a = ap.parse_args()
    t, s = dem(Path(a.truoc).read_text(encoding="utf-8")), dem(Path(a.sau).read_text(encoding="utf-8"))
    cho = {chuan_so(x) for x in a.cho_doi.split(";") if x.strip()}
    mat = sorted(k for k in t if k not in s and k not in cho)
    moi = sorted(k for k in s if k not in t)
    k = kho(a.bang_chung)
    moi_khong_nguon = [x for x in moi if x not in k] if a.bang_chung else moi
    print(f"số trước: {len(t)} | số sau: {len(s)} | mất ngoài danh sách: {len(mat)} | mới không có trong kho: {len(moi_khong_nguon)}")
    if mat:
        print("mất:", ", ".join(mat[:20]))
    if moi_khong_nguon:
        print("mới không nguồn:", ", ".join(moi_khong_nguon[:20]))
    dat = not mat and not moi_khong_nguon
    print("DAT" if dat else "CHUA_DAT")
    return 0 if dat else 1


if __name__ == "__main__":
    sys.exit(main())
