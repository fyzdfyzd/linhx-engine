#!/usr/bin/env python3
"""Adapter B1: bảng xếp hạng Apple Podcasts (JSON công khai, không cần đăng nhập).

  python apple_podcast.py vn 100 > b1-podcast-vn.jsonl
  python apple_podcast.py us 100 > b1-podcast-us.jsonl
Rồi: python gapscan.py nhap b1-podcast-vn.jsonl
Thứ hạng được đổi thành điểm tương tác giả định (view = (so_luong - hạng + 1) * 1000) để so trong cùng nguồn.
"""
import json, sys, time, urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

nuoc = (sys.argv[1] if len(sys.argv) > 1 else "vn").lower()
n = int(sys.argv[2]) if len(sys.argv) > 2 else 100
url = f"https://rss.applemarketingtools.com/api/v2/{nuoc}/podcasts/top/{n}/podcasts.json"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (LINHX LAB029 nghiên cứu cá nhân)"})
d = json.load(urllib.request.urlopen(req, timeout=30))
ngay = time.strftime("%Y-%m-%d")
for i, r in enumerate(d["feed"]["results"], 1):
    print(json.dumps({
        "id": f"podcast-{nuoc}:{r['id']}", "nguon": "podcast", "thi_truong": "vn" if nuoc == "vn" else "quoc-te",
        "loai": "kenh", "tieu_de": r["name"], "kenh": r["name"], "tac_gia": r.get("artistName", ""),
        "url": r.get("url", ""), "the": [g["name"] for g in r.get("genres", [])], "mo_ta": ", ".join(g["name"] for g in r.get("genres", [])),
        "hang": f"apple-{nuoc}#{i}", "so_do": {"view": (n - i + 1) * 1000}, "ngay_quet": ngay}, ensure_ascii=False))
