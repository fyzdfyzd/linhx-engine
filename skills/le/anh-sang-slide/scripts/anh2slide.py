#!/usr/bin/env python3
"""anh2slide: chuyển ảnh slide (GPT Image, Nano Banana...) thành PPTX và Claude slide chỉnh được.

Ba bước, có cổng duyệt chữ ở giữa (giống "bước 3" của PPT Master):
  doc    ảnh -> duyet.json   (OCR tìm vị trí dòng chữ, gom thành khối, đo cỡ chữ và màu)
         Claude mở từng ảnh, sửa trường "chu" cho đúng dấu tiếng Việt, đặt "dam": true nếu chữ đậm,
         xoá khối rác (logo, chữ trong hình). Đặt "da_duyet": true khi xong.
  xuat   duyet.json -> nền sạch (xoá chữ) + deck.pptx + claude-slide/*.html
  xem    dựng ảnh từ PPTX (LibreOffice) và ghép cạnh ảnh gốc để so

Cài: pip install rapidocr-onnxruntime opencv-python-headless python-pptx pillow
"""
import argparse, json, os, subprocess, sys, glob, shutil
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

FONT_MAC_DINH = "Inter"
W_IN, H_IN = 13.333, 7.5


def ocr_dong(path):
    from rapidocr_onnxruntime import RapidOCR
    eng = RapidOCR()
    r, _ = eng(path)
    out = []
    for b, t, c in r or []:
        xs = [p[0] for p in b]; ys = [p[1] for p in b]
        out.append({"x0": int(min(xs)), "y0": int(min(ys)), "x1": int(max(xs)), "y1": int(max(ys)), "ocr": t, "tin_cay": round(float(c), 2)})
    out.sort(key=lambda d: (d["y0"], d["x0"]))
    return out


def gom_khoi(dong):
    """Gom các dòng thẳng lề trái, cùng cỡ, sát nhau thành một khối (đoạn văn)."""
    khoi = []
    for d in sorted(dong, key=lambda d: (d["y0"], d["x0"])):
        h = d["y1"] - d["y0"]
        ghep = None
        for k in khoi:
            cuoi = k["dong"][-1]
            hk = cuoi["y1"] - cuoi["y0"]
            gan_doc = 0 <= d["y0"] - cuoi["y1"] < 0.9 * hk
            cung_co = 0.75 < h / max(hk, 1) < 1.33
            cung_le = abs(d["x0"] - cuoi["x0"]) < 0.6 * hk or abs((d["x0"] + d["x1"]) / 2 - (cuoi["x0"] + cuoi["x1"]) / 2) < 0.6 * hk
            if gan_doc and cung_co and cung_le:
                ghep = k; break
        if ghep:
            ghep["dong"].append(d)
        else:
            khoi.append({"dong": [d]})
    return khoi


def mau_chu(img, x0, y0, x1, y1):
    """Màu chữ = cụm màu khác nền nhất trong hộp; nền = trung vị viền ngoài hộp."""
    h, w = img.shape[:2]
    p = 4
    vung = img[max(0, y0 - p):min(h, y1 + p), max(0, x0 - p):min(w, x1 + p)].reshape(-1, 3).astype(np.float32)
    vien = np.concatenate([img[max(0, y0 - p):y0, x0:x1].reshape(-1, 3), img[y1:min(h, y1 + p), x0:x1].reshape(-1, 3)]).astype(np.float32)
    nen = np.median(vien, 0) if len(vien) else np.median(vung, 0)
    kc = np.linalg.norm(vung - nen, axis=1)
    chu = vung[kc >= np.percentile(kc, 93)]
    c = np.median(chu, 0) if len(chu) else np.array([0, 0, 0])
    b, g, r = [int(v) for v in c]
    return "#%02x%02x%02x" % (r, g, b), nen


