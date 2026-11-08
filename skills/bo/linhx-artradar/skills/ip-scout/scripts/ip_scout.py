"""Thẻ IP (M6): lấy metadata từ Wikidata SPARQL / Bangumi / AniList / Fandom API, chấm 6 tiêu chí, xếp hạng.

  python ip_scout.py lay --seeds seeds-tuan-3.json --out data/ips.json
  python ip_scout.py xep --ips data/ips.json --md output/ip-xep-hang.md

`lay` chỉ ghi metadata + link + số đếm; giữ nguyên phần Claude đã chấm (diem, bai_hoc, ghi_chu).
Fandom: chỉ đọc số thống kê của wiki (siteinfo), không chép chữ bài viết.
Chỉ dùng thư viện chuẩn Python 3.9+.
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

UA = "LINHX-LAB-artradar/0.1 (research; metadata and links only)"
SPARQL = "https://query.wikidata.org/sparql"
WD_API = "https://www.wikidata.org/w/api.php"
BGM = "https://api.bgm.tv"
ANILIST = "https://graphql.anilist.co"
TIEU_CHI = ["do_sau_the_gioi", "nhan_vat_co_ca_tinh", "kha_nang_mo_rong", "cong_dong_fan",
            "khac_biet_hinh_anh", "ban_quyen_kha_nang_hoc"]
TIEU_CHI_TEN = ["Độ sâu thế giới", "Nhân vật có cá tính", "Mở rộng", "Cộng đồng fan", "Khác biệt hình ảnh",
                "Bản quyền/khả năng học"]
WD_PROPS = {"P31": "loai_hinh", "P50": "tac_gia", "P170": "tac_gia", "P178": "chu_so_huu", "P123": "chu_so_huu",
            "P127": "chu_so_huu", "P272": "chu_so_huu", "P577": "nam", "P571": "nam", "P495": "quoc_gia"}
CLAUDE_FIELDS = ("diem", "bai_hoc", "ghi_chu", "so_nhan_vat_co_ca_tinh", "nam_goc")


def http_json(url, delay, data=None, headers=None):
    body = json.dumps(data).encode() if data is not None else None
    h = {"User-Agent": UA, "Accept": "application/json"}
    if data is not None:
        h["Content-Type"] = "application/json"
    h.update(headers or {})
    req = urllib.request.Request(url, data=body, headers=h)
    for attempt in range(3):
        time.sleep(delay * (attempt + 1))
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            # WDQS 429 kèm thông điệp giới hạn cứng: không chờ, để wd_meta chuyển sang Action API
            if e.code == 429 and attempt < 2 and "query.wikidata.org" not in url:
                time.sleep(60)
                continue
            raise
    return None


# ---------- Wikidata ----------

def wd_search(text, lang, delay):
    q = urllib.parse.urlencode({"action": "wbsearchentities", "search": text, "language": lang,
                                "uselang": lang, "limit": 1, "format": "json"})
    hits = (http_json(f"{WD_API}?{q}", delay) or {}).get("search") or []
    if not hits:
        raise ValueError(f"wikidata không tìm thấy '{text}' ({lang}); ghi QID vào seed")
    return hits[0]["id"]


def wd_meta(qid, delay):
    """SPARQL trước; WDQS trả 429 (đợt 10/2026 giới hạn 1 truy vấn/phút) thì dùng Action API wbgetentities."""
    try:
        return wd_meta_sparql(qid, delay)
    except urllib.error.HTTPError as e:
        if e.code not in (429, 403, 503):
            raise
        print(f"[wikidata] SPARQL {e.code}, chuyển sang wbgetentities: {qid}", file=sys.stderr)
        return wd_meta_api(qid, delay)


def wd_entities(ids, delay, props):
    q = urllib.parse.urlencode({"action": "wbgetentities", "ids": "|".join(ids), "props": props,
                                "languages": "vi|en|zh|ja", "format": "json"})
    return (http_json(f"{WD_API}?{q}", delay) or {}).get("entities") or {}


def wd_label(ent):
    for lang in ("vi", "en", "zh", "ja"):
        v = ((ent.get("labels") or {}).get(lang) or {}).get("value")
        if v:
            return v
    return ""


def wd_meta_api(qid, delay):
    ent = wd_entities([qid], delay, "labels|descriptions|claims").get(qid) or {}
    out = {"wikidata": f"https://www.wikidata.org/wiki/{qid}", "_nhan": wd_label(ent),
           "_mo_ta_wd": ((ent.get("descriptions") or {}).get("en") or {}).get("value", "")}
    refs = []
    for p, k in WD_PROPS.items():
        for cl in (ent.get("claims") or {}).get(p, []):
            dv = ((cl.get("mainsnak") or {}).get("datavalue") or {}).get("value")
            if isinstance(dv, dict) and dv.get("id"):
                refs.append((k, dv["id"]))
            elif isinstance(dv, dict) and dv.get("time"):
                y = dv["time"].lstrip("+")[:4]
                out.setdefault(k, [])
                if y not in out[k]:
                    out[k].append(y)
    labels = wd_entities(sorted({r for _, r in refs})[:50], delay, "labels") if refs else {}
    for k, r in refs:
        v = wd_label(labels.get(r) or {}) or r
        out.setdefault(k, [])
        if v not in out[k]:
            out[k].append(v)
    if "nam" in out:
        out["nam"] = sorted(out["nam"])[:1]
    return out


def wd_meta_sparql(qid, delay):
    values = " ".join(f'("{p}" wdt:{p})' for p in WD_PROPS)
    query = f"""SELECT ?p ?vLabel ?itemLabel ?itemDescription WHERE {{
      VALUES (?p ?wdt) {{ {values} }}
      OPTIONAL {{ wd:{qid} ?wdt ?v . }}
      BIND(wd:{qid} AS ?item)
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "vi,en,zh,ja". }} }}"""
    res = http_json(f"{SPARQL}?{urllib.parse.urlencode({'query': query, 'format': 'json'})}", delay,
                    headers={"Accept": "application/sparql-results+json"})
    out = {"wikidata": f"https://www.wikidata.org/wiki/{qid}"}
    for b in (res or {}).get("results", {}).get("bindings", []):
        out.setdefault("_nhan", b.get("itemLabel", {}).get("value"))
        out.setdefault("_mo_ta_wd", b.get("itemDescription", {}).get("value", ""))
        v = b.get("vLabel", {}).get("value")
        if not v:
            continue
        k = WD_PROPS[b["p"]["value"]]
        if k == "nam":
            v = v[:4]
        out.setdefault(k, [])
        if v not in out[k]:
            out[k].append(v)
    return out


# ---------- Bangumi / AniList / Fandom ----------

def bgm_meta(sid, delay):
    s = http_json(f"{BGM}/v0/subjects/{sid}", delay) or {}
    chars = http_json(f"{BGM}/v0/subjects/{sid}/characters", delay) or []
    return {"bangumi": f"https://bgm.tv/subject/{sid}", "_bgm_ten": s.get("name_cn") or s.get("name"),
            "_bgm_nam": (s.get("date") or "")[:4], "_bgm_so_nhan_vat": len(chars),
            "_bgm_thu_thap": (s.get("collection") or {}).get("collect", 0)}


# characters.pageInfo.total của AniList không tin được (trả 500 cho cả Chi's Sweet Home) nên không lấy
AL_Q = """query($id:Int){ Media(id:$id){ siteUrl title{romaji} startDate{year} popularity favourites } }"""


def al_meta(mid, delay):
    m = ((http_json(ANILIST, delay, {"query": AL_Q, "variables": {"id": mid}}) or {}).get("data") or {}).get("Media") or {}
    return {"anilist": m.get("siteUrl"), "_al_ten": (m.get("title") or {}).get("romaji"),
            "_al_nam": (m.get("startDate") or {}).get("year"), "_al_popularity": m.get("popularity"),
            "_al_favourites": m.get("favourites")}


def fandom_meta(wiki, delay):
    q = urllib.parse.urlencode({"action": "query", "meta": "siteinfo", "siprop": "statistics", "format": "json"})
    st = ((http_json(f"https://{wiki}.fandom.com/api.php?{q}", delay) or {}).get("query") or {}).get("statistics") or {}
    return {"fandom": f"https://{wiki}.fandom.com/", "_fandom_bai": st.get("articles"),
            "_fandom_nguoi_sua_30n": st.get("activeusers")}


def lay(a):
    seeds = json.loads(Path(a.seeds).read_text(encoding="utf-8"))
    out = Path(a.out)
    old = {c["id"]: c for c in json.loads(out.read_text(encoding="utf-8"))} if out.exists() else {}
    cards, loi = [], []
    for s in seeds["ips"]:
        card = {"id": s["id"], "ten": s["ten"], "ten_goc": s.get("ten_goc", ""), "nhom": s["nhom"],
                "loai_hinh_seed": s.get("loai_hinh", ""), "link": {}, "so_lieu": {}}
        steps = []
        if s.get("wikidata") or s.get("wikidata_search"):
            steps.append(("wikidata", lambda s=s: wd_meta(s.get("wikidata") or wd_search(
                s["wikidata_search"], s.get("lang", "en"), a.delay), a.delay)))
        if s.get("bangumi"):
            steps.append(("bangumi", lambda s=s: bgm_meta(s["bangumi"], a.delay)))
        if s.get("anilist"):
            steps.append(("anilist", lambda s=s: al_meta(s["anilist"], a.delay)))
        if s.get("fandom"):
            steps.append(("fandom", lambda s=s: fandom_meta(s["fandom"], a.delay)))
        for name, fn in steps:
            try:
                for k, v in fn().items():
                    if k in ("wikidata", "bangumi", "anilist", "fandom"):
                        card["link"][k] = v
                    elif k.startswith("_"):
                        card["so_lieu"][k[1:]] = v
                    else:
                        card[k] = v
            except Exception as e:  # noqa: BLE001
                if name == "fandom":
                    # Fandom chặn API với UA tự khai (403); giữ link để người xem tay, không đổi UA để lách
                    card["link"]["fandom"] = f"https://{s['fandom']}.fandom.com/"
                    card["so_lieu"]["fandom_trang_thai"] = f"chưa kiểm ({e})"
                loi.append(f"{s['id']} {name}: {e}")
                print(f"[lỗi {name}] {s['id']}: {e}", file=sys.stderr)
        card["chu_so_huu"] = card.get("chu_so_huu") or s.get("chu_so_huu", [])
        card["nam"] = (card.get("nam") or [str(card["so_lieu"].get("bgm_nam") or card["so_lieu"].get("al_nam") or "")])
        prev = old.get(s["id"], {})
        for k in CLAUDE_FIELDS:
            if k in prev:
                card[k] = prev[k]
        card.setdefault("diem", {k: None for k in TIEU_CHI})
        card.setdefault("bai_hoc", [])
        print(f"[ip] {s['id']}: {card['so_lieu'].get('nhan') or '-'} | {', '.join(card['link'])}", file=sys.stderr)
        cards.append(card)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(cards, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"ips": len(cards), "loi": loi, "at": datetime.now(timezone.utc).isoformat(timespec="seconds")},
                     ensure_ascii=False))


def tong(c):
    d = c.get("diem") or {}
    return sum(d.get(k) or 0 for k in TIEU_CHI)


def xep(a):
    cards = json.loads(Path(a.ips).read_text(encoding="utf-8"))
    thieu = [c["id"] for c in cards if any((c.get("diem") or {}).get(k) is None for k in TIEU_CHI)]
    lines = ["# Xếp hạng IP (6 tiêu chí, mỗi tiêu chí 1-5, tối đa 30)", ""]
    for nhom in dict.fromkeys(c["nhom"] for c in cards):
        cs = sorted([c for c in cards if c["nhom"] == nhom], key=lambda c: (-tong(c), c["ten"]))
        lines += [f"## {nhom}", "", "| # | IP | " + " | ".join(TIEU_CHI_TEN) + " | Tổng |",
                  "|---|---|" + "---|" * (len(TIEU_CHI) + 1)]
        for i, c in enumerate(cs, 1):
            d = c.get("diem") or {}
            lines.append(f"| {i} | {c['ten']} | " + " | ".join(str(d.get(k) or "-") for k in TIEU_CHI) + f" | **{tong(c)}** |")
        lines.append("")
    if thieu:
        lines.append(f"Chưa chấm đủ: {', '.join(thieu)}")
    Path(a.md).parent.mkdir(parents=True, exist_ok=True)
    Path(a.md).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"xep": len(cards), "chua_cham": thieu, "md": a.md}, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("lay"); p.add_argument("--seeds", required=True); p.add_argument("--out", required=True)
    p.add_argument("--delay", type=float, default=2.0)
    p = sp.add_parser("xep"); p.add_argument("--ips", required=True); p.add_argument("--md", required=True)
    a = ap.parse_args()
    {"lay": lay, "xep": xep}[a.cmd](a)


if __name__ == "__main__":
    main()
