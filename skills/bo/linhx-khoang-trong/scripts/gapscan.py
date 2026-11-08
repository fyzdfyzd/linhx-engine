#!/usr/bin/env python3
"""gapscan.py: phần đếm, gom, chấm của radar khoảng trống độc giả (LAB029).

Chỉ dùng thư viện chuẩn. Embedding đa ngôn ngữ là tuỳ chọn (cờ --embed, cần sentence-transformers).
Mọi lệnh chạy trong THƯ MỤC LƯỢT CHẠY (mặc định thư mục hiện tại, hoặc --thu-muc / biến GAP_RUN).

Lệnh theo bước:
  init                      tạo cau-hinh.json mẫu
  nhap <tệp>...             B1 nạp dữ liệu adapter (.jsonl) hoặc snapshot cũ của vault
                            (substack scan.txt, medium raw.json.gz) vào 01-hien-tuong.jsonl
  tin-hieu                  B2a chỉ số cầu/cung theo tag, bài vượt trung vị, bài nhỏ mà nổ → 02-tin-hieu.json
                            + 02-mau-cho-claude.md (tít top mỗi tag để Claude gom cụm nhu cầu)
  gan-cum                   B2b áp 02-cum.json (Claude viết) → 02-nhu-cau.json
  dau-vao-b3                B3 xuất 03-dau-vao.md: kênh và bài thắng mỗi cụm để Claude chưng cất
  quy-mo                    B4 → 04-quy-mo.json
  so-vn [--embed]           B5 so với dữ liệu Việt Nam → 05-viet-nam.json
  cham                      B6 điểm khoảng trống → 06-khoang-trong.json + .md
  kiem <b1..b6>             cổng kiểm một bước
  tom-tat                   in tóm tắt lượt chạy
"""
import argparse, gzip, json, math, os, re, statistics, sys, time, unicodedata
from collections import defaultdict, Counter
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

NOW = time.time()
DAY = 86400

CAU_HINH_MAU = {
    "_ghi_chu": "Cấu hình một lượt chạy LAB029. Sửa tay được.",
    "chu_de": "toàn cảnh",
    "nen_tang_vn": {
        "_ghi_chu": "trọng số độ phủ khi soi Việt Nam; nền tảng chưa quét vẫn tính vào mẫu số độ phủ dữ liệu",
        "facebook": 3, "youtube": 3, "tiktok": 2, "substack": 1, "spiderum": 1, "linkedin": 1,
        "threads": 1, "podcast": 1, "sach": 2, "bao": 1
    },
    "nguong_kenh_lon": {"_mac_dinh": 50000, "facebook": 100000, "youtube": 100000, "tiktok": 200000,
                         "substack": 10000, "spiderum": 5000, "linkedin": 20000, "podcast": 0, "sach": 0},
    "nguong_kenh_vua": {"_mac_dinh": 10000, "substack": 5000, "spiderum": 2000, "linkedin": 5000},
    "nguong_phu_du_lieu": 0.6,
    "so_bai_toi_thieu_moi_tag": 30,
    "so_bai_toi_thieu_moi_cum": 5,
    "follower_nho": 5000,
    "nguong_tieu_bieu_vuot": 3.0,
    "cua_so_tang_truong_ngay": 28,
    "tag_bo_qua": ["about-me", "editor-picks", "editors-pick", "infinite-library", "medium", "writer", "writers",
                   "blogging", "writing-prompts", "full-frame", "publication", "submission", "newsletter",
                   "writing-community", "medium-partner-program", "authors", "poem", "poetry", "flash-fiction",
                   "short-story", "fiction", "short-fiction"]
}

TRONG_SO = {  # quy đổi tương tác về một số; so sánh chỉ trong cùng nguồn
    "medium": {"clap": 1, "comment": 5},
    "substack": {"like": 1, "comment": 5, "share": 10},
    "_mac_dinh": {"like": 1, "comment": 5, "share": 10, "clap": 1, "view": 0.01},
}


# ---------- tiện ích ----------
def home(args):
    p = Path(getattr(args, "thu_muc", None) or os.environ.get("GAP_RUN") or ".").resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p


def doc_json(p, mac_dinh=None):
    p = Path(p)
    if not p.exists():
        return mac_dinh
    return json.loads(p.read_text(encoding="utf-8"))


def ghi_json(p, d):
    Path(p).write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def cau_hinh(h):
    c = dict(CAU_HINH_MAU)
    c.update(doc_json(h / "cau-hinh.json", {}) or {})
    return c


def doc_hien_tuong(h):
    p = h / "01-hien-tuong.jsonl"
    if not p.exists():
        sys.exit("Chưa có 01-hien-tuong.jsonl. Chạy `nhap` trước.")
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def trung_vi(a):
    a = [x for x in a if x is not None]
    return statistics.median(a) if a else 0


