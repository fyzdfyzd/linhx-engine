"""M2 thu-link: lấy metadata + link (không tải ảnh) vào KHO/nguon/records.jsonl.

Cách dùng (chạy trên máy Linh):
  python thu_link.py url "https://www.instagram.com/<ten>/saved/kho-y-tuong/<id>/" --cookies chrome
  python thu_link.py url "https://www.pinterest.com/<ten>/<board>/"
  python thu_link.py dan nguon/dan-tay.txt          # mỗi dòng một link Linh dán
  python thu_link.py chuan-hoa du-lieu.json          # chuẩn hoá file gallery-dl -j có sẵn

Dựa trên gallery-dl -j: mỗi message dạng [3, url_anh, metadata] (Message.Url).
"""
import argparse, datetime, json, os, re, subprocess, sys
from pathlib import Path

KHO = Path(os.environ.get("KHO_MINH_HOA", r"D:\LINHX\KHO-MINH-HOA"))
RECORDS = KHO / "nguon" / "records.jsonl"
NOAI = re.compile(r"(^|\W)(no[\s_-]?ai|noimageai|no ai training)(\W|$)", re.I)


def nguon_tu_url(url):
    for key in ("instagram", "pinterest", "behance", "bsky", "reddit", "tumblr", "deviantart"):
        if key in url:
            return {"instagram": "instagram-saved", "bsky": "bluesky"}.get(key, key if key != "pinterest" else "pinterest-board")
    return "web"


def chuan_hoa(meta, url_anh, nguon):
    """Đưa metadata của từng extractor về một dạng chung."""
    cat = meta.get("category", "")
    if cat == "instagram":
        code = meta.get("post_shortcode") or meta.get("shortcode")
        rid, link = f"instagram:{code}", f"https://www.instagram.com/p/{code}/"
        tac_gia = {"ten": meta.get("fullname") or meta.get("username"), "link": f"https://www.instagram.com/{meta.get('username')}/"}
        chu_thich, tuong_tac = meta.get("description", ""), meta.get("likes")
    elif cat == "pinterest":
        rid, link = f"pinterest:{meta.get('id')}", f"https://www.pinterest.com/pin/{meta.get('id')}/"
        pinner = meta.get("pinner") or {}
        tac_gia = {"ten": (meta.get("native_creator") or {}).get("full_name") or pinner.get("full_name"), "link": meta.get("link") or ""}
        chu_thich, tuong_tac = " ".join(filter(None, [meta.get("title"), meta.get("description")])), meta.get("repin_count")
    else:
        pid = meta.get("id") or meta.get("project_id") or meta.get("post_id") or url_anh
        rid = f"{cat or nguon}:{pid}"
        link = meta.get("url") or meta.get("post_url") or meta.get("permalink") or url_anh
        user = meta.get("user") or meta.get("owner") or meta.get("author") or {}
        ten = user.get("display_name") or user.get("name") or user.get("username") if isinstance(user, dict) else str(user)
        tac_gia = {"ten": ten, "link": ""}
        chu_thich = " ".join(filter(None, [meta.get("title"), meta.get("description")]))
        tuong_tac = meta.get("likes") or meta.get("stats", {}).get("appreciations") if isinstance(meta.get("stats"), dict) else meta.get("likes")
    tags = meta.get("tags") or []
    if isinstance(tags, str):
        tags = [tags]
    noai = bool(NOAI.search(chu_thich or "")) or any(NOAI.search(str(t)) for t in tags)
    return {
        "id": rid, "link_goc": link, "tac_gia": tac_gia, "nguon": nguon,
        "chu_thich_goc": (chu_thich or "")[:1500], "hashtag": [str(t) for t in tags][:30],
        "tuong_tac": tuong_tac, "ngay_dang": str(meta.get("date") or meta.get("post_date") or ""),
        "anh_tam_url": url_anh,  # link CDN có chữ ký, hết hạn nhanh: chỉ để M3/M4 dùng ngay, không đưa vào kho
        "co_noai": noai, "ngay_quet": datetime.date.today().isoformat(),
    }


def doc_messages(messages, nguon):
    out, da_co = [], set()
    for m in messages:
        if not isinstance(m, list) or len(m) < 3 or m[0] != 3:  # 3 = Message.Url
            continue
        r = chuan_hoa(m[2], m[1], nguon)
        if r["id"] in da_co:  # bài nhiều ảnh: giữ ảnh đầu
            continue
        da_co.add(r["id"])
        out.append(r)
    return out


def ghi(records):
    RECORDS.parent.mkdir(parents=True, exist_ok=True)
    cu = set()
    if RECORDS.exists():
        cu = {json.loads(l)["id"] for l in RECORDS.read_text(encoding="utf-8").splitlines() if l.strip()}
    moi = [r for r in records if r["id"] not in cu]
    with RECORDS.open("a", encoding="utf-8") as f:
        for r in moi:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    bo = sum(r["co_noai"] for r in moi)
    print(f"Thêm {len(moi)} bản ghi mới ({bo} gắn NoAI sẽ bị bỏ ở bước lọc), bỏ qua {len(records) - len(moi)} đã có. Kho: {RECORDS}")


def chay_gallery_dl(url, cookies, sleep):
    cmd = ["gallery-dl", "-j", "--sleep-request", str(sleep), url]
    if cookies:
        cmd[1:1] = ["--cookies-from-browser", cookies]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if p.returncode not in (0, 4) or not p.stdout.strip():
        sys.exit(f"gallery-dl lỗi:\n{p.stderr[-1500:]}")
    return json.loads(p.stdout)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="lenh", required=True)
    a = sub.add_parser("url"); a.add_argument("url"); a.add_argument("--cookies", default=""); a.add_argument("--sleep", type=float, default=6)
    b = sub.add_parser("dan"); b.add_argument("file")
    c = sub.add_parser("chuan-hoa"); c.add_argument("file"); c.add_argument("--nguon", default="")
    args = ap.parse_args()
    if args.lenh == "url":
        ghi(doc_messages(chay_gallery_dl(args.url, args.cookies, args.sleep), nguon_tu_url(args.url)))
    elif args.lenh == "chuan-hoa":
        msgs = json.loads(Path(args.file).read_text(encoding="utf-8"))
        ghi(doc_messages(msgs, args.nguon or "web"))
    else:
        recs = []
        for line in Path(args.file).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                recs.append({"id": f"dan:{line}", "link_goc": line, "tac_gia": {"ten": "", "link": ""}, "nguon": "linh-dan-tay",
                             "chu_thich_goc": "", "hashtag": [], "tuong_tac": None, "ngay_dang": "", "anh_tam_url": "",
                             "co_noai": False, "ngay_quet": datetime.date.today().isoformat()})
        ghi(recs)


if __name__ == "__main__":
    main()
