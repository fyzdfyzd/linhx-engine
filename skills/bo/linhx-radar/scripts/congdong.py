#!/usr/bin/env python3
"""Radar LINHX (LAB035, gộp LAB037), mô-đun cộng đồng: theo dõi hiệp hội, cộng đồng, sự kiện doanh nghiệp ở Việt Nam
(CSMO, VSMCamp, Brands Vietnam...), CSDL doanh nghiệp tài trợ + KOL, khớp pain point với
offer/dịch vụ agentic của LINHX, ra bảng xlsx/csv và bản tin định kỳ.

Chỉ dùng thư viện chuẩn Python 3.9+ (openpyxl nếu có thì xuất thêm .xlsx).
Chạy trong thư mục radar có config/ data/ output/ (đặt biến RADAR_HOME hoặc đứng tại đó):

    python congdong.py init                      # tạo data/radar.db
    python congdong.py seed data/seed-*.json     # nhập cộng đồng, DN, KOL (gộp theo tên)
    python congdong.py scan                      # Google News RSS, YouTube RSS, RSS, theo dõi trang
    python congdong.py match                     # dò tên DN/KOL trong tín hiệu, bắt nhà tài trợ mới
    python congdong.py score                     # điểm cơ hội + gợi ý offer/dịch vụ
    python congdong.py export                    # output/RADAR-LINHX.xlsx + output/csv/
    python congdong.py digest                    # output/digest/DIGEST-<ngày>.md
    python congdong.py mark company "Vinamilk" "đã kết nối" "gặp ở CSMO"   # CRM nhẹ
    python congdong.py all [--no-fetch]          # scan → match → score → export → digest
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import os
import re
import sqlite3
import sys
import unicodedata
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HOME = Path(os.environ.get("RADAR_HOME", Path.cwd())).resolve()
CFG, DATA, OUT = HOME / "config", HOME / "data", HOME / "output"
DB = DATA / "radar.db"
TODAY = dt.date.today()
UA = "Mozilla/5.0 (LINHX-LAB community-radar)"

STAGES = ["chưa tiếp cận", "đang tìm hiểu", "đã kết nối", "đã chia sẻ", "đã gửi offer",
          "đang trao đổi", "đã chốt", "không hợp"]
# Trọng số vai trò khi chấm (khớp không dấu, chứa chuỗi)
ROLE_W = [("kim cuong", 10), ("diamond", 10), ("dong to chuc", 9), ("chien luoc", 9), ("title", 9),
          ("platinum", 8), ("bach kim", 8), ("vang", 7), ("gold", 7), ("bac", 5), ("silver", 5),
          ("dong", 4), ("bronze", 4), ("tai tro", 5), ("sponsor", 5), ("doi tac", 4), ("partner", 4),
          ("truyen thong", 2), ("media", 2), ("trien lam", 3), ("booth", 3)]
KOL_W = {"sang_lap": 9, "chu_tich": 9, "co_van": 8, "giam_khao": 7, "dien_gia": 6, "host": 5}
SPONSOR_CUE = re.compile(r"(nhà tài trợ|tài trợ (kim cương|vàng|bạc|đồng|chính)|đồng hành|"
                         r"đối tác (chiến lược|chính thức)|sponsor(ed)? by|sponsors?|partners?)", re.I)


# ---------------------------------------------------------------- tiện ích
def load_json(p: Path, default):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def fold(s: str) -> str:
    """Bỏ dấu, chữ thường, gọn khoảng trắng: khoá so khớp tên."""
    s = unicodedata.normalize("NFD", (s or "").replace("đ", "d").replace("Đ", "D"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^\w]+", " ", s).strip()


def key_of(name: str) -> str:
    k = fold(name)
    k = re.sub(r"\b(cong ty|cty|tnhh|co phan|cp|jsc|ltd|group|tap doan|viet nam|vietnam|vn)\b", " ", k)
    return re.sub(r"\s+", " ", k).strip() or fold(name)


def fetch(url: str, timeout=25) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "vi,en;q=0.8"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        enc = r.headers.get_content_charset() or "utf-8"
    return raw.decode(enc, errors="replace")


def strip_tags(s: str) -> str:
    s = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", " ", s or "", flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def jl(x) -> str:
    return json.dumps(x or [], ensure_ascii=False)


def jr(s, default=None):
    try:
        return json.loads(s) if s else (default if default is not None else [])
    except ValueError:
        return default if default is not None else []


def con() -> sqlite3.Connection:
    DATA.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


SCHEMA = """
CREATE TABLE IF NOT EXISTS community(
  id TEXT PRIMARY KEY, ten TEXT, loai TEXT, linh_vuc TEXT, mo_ta TEXT, don_vi_dung_sau TEXT,
  quy_mo TEXT, kenh TEXT, su_kien TEXT, chu_de TEXT, pain_point TEXT, ho_da_co TEXT,
  mo_hinh TEXT, nguon TEXT, uu_tien INTEGER DEFAULT 0, cap_nhat TEXT);
CREATE TABLE IF NOT EXISTS company(
  k TEXT PRIMARY KEY, ten TEXT, nganh TEXT, website TEXT, ghi_chu TEXT, nguon TEXT,
  chua_xac_minh INTEGER DEFAULT 0, diem INTEGER DEFAULT 0, goi_y TEXT, giai_doan TEXT DEFAULT 'chưa tiếp cận',
  ghi_chu_crm TEXT, lan_cham TEXT, them_ngay TEXT, nhom TEXT);
