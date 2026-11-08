"""LVN listening: bản ghi nhắc (jsonl) + hồ sơ md -> báo cáo md + feed json cho agent.

0 token: cảm xúc bằng từ điển có xử lý phủ định, câu nhận định sinh bằng luật.
Bản ghi theo chuẩn chung LINHX_CRAWLER: platform, url, author, text, published_at, metrics{like,comment,share}.

Chạy: python bao_cao.py <mentions.jsonl> <ho-so.md> <thu-muc-ra> [--den YYYY-MM-DD] [--so-ngay 7]
"""
import argparse, json, math, re, statistics, sys, unicodedata
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

DUONG = """tốt tuyệt hay đẹp ổn êm mượt bền rẻ thích hài_lòng xịn đáng chất_lượng
ưng ok yêu tiện tiết_kiệm ngon nhiệt_tình chuyên_nghiệp ấn_tượng mạnh_mẽ khen"""
# "nhanh" không nằm ở đây vì "pin xuống nhanh" là chê.split()
AM = """tệ kém xấu đắt lỗi hỏng chậm ồn kêu chán thất_vọng lừa bực tồi dở phốt
cháy nóng hết_pin khó_chịu tốn đểu ức_chế lag sập trễ""".split()
PHU_DINH = {"không", "chẳng", "chả", "chưa", "ko", "k", "khum", "hok", "đéo", "hông"}
GHEP = ["hài lòng", "thất vọng", "chất lượng", "tiết kiệm", "nhiệt tình", "chuyên nghiệp",
        "ấn tượng", "mạnh mẽ", "khó chịu", "hết pin", "ức chế", "giải quyết", "bảo hành", "trạm sạc", "tuy nhiên"]
DUNG = set("và là của có cho với thì mà này kia đã đang sẽ được bị một những các như ở tại từ đi ra vào lên xuống rồi nữa cũng vẫn còn rất quá lắm nhé nha ạ ơi thế vậy nào gì ai đó đây khi nếu vì nên để không chưa có_thể".split())


def chuan(s):
    s = unicodedata.normalize("NFC", s.lower())
    for g in GHEP:
        s = s.replace(g, g.replace(" ", "_"))
    return re.findall(r"[\wÀ-ỹ_]+", s)


def cam_xuc(text):
    """-1..1; phủ định đảo dấu từ cảm xúc trong 2 từ kế tiếp; vế sau "nhưng" nặng gấp đôi."""
    tu = chuan(text)
    diem, dao, he_so = 0, 0, 1
    for t in tu:
        if t in ("nhưng", "mà_lại", "tuy_nhiên"):
            diem, he_so = diem / 2, 2
            continue
        if t in PHU_DINH:
            dao = 2
            continue
        v = 1 if t in DUONG else -1 if t in AM else 0
        if v and dao:
            v = -v
        diem += v * he_so
        dao = max(0, dao - 1)
    return max(-1.0, min(1.0, diem / 2))


def doc_ho_so(path):
    hs = {"ten": "", "thuc_the": {}, "loai_tru": [], "khia_canh": {}, "nguong": {}}
    muc = None
    for dong in Path(path).read_text(encoding="utf-8").splitlines():
        if dong.startswith("# "):
            hs["ten"] = dong[2:].split(":", 1)[-1].strip()
        elif dong.startswith("## "):
            muc = dong[3:].strip().lower()
        elif dong.startswith("- ") and muc:
            noi_dung = dong[2:]
            if muc == "loại trừ":
                hs["loai_tru"] += [x.strip().lower() for x in noi_dung.split(",") if x.strip()]
                continue
            k, _, v = noi_dung.partition(":")
            tu = [x.strip().lower() for x in v.split(",") if x.strip()]
            if muc == "thực thể":
                hs["thuc_the"][k.strip()] = tu
            elif muc == "khía cạnh":
                hs["khia_canh"][k.strip()] = tu
            elif muc == "ngưỡng":
                hs["nguong"][k.strip()] = float(v)
    return hs


def co_tu(text, tu_list):
    t = " " + re.sub(r"\s+", " ", text.lower()) + " "
    return any(re.search(r"(?<![\wÀ-ỹ])" + re.escape(w) + r"(?![\wÀ-ỹ])", t) for w in tu_list)


def tuong_tac(m):
    me = m.get("metrics") or {}
    return int(me.get("like", 0)) + 2 * int(me.get("comment", 0)) + 3 * int(me.get("share", 0))


def nsr(ds):
    p = sum(1 for m in ds if m["cx"] > 0)
    n = sum(1 for m in ds if m["cx"] < 0)
    return round(100 * (p - n) / (p + n)) if p + n else 0