def lenh_doc(anh, ra, kich_ban=None):
    os.makedirs(ra, exist_ok=True)
    slides = []
    for i, p in enumerate(anh, 1):
        img = cv2.imread(p)
        if img is None:
            sys.exit(f"Không đọc được ảnh {p}")
        H, W = img.shape[:2]
        dong = ocr_dong(p)
        ds = []
        for j, k in enumerate(gom_khoi(dong), 1):
            x0 = min(d["x0"] for d in k["dong"]); y0 = min(d["y0"] for d in k["dong"])
            x1 = max(d["x1"] for d in k["dong"]); y1 = max(d["y1"] for d in k["dong"])
            cao = float(np.median([d["y1"] - d["y0"] for d in k["dong"]]))
            mau, _ = mau_chu(img, x0, y0, x1, y1)
            ds.append({"id": f"s{i}k{j}", "hop": [x0, y0, x1, y1], "cao_dong_px": round(cao, 1),
                       "mau": mau, "dam": False, "can": "trai",
                       "ocr": "\n".join(d["ocr"] for d in k["dong"]),
                       "chu": "\n".join(d["ocr"] for d in k["dong"]),
                       "tin_cay": min(d["tin_cay"] for d in k["dong"])})
        slides.append({"so": i, "anh": os.path.relpath(os.path.abspath(p), os.path.abspath(ra)), "rong": W, "cao": H, "khoi": ds})
        print(f"slide {i}: {len(ds)} khối chữ, {len(dong)} dòng")
    d = {"da_duyet": False, "font": FONT_MAC_DINH, "slides": slides}
    if kich_ban:
        khop_kich_ban(d, kich_ban)
    with open(os.path.join(ra, "duyet.json"), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    lenh_ban_xem(d, ra)
    print("Tiếp: Claude sửa 'chu' trong duyet.json theo ảnh gốc (xem ban-duyet-*.png), rồi đặt da_duyet=true.")


def bo_dau(t):
    import unicodedata
    t = unicodedata.normalize("NFD", t.replace("đ", "d").replace("Đ", "D"))
    return "".join(c for c in t if unicodedata.category(c) != "Mn").lower()


def khop_kich_ban(d, kich_ban):
    """Ảnh GPT vẽ từ kịch bản ghost deck đã có: khớp chữ OCR (mất dấu) với dòng kịch bản để tự điền dấu.
    Khối khớp tốt (>=0.8) được đánh dấu tu_khop; khối còn lại Claude duyệt tay."""
    import difflib, re
    dong = [x.strip() for x in open(kich_ban, encoding="utf-8").read().splitlines() if x.strip()]
    chuan = lambda t: re.sub(r"[^a-z0-9]+", "", bo_dau(t))
    kb = [(x, chuan(x)) for x in dong]
    n_khop = n = 0
    for s in d["slides"]:
        for k in s["khoi"]:
            ra_dong = []
            ok = True
            for o in k["ocr"].split("\n"):
                n += 1
                co, best = max(((difflib.SequenceMatcher(None, chuan(o), c).ratio(), x) for x, c in kb), default=(0, None))
                if co >= 0.8:
                    ra_dong.append(best); n_khop += 1
                else:
                    ra_dong.append(o); ok = False
            if not ok:
                # kịch bản viết cả câu, ảnh ngắt dòng khác: khớp cả khối rồi chia lại theo số từ mỗi dòng OCR
                o_dong = k["ocr"].split("\n")
                co, best = max(((difflib.SequenceMatcher(None, chuan(k["ocr"]), c).ratio(), x) for x, c in kb), default=(0, None))
                if co >= 0.8:
                    # chia câu có dấu theo tỉ lệ độ dài ký tự của từng dòng OCR
                    tu = best.split(); dai = [len(chuan(o)) for o in o_dong]; tong = max(sum(dai), 1)
                    tong_kb = sum(len(chuan(t)) for t in tu); moc = []; c = 0
                    for m in dai[:-1]:
                        c += m; moc.append(c * tong_kb / tong)
                    ra_dong = [[] for _ in o_dong]; c = 0; j = 0
                    for t in tu:
                        giua = c + len(chuan(t)) / 2
                        while j < len(moc) and giua > moc[j]:
                            j += 1
                        ra_dong[j].append(t); c += len(chuan(t))
                    ra_dong = [" ".join(x) for x in ra_dong if x]
                    ok = True
            k["chu"] = "\n".join(ra_dong); k["tu_khop"] = ok
    kh = [k for s in d["slides"] for k in s["khoi"]]
    tk = sum(1 for k in kh if k.get("tu_khop"))
    print(f"Khớp kịch bản: {tk}/{len(kh)} khối tự điền dấu; còn {len(kh) - tk} khối cần Claude duyệt (tu_khop=false).")


def lenh_ban_xem(d, ra):
    """Ảnh gốc có khung đánh số từng khối, để Claude và Linh đối chiếu khi duyệt chữ."""
    for s in d["slides"]:
        im = Image.open(os.path.join(ra, s["anh"]) if not os.path.isabs(s["anh"]) else s["anh"]).convert("RGB")
        dr = ImageDraw.Draw(im)
        for k in s["khoi"]:
            x0, y0, x1, y1 = k["hop"]
            dr.rectangle([x0, y0, x1, y1], outline=(255, 0, 80), width=2)
            dr.text((x0, max(0, y0 - 12)), k["id"], fill=(255, 0, 80))
        im.save(os.path.join(ra, f"ban-duyet-{s['so']:02d}.png"))


def xoa_chu(img, hop_list):
    """Xoá chữ: nền phẳng thì tô màu viền; nền có hoạ tiết thì inpaint vùng nét chữ."""
    out = img.copy()
    H, W = img.shape[:2]
    mask_inp = np.zeros((H, W), np.uint8)
    for (x0, y0, x1, y1) in hop_list:
        p = max(3, int((y1 - y0) * 0.15))
        a0, b0, a1, b1 = max(0, x0 - p), max(0, y0 - p), min(W, x1 + p), min(H, y1 + p)
        r = 3
        vien = np.concatenate([
            img[max(0, b0 - r):b0, a0:a1].reshape(-1, 3), img[b1:min(H, b1 + r), a0:a1].reshape(-1, 3),
            img[b0:b1, max(0, a0 - r):a0].reshape(-1, 3), img[b0:b1, a1:min(W, a1 + r)].reshape(-1, 3)]).astype(np.float32)
        if len(vien) == 0:
            continue
        nen = np.median(vien, 0)
        lech = float(np.median(np.linalg.norm(vien - nen, axis=1)))
        if os.environ.get("A2S_DEBUG"):
            print("xoa_chu", (x0, y0, x1, y1), round(lech, 1))
        if lech < 10:
            out[b0:b1, a0:a1] = nen.astype(np.uint8)
        else:
            vung = img[b0:b1, a0:a1].astype(np.float32)
            kc = np.linalg.norm(vung - nen, axis=2)
            m = (kc > max(18, lech * 2.0)).astype(np.uint8) * 255
            dd = max(7, int((y1 - y0) * 0.12) | 1)
            m = cv2.dilate(m, np.ones((dd, dd), np.uint8))
            mask_inp[b0:b1, a0:a1] = np.maximum(mask_inp[b0:b1, a0:a1], m)
    if mask_inp.any():
        out = cv2.inpaint(out, mask_inp, 7, cv2.INPAINT_TELEA)
    return out


_font_cache = {}


def tep_font(ten, dam):
    k = (ten, dam)
    if k not in _font_cache:
        try:
            r = subprocess.run(["fc-match", "-f", "%{file}", f"{ten}:{'bold' if dam else 'regular'}"], capture_output=True, text=True)
            _font_cache[k] = r.stdout.strip() or None
        except FileNotFoundError:  # Windows: không có fc-match
            goc = os.path.join(os.environ.get("WINDIR", "C:/Windows"), "Fonts")
            ung = [f for f in glob.glob(os.path.join(goc, "*.ttf")) if ten.lower().replace(" ", "") in os.path.basename(f).lower()]
            _font_cache[k] = (sorted(ung, key=lambda f: ("bold" in f.lower()) != dam) or [os.path.join(goc, "arial.ttf")])[0]
    return _font_cache[k]


def em_px(k, font):
    """Cỡ chữ (px trong ảnh): ưu tiên khớp bề ngang dòng dài nhất với hộp OCR, chặn bằng ước lượng theo chiều cao."""
    theo_cao = k["cao_dong_px"] / 1.22
    f = tep_font(font, bool(k.get("dam")))
    if not f:
        return theo_cao
    ft = ImageFont.truetype(f, 100)
    rong = max(ft.getlength(d) for d in k["chu"].split("\n"))
    if rong <= 0:
        return theo_cao
    theo_ngang = 100.0 * (k["hop"][2] - k["hop"][0]) / rong
    return theo_ngang if 0.6 * theo_cao < theo_ngang < 1.7 * theo_cao else theo_cao


def doc_duyet(duyet):
    d = json.load(open(duyet, encoding="utf-8"))
    goc = os.path.dirname(os.path.abspath(duyet))
    for s in d["slides"]:  # đường dẫn ảnh tương đối tính từ thư mục chứa duyet.json
        if not os.path.isabs(s["anh"]):
            s["anh"] = os.path.join(goc, s["anh"])
    return d


def lenh_xuat(duyet, ra, ep=False):
    d = doc_duyet(duyet)
    if not d.get("da_duyet") and not ep:
        sys.exit("Chưa duyệt chữ: sửa duyet.json rồi đặt da_duyet=true (hoặc --ep để xuất thử).")
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
    os.makedirs(os.path.join(ra, "nen"), exist_ok=True)
    os.makedirs(os.path.join(ra, "claude-slide"), exist_ok=True)
    prs = Presentation(); prs.slide_width = Inches(W_IN); prs.slide_height = Inches(H_IN)
    so_hop = 0
    for s in d["slides"]:
        img = cv2.imread(s["anh"]); H, W = img.shape[:2]
        khoi = [k for k in s["khoi"] if k.get("chu", "").strip() and not k.get("bo")]
        nen = xoa_chu(img, [k["hop"] for k in khoi])
        pnen = os.path.join(ra, "nen", f"nen-{s['so']:02d}.png"); cv2.imwrite(pnen, nen)
        sl = prs.slides.add_slide(prs.slide_layouts[6])
        sl.shapes.add_picture(pnen, 0, 0, prs.slide_width, prs.slide_height)
        kx = prs.slide_width / W; ky = prs.slide_height / H
        html = []
        for k in khoi:
            x0, y0, x1, y1 = k["hop"]
            em = em_px(k, d.get("font", FONT_MAC_DINH))
            pt = k.get("co_pt") or max(6, round(em * 540.0 / H, 1))
            n = len(k["chu"].split("\n"))
            n_ocr = k["ocr"].count("\n") + 1
            # khoảng cách dòng đo từ ảnh nếu khối có nhiều dòng, mặc định 1.2em
            buoc = (y1 - y0 - k["cao_dong_px"]) / (n - 1) if n > 1 else 1.2 * em
            buoc = min(max(buoc, 1.0 * em), 2.2 * em)
            rong = (x1 - x0) * 1.10 + 0.3 * em; cao = (n - 1) * buoc + 1.2 * em + 0.2 * em
            ox = {"giua": x0 - 0.05 * (x1 - x0) - 0.15 * em, "phai": x0 - 0.10 * (x1 - x0) - 0.3 * em}.get(k.get("can"), x0)
            oy = (y0 + y1) / 2 - cao / 2
            tb = sl.shapes.add_textbox(Emu(int(ox * kx)), Emu(int(oy * ky)), Emu(int(rong * kx)), Emu(int(cao * ky)))
            tf = tb.text_frame; tf.word_wrap = True
            tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
            tf.vertical_anchor = MSO_ANCHOR.TOP
            c = k["mau"].lstrip("#")
            for i, dong in enumerate(k["chu"].split("\n")):
                para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                para.alignment = {"giua": PP_ALIGN.CENTER, "phai": PP_ALIGN.RIGHT}.get(k.get("can"), PP_ALIGN.LEFT)
                para.line_spacing = Pt(buoc * 540.0 / H)
                run = para.add_run(); run.text = dong
                run.font.size = Pt(pt); run.font.bold = bool(k.get("dam")); run.font.name = d.get("font", FONT_MAC_DINH)
                run.font.color.rgb = RGBColor.from_string(c.upper())
            so_hop += 1
            # Claude slide 1920x1080
            sx = 1920 / W
            html.append(f'<div style="position:absolute;left:{ox*sx:.0f}px;top:{oy*sx:.0f}px;width:{rong*sx:.0f}px;'
                        f'font-size:{em*sx:.1f}px;line-height:{buoc*sx:.1f}px;color:{k["mau"]};font-weight:{700 if k.get("dam") else 400};'
                        f'text-align:{ {"giua":"center","phai":"right"}.get(k.get("can"),"left") };white-space:pre">'
                        + k["chu"].replace("&", "&amp;").replace("<", "&lt;") + "</div>")
        shutil.copy(pnen, os.path.join(ra, "claude-slide", f"nen-{s['so']:02d}.png"))
        with open(os.path.join(ra, "claude-slide", f"slide-{s['so']:02d}.html"), "w", encoding="utf-8") as f:
            f.write(f'<section style="position:relative;width:1920px;height:1080px;overflow:hidden;'
                    f'background:url(nen-{s["so"]:02d}.png) center/cover;font-family:\'{d.get("font", FONT_MAC_DINH)}\',sans-serif">\n'
                    + "\n".join(html) + "\n</section>\n")
    p = os.path.join(ra, "deck.pptx"); prs.save(p)
    print(f"Đã xuất {p}: {len(d['slides'])} slide, {so_hop} hộp chữ chỉnh được; claude-slide/ có {len(d['slides'])} trang HTML.")


def lenh_xem(duyet, ra):
    d = doc_duyet(duyet)
    pptx = os.path.join(ra, "deck.pptx")
    tmp = os.path.join(ra, "_xem"); os.makedirs(tmp, exist_ok=True)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", tmp, pptx], check=True, capture_output=True)
    subprocess.run(["pdftoppm", "-png", "-r", "110", os.path.join(tmp, "deck.pdf"), os.path.join(tmp, "p")], check=True)
    trang = sorted(glob.glob(os.path.join(tmp, "p-*.png")))
    for s, t in zip(d["slides"], trang):
        a = Image.open(s["anh"]).convert("RGB"); b = Image.open(t).convert("RGB").resize(a.size)
        c = Image.new("RGB", (a.width * 2 + 20, a.height), "white"); c.paste(a, (0, 0)); c.paste(b, (a.width + 20, 0))
        c.save(os.path.join(ra, f"so-sanh-{s['so']:02d}.png"))
        print(f"slide {s['so']}: so-sanh-{s['so']:02d}.png (trái: ảnh gốc, phải: PPTX dựng lại)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="lenh", required=True)
    a = sub.add_parser("doc"); a.add_argument("anh", nargs="+"); a.add_argument("--ra", default="anh2slide-ra"); a.add_argument("--kich-ban", help="tệp chữ của deck (mỗi dòng một câu) để tự điền dấu")
    b = sub.add_parser("xuat"); b.add_argument("duyet"); b.add_argument("--ra", default=None); b.add_argument("--ep", action="store_true")
    c = sub.add_parser("xem"); c.add_argument("duyet"); c.add_argument("--ra", default=None)
    g = ap.parse_args()
    if g.lenh == "doc":
        anh = sorted(sum([glob.glob(x) if any(ch in x for ch in "*?") else [x] for x in g.anh], []))
        lenh_doc(anh, g.ra, g.kich_ban)
    elif g.lenh == "xuat":
        lenh_xuat(g.duyet, g.ra or os.path.dirname(os.path.abspath(g.duyet)), g.ep)
    else:
        lenh_xem(g.duyet, g.ra or os.path.dirname(os.path.abspath(g.duyet)))