CREATE TABLE IF NOT EXISTS kol(
  k TEXT PRIMARY KEY, ten TEXT, chuc_danh TEXT, to_chuc TEXT, chu_de TEXT, linkedin TEXT, facebook TEXT,
  nguon TEXT, chua_xac_minh INTEGER DEFAULT 0, diem INTEGER DEFAULT 0, goi_y TEXT,
  giai_doan TEXT DEFAULT 'chưa tiếp cận', ghi_chu_crm TEXT, lan_cham TEXT, them_ngay TEXT);
CREATE TABLE IF NOT EXISTS link(
  loai TEXT, k TEXT, community TEXT, vai_tro TEXT, nam TEXT, nguon TEXT,
  PRIMARY KEY(loai, k, community, vai_tro));
CREATE TABLE IF NOT EXISTS signal(
  id TEXT PRIMARY KEY, community TEXT, nguon TEXT, kieu TEXT, tieu_de TEXT, url TEXT, tom_tat TEXT,
  ngay_dang TEXT, thay_ngay TEXT, nhac_den TEXT, ung_vien_tai_tro TEXT);
CREATE TABLE IF NOT EXISTS page(
  url TEXT PRIMARY KEY, community TEXT, hash TEXT, text TEXT, kiem_ngay TEXT, doi_ngay TEXT);
