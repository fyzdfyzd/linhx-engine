"""Bước 0 linhx-report: tìm mẫu và clone style + structure từ một báo cáo đẹp.

Dùng:
  python clone.py do <mau.pdf> --ra <thu-muc-bao-cao> [--ten ten-mau] [--trang 1-40]
      Đo PDF mẫu → 00-mau/<ten>/ (ảnh từng trang, ảnh ghép), 00-mau/<ten>/so-do.json,
      00-style.json (token theo schema phong cách nhà, có 'do_tu'), 00-cau-truc-goi-y.json (đoán kiểu trang).
  python clone.py anh <anh1> [anh2 ...] --ra <thu-muc-bao-cao> --ten <ten-mau>
      Mẫu chỉ có ảnh xem trước (Envato, Dribbble, Behance, Issuu): rút bảng màu, tỷ lệ khổ, ảnh ghép.
  python clone.py so-sanh <goc.pdf> <trang> <bao-cao.pdf> <trang> --ra <png>
      Đặt trang gốc cạnh trang dựng lại, in độ lệch lề, cỡ chữ thân, màu chính.
  python clone.py luu <thu-muc-bao-cao> --ten <ten-phong-cach>
      Lưu 00-style.json + 00-cau-truc.json + ảnh so sánh thành phong cách nhà mới trong du-lieu/phong-cach/.

Chỉ đo và học tỷ lệ, lưới, nhịp. Không chép logo, ảnh, chữ hay font độc quyền của mẫu.
Chạy với python -I khi đọc PDF tải từ ngoài về (dữ liệu không tin cậy).
"""
import argparse
import collections
import json
import re
import shutil
import statistics
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
SERIF_GOI_Y = ("serif", "times", "georgia", "garamond", "bower", "playfair", "minion", "caslon", "tiempos", "merriweather",
               "lora", "baskerville", "bodoni", "didot", "publico", "freight", "sabon", "mckinsey", "charter", "cambria")


def ghi(p, d):
    Path(p).write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def hex_mau(c):
    return "#{:06X}".format(c & 0xFFFFFF)


def la_xam(h, nguong=18):
    r, g, b = int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)
    return max(r, g, b) - min(r, g, b) < nguong


def sang(h):
    r, g, b = int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255


def lam_tron_mau(h, buoc=24):
    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
    q = lambda x: min(255, round(x / buoc) * buoc)  # noqa: E731
    return "#{:02X}{:02X}{:02X}".format(q(r), q(g), q(b))


def la_serif(ten):
    t = ten.lower()
    if "sans" in t:
        return False
    return any(k in t for k in SERIF_GOI_Y)


def kieu_trang_doan(i, n, so_ky_tu, co_lon, co_anh, phu_anh, so_hinh_nhan, co_muc_luc):
    """Đoán kiểu trang T01–T23 bằng số đo. Claude xem ảnh và sửa lại trong 00-cau-truc.json."""
    if i == 0:
        return "T01"
    if i == n - 1 and so_ky_tu < 600:
        return "T23"
    if co_muc_luc:
        return "T04"
    if so_hinh_nhan:
        return "T12" if so_ky_tu < 1500 else "T13"
    if phu_anh > 0.45 and so_ky_tu < 900:
        return "T09"
    if co_lon >= 34 and so_ky_tu < 1800:
        return "T14"
    if so_ky_tu > 2600:
        return "T10"
    if co_anh:
        return "T13"
    return "T11"