def phan_tich(mentions, hs, den, so_ngay):
    tu = den - timedelta(days=so_ngay - 1)
    truoc_tu = tu - timedelta(days=so_ngay)
    ky, ky_truoc = [], []
    for m in mentions:
        text = m.get("text", "")
        if not text or co_tu(text, hs["loai_tru"]):
            continue
        tt = [k for k, ws in hs["thuc_the"].items() if co_tu(text, ws)]
        if not tt:
            continue
        d = datetime.fromisoformat(m["published_at"][:10]).date()
        m = dict(m, ngay=d, thuc_the=tt, cx=cam_xuc(text), tt_diem=tuong_tac(m),
                 khia_canh=[k for k, ws in hs["khia_canh"].items() if co_tu(text, ws)])
        if tu <= d <= den:
            ky.append(m)
        elif truoc_tu <= d < tu:
            ky_truoc.append(m)

    theo_ngay = Counter(m["ngay"] for m in ky)
    chuoi = [theo_ngay.get(tu + timedelta(days=i), 0) for i in range(so_ngay)]
    tb = statistics.mean(chuoi) if chuoi else 0
    lc = statistics.pstdev(chuoi) if len(chuoi) > 1 else 0
    z_nguong = hs["nguong"].get("đột biến z", 2.0)
    dot_bien = [(tu + timedelta(days=i), c, round((c - tb) / lc, 1)) for i, c in enumerate(chuoi)
                if lc and (c - tb) / lc >= z_nguong]

    def nhom(key):
        g = defaultdict(list)
        for m in ky:
            for k in (m[key] if isinstance(m[key], list) else [m[key]]):
                g[k].append(m)
        return g

    def tu_noi(a, b):
        ca = Counter(t for m in a for t in set(chuan(m["text"])) if t not in DUNG and len(t) > 2)
        cb = Counter(t for m in b for t in set(chuan(m["text"])) if t not in DUNG and len(t) > 2)
        tat_ca = {w for ws in hs["thuc_the"].values() for w in ws}
        diem = {w: (c + 1) / (cb.get(w, 0) + 1) for w, c in ca.items() if c >= 3 and w not in tat_ca}
        return sorted(diem.items(), key=lambda x: -x[1])[:8]

    return {
        "tu": tu, "den": den, "ky": ky, "ky_truoc": ky_truoc, "chuoi": chuoi, "dot_bien": dot_bien,
        "thuc_the": nhom("thuc_the"), "nen_tang": nhom("platform"), "khia_canh": nhom("khia_canh"),
        "tu_noi": tu_noi(ky, ky_truoc),
    }


def cong_chat_luong(a, hs):
    loi = []
    toi_thieu = hs["nguong"].get("tối thiểu bài", 30)
    if len(a["ky"]) < toi_thieu:
        loi.append(f"Chỉ có {len(a['ky'])} bài khớp, dưới ngưỡng {int(toi_thieu)}.")
    ngay_trong = sum(1 for c in a["chuoi"] if c == 0)
    if ngay_trong > len(a["chuoi"]) // 2:
        loi.append(f"{ngay_trong}/{len(a['chuoi'])} ngày không có bài, có thể crawler đã dừng.")
    if a["ky"] and len(a["nen_tang"]) < 2:
        loi.append("Chỉ có một nền tảng, báo cáo sẽ lệch nguồn.")
    return loi


def doi(a, b):
    if not b:
        return "chưa có kỳ trước"
    return f"{'+' if a >= b else ''}{round(100 * (a - b) / b)}% so với kỳ trước"


def nhan_dinh(a):
    """Câu nhận định sinh bằng luật, không gọi LLM."""
    cau = []
    tt = sorted(a["thuc_the"].items(), key=lambda x: -len(x[1]))
    if tt:
        k, ds = tt[0]
        cau.append(f"{k} được nhắc nhiều nhất ({len(ds)} bài, {round(100*len(ds)/len(a['ky']))}% tổng), chỉ số cảm xúc ròng {nsr(ds)}.")
    xau = [(k, nsr(ds), len(ds)) for k, ds in a["khia_canh"].items() if len(ds) >= 5]
    xau.sort(key=lambda x: x[1])
    if xau and xau[0][1] < 0:
        cau.append(f"Khía cạnh bị chê nhiều nhất là {xau[0][0]} (NSR {xau[0][1]}, {xau[0][2]} bài).")
    for d, c, z in a["dot_bien"][:2]:
        top = sorted([m for m in a["ky"] if m["ngay"] == d], key=lambda m: -m["tt_diem"])[:1]
        goi_y = f", bài lan nhất: \"{top[0]['text'][:80]}\"" if top else ""
        cau.append(f"Ngày {d:%d/%m} có {c} bài, cao bất thường (z={z}){goi_y}.")
    if a["tu_noi"]:
        cau.append("Từ mới nổi so với kỳ trước: " + ", ".join(w.replace("_", " ") for w, _ in a["tu_noi"][:5]) + ".")
    return cau


