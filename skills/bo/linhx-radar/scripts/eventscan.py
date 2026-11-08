#!/usr/bin/env python3
"""LAB037 Event radar Việt Nam: index sự kiện business + tech (offline, online), giải thưởng DN và cá nhân, diễn giả,
nhà tài trợ, chủ đề, pain point, solution; chấm "nên đi không" và gom bản đồ chủ đề.

Chỉ dùng thư viện chuẩn Python 3.9+. Chạy trong thư mục radar có config/ data/ output/
(đặt biến RADAR_HOME hoặc đứng tại đó). CSDL: data/su-kien.db (SQLite).

    python eventscan.py init                       # tạo CSDL
    python eventscan.py seed data/seed-events.json # nhập sự kiện (gộp theo id, khớp mờ theo tên + tháng)
    python eventscan.py scan                       # RSS, Google News RSS, iCal (Luma/Meetup), trang HTML
    python eventscan.py extract                    # tin quét được → ứng viên sự kiện (ngày, thành phố, hình thức)
    python eventscan.py absorb data/hap-thu/x.json # nạp talk, insight, chấm diễn giả do Claude trích
    python eventscan.py score                      # điểm "nên đi" + nhãn Đi / Cân nhắc / Xem bản ghi / Bỏ
    python eventscan.py insight                    # output/BAN-DO-CHU-DE.md: đang nói gì, ai hay, pain, solution mới
    python eventscan.py report                     # output/LICH-SU-KIEN.md + .csv + lich-su-kien.ics
    python eventscan.py digest                     # output/digest/DIGEST-<ngày>.md
    python eventscan.py mark <event_id> <giai đoạn> [ghi chú]   # quan tâm | đăng ký | đã đi | xem bản ghi | bỏ
    python eventscan.py gan-nhom data/hap-thu/gan-nhom.json      # Claude gom nhóm lại các ý (insight_id → [loại, nhóm])
    python eventscan.py rate "<tên diễn giả>" <1-5> [lý do]       # chấm diễn giả sau khi nghe
    python eventscan.py phude <youtube_url> [event_id]           # tải phụ đề bằng yt-dlp nếu máy có
    python eventscan.py export-lab035              # data/xuat-lab035.json: diễn giả=KOL, tài trợ, người đoạt giải=DN
    python eventscan.py import-lab022 <seed-contests.json>      # nhập kho cuộc thi/giải cá nhân của LAB022
    (seed nhận cả khoá "awards": giải thưởng cho DN và cá nhân, kèm người đoạt giải; lễ trao giải thành sự kiện)
    python eventscan.py all [--no-fetch]           # scan → extract → score → insight → report → digest

Khoá tên người/doanh nghiệp dùng đúng hàm key_of() của LAB035 (congdong.py) để hai radar ghép được.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import html
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

HOME = Path(os.environ.get("RADAR_HOME", Path.cwd())).resolve()
CFG, DATA, OUT = HOME / "config", HOME / "data", HOME / "output"
DB = DATA / "su-kien.db"  # đổi bằng profile.json → "db" (vd. trỏ vào radar.db của LAB035 để dùng chung một file)
TODAY = dt.date.today()
UA = "Mozilla/5.0 (LINHX-LAB event-radar)"

STAGES = ["mới", "quan tâm", "đăng ký", "đã đi", "xem bản ghi", "đã hấp thu", "bỏ"]
INSIGHT_KINDS = ["chu_de", "pain_point", "solution", "xu_huong", "so_lieu", "cau_noi", "cong_cu"]
EVENT_CUE = re.compile(r"(hội thảo|hội nghị|diễn đàn|tọa đàm|toạ đàm|workshop|webinar|summit|conference|"
                       r"meetup|hackathon|triển lãm|expo|festival|talkshow|sự kiện|forum|demo day|"
                       r"bootcamp|masterclass|ra mắt|lễ trao giải|networking)", re.I)
CITY = [("Hà Nội", r"hà nội|ha noi|hanoi"), ("TP.HCM", r"tp\.? ?hcm|hồ chí minh|ho chi minh|sài gòn|saigon|hcmc"),
        ("Đà Nẵng", r"đà nẵng|da nang|danang"), ("Hải Phòng", r"hải phòng|hai phong"),
        ("Cần Thơ", r"cần thơ|can tho"), ("Nha Trang", r"nha trang"), ("Huế", r"\bhuế\b|\bhue\b")]
ONLINE = re.compile(r"online|trực tuyến|webinar|livestream|zoom|google meet|ms teams|youtube live", re.I)
MONTHS_EN = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug",
                                         "sep", "oct", "nov", "dec"], 1)}


# ---------------------------------------------------------------- tiện ích
def load_json(p: Path, default):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def fold(s: str) -> str:
    """Bỏ dấu, chữ thường, gọn khoảng trắng (giống LAB035)."""
    s = unicodedata.normalize("NFD", (s or "").replace("đ", "d").replace("Đ", "D"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^\w]+", " ", s).strip()


def key_of(name: str) -> str:
    """Khoá người/DN, trùng thuật toán với congdong.py (LAB035)."""
    k = fold(name)
    k = re.sub(r"\b(cong ty|cty|tnhh|co phan|cp|jsc|ltd|group|tap doan|viet nam|vietnam|vn)\b", " ", k)
    return re.sub(r"\s+", " ", k).strip() or fold(name)


def has(blob_folded: str, kw: str) -> bool:
    """Khớp nguyên từ trên chuỗi đã fold ("ai" không khớp "giai")."""
    k = fold(kw)
    return bool(k) and re.search(r"(?<!\w)" + re.escape(k) + r"(?!\w)", blob_folded) is not None


def slug(s: str, n=60) -> str:
    return re.sub(r"\s+", "-", fold(s))[:n].strip("-")


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
    return json.dumps(x if x is not None else [], ensure_ascii=False)


def jr(s, default=None):
    try:
        return json.loads(s) if s else (default if default is not None else [])
    except ValueError:
        return default if default is not None else []


def words(t: str) -> set:
    return set(w for w in re.sub(r"20\d\d|[^\w\s]", " ", fold(t)).split() if len(w) > 1)


def similar(a: str, b: str, th=0.6) -> bool:
    wa, wb = words(a), words(b)
    return bool(wa and wb) and len(wa & wb) / len(wa | wb) >= th


def con() -> sqlite3.Connection:
    DATA.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(db_path())
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    return c


SCHEMA = """
CREATE TABLE IF NOT EXISTS event(
  id TEXT PRIMARY KEY, ten TEXT, ngay_bd TEXT, ngay_kt TEXT, thanh_pho TEXT, dia_diem TEXT,
  hinh_thuc TEXT, linh_vuc TEXT, to_chuc TEXT, url TEXT, gia_ve TEXT, quy_mo TEXT, chu_de TEXT,
  mo_ta TEXT, nguon TEXT, chua_xac_minh INTEGER DEFAULT 1, lap_lai TEXT, giai_doan TEXT DEFAULT 'mới',
  ghi_chu TEXT, diem INTEGER DEFAULT 0, nhan TEXT, ly_do TEXT, first_seen TEXT, last_seen TEXT);
CREATE TABLE IF NOT EXISTS person(
  k TEXT PRIMARY KEY, ten TEXT, chuc_danh TEXT, to_chuc TEXT, chu_de TEXT, linkedin TEXT,
  diem_hay REAL, so_lan_cham INTEGER DEFAULT 0, ghi_chu TEXT, theo_doi INTEGER DEFAULT 0, them_ngay TEXT);
CREATE TABLE IF NOT EXISTS org(
  k TEXT PRIMARY KEY, ten TEXT, loai TEXT, website TEXT, them_ngay TEXT);
CREATE TABLE IF NOT EXISTS role(
  event_id TEXT, loai TEXT, k TEXT, vai_tro TEXT, PRIMARY KEY(event_id, loai, k, vai_tro));
CREATE TABLE IF NOT EXISTS talk(
  id TEXT PRIMARY KEY, event_id TEXT, tieu_de TEXT, dien_gia TEXT, chu_de TEXT, tom_tat TEXT,
  url_video TEXT, nguon TEXT, them_ngay TEXT);
CREATE TABLE IF NOT EXISTS insight(
  id TEXT PRIMARY KEY, event_id TEXT, talk_id TEXT, loai TEXT, noi_dung TEXT, nhom TEXT,
  ai_noi TEXT, nguon TEXT, ngay TEXT, them_ngay TEXT);
CREATE TABLE IF NOT EXISTS item(
  id TEXT PRIMARY KEY, source TEXT, title TEXT, url TEXT, summary TEXT, published TEXT,
  first_seen TEXT, last_seen TEXT, status TEXT DEFAULT 'new', event_id TEXT);
CREATE TABLE IF NOT EXISTS award(
  id TEXT PRIMARY KEY, ten TEXT, to_chuc TEXT, doi_tuong TEXT, linh_vuc TEXT, hang_muc TEXT,
  han_nop TEXT, mua_nop TEXT, le_trao TEXT, dia_diem_le_trao TEXT, phi_tham_du TEXT, uy_tin INTEGER,
  ly_do_uy_tin TEXT, tra_phi_de_nhan INTEGER, url TEXT, chu_ky TEXT, nguon TEXT, chua_xac_minh INTEGER DEFAULT 1,
  giai_doan TEXT DEFAULT 'mới', ghi_chu TEXT, diem INTEGER DEFAULT 0, nhan TEXT, ly_do TEXT, ai_nop TEXT,
  first_seen TEXT, last_seen TEXT);
