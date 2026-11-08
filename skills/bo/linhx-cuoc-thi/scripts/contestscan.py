#!/usr/bin/env python3
"""LAB022 Radar cuộc thi & giải thưởng: quét cuộc thi sáng tạo, viết lách, giải thưởng tại Việt Nam,
chấm độ hợp với hồ sơ cá nhân (branding), lịch hạn (.ics), pipeline nộp bài, theo dõi kết quả.

Tái dùng khung của LAB013 (callscan.py): nguồn rss/html → bóc hạn → chấm → báo cáo → digest.
Khác LAB013: đơn vị là "cuộc thi" (thể loại, ngôn ngữ, phí, ngày công bố kết quả), luật cứng về
điều kiện cá nhân (tuổi, sinh viên, tổ chức), pipeline có "chờ kết quả", lệnh `results` dò trang kết quả,
lệnh `ics` xuất lịch, sổ giải thưởng cho branding.

Chỉ dùng thư viện chuẩn Python 3.9+. Chạy từ thư mục radar (có config/sources.json, config/profile.json):
    python <plugin>/scripts/contestscan.py seed data/seed-contests.json   # nhập danh mục tuyển tay
    python <plugin>/scripts/contestscan.py scan                            # quét nguồn trong config/sources.json
    python <plugin>/scripts/contestscan.py extract                         # bóc hạn nộp, giải, phí
    python <plugin>/scripts/contestscan.py score                           # chấm theo config/profile.json
    python <plugin>/scripts/contestscan.py report                          # output/BANG-CUOC-THI.md + output/lich-han.ics
    python <plugin>/scripts/contestscan.py digest                          # output/digest/DIGEST-<ngày>.md
    python <plugin>/scripts/contestscan.py mark <id> "đang viết" [--note ..] [--entry "tên bài"]
    python <plugin>/scripts/contestscan.py results                         # dò trang kết quả các bài đã nộp
    python <plugin>/scripts/contestscan.py all                             # scan → extract → score → report → digest
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

# Thư mục radar (chứa config/ data/ output/): biến RADAR_HOME, nếu không có thì thư mục đang đứng.
ROOT = Path(os.environ.get("RADAR_HOME") or Path.cwd()).resolve()
SRC = ROOT / "config"
DATA = ROOT / "data"
OUT = ROOT / "output"
DB = DATA / "contests.json"
PIPE = DATA / "pipeline.json"
TODAY = dt.date.today()
UA = "Mozilla/5.0 (LINHX-LAB contest-radar)"

CONTEST_WORDS = [
    "cuộc thi", "giải thưởng", "thể lệ", "phát động", "sáng tác", "viết về", "truyện ngắn", "tản văn",
    "bút ký", "tác phẩm", "dự thi", "bình chọn", "đề cử", "vinh danh", "tôn vinh", "trao giải",
    "competition", "contest", "award", "prize", "call for entries", "call for submissions", "open call",
    "submissions", "nominations", "essay", "short story", "festival",
]

MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august",
     "september", "october", "november", "december"], 1)}
MONTHS.update({k[:3]: v for k, v in list(MONTHS.items())})
MONTHS["sept"] = 9


# ---------------------------------------------------------------- tiện ích
def load_json(p: Path, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def save_json(p: Path, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def canon_url(url: str) -> str:
    """Bỏ utm_*, fbclid, m./www., dấu / cuối: cùng một bài đăng lại không thành hai mục."""
    u = urlparse((url or "").strip())
    q = "&".join(x for x in u.query.split("&") if x and not re.match(r"(utm_|fbclid|gclid)", x))
    host = re.sub(r"^(www|m)\.", "", u.netloc.lower())
    return f"{host}{u.path.rstrip('/')}{'?' + q if q else ''}"


def make_id(url: str, title: str) -> str:
    return hashlib.sha1((canon_url(url) or title.strip().lower()).encode()).hexdigest()[:10]


def fetch(url: str, timeout=25) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "vi,en;q=0.8"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        enc = r.headers.get_content_charset() or "utf-8"
    return raw.decode(enc, errors="replace")


def strip_tags(s: str) -> str:
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s or "", flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").lower()).strip()


def looks_like_contest(text: str) -> bool:
    t = norm(text)
    return any(w in t for w in CONTEST_WORDS)


# ---------------------------------------------------------------- đọc nguồn
class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self._href, self._buf = [], None, []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._buf = []

    def handle_data(self, data):
        if self._href is not None:
            self._buf.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href:
            text = re.sub(r"\s+", " ", "".join(self._buf)).strip()
            if text:
                self.links.append((self._href, text))
            self._href = None


def parse_rss(xml_text: str, src: dict) -> list[dict]:
    items = []
    root = ET.fromstring(xml_text.encode("utf-8", errors="replace"))
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entries = root.findall(".//item") or root.findall(".//atom:entry", ns)
    for e in entries:
        def g(tag):
            el = e.find(tag) if not tag.startswith("atom:") else e.find(tag, ns)
            return (el.text or "") if el is not None else ""
        title = g("title") or g("atom:title")
        link = g("link")
        if not link:
            le = e.find("atom:link", ns)
            link = le.get("href") if le is not None else ""
        desc = g("description") or g("atom:summary") or g("atom:content")
        pub = g("pubDate") or g("atom:updated") or g("atom:published")
        items.append({"title": strip_tags(title), "url": link.strip(),
                      "summary": strip_tags(desc)[:1500], "published": pub.strip()})
    return items


def parse_html_list(page: str, src: dict) -> list[dict]:
    p = LinkParser()
    p.feed(page)
    base = src["url"]
    host = urlparse(base).netloc
    inc = [re.compile(x, re.I) for x in src.get("link_patterns", [])]
    seen, items = set(), []
    for href, text in p.links:
        url = urljoin(base, href)
        if urlparse(url).netloc != host or url in seen or len(text) < 15:
            continue
        if inc and not any(r.search(url) for r in inc):
            continue
        seen.add(url)
        items.append({"title": text, "url": url, "summary": "", "published": ""})
    return items


def blank(it: dict, src: dict) -> dict:
    return {
        "id": make_id(it["url"], it["title"]), "title": it["title"], "organizer": src.get("organizer", ""),
        "category": src.get("category", ""), "format": "", "eligibility": "", "language": "", "fee": "",
        "prize": "", "url": it["url"], "deadline": None, "expected_deadline": None, "results_date": None,
        "results_url": "", "cycle": "", "status": "new", "verified": False, "source": src["id"],
        "summary": it["summary"], "published": it["published"], "branding_value": None,
        "first_seen": TODAY.isoformat(), "last_seen": TODAY.isoformat(), "note": "",
    }


def words(t: str) -> set:
    return set(re.sub(r"20\d\d|[^\w\s]", " ", norm(t)).split())


def similar(a: str, b: str) -> bool:
    """Khớp mờ (học từ eventio): Jaccard tiêu đề >= 0.7."""
    wa, wb = words(a), words(b)
    return bool(wa and wb) and len(wa & wb) / len(wa | wb) >= 0.7


def title_key(t: str) -> str:
    """Khử trùng bài đăng lại cùng cuộc thi ở nhiều báo: bỏ năm, dấu câu, lấy 8 từ đầu."""
    t = re.sub(r"20\d\d|lần thứ \w+|[^\w\s]", " ", norm(t))
    return " ".join(t.split()[:8])


def cmd_scan(args):
    sources = load_json(SRC / "sources.json", {"sources": []})["sources"]
    db = {c["id"]: c for c in load_json(DB, [])}
    keys = {title_key(c["title"]): c["id"] for c in db.values()}
    log = []
    for src in sources:
        if not src.get("active", True) or src.get("kind") not in ("rss", "html"):
            continue
        try:
            text = fetch(src["url"])
            items = parse_rss(text, src) if src["kind"] == "rss" else parse_html_list(text, src)
        except Exception as e:  # nguồn chết không làm hỏng cả lượt quét
            log.append(f"LỖI  {src['id']}: {type(e).__name__}: {e}")
            continue
        new = 0
        for it in items:
            if src["kind"] == "rss" and src.get("link_patterns") and not any(
                    re.search(x, f"{it['url']} {it['title']}", re.I) for x in src["link_patterns"]):
                continue
            if src.get("filter", True) and not looks_like_contest(f"{it['title']} {it['summary']}"):
                continue
            c = blank(it, src)
            dup = db.get(c["id"]) or db.get(keys.get(title_key(c["title"]), "")) or next(
                (x for x in db.values() if similar(x["title"], c["title"])), None)
            if dup:
                dup["last_seen"] = TODAY.isoformat()
                dup.setdefault("mentions", [])
                if it["url"] not in dup["mentions"] and it["url"] != dup["url"]:
                    dup["mentions"].append(it["url"])
                continue
            db[c["id"]] = c
            keys[title_key(c["title"])] = c["id"]
            new += 1
        log.append(f"OK   {src['id']}: {len(items)} tin, {new} cuộc thi mới")
    save_json(DB, sorted(db.values(), key=lambda c: c["first_seen"]))
    with (DATA / "scan-log.txt").open("a", encoding="utf-8") as f:
        f.write(f"\n## {dt.datetime.now():%Y-%m-%d %H:%M}\n" + "\n".join(log) + "\n")
    print("\n".join(log))


def cmd_seed(args):
    db = {c["id"]: c for c in load_json(DB, [])}
    raw = load_json(Path(args.file), [])
    seed = raw.get("contests", []) if isinstance(raw, dict) else raw
    for s in seed:
        cid = s.get("id") or make_id(s.get("url", ""), s["title"])
        base = db.get(cid) or dict(blank({"url": s.get("url", ""), "title": s["title"], "summary": "", "published": ""},
                                         {"id": "seed"}))
        base.update({k: v for k, v in s.items() if k != "status" or v})
        base["id"] = cid
        base["last_seen"] = TODAY.isoformat()
        db[cid] = base
    save_json(DB, list(db.values()))
    print(f"Đã nhập {len(seed)} cuộc thi, tổng {len(db)}")


# ---------------------------------------------------------------- bóc thông tin
DATE_PATTERNS = [
    (re.compile(r"(20\d\d)-(\d{1,2})-(\d{1,2})"), lambda m: (int(m[1]), int(m[2]), int(m[3]))),
    (re.compile(r"(\d{1,2})[/.-](\d{1,2})[/.-](20\d\d)"), lambda m: (int(m[3]), int(m[2]), int(m[1]))),
    (re.compile(r"ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})(?:\s+năm\s+|/)(20\d\d)", re.I),
     lambda m: (int(m[3]), int(m[2]), int(m[1]))),
    (re.compile(r"(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]{3,9})\.?,?\s+(20\d\d)"),
     lambda m: (int(m[3]), MONTHS.get(m[2].lower()), int(m[1]))),
    (re.compile(r"([A-Za-z]{3,9})\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(20\d\d)"),
     lambda m: (int(m[3]), MONTHS.get(m[1].lower()), int(m[2]))),
]
DEADLINE_CUE = re.compile(
    r"(hạn (?:chót|nộp|cuối|nhận)|thời hạn|nhận (?:bài|tác phẩm) (?:dự thi )?(?:đến|trước)|trước ngày|"
    r"kết thúc nhận|đến hết ngày|deadline|closing date|close[sd]? on|due|submit(?:ted)? by|no later than)", re.I)
RESULT_CUE = re.compile(r"(công bố kết quả|lễ (?:tổng kết và )?trao giải|trao giải|results? (?:announced|will be)|winners announced)", re.I)
PRIZE_RE = re.compile(
    r"((?:giải (?:đặc biệt|nhất|a)[^.;]{0,40}?)?[\d.,]+\s?(?:triệu đồng|tr đồng|tỷ đồng|triệu|đồng|VNĐ|VND)"
    r"|(?:US\$|USD|\$|€|£)\s?[\d.,]+(?:\s?(?:million|k))?)", re.I)
FEE_FREE = re.compile(r"(miễn phí|không (?:thu|mất) phí|free (?:to enter|entry)|no (?:entry )?fee)", re.I)


def find_dates(text: str) -> list[tuple[int, dt.date]]:
    out = []
    for rx, conv in DATE_PATTERNS:
        for m in rx.finditer(text):
            try:
                y, mo, d = conv(m)
                if mo:
                    out.append((m.start(), dt.date(y, mo, d)))
            except (ValueError, TypeError):
                pass
    return out


def nearest(dates, cue_rx, text, limit=120):
    cues = [m.end() for m in cue_rx.finditer(text)]
    best = None
    for pos, d in dates:
        dist = min((abs(pos - q) for q in cues), default=10**6)
        if dist < limit and (best is None or dist < best[0]):
            best = (dist, d)
    return best[1] if best else None


def regex_extract(c: dict) -> dict:
    text = f"{c.get('title','')} . {c.get('summary','')}"
    dates = find_dates(text)
    if not c.get("deadline"):
        d = nearest(dates, DEADLINE_CUE, text)
        if d:
            c["deadline"] = d.isoformat()
    if not c.get("results_date"):
        d = nearest(dates, RESULT_CUE, text)
        if d:
            c["results_date"] = d.isoformat()
    if not c.get("prize"):
        m = PRIZE_RE.search(text)
        if m:
            c["prize"] = m.group(0).strip()
    if not c.get("fee") and FEE_FREE.search(text):
        c["fee"] = "miễn phí"
    if not c.get("format"):
        t = norm(text)
        for fmt, words in [("truyen-ngan", ["truyện ngắn", "short story"]), ("tan-van", ["tản văn", "bút ký", "ký sự"]),
                           ("tho", ["thơ", "poetry"]), ("tieu-luan", ["tiểu luận", "essay", "bài luận", "bình luận"]),
                           ("bai-bao", ["báo chí", "tác phẩm báo", "journalism"]), ("video", ["video", "phim", "film", "clip"]),
                           ("anh", ["ảnh", "photo"]), ("podcast", ["podcast"]),
                           ("ho-so-de-cu", ["đề cử", "bình chọn", "vinh danh", "nominat", "30 under 30"]),
                           ("chien-dich", ["chiến dịch", "campaign"])]:
            if any(w in t for w in words):
                c["format"] = fmt
                break
    return c


def cmd_extract(args):
    db = [regex_extract(c) for c in load_json(DB, [])]
    save_json(DB, db)
    print(f"{sum(1 for c in db if c.get('deadline'))}/{len(db)} cuộc thi có hạn nộp")


# ---------------------------------------------------------------- điều kiện + chấm điểm
AGE_RE = re.compile(r"(?:từ|from)\s*(\d{1,2})\s*(?:đến|tới|-|to)\s*(\d{1,2})\s*tuổi|(?:dưới|under|không quá|tối đa)\s*(\d{1,2})\s*tuổi|aged?\s*(\d{1,2})\s*(?:-|to)\s*(\d{1,2})|under\s*(\d{2})", re.I)


def gate(c: dict, prof: dict) -> tuple[str, str]:
    """Luật cứng điều kiện cá nhân. Trả (vai, lý do). Ghi đè tay bằng trường `gate` trong dữ liệu."""
    if c.get("gate"):
        return c["gate"], "ghi đè tay"
    e = norm(" ".join([c.get("eligibility", ""), c.get("title", ""), c.get("summary", "")[:600]]))
    age = prof.get("age")
    for m in AGE_RE.finditer(e):
        nums = [int(x) for x in m.groups() if x]
        hi = max(nums) if nums else None
        if age and hi and age > hi:
            team = prof.get("team") or {}
            ya = team.get("youngest_age")
            if team.get("available") and (ya is None or ya <= hi):
                return "Giao đội/CTV", f"giới hạn tuổi {hi}, Linh quá tuổi"
            return "Không đủ điều kiện", f"giới hạn tuổi {hi}"
        if not age and hi and hi < 60:
            return "Kiểm điều kiện", f"giới hạn tuổi {hi}, chưa điền tuổi trong profile.json"
    open_all = any(ok in e for ok in prof.get("unless", []))
    for w in prof.get("excluded_if", []):
        if w in e and not open_all:
            return "Không đủ điều kiện", f"thể lệ có '{w}'"
    for w in prof.get("check_if", []):
        if w in e and not open_all:
            return "Kiểm điều kiện", f"thể lệ có '{w}'"
    for w in prof.get("organization_only", []):
        if w in e:
            return "Qua tổ chức", f"chỉ nhận '{w}'"
    nat = norm(c.get("eligibility", ""))
    if nat and any(x in nat for x in ("citizens of", "residents of", "commonwealth")) and "viet" not in nat:
        return "Kiểm điều kiện", "giới hạn quốc tịch"
    return "Nộp được", ""


def score(c: dict, prof: dict) -> int:
    t = norm(" ".join([c.get("title", ""), c.get("summary", ""), c.get("organizer", ""), c.get("format", ""),
                       c.get("category", ""), c.get("fit_note", ""), " ".join(c.get("tags", []))]))
    s = 0
    for kw, w in prof["keywords"].items():
        if re.search(r"(?<!\w)" + re.escape(kw) + r"(?!\w)", t):
            s += w
    for kw, w in prof.get("must_not", {}).items():
        if kw in t:
            s -= w * 2
    s += prof.get("format_weight", {}).get(c.get("format", ""), 0)
    s += prof.get("category_weight", {}).get(c.get("category", ""), 0)
    bv = c.get("branding_value")
    if isinstance(bv, (int, float)):
        s += int(bv) * prof.get("branding_weight", 3)
    if c.get("fee") and not re.search(r"miễn phí|free|0", str(c["fee"]), re.I):
        s -= 2
    return max(0, min(100, s * 3))


def state_of(c: dict) -> str:
    d = c.get("deadline")
    if not d:
        exp = c.get("expected_deadline")
        return "dự kiến" if exp or c.get("cycle") else "chưa rõ hạn"
    days = (dt.date.fromisoformat(d) - TODAY).days
    if days < 0:
        return "lặp lại, chờ mùa sau" if "năm" in (c.get("cycle") or "") or c.get("cycle") == "recurring" else "đã đóng"
    return "gấp" if days <= 14 else "đang mở"


def exp_month(c):
    """expected_deadline có thể là '2027-03' hoặc chữ; lấy YYYY-MM nếu đọc được."""
    m = re.match(r"(20\d\d)-(\d\d)", str(c.get("expected_deadline") or ""))
    return f"{m[1]}-{m[2]}" if m else None


def cmd_score(args):
    prof = load_json(SRC / "profile.json", {})
    db = load_json(DB, [])
    for c in db:
        c["score"] = score(c, prof)
        c["gate_role"], c["gate_reason"] = gate(c, prof)
        c["state"] = state_of(c)
    save_json(DB, db)
    top = sorted([c for c in db if c["gate_role"] == "Nộp được"], key=lambda c: -c["score"])[:8]
    print("Top: " + "; ".join(f"{c['title'][:45]} ({c['score']})" for c in top))


# ---------------------------------------------------------------- pipeline + kết quả
STAGES = ["mới", "đang xem", "đang viết", "đã nộp", "chờ kết quả", "vào vòng sau", "đạt giải", "trượt", "bỏ",
          "đã khai thác"]


def cmd_mark(args):
    if args.stage not in STAGES:
        sys.exit(f"Giai đoạn phải là một trong: {', '.join(STAGES)}")
    pipe = load_json(PIPE, {})
    db = {c["id"]: c for c in load_json(DB, [])}
    if args.id not in db:
        sys.exit(f"Không có id {args.id}")
    rec = pipe.get(args.id, {"history": []})
    rec.update({"stage": args.stage, "updated": TODAY.isoformat(), "title": db[args.id]["title"]})
    if args.note:
        rec["note"] = args.note
    if args.entry:
        rec["entry"] = args.entry
    if args.prize:
        rec["prize"] = args.prize
    rec["history"].append([TODAY.isoformat(), args.stage])
    pipe[args.id] = rec
    save_json(PIPE, pipe)
    print(f"{db[args.id]['title'][:60]} → {args.stage}")
    if args.stage == "đạt giải":
        write_awards(pipe, db)


def write_awards(pipe, db):
    """Sổ giải thưởng: nguồn sự thật cho bio, hồ sơ diễn giả, trang giới thiệu."""
    won = [(k, v) for k, v in pipe.items() if v["stage"] in ("đạt giải", "đã khai thác")]
    lines = ["# Giải thưởng & ghi nhận của Linh", "",
             "Sinh tự động từ `data/pipeline.json` (giai đoạn `đạt giải`). Dùng cho bio, hồ sơ diễn giả, LinkedIn.", ""]
    for k, v in sorted(won, key=lambda kv: kv[1]["updated"], reverse=True):
        c = db.get(k, {})
        lines.append(f"- **{v.get('prize','Đạt giải')}**, {c.get('title', v['title'])} ({c.get('organizer','')}, "
                     f"{v['updated'][:4]}){': ' + v['entry'] if v.get('entry') else ''}. Nguồn: {c.get('results_url') or c.get('url','')}")
    (OUT / "GIAI-THUONG.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def cmd_results(args):
    """Với bài đã nộp: tải trang kết quả, báo nếu trang đổi hoặc thấy tên Linh / tên bài."""
    prof = load_json(SRC / "profile.json", {})
    names = [norm(n) for n in prof.get("watch_names", [])]
    pipe = load_json(PIPE, {})
    db = {c["id"]: c for c in load_json(DB, [])}
    state = load_json(DATA / "state.json", {})
    hashes = state.setdefault("results_hash", {})
    out = []
    for cid, rec in pipe.items():
        if rec["stage"] not in ("đã nộp", "chờ kết quả", "vào vòng sau"):
            continue
        c = db.get(cid, {})
        rd = c.get("results_date")
        url = c.get("results_url") or c.get("url")
        when = f" (dự kiến công bố {rd})" if rd else ""
        try:
            page = norm(strip_tags(fetch(url)))
        except Exception as e:
            out.append(f"- {rec['title']}: không tải được trang kết quả ({type(e).__name__}){when}")
            continue
        h = hashlib.sha1(page.encode()).hexdigest()
        changed = hashes.get(cid) not in (None, h)
        hashes[cid] = h
        hits = [n for n in names + [norm(rec.get("entry", ""))] if n and n in page]
        has_result_words = bool(re.search(r"kết quả|danh sách (?:đạt|trao|vào)|trao giải|winners|shortlist", page))
        flag = "**THẤY TÊN**" if hits else ("trang đã đổi" if changed else "chưa đổi")
        out.append(f"- {rec['title']}: {flag}{', có chữ “kết quả/trao giải”' if has_result_words else ''}{when} · {url}")
    save_json(DATA / "state.json", state)
    text = "\n".join(out) or "- Chưa có bài nào ở giai đoạn đã nộp / chờ kết quả"
    print(text)
    return text


# ---------------------------------------------------------------- báo cáo
LIVE = ("gấp", "đang mở", "dự kiến", "lặp lại, chờ mùa sau", "chưa rõ hạn")


def due(c):
    return c.get("deadline") or (f"~{c['expected_deadline']}" if c.get("expected_deadline") else "?")


def ics(db, pipe) -> str:
    """Lịch hạn nộp (chỉ hạn đã xác định) + nhắc trước 7 ngày; mở được bằng Google/Outlook Calendar."""
    def esc(s):
        return re.sub(r"([,;\\])", r"\\\1", s or "").replace("\n", " ")
    ev = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//LINHX LAB//LAB022 contest radar//VI", "X-WR-CALNAME:Hạn cuộc thi"]
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for c in db:
        if c.get("gate_role") == "Không đủ điều kiện" or pipe.get(c["id"], {}).get("stage") in ("bỏ", "trượt"):
            continue
        for kind, uid, d in (("Hạn nộp", "dl", c.get("deadline")), ("Công bố kết quả", "kq", c.get("results_date"))):
            if not d or d < TODAY.isoformat():
                continue
            if kind == "Công bố kết quả" and pipe.get(c["id"], {}).get("stage") not in ("đã nộp", "chờ kết quả", "vào vòng sau"):
                continue
            day = d.replace("-", "")
            nxt = (dt.date.fromisoformat(d) + dt.timedelta(days=1)).strftime("%Y%m%d")
            ev += ["BEGIN:VEVENT", f"UID:{c['id']}-{uid}@lab022", f"DTSTAMP:{stamp}",
                   f"DTSTART;VALUE=DATE:{day}", f"DTEND;VALUE=DATE:{nxt}",
                   f"SUMMARY:{esc(kind + ': ' + c['title'])}",
                   f"DESCRIPTION:{esc((c.get('organizer') or '') + ' · ' + (c.get('prize') or '') + ' · ' + c.get('url',''))}",
                   f"URL:{c.get('url','')}"]
            if kind == "Hạn nộp":
                for t in ("7", "1"):
                    ev += ["BEGIN:VALARM", f"TRIGGER:-P{t}D", "ACTION:DISPLAY",
                           f"DESCRIPTION:{esc(f'Còn {t} ngày: ' + c['title'])}", "END:VALARM"]
            ev.append("END:VEVENT")
    ev.append("END:VCALENDAR")
    return "\r\n".join(ev) + "\r\n"


def cmd_report(args):
    db = [c for c in load_json(DB, []) if c.get("status") != "bỏ qua"]
    pipe = load_json(PIPE, {})
    OUT.mkdir(exist_ok=True)
    (OUT / "lich-han.ics").write_text(ics(db, pipe), encoding="utf-8")

    def row(c):
        return (f"| {c.get('score',0)} | {c.get('gate_role','')} | [{c['title']}]({c['url']}) | {c.get('organizer','')} | "
                f"{c.get('format','')} | {due(c)} | {c.get('prize','')} | {c.get('state','')} | "
                f"{pipe.get(c['id'],{}).get('stage','')} | {'✓' if c.get('verified') else ''} |")
    head = ["| Điểm | Điều kiện | Cuộc thi | Đơn vị | Thể loại | Hạn | Giải | Trạng thái | Pipeline | Đã kiểm |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    lines = [f"# Bảng cuộc thi & giải thưởng, cập nhật {TODAY.isoformat()}", "",
             f"Tổng {len(db)} mục. Lịch hạn: `lich-han.ics` (nhập vào Google Calendar). Hạn có dấu ~ là ước theo chu kỳ.", ""]
    cats = sorted({c.get("category") or "khác" for c in db})
    for cat in cats:
        rows = [c for c in db if (c.get("category") or "khác") == cat and c.get("state") in LIVE
                and c.get("gate_role") != "Không đủ điều kiện"]
        if rows:
            lines += [f"## {cat}", ""] + head + [row(c) for c in sorted(rows, key=lambda c: -c.get("score", 0))] + [""]
    by_month = {}
    for c in db:
        d = c.get("deadline") or exp_month(c)
        if d and d[:7] >= TODAY.isoformat()[:7] and c.get("gate_role") != "Không đủ điều kiện":
            by_month.setdefault(d[:7], []).append((d, c))
    lines += ["## Lịch hạn theo tháng", ""]
    for m in sorted(by_month):
        lines.append(f"- **{m}**: " + "; ".join(
            f"{d[8:] or '(dự kiến)'} {c['title'][:55]}" for d, c in sorted(by_month[m], key=lambda x: x[0])))
    (OUT / "BANG-CUOC-THI.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Đã ghi {OUT/'BANG-CUOC-THI.md'} và {OUT/'lich-han.ics'}")


def cmd_digest(args):
    state = load_json(DATA / "state.json", {})
    seen = set(state.get("reported", []))
    db = [c for c in load_json(DB, []) if c.get("status") != "bỏ qua"]
    pipe = load_json(PIPE, {})
    ok = lambda c: c.get("gate_role") in ("Nộp được", "Kiểm điều kiện", "Giao đội/CTV") and c.get("score", 0) >= args.min_score

    def line(c):
        return (f"- **{c['title']}** ({c.get('organizer','')}) · hạn {due(c)} · {c.get('format','')} · "
                f"điểm {c.get('score',0)} · {c.get('gate_role','')}{' (' + c['gate_reason'] + ')' if c.get('gate_reason') else ''} · "
                f"[link]({c['url']})" + (f"\n  - {c['fit_note']}" if c.get("fit_note") else ""))

    soon = [c for c in db if c.get("deadline") and 0 <= (dt.date.fromisoformat(c["deadline"]) - TODAY).days <= 60 and ok(c)]
    new = [c for c in db if c["id"] not in seen and ok(c)] if seen else []
    prep = [c for c in db if not c.get("deadline") and exp_month(c) and
            TODAY.isoformat()[:7] <= exp_month(c) <= (TODAY + dt.timedelta(days=120)).isoformat()[:7] and ok(c)]
    out = [f"# Radar cuộc thi: {TODAY.isoformat()}", "",
           f"Hạn trong 60 ngày: **{len(soon)}** · mới từ lần trước: **{len(new)}** · chuẩn bị sớm: **{len(prep)}** · "
           f"đang theo dõi trong pipeline: **{sum(1 for v in pipe.values() if v['stage'] not in ('bỏ','trượt'))}**", ""]
    out += ["## Hạn trong 60 ngày", ""] + ([line(c) for c in sorted(soon, key=lambda c: c["deadline"])] or ["- Không có"]) + [""]
    if seen:
        out += ["## Mới phát hiện", ""] + ([line(c) for c in sorted(new, key=lambda c: -c.get("score", 0))] or ["- Không có"]) + [""]
    out += ["## Chuẩn bị sớm (mùa trước rơi vào 4 tháng tới)", ""] + (
        [line(c) for c in sorted(prep, key=lambda c: exp_month(c))] or ["- Không có"]) + [""]
    out += ["## Bài đã nộp, chờ kết quả", ""] + [cmd_results(args) if not args.no_fetch else "- (bỏ qua dò kết quả)"] + [""]
    out += ["## Pipeline", ""] + ([f"- {v['stage']}: {v['title']}{' · ' + v['note'] if v.get('note') else ''}"
                                   for v in pipe.values()] or ["- Trống. Đánh dấu: `python <plugin>/scripts/contestscan.py mark <id> \"đang viết\"`"]) + [""]
    d = OUT / "digest"
    d.mkdir(parents=True, exist_ok=True)
    f = d / f"DIGEST-{TODAY.isoformat()}.md"
    f.write_text("\n".join(out) + "\n", encoding="utf-8")
    state["last_digest"] = TODAY.isoformat()
    state["reported"] = sorted(seen | {c["id"] for c in db})
    save_json(DATA / "state.json", state)
    print(f"Đã ghi {f}")


def main():
    try:  # console Windows mặc định không phải UTF-8
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("scan")
    sp = sub.add_parser("seed"); sp.add_argument("file")
    sub.add_parser("extract")
    sub.add_parser("score")
    sub.add_parser("report")
    sub.add_parser("results")
    for name in ("digest", "all"):
        p = sub.add_parser(name)
        p.add_argument("--min-score", type=int, default=30)
        p.add_argument("--no-fetch", action="store_true", help="không tải trang kết quả")
    mk = sub.add_parser("mark"); mk.add_argument("id"); mk.add_argument("stage")
    mk.add_argument("--note"); mk.add_argument("--entry", help="tên bài dự thi, dùng để dò kết quả")
    mk.add_argument("--prize", help="giải đạt được, ghi vào sổ giải thưởng")
    a = ap.parse_args()
    if a.cmd == "all":
        cmd_scan(a); cmd_extract(a); cmd_score(a); cmd_report(a); cmd_digest(a)
    else:
        {"scan": cmd_scan, "seed": cmd_seed, "extract": cmd_extract, "score": cmd_score, "report": cmd_report,
         "digest": cmd_digest, "mark": cmd_mark, "results": cmd_results}[a.cmd](a)


if __name__ == "__main__":
    main()