def phan_vi(a, q):
    a = sorted(a)
    if not a:
        return 0
    return a[min(len(a) - 1, int(q * len(a)))]


def khong_dau(s):
    s = (s or "").lower().replace("đ", "d")
    s = unicodedata.normalize("NFD", s)
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn")


def tuong_tac(r):
    sd = r.get("so_do") or {}
    w = TRONG_SO.get(r.get("nguon"), TRONG_SO["_mac_dinh"])
    return sum(w.get(k, 0) * (sd.get(k) or 0) for k in w)


def co_khop(text_kd, tu_khoa):
    """tu_khoa đã bỏ dấu; khớp theo ranh giới từ."""
    for k in tu_khoa:
        if re.search(r"(?<![a-z0-9])" + re.escape(k) + r"(?![a-z0-9])", text_kd):
            return k
    return None


def kich_co(r):
    sd = r.get("so_do") or {}
    return max(sd.get("subscriber") or 0, sd.get("follower") or 0)


# ---------- B0 ----------
def cmd_init(a):
    h = home(a)
    p = h / "cau-hinh.json"
    if p.exists():
        print("Đã có", p)
    else:
        ghi_json(p, CAU_HINH_MAU)
        print("Tạo", p)


# ---------- B1 nhập ----------
def ban_ghi(**k):
    k.setdefault("thi_truong", "quoc-te")
    k.setdefault("loai", "bai")
    k.setdefault("the", [])
    k.setdefault("so_do", {})
    return k


def nhap_substack_scan(path):
    """snapshot substack_scan.js cũ (khối #A #V #W #S, phân cách ¦)."""
    b, cur = defaultdict(list), None
    for l in Path(path).read_text(encoding="utf-8").replace("\r", "").split("\n"):
        if l in ("#M", "#A", "#V", "#W", "#S"):
            cur = l
            continue
        if cur and l:
            b[cur].append(l.split("¦"))
    n = lambda x: int(re.sub(r"[^\d]", "", x or "") or 0)
    out = []
    for key, tt in (("#A", "quoc-te"), ("#V", "vn")):
        for r in b[key]:
            lb = [x.split("#")[0].split("/")[0] for x in (r[8] or "").split() if "/" in x]
            out.append(ban_ghi(nguon="substack", thi_truong=tt, loai="kenh", id="sub:" + r[3],
                               tieu_de=r[4], tac_gia=r[2], kenh=r[4], kenh_id=r[3], url=r[5],
                               mo_ta=r[18] if len(r) > 18 else "", the=sorted(set(lb)),
                               bac_tra_phi=r[7] if "paid" in (r[7] or "").lower() else "",
                               so_do={"subscriber": n(r[6])}, hang=r[8]))
    for r in b["#S"]:
        vi = bool(re.search(r"[đơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]", r[1], re.I))
        out.append(ban_ghi(nguon="substack", thi_truong="vn" if vi else "quoc-te", id="subp:" + r[-1],
                           tieu_de=r[1], url=r[2], tac_gia=r[3], kenh=r[4], ngay=r[5],
                           so_do={"like": n(r[6]), "comment": n(r[7]), "share": n(r[8])}))
    return out


def nhap_medium_raw(path):
    """snapshot medium_scan.js cũ: posts + authors.homepagePostsConnection."""
    d = json.load(gzip.open(path, "rt", encoding="utf-8"))
    out, seen = [], set()

    def them(p, creator):
        if not p or p["id"] in seen:
            return
        seen.add(p["id"])
        col = p.get("collection") or {}
        out.append(ban_ghi(nguon="medium", id="med:" + p["id"], tieu_de=p.get("title", ""),
                           mo_ta=((p.get("extendedPreviewContent") or {}).get("subtitle") or ""),
                           url=p.get("mediumUrl") or ("https://medium.com/p/" + p["id"]), tac_gia=creator.get("name", ""),
                           tac_gia_id=creator.get("id", ""), kenh=col.get("name") or "",
                           ngay=time.strftime("%Y-%m-%d", time.gmtime((p.get("firstPublishedAt") or 0) / 1000)),
                           the=[t["normalizedTagSlug"] for t in (p.get("tags") or [])],
                           so_do={"clap": p.get("clapCount") or 0, "comment": (p.get("postResponses") or {}).get("count") or 0,
                                  "follower": ((creator.get("socialStats") or {}).get("followerCount") or 0)},
                           nguon_phu=p.get("src") or []))

    for p in d.get("posts", {}).values():
        them(p, p.get("creator") or {})
    for a in d.get("authors", {}).values():
        for p in (a.get("homepagePostsConnection") or {}).get("posts", []):
            them(p, a)
    return out


