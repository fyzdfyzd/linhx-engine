"""Nhập nhân vật từ Bangumi (manhua/donghua, tiên hiệp) và AniList (anime/manga) thành thẻ nhân vật.

Chỉ lưu metadata, link, link ảnh (không tải), tóm tắt nguồn cắt ngắn ≤300 ký tự để Claude viết lại.

Dùng:
  python nhap_nhan_vat.py --seeds seeds.json --out data/characters.json
Chỉ dùng thư viện chuẩn Python 3.9+.
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

UA = "LINHX-LAB-artradar/0.1 (research; metadata and links only)"
BGM = "https://api.bgm.tv"
ANILIST = "https://graphql.anilist.co"
BGM_TYPE = {1: "sách/truyện", 2: "anime", 4: "game", 6: "phim"}
BGM_ROLE_ORDER = {"主角": 0, "配角": 1, "客串": 2}
VISUAL_FIELDS = {"hinh_khoi": "", "bang_mau": "", "dac_diem_nhan_dien": "", "trang_phuc": "",
                 "ty_le": "", "vai_tro": "", "archetype": "", "mo_ta": "", "style_tags": {},
                 "dung_cho": [], "ghi_chu": ""}


def http_json(url, delay, data=None):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers={
        "User-Agent": UA, "Accept": "application/json", "Content-Type": "application/json"})
    for attempt in range(3):
        time.sleep(delay * (attempt + 1))
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                time.sleep(60)
                continue
            raise
    return None


def short(text, n=300):
    text = " ".join((text or "").split())
    return text if len(text) <= n else text[: n - 1] + "…"


# ---------- Bangumi ----------

def bgm_find_subject(keyword, delay):
    res = http_json(f"{BGM}/v0/search/subjects?limit=5", delay,
                    {"keyword": keyword, "filter": {"type": [1, 2], "nsfw": False}})
    items = (res or {}).get("data") or []
    for it in items:
        if keyword in (it.get("name_cn"), it.get("name")):
            return it
    return items[0] if items else None


def bgm_card(ch, subject, relation, chu_de):
    info = {}
    for kv in ch.get("infobox") or []:
        v = kv.get("value")
        if isinstance(v, list):
            v = ", ".join(x.get("v", "") for x in v if isinstance(x, dict))
        info[kv.get("key")] = v
    return {
        "id": f"bangumi:{ch['id']}", "type": "character",
        "name": info.get("简体中文名") or ch.get("name"), "name_native": ch.get("name"),
        "source": "bangumi", "source_url": f"https://bgm.tv/character/{ch['id']}",
        "works": [{"title": subject.get("name_cn") or subject.get("name"), "title_native": subject.get("name"),
                   "url": f"https://bgm.tv/subject/{subject['id']}", "role": relation,
                   "media": BGM_TYPE.get(subject.get("type"), "")}],
        "gender": ch.get("gender") or info.get("性别") or "",
        "image_url": (ch.get("images") or {}).get("medium", ""),
        "popularity": (ch.get("stat") or {}).get("collects", 0),
        "tom_tat_nguon": short(ch.get("summary")),
        "infobox": {k: short(str(v), 80) for k, v in info.items() if k in ("性别", "身高", "生日", "别名", "门派", "境界", "种族")},
        "chu_de": list(chu_de), **json.loads(json.dumps(VISUAL_FIELDS)),
    }


def from_bangumi(seed, delay):
    # subject_id trong seed: bỏ bước tìm (tìm theo tên hay khớp nhầm bản tiểu thuyết/phim ngắn ít nhân vật)
    subj = (http_json(f"{BGM}/v0/subjects/{seed['subject_id']}", delay) if seed.get("subject_id")
            else bgm_find_subject(seed["keyword"], delay))
    if not subj:
        print(f"[bangumi] không tìm thấy: {seed['keyword']}", file=sys.stderr)
        return []
    chars = http_json(f"{BGM}/v0/subjects/{subj['id']}/characters", delay) or []
    chars.sort(key=lambda c: BGM_ROLE_ORDER.get(c.get("relation"), 9))
    cards = []
    for c in chars[: seed.get("top", 6)]:
        full = http_json(f"{BGM}/v0/characters/{c['id']}", delay)
        if full:
            cards.append(bgm_card(full, subj, c.get("relation", ""), seed.get("chu_de", [])))
    print(f"[bangumi] {seed['keyword']} -> {subj.get('name_cn') or subj.get('name')} ({len(cards)} nhân vật)", file=sys.stderr)
    return cards


# ---------- AniList ----------

AL_QUERY = """query($search:String,$id:Int,$n:Int){ Media(search:$search, id:$id, sort:SEARCH_MATCH){
  id siteUrl type title{romaji english native}
  characters(sort:[ROLE,FAVOURITES_DESC], perPage:$n){ edges{ role node{
    id siteUrl name{full native} gender age description(asHtml:false) favourites image{medium} } } } } }"""


def al_card(edge, media, chu_de):
    n = edge["node"]
    t = media.get("title") or {}
    return {
        "id": f"anilist:{n['id']}", "type": "character",
        "name": (n.get("name") or {}).get("full"), "name_native": (n.get("name") or {}).get("native"),
        "source": "anilist", "source_url": n.get("siteUrl"),
        "works": [{"title": t.get("english") or t.get("romaji"), "title_native": t.get("native"),
                   "url": media.get("siteUrl"), "role": edge.get("role"), "media": (media.get("type") or "").lower()}],
        "gender": n.get("gender") or "", "image_url": (n.get("image") or {}).get("medium", ""),
        "popularity": n.get("favourites") or 0,
        "tom_tat_nguon": short((n.get("description") or "").replace("~!", "").replace("!~", "")),
        "infobox": {"age": n.get("age")} if n.get("age") else {},
        "chu_de": list(chu_de), **json.loads(json.dumps(VISUAL_FIELDS)),
    }


def from_anilist(seed, delay):
    # id trong seed: chọn đúng bản (tìm "Natsume Yuujinchou" khớp nhầm ONA hợp tác Kumamoto)
    var = {"id": seed["id"]} if seed.get("id") else {"search": seed["search"]}
    res = http_json(ANILIST, delay, {"query": AL_QUERY, "variables": {**var, "n": seed.get("top", 6)}})
    media = ((res or {}).get("data") or {}).get("Media")
    if not media:
        print(f"[anilist] không tìm thấy: {seed.get('search') or seed.get('id')}", file=sys.stderr)
        return []
    cards = [al_card(e, media, seed.get("chu_de", [])) for e in media["characters"]["edges"]]
    print(f"[anilist] {seed.get('search') or seed.get('id')} -> {media['title'].get('romaji')} ({len(cards)} nhân vật)", file=sys.stderr)
    return cards


def merge(cards, new):
    for c in new:
        old = cards.get(c["id"])
        if not old:
            cards[c["id"]] = c
            continue
        for k in ("name", "name_native", "source_url", "gender", "image_url", "popularity", "tom_tat_nguon", "infobox"):
            old[k] = c[k]
        for w in c["works"]:
            if w["url"] not in [x["url"] for x in old["works"]]:
                old["works"].append(w)
        old["chu_de"] = list(dict.fromkeys(old["chu_de"] + c["chu_de"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--delay", type=float, default=2.0)
    a = ap.parse_args()
    seeds = json.loads(Path(a.seeds).read_text(encoding="utf-8"))
    out = Path(a.out)
    cards = {c["id"]: c for c in json.loads(out.read_text(encoding="utf-8"))} if out.exists() else {}
    before = len(cards)
    errors = 0
    for s in seeds.get("bangumi", []):
        try:
            merge(cards, from_bangumi(s, a.delay))
        except Exception as e:  # noqa: BLE001
            errors += 1
            print(f"[lỗi bangumi] {s}: {e}", file=sys.stderr)
    for s in seeds.get("anilist", []):
        try:
            merge(cards, from_anilist(s, a.delay))
        except Exception as e:  # noqa: BLE001
            errors += 1
            print(f"[lỗi anilist] {s}: {e}", file=sys.stderr)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(list(cards.values()), ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"characters": len(cards), "new": len(cards) - before, "errors": errors,
                      "at": datetime.now(timezone.utc).isoformat(timespec="seconds")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
