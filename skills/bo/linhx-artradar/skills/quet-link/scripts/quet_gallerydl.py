"""Lấy metadata + link qua gallery-dl (gọi CLI, không tải ảnh), bỏ mục gắn NoAI.

Dùng:
  python quet_gallerydl.py --out data/records.jsonl --limit 20 URL [URL ...]
Cần: pip install gallery-dl
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

UA = "LINHX-LAB-artradar/0.1 (research; metadata and links only)"
KEEP = ("title", "description", "tags", "date", "user", "username", "author", "artist",
        "category", "subcategory", "permalink", "url", "id", "medium", "software", "mediums",
        "likes_count", "views_count", "subreddit", "score")


def flat_user(kw):
    for k in ("user", "author", "artist", "owners"):
        v = kw.get(k)
        if isinstance(v, dict):
            return v.get("username") or v.get("name") or v.get("full_name"), v.get("permalink") or v.get("url")
        if isinstance(v, list) and v and isinstance(v[0], dict):
            return v[0].get("username") or v[0].get("display_name"), v[0].get("url")
        if isinstance(v, str):
            return v, None
    return kw.get("username"), None


def is_noai(kw):
    blob = json.dumps({k: kw.get(k) for k in ("tags", "title", "description", "categories", "ai")},
                      ensure_ascii=False, default=str).lower()
    return "noai" in blob or "no ai" in blob or "no_ai" in blob or kw.get("noai") is True


def slim(kw):
    out = {}
    for k in KEEP:
        v = kw.get(k)
        if v in (None, "", [], {}):
            continue
        if isinstance(v, (dict, list)):
            v = json.loads(json.dumps(v, default=str))
        if isinstance(v, str) and len(v) > 400:
            v = v[:400]
        out[k] = v
    return out


def run(url, limit, delay):
    cmd = ["gallery-dl", "-j", "--post-range", f"1-{limit}", "-a", UA,
           "--sleep-request", str(delay), url]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if p.returncode not in (0, 4, 8) and not p.stdout.strip():
        raise RuntimeError(p.stderr.strip()[-500:])
    return json.loads(p.stdout or "[]")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=20, help="số post tối đa mỗi URL")
    ap.add_argument("--delay", type=float, default=4.0, help="giây giữa 2 request (sổ nguồn: delay_s)")
    ap.add_argument("urls", nargs="+")
    a = ap.parse_args()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    stats = {"records": 0, "noai_skipped": 0}
    with out.open("a", encoding="utf-8") as f:
        for url in a.urls:
            try:
                msgs = run(url, a.limit, a.delay)
            except Exception as e:  # noqa: BLE001
                print(f"[lỗi] {url}: {e}", file=sys.stderr)
                continue
            seen = set()
            for m in msgs:
                if not isinstance(m, list) or len(m) < 2 or m[0] not in (3, 6):
                    continue  # chỉ lấy Url (3) và Queue (6)
                file_url, kw = (m[1], m[2] if len(m) > 2 else {})
                page = kw.get("permalink") or kw.get("url") or file_url
                if isinstance(page, str) and page in seen:
                    continue
                seen.add(page)
                if is_noai(kw):
                    stats["noai_skipped"] += 1
                    continue
                name, profile = flat_user(kw)
                rec = {
                    "source": kw.get("category") or urlparse(url).netloc,
                    "url": page if isinstance(page, str) and page.startswith("http") else url,
                    "title": kw.get("title", ""),
                    "artist": name,
                    "artist_url": profile,
                    "thumb_url": file_url if m[0] == 3 else "",
                    "noai": False,
                    "meta": slim(kw),
                    "scanned_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                }
                f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
                stats["records"] += 1
    print(json.dumps(stats, ensure_ascii=False))


if __name__ == "__main__":
    main()
