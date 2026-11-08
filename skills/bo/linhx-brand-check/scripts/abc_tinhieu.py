"""Vế tín hiệu (B1–B6): thương hiệu đã đưa cho máy những gì để kiểm.

B1 kiểm tự động trên website (dùng nen/aeoweb.py của ai-visibility-skill: robots cho bot AI, JSON-LD, sitemap).
B2 tự động một phần: tải từng kênh khai trong bảng sự thật và tìm các giá trị cốt lõi.
B3–B6 đọc từ <ws>/tin-hieu-tay.json do skill `kiem-tin-hieu` điền bằng tra web có link (điểm vẫn do code tính).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from abc_lib import fold, load_json  # noqa: E402
from nen import aeoweb  # noqa: E402

LIVE = {"ChatGPT-User", "OAI-SearchBot", "Claude-User", "Claude-SearchBot", "PerplexityBot",
        "Perplexity-User", "Bingbot", "Google-Extended"}


def b1_website(website: str) -> dict:
    base = aeoweb.base_url(website)
    robots = aeoweb.fetch(base + "/robots.txt")
    bots = [aeoweb.bot_status(robots.text if robots.ok else None, b) | {"hang": h, "vai_tro": r}
            for b, h, r in aeoweb.AI_BOTS]
    w = [(2 if x["bot"] in LIVE else 1, x["allowed"]) for x in bots]
    robots_score = sum(k for k, ok in w if ok) / sum(k for k, _ in w)
    home = aeoweb.fetch(base + "/")
    sig = aeoweb.extract_page_signals(home.text) if home.ok and home.text else {}
    types = set((sig.get("schema") or {}).get("types", []))
    llms = aeoweb.fetch(base + "/llms.txt")
    sitemap = aeoweb.fetch(base + "/sitemap.xml")
    html = home.text or ""
    checks = {
        "bot_ai_vao_duoc": (35 * robots_score, f"{sum(1 for x in bots if x['allowed'])}/{len(bots)} bot AI được phép"),
        "doc_duoc_khong_can_js": (15 if sig.get("word_count", 0) >= 150 else 0, f"{sig.get('word_count', 0)} từ đọc được trên trang chủ"),
        "schema_to_chuc": (15 if types & {"Organization", "Corporation", "LocalBusiness", "Store", "OnlineStore"} else 0, "JSON-LD Organization/LocalBusiness"),
        "schema_san_pham_gia": (10 if types & {"Product", "Offer", "Service", "AggregateOffer"} else 0, "JSON-LD Product/Offer/Service"),
        "schema_faq": (5 if "FAQPage" in types else 0, "JSON-LD FAQPage"),
        "sitemap": (10 if sitemap.ok and "<loc>" in (sitemap.text or "") else 0, "sitemap.xml"),
        "llms_txt": (5 if llms.ok and (llms.text or "").lstrip().startswith("#") else 0, "llms.txt (điểm nhỏ: bằng chứng hiệu quả yếu)"),
        "mo_ta_va_ngay": (5 if sig.get("meta_description") and ("dateModified" in html or "article:modified_time" in html) else
                          (3 if sig.get("meta_description") else 0), "meta description + ngày cập nhật"),
    }
    return {
        "score": round(sum(v for v, _ in checks.values())) if home.ok else None,
        "trang_chu": {"ok": home.ok, "status": home.status, "loi": home.error},
        "checks": {k: {"diem": round(v, 1), "ghi_chu": n} for k, (v, n) in checks.items()},
        "bot_bi_chan": [x["bot"] for x in bots if not x["allowed"]],
        "schema_types": sorted(types), "co_person": "Person" in types,
        "co_gia": bool(types & {"Offer", "AggregateOffer"}),
    }


def b2_kenh(facts: dict) -> dict:
    keys = [f for f in facts.get("facts", []) if f.get("kiem_kenh") and f.get("value")]
    keys = [{"id": "ten", "value": facts.get("brand", "")}] + keys
    rows, unreachable = [], []
    for ch in facts.get("channels", []):
        url = ch.get("url")
        if not url:
            continue
        r = aeoweb.fetch(url)
        if not r.ok or not r.text or len(aeoweb.strip_html(r.text)) < 200:
            unreachable.append({"kenh": ch.get("type"), "url": url, "loi": r.error or "nội dung ít (cần đăng nhập hoặc JS)"})
            continue
        text = fold(aeoweb.strip_html(r.text))
        hit = [k["id"] for k in keys if fold(str(k["value"]))[:60] in text]
        rows.append({"kenh": ch.get("type"), "url": url, "khop": hit, "thieu": [k["id"] for k in keys if k["id"] not in hit]})
    return {"tu_dong": rows, "can_kiem_tay": unreachable}


def score_manual(tay: dict, b1: dict, b2: dict) -> dict:
    out = {}
    # B2: tự động + tay
    pairs = [(len(r["khop"]), len(r["khop"]) + len(r["thieu"])) for r in b2["tu_dong"]]
    for r in tay.get("B2", {}).get("kenh", []):
        pairs.append((len(r.get("khop", [])), len(r.get("khop", [])) + len(r.get("lech", []))))
    k, n = sum(a for a, _ in pairs), sum(b for _, b in pairs)
    out["B2"] = {"score": round(100 * k / n) if n else None, "ghi_chu": f"{k}/{n} trường khớp trên {len(pairs)} kênh"}
    # B3: số nguồn độc lập, 11 nguồn ≈ 100 (nghiên cứu engine tiếng Trung: ≥11 nguồn chéo ~60% được chọn)
    b3 = tay.get("B3")
    if b3:
        ns = len(b3.get("nguon_doc_lap", []))
        s = 100 * math.log2(1 + ns) / math.log2(12) + (10 if b3.get("wikipedia") else 0)
        out["B3"] = {"score": min(100, round(s)), "ghi_chu": f"{ns} nguồn độc lập có link"}
    b4 = tay.get("B4")
    if b4 is not None or b1.get("co_person"):
        people = (b4 or {}).get("nguoi_dung_ten", [])
        with_profile = [p for p in people if p.get("ho_so_url")]
        s = (60 if with_profile else 0) + (20 if len(with_profile) >= 2 else 0) + (20 if b1.get("co_person") or (b4 or {}).get("schema_person") else 0)
        out["B4"] = {"score": s, "ghi_chu": f"{len(with_profile)} người có hồ sơ công khai"}
    b5 = tay.get("B5")
    if b5:
        s = 0.0
        if b5.get("diem_review"):
            s += max(0.0, (float(b5["diem_review"]) - 1) / 4) * 50
        if b5.get("so_review"):
            s += min(30.0, 30 * math.log10(1 + float(b5["so_review"])) / 3)
        s += 10 if b5.get("phan_hoi_khieu_nai") else 0
        s += 10 if b5.get("chinh_sach_doi_tra_cong_khai") else 0
        out["B5"] = {"score": round(s), "ghi_chu": f"review {b5.get('diem_review', '?')}/5, {b5.get('so_review', '?')} lượt"}
    b6 = tay.get("B6")
    if b6 is not None:
        items = ["feed_san_pham", "api_mcp", "zalo_mini_app", "thanh_toan_online", "gia_ton_kho_tren_web"]
        got = [i for i in items if b6.get(i) or (i == "gia_ton_kho_tren_web" and b1.get("co_gia"))]
        out["B6"] = {"score": 20 * len(got), "ghi_chu": "có: " + (", ".join(got) or "chưa có gì")}
    return out


def run(ws: Path, facts: dict, offline: bool = False) -> dict:
    b1 = b1_website(facts["website"]) if facts.get("website") and not offline else {"score": None, "checks": {}}
    b2 = b2_kenh(facts) if not offline else {"tu_dong": [], "can_kiem_tay": []}
    tay_p = ws / "tin-hieu-tay.json"
    tay = load_json(tay_p) if tay_p.exists() else {}
    res = {"B1": b1, "B2_chi_tiet": b2, **score_manual(tay, b1, b2)}
    res["B1"]["ghi_chu"] = "kiểm tự động website"
    return res