def cmd_nhap(a):
    h = home(a)
    dich = h / "01-hien-tuong.jsonl"
    cu = {}
    if dich.exists() and not a.moi:
        for l in dich.read_text(encoding="utf-8").splitlines():
            if l.strip():
                r = json.loads(l)
                cu[r["id"]] = r
    them = 0
    for f in a.tep:
        f = Path(f)
        if f.name.endswith(".json.gz"):
            rs = nhap_medium_raw(f)
        elif f.suffix == ".txt":
            rs = nhap_substack_scan(f)
        else:
            rs = [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
        loi = 0
        for r in rs:
            if not r.get("id") or not r.get("nguon"):
                loi += 1
                continue
            r = ban_ghi(**r)
            if a.thi_truong:
                r["thi_truong"] = a.thi_truong
            r.setdefault("ngay_quet", time.strftime("%Y-%m-%d"))
            r["tt"] = tuong_tac(r)
            cu[r["id"]] = {**cu.get(r["id"], {}), **r}
            them += 1
        print(f"{f.name}: {len(rs)} bản ghi, bỏ {loi} thiếu id/nguon")
    with dich.open("w", encoding="utf-8") as fo:
        for r in cu.values():
            fo.write(json.dumps(r, ensure_ascii=False) + "\n")
    c = Counter((r["thi_truong"], r["nguon"], r["loai"]) for r in cu.values())
    print(f"01-hien-tuong.jsonl: {len(cu)} bản ghi")
    for k, v in sorted(c.items()):
        print("  ", "/".join(k), v)


# ---------- B2a tín hiệu ----------
def cmd_tin_hieu(a):
    h = home(a)
    ch = cau_hinh(h)
    R = [r for r in doc_hien_tuong(h) if r["thi_truong"] == "quoc-te" and r["loai"] == "bai"]
    theo_nguon = defaultdict(list)
    for r in R:
        theo_nguon[r["nguon"]].append(r)
    ket = {"nguon": {}, "tag": [], "bai_vuot": [], "nho_ma_no": []}
    for ng, rs in theo_nguon.items():
        tts = [r["tt"] for r in rs]
        med = trung_vi(tts) or 1
        p90 = phan_vi(tts, 0.9)
        ket["nguon"][ng] = {"so_bai": len(rs), "trung_vi_tt": med, "p90_tt": p90}
        # theo tag
        tg = defaultdict(list)
        for r in rs:
            for t in set(r.get("the") or []):
                tg[t].append(r)
        bo = set(ch.get("tag_bo_qua", []))
        for t, xs in tg.items():
            if len(xs) < ch["so_bai_toi_thieu_moi_tag"] or t in bo:
                continue
            m = trung_vi([x["tt"] for x in xs])
            ket["tag"].append({"nguon": ng, "tag": t, "so_bai": len(xs), "trung_vi_tt": m,
                               "chi_so_cau_cung": round(m / med, 2),
                               "so_tac_gia": len({x.get("tac_gia") for x in xs})})
        # bài vượt trung vị của chính tác giả
        ta = defaultdict(list)
        for r in rs:
            ta[r.get("tac_gia_id") or r.get("tac_gia")].append(r)
        for k, xs in ta.items():
            if len(xs) < 4 or not k:
                continue
            m = max(trung_vi([x["tt"] for x in xs]), 0.25 * med, 1)  # chặn tác giả gần như không có tương tác
            for x in xs:
                if x["tt"] / m >= ch["nguong_tieu_bieu_vuot"] and x["tt"] >= med:
                    ket["bai_vuot"].append({"id": x["id"], "nguon": ng, "tieu_de": x["tieu_de"], "url": x.get("url"),
                                            "tac_gia": x.get("tac_gia"), "he_so": round(x["tt"] / m, 1), "tt": x["tt"]})
        for r in rs:
            f = (r.get("so_do") or {}).get("follower")
            if f and f < ch["follower_nho"] and r["tt"] >= p90:
                ket["nho_ma_no"].append({"id": r["id"], "nguon": ng, "tieu_de": r["tieu_de"], "url": r.get("url"),
                                         "tac_gia": r.get("tac_gia"), "follower": f, "tt": r["tt"]})
    ket["tag"].sort(key=lambda x: -x["chi_so_cau_cung"])
    ket["bai_vuot"].sort(key=lambda x: -x["he_so"])
    ket["nho_ma_no"].sort(key=lambda x: -x["tt"])
    ghi_json(h / "02-tin-hieu.json", ket)

    # bản cho Claude đọc
    by_id = {r["id"]: r for r in R}
    L = [f"# Mẫu để gom cụm nhu cầu ({time.strftime('%Y-%m-%d')})", "",
         "Chỉ số cầu/cung = trung vị tương tác của tag ÷ trung vị cả nguồn. Trên 1 là độc giả thưởng nhiều hơn mức cung.", ""]
    for ng, inf in ket["nguon"].items():
        L.append(f"- {ng}: {inf['so_bai']} bài, trung vị tương tác {inf['trung_vi_tt']:g}")
    L += ["", "## Tag cầu cao (tối đa 40)", "", "| Nguồn | Tag | Bài | Tác giả | Cầu/cung |", "|---|---|---|---|---|"]
    tags_top = [t for t in ket["tag"]][:40]
    for t in tags_top:
        L.append(f"| {t['nguon']} | {t['tag']} | {t['so_bai']} | {t['so_tac_gia']} | {t['chi_so_cau_cung']} |")
    L += ["", "## Tag đông bài nhất (để thấy chỗ cung thừa)", ""]
    for t in sorted(ket["tag"], key=lambda x: -x["so_bai"])[:15]:
        L.append(f"- {t['nguon']}/{t['tag']}: {t['so_bai']} bài, cầu/cung {t['chi_so_cau_cung']}")
    L += ["", "## Tít top theo tag cầu cao", ""]
    for t in tags_top[:25]:
        xs = sorted([r for r in R if r["nguon"] == t["nguon"] and t["tag"] in (r.get("the") or [])], key=lambda r: -r["tt"])[:10]
        L.append(f"### {t['nguon']}/{t['tag']} (cầu/cung {t['chi_so_cau_cung']})")
        for r in xs:
            L.append(f"- {r['tt']:g} · {r['tieu_de'][:110]} · {r.get('tac_gia','')}")
        L.append("")
    L += ["## Bài vượt trung vị của chính tác giả (top 40)", ""]
    for b in ket["bai_vuot"][:40]:
        L.append(f"- ×{b['he_so']} · {b['tieu_de'][:110]} · {b['tac_gia']}")
    L += ["", "## Tác giả nhỏ mà bài nổ (top 30)", ""]
    for b in ket["nho_ma_no"][:30]:
        L.append(f"- {b['tt']:g} (follower {b['follower']}) · {b['tieu_de'][:110]} · {b['tac_gia']}")
    kenh = sorted([r for r in doc_hien_tuong(h) if r["thi_truong"] == "quoc-te" and r["loai"] == "kenh"], key=lambda r: -kich_co(r))[:60]
    if kenh:
        L += ["", "## Kênh lớn nhất (top 60)", ""]
        for r in kenh:
            L.append(f"- {kich_co(r):,} · {r['nguon']} · {r.get('kenh') or r['tieu_de']} · {r.get('bac_tra_phi','')} · {(r.get('mo_ta') or '')[:90]}")
    (h / "02-mau-cho-claude.md").write_text("\n".join(L), encoding="utf-8")
    print(f"02-tin-hieu.json: {len(ket['tag'])} tag, {len(ket['bai_vuot'])} bài vượt, {len(ket['nho_ma_no'])} bài nhỏ mà nổ")
    print("02-mau-cho-claude.md: đọc file này rồi viết 02-cum.json (xem references/schema.md)")


# ---------- B2b gán cụm ----------
def doc_cum(h):
    c = doc_json(h / "02-cum.json")
    if not c:
        sys.exit("Chưa có 02-cum.json (Claude viết sau khi đọc 02-mau-cho-claude.md).")
    cums = c["cum"] if isinstance(c, dict) else c
    for x in cums:
        x["_the"] = {t.lower() for t in x.get("the", [])}
        x["_en"] = [khong_dau(k) for k in x.get("tu_khoa_en", [])]
        x["_vi"] = [khong_dau(k) for k in x.get("tu_khoa_vi", [])]
        x["_vi_dau"] = [unicodedata.normalize("NFC", k.lower()) for k in x.get("tu_khoa_vi", [])]
    return cums


CO_DAU = re.compile(r"[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]")


def khop_cum(r, cum, ngon_ngu):
    goc = unicodedata.normalize("NFC", " ".join([r.get("tieu_de") or "", r.get("mo_ta") or "", r.get("kenh") or ""]).lower())
    if r.get("loai") == "bai" and set(t.lower() for t in r.get("the") or []) & cum["_the"]:
        return "tag"
    if ngon_ngu == "vi" and CO_DAU.search(goc):
        # văn bản có dấu: so có dấu, tránh "giàu" khớp "giấu", "ai" khớp mọi câu
        k = next((k for k in cum["_vi_dau"] if re.search(r"(?<!\w)" + re.escape(k) + r"(?!\w)", goc)), None)
        return ("tu:" + k) if k else None
    kws = cum["_vi"] if ngon_ngu == "vi" else cum["_en"]
    k = co_khop(khong_dau(goc), kws)
    return ("tu:" + k) if k else None


def cmd_gan_cum(a):
    h = home(a)
    ch = cau_hinh(h)
    R = doc_hien_tuong(h)
    cums = doc_cum(h)
    th = doc_json(h / "02-tin-hieu.json", {"nguon": {}, "bai_vuot": [], "nho_ma_no": []})
    vuot = {b["id"] for b in th["bai_vuot"]}
    nho = {b["id"] for b in th["nho_ma_no"]}
    QT = [r for r in R if r["thi_truong"] == "quoc-te"]
    out = []
    t28 = ch["cua_so_tang_truong_ngay"]
    for c in cums:
        bai = [r for r in QT if r["loai"] == "bai" and khop_cum(r, c, "en")]
        kenh = [r for r in QT if r["loai"] == "kenh" and khop_cum(r, c, "en")]
        cc = []
        for ng, inf in th["nguon"].items():
            xs = [r["tt"] for r in bai if r["nguon"] == ng]
            if xs:
                cc.append((len(xs), trung_vi(xs) / (inf["trung_vi_tt"] or 1)))
        chi_so = round(sum(n * v for n, v in cc) / sum(n for n, _ in cc), 2) if cc else 0

        def tuoi(r):
            try:
                return (NOW - time.mktime(time.strptime(r["ngay"][:10], "%Y-%m-%d"))) / DAY
            except Exception:
                return None
        moi = sum(1 for r in bai if (tuoi(r) or 1e9) <= t28)
        truoc = sum(1 for r in bai if t28 < (tuoi(r) or 1e9) <= 2 * t28)
        tg = defaultdict(float)
        for r in bai:
            tg[r.get("tac_gia")] += r["tt"]
        out.append({
            "id": c["id"], "ten": c.get("ten"), "nhu_cau": c.get("nhu_cau"),
            "so_bai": len(bai), "so_tac_gia": len({r.get('tac_gia') for r in bai}),
            "chi_so_cau_cung": chi_so,
            "so_bai_vuot": sum(1 for r in bai if r["id"] in vuot),
            "so_bai_nho_ma_no": sum(1 for r in bai if r["id"] in nho),
            "bai_28_ngay": moi, "bai_28_ngay_truoc": truoc,
            "top_bai": [{"tieu_de": r["tieu_de"], "url": r.get("url"), "tac_gia": r.get("tac_gia"), "nguon": r["nguon"], "tt": r["tt"]}
                        for r in sorted(bai, key=lambda r: -r["tt"])[:12]],
            "top_tac_gia": [{"tac_gia": k, "tong_tt": v} for k, v in sorted(tg.items(), key=lambda x: -x[1])[:10]],
            "top_kenh": [{"kenh": r.get("kenh") or r["tieu_de"], "nguon": r["nguon"], "url": r.get("url"), "co": kich_co(r),
                          "bac_tra_phi": r.get("bac_tra_phi", ""), "mo_ta": (r.get("mo_ta") or "")[:140]}
                         for r in sorted(kenh, key=lambda r: -kich_co(r))[:12]],
            "_kenh_ids": [r["id"] for r in kenh],
        })
    ghi_json(h / "02-nhu-cau.json", out)
    for x in out:
        print(f"{x['id']} {x['ten']}: {x['so_bai']} bài, {len(x['_kenh_ids'])} kênh, cầu/cung {x['chi_so_cau_cung']}, vượt {x['so_bai_vuot']}")
    thieu = [x["id"] for x in out if x["so_bai"] < ch["so_bai_toi_thieu_moi_cum"]]
    if thieu:
        print("CẢNH BÁO cụm dưới", ch["so_bai_toi_thieu_moi_cum"], "bài:", ", ".join(thieu), "(thêm tag/từ khoá hoặc gộp cụm)")


# ---------- B3 ----------
def cmd_dau_vao_b3(a):
    h = home(a)
    N = doc_json(h / "02-nhu-cau.json") or sys.exit("Chạy gan-cum trước.")
    L = ["# Đầu vào B3: ai đang thắng ở mỗi cụm", "",
         "Với mỗi cụm: chọn 3 đến 5 kênh, mở 2 đến 3 bài top của họ, chưng cất 3 tầng (nhận thức, chiến lược, nội dung). Mỗi nhận định trỏ về link.", ""]
    for x in N:
        L.append(f"## {x['id']} {x['ten']}")
        L.append(f"Nhu cầu: {x.get('nhu_cau','')}")
        L.append("")
        L.append("Kênh lớn:")
        for k in x["top_kenh"][:8]:
            L.append(f"- {k['co']:,} · {k['nguon']} · {k['kenh']} · {k['bac_tra_phi']} · {k['url']} · {k['mo_ta']}")
        L.append("Tác giả có tổng tương tác cao trong mẫu:")
        for t in x["top_tac_gia"][:6]:
            L.append(f"- {t['tac_gia']} ({t['tong_tt']:g})")
        L.append("Bài top:")
        for b in x["top_bai"][:8]:
            L.append(f"- {b['tt']:g} · {b['tieu_de'][:110]} · {b['tac_gia']} · {b['url']}")
        L.append("")
    (h / "03-dau-vao.md").write_text("\n".join(L), encoding="utf-8")
    print("03-dau-vao.md đã ghi. Claude viết 03-nguoi-thang.md.")


# ---------- B4 ----------
def cmd_quy_mo(a):
    h = home(a)
    R = {r["id"]: r for r in doc_hien_tuong(h)}
    N = doc_json(h / "02-nhu-cau.json") or sys.exit("Chạy gan-cum trước.")
    out = []
    for x in N:
        ks = [R[i] for i in x["_kenh_ids"] if i in R]
        tong = sum(kich_co(k) for k in ks)
        tra_phi = [k for k in ks if k.get("bac_tra_phi")]
        moi, truoc = x["bai_28_ngay"], x["bai_28_ngay_truoc"]
        tang = (moi - truoc) / truoc if truoc else (1.0 if moi else 0.0)
        cau = (0.35 * min(1, math.log10(tong + 1) / 7)
               + 0.35 * min(1, x["chi_so_cau_cung"] / 3)
               + 0.15 * min(1, math.log2(1 + x["so_bai_vuot"]) / 4)
               + 0.15 * min(1, x["so_tac_gia"] / 50))
        out.append({"id": x["id"], "ten": x["ten"], "so_kenh": len(ks), "tong_nguoi_theo": tong,
                    "so_kenh_tra_phi": len(tra_phi),
                    "bac_tra_phi": Counter(k["bac_tra_phi"] for k in tra_phi).most_common(),
                    "tang_truong_28_ngay": round(tang, 2), "cau_nguon": round(cau, 3),
                    "ghi_chu": "số subscriber Substack là số làm tròn công khai"})
    ghi_json(h / "04-quy-mo.json", out)
    for o in out:
        print(f"{o['id']}: {o['so_kenh']} kênh, {o['tong_nguoi_theo']:,} người theo, {o['so_kenh_tra_phi']} kênh trả phí, cầu nguồn {o['cau_nguon']}")


# ---------- B5 ----------
def cmd_so_vn(a):
    h = home(a)
    ch = cau_hinh(h)
    R = doc_hien_tuong(h)
    cums = doc_cum(h)
    VN = [r for r in R if r["thi_truong"] == "vn"]
    nen = {k: v for k, v in ch["nen_tang_vn"].items() if not k.startswith("_")}
    da_quet = {r["nguon"] for r in VN}
    tong_w = sum(nen.values()) or 1
    phu_du_lieu = sum(w for k, w in nen.items() if k in da_quet) / tong_w
    lon, vua = ch["nguong_kenh_lon"], ch["nguong_kenh_vua"]

    sim = None
    if a.embed:
        try:
            from sentence_transformers import SentenceTransformer, util
            m = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
            desc = [f"{c.get('ten','')}. {c.get('nhu_cau','')}" for c in cums]
            E1 = m.encode(desc, convert_to_tensor=True)
            E2 = m.encode([f"{r.get('tieu_de','')} {r.get('mo_ta','')}" for r in VN], convert_to_tensor=True)
            sim = util.cos_sim(E2, E1).cpu().numpy()
            print("Đã dùng embedding đa ngôn ngữ (ngưỡng 0,62).")
        except Exception as e:
            print("Bỏ qua --embed:", e)

    out = []
    for ci, c in enumerate(cums):
        theo = {}
        for ng in sorted(set(nen) | da_quet):
            xs = []
            for ri, r in enumerate(VN):
                if r["nguon"] != ng:
                    continue
                why = khop_cum(r, c, "vi") or khop_cum(r, c, "en")
                if not why and sim is not None and sim[ri][ci] >= 0.62:
                    why = f"emb:{sim[ri][ci]:.2f}"
                if why:
                    xs.append((r, why))
            if ng not in da_quet:
                muc = "chua_quet"
            elif not xs:
                muc = "open"
            else:
                L_ = lon.get(ng, lon["_mac_dinh"])
                V_ = vua.get(ng, vua["_mac_dinh"])
                co = [kich_co(r) for r, _ in xs]
                hang = [int(m.group(1)) for r, _ in xs for m in [re.search(r"#(\d+)", r.get("hang") or "")] if m]
                if L_ == 0:  # bảng xếp hạng (podcast, sách): lọt top 20 là đã có người chiếm
                    phu = bool(hang) and min(hang) <= 20
                else:
                    phu = max(co) >= L_ or sum(1 for x in co if V_ and x >= V_) >= 3
                if phu:
                    muc = "covered"
                else:
                    muc = "thin"
            theo[ng] = {"muc": muc, "so_khop": len(xs),
                        "lon_nhat": [{"ten": r.get("kenh") or r.get("tieu_de"), "co": kich_co(r), "tt": r.get("tt", 0),
                                      "url": r.get("url"), "khop": why}
                                     for r, why in sorted(xs, key=lambda t: -(kich_co(t[0]) or t[0].get("tt", 0)))[:5]]}
        diem = {"open": 0.1, "thin": 0.45, "covered": 0.9}
        w = sum(nen.get(k, 1) for k, v in theo.items() if v["muc"] != "chua_quet")
        phu = sum(nen.get(k, 1) * diem[v["muc"]] for k, v in theo.items() if v["muc"] != "chua_quet") / w if w else None
        out.append({"id": c["id"], "ten": c.get("ten"), "phu_vn": None if phu is None else round(phu, 3), "nen_tang": theo})
    ghi_json(h / "05-viet-nam.json", {"do_phu_du_lieu": round(phu_du_lieu, 2), "nen_tang_da_quet": sorted(da_quet), "cum": out})
    print(f"Độ phủ dữ liệu VN: {phu_du_lieu:.0%} (đã quét: {', '.join(sorted(da_quet)) or 'chưa có'})")
    if phu_du_lieu < ch["nguong_phu_du_lieu"]:
        print(f"CẢNH BÁO dưới {ch['nguong_phu_du_lieu']:.0%}: B6 chỉ ra BẢN NHÁP. Quét thêm: "
              + ", ".join(k for k in nen if k not in da_quet))
    for o in out:
        tom = " ".join(f"{k}:{v['muc']}" for k, v in o["nen_tang"].items())
        print(f"{o['id']} phủ VN {o['phu_vn']} | {tom}")


# ---------- B6 ----------
def cmd_cham(a):
    h = home(a)
    ch = cau_hinh(h)
    cums = {c["id"]: c for c in doc_cum(h)}
    Q = {x["id"]: x for x in doc_json(h / "04-quy-mo.json") or sys.exit("Chạy quy-mo trước.")}
    V = doc_json(h / "05-viet-nam.json") or sys.exit("Chạy so-vn trước.")
    nhap = V["do_phu_du_lieu"] < ch["nguong_phu_du_lieu"]
    rows = []
    for v in V["cum"]:
        q = Q.get(v["id"], {})
        c = cums.get(v["id"], {})
        cg = c.get("chuyen_giao", 0.6)
        phu = v["phu_vn"] if v["phu_vn"] is not None else 0.5
        td = max(0.8, min(1.3, 1 + 0.3 * q.get("tang_truong_28_ngay", 0)))
        diem = q.get("cau_nguon", 0) * cg * (1 - phu) * td
        rows.append({"id": v["id"], "ten": v["ten"], "diem": round(100 * diem, 1), "cau_nguon": q.get("cau_nguon"),
                     "chuyen_giao": cg, "ly_do_chuyen_giao": c.get("ly_do_chuyen_giao", ""), "phu_vn": v["phu_vn"],
                     "thoi_diem": round(td, 2),
                     "muc_vn": {k: x["muc"] for k, x in v["nen_tang"].items()}})
    rows.sort(key=lambda r: -r["diem"])
    ghi_json(h / "06-khoang-trong.json", {"ban_nhap": nhap, "do_phu_du_lieu": V["do_phu_du_lieu"], "xep_hang": rows})
    L = [f"# Khoảng trống độc giả ({ch.get('chu_de')}, {time.strftime('%Y-%m-%d')})", ""]
    if nhap:
        L += [f"> **BẢN NHÁP.** Độ phủ dữ liệu Việt Nam {V['do_phu_du_lieu']:.0%}, dưới ngưỡng {ch['nguong_phu_du_lieu']:.0%}. "
              "Mức \"open\" ở đây có thể chỉ là chưa quét. Không dùng để quyết định.", ""]
    L += ["Điểm = 100 × cầu nguồn × chuyển giao được × (1 − phủ VN) × thời điểm.", "",
          "| # | Cụm | Điểm | Cầu nguồn | Chuyển giao | Phủ VN | Thời điểm | Mức theo nền tảng VN |", "|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rows, 1):
        muc = ", ".join(f"{k} {v}" for k, v in r["muc_vn"].items() if v != "chua_quet") or "chưa quét"
        L.append(f"| {i} | {r['id']} {r['ten']} | **{r['diem']}** | {r['cau_nguon']} | {r['chuyen_giao']} | {r['phu_vn']} | {r['thoi_diem']} | {muc} |")
    L += ["", "Lý do chuyển giao (Claude ghi ở 02-cum.json):", ""]
    for r in rows:
        if r["ly_do_chuyen_giao"]:
            L.append(f"- {r['id']}: {r['ly_do_chuyen_giao']}")
    (h / "06-khoang-trong.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:len(rows) + 8]))


# ---------- cổng kiểm ----------
def cmd_kiem(a):
    h = home(a)
    ch = cau_hinh(h)
    b = a.buoc.lower()
    loi = []
    if b == "b1":
        R = doc_hien_tuong(h)
        c = Counter((r["thi_truong"], r["nguon"]) for r in R)
        if not any(k[0] == "quoc-te" for k in c):
            loi.append("không có dữ liệu quốc tế")
        thieu_url = sum(1 for r in R if not r.get("url"))
        if thieu_url > 0.2 * len(R):
            loi.append(f"{thieu_url} bản ghi thiếu url")
        print(dict(c))
    elif b == "b2":
        N = doc_json(h / "02-nhu-cau.json") or []
        for x in N:
            if x["so_bai"] < ch["so_bai_toi_thieu_moi_cum"]:
                loi.append(f"{x['id']} chỉ {x['so_bai']} bài")
            if not any(t.get("url") for t in x["top_bai"]):
                loi.append(f"{x['id']} không có link bằng chứng")
        for c in doc_cum(h):
            if not c.get("_vi"):
                loi.append(f"{c['id']} thiếu tu_khoa_vi (B5 sẽ không so được)")
    elif b == "b3":
        p = h / "03-nguoi-thang.md"
        if not p.exists():
            loi.append("chưa có 03-nguoi-thang.md")
        else:
            t = p.read_text(encoding="utf-8")
            for c in doc_cum(h):
                if c["id"] not in t:
                    loi.append(f"thiếu cụm {c['id']}")
            if t.count("http") < 3 * len(doc_cum(h)):
                loi.append("ít link bằng chứng (cần ≥ 3 mỗi cụm)")
    elif b == "b4":
        if not (h / "04-quy-mo.json").exists():
            loi.append("chưa có 04-quy-mo.json")
    elif b == "b5":
        V = doc_json(h / "05-viet-nam.json")
        if not V:
            loi.append("chưa có 05-viet-nam.json")
        elif V["do_phu_du_lieu"] < ch["nguong_phu_du_lieu"]:
            loi.append(f"độ phủ dữ liệu VN {V['do_phu_du_lieu']:.0%} < {ch['nguong_phu_du_lieu']:.0%}")
    elif b == "b6":
        K = doc_json(h / "06-khoang-trong.json")
        if not K:
            loi.append("chưa có 06-khoang-trong.json")
        elif K["ban_nhap"]:
            loi.append("06 là bản nháp")
        for c in doc_cum(h):
            if not c.get("ly_do_chuyen_giao"):
                loi.append(f"{c['id']} thiếu lý do chuyển giao")
    else:
        sys.exit("bước: b1..b6")
    if loi:
        print("CHƯA QUA", b.upper())
        for l in loi:
            print("  -", l)
        sys.exit(1)
    print("QUA", b.upper())


def cmd_tom_tat(a):
    h = home(a)
    for f in sorted(h.iterdir()):
        if f.is_file():
            print(f"{f.name:28s} {f.stat().st_size:>9,} B")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--thu-muc", help="thư mục lượt chạy")
    sp = ap.add_subparsers(dest="lenh", required=True)
    sp.add_parser("init").set_defaults(f=cmd_init)
    p = sp.add_parser("nhap")
    p.add_argument("tep", nargs="+")
    p.add_argument("--thi-truong", choices=["quoc-te", "vn"], help="ép thị trường cho mọi bản ghi của tệp")
    p.add_argument("--moi", action="store_true", help="xoá dữ liệu cũ trong 01 trước khi nạp")
    p.set_defaults(f=cmd_nhap)
    sp.add_parser("tin-hieu").set_defaults(f=cmd_tin_hieu)
    sp.add_parser("gan-cum").set_defaults(f=cmd_gan_cum)
    sp.add_parser("dau-vao-b3").set_defaults(f=cmd_dau_vao_b3)
    sp.add_parser("quy-mo").set_defaults(f=cmd_quy_mo)
    p = sp.add_parser("so-vn")
    p.add_argument("--embed", action="store_true")
    p.set_defaults(f=cmd_so_vn)
    sp.add_parser("cham").set_defaults(f=cmd_cham)
    p = sp.add_parser("kiem")
    p.add_argument("buoc")
    p.set_defaults(f=cmd_kiem)
    sp.add_parser("tom-tat").set_defaults(f=cmd_tom_tat)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
