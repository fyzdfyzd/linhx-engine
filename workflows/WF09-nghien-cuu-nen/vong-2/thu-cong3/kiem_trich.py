#!/usr/bin/env python3
"""Máy đo tầng 1 đề xuất: mỗi `trich` phải là chuỗi con (sau chuẩn hoá) của tệp đã tải."""
import csv, json, re, sys, html
from pathlib import Path
d = Path(sys.argv[1])
def norm(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    return re.sub(r"\s+", " ", s.replace("’", "'").replace("—", "-")).strip().lower()
ng = {r["ma"]: r for r in csv.DictReader(open(d/"03-nguon.csv", encoding="utf-8"))}
txt = {m: norm((d/r["tep_tai"]).read_text(encoding="utf-8", errors="ignore")) for m, r in ng.items()}
bad = ok = 0
for l in (d/"03-bang-chung.jsonl").read_text(encoding="utf-8").splitlines():
    o = json.loads(l)
    hit = norm(o["trich"]) in txt[o["nguon"]]
    ok += hit; bad += not hit
    print(("KHỚP " if hit else "SAI  ") + o["id"] + " " + o["trich"][:60])
print(f"{ok}/{ok+bad} khớp nguyên văn · đạt={bad==0}")
sys.exit(1 if bad else 0)