CREATE TABLE IF NOT EXISTS log(ngay TEXT, loai TEXT, k TEXT, noi_dung TEXT);
"""


def profile() -> dict:
    return load_json(CFG / "profile.json", {})


def rel(p: str) -> Path:
    """Đường dẫn trong profile.json: tương đối thì tính từ thư mục radar (RADAR_HOME); nhận cả dấu \\ của Windows."""
    q = Path(str(p).replace("\\", "/"))
    return q if q.is_absolute() or re.match(r"^[A-Za-z]:", str(p)) else (HOME / q).resolve()


def db_path() -> Path:
    """CSDL dùng chung: profile.db (bản gộp trỏ vào ../data/radar.db cùng radar cộng đồng)."""
    p = os.environ.get("RADAR_DB") or profile().get("db")
    if not p:
        return DB
    return Path(p) if re.match(r"^[A-Za-z]:", str(p)) else rel(p)


# ---------------------------------------------------------------- ngày tháng
DATE_PATTERNS = [
    (re.compile(r"\b(\d{1,2})\s*[-–]\s*(\d{1,2})[/.](\d{1,2})[/.](20\d\d)\b"),
     lambda m: ((int(m[4]), int(m[3]), int(m[1])), (int(m[4]), int(m[3]), int(m[2])))),
    (re.compile(r"\b(\d{1,2})[/.](\d{1,2})[/.](20\d\d)\b"),
     lambda m: ((int(m[3]), int(m[2]), int(m[1])), None)),
    (re.compile(r"ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})(?:\s+năm\s+(20\d\d))?", re.I),
     lambda m: ((int(m[3] or 0), int(m[2]), int(m[1])), None)),
    (re.compile(r"\b(\d{1,2})[/.](\d{1,2})\b(?![/.]\d)"),
     lambda m: ((0, int(m[2]), int(m[1])), None)),
    (re.compile(r"\b(\d{1,2})\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?,?\s*(20\d\d)?", re.I),
     lambda m: ((int(m[3] or 0), MONTHS_EN[m[2].lower()[:3]], int(m[1])), None)),
]


def _mk(t, ref: dt.date):
    y, mo, d = t
    if not y:  # thiếu năm: lấy lần xuất hiện tới gần nhất (sự kiện thường được loan báo trước)
        y = ref.year
        try:
            if dt.date(y, mo, d) < ref - dt.timedelta(days=45):
                y += 1
        except ValueError:
            return None
    try:
        return dt.date(y, mo, d)
    except ValueError:
        return None


def find_dates(text: str, ref: dt.date):
    out, used = [], []
    for rx, conv in DATE_PATTERNS:
        for m in rx.finditer(text):
            if any(a <= m.start() < b for a, b in used):
                continue
            a, b = conv(m)
            da = _mk(a, ref)
            if da:
                out.append((da, _mk(b, ref) if b else None))
                used.append((m.start(), m.end()))
    return out


# ---------------------------------------------------------------- init / seed
def upsert_person(c, x: dict, today: str) -> str:
    k = key_of(x["ten"])
    row = c.execute("SELECT * FROM person WHERE k=?", (k,)).fetchone()
    cd = x.get("chu_de") or []
    cd = cd if isinstance(cd, list) else [cd]
    if row:
        merged = list(dict.fromkeys(jr(row["chu_de"]) + cd))
        c.execute("UPDATE person SET chuc_danh=coalesce(nullif(?,''),chuc_danh), to_chuc=coalesce(nullif(?,''),to_chuc),"
                  " chu_de=?, linkedin=coalesce(nullif(?,''),linkedin) WHERE k=?",
                  (x.get("chuc_danh", ""), x.get("to_chuc", ""), jl(merged[:20]), x.get("linkedin", ""), k))
    else:
        c.execute("INSERT INTO person(k,ten,chuc_danh,to_chuc,chu_de,linkedin,them_ngay) VALUES(?,?,?,?,?,?,?)",
                  (k, x["ten"], x.get("chuc_danh", ""), x.get("to_chuc", ""), jl(cd), x.get("linkedin", ""), today))
    return k


def upsert_org(c, ten: str, loai: str, today: str, website="") -> str:
    k = key_of(ten)
    if not c.execute("SELECT 1 FROM org WHERE k=?", (k,)).fetchone():
        c.execute("INSERT INTO org VALUES(?,?,?,?,?)", (k, ten, loai, website, today))
    return k


def canon_url(u: str) -> str:
    """Chuẩn hoá để gộp trùng: luma.com ↔ lu.ma, bỏ www, query theo dõi, dấu / cuối."""
    u = (u or "").strip()
    u = re.sub(r"^https?://(www\.)?", "https://", u)
    u = re.sub(r"^https://luma\.com/", "https://lu.ma/", u)
    u = re.sub(r"[?#].*$", "", u) if re.search(r"[?&](utm_|fbclid|ref=)", u) else u
    return u.rstrip("/")


def find_event(c, e: dict):
    """Khớp sự kiện đã có: cùng id, hoặc tên giống + cùng tháng (kỳ lặp lại năm khác thì không gộp)."""
    if e.get("id"):
        row = c.execute("SELECT * FROM event WHERE id=?", (e["id"],)).fetchone()
        if row:
            return row
    if e.get("url"):
        row = c.execute("SELECT * FROM event WHERE url=?", (canon_url(e["url"]),)).fetchone()
        if row:
            return row
    mon = (e.get("ngay_bd") or "")[:7]
    for row in c.execute("SELECT * FROM event WHERE substr(ngay_bd,1,7)=?", (mon,)):
        if mon and similar(row["ten"], e.get("ten", "")):
            return row
    return None


ALIAS = {"ngay_bat_dau": "ngay_bd", "ngay_ket_thuc": "ngay_kt", "ghi_chu": "mo_ta"}


def upsert_event(c, e: dict, today: str) -> str:
    e = {ALIAS.get(k, k) if ALIAS.get(k, k) not in e else k: v for k, v in e.items()}
    if e.get("url"):
        e["url"] = canon_url(e["url"])
    row = find_event(c, e)
    eid = row["id"] if row else (e.get("id") or slug(f"{e.get('ten','')} {(e.get('ngay_bd') or '')[:7]}"))
    lst = lambda v: v if isinstance(v, list) else ([v] if v else [])
    if row:
        def merge(f):
            return jl(list(dict.fromkeys(jr(row[f]) + lst(e.get(f)))))
        verified = 0 if (row["chua_xac_minh"] == 0 or e.get("chua_xac_minh") is False) else 1
        c.execute("UPDATE event SET ten=coalesce(nullif(?,''),ten), ngay_bd=coalesce(nullif(?,''),ngay_bd),"
                  " ngay_kt=coalesce(nullif(?,''),ngay_kt), thanh_pho=coalesce(nullif(?,''),thanh_pho),"
                  " dia_diem=coalesce(nullif(?,''),dia_diem), hinh_thuc=coalesce(nullif(?,''),hinh_thuc),"
                  " to_chuc=coalesce(nullif(?,''),to_chuc), url=coalesce(nullif(?,''),url),"
                  " gia_ve=coalesce(nullif(?,''),gia_ve), quy_mo=coalesce(nullif(?,''),quy_mo),"
                  " mo_ta=coalesce(nullif(?,''),mo_ta), lap_lai=coalesce(nullif(?,''),lap_lai),"
                  " linh_vuc=?, chu_de=?, nguon=?, chua_xac_minh=?, last_seen=? WHERE id=?",
                  (e.get("ten", ""), e.get("ngay_bd", ""), e.get("ngay_kt", ""), e.get("thanh_pho", ""),
                   e.get("dia_diem", ""), e.get("hinh_thuc", ""), e.get("to_chuc", ""), e.get("url", ""),
                   str(e.get("gia_ve") or ""), str(e.get("quy_mo") or ""), e.get("mo_ta", ""), e.get("lap_lai", ""),
                   merge("linh_vuc"), merge("chu_de"), merge("nguon"), verified, today, eid))
    else:
        c.execute("INSERT INTO event(id,ten,ngay_bd,ngay_kt,thanh_pho,dia_diem,hinh_thuc,linh_vuc,to_chuc,url,gia_ve,"
                  "quy_mo,chu_de,mo_ta,nguon,chua_xac_minh,lap_lai,first_seen,last_seen) VALUES"
                  "(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                  (eid, e.get("ten", ""), e.get("ngay_bd", ""), e.get("ngay_kt", ""), e.get("thanh_pho", ""),
                   e.get("dia_diem", ""), e.get("hinh_thuc", ""), jl(lst(e.get("linh_vuc"))), e.get("to_chuc", ""),
                   e.get("url", ""), str(e.get("gia_ve") or ""), str(e.get("quy_mo") or ""), jl(lst(e.get("chu_de"))),
                   e.get("mo_ta", ""), jl(lst(e.get("nguon"))), 0 if e.get("chua_xac_minh") is False else 1,
                   e.get("lap_lai", ""), today, today))
    for tc in [t for t in re.split(r"\s*[;,&]\s*| và | x ", e.get("to_chuc") or "") if t.strip()][:4]:
        c.execute("INSERT OR IGNORE INTO role VALUES(?,?,?,?)", (eid, "org", upsert_org(c, tc, "", today), "tổ chức"))
    for sp in e.get("tai_tro") or []:
        ten, vt = (sp.get("ten"), sp.get("hang") or "tài trợ") if isinstance(sp, dict) else (sp, "tài trợ")
        if ten:
            c.execute("INSERT OR IGNORE INTO role VALUES(?,?,?,?)", (eid, "org", upsert_org(c, ten, "", today), vt))
    for p in e.get("dien_gia") or []:
        p = p if isinstance(p, dict) else {"ten": p}
        if p.get("ten"):
            c.execute("INSERT OR IGNORE INTO role VALUES(?,?,?,?)",
                      (eid, "person", upsert_person(c, p, today), p.get("vai_tro") or "diễn giả"))
    for i, ins in enumerate(e.get("da_noi") or []):
        if not isinstance(ins, dict):  # chuỗi tự do: đoán loại theo tiền tố
            m = re.match(r"\s*(pain ?point|nỗi đau|vấn đề|giải pháp[^:]{0,15}|solution|xu hướng|số liệu)\s*:\s*", ins, re.I)
            loai = "chu_de"
            if m:
                h = fold(m[1])
                loai = "pain_point" if h.startswith(("pain", "noi dau", "van de")) else "solution" if h.startswith(("giai phap", "solution")) \
                    else "xu_huong" if h.startswith("xu huong") else "so_lieu"
                ins = ins[m.end():]
            elif re.search(r"\d+([.,]\d+)?\s*%|tỷ|triệu", ins):
                loai = "so_lieu"
            ins = {"loai": loai, "noi_dung": ins}
        add_insight(c, eid, None, ins, today)
    return eid


def add_insight(c, eid, tid, ins: dict, today: str):
    loai = ins.get("loai", "chu_de")
    if loai not in INSIGHT_KINDS:
        loai = "chu_de"
    nd = (ins.get("noi_dung") or "").strip()
    if not nd:
        return
    iid = hashlib.sha1(f"{eid}|{loai}|{fold(nd)}".encode()).hexdigest()[:16]
    c.execute("INSERT OR IGNORE INTO insight VALUES(?,?,?,?,?,?,?,?,?,?)",
              (iid, eid, tid, loai, nd, ins.get("nhom") or slug(nd, 40), ins.get("ai_noi", ""),
               ins.get("nguon", ""), ins.get("ngay", ""), today))


def cmd_init(args):
    con().commit()
    print(f"OK {DB}")


def cmd_seed(args):
    c = con()
    today = TODAY.isoformat()
    for f in args.files:
        d = load_json(Path(f), {})
        evs = d.get("events", d if isinstance(d, list) else [])
        for e in evs:
            if e.get("ten"):
                upsert_event(c, e, today)
        for p in d.get("people", []):
            upsert_person(c, p, today)
        aws = d.get("awards", [])
        for a in aws:
            if a.get("ten"):
                upsert_award(c, a, today)
        print(f"{f}: {len(evs)} sự kiện, {len(aws)} giải thưởng")
    c.commit()


# ---------------------------------------------------------------- giải thưởng
# Giải cá nhân viết lách/báo chí: LAB022 (contestscan.py) vẫn là nơi kiểm điều kiện và viết bài dự thi.
AWARD_STAGES = ["mới", "theo dõi", "chuẩn bị hồ sơ", "đã nộp", "vào vòng sau", "đoạt giải", "trượt", "bỏ"]
ISO = re.compile(r"^\d{4}-\d\d-\d\d$")


def upsert_award(c, a: dict, today: str) -> str:
    aid = a.get("id") or slug(a["ten"])
    row = c.execute("SELECT * FROM award WHERE id=?", (aid,)).fetchone()
    lst = lambda v: v if isinstance(v, list) else ([v] if v else [])
    tp = a.get("tra_phi_de_nhan")
    vals = dict(ten=a["ten"], to_chuc=a.get("to_chuc", ""), doi_tuong=a.get("doi_tuong", ""),
                linh_vuc=jl(lst(a.get("linh_vuc"))), hang_muc=jl(lst(a.get("hang_muc"))), han_nop=a.get("han_nop") or "",
                mua_nop=a.get("mua_nop") or "", le_trao=a.get("le_trao") or "", dia_diem_le_trao=a.get("dia_diem_le_trao") or "",
                phi_tham_du=str(a.get("phi_tham_du") or ""), uy_tin=a.get("uy_tin"), ly_do_uy_tin=a.get("ly_do_uy_tin", ""),
                tra_phi_de_nhan=None if tp is None else int(bool(tp)), url=a.get("url", ""), chu_ky=a.get("chu_ky", ""),
                nguon=jl(lst(a.get("nguon"))), chua_xac_minh=0 if a.get("chua_xac_minh") is False else 1)
    if row:
        sets = ", ".join(f"{k}=coalesce(nullif(?,''),{k})" for k in vals)
        c.execute(f"UPDATE award SET {sets}, last_seen=? WHERE id=?", [*(v if v is not None else "" for v in vals.values()), today, aid])
    else:
        c.execute(f"INSERT INTO award(id,{','.join(vals)},first_seen,last_seen) VALUES({','.join('?' * (len(vals) + 3))})",
                  [aid, *vals.values(), today, today])
    for w in a.get("nguoi_doat_gan_nhat") or a.get("nguoi_doat") or []:
        w = w if isinstance(w, dict) else {"ten": w}
        if not w.get("ten"):
            continue
        vt = " ".join(x for x in ["đoạt giải", str(w.get("nam") or ""), w.get("hang_muc") or ""] if x)[:120]
        if w.get("loai") == "ca_nhan":
            k, loai = upsert_person(c, {"ten": w["ten"], "to_chuc": w.get("to_chuc", "")}, today), "person"
        else:
            k, loai = upsert_org(c, w["ten"], "doanh nghiệp", today), "org"
        c.execute("INSERT OR IGNORE INTO role VALUES(?,?,?,?)", ("award:" + aid, loai, k, vt))
    # Lễ trao giải có ngày cụ thể → thành một sự kiện để chấm "có nên dự"
    if ISO.match(a.get("le_trao") or ""):
        upsert_event(c, {"id": "le-trao-" + aid, "ten": "Lễ trao giải " + a["ten"], "ngay_bd": a["le_trao"],
                         "thanh_pho": a.get("dia_diem_le_trao", ""), "hinh_thuc": "offline", "to_chuc": a.get("to_chuc", ""),
                         "linh_vuc": lst(a.get("linh_vuc")), "chu_de": lst(a.get("hang_muc"))[:6], "url": a.get("url", ""),
                         "nguon": lst(a.get("nguon")), "chua_xac_minh": a.get("chua_xac_minh", True)}, today)
    return aid


def cmd_import22(args):
    """Nhập kho cuộc thi/giải của LAB022 (seed-contests.json hoặc contests.json) thành giải cho cá nhân."""
    c = con()
    d = load_json(Path(args.file), {})
    L = d.get("contests", []) if isinstance(d, dict) else d
    n = 0
    for x in L:
        if not x.get("title"):
            continue
        dl = x.get("deadline") or ""
        rd = x.get("results_date") or ""
        upsert_award(c, {"id": "lab022-" + x["id"], "ten": x["title"], "to_chuc": x.get("organizer", ""),
                         "doi_tuong": "ca_nhan", "linh_vuc": [x.get("category", "")], "hang_muc": [x.get("format", "")],
                         "han_nop": dl if ISO.match(dl) else "", "mua_nop": x.get("expected_deadline") or "",
                         "le_trao": rd if ISO.match(rd) else "", "phi_tham_du": x.get("fee", ""),
                         "uy_tin": x.get("branding_value"), "ly_do_uy_tin": x.get("fit_note", ""), "url": x.get("url", ""),
                         "chu_ky": x.get("cycle", ""), "nguon": [x.get("source") or x.get("url", "")],
                         "chua_xac_minh": not x.get("verified")}, TODAY.isoformat())
        n += 1
    c.commit()
    print(f"Nhập {n} mục từ LAB022 (LAB022 vẫn là nơi viết bài dự thi; ở đây chỉ để chấm chung và xem lịch)")


def score_award(c, a, prof, l35) -> tuple[int, str, str]:
    why, s = [], 0
    blob = fold(" ".join([a["ten"] or "", a["to_chuc"] or "", " ".join(jr(a["linh_vuc"])), " ".join(jr(a["hang_muc"]))]))
    hits = [k for k in prof.get("quan_tam", {}) if has(blob, k)]
    s += min(25, sum(prof["quan_tam"][k] for k in hits))
    if hits:
        why.append("hợp: " + ", ".join(hits[:3]))
    ut = a["uy_tin"] or 3
    s += ut * 6
    if a["tra_phi_de_nhan"] == 1:
        s -= 30
        why.append("nghi trả phí là có giải")
    # ai trong hồ sơ nộp được
    can = []
    young = re.search(r"(?<!\w)(under 30|duoi 3\d|tuoi 20|tre tieu bieu|nha khoa hoc tre|guong mat tre|sinh vien|hoc sinh|thanh nien)(?!\w)",
                      fold(" ".join([a["ten"] or "", a["ly_do_uy_tin"] or "", " ".join(jr(a["hang_muc"]))])))
    for u in prof.get("ung_vien", []):
        if young and u.get("loai") == "ca_nhan" and (u.get("tuoi") or 0) > 35:
            continue
        if a["doi_tuong"] in ("ca_hai", u.get("loai")) or not a["doi_tuong"]:
            if not u.get("linh_vuc") or any(has(blob, x) for x in u["linh_vuc"]):
                can.append(u["ten"])
    if can:
        s += 15
        why.append("ứng viên: " + ", ".join(can))
    # người thắng là đối tượng LINHX quan tâm → giá trị theo dõi/networking
    wins = c.execute("SELECT o.ten FROM role r JOIN org o ON o.k=r.k WHERE r.event_id=? AND r.loai='org'", ("award:" + a["id"],)).fetchall()
    hot = [w["ten"] for w in wins if l35 and max((l35["company"].get(x, 0) for x in aliases(w["ten"])), default=0) >= prof.get("lab035_nguong_dn", 50)]
    if hot:
        s += min(10, 3 * len(hot))
        why.append("người thắng đáng theo dõi: " + ", ".join(hot[:3]))
    days = None
    if ISO.match(a["han_nop"] or ""):
        days = (dt.date.fromisoformat(a["han_nop"]) - TODAY).days
        if days < 0:
            why.append("đã hết hạn kỳ này")
        elif days <= 14:
            why.append(f"còn {days} ngày")
    if a["chua_xac_minh"]:
        why.append("chưa xác minh")
    th = prof.get("nguong_giai", {"nop": 55, "theo_doi": 35})
    if a["giai_doan"] == "bỏ" or s < th["theo_doi"] - 10:
        lab = "Bỏ"
    elif can and s >= th["nop"] and (days is None or days >= 0):
        lab = "Nộp"
    elif can and s >= th["theo_doi"] and (days is None or days >= 0):
        lab = "Cân nhắc nộp"
    elif wins or (a["uy_tin"] or 0) >= 4 or s >= th["theo_doi"]:
        lab = "Theo dõi người thắng"
    else:
        lab = "Bỏ"
    return s, lab, "; ".join(why)


def write_awards(c):
    L = [f"# Radar giải thưởng ({TODAY})", "",
         "Nhãn: **Nộp** (có ứng viên trong hồ sơ, điểm đủ), **Cân nhắc nộp**, **Theo dõi người thắng** (danh sách người thắng là khách hàng, đối tác hoặc diễn giả tiềm năng), **Bỏ**. "
         "Uy tín 1 đến 5 do Claude đánh giá kèm lý do; ⚠ là chưa xác minh.", ""]
    for lab in ("Nộp", "Cân nhắc nộp", "Theo dõi người thắng"):
        xs = c.execute("SELECT * FROM award WHERE nhan=? ORDER BY (han_nop='' ), han_nop, diem DESC", (lab,)).fetchall()
        if not xs:
            continue
        L += [f"## {lab} ({len(xs)})", "", "| Hạn nộp | Giải | Cho ai | Uy tín | Lễ trao | Điểm | Vì sao |", "|---|---|---|---|---|---|---|"]
        for a in xs:
            ten = f"[{a['ten']}]({a['url']})" if a["url"] else a["ten"]
            L.append(f"| {a['han_nop'] or a['mua_nop'] or '?'} | {ten}{' ⚠' if a['chua_xac_minh'] else ''} | "
                     f"{ {'doanh_nghiep': 'DN', 'ca_nhan': 'cá nhân', 'ca_hai': 'cả hai'}.get(a['doi_tuong'], a['doi_tuong'] or '?') } | "
                     f"{a['uy_tin'] or '?'} | {a['le_trao'] or ''} | {a['diem']} | {(a['ly_do'] or '').replace('|', '/')} |")
        L.append("")
    L += ["## Ai hay đoạt giải (theo kho)", "", "| Đơn vị / người | Số giải | Giải |", "|---|---|---|"]
    q = ("SELECT coalesce(o.ten, p.ten) ten, count(DISTINCT r.event_id) n, group_concat(DISTINCT a.ten) g FROM role r "
         "LEFT JOIN org o ON r.loai='org' AND o.k=r.k LEFT JOIN person p ON r.loai='person' AND p.k=r.k "
         "JOIN award a ON 'award:' || a.id = r.event_id GROUP BY r.loai, r.k ORDER BY n DESC LIMIT 30")
    for r in c.execute(q):
        L.append(f"| {r['ten']} | {r['n']} | {(r['g'] or '')[:150]} |")
    (OUT / "GIAI-THUONG.md").write_text("\n".join(L) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- scan
class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self._href, self._buf = [], None, []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._href, self._buf = dict(attrs).get("href"), []

    def handle_data(self, data):
        if self._href is not None:
            self._buf.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href:
            t = re.sub(r"\s+", " ", "".join(self._buf)).strip()
            if t:
                self.links.append((self._href, t))
            self._href = None


def parse_feed(xml_text: str) -> list[dict]:
    root = ET.fromstring(xml_text.encode("utf-8", errors="replace"))
    ns = {"a": "http://www.w3.org/2005/Atom"}
    out = []
    for e in root.findall(".//item") or root.findall(".//a:entry", ns):
        def g(*tags):
            for t in tags:
                el = e.find(t, ns)
                if el is not None and (el.text or "").strip():
                    return el.text.strip()
            return ""
        link = g("link")
        if not link:
            le = e.find("a:link", ns)
            link = le.get("href", "") if le is not None else ""
        out.append({"title": strip_tags(g("title", "a:title")), "url": link,
                    "summary": strip_tags(g("description", "a:summary", "a:content"))[:2000],
                    "published": g("pubDate", "a:published", "a:updated")})
    return out


def parse_ical(text: str) -> list[dict]:
    """VEVENT tối giản (Luma/Meetup/Google Calendar xuất .ics). Bỏ qua RRULE."""
    text = re.sub(r"\r?\n[ \t]", "", text)
    out = []
    for blk in re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", text, re.S):
        f = {}
        for line in blk.strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                f[k.split(";")[0].upper()] = v.replace("\\n", "\n").replace("\\,", ",").replace("\\;", ";")

        def d(v):
            m = re.match(r"(\d{4})(\d\d)(\d\d)", v or "")
            return f"{m[1]}-{m[2]}-{m[3]}" if m else ""
        out.append({"title": f.get("SUMMARY", ""), "url": f.get("URL", "") or (re.search(r"https?://\S+", f.get("DESCRIPTION", "")) or [""])[0],
                    "summary": (f.get("DESCRIPTION", "")[:1500] + " | " + f.get("LOCATION", "")).strip(" |"),
                    "published": "", "ngay_bd": d(f.get("DTSTART")), "ngay_kt": d(f.get("DTEND")),
                    "dia_diem": f.get("LOCATION", "")})
    return out


def scrub(t: str) -> str:
    """Văn bản do người lạ viết sẽ được Claude đọc: bỏ ký tự ẩn, đánh dấu câu kiểu chỉ dẫn (ý của luma-mcp/scrubber.py)."""
    t = "".join(ch for ch in unicodedata.normalize("NFKC", t or "") if unicodedata.category(ch) != "Cf")
    return re.sub(r"(?i)(ignore (all )?previous instructions|^\s*system\s*:|bỏ qua (mọi|các) hướng dẫn)", r"`\1`", t)


def luma_get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "origin": "https://lu.ma", "referer": "https://lu.ma/"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def parse_luma(src: dict) -> list[dict]:
    """API web nội bộ api.lu.ma (theo alx1p/luma-cal-mcp): discover/get-paginated-events hoặc calendar/get-items.
    Không chính thức, có thể đổi; tối đa 4 trang, mỗi trang 50."""
    out, cursor = [], None
    for _ in range(4):
        url = src["url"] + (("&" if "?" in src["url"] else "?") + f"pagination_cursor={cursor}" if cursor else "")
        d = luma_get(url)
        for en in d.get("entries", []):
            ev = en.get("event") or {}
            geo = ev.get("geo_address_info") or {}
            hosts = [h.get("name") for h in en.get("hosts") or [] if h.get("name")]
            out.append({"title": ev.get("name", ""), "url": "https://lu.ma/" + ev.get("url", "") if ev.get("url") else "",
                        "summary": " | ".join(x for x in [geo.get("full_address") or geo.get("address") or "",
                                                         "Host: " + ", ".join(hosts) if hosts else "",
                                                         "miễn phí" if (en.get("ticket_info") or {}).get("is_free") else ""] if x),
                        "published": "", "ngay_bd": (ev.get("start_at") or "")[:10], "ngay_kt": (ev.get("end_at") or "")[:10],
                        "dia_diem": geo.get("city") or geo.get("full_address") or ("online" if ev.get("location_type") == "online" else "")})
        if not d.get("has_more") or not d.get("next_cursor"):
            break
        cursor = d["next_cursor"]
    return out


def parse_jsonld(page: str) -> list[dict]:
    """Khối schema.org/Event trên trang sự kiện (Ticketbox, Eventbrite, WordPress The Events Calendar...)."""
    out = []
    for blk in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', page, re.S | re.I):
        try:
            d = json.loads(blk.strip())
        except ValueError:
            continue
        stack = d if isinstance(d, list) else [d]
        while stack:
            x = stack.pop()
            if not isinstance(x, dict):
                continue
            stack += x.get("@graph", []) if isinstance(x.get("@graph"), list) else []
            ty = x.get("@type")
            ty = " ".join(ty) if isinstance(ty, list) else str(ty or "")
            if not re.search(r"Event$|Festival|Hackathon|EventSeries", ty):
                continue
            loc = x.get("location") or {}
            loc = loc[0] if isinstance(loc, list) and loc else loc
            addr = loc.get("address", "") if isinstance(loc, dict) else ""
            addr = " ".join(str(v) for v in addr.values() if isinstance(v, str)) if isinstance(addr, dict) else str(addr)
            perf = x.get("performer") or []
            perf = perf if isinstance(perf, list) else [perf]
            names = [p.get("name") for p in perf if isinstance(p, dict) and p.get("name")]
            out.append({"title": x.get("name", ""), "url": x.get("url", ""), "published": "",
                        "summary": " | ".join(v for v in [str(x.get("description", ""))[:800], addr,
                                                         "Diễn giả: " + ", ".join(names) if names else "",
                                                         "online" if "Online" in str(x.get("eventAttendanceMode", "")) else ""] if v),
                        "ngay_bd": str(x.get("startDate", ""))[:10], "ngay_kt": str(x.get("endDate", ""))[:10],
                        "dia_diem": (loc.get("name", "") if isinstance(loc, dict) else "") + " " + addr})
    return out


def parse_html(page: str, src: dict) -> list[dict]:
    p = LinkParser()
    p.feed(page)
    host = urlparse(src["url"]).netloc
    inc = [re.compile(x, re.I) for x in src.get("link_patterns", [])]
    seen, out = set(), []
    for href, text in p.links:
        url = urljoin(src["url"], href)
        if urlparse(url).netloc != host or url in seen or len(text) < 12:
            continue
        if inc and not any(r.search(url) for r in inc):
            continue
        seen.add(url)
        out.append({"title": text, "url": url, "summary": "", "published": ""})
    return out


def cmd_scan(args):
    srcs = [s for s in load_json(CFG / "sources.json", {"sources": []})["sources"] if s.get("active", True)]
    c = con()
    today = TODAY.isoformat()
    tot = new = 0
    for s in srcs:
        kind = s.get("kind")
        if kind in ("manual", "websearch"):
            continue
        try:
            if kind == "luma":
                items = parse_luma(s)
            else:
                raw = fetch(s["url"])
                items = parse_feed(raw) if kind in ("rss", "gnews") else parse_ical(raw) if kind == "ical" \
                    else parse_jsonld(raw) if kind == "jsonld" else parse_html(raw, s) if kind == "html" else []
        except Exception as ex:  # nguồn chết không làm hỏng cả lượt
            print(f"LỖI {s['id']}: {ex.__class__.__name__}: {str(ex)[:120]}")
            c.execute("INSERT INTO log VALUES(?,?,?,?)", (today, "scan_loi", s["id"], str(ex)[:300]))
            continue
        flt = re.compile(s["filter"], re.I) if s.get("filter") else None
        for it in items:
            blob = f"{it['title']} {it.get('summary','')}"
            if flt and not flt.search(blob):
                continue
            if kind in ("rss", "gnews", "html") and not EVENT_CUE.search(blob):
                continue
            iid = hashlib.sha1((it["url"] or it["title"]).encode()).hexdigest()[:16]
            tot += 1
            if c.execute("SELECT 1 FROM item WHERE id=?", (iid,)).fetchone():
                c.execute("UPDATE item SET last_seen=? WHERE id=?", (today, iid))
                continue
            new += 1
            summ = scrub(it.get("summary", ""))
            it["title"] = scrub(it["title"])
            if it.get("ngay_bd"):  # iCal đã có ngày chuẩn: ghi kèm để extract dùng
                summ = f"[ngay_bd={it['ngay_bd']};ngay_kt={it.get('ngay_kt','')};dia_diem={it.get('dia_diem','')}] {summ}"
            c.execute("INSERT INTO item VALUES(?,?,?,?,?,?,?,?,?,?)",
                      (iid, s["id"], it["title"], it["url"], summ, it.get("published", ""), today, today, "new", None))
        print(f"{s['id']}: {len(items)} mục")
    c.commit()
    print(f"Tổng {tot} tin sự kiện, {new} tin mới")


# ---------------------------------------------------------------- extract
def guess(blob: str, ref: dt.date) -> dict:
    g = {}
    m = re.search(r"\[ngay_bd=([\d-]*);ngay_kt=([\d-]*);dia_diem=([^\]]*)\]", blob)
    if m and m[1]:
        g["ngay_bd"], g["ngay_kt"], g["dia_diem"] = m[1], m[2], m[3]
    else:
        ds = [x for x in find_dates(blob, ref) if x[0] >= ref - dt.timedelta(days=3)]
        if ds:
            g["ngay_bd"] = ds[0][0].isoformat()
            if ds[0][1]:
                g["ngay_kt"] = ds[0][1].isoformat()
    for name, rx in CITY:
        if re.search(rx, blob, re.I):
            g["thanh_pho"] = name
            break
    on = bool(ONLINE.search(blob))
    g["hinh_thuc"] = "hybrid" if on and g.get("thanh_pho") else "online" if on else "offline" if g.get("thanh_pho") else ""
    if re.search(r"miễn phí|free", blob, re.I):
        g["gia_ve"] = "miễn phí"
    return g


def cmd_extract(args):
    c = con()
    today = TODAY.isoformat()
    lv = profile().get("linh_vuc_tu_khoa", {})
    n = 0
    for it in c.execute("SELECT * FROM item WHERE status='new'").fetchall():
        blob = f"{it['title']} . {it['summary']}"
        try:
            ref = dt.date.fromisoformat((it["first_seen"] or today)[:10])
        except ValueError:
            ref = TODAY
        g = guess(blob, ref)
        if not g.get("ngay_bd"):
            c.execute("UPDATE item SET status='no_date' WHERE id=?", (it["id"],))
            continue
        fb = fold(blob)
        e = dict(g, ten=re.sub(r"\s+-\s+[^-]{2,40}$", "", it["title"])[:200], url=it["url"],
                 linh_vuc=[k for k, kws in lv.items() if any(has(fb, w) for w in kws)],
                 mo_ta=it["summary"][:600], nguon=[it["url"]], chua_xac_minh=True)
        m = re.search(r"Diễn giả: ([^|]+)", blob)
        if m:
            e["dien_gia"] = [{"ten": x.strip()} for x in m[1].split(",") if x.strip()][:12]
        m = re.search(r"Host: ([^|]+)", blob)
        if m:
            e["to_chuc"] = m[1].strip()[:150]
        eid = upsert_event(c, e, today)
        c.execute("UPDATE item SET status='event', event_id=? WHERE id=?", (eid, it["id"]))
        n += 1
    c.commit()
    print(f"Ra {n} ứng viên sự kiện (cần Claude hoặc Linh xác minh trước khi tin)")


# ---------------------------------------------------------------- absorb (Claude trích → CSDL)
def cmd_absorb(args):
    """JSON: {event_id | event:{...}, talks:[{tieu_de, dien_gia:[{ten,chuc_danh,to_chuc}], chu_de, tom_tat,
    url_video, insights:[...]}], insights:[{loai, noi_dung, nhom, ai_noi, nguon}], danh_gia:[{ten, diem, ly_do}]}"""
    c = con()
    today = TODAY.isoformat()
    for f in args.files:
        d = load_json(Path(f), {})
        eid = d.get("event_id") or upsert_event(c, d["event"], today)
        if not c.execute("SELECT 1 FROM event WHERE id=?", (eid,)).fetchone():
            print(f"{f}: không thấy sự kiện {eid}, thêm 'event' vào file")
            continue
        nt = ni = 0
        for t in d.get("talks", []):
            ks = []
            for p in t.get("dien_gia") or []:
                p = p if isinstance(p, dict) else {"ten": p}
                k = upsert_person(c, dict(p, chu_de=t.get("chu_de") or []), today)
                ks.append(k)
                c.execute("INSERT OR IGNORE INTO role VALUES(?,?,?,?)", (eid, "person", k, "diễn giả"))
            tid = hashlib.sha1(f"{eid}|{fold(t.get('tieu_de',''))}".encode()).hexdigest()[:16]
            c.execute("INSERT OR REPLACE INTO talk VALUES(?,?,?,?,?,?,?,?,?)",
                      (tid, eid, t.get("tieu_de", ""), jl(ks), jl(t.get("chu_de")), t.get("tom_tat", ""),
                       t.get("url_video", ""), t.get("nguon", ""), today))
            nt += 1
            for ins in t.get("insights") or []:
                add_insight(c, eid, tid, dict(ins, ai_noi=ins.get("ai_noi") or ", ".join(ks)), today)
                ni += 1
        for ins in d.get("insights") or []:
            add_insight(c, eid, None, ins, today)
            ni += 1
        for r in d.get("danh_gia") or []:
            rate(c, r["ten"], float(r["diem"]), r.get("ly_do", ""))
        if d.get("giai_doan"):
            c.execute("UPDATE event SET giai_doan=? WHERE id=?", (d["giai_doan"], eid))
        c.execute("INSERT INTO log VALUES(?,?,?,?)", (today, "absorb", eid, f"{nt} talk, {ni} insight"))
        print(f"{f}: {eid} +{nt} talk, +{ni} insight")
    c.commit()


def cmd_gannhom(args):
    """Claude gom nhóm lại các ý đã có: {"nhom": {insight_id: [loai, nhom]}}; nhom "bo" thì xoá ý đó."""
    c = con()
    d = load_json(Path(args.file), {}).get("nhom", {})
    for iid, (loai, nhom) in d.items():
        if nhom in ("bo", "khac"):
            c.execute("DELETE FROM insight WHERE id=?", (iid,))
        else:
            c.execute("UPDATE insight SET loai=?, nhom=? WHERE id=?", (loai, nhom, iid))
    c.commit()
    print(f"Gán lại {len(d)} ý")


def rate(c, ten, diem, ly_do=""):
    k = key_of(ten)
    row = c.execute("SELECT * FROM person WHERE k=?", (k,)).fetchone()
    if not row:
        upsert_person(c, {"ten": ten}, TODAY.isoformat())
        row = c.execute("SELECT * FROM person WHERE k=?", (k,)).fetchone()
    n = row["so_lan_cham"] or 0
    avg = ((row["diem_hay"] or 0) * n + diem) / (n + 1)
    note = "; ".join(x for x in [row["ghi_chu"] or "", f"{TODAY}: {diem:g}/5 {ly_do}".strip()] if x)
    c.execute("UPDATE person SET diem_hay=?, so_lan_cham=?, ghi_chu=? WHERE k=?", (round(avg, 2), n + 1, note[-1500:], k))


def cmd_rate(args):
    c = con()
    rate(c, args.ten, float(args.diem), " ".join(args.ly_do))
    c.commit()
    print("OK")


# ---------------------------------------------------------------- score
def aliases(ten: str) -> set:
    """'FPT (FPT Telecom / FPT Digital)' → {fpt, fpt telecom, fpt digital, ...}: tên ở LAB035 hay ghép nhiều thực thể."""
    out = {key_of(ten)}
    for part in re.split(r"[()/,;]| - ", ten or ""):
        if len(part.strip()) >= 2:
            out.add(key_of(part))
    return {a for a in out if len(a) >= 2}


def lab035_db() -> dict | None:
    """Chỉ mục DN/KOL của radar cộng đồng LAB035: {"company": {alias: diem}, "kol": {alias: diem}}."""
    p = os.environ.get("LAB035_DB") or profile().get("lab035_db")
    if p and not re.match(r"^[A-Za-z]:", str(p)):
        p = rel(p)
    if not (p and Path(p).exists()):
        return None
    x = sqlite3.connect(p)
    idx = {"company": {}, "kol": {}}
    for t in idx:
        try:
            for ten, diem in x.execute(f"SELECT ten, diem FROM {t}"):
                for a in aliases(ten):
                    idx[t][a] = max(idx[t].get(a, 0), diem or 0)
        except sqlite3.Error:
            pass
    x.close()
    return idx


def score_event(c, e, prof, hot_topics: set, l35) -> tuple[int, str, list[str]]:
    why, s = [], 0
    blob = fold(" ".join([e["ten"] or "", e["mo_ta"] or "", " ".join(jr(e["chu_de"])), " ".join(jr(e["linh_vuc"]))]))
    # 1. Khớp quan tâm (tối đa 30)
    hits = [k for k in prof.get("quan_tam", {}) if has(blob, k)]
    pt = min(30, sum(prof["quan_tam"][k] for k in hits))
    if pt:
        s += pt
        why.append("hợp: " + ", ".join(hits[:4]))
    if any(has(blob, k) for k in prof.get("tranh", [])):
        s -= 25
        why.append("chủ đề nên tránh")
    # 2. Diễn giả (tối đa 20): diễn giả đã chấm hay, đang theo dõi, xuất hiện nhiều nơi
    ps = c.execute("SELECT p.* FROM role r JOIN person p ON p.k=r.k WHERE r.event_id=? AND r.loai='person'", (e["id"],)).fetchall()
    watch = {key_of(x) for x in prof.get("dien_gia_theo_doi", [])}
    sp, good = 0, []
    for p in ps:
        appear = c.execute("SELECT count(DISTINCT event_id) FROM role WHERE loai='person' AND k=?", (p["k"],)).fetchone()[0]
        v = (6 if p["k"] in watch or p["theo_doi"] else 0) + (int((p["diem_hay"] or 0) * 2) if p["diem_hay"] else 0) + min(3, appear - 1)
        if l35 is not None:
            v += 3 if l35["kol"].get(p["k"], 0) > 0 else 0
        if v >= 4:
            good.append(p["ten"])
        sp += v
    if ps:
        sp += 2
    s += min(20, sp)
    if good:
        why.append("diễn giả: " + ", ".join(good[:3]))
    # 3. Gặp ai (tối đa 15): nhà tài trợ/BTC là đối tượng LINHX quan tâm (profile hoặc LAB035)
    orgs = c.execute("SELECT o.ten, o.k, r.vai_tro FROM role r JOIN org o ON o.k=r.k WHERE r.event_id=? AND r.loai='org'", (e["id"],)).fetchall()
    target = {key_of(x) for x in prof.get("doi_tuong_muon_gap", [])}
    meet = [o["ten"] for o in orgs if o["k"] in target]
    if l35 is not None:
        for o in orgs:
            if max((l35["company"].get(a, 0) for a in aliases(o["ten"])), default=0) >= prof.get("lab035_nguong_dn", 50) \
                    and o["ten"] not in meet:
                meet.append(o["ten"])
    if meet:
        s += min(15, 5 * len(meet))
        why.append("gặp: " + ", ".join(meet[:3]))
    elif orgs:
        s += min(4, len(orgs))
    # 4. Đi lại (tối đa 15)
    home = {fold(x) for x in prof.get("thanh_pho_nha", [])}
    hf = e["hinh_thuc"] or ""
    if hf == "online":
        s += 10
    elif fold(e["thanh_pho"] or "") in home:
        s += 15 if hf != "online" else 10
    elif e["thanh_pho"]:
        s += 4
        why.append(f"phải đi {e['thanh_pho']}")
    # 5. Chi phí (tối đa 10)
    gv = fold(e["gia_ve"] or "")
    num = re.findall(r"\d[\d.]*", (e["gia_ve"] or "").replace(",", "."))
    if "mien phi" in gv or "free" in gv:
        s += 10
    elif num:
        try:
            v = max(float(x.replace(".", "")) for x in num)
            v = v * 1000 if v < 10000 else v
            s += 7 if v <= 1_000_000 else 4 if v <= 5_000_000 else 1
            if v > prof.get("ngan_sach_ve", 5_000_000):
                why.append(f"vé {e['gia_ve']}")
        except ValueError:
            s += 5
    else:
        s += 5
    # 6. Mới lạ (tối đa 5): chủ đề chưa có trong bản đồ
    tops = {slug(t, 40) for t in jr(e["chu_de"])}
    if len(hot_topics) >= 30 and tops and not (tops & hot_topics):  # chỉ tính khi bản đồ insight đủ dày
        s += 5
        why.append("chủ đề chưa gặp ở sự kiện trước")
    if e["chua_xac_minh"]:
        why.append("chưa xác minh")
    return s, why, good


def label(s: int, e, prof) -> str:
    if e["giai_doan"] in ("bỏ",):
        return "Bỏ"
    th = prof.get("nguong", {"di": 55, "can_nhac": 38, "xem": 25})
    if s >= th["di"]:
        return "Đi"
    if s >= th["can_nhac"]:
        return "Cân nhắc"
    if s >= th["xem"]:
        return "Xem bản ghi"
    return "Bỏ"


def cmd_score(args):
    c = con()
    prof = profile()
    l35 = lab035_db()
    hot = {r[0] for r in c.execute("SELECT nhom FROM insight")}
    n = 0
    for e in c.execute("SELECT * FROM event").fetchall():
        s, why, _ = score_event(c, e, prof, hot, l35)
        c.execute("UPDATE event SET diem=?, nhan=?, ly_do=? WHERE id=?", (s, label(s, e, prof), "; ".join(why), e["id"]))
        n += 1
    m = 0
    for a in c.execute("SELECT * FROM award").fetchall():
        sc, lab, why = score_award(c, a, prof, l35)
        c.execute("UPDATE award SET diem=?, nhan=?, ly_do=? WHERE id=?", (sc, lab, why, a["id"]))
        m += 1
    c.commit()
    print(f"Chấm {n} sự kiện, {m} giải thưởng")


# ---------------------------------------------------------------- insight (bản đồ chủ đề)
def cmd_insight(args):
    c = con()
    since = (TODAY - dt.timedelta(days=args.days)).isoformat()
    rows = c.execute("SELECT i.*, e.ten ev, e.ngay_bd FROM insight i JOIN event e ON e.id=i.event_id "
                     "WHERE coalesce(nullif(e.ngay_bd,''), i.them_ngay) >= ?", (since,)).fetchall()
    by = defaultdict(list)
    for r in rows:
        by[r["loai"]].append(r)
    L = [f"# Bản đồ chủ đề sự kiện ({since} → {TODAY})", "",
         f"Từ {len({r['event_id'] for r in rows})} sự kiện, {len(rows)} ý đã hấp thu. "
         "Nhóm (`nhom`) do Claude gán khi hấp thu; ý xuất hiện ở nhiều sự kiện là tín hiệu mạnh.", ""]
    names = {"chu_de": "Mọi người đang nói gì", "pain_point": "Pain point lặp lại", "solution": "Solution, cách làm mới",
             "xu_huong": "Xu hướng", "so_lieu": "Số liệu đáng nhớ", "cong_cu": "Công cụ được nhắc", "cau_noi": "Câu nói đáng trích"}
    for loai in INSIGHT_KINDS:
        rs = by.get(loai)
        if not rs:
            continue
        L += [f"## {names[loai]}", "", "| Nhóm | Số sự kiện | Lần đầu | Ví dụ | Ở đâu |", "|---|---|---|---|---|"]
        grp = defaultdict(list)
        for r in rs:
            grp[r["nhom"]].append(r)
        order = sorted(grp.items(), key=lambda kv: (-len({x["event_id"] for x in kv[1]}), kv[0]))
        for g, xs in order[:25]:
            evs = sorted({x["ev"] for x in xs})
            first = min((x["ngay_bd"] or x["them_ngay"]) for x in xs)
            ex = xs[0]["noi_dung"].replace("|", "/")[:160]
            L.append(f"| {g} | {len(evs)} | {first} | {ex} | {'; '.join(evs)[:120]} |")
        L.append("")
    L += ["## Diễn giả", "", "| Diễn giả | Tổ chức | Số sự kiện | Điểm hay (lượt chấm) | Chủ đề |", "|---|---|---|---|---|"]
    for p in c.execute("SELECT p.*, count(DISTINCT r.event_id) n FROM person p JOIN role r ON r.k=p.k AND r.loai='person' "
                       "GROUP BY p.k ORDER BY coalesce(p.diem_hay,0) DESC, n DESC LIMIT 40"):
        hay = f"{p['diem_hay']:g} ({p['so_lan_cham']})" if p["diem_hay"] else "chưa chấm"
        L.append(f"| {p['ten']} | {p['to_chuc'] or ''} | {p['n']} | {hay} | {', '.join(jr(p['chu_de'])[:4])} |")
    L += ["", "## Ai tài trợ nhiều nhất", "", "| Đơn vị | Số sự kiện | Vai trò |", "|---|---|---|"]
    for o in c.execute("SELECT o.ten, count(DISTINCT r.event_id) n, group_concat(DISTINCT r.vai_tro) vt FROM org o "
                       "JOIN role r ON r.k=o.k AND r.loai='org' WHERE r.vai_tro!='tổ chức' GROUP BY o.k ORDER BY n DESC LIMIT 25"):
        L.append(f"| {o['ten']} | {o['n']} | {o['vt']} |")
    tags = Counter(t for (cd,) in c.execute("SELECT chu_de FROM event WHERE ngay_bd >= ?", (since,)) for t in jr(cd))
    L += ["", "## Chủ đề trên lịch sự kiện (theo tên/agenda, chưa hấp thu)", "",
          ", ".join(f"{t} ({n})" for t, n in tags.most_common(40)) or "(chưa có)", ""]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "BAN-DO-CHU-DE.md").write_text("\n".join(L), encoding="utf-8")
    print(f"OK {OUT / 'BAN-DO-CHU-DE.md'}")


# ---------------------------------------------------------------- report / ics / digest
def upcoming(c, days=120):
    end = (TODAY + dt.timedelta(days=days)).isoformat()
    return c.execute("SELECT * FROM event WHERE ngay_bd >= ? AND ngay_bd <= ? ORDER BY ngay_bd",
                     (TODAY.isoformat(), end)).fetchall()


def speakers(c, eid, n=4):
    return [r[0] for r in c.execute("SELECT p.ten FROM role r JOIN person p ON p.k=r.k WHERE r.event_id=? AND r.loai='person' LIMIT ?", (eid, n))]


def ics_text(evs) -> str:
    def esc(s):
        return re.sub(r"([,;\\])", r"\\\1", s or "").replace("\n", " ")
    L = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//LINHX LAB//LAB037 event radar//VI", "X-WR-CALNAME:Sự kiện nên đi"]
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for e in evs:
        if not re.match(r"\d{4}-\d\d-\d\d$", e["ngay_bd"] or ""):
            continue
        end = e["ngay_kt"] if re.match(r"\d{4}-\d\d-\d\d$", e["ngay_kt"] or "") else e["ngay_bd"]
        nxt = (dt.date.fromisoformat(end) + dt.timedelta(days=1)).strftime("%Y%m%d")
        L += ["BEGIN:VEVENT", f"UID:{e['id']}@lab036", f"DTSTAMP:{stamp}", f"DTSTART;VALUE=DATE:{e['ngay_bd'].replace('-', '')}",
              f"DTEND;VALUE=DATE:{nxt}", f"SUMMARY:{esc(('[' + e['nhan'] + '] ') + e['ten'])}",
              f"LOCATION:{esc(e['dia_diem'] or e['thanh_pho'] or e['hinh_thuc'] or '')}",
              f"DESCRIPTION:{esc((e['ly_do'] or '') + ' · ' + (e['url'] or ''))}", f"URL:{e['url'] or ''}",
              "BEGIN:VALARM", "TRIGGER:-P7D", "ACTION:DISPLAY", f"DESCRIPTION:{esc('Còn 7 ngày: ' + e['ten'])}", "END:VALARM",
              "END:VEVENT"]
    L.append("END:VCALENDAR")
    return "\r\n".join(L) + "\r\n"


def cmd_report(args):
    c = con()
    OUT.mkdir(parents=True, exist_ok=True)
    evs = upcoming(c, args.days)
    L = [f"# Lịch sự kiện business và tech ({TODAY} → +{args.days} ngày)", "",
         f"{len(evs)} sự kiện. Nhãn: **Đi** / **Cân nhắc** / **Xem bản ghi** / **Bỏ**. "
         "Dấu ⚠ là chưa xác minh trên trang chính thức.", ""]
    for lab in ("Đi", "Cân nhắc", "Xem bản ghi"):
        xs = [e for e in evs if e["nhan"] == lab]
        if not xs:
            continue
        L += [f"## {lab} ({len(xs)})", "", "| Ngày | Sự kiện | Nơi | Điểm | Vì sao | Diễn giả |", "|---|---|---|---|---|---|"]
        for e in sorted(xs, key=lambda e: (-e["diem"], e["ngay_bd"])):
            warn = " ⚠" if e["chua_xac_minh"] else ""
            ten = f"[{e['ten']}]({e['url']})" if e["url"] else e["ten"]
            L.append(f"| {e['ngay_bd']} | {ten}{warn} | {e['thanh_pho'] or ''} {e['hinh_thuc'] or ''} | {e['diem']} | "
                     f"{(e['ly_do'] or '').replace('|', '/')} | {', '.join(speakers(c, e['id']))} |")
        L.append("")
    bo = [e for e in evs if e["nhan"] == "Bỏ"]
    if bo:
        L += [f"## Bỏ qua ({len(bo)})", "", "; ".join(f"{e['ngay_bd']} {e['ten']}" for e in bo), ""]
    (OUT / "LICH-SU-KIEN.md").write_text("\n".join(L), encoding="utf-8")
    with open(OUT / "su-kien.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "ngay_bd", "ngay_kt", "ten", "thanh_pho", "hinh_thuc", "linh_vuc", "to_chuc", "gia_ve",
                    "chu_de", "dien_gia", "diem", "nhan", "ly_do", "giai_doan", "chua_xac_minh", "url"])
        for e in c.execute("SELECT * FROM event ORDER BY ngay_bd"):
            w.writerow([e["id"], e["ngay_bd"], e["ngay_kt"], e["ten"], e["thanh_pho"], e["hinh_thuc"],
                        "; ".join(jr(e["linh_vuc"])), e["to_chuc"], e["gia_ve"], "; ".join(jr(e["chu_de"])),
                        "; ".join(speakers(c, e["id"], 10)), e["diem"], e["nhan"], e["ly_do"], e["giai_doan"],
                        e["chua_xac_minh"], e["url"]])
    dl = [{"id": "han-" + a["id"], "ngay_bd": a["han_nop"], "ngay_kt": a["han_nop"], "nhan": "Hạn nộp giải",
           "ten": a["ten"], "dia_diem": "", "thanh_pho": "", "hinh_thuc": "", "ly_do": a["ly_do"], "url": a["url"]}
          for a in c.execute("SELECT * FROM award WHERE nhan='Nộp' AND han_nop >= ?", (TODAY.isoformat(),))]
    (OUT / "lich-su-kien.ics").write_text(ics_text([e for e in evs if e["nhan"] in ("Đi", "Cân nhắc")
                                                     or e["giai_doan"] in ("quan tâm", "đăng ký")] + dl), encoding="utf-8")
    write_awards(c)
    print(f"OK {OUT / 'LICH-SU-KIEN.md'}, su-kien.csv, lich-su-kien.ics")


def cmd_digest(args):
    c = con()
    evs = upcoming(c, 45)
    week = (TODAY - dt.timedelta(days=7)).isoformat()
    new = c.execute("SELECT * FROM event WHERE first_seen >= ? AND ngay_bd >= ? ORDER BY ngay_bd", (week, TODAY.isoformat())).fetchall()
    top = sorted([e for e in evs if e["nhan"] in ("Đi", "Cân nhắc")], key=lambda e: -e["diem"])[:7]
    todo = c.execute("SELECT * FROM event WHERE giai_doan='đã đi' ORDER BY ngay_bd DESC").fetchall()
    L = [f"# Event radar: bản tin {TODAY}", "",
         f"- {len(evs)} sự kiện trong 45 ngày tới, {len(new)} sự kiện mới vào kho tuần này.", ""]
    L += ["## Nên đi (45 ngày tới)", ""]
    for e in top:
        L.append(f"- **{e['ngay_bd']} · {e['ten']}** ({e['thanh_pho'] or e['hinh_thuc'] or '?'}; {e['nhan']}, {e['diem']} điểm). "
                 f"{e['ly_do'] or ''}. {e['url'] or ''}")
    if not top:
        L.append("- Chưa có sự kiện đạt ngưỡng.")
    L += ["", "## Mới vào kho", ""] + [f"- {e['ngay_bd']} · {e['ten']} ({e['nhan'] or 'chưa chấm'})" for e in new if e["nhan"] != "Bỏ"][:20]
    due = c.execute("SELECT * FROM award WHERE nhan='Nộp' AND han_nop >= ? AND han_nop <= ? ORDER BY han_nop",
                    (TODAY.isoformat(), (TODAY + dt.timedelta(days=45)).isoformat())).fetchall()
    if due:
        L += ["", "## Giải thưởng sắp hạn nộp", ""] + [f"- **{a['han_nop']} · {a['ten']}** ({a['ly_do']}). {a['url'] or ''}" for a in due]
    if todo:
        L += ["", "## Đã đi, chưa hấp thu", ""] + [f"- {e['ten']}: chạy skill `hap-thu-su-kien`" for e in todo]
    hot = c.execute("SELECT nhom, count(DISTINCT event_id) n FROM insight WHERE loai='pain_point' AND them_ngay >= ? "
                    "GROUP BY nhom ORDER BY n DESC LIMIT 5", ((TODAY - dt.timedelta(days=30)).isoformat(),)).fetchall()
    if hot:
        L += ["", "## Pain point nổi 30 ngày", ""] + [f"- {r['nhom']} ({r['n']} sự kiện)" for r in hot]
    (OUT / "digest").mkdir(parents=True, exist_ok=True)
    p = OUT / "digest" / f"DIGEST-{TODAY}.md"
    p.write_text("\n".join(L) + "\n", encoding="utf-8")
    shutil.copyfile(p, OUT / "digest" / "MOI-NHAT.md")
    print(f"OK {p}")


# ---------------------------------------------------------------- mark / phude / export
def cmd_mark(args):
    c = con()
    if c.execute("SELECT 1 FROM award WHERE id=?", (args.id,)).fetchone():
        if args.stage not in AWARD_STAGES:
            sys.exit(f"Giai đoạn giải phải là một trong: {', '.join(AWARD_STAGES)}")
        c.execute("UPDATE award SET giai_doan=?, ghi_chu=trim(coalesce(ghi_chu,'') || ' ' || ?) WHERE id=?",
                  (args.stage, f"{TODAY}: {' '.join(args.note)}", args.id))
        c.commit()
        print(f"{args.id} → {args.stage}")
        return
    if args.stage not in STAGES:
        sys.exit(f"Giai đoạn phải là một trong: {', '.join(STAGES)}")
    row = c.execute("SELECT id FROM event WHERE id=?", (args.id,)).fetchone() or \
        next((r for r in c.execute("SELECT id, ten FROM event") if similar(r["ten"], args.id, 0.5)), None)
    if not row:
        sys.exit(f"Không thấy sự kiện '{args.id}'")
    note = " ".join(args.note)
    c.execute("UPDATE event SET giai_doan=?, ghi_chu=trim(coalesce(ghi_chu,'') || ' ' || ?) WHERE id=?",
              (args.stage, f"{TODAY}: {note}" if note else "", row["id"]))
    c.execute("INSERT INTO log VALUES(?,?,?,?)", (TODAY.isoformat(), "mark", row["id"], f"{args.stage} {note}"))
    c.commit()
    print(f"{row['id']} → {args.stage}")


def cmd_phude(args):
    """Phụ đề bài talk YouTube (tự động hoặc chính thức) bằng yt-dlp; không có yt-dlp thì hướng dẫn."""
    exe = shutil.which("yt-dlp")
    dest = DATA / "transcripts"
    dest.mkdir(parents=True, exist_ok=True)
    if not exe:
        sys.exit("Chưa có yt-dlp. Cài: pip install yt-dlp (hoặc winget install yt-dlp), rồi chạy lại.")
    tpl = str(dest / f"{args.event_id or 'talk'}-%(id)s.%(ext)s")
    r = subprocess.run([exe, "--skip-download", "--write-subs", "--write-auto-subs", "--sub-langs", "vi,vi-orig,en",
                        "--sub-format", "vtt", "-o", tpl, args.url], capture_output=True, text=True)
    print(r.stdout[-800:] or r.stderr[-800:])
    for v in dest.glob("*.vtt"):
        txt = v.with_suffix(".txt")
        if not txt.exists():
            lines, prev = [], ""
            for ln in v.read_text(encoding="utf-8", errors="replace").splitlines():
                ln = re.sub(r"<[^>]+>", "", ln).strip()
                if not ln or "-->" in ln or ln.startswith(("WEBVTT", "Kind:", "Language:")) or ln == prev:
                    continue
                lines.append(ln)
                prev = ln
            txt.write_text("\n".join(lines), encoding="utf-8")
            print(f"OK {txt}")


def cmd_export35(args):
    """Ghi seed đúng định dạng congdong.py seed (LAB035): DN tài trợ + KOL diễn giả, cộng đồng = sự kiện/BTC."""
    c = con()
    comm, comp, kols = [], [], []
    for e in c.execute("SELECT * FROM event"):
        cid = "su-kien-" + e["id"]
        comm.append({"id": cid, "ten": e["ten"], "loai": "sự kiện", "linh_vuc": ", ".join(jr(e["linh_vuc"])),
                     "don_vi_dung_sau": e["to_chuc"] or "", "su_kien": [f"{e['ngay_bd']} {e['ten']}"],
                     "chu_de_dang_noi": jr(e["chu_de"]), "nguon": jr(e["nguon"])})
        yr = [(e["ngay_bd"] or "")[:4]] if e["ngay_bd"] else []
        for o in c.execute("SELECT o.ten, r.vai_tro FROM role r JOIN org o ON o.k=r.k WHERE r.event_id=? AND r.loai='org' AND r.vai_tro!='tổ chức'", (e["id"],)):
            comp.append({"ten": o["ten"], "cong_dong": [cid], "vai_tro": o["vai_tro"], "nam": yr, "nguon": jr(e["nguon"])[:2],
                         "chua_xac_minh": bool(e["chua_xac_minh"])})
        for p in c.execute("SELECT p.* FROM role r JOIN person p ON p.k=r.k WHERE r.event_id=? AND r.loai='person'", (e["id"],)):
            kols.append({"ten": p["ten"], "chuc_danh": p["chuc_danh"] or "", "to_chuc": p["to_chuc"] or "",
                         "chu_de": ", ".join(jr(p["chu_de"])[:5]), "cong_dong": [cid], "vai_tro": "dien_gia", "nam": yr,
                         "nguon": jr(e["nguon"])[:2], "chua_xac_minh": bool(e["chua_xac_minh"])})
    for a in c.execute("SELECT * FROM award"):
        cid = "giai-" + a["id"]
        ws = c.execute("SELECT r.loai, r.vai_tro, coalesce(o.ten, p.ten) ten FROM role r LEFT JOIN org o ON r.loai='org' AND o.k=r.k "
                       "LEFT JOIN person p ON r.loai='person' AND p.k=r.k WHERE r.event_id=?", ("award:" + a["id"],)).fetchall()
        if not ws:
            continue
        comm.append({"id": cid, "ten": a["ten"], "loai": "giải thưởng", "linh_vuc": ", ".join(jr(a["linh_vuc"])),
                     "don_vi_dung_sau": a["to_chuc"] or "", "nguon": jr(a["nguon"])})
        for w in ws:
            yr = re.findall(r"20\d\d", w["vai_tro"])[:1]
            x = {"ten": w["ten"], "cong_dong": [cid], "vai_tro": "đoạt giải", "nam": yr, "nguon": jr(a["nguon"])[:2],
                 "chua_xac_minh": bool(a["chua_xac_minh"])}
            (comp if w["loai"] == "org" else kols).append(x)
    p = DATA / "xuat-lab035.json"
    p.write_text(json.dumps({"_ghi_chu": f"Xuất từ LAB037 ngày {TODAY}. Nạp bằng: python congdong.py seed <file này>",
                             "communities": comm, "companies": comp, "kols": kols}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"OK {p}: {len(comm)} sự kiện, {len(comp)} lượt tài trợ, {len(kols)} lượt diễn giả")


def cmd_all(args):
    if not args.no_fetch:
        cmd_scan(args)
        cmd_extract(args)
    cmd_score(args)
    args.days = 90
    cmd_insight(args)
    args.days = 120
    cmd_report(args)
    cmd_digest(args)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="LAB037 event radar")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    sp = sub.add_parser("seed"); sp.add_argument("files", nargs="+")
    sub.add_parser("scan")
    sub.add_parser("extract")
    sp = sub.add_parser("absorb"); sp.add_argument("files", nargs="+")
    sub.add_parser("score")
    sp = sub.add_parser("insight"); sp.add_argument("--days", type=int, default=90)
    sp = sub.add_parser("report"); sp.add_argument("--days", type=int, default=120)
    sub.add_parser("digest")
    sp = sub.add_parser("mark"); sp.add_argument("id"); sp.add_argument("stage"); sp.add_argument("note", nargs="*")
    sp = sub.add_parser("gan-nhom"); sp.add_argument("file")
    sp = sub.add_parser("rate"); sp.add_argument("ten"); sp.add_argument("diem"); sp.add_argument("ly_do", nargs="*")
    sp = sub.add_parser("phude"); sp.add_argument("url"); sp.add_argument("event_id", nargs="?")
    sub.add_parser("export-lab035")
    sp = sub.add_parser("import-lab022"); sp.add_argument("file")
    sp = sub.add_parser("all"); sp.add_argument("--no-fetch", action="store_true")
    a = ap.parse_args()
    {"init": cmd_init, "seed": cmd_seed, "scan": cmd_scan, "extract": cmd_extract, "absorb": cmd_absorb,
     "score": cmd_score, "insight": cmd_insight, "report": cmd_report, "digest": cmd_digest, "mark": cmd_mark,
     "rate": cmd_rate, "gan-nhom": cmd_gannhom, "phude": cmd_phude, "export-lab035": cmd_export35, "import-lab022": cmd_import22, "all": cmd_all}[a.cmd](a)


if __name__ == "__main__":
    main()