def viet(a, hs, ra: Path):
    ra.mkdir(parents=True, exist_ok=True)
    ky, tr = a["ky"], a["ky_truoc"]
    L = [f"# Bản tin lắng nghe: {hs['ten']}", "",
         f"Kỳ {a['tu']:%d/%m} – {a['den']:%d/%m/%Y}. Sinh tự động, cảm xúc chấm bằng từ điển nên chỉ dùng để xem xu hướng.", "",
         "## Con số chính", "",
         f"- Tổng bài nhắc: **{len(ky)}** ({doi(len(ky), len(tr))})",
         f"- Chỉ số cảm xúc ròng (NSR): **{nsr(ky)}** (kỳ trước {nsr(tr) if tr else 'n/a'})",
         f"- Tổng tương tác quy đổi: {sum(m['tt_diem'] for m in ky):,}".replace(",", "."), "",
         "## Nhận định", ""] + [f"- {c}" for c in nhan_dinh(a)] + ["",
         "## Theo thực thể", "", "| Thực thể | Bài | Thị phần thảo luận | NSR |", "|---|---:|---:|---:|"]
    for k, ds in sorted(a["thuc_the"].items(), key=lambda x: -len(x[1])):
        L.append(f"| {k} | {len(ds)} | {round(100*len(ds)/len(ky))}% | {nsr(ds)} |")
    L += ["", "## Theo nền tảng", "", "| Nền tảng | Bài | NSR |", "|---|---:|---:|"]
    for k, ds in sorted(a["nen_tang"].items(), key=lambda x: -len(x[1])):
        L.append(f"| {k} | {len(ds)} | {nsr(ds)} |")
    L += ["", "## Theo khía cạnh", "", "| Khía cạnh | Bài | NSR |", "|---|---:|---:|"]
    for k, ds in sorted(a["khia_canh"].items(), key=lambda x: -len(x[1])):
        L.append(f"| {k} | {len(ds)} | {nsr(ds)} |")
    L += ["", "## Diễn biến theo ngày", "", "```"]
    mx = max(a["chuoi"]) or 1
    for i, c in enumerate(a["chuoi"]):
        L.append(f"{a['tu'] + timedelta(days=i):%d/%m} {'█' * round(20 * c / mx):<20} {c}")
    L += ["```", "", "## Bài lan rộng nhất", ""]
    for m in sorted(ky, key=lambda m: -m["tt_diem"])[:5]:
        L.append(f"- [{m['platform']}] {m['text'][:120]} ({m['tt_diem']} điểm) {m.get('url','')}")
    L += ["", "## Lời chê tiêu biểu", ""]
    for m in sorted([m for m in ky if m["cx"] < 0], key=lambda m: -m["tt_diem"])[:5]:
        L.append(f"- [{m['platform']}] {m['text'][:120]}")
    L += ["", "---", "Nguồn: bài công khai, không lưu tên người viết trong báo cáo."]
    (ra / "BAO-CAO.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    feed = {
        "ho_so": hs["ten"], "tu": str(a["tu"]), "den": str(a["den"]), "tong": len(ky), "tong_ky_truoc": len(tr),
        "nsr": nsr(ky), "nhan_dinh": nhan_dinh(a),
        "tin_hieu": [{"loai": "dot_bien", "ngay": str(d), "so_bai": c, "z": z} for d, c, z in a["dot_bien"]]
        + [{"loai": "tu_moi", "tu": w.replace("_", " "), "he_so": round(s, 1)} for w, s in a["tu_noi"]],
        "thuc_the": {k: {"bai": len(ds), "nsr": nsr(ds)} for k, ds in a["thuc_the"].items()},
        "khia_canh": {k: {"bai": len(ds), "nsr": nsr(ds)} for k, ds in a["khia_canh"].items()},
    }
    (ra / "feed.json").write_text(json.dumps(feed, ensure_ascii=False, indent=1), encoding="utf-8")
    return feed


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("mentions"); p.add_argument("ho_so"); p.add_argument("ra")
    p.add_argument("--den"); p.add_argument("--so-ngay", type=int, default=7)
    g = p.parse_args(argv)
    mentions = [json.loads(l) for l in Path(g.mentions).read_text(encoding="utf-8").splitlines() if l.strip()]
    den = date.fromisoformat(g.den) if g.den else max(datetime.fromisoformat(m["published_at"][:10]).date() for m in mentions)
    hs = doc_ho_so(g.ho_so)
    a = phan_tich(mentions, hs, den, g.so_ngay)
    loi = cong_chat_luong(a, hs)
    ra = Path(g.ra)
    if loi:
        ra.mkdir(parents=True, exist_ok=True)
        (ra / "CANH-BAO.md").write_text("# Chưa xuất báo cáo\n\n" + "\n".join(f"- {x}" for x in loi) + "\n", encoding="utf-8")
        print("CHAN:", *loi, sep="\n- ")
        return 2
    feed = viet(a, hs, ra)
    print(f"OK {feed['tong']} bài, NSR {feed['nsr']}, {len(feed['tin_hieu'])} tín hiệu -> {ra}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
