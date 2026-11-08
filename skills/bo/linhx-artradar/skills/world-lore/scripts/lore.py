"""Lorebook (M5): kiểm mâu thuẫn đơn giản, xuất world info SillyTavern và ghi chú Markdown.

  python lore.py kiem --lore data/lore/warrior-cats.json [data/lore/khac.json ...]
  python lore.py xuat --lore data/lore/warrior-cats.json --st output/lore/warrior-cats.st.json --md output/lore/warrior-cats

Mỗi file lore là mảng mục: {id, ip, loai, keys[], noi_dung, nguon[], lien_quan[]}.
noi_dung do Claude tự viết (2-4 câu); nguon chỉ ghi link, chữ Fandom (CC BY-SA) nếu trích thì ngắn và có nguồn.
Chỉ dùng thư viện chuẩn Python 3.9+.
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

LOAI = ["địa danh", "phe", "hệ sức mạnh", "luật thế giới", "sinh vật", "vật phẩm", "sự kiện"]
# thứ tự chèn trong SillyTavern: luật/hệ sức mạnh đứng trước để model đọc nền trước
ORDER = {"luật thế giới": 200, "hệ sức mạnh": 190, "phe": 180, "địa danh": 170, "sinh vật": 160, "sự kiện": 150, "vật phẩm": 140}


def load(paths):
    out = []
    for p in paths:
        out += json.loads(Path(p).read_text(encoding="utf-8"))
    return out


def so_cau(text):
    return len([s for s in re.split(r"(?<=[.!?…])\s+", text.strip()) if s])


def kiem_list(entries):
    """Trả về danh sách (mức, mã, thông điệp). Mức: loi | canh_bao."""
    res = []
    ids = defaultdict(int)
    key_owner = defaultdict(list)
    for e in entries:
        ids[e.get("id")] += 1
        for f in ("id", "ip", "loai", "keys", "noi_dung"):
            if not e.get(f):
                res.append(("loi", "thieu_truong", f"{e.get('id')}: thiếu {f}"))
        if e.get("loai") and e["loai"] not in LOAI:
            res.append(("loi", "loai_sai", f"{e['id']}: loai '{e['loai']}' không thuộc {LOAI}"))
        n = so_cau(e.get("noi_dung", ""))
        if e.get("noi_dung") and not 2 <= n <= 4:
            res.append(("canh_bao", "do_dai", f"{e['id']}: noi_dung {n} câu (nên 2-4)"))
        if not e.get("nguon"):
            res.append(("canh_bao", "thieu_nguon", f"{e['id']}: chưa ghi nguồn"))
        for k in e.get("keys", []):
            key_owner[(e.get("ip"), k.lower())].append(e["id"])
    for i, n in ids.items():
        if n > 1:
            res.append(("loi", "trung_id", f"{i}: xuất hiện {n} lần"))
    for (ip, k), owners in key_owner.items():
        if len(set(owners)) > 1:
            res.append(("loi", "trung_key", f"[{ip}] key '{k}' nằm ở {', '.join(sorted(set(owners)))}"))
    known = {e["id"] for e in entries}
    for e in entries:
        for r in e.get("lien_quan", []):
            if r not in known:
                res.append(("loi", "lien_quan_hong", f"{e['id']}: lien_quan trỏ tới '{r}' không có"))
    # mồ côi: không trỏ tới ai, không ai trỏ tới, và không key nào được nhắc trong nội dung mục khác
    in_ref = defaultdict(int)
    for e in entries:
        for r in e.get("lien_quan", []):
            in_ref[r] += 1
    for i, e in enumerate(entries):
        others = " ".join(x.get("noi_dung", "") for j, x in enumerate(entries) if j != i and x.get("ip") == e.get("ip")).lower()
        nhac = any(k.lower() in others for k in e.get("keys", []))
        if not e.get("lien_quan") and not in_ref[e["id"]] and not nhac:
            res.append(("canh_bao", "mo_coi", f"{e['id']}: mục mồ côi (không liên kết, không được nhắc)"))
    return res


def cmd_kiem(a):
    entries = load(a.lore)
    res = kiem_list(entries)
    for muc, ma, msg in res:
        print(f"[{muc}] {ma}: {msg}")
    tom = {"muc": len(entries), "loi": sum(r[0] == "loi" for r in res), "canh_bao": sum(r[0] == "canh_bao" for r in res),
           "theo_loai": {l: sum(e.get("loai") == l for e in entries) for l in LOAI}}
    print(json.dumps(tom, ensure_ascii=False))
    if tom["loi"]:
        sys.exit(1)


def to_st(entries, name):
    """World info SillyTavern (định dạng file xuất/nhập của tab World Info)."""
    out = {}
    for i, e in enumerate(entries):
        out[str(i)] = {
            "uid": i, "key": e["keys"], "keysecondary": [], "comment": f"{e['loai']}: {e['id']}",
            "content": e["noi_dung"], "constant": e["loai"] == "luật thế giới" and e.get("constant", False),
            "vectorized": False, "selective": True, "selectiveLogic": 0, "addMemo": True,
            "order": ORDER.get(e["loai"], 100), "position": 0, "disable": False, "excludeRecursion": False,
            "preventRecursion": False, "delayUntilRecursion": False, "probability": 100, "useProbability": True,
            "depth": 4, "group": e["loai"], "groupOverride": False, "groupWeight": 100, "scanDepth": None,
            "caseSensitive": None, "matchWholeWords": None, "useGroupScoring": None, "automationId": "",
            "role": None, "sticky": 0, "cooldown": 0, "delay": 0, "displayIndex": i,
            "extensions": {"linhx": {"id": e["id"], "ip": e["ip"], "nguon": e.get("nguon", []), "lien_quan": e.get("lien_quan", [])}},
        }
    return {"name": name, "entries": out}


def cmd_xuat(a):
    entries = load(a.lore)
    loi = [r for r in kiem_list(entries) if r[0] == "loi"]
    if loi:
        print(json.dumps({"dung": "còn lỗi, chạy kiem trước", "loi": [r[2] for r in loi]}, ensure_ascii=False))
        sys.exit(1)
    name = a.name or Path(a.lore[0]).stem
    if a.st:
        Path(a.st).parent.mkdir(parents=True, exist_ok=True)
        Path(a.st).write_text(json.dumps(to_st(entries, name), ensure_ascii=False, indent=1), encoding="utf-8")
    if a.md:
        d = Path(a.md)
        d.mkdir(parents=True, exist_ok=True)
        by_id = {e["id"]: e for e in entries}
        for e in entries:
            lines = ["---", "type: lore", f"id: \"{e['id']}\"", f"ip: \"{e['ip']}\"", f"loai: \"{e['loai']}\"",
                     f"keys: {json.dumps(e['keys'], ensure_ascii=False)}", "---", f"# {e['keys'][0]}", "",
                     e["noi_dung"], ""]
            if e.get("lien_quan"):
                lines += ["## Liên quan", *[f"- [[{r}]] ({by_id[r]['keys'][0]})" for r in e["lien_quan"] if r in by_id], ""]
            lines += ["## Nguồn", *[f"- {n}" for n in e.get("nguon", [])]]
            (d / f"{e['id']}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        idx = [f"# Lorebook {name}", ""]
        for l in LOAI:
            es = [e for e in entries if e["loai"] == l]
            if es:
                idx += [f"## {l}", *[f"- [[{e['id']}]] {e['keys'][0]}" for e in es], ""]
        (d / "_index.md").write_text("\n".join(idx), encoding="utf-8")
    print(json.dumps({"muc": len(entries), "st": a.st, "md": a.md}, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("kiem"); p.add_argument("--lore", nargs="+", required=True)
    p = sp.add_parser("xuat"); p.add_argument("--lore", nargs="+", required=True)
    p.add_argument("--st"); p.add_argument("--md"); p.add_argument("--name")
    a = ap.parse_args()
    {"kiem": cmd_kiem, "xuat": cmd_xuat}[a.cmd](a)


if __name__ == "__main__":
    main()
