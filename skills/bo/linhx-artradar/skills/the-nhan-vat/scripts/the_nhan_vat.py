"""Làm việc với data/characters.json: xuất ghi chú, xuất Character Card V2, lọc.

  python the_nhan_vat.py notes --cards data/characters.json --dir output/characters
  python the_nhan_vat.py v2    --cards data/characters.json --dir output/cards-v2 [--ids bangumi:1,anilist:2]
  python the_nhan_vat.py loc   --cards data/characters.json --chu-de mèo --vai-tro "người dẫn đường" --ty-le chibi [--loai mèo] [--q "linh thú"]

loc: mỗi cờ chỉ khớp trường của nó (--chu-de với chu_de, --loai với loai...); --q tìm tự do trên mọi trường kể cả mo_ta.
"""
import argparse
import json
import re
from pathlib import Path


def slug(s):
    return re.sub(r"[^\w\-]+", "-", s.lower()).strip("-")[:60]


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def tags_flat(c):
    st = c.get("style_tags") or {}
    return [v for vs in st.values() for v in (vs if isinstance(vs, list) else [vs])]


def cmd_notes(a):
    d = Path(a.dir)
    d.mkdir(parents=True, exist_ok=True)
    cards = load(a.cards)
    for c in cards:
        w = c["works"][0] if c.get("works") else {}
        lines = [
            "---", "type: character", f"id: \"{c['id']}\"", f"name: \"{c['name']}\"",
            f"work: \"{w.get('title', '')}\"", f"role: \"{w.get('role', '')}\"",
            f"chu_de: {json.dumps(c.get('chu_de', []), ensure_ascii=False)}",
            f"loai: \"{c.get('loai', '')}\"", f"vai_tro: \"{c.get('vai_tro', '')}\"", f"archetype: \"{c.get('archetype', '')}\"",
            f"ty_le: \"{c.get('ty_le', '')}\"",
            f"style_tags: {json.dumps(tags_flat(c), ensure_ascii=False)}", "---",
            f"# {c['name']} ({c.get('name_native') or ''})", "",
            c.get("mo_ta") or "_Chưa mô tả._", "",
            "## Hình ảnh",
            f"- Hình khối: {c.get('hinh_khoi', '')}", f"- Bảng màu: {c.get('bang_mau', '')}",
            f"- Đặc điểm nhận diện: {c.get('dac_diem_nhan_dien', '')}", f"- Trang phục: {c.get('trang_phuc', '')}", "",
            "## Nguồn",
            f"- {c['source']}: {c['source_url']}",
            *[f"- Tác phẩm: [{x.get('title')}]({x.get('url')}) · {x.get('role', '')}" for x in c.get("works", [])],
            f"- Ảnh (link, không lưu): {c.get('image_url', '')}",
        ]
        (d / f"{slug(c['id'])}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"notes": len(cards), "dir": str(d)}, ensure_ascii=False))


def cmd_v2(a):
    """Character Card V2. Chỉ dùng phần ta tự viết, không đưa tóm tắt nguồn vào."""
    d = Path(a.dir)
    d.mkdir(parents=True, exist_ok=True)
    ids = set(a.ids.split(",")) if a.ids else None
    n = 0
    for c in load(a.cards):
        if ids and c["id"] not in ids:
            continue
        if not c.get("mo_ta"):
            continue
        look = "; ".join(f"{k}: {c[k]}" for k in ("hinh_khoi", "bang_mau", "dac_diem_nhan_dien", "trang_phuc", "ty_le") if c.get(k))
        card = {
            "spec": "chara_card_v2", "spec_version": "2.0",
            "data": {
                "name": c["name"], "description": f"{c['mo_ta']}\nNgoại hình: {look}",
                "personality": c.get("archetype", ""), "scenario": "", "first_mes": "", "mes_example": "",
                "creator_notes": f"Thẻ tham khảo LAB020, nguồn {c['source_url']}. Nhân vật thuộc IP của người khác: chỉ dùng để học cấu trúc.",
                "system_prompt": "", "post_history_instructions": "", "alternate_greetings": [],
                "tags": list(dict.fromkeys(c.get("chu_de", []) + tags_flat(c))),
                "creator": "LINHX LAB020", "character_version": "0.1",
                "extensions": {"linhx": {"id": c["id"], "vai_tro": c.get("vai_tro", ""), "works": c.get("works", [])}},
            },
        }
        (d / f"{slug(c['id'])}.json").write_text(json.dumps(card, ensure_ascii=False, indent=1), encoding="utf-8")
        n += 1
    print(json.dumps({"cards_v2": n, "dir": str(d)}, ensure_ascii=False))


def cmd_loc(a):
    # Bản đầu gộp mọi trường vào một chuỗi: "mèo" trong mo_ta ("hợp Làng Mèo") làm lọt nhân vật không phải mèo.
    def has(q, *vals):
        return not q or any(q.lower() in str(v).lower() for v in vals)

    # ty_le_alias (tu-dien-nhan-vat.json): lọc chibi thì thú mascot/blob cũng tính
    tu_dien = Path(__file__).resolve().parents[3] / "schemas" / "tu-dien-nhan-vat.json"
    aliases = load(tu_dien).get("ty_le_alias", []) if tu_dien.exists() else []

    def ty_le_ok(c):
        if has(a.ty_le, c.get("ty_le", "")):
            return True
        return any(al["tim"] in a.ty_le.lower() and al["cung_khop"] in c.get("ty_le", "")
                   and c.get("loai", "") not in al.get("tru_loai", []) for al in aliases)

    def ok(c):
        hay = " ".join([*c.get("chu_de", []), c.get("loai", ""), c.get("vai_tro", ""), c.get("archetype", ""),
                        c.get("ty_le", ""), *tags_flat(c), c.get("mo_ta", "")])
        return (has(a.chu_de, *c.get("chu_de", [])) and has(a.vai_tro, c.get("vai_tro", ""))
                and ty_le_ok(c) and has(a.loai, c.get("loai", "")) and has(a.q, hay))
    hits = [c for c in load(a.cards) if ok(c)]
    hits.sort(key=lambda c: -(c.get("popularity") or 0))
    for c in hits[: a.n]:
        w = c["works"][0]["title"] if c.get("works") else ""
        print(f"{c['id']}\t{c['name']}\t{w}\t{c.get('loai', '')}\t{c.get('vai_tro', '')}\t{c.get('ty_le', '')}")
    print(f"# {len(hits)} kết quả")


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("notes"); p.add_argument("--cards", required=True); p.add_argument("--dir", required=True)
    p = sp.add_parser("v2"); p.add_argument("--cards", required=True); p.add_argument("--dir", required=True); p.add_argument("--ids")
    p = sp.add_parser("loc"); p.add_argument("--cards", required=True)
    for f in ("--chu-de", "--vai-tro", "--ty-le", "--loai", "--q"):
        p.add_argument(f)
    p.add_argument("--n", type=int, default=20)
    a = ap.parse_args()
    {"notes": cmd_notes, "v2": cmd_v2, "loc": cmd_loc}[a.cmd](a)


if __name__ == "__main__":
    main()