def do_pdf(pdf, ra, ten, pham_vi, chinh_mau=False):
    import pymupdf
    ra = Path(ra)
    thu = ra / "00-mau" / ten
    thu.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(pdf)
    n = len(doc)
    a, b = 1, n
    if pham_vi:
        a, b = (int(x) for x in pham_vi.split("-"))
        b = min(b, n)
    W, H = doc[0].rect.width, doc[0].rect.height
    co_dem = collections.Counter()
    font_dem = collections.Counter()
    font_co = collections.defaultdict(collections.Counter)
    mau_chu = collections.Counter()
    mau_vec = collections.Counter()
    le_trai, le_phai, le_tren, le_duoi, x_dong = [], [], [], [], []
    gian = []
    trang = []
    nhan_hinh = collections.Counter()
    for i in range(a - 1, b):
        pg = doc[i]
        d = pg.get_text("dict")
        txt = pg.get_text()
        co_lon = 0
        bx = []
        for bl in d["blocks"]:
            if bl.get("type") != 0:
                continue
            for ln in bl["lines"]:
                sz = [s["size"] for s in ln["spans"] if s["text"].strip()]
                if not sz:
                    continue
                bx.append(ln["bbox"])
                for s in ln["spans"]:
                    t = s["text"].strip()
                    if not t:
                        continue
                    k = round(s["size"] * 2) / 2
                    co_dem[k] += len(t)
                    f = re.sub(r"^[A-Z]{6}\+", "", s["font"])
                    font_dem[f] += len(t)
                    font_co[f][k] += len(t)
                    mau_chu[hex_mau(s["color"])] += len(t)
                    co_lon = max(co_lon, s["size"])
        if bx:
            le_trai.append(min(x[0] for x in bx) / W)
            le_phai.append(1 - max(x[2] for x in bx) / W)
            le_tren.append(min(x[1] for x in bx) / H)
            le_duoi.append(1 - max(x[3] for x in bx) / H)
            x_dong += [round(x[0] / W, 2) for x in bx]
            ys = sorted({round(x[3], 1) for x in bx})
            gian += [ys[k + 1] - ys[k] for k in range(len(ys) - 1) if 0 < ys[k + 1] - ys[k] < 30]
        phu_anh = 0
        for im in pg.get_image_info():
            x0, y0, x1, y1 = im["bbox"]
            phu_anh += max(0, (x1 - x0) * (y1 - y0)) / (W * H)
        for dr in pg.get_drawings():
            if dr.get("fill") and dr["rect"].width * dr["rect"].height > 200:
                c = dr["fill"]
                h = "#{:02X}{:02X}{:02X}".format(*(int(v * 255) for v in c[:3]))
                mau_vec[h] += dr["rect"].width * dr["rect"].height
        nh = re.findall(r"(?im)^(exhibit|figure|hình|chart|biểu đồ)\s*\d+", txt)
        for x in nh:
            nhan_hinh[x.lower()] += 1
        co_ml = bool(re.search(r"(?i)\b(contents|mục lục|table of contents)\b", txt)) and i < 6
        trang.append({"so": i + 1, "ky_tu": len(txt), "co_lon": round(co_lon, 1), "phu_anh": round(phu_anh, 2),
                      "co_anh": phu_anh > 0.05 or len(pg.get_drawings()) > 30, "nhan_hinh": len(nh),
                      "kieu": kieu_trang_doan(i, n, len(txt), co_lon, phu_anh > 0.05 or len(pg.get_drawings()) > 30,
                                              phu_anh, len(nh), co_ml)})
        pg.get_pixmap(dpi=45).save(thu / f"p-{i + 1:03d}.png")
    # cỡ chữ thân: mode theo ký tự trong dải 7–14
    than = max((k for k in co_dem if 7 <= k <= 14), key=lambda k: co_dem[k], default=10)
    lon = sorted((k for k in co_dem if k > than + 1.5), key=lambda k: -co_dem[k])
    h2 = min(lon, default=than + 3, key=lambda k: abs(k - (than + 3)))
    h1 = max((k for k in lon if co_dem[k] > 30), default=than * 2.4)
    chu_thich = max((k for k in co_dem if 5.5 <= k < than - 0.9), key=lambda k: co_dem[k], default=7)
    f_than = max(font_dem, key=lambda f: font_co[f][than]) if font_dem else ""
    f_tieu = max(font_dem, key=lambda f: sum(v for k, v in font_co[f].items() if k >= h2)) if font_dem else ""
    mau_mau = [h for h, _ in mau_chu.most_common(40) if not la_xam(h)]
    vec = [lam_tron_mau(h) for h, _ in mau_vec.most_common(60) if not la_xam(h, 22) and 0.08 < sang(h) < 0.95]
    vec_dem = collections.Counter(vec)
    chinh = (mau_mau[0] if mau_mau else (vec_dem.most_common(1)[0][0] if vec_dem else "#0B1F3A"))
    nhan = next((h for h, _ in vec_dem.most_common() if h != lam_tron_mau(chinh)), chinh)
    toi_chu = [h for h, _ in mau_chu.most_common(10) if la_xam(h) and sang(h) < 0.35]
    phu_chu = [h for h, _ in mau_chu.most_common(15) if la_xam(h) and 0.35 <= sang(h) < 0.75]
    # số cột: đếm cụm x0 của dòng có tần suất cao
    cum = collections.Counter(x_dong)
    cot_x = [x for x, c in cum.most_common(6) if c > len(x_dong) * 0.08]
    cot = 2 if len([x for x in cot_x if x > 0.4]) and len([x for x in cot_x if x < 0.4]) else 1
    lt = statistics.median(le_trai) if le_trai else 0.08
    gd = statistics.median(gian) / than if gian else 1.35
    tt_kytu = statistics.median([t["ky_tu"] for t in trang]) * (595 * 842) / (W * H)
    do_tu = {"tep": Path(pdf).name, "trang_do": f"{a}-{b}", "kho_pt": [round(W), round(H)],
             "le_ty_le": {"trai": round(lt, 3), "phai": round(statistics.median(le_phai), 3) if le_phai else None,
                          "tren": round(statistics.median(le_tren), 3) if le_tren else None,
                          "duoi": round(statistics.median(le_duoi), 3) if le_duoi else None},
             "co_than": than, "co_h2": h2, "co_h1": h1, "co_chu_thich": chu_thich, "gian_dong": round(gd, 2),
             "font_than_goc": f_than, "font_tieu_de_goc": f_tieu, "font_dem": font_dem.most_common(6),
             "mau_chu": mau_chu.most_common(8), "mau_vector": vec_dem.most_common(8), "cot_x": cot_x,
             "ky_tu_trang_trung_vi_A4": round(tt_kytu), "nhan_hinh": dict(nhan_hinh)}
    kho = "a4" if abs(W / H - 0.707) < 0.02 else ("us-letter" if abs(W / H - 0.773) < 0.02 else "presentation-16-9")
    serif_tieu = la_serif(f_tieu)
    serif_than = la_serif(f_than)
    style = {
        "ten": f"Clone {ten}", "goc": f"Đo từ {Path(pdf).name}. Chỉ học tỷ lệ, lưới, nhịp; font thay bằng font mở đủ dấu.",
        "kho": kho,
        "le": {"tren": round(max(16, (do_tu['le_ty_le']['tren'] or 0.07) * 297 * 0.9)),
               "duoi": round(max(18, (do_tu['le_ty_le']['duoi'] or 0.07) * 297 * 0.9)),
               "ngoai": round(max(14, min(lt, 0.12) * 210))},
        "le_treo": round(max(0, lt - 0.12), 2) if cot == 1 and lt > 0.16 else 0,
        "cot": cot, "ranh_cot": 6,
        "font": {"tieu_de": "Source Serif 4" if serif_tieu else "Be Vietnam Pro",
                 "than": "Source Serif 4" if serif_than else "Be Vietnam Pro", "phu": "Be Vietnam Pro"},
        "co": {"than": min(11, max(9.2, than)), "chu_thich": max(6.5, chu_thich), "h1": min(34, max(22, h1)),
               "h2": min(16, max(11, h2)), "sapo": round(min(14, than * 1.3), 1), "hinh_tieu_de": round(min(12, than + 1), 1),
               "so_lon": 30, "bia": 40},
        "gian_dong": round(min(1.6, max(1.3, gd)), 2), "can_deu": cot > 1,
        "mau": {"chinh": toi_chu[0] if (toi_chu and sang(chinh) > 0.6) else chinh, "nhan": nhan,
                "nhan_toi": "#FFFFFF", "chu": toi_chu[0] if toi_chu else "#1F2933",
                "chu_phu": phu_chu[0] if phu_chu else "#5C677D", "nen_phu": "#F1F3F6", "ke": "#C9D1DC",
                "bieu_do": [chinh, nhan] + [h for h, _ in vec_dem.most_common(6) if h not in (chinh, nhan)][:3]},
        "hinh": {"nhan": "Hình", "vach_tren": True},
        "mo_chuong": "nua-trang" if any(t["kieu"] == "T09" for t in trang) else "chu-lon",
        "dropcap": False,
        "nguong": {"phu_chu": [0.18, 0.4], "ky_tu_trang_trung_vi": [int(tt_kytu * 0.7), int(tt_kytu * 1.2)],
                   "ty_le_trang_co_hinh": [0.4, 0.85]},
        "do_tu": do_tu,
    }
    while len(style["mau"]["bieu_do"]) < 5:
        style["mau"]["bieu_do"].append("#9AA5B1")
    ghi(thu / "so-do.json", {"do_tu": do_tu, "trang": trang})
    ghi(thu / "style.json", style)
    if chinh_mau:
        ghi(ra / "00-style.json", style)
    ghi(ra / "00-cau-truc-goi-y.json", {"mau": ten, "trang": [{"so": t["so"], "kieu": t["kieu"]} for t in trang],
                                         "ghi_chu": "Máy đoán. Claude xem ảnh 00-mau/<ten>/ rồi sửa vào 00-cau-truc.json."})
    anh_ghep(sorted(thu.glob("p-*.png")), thu / "tong-quan.jpg")
    print(json.dumps({k: do_tu[k] for k in ("kho_pt", "co_than", "co_h2", "co_h1", "gian_dong", "font_than_goc",
                                             "font_tieu_de_goc", "ky_tu_trang_trung_vi_A4")}, ensure_ascii=False))
    print("kiểu trang đoán:", collections.Counter(t["kieu"] for t in trang).most_common())
    print("đã ghi", thu / "style.json", "(và 00-style.json)" if chinh_mau else "", "00-cau-truc-goi-y.json,", thu / "tong-quan.jpg")


