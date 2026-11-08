"""Gom records.jsonl thành thẻ nghệ sĩ (artist cards): JSON + ghi chú Markdown cho vault.

Khoá nghệ sĩ: handle Instagram > ArtStation > Behance > X > web đầu tiên > tên credit.
Phần phong cách (style_tags, mo_ta_phong_cach) để trống cho Claude điền ở bước sau.

Dùng:
  python gom_nghe_si.py --records data/records.jsonl --cards data/artists.json --notes vault/artists
"""
import argparse
import json
import re
from pathlib import Path

PRIORITY = ["instagram", "artstation", "behance", "x", "deviantart", "tiktok", "webtoon",
            "tapas", "patreon", "tumblr", "pixiv", "web"]


def slugify(s):
    s = re.sub(r"[^\w\-]+", "-", s.lower()).strip("-")
    return s[:60] or "khong-ten"


def keys_for(rec):
    """Một bài Bored Panda thường về 1 nghệ sĩ; trả (khoá, tên hiển thị, dict link)."""
    links = rec.get("links") or {}
    if rec.get("artist"):
        url = rec.get("artist_url") or rec.get("url")
        return f"{rec['source']}:{rec['artist'].lower()}", rec["artist"], {rec["source"]: [url]}
    for lab in PRIORITY:
        if links.get(lab):
            first = links[lab][0]
            handle = first.rstrip("/").split("/")[-1]
            name = (rec.get("credits") or [handle])[0]
            return f"{lab}:{handle.lower()}", name, links
    if rec.get("credits"):
        c = rec["credits"][0]
        return f"credit:{c.lower()}", c, links
    return None, None, links


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", required=True)
    ap.add_argument("--cards", required=True)
    ap.add_argument("--notes", help="thư mục ghi chú Markdown (Obsidian)")
    a = ap.parse_args()

    cards_path = Path(a.cards)
    cards = {c["id"]: c for c in json.loads(cards_path.read_text(encoding="utf-8"))} if cards_path.exists() else {}
    skipped = {"noai": 0, "no_artist": 0, "tong_hop": 0}
    for line in Path(a.records).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("noai"):
            skipped["noai"] += 1
            continue
        if rec.get("tong_hop"):
            skipped["tong_hop"] += 1
            continue
        key, name, links = keys_for(rec)
        if not key:
            skipped["no_artist"] += 1
            continue
        c = cards.setdefault(key, {
            "id": key, "type": "artist", "name": name, "links": {}, "found_in": [],
            "thumbs": [], "credits": [], "country": "", "medium": "",
            "style_tags": {}, "mo_ta_phong_cach": "", "chu_de": [], "dung_cho": [],
            "noai": False, "ghi_chu": "",
        })
        for lab, urls in links.items():
            for u in urls:
                if u and u not in c["links"].setdefault(lab, []):
                    c["links"][lab].append(u)
        if rec["url"] not in [f["url"] for f in c["found_in"]]:
            c["found_in"].append({"source": rec["source"], "url": rec["url"], "title": rec.get("title", "")})
        if rec.get("thumb_url") and rec["thumb_url"] not in c["thumbs"]:
            c["thumbs"].append(rec["thumb_url"])
        for cr in rec.get("credits") or []:
            if cr not in c["credits"]:
                c["credits"].append(cr)

    cards_path.parent.mkdir(parents=True, exist_ok=True)
    cards_path.write_text(json.dumps(list(cards.values()), ensure_ascii=False, indent=1), encoding="utf-8")

    if a.notes:
        nd = Path(a.notes)
        nd.mkdir(parents=True, exist_ok=True)
        for c in cards.values():
            lines = [
                "---", f"type: artist", f"id: \"{c['id']}\"", f"name: \"{c['name']}\"",
                f"style_tags: {json.dumps(c['style_tags'], ensure_ascii=False)}",
                f"chu_de: {json.dumps(c['chu_de'], ensure_ascii=False)}", "---",
                f"# {c['name']}", "",
                c["mo_ta_phong_cach"] or "_Chưa mô tả phong cách._", "",
                "## Link gốc",
                *[f"- {lab}: {u}" for lab, us in c["links"].items() for u in us], "",
                "## Phát hiện ở",
                *[f"- [{f['title'] or f['url']}]({f['url']})" for f in c["found_in"]], "",
                "## Ảnh tham khảo (link, không lưu)",
                *[f"- {t}" for t in c["thumbs"][:5]],
            ]
            (nd / f"{slugify(c['id'])}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"artists": len(cards), **skipped}, ensure_ascii=False))


if __name__ == "__main__":
    main()