CREATE TABLE IF NOT EXISTS log(ngay TEXT, loai TEXT, k TEXT, noi_dung TEXT);
"""


# ---------------------------------------------------------------- init / seed
def cmd_init(args):
    c = con()
    c.executescript(SCHEMA)
    c.commit()
    print(f"OK {DB}")


def upsert_company(c, x, today):
    k = key_of(x["ten"])
    row = c.execute("SELECT * FROM company WHERE k=?", (k,)).fetchone()
    if row:
        nguon = sorted(set(jr(row["nguon"])) | set(x.get("nguon") or []))
        c.execute("UPDATE company SET nganh=coalesce(nullif(?,''),nganh), website=coalesce(nullif(?,''),website),"
                  " ghi_chu=coalesce(nullif(?,''),ghi_chu), nguon=?, chua_xac_minh=min(chua_xac_minh,?) WHERE k=?",
                  (x.get("nganh", ""), x.get("website", ""), x.get("ghi_chu", ""), jl(nguon),
                   int(bool(x.get("chua_xac_minh"))), k))
    else:
        c.execute("INSERT INTO company(k,ten,nganh,website,ghi_chu,nguon,chua_xac_minh,them_ngay) VALUES(?,?,?,?,?,?,?,?)",
                  (k, x["ten"], x.get("nganh", ""), x.get("website", ""), x.get("ghi_chu", ""),
                   jl(x.get("nguon")), int(bool(x.get("chua_xac_minh"))), today))
    return k


def upsert_kol(c, x, today):
    k = key_of(x["ten"])
    row = c.execute("SELECT * FROM kol WHERE k=?", (k,)).fetchone()
    if row:
        nguon = sorted(set(jr(row["nguon"])) | set(x.get("nguon") or []))
        chu_de = "; ".join(t for t in dict.fromkeys([row["chu_de"] or "", x.get("chu_de", "")]) if t)
        c.execute("UPDATE kol SET chuc_danh=coalesce(nullif(?,''),chuc_danh), to_chuc=coalesce(nullif(?,''),to_chuc),"
                  " chu_de=?, linkedin=coalesce(nullif(?,''),linkedin), facebook=coalesce(nullif(?,''),facebook),"
                  " nguon=?, chua_xac_minh=min(chua_xac_minh,?) WHERE k=?",
                  (x.get("chuc_danh", ""), x.get("to_chuc", ""), chu_de[:600], x.get("linkedin", ""),
                   x.get("facebook", ""), jl(nguon), int(bool(x.get("chua_xac_minh"))), k))
    else:
        c.execute("INSERT INTO kol(k,ten,chuc_danh,to_chuc,chu_de,linkedin,facebook,nguon,chua_xac_minh,them_ngay)"
                  " VALUES(?,?,?,?,?,?,?,?,?,?)",
                  (k, x["ten"], x.get("chuc_danh", ""), x.get("to_chuc", ""), x.get("chu_de", ""),
                   x.get("linkedin", ""), x.get("facebook", ""), jl(x.get("nguon")),
                   int(bool(x.get("chua_xac_minh"))), today))
    return k


def add_link(c, loai, k, comms, vai_tro, nam, nguon):
    for cm in comms or ["?"]:
        old = c.execute("SELECT nam FROM link WHERE loai=? AND k=? AND community=? AND vai_tro=?",
                        (loai, k, cm, vai_tro or "")).fetchone()
        years = sorted(set(jr(old["nam"]) if old else []) | set(nam or []))
        c.execute("INSERT OR REPLACE INTO link VALUES(?,?,?,?,?,?)",
                  (loai, k, cm, vai_tro or "", jl(years), jl(nguon)))


def cmd_seed(args):
    c = con()
    c.executescript(SCHEMA)
    today = TODAY.isoformat()
    for f in args.files:
        d = load_json(Path(f), {})
        n = [0, 0, 0]
        for cm in d.get("communities", []):
            old = c.execute("SELECT * FROM community WHERE id=?", (cm["id"],)).fetchone()
            merged = {}
            for fld in ("chu_de_dang_noi", "pain_point", "ho_da_co", "nguon", "su_kien"):
                prev = jr(old[{"chu_de_dang_noi": "chu_de", "su_kien": "su_kien"}.get(fld, fld)]) if old else []
                cur = cm.get(fld) or []
                merged[fld] = prev + [v for v in cur if v not in prev]
            c.execute("INSERT OR REPLACE INTO community VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                      (cm["id"], cm.get("ten", ""), cm.get("loai", ""), cm.get("linh_vuc", ""), cm.get("mo_ta", ""),
                       cm.get("don_vi_dung_sau", ""), cm.get("quy_mo", ""), json.dumps(cm.get("kenh") or {}, ensure_ascii=False),
                       jl(merged["su_kien"]), jl(merged["chu_de_dang_noi"]), jl(merged["pain_point"]),
                       jl(merged["ho_da_co"]), cm.get("mo_hinh_doanh_thu", ""), jl(merged["nguon"]),
                       int(cm.get("uu_tien", old["uu_tien"] if old else 0)), today))
            n[0] += 1
        for x in d.get("companies", []):
            if not x.get("ten"):
                continue
            k = upsert_company(c, x, today)
            add_link(c, "company", k, x.get("cong_dong"), x.get("vai_tro"), x.get("nam"), x.get("nguon"))
            n[1] += 1
        for x in d.get("kols", []):
            if not x.get("ten"):
                continue
            k = upsert_kol(c, x, today)
            add_link(c, "kol", k, x.get("cong_dong"), x.get("vai_tro"), x.get("nam"), x.get("nguon"))
            n[2] += 1
        print(f"{f}: {n[0]} cộng đồng, {n[1]} DN, {n[2]} KOL")
    c.commit()


# ---------------------------------------------------------------- scan
def parse_feed(xml_text: str) -> list[dict]:
    root = ET.fromstring(xml_text.encode("utf-8", errors="replace"))
    ns = {"a": "http://www.w3.org/2005/Atom", "media": "http://search.yahoo.com/mrss/"}
    out = []
    for e in root.findall(".//item") or root.findall(".//a:entry", ns):
        def g(*tags):
            for t in tags:
                el = e.find(t, ns)
                if el is not None and (el.text or "").strip():
                    return el.text
            return ""
        link = g("link")
        if not link:
            le = e.find("a:link", ns)
            link = le.get("href") if le is not None else ""
        out.append({"title": strip_tags(g("title", "a:title")), "url": (link or "").strip(),
                    "summary": strip_tags(g("description", "a:summary", "media:group/media:description"))[:1500],
                    "published": g("pubDate", "a:published", "a:updated").strip()})
    return out


def feed_urls(src: dict, comm: str) -> list[tuple[str, str]]:
    """Trả về [(kieu, url)] cho một nguồn khai báo trong sources.json."""
    k = src["kind"]
    if k == "gnews":
        q = src["query"] if "when:" in src["query"] else src["query"] + " when:" + src.get("when", "14d")
        q = urllib.parse.quote(q)
        return [("tin", f"https://news.google.com/rss/search?q={q}&hl=vi&gl=VN&ceid=VN:vi")]
    if k == "youtube":
        if src.get("channel_id"):
            return [("video", f"https://www.youtube.com/feeds/videos.xml?channel_id={src['channel_id']}")]
        return []
    if k == "rss":
        return [("bai", src["url"])]
    return []


def resolve_youtube(url: str) -> str:
    """Lấy channel_id từ trang kênh @handle (YouTube nhúng 'channelId' trong HTML)."""
    m = re.search(r'"(?:channelId|externalId)":"(UC[\w-]{22})"', fetch(url))
    return m.group(1) if m else ""


def cmd_scan(args):
    if args.no_fetch:
        print("Bỏ qua quét mạng (--no-fetch)")
        return
    c = con()
    c.executescript(SCHEMA)
    conf = load_json(CFG / "sources.json", {"sources": []})
    changed_src = False
    now = TODAY.isoformat()
    new_sig = new_page = 0
    for src in conf["sources"]:
        if not src.get("active", True):
            continue
        comm = src.get("community", "")
        try:
            if src["kind"] == "youtube" and not src.get("channel_id") and src.get("url"):
                src["channel_id"] = resolve_youtube(src["url"])
                changed_src = True
            if src["kind"] == "page":
                text = strip_tags(fetch(src["url"]))[:60000]
                h = hashlib.sha1(text.encode()).hexdigest()
                old = c.execute("SELECT hash,text FROM page WHERE url=?", (src["url"],)).fetchone()
                if not old or old["hash"] != h:
                    prev = old["text"] if old else ""
                    added = " ".join(w for w in text.split(". ") if w not in prev)[:3000]
                    c.execute("INSERT OR REPLACE INTO page VALUES(?,?,?,?,?,?)",
                              (src["url"], comm, h, text, now, now))
                    if old:  # lần đầu chỉ lưu mốc, không báo thay đổi
                        sid = hashlib.sha1((src["url"] + h).encode()).hexdigest()[:12]
                        c.execute("INSERT OR IGNORE INTO signal(id,community,nguon,kieu,tieu_de,url,tom_tat,ngay_dang,thay_ngay)"
                                  " VALUES(?,?,?,?,?,?,?,?,?)",
                                  (sid, comm, src["id"], "trang_doi", f"Trang thay đổi: {src.get('label', src['url'])}",
                                   src["url"], added, now, now))
                        new_page += 1
                else:
                    c.execute("UPDATE page SET kiem_ngay=? WHERE url=?", (now, src["url"]))
                continue
            for kieu, url in feed_urls(src, comm):
                for it in parse_feed(fetch(url))[: src.get("max", 30)]:
                    if not it["url"]:
                        continue
                    t = fold(it["title"] + " " + it["summary"])
                    # Lọc kiểu TrendRadar: can_co (phải có ít nhất một), loai_tru (bỏ nếu có)
                    if src.get("can_co") and not any(fold(w) in t for w in src["can_co"]):
                        continue
                    if any(fold(w) in t for w in src.get("loai_tru", [])):
                        continue
                    # Link Google News là link chuyển hướng: khử trùng theo tiêu đề (bỏ " - Tên báo")
                    base = re.sub(r"\s+-\s+[^-]{2,40}$", "", it["title"]) if kieu == "tin" else it["url"]
                    sid = hashlib.sha1(fold(base).encode()).hexdigest()[:12]
                    cur = c.execute("INSERT OR IGNORE INTO signal(id,community,nguon,kieu,tieu_de,url,tom_tat,ngay_dang,thay_ngay)"
                                    " VALUES(?,?,?,?,?,?,?,?,?)",
                                    (sid, comm, src["id"], kieu, it["title"], it["url"], it["summary"],
                                     it["published"], now))
                    new_sig += cur.rowcount
        except Exception as e:  # nguồn chết không làm dừng cả lượt
            print(f"LỖI {src['id']}: {type(e).__name__} {str(e)[:120]}")
    if changed_src:
        (CFG / "sources.json").write_text(json.dumps(conf, ensure_ascii=False, indent=2), encoding="utf-8")
    c.commit()
    print(f"Quét xong: {new_sig} tín hiệu mới, {new_page} trang thay đổi")


# ---------------------------------------------------------------- match
def cmd_match(args):
    """Dò tên DN/KOL đã biết trong tín hiệu; câu có từ khoá tài trợ thì tách ứng viên tài trợ mới."""
    c = con()
    comps = []
    for r in c.execute("SELECT k,ten,ghi_chu FROM company"):
        comps += [(r["k"], a) for a in aliases(r["ten"], r["ghi_chu"])]
    kols = [(r["k"], r["ten"]) for r in c.execute("SELECT k,ten FROM kol")]
    names = {("company", r["k"]): r["ten"] for r in c.execute("SELECT k,ten FROM company")}
    names.update({("kol", k): t for k, t in kols})
    pats = [(("company", k, t), re.compile(r"\b" + re.escape(fold(t)) + r"\b")) for k, t in comps if len(fold(t)) >= 3]
    pats += [(("kol", k, t), re.compile(r"\b" + re.escape(fold(t)) + r"\b")) for k, t in kols if len(fold(t).split()) >= 2]
    n = 0
    for s in c.execute("SELECT * FROM signal WHERE nhac_den IS NULL").fetchall():
        raw = f"{s['tieu_de']} . {s['tom_tat']}"
        text = fold(raw)
        hits = list({(l, k): {"loai": l, "k": k, "ten": names[(l, k)]}
                     for (l, k, t), rx in pats if rx.search(text)}.values())
        known = {fold(a) for (l, k, a), _ in pats}
        cands = []
        for sent in re.split(r"(?<=[.!?;])\s+", raw):
            if SPONSOR_CUE.search(sent):
                for m in re.finditer(r"\b([A-ZĐ][\w&\.-]+(?:\s+[A-ZĐ0-9][\w&\.-]+){0,3})", sent):
                    ws = m.group(1).strip(" .").split()
                    while ws and fold(ws[0]) in CAP_STOP:
                        ws.pop(0)
                    w = " ".join(ws)
                    if len(fold(w)) > 2 and not all(fold(t) in CAP_STOP for t in ws) \
                            and fold(w) not in {"vietnam", "viet nam"} | known:
                        cands.append(w)
        c.execute("UPDATE signal SET nhac_den=?, ung_vien_tai_tro=? WHERE id=?",
                  (jl(hits), jl(sorted(set(cands))[:20]), s["id"]))
        n += 1
    c.commit()
    print(f"Đã dò {n} tín hiệu")


CAP_STOP = {"nha", "kim", "vang", "bac", "dong", "ban", "chuong", "su", "voi", "cac", "hoi", "le", "tai", "doi",
            "cong", "ty", "ngan", "hang", "tap", "doan", "chinh", "thuc", "va", "cung", "nam", "thang", "ngay",
            "summit", "camp", "the", "and", "of", "by", "with", "official", "strategic", "gold", "silver",
            "diamond", "platinum", "media", "partner", "partners", "sponsor", "sponsors"}


def aliases(ten: str, ghi_chu: str = "") -> list[str]:
    """Tên chính + tên trong ngoặc + tên thương mại (bỏ 'Công ty CP...') + 'alias: a, b' trong ghi chú."""
    out = [ten]
    out += re.findall(r"\(([^)]{2,40})\)", ten)
    short = re.sub(r"(?i)^(công ty|cty|tập đoàn|ngân hàng|tổng công ty)\s+((cổ phần|cp|tnhh|tmcp|jsc)\s+)?", "", ten).strip()
    if short != ten:
        out.append(short)
        last = short.split()[-1] if short.split() else ""
        if len(last) >= 4 and last[0].isupper():
            out.append(last)
    m = re.search(r"alias:\s*([^;\n]+)", ghi_chu or "", re.I)
    if m:
        out += [a.strip() for a in m.group(1).split(",") if a.strip()]
    return list(dict.fromkeys(a for a in out if len(fold(a)) >= 3))


# ---------------------------------------------------------------- score
NHOM_DN = [("Đơn vị tổ chức", r"tổ chức chủ quản|đơn vị thực hiện|^đồng tổ chức|^tổ chức (vmf|accesstrade|tiktok)|chủ quản"),
           ("Truyền thông", r"media|truyền thông|kênh đưa tin|báo"),
           ("Địa điểm, học thuật", r"địa điểm|venue|học thuật|university|đại học"),
           ("Nhà tài trợ", r"tài trợ|sponsor|đồng hành|platinum|kim cương|partner|đối tác"),
           ("Đoạt giải, vinh danh", r"giải|award|winning|finalist|vinh danh|top brand"),
           ("DN có diễn giả", r"diễn giả|speaker"),
           ("Đối tác công nghệ", r"công nghệ|nền tảng|mou|công cụ ai")]
NHOM_PHAT = {"Đơn vị tổ chức": -15, "Truyền thông": -10, "Địa điểm, học thuật": -10}


def nhom_dn(vai_tros: list[str], nganh: str = "") -> str:
    """Nhóm chính của DN: tổ chức > địa điểm > nhà tài trợ > các nhóm khác."""
    found = [n for n, rx in NHOM_DN for v in vai_tros if re.search(rx, v or "", re.I)]
    if re.search(r"hiệp hội|câu lạc bộ", nganh or "", re.I):
        return "Đơn vị tổ chức"
    for n in ("Đơn vị tổ chức", "Địa điểm, học thuật", "Nhà tài trợ"):
        if n in found:
            return n
    return found[0] if found else "Khác"


def offers_for(text: str, offers: list[dict]) -> list[dict]:
    t = fold(text)
    res = []
    for o in offers:
        hit = [kw for kw in o.get("tu_khoa", []) if fold(kw) in t]
        if hit:
            res.append({"id": o["id"], "ten": o["ten"], "khop": hit[:4], "n": sum(len(h) for h in hit)})
    return sorted(res, key=lambda r: -r["n"])


def cmd_score(args):
    c = con()
    offers = load_json(CFG / "offers.json", {"offers": []})["offers"]
    prof = load_json(CFG / "profile.json", {})
    nganh_uu = [fold(x) for x in prof.get("nganh_uu_tien", [])]
    comms = {r["id"]: r for r in c.execute("SELECT * FROM community")}
    year = TODAY.year
    mentions: dict[str, int] = {}
    for s in c.execute("SELECT nhac_den, thay_ngay FROM signal WHERE nhac_den IS NOT NULL"):
        if s["thay_ngay"] and s["thay_ngay"] >= (TODAY - dt.timedelta(days=90)).isoformat():
            for h in jr(s["nhac_den"]):
                mentions[h["loai"] + h["k"]] = mentions.get(h["loai"] + h["k"], 0) + 1
    for loai, table in (("company", "company"), ("kol", "kol")):
        for r in c.execute(f"SELECT * FROM {table}").fetchall():
            links = c.execute("SELECT * FROM link WHERE loai=? AND k=?", (loai, r["k"])).fetchall()
            cm_ids = sorted({l["community"] for l in links})
            years = {int(y) for l in links for y in jr(l["nam"]) if str(y).isdigit()}
            if loai == "company":
                role = max([w for l in links for kw, w in ROLE_W if kw in fold(l["vai_tro"])] or [3])
            else:
                role = max([KOL_W.get(l["vai_tro"], 5) for l in links] or [5])
            diem = role * 3                                   # vai trò: tối đa 30
            diem += min(len(cm_ids), 4) * 6                   # có mặt nhiều cộng đồng: tối đa 24
            diem += 12 if year in years else 8 if year - 1 in years else 0   # còn hoạt động
            diem += min(mentions.get(loai + r["k"], 0), 5) * 2  # được nhắc gần đây: tối đa 10
            diem += sum(comms[i]["uu_tien"] for i in cm_ids if i in comms)   # cộng đồng ưu tiên
            # Ghép pain point của các cộng đồng + ngành/chủ đề của chính đối tượng để gợi ý offer
            ctx = " ".join(" ".join(jr(comms[i]["pain_point"]) + jr(comms[i]["chu_de"])) for i in cm_ids if i in comms)
            own = (r["nganh"] if loai == "company" else f"{r['chuc_danh']} {r['chu_de']}") or ""
            if loai == "company" and any(n in fold(own) for n in nganh_uu):
                diem += 8
            # Ngành/chủ đề của chính đối tượng nặng gấp 3 bối cảnh cộng đồng
            sc = {}
            for w, txt in ((3, own), (1, ctx)):
                for o in offers_for(txt, offers):
                    e = sc.setdefault(o["id"], {**o, "n": 0, "khop": []})
                    e["n"] += w * o["n"]
                    e["khop"] = list(dict.fromkeys(e["khop"] + o["khop"]))[:4]
            sug = sorted(sc.values(), key=lambda o: -o["n"])[:3]
            if loai == "company":
                nh = nhom_dn([l["vai_tro"] for l in links], r["nganh"])
                diem += NHOM_PHAT.get(nh, 0)
            if sug:
                diem += 6
            if r["chua_xac_minh"]:
                diem -= 5
            c.execute(f"UPDATE {table} SET diem=?, goi_y=?, lan_cham=? WHERE k=?",
                      (max(diem, 0), jl(sug), TODAY.isoformat(), r["k"]))
            if loai == "company":
                c.execute("UPDATE company SET nhom=? WHERE k=?", (nh, r["k"]))
    c.commit()
    print("Đã chấm điểm DN và KOL")


# ---------------------------------------------------------------- mark (CRM nhẹ)
def cmd_mark(args):
    c = con()
    table = {"company": "company", "dn": "company", "kol": "kol"}[args.loai]
    k = key_of(args.ten)
    if args.giai_doan not in STAGES:
        sys.exit(f"Giai đoạn phải là một trong: {', '.join(STAGES)}")
    row = c.execute(f"SELECT k, ghi_chu_crm FROM {table} WHERE k=?", (k,)).fetchone()
    if not row:  # cho gõ tên ngắn: "Vinamilk" khớp "Công ty CP Sữa Việt Nam Vinamilk"
        cands = c.execute(f"SELECT k, ten, ghi_chu_crm FROM {table} WHERE k LIKE ?", (f"%{k}%",)).fetchall()
        if len(cands) != 1:
            sys.exit(f"Không thấy đúng một '{args.ten}' trong {table}: " + ", ".join(r["ten"] for r in cands[:10]))
        row = cands[0]
    k = row["k"]
    note = f"{TODAY.isoformat()} {args.giai_doan}: {args.ghi_chu}".strip()
    c.execute(f"UPDATE {table} SET giai_doan=?, ghi_chu_crm=? WHERE k=?",
              (args.giai_doan, ((row["ghi_chu_crm"] or "") + "\n" + note).strip(), k))
    c.execute("INSERT INTO log VALUES(?,?,?,?)", (TODAY.isoformat(), table, k, note))
    c.commit()
    print(f"OK {args.ten} → {args.giai_doan}")


# ---------------------------------------------------------------- export
def rows_export(c):
    comms = {r["id"]: r["ten"] for r in c.execute("SELECT id,ten FROM community")}

    def links_of(loai, k):
        ls = c.execute("SELECT * FROM link WHERE loai=? AND k=?", (loai, k)).fetchall()
        return "; ".join(f"{comms.get(l['community'], l['community'])} ({l['vai_tro'] or '?'} {','.join(map(str, jr(l['nam'])))})".strip()
                         for l in ls)

    def sug(s):
        return "; ".join(f"{g['id']} {g['ten']}" for g in jr(s))

    t = {}
    t["Cộng đồng"] = [["ID", "Tên", "Loại", "Lĩnh vực", "Đứng sau", "Quy mô", "Mô tả", "Kênh", "Sự kiện",
                       "Họ nói về gì", "Pain point cộng đồng", "Họ đã có gì", "Mô hình doanh thu", "Ưu tiên", "Nguồn"]]
    for r in c.execute("SELECT * FROM community WHERE coalesce(loai,'') NOT IN ('sự kiện','giải thưởng') ORDER BY uu_tien DESC, ten"):
        kenh = json.loads(r["kenh"] or "{}")
        kenh_s = "\n".join(f"{k}: {v if isinstance(v, str) else ', '.join(v)}" for k, v in kenh.items() if v)
        sk = "\n".join(f"{e.get('ten', '')} {e.get('nam', '')} {e.get('thoi_gian', '')} {e.get('dia_diem', '')}".strip()
                       for e in jr(r["su_kien"]))
        t["Cộng đồng"].append([r["id"], r["ten"], r["loai"], r["linh_vuc"], r["don_vi_dung_sau"], r["quy_mo"], r["mo_ta"],
                               kenh_s, sk, "\n".join(jr(r["chu_de"])), "\n".join(jr(r["pain_point"])),
                               "\n".join(jr(r["ho_da_co"])), r["mo_hinh"], r["uu_tien"], "\n".join(jr(r["nguon"])[:5])])
    t["Doanh nghiệp"] = [["Tên", "Nhóm", "Ngành", "Website", "Cộng đồng (vai trò, năm)", "Số cộng đồng", "Điểm cơ hội",
                          "Gợi ý offer/dịch vụ", "Giai đoạn", "Ghi chú CRM", "Ghi chú", "Chưa xác minh", "Nguồn"]]
    for r in c.execute("SELECT * FROM company ORDER BY diem DESC, ten"):
        n = c.execute("SELECT count(DISTINCT community) FROM link WHERE loai='company' AND k=?", (r["k"],)).fetchone()[0]
        t["Doanh nghiệp"].append([r["ten"], r["nhom"] or "", r["nganh"], r["website"], links_of("company", r["k"]), n, r["diem"],
                                  sug(r["goi_y"]), r["giai_doan"], r["ghi_chu_crm"] or "", r["ghi_chu"],
                                  "x" if r["chua_xac_minh"] else "", "\n".join(jr(r["nguon"])[:3])])
    t["KOL"] = [["Tên", "Chức danh", "Tổ chức", "Cộng đồng (vai trò, năm)", "Chủ đề", "LinkedIn", "Facebook",
                 "Điểm", "Gợi ý offer/dịch vụ", "Giai đoạn", "Ghi chú CRM", "Chưa xác minh", "Nguồn"]]
    for r in c.execute("SELECT * FROM kol ORDER BY diem DESC, ten"):
        t["KOL"].append([r["ten"], r["chuc_danh"], r["to_chuc"], links_of("kol", r["k"]), r["chu_de"], r["linkedin"],
                         r["facebook"], r["diem"], sug(r["goi_y"]), r["giai_doan"], r["ghi_chu_crm"] or "",
                         "x" if r["chua_xac_minh"] else "", "\n".join(jr(r["nguon"])[:3])])
    offers = load_json(CFG / "offers.json", {"offers": []})["offers"]
    by_id = {o["id"]: o for o in offers}
    t["Pain → Offer"] = [["Cộng đồng", "Pain point cộng đồng", "LINHX chia sẻ / offer", "Dịch vụ agentic có thể bán",
                          "Từ khoá khớp"]]
    for r in c.execute("SELECT * FROM community WHERE coalesce(loai,'') NOT IN ('sự kiện','giải thưởng') ORDER BY uu_tien DESC, ten"):
        for p in jr(r["pain_point"]):
            m = offers_for(p, offers)[:2]
            t["Pain → Offer"].append([r["ten"], p,
                                      "\n".join(f"{x['id']} {x['ten']}: {by_id[x['id']].get('chia_se', '')}" for x in m),
                                      "\n".join(f"{x['id']} {by_id[x['id']].get('dich_vu_agentic', '')}" for x in m),
                                      ", ".join(k for x in m for k in x["khop"])])
    t["Offer & dịch vụ"] = [["ID", "Offer", "Lời hứa", "Chia sẻ miễn phí cho cộng đồng", "Dịch vụ agentic (trả phí)",
                             "Đầu ra", "Năng lực đã có (lab)", "Hợp với", "Giá"]]
    for o in offers:
        t["Offer & dịch vụ"].append([o["id"], o["ten"], o.get("loi_hua", ""), o.get("chia_se", ""),
                                     o.get("dich_vu_agentic", ""), o.get("dau_ra", ""), o.get("bang_chung", ""),
                                     o.get("hop_voi", ""), o.get("gia", "[Linh chốt]")])
    # Sự kiện và giải thưởng (bảng của eventscan.py trong cùng radar.db)
    if has_table(c, "event"):
        t["Sự kiện"] = [["Ngày", "Đến ngày", "Tên", "Thành phố", "Hình thức", "Tổ chức", "Lĩnh vực", "Chủ đề", "Giá vé",
                         "Nhãn", "Điểm", "Lý do", "Giai đoạn", "Nhà tài trợ, đối tác", "Diễn giả", "Chưa xác minh", "URL"]]
        for e in c.execute("SELECT * FROM event WHERE coalesce(ngay_bd,'')>=? OR coalesce(lap_lai,'')!='' "
                           "ORDER BY coalesce(ngay_bd,'9999'), diem DESC", ((TODAY - dt.timedelta(days=30)).isoformat(),)):
            tt = c.execute("SELECT o.ten FROM role r JOIN org o ON o.k=r.k WHERE r.event_id=? AND r.loai='org' "
                           "AND r.vai_tro!='tổ chức'", (e["id"],)).fetchall()
            dg = c.execute("SELECT p.ten FROM role r JOIN person p ON p.k=r.k WHERE r.event_id=? AND r.loai='person'",
                           (e["id"],)).fetchall()
            t["Sự kiện"].append([e["ngay_bd"], e["ngay_kt"], e["ten"], e["thanh_pho"], e["hinh_thuc"], e["to_chuc"],
                                 ", ".join(jr(e["linh_vuc"])), "; ".join(jr(e["chu_de"])[:4]), e["gia_ve"], e["nhan"],
                                 e["diem"], e["ly_do"], e["giai_doan"], ", ".join(x[0] for x in tt[:12]),
                                 ", ".join(x[0] for x in dg[:12]), "x" if e["chua_xac_minh"] else "", e["url"]])
    if has_table(c, "award"):
        t["Giải thưởng"] = [["Tên", "Tổ chức", "Đối tượng", "Lĩnh vực", "Hạn nộp", "Lễ trao", "Uy tín", "Trả phí để nhận",
                             "Nhãn", "Điểm", "Lý do", "Ai nộp", "Giai đoạn", "Người/DN đoạt giải gần đây", "Chưa xác minh", "URL"]]
        for a in c.execute("SELECT * FROM award ORDER BY diem DESC, ten"):
            ws = c.execute("SELECT coalesce(o.ten, p.ten) FROM role r LEFT JOIN org o ON r.loai='org' AND o.k=r.k "
                           "LEFT JOIN person p ON r.loai='person' AND p.k=r.k WHERE r.event_id=?", ("award:" + a["id"],)).fetchall()
            t["Giải thưởng"].append([a["ten"], a["to_chuc"], a["doi_tuong"], ", ".join(jr(a["linh_vuc"])), a["han_nop"],
                                     a["le_trao"], a["uy_tin"], "có" if a["tra_phi_de_nhan"] else "", a["nhan"], a["diem"],
                                     a["ly_do"], a["ai_nop"], a["giai_doan"], ", ".join(x[0] for x in ws[:10] if x[0]),
                                     "x" if a["chua_xac_minh"] else "", a["url"]])
    t["Tín hiệu"] = [["Ngày thấy", "Cộng đồng", "Kiểu", "Tiêu đề", "Nhắc đến", "Ứng viên tài trợ", "URL"]]
    for r in c.execute("SELECT * FROM signal ORDER BY thay_ngay DESC, ngay_dang DESC LIMIT 2000"):
        t["Tín hiệu"].append([r["thay_ngay"], comms.get(r["community"], r["community"]), r["kieu"], r["tieu_de"],
                              ", ".join(h["ten"] for h in jr(r["nhac_den"])), ", ".join(jr(r["ung_vien_tai_tro"])), r["url"]])
    return t


def has_table(c, name: str) -> bool:
    return bool(c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone())


def cmd_export(args):
    c = con()
    t = rows_export(c)
    (OUT / "csv").mkdir(parents=True, exist_ok=True)
    import csv
    names = {"Cộng đồng": "cong-dong", "Doanh nghiệp": "doanh-nghiep", "KOL": "kol", "Tín hiệu": "tin-hieu",
             "Pain → Offer": "pain-offer", "Offer & dịch vụ": "offer-dich-vu", "Sự kiện": "su-kien",
             "Giải thưởng": "giai-thuong"}
    for sheet, rows in t.items():
        with open(OUT / "csv" / f"{names[sheet]}.csv", "w", encoding="utf-8-sig", newline="") as f:
            csv.writer(f).writerows(rows)
    try:
        from xlsx_style import write_xlsx  # cùng thư mục script
    except ImportError:
        sys.path.insert(0, str(Path(__file__).parent))
        try:
            from xlsx_style import write_xlsx
        except ImportError:
            write_xlsx = None
    if write_xlsx:
        try:
            p = write_xlsx(t, OUT / "RADAR-LINHX.xlsx", CFG)
            print(f"OK {p}")
        except ImportError:
            print("Chưa có openpyxl (pip install openpyxl); đã xuất csv")
    print(f"OK {OUT / 'csv'}")


# ---------------------------------------------------------------- digest
def cmd_digest(args):
    c = con()
    since = (TODAY - dt.timedelta(days=args.days)).isoformat()
    comms = {r["id"]: r for r in c.execute("SELECT * FROM community")}
    n_cd = c.execute("SELECT count(*) FROM community WHERE coalesce(loai,'') NOT IN ('sự kiện','giải thưởng')").fetchone()[0]
    L = [f"# Radar cộng đồng · {TODAY.isoformat()}", "",
         f"Kho: {n_cd} cộng đồng, {c.execute('SELECT count(*) FROM company').fetchone()[0]} doanh nghiệp, "
         f"{c.execute('SELECT count(*) FROM kol').fetchone()[0]} KOL. Tín hiệu từ {since}.", ""]
    sig = c.execute("SELECT * FROM signal WHERE thay_ngay>=? ORDER BY community, ngay_dang DESC", (since,)).fetchall()
    L += ["## Tín hiệu mới", ""]
    if not sig:
        L.append("Không có tín hiệu mới (hoặc lượt quét chưa chạy trên máy).")
    cur = None
    for s in sig[:80]:
        if s["community"] != cur:
            cur = s["community"]
            L += ["", f"**{comms[cur]['ten'] if cur in comms else cur}**"]
        extra = ", ".join(h["ten"] for h in jr(s["nhac_den"]))
        cand = ", ".join(jr(s["ung_vien_tai_tro"])[:6])
        L.append(f"- [{s['tieu_de'][:140]}]({s['url']})" + (f" · nhắc: {extra}" if extra else "")
                 + (f" · ứng viên tài trợ: {cand}" if cand else ""))
    new_c = c.execute("SELECT ten FROM company WHERE them_ngay>=?", (since,)).fetchall()
    new_k = c.execute("SELECT ten FROM kol WHERE them_ngay>=?", (since,)).fetchall()
    L += ["", "## Mới vào kho", "",
          f"- Doanh nghiệp ({len(new_c)}): " + ", ".join(r[0] for r in new_c[:40]),
          f"- KOL ({len(new_k)}): " + ", ".join(r[0] for r in new_k[:40]), ""]
    L += ["## 10 doanh nghiệp đáng tiếp cận", "", "| DN | Nhóm | Ngành | Điểm | Gợi ý |", "|---|---|---|---|---|"]
    for r in c.execute("SELECT * FROM company WHERE giai_doan!='không hợp' AND coalesce(nhom,'') NOT IN"
                       " ('Đơn vị tổ chức','Truyền thông','Địa điểm, học thuật') ORDER BY diem DESC LIMIT 10"):
        g = "; ".join(x["ten"] for x in jr(r["goi_y"])[:2])
        L.append(f"| {r['ten']} | {r['nhom'] or ''} | {r['nganh'] or ''} | {r['diem']} | {g} |")
    L += ["", "## 10 KOL đáng kết nối", "", "| KOL | Chức danh | Điểm | Giai đoạn | Gợi ý |", "|---|---|---|---|---|"]
    for r in c.execute("SELECT * FROM kol WHERE giai_doan!='không hợp' ORDER BY diem DESC LIMIT 10"):
        g = "; ".join(x["ten"] for x in jr(r["goi_y"])[:2])
        L.append(f"| {r['ten']} | {(r['chuc_danh'] or '')[:40]} {('· ' + r['to_chuc']) if r['to_chuc'] else ''} | {r['diem']} | {r['giai_doan']} | {g} |")
    up = []
    for cm in comms.values():
        for e in jr(cm["su_kien"]):
            if isinstance(e, dict) and str(e.get("nam", "")) in (str(TODAY.year), str(TODAY.year + 1)):
                up.append(f"- {cm['ten']}: {e.get('ten', '')} {e.get('thoi_gian', '')} {e.get('dia_diem', '')}".rstrip())
    L += ["", "## Sự kiện của các cộng đồng năm nay và năm tới", ""] + (up or ["- chưa có"])
    d = OUT / "digest"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"DIGEST-{TODAY.isoformat()}.md"
    p.write_text("\n".join(L) + "\n", encoding="utf-8")
    (d / "MOI-NHAT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"OK {p}")


def cmd_all(args):
    cmd_init(args)
    cmd_scan(args)
    cmd_match(args)
    cmd_score(args)
    cmd_export(args)
    cmd_digest(args)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    sp = sub.add_parser("seed"); sp.add_argument("files", nargs="+")
    sc = sub.add_parser("scan"); sc.add_argument("--no-fetch", action="store_true")
    sub.add_parser("match"); sub.add_parser("score"); sub.add_parser("export")
    dg = sub.add_parser("digest"); dg.add_argument("--days", type=int, default=7)
    mk = sub.add_parser("mark"); mk.add_argument("loai", choices=["company", "dn", "kol"])
    mk.add_argument("ten"); mk.add_argument("giai_doan"); mk.add_argument("ghi_chu", nargs="?", default="")
    al = sub.add_parser("all"); al.add_argument("--no-fetch", action="store_true"); al.add_argument("--days", type=int, default=7)
    a = ap.parse_args()
    {"init": cmd_init, "seed": cmd_seed, "scan": cmd_scan, "match": cmd_match, "score": cmd_score,
     "export": cmd_export, "digest": cmd_digest, "mark": cmd_mark, "all": cmd_all}[a.cmd](a)


if __name__ == "__main__":
    main()