def anh_ghep(paths, ra, cot=8, toi_da=48):
    from PIL import Image
    paths = list(paths)[:toi_da]
    if not paths:
        return
    ims = [Image.open(p).convert("RGB") for p in paths]
    w = max(i.size[0] for i in ims)
    h = max(i.size[1] for i in ims)
    cot = min(cot, len(ims))
    hang = (len(ims) + cot - 1) // cot
    g = Image.new("RGB", (cot * (w + 8) + 8, hang * (h + 8) + 8), "#7d828a")
    for k, im in enumerate(ims):
        g.paste(im, (8 + (k % cot) * (w + 8), 8 + (k // cot) * (h + 8)))
    g.save(ra, quality=82)


def tu_anh(anh, ra, ten):
    from PIL import Image
    ra = Path(ra)
    thu = ra / "00-mau" / ten
    thu.mkdir(parents=True, exist_ok=True)
    dem = collections.Counter()
    ty_le = []
    for i, p in enumerate(anh, 1):
        im = Image.open(p).convert("RGB")
        ty_le.append(round(im.size[0] / im.size[1], 3))
        nho = im.copy()
        nho.thumbnail((360, 360))
        nho.save(thu / f"p-{i:03d}.png")
        q = im.resize((160, int(160 * im.size[1] / im.size[0]))).quantize(colors=8, method=Image.Quantize.MEDIANCUT)
        pal = q.getpalette()
        for idx, c in sorted(q.getcolors(), reverse=True):
            dem[lam_tron_mau("#{:02X}{:02X}{:02X}".format(*pal[idx * 3: idx * 3 + 3]))] += c
    anh_ghep(sorted(thu.glob("p-*.png")), thu / "tong-quan.jpg", cot=6)
    mau = [h for h, _ in dem.most_common(12)]
    out = {"mau": ten, "nguon": "anh-xem-truoc", "ty_le_khung": ty_le, "bang_mau": mau,
           "mau_nhan_goi_y": [h for h in mau if not la_xam(h, 30)][:3],
           "ghi_chu": "Ảnh xem trước không đo được font và cỡ chữ: Claude xem ảnh, ước lượng lưới, cỡ chữ, nhịp và ghi vào 00-cau-truc.json."}
    ghi(thu / "so-do.json", out)
    print(json.dumps(out, ensure_ascii=False))


def so_sanh(goc, tg, moi, tm, ra):
    import pymupdf
    from PIL import Image, ImageDraw
    a = pymupdf.open(goc)[tg - 1]
    b = pymupdf.open(moi)[tm - 1]
    tmp = Path(ra).with_suffix("")
    pa, pb = Path(str(tmp) + "-a.png"), Path(str(tmp) + "-b.png")
    a.get_pixmap(dpi=60).save(pa)
    b.get_pixmap(dpi=60).save(pb)
    ia, ib = Image.open(pa), Image.open(pb)
    h = max(ia.size[1], ib.size[1])
    g = Image.new("RGB", (ia.size[0] + ib.size[0] + 30, h + 30), "white")
    g.paste(ia, (10, 25))
    g.paste(ib, (ia.size[0] + 20, 25))
    dr = ImageDraw.Draw(g)
    dr.text((10, 6), f"MẪU · trang {tg}", fill="black")
    dr.text((ia.size[0] + 20, 6), f"DỰNG LẠI · trang {tm}", fill="black")
    g.save(ra)
    pa.unlink()
    pb.unlink()

    def m(pg):
        W, H = pg.rect.width, pg.rect.height
        d = pg.get_text("dict")
        bx, co = [], collections.Counter()
        for bl in d["blocks"]:
            if bl.get("type") == 0:
                for ln in bl["lines"]:
                    for s in ln["spans"]:
                        if s["text"].strip():
                            bx.append(ln["bbox"])
                            co[round(s["size"] * 2) / 2] += len(s["text"])
        if not bx:
            return {}
        return {"le_trai": round(min(x[0] for x in bx) / W, 3), "le_phai": round(1 - max(x[2] for x in bx) / W, 3),
                "le_tren": round(min(x[1] for x in bx) / H, 3), "co_than": co.most_common(1)[0][0]}
    ma, mb = m(a), m(b)
    lech = {k: round(mb.get(k, 0) - ma.get(k, 0), 3) for k in ma}
    print(json.dumps({"mau": ma, "dung_lai": mb, "lech": lech}, ensure_ascii=False))
    ghi(Path(ra).with_suffix(".json"), {"mau": ma, "dung_lai": mb, "lech": lech})


def luu(d, ten):
    d = Path(d)
    dich = GOC / "du-lieu" / "phong-cach" / ten
    dich.mkdir(parents=True, exist_ok=True)
    shutil.copy(d / "00-style.json", dich / "style.json")
    if (d / "00-cau-truc.json").exists():
        shutil.copy(d / "00-cau-truc.json", dich / "cau-truc.json")
    for p in (d / "00-so-sanh").glob("*.png"):
        shutil.copy(p, dich / p.name)
    print("đã lưu phong cách", dich)


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="lenh", required=True)
    a = sp.add_parser("do")
    a.add_argument("pdf")
    a.add_argument("--ra", required=True)
    a.add_argument("--ten", default="mau-chinh")
    a.add_argument("--trang")
    a.add_argument("--chinh", action="store_true", help="mẫu chính: ghi thêm 00-style.json ở gốc báo cáo")
    a = sp.add_parser("anh")
    a.add_argument("anh", nargs="+")
    a.add_argument("--ra", required=True)
    a.add_argument("--ten", required=True)
    a = sp.add_parser("so-sanh")
    a.add_argument("goc")
    a.add_argument("tg", type=int)
    a.add_argument("moi")
    a.add_argument("tm", type=int)
    a.add_argument("--ra", required=True)
    a = sp.add_parser("luu")
    a.add_argument("dir")
    a.add_argument("--ten", required=True)
    g = ap.parse_args()
    if g.lenh == "do":
        do_pdf(g.pdf, g.ra, g.ten, g.trang, g.chinh)
    elif g.lenh == "anh":
        tu_anh(g.anh, g.ra, g.ten)
    elif g.lenh == "so-sanh":
        Path(g.ra).parent.mkdir(parents=True, exist_ok=True)
        so_sanh(g.goc, g.tg, g.moi, g.tm, g.ra)
    elif g.lenh == "luu":
        luu(g.dir, g.ten)


if __name__ == "__main__":
    sys.exit(main())
