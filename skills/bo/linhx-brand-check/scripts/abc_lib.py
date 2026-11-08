"""Phần dùng chung của chuẩn ABC: bảng sự thật, sinh câu hỏi, dò tên, thống kê.

Thư viện chuẩn Python. Chép ý từ potato (Wilson, ranh giới tên chạy với chữ có dấu)
và HeiGe-GEO-SEO (câu phủ định "không tìm thấy X" không tính là được nhắc).
"""

from __future__ import annotations

import json
import math
import re
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"

# ---------------------------------------------------------------- bảng sự thật

def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def save_json(path: str | Path, data: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(p)


def khong_dau(s: str) -> str:
    s = unicodedata.normalize("NFD", s or "").replace("đ", "d").replace("Đ", "D")
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def fold(s: str) -> str:
    return re.sub(r"\s+", " ", khong_dau(s).lower()).strip()


def domain_of(url: str) -> str:
    u = url if "://" in (url or "") else "https://" + (url or "")
    host = urlsplit(u).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def brand_names(facts: dict) -> list[str]:
    names = [facts.get("brand", "")] + list(facts.get("aliases", []))
    return [n for n in names if n and len(n.strip()) >= 2]


def competitor_names(facts: dict) -> list[dict]:
    out = []
    for c in facts.get("competitors", []):
        if isinstance(c, str):
            c = {"name": c}
        if c.get("name"):
            out.append({"name": c["name"], "aliases": c.get("aliases", []), "domain": c.get("domain", "")})
    return out

# ---------------------------------------------------------------- dò tên

# So trên chuỗi đã bỏ dấu (fold), nên mẫu viết không dấu.
_NEG = re.compile(r"(khong (tim thay|co thong tin|biet|ro)|chua (co|tim thay) thong tin|i (do not|don't) (know|have))")


def name_pattern(name: str) -> re.Pattern[str]:
    # Ranh giới bằng lookaround thay cho \b để tên có dấu, viết hoa, có dấu chấm vẫn khớp (potato matching.py).
    return re.compile(r"(?<![0-9a-z])" + re.escape(fold(name)) + r"(?![0-9a-z])")


def mentions(text: str, names: list[str]) -> bool:
    t = fold(text)
    return any(name_pattern(n).search(t) for n in names if n)


def first_pos(text: str, names: list[str]) -> int | None:
    t = fold(text)
    pos = [m.start() for n in names if n for m in [name_pattern(n).search(t)] if m]
    return min(pos) if pos else None


def negated_only(text: str, names: list[str]) -> bool:
    """Chỉ nhắc tên trong câu kiểu "không tìm thấy thông tin về X" → không tính là có mặt."""
    hits = [s for s in re.split(r"(?<=[.!?\n])", text or "") if mentions(s, names)]
    return bool(hits) and all(_NEG.search(fold(s)) for s in hits)

# ---------------------------------------------------------------- thống kê

def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def pct(k: float, n: float) -> int | None:
    return round(100 * k / n) if n else None


def rate(k: int, n: int) -> dict:
    lo, hi = wilson(k, n)
    return {"score": pct(k, n), "k": k, "n": n, "ci": [round(100 * lo), round(100 * hi)] if n else None}

# ---------------------------------------------------------------- câu hỏi

def _fill(text: str, v: dict) -> str:
    return re.sub(r"\{(\w+)\}", lambda m: str(v.get(m.group(1), m.group(0))), text)


def build_questions(facts: dict, goi: str = "N", bank: dict | None = None) -> list[dict]:
    """Sinh bộ câu hỏi từ mẫu ABC. goi: N (Nhanh), C (Chuẩn), S (Sâu: nhân biến thể)."""
    bank = bank or load_json(DATA / "bo-cau-hoi-abc.json")
    products = facts.get("products") or [{"name": facts.get("category", "")}]
    comps = competitor_names(facts) or [{"name": "thương hiệu dẫn đầu ngành"}]
    personas = facts.get("personas") or bank.get("bien_the", {}).get("persona", ["khách hàng phổ thông"])[:1]
    base = {
        "brand": facts.get("brand", ""), "category": facts.get("category", ""),
        "market": facts.get("market", "Việt Nam"), "city": facts.get("city", "TP. Hồ Chí Minh"),
        "need": facts.get("need", "dùng hằng ngày"), "budget": facts.get("budget", "mức trung bình"),
        "product": products[0].get("name", ""), "competitor": comps[0]["name"], "persona": personas[0],
    }
    base["brand_khong_dau"] = fold(base["brand"])
    base["category_khong_dau"] = fold(base["category"])
    custom = facts.get("abc", {}).get("cau_hoi_them", [])
    out: list[dict] = []
    for q in bank["cau_hoi"] + custom:
        if goi not in q.get("goi", "NCS"):
            continue
        variants = [dict(base)]
        if goi == "S":
            if "{persona}" in q["text"]:
                variants = [dict(base, persona=p) for p in personas[:3]]
            elif "{competitor}" in q["text"]:
                variants = [dict(base, competitor=c["name"]) for c in comps[:3]]
            elif "{product}" in q["text"]:
                variants = [dict(base, product=p.get("name", "")) for p in products[:2]]
        for i, v in enumerate(variants):
            qid = q["id"] if len(variants) == 1 else f"{q['id']}-{i + 1}"
            out.append({k: q[k] for k in ("loai", "buoc", "giai_doan", "chi_so") if k in q}
                       | {"id": qid, "text": _fill(q["text"], v), "goc": q["id"]})
    return out

# ---------------------------------------------------------------- nguồn

SOURCE_KINDS = [
    ("san", ["shopee.vn", "lazada.vn", "tiki.vn", "sendo.vn", "tiktok.com/shop", "bachhoaxanh.com", "thegioididong.com", "dienmayxanh.com", "fptshop.com.vn", "cellphones.com.vn"]),
    ("bao_chi", ["vnexpress.net", "tuoitre.vn", "thanhnien.vn", "cafef.vn", "cafebiz.vn", "vietnamnet.vn", "dantri.com.vn", "znews.vn", "zingnews.vn", "baomoi.com", "genk.vn", "vneconomy.vn", "nld.com.vn", "laodong.vn", "tienphong.vn", "vtv.vn", "brandsvietnam.com", "forbes.vn", "reuters.com", "bloomberg.com"]),
    ("review_dien_dan", ["voz.vn", "tinhte.vn", "reddit.com", "webtretho.com", "toplist.vn", "review", "danhgia", "trustpilot.com", "quora.com"]),
    ("mang_xa_hoi", ["facebook.com", "youtube.com", "tiktok.com", "instagram.com", "linkedin.com", "x.com", "twitter.com", "zalo.me"]),
    ("tham_khao", ["wikipedia.org", "wikidata.org", "masothue.com", "thuvienphapluat.vn", "dangkykinhdoanh.gov.vn"]),
]


def classify_source(url: str, facts: dict) -> str:
    d = domain_of(url)
    own = domain_of(facts.get("website", "")) if facts.get("website") else ""
    if own and (d == own or d.endswith("." + own)):
        return "cua_minh"
    for c in competitor_names(facts):
        cd = domain_of(c["domain"]) if c.get("domain") else ""
        if cd and (d == cd or d.endswith("." + cd)):
            return "doi_thu"
    full = url.lower()
    for kind, keys in SOURCE_KINDS:
        if any(k in full for k in keys):
            return kind
    return "khac"
