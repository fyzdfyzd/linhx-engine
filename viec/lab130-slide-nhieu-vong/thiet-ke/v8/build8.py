#!/usr/bin/env python3
"""Dựng deck CSMO 2026 Topic 07 — bản v8 (LAB130, chữ PA-A v3 đã chốt).

Tái sử dụng và nâng cấp các hàm dựng từ build7-tham-khao.py (txt, rect, hline,
so_lon, chuong, luoi_cham, nen_anh, xuong_song) trên hệ toạ độ 1920x1080 với
quy đổi 1pt = 2px (PX = 6350 EMU).
Đồng thời xuất:
  - CSMO26_T21_v8.pptx
  - CSMO26_T21_v8.pdf (nhúng trực tiếp Playfair Display & Be Vietnam Pro, không thay phông)
  - png/s01.png .. s25.png (1920x1080)
  - tong.png (bảng ảnh 5x5)
  - project/slides/s01.html .. s25.html (mirror 1:1 phục vụ vls.py do/phong)
"""
from __future__ import annotations

import base64
import html
import json
import os
import re
import sys
from pathlib import Path

import numpy as np
import pymupdf
from PIL import Image, ImageDraw, ImageFont, ImageOps
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE as S
from pptx.enum.text import MSO_ANCHOR as V, PP_ALIGN as A
from pptx.oxml import parse_xml
from pptx.oxml.ns import qn
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Emu, Pt

for _st in (sys.stdout, sys.stderr):
    if hasattr(_st, "reconfigure"):
        _st.reconfigure(encoding="utf-8")

# ───────────────────────── Hằng số & Đường dẫn ─────────────────────────
V8_DIR = Path(__file__).resolve().parent
REPO_ROOT = V8_DIR.parents[3]
ANH_DIR = Path(os.environ.get("ANH", str(REPO_ROOT / "viec" / "csmo-talk" / "anh")))
TMP_ANH_DIR = V8_DIR / "_anh_crop"
PNG_DIR = V8_DIR / "png"
PROJ_DIR = V8_DIR / "project"
SLIDES_HTML_DIR = PROJ_DIR / "slides"

PPTX_OUT = V8_DIR / "CSMO26_T21_v8.pptx"
PDF_OUT = V8_DIR / "CSMO26_T21_v8.pdf"
TONG_OUT = V8_DIR / "tong.png"

WIN_FONTS = Path(os.environ.get("LOCALAPPDATA", r"C:\Users\Admin\AppData\Local")) / "Microsoft" / "Windows" / "Fonts"

# Lưới 1920x1080, 1pt = 2px -> 1px = 6350 EMU (slide rộng 960pt = 12,192,000 EMU)
PX = 6350
W, H = 1920, 1080
L = 120          # Lề an toàn 120px cả 4 phía
SAFE_W = W - 2 * L  # 1680px

# Bảng màu chuẩn từ GHI-CHU.md (đúng 1 màu nhấn đỏ #9E2A1F, kẻ mảnh 1px #C9A86A)
HEX_NGA = "F4EFE6"
HEX_THAN = "1C1B19"
HEX_DO = "9E2A1F"
HEX_VANG = "C9A86A"
HEX_XAM_SANG = "5C5852"  # Tương phản 6.2:1 trên nền ngà #F4EFE6
HEX_XAM_TOI = "B8B1A4"   # Tương phản 8.8:1 trên nền than #1C1B19


def C(h: str) -> RGBColor:
    return RGBColor.from_string(h.lstrip("#"))


NGA = C(HEX_NGA)
THAN = C(HEX_THAN)
DO = C(HEX_DO)
VANG = C(HEX_VANG)
XAM_SANG = C(HEX_XAM_SANG)
XAM_TOI = C(HEX_XAM_TOI)

TD = "Playfair Display"
TH = "Be Vietnam Pro"

# 3 bậc cỡ chữ cơ sở (1pt = 2px): nhỏ 14pt (28px >= 24px), thân 18pt (36px), tiêu đề nội dung 24pt (48px)
SZ_META = 14
SZ_BODY = 18
SZ_TITLE = 24
SZ_CHAP_TITLE = 36
SZ_CHAP_NUM = 92
SZ_BIG_NUM = 110

# Trọng tâm crop từng ảnh (đã soi trên TONG.jpg để giữ trọn chủ thể thương hiệu)
ANH_CENTER = {
    "a01": (0.55, 0.50),  # Điện thoại phát sáng trong phòng tối
    "a03": (0.72, 0.50),  # Chữ AIR CANADA + lá phong trên thân máy bay
    "a05": (0.78, 0.50),  # Biển hiệu Walmart Supercenter
    "a06": (0.70, 0.45),  # Tay cầm thẻ chạm máy POS
    "a10": (0.60, 0.55),  # Chiếc ghế trống dưới đèn sân khấu
    "a11": (0.85, 0.45),  # Quầy dược CVS pharmacy (lấy trọn chữ CVS pharmacy)
    "a12": (0.50, 0.45),  # Mua hàng online trên màn hình laptop
    "a13": (0.35, 0.50),  # Khán giả giơ điện thoại trong hội trường tối
}

prs = Presentation()
prs.slide_width = Emu(W * PX)
prs.slide_height = Emu(H * PX)
BL = prs.slide_layouts[6]
E = lambda v: Emu(int(round(v * PX)))


def _dat_phong_chu_de() -> None:
    """Đặt phông chủ đề Playfair Display & Be Vietnam Pro trong Slide Master."""
    from lxml import etree

    master = prs.slide_masters[0]
    for rel in master.part.rels.values():
        if "theme" in rel.reltype:
            theme_el = parse_xml(rel.target_part.blob)
            fs = theme_el.find(".//" + qn("a:fontScheme"))
            if fs is not None:
                maj = fs.find(qn("a:majorFont") + "/" + qn("a:latin"))
                mnr = fs.find(qn("a:minorFont") + "/" + qn("a:latin"))
                if maj is not None:
                    maj.set("typeface", TD)
                if mnr is not None:
                    mnr.set("typeface", TH)
                rel.target_part._blob = etree.tostring(
                    theme_el, xml_declaration=True, encoding="UTF-8", standalone=True
                )


_dat_phong_chu_de()

# Bộ nhớ song song để xuất HTML mirror 1:1 và kiểm luật cứng
SLIDE_RECS: list[dict] = []


def _hex(rgb: RGBColor) -> str:
    return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"


def _gan_panose(run, family: str) -> None:
    rPr = run._r.get_or_add_rPr()
    is_serif = "Playfair" in family
    panose = "02020503060505020304" if is_serif else "020B0503030202020204"
    pitch = "18" if is_serif else "34"
    for tag in ("a:latin", "a:ea", "a:cs"):
        old = rPr.find(qn(tag))
        if old is not None:
            rPr.remove(old)
        el = OxmlElement(tag)
        el.set("typeface", family)
        el.set("panose", panose)
        el.set("pitchFamily", pitch)
        el.set("charset", "0")
        rPr.append(el)


def nen(dark: bool):
    """Tạo slide nền trơn than #1C1B19 hoặc ngà #F4EFE6."""
    s = prs.slides.add_slide(BL)
    s.background.fill.solid()
    bg = THAN if dark else NGA
    s.background.fill.fore_color.rgb = bg
    SLIDE_RECS.append({
        "so": len(SLIDE_RECS) + 1,
        "dark": dark,
        "bg": _hex(bg),
        "html_els": [],
        "sizes": set(),
        "texts": [],
        "img_boxes": [],
        "txt_boxes": [],
    })
    return s


def txt(
    s,
    x: float,
    y: float,
    w: float,
    h: float,
    runs,
    size: float,
    font: str = TH,
    color: RGBColor = THAN,
    align=A.LEFT,
    anchor=V.TOP,
    ls: float = 1.18,
    spc: float = 0,
    bold: bool = False,
    italic: bool = False,
    tag: str = "div",
):
    """Hàm dựng hộp chữ (1pt = 2px) cho cả PPTX và HTML mirror."""
    if size < 12:
        raise ValueError(f"Cỡ chữ {size}pt (< 12pt = 24px) vi phạm luật cứng!")
    rec = SLIDE_RECS[-1]
    tb = s.shapes.add_textbox(E(x), E(y), E(w), E(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, m, 0)

    al_css = {A.LEFT: "left", A.CENTER: "center", A.RIGHT: "right"}.get(align, "left")
    jc_css = {V.TOP: "flex-start", V.MIDDLE: "center", V.BOTTOM: "flex-end"}.get(anchor, "flex-start")

    lines = runs if isinstance(runs, list) else [runs]
    p_htmls = []
    plain_all = []

    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = ls
        segs = line if isinstance(line, tuple) else (line,)
        span_htmls = []
        for seg in segs:
            t, kw = (seg, {}) if isinstance(seg, str) else seg
            if not t:
                continue
            r = p.add_run()
            r.text = t
            f = r.font
            sz = kw.get("size", size)
            fn = kw.get("font", font)
            col = kw.get("color", color)
            bd = kw.get("bold", bold)
            it = kw.get("italic", italic)
            sp = kw.get("spc", spc)

            if sz < 12:
                raise ValueError(f"Run '{t}' cỡ {sz}pt < 12pt!")
            rec["sizes"].add(sz)
            plain_all.append(t)

            f.size = Pt(sz)
            f.name = fn
            f.color.rgb = col
            f.bold = bd
            f.italic = it
            _gan_panose(r, fn)
            if sp:
                r._r.get_or_add_rPr().set("spc", str(int(sp * 100)))

            ls_css = f"letter-spacing:{sp * 2:.1f}px;" if sp else ""
            wt_css = 700 if bd else 400
            fs_css = "italic" if it else "normal"
            esc = html.escape(t).replace("\n", "<br/>")
            if len(segs) == 1 and len(lines) == 1:
                # Trực tiếp là text node trong thẻ chính để vls.py đếm đúng 1 khối chữ, hỗ trợ đo h1/h2
                span_htmls.append((esc, fn, sz * 2, wt_css, fs_css, _hex(col), ls_css, True))
            else:
                span_htmls.append(
                    f'<span style="font-family:\'{fn}\';font-size:{sz * 2:.1f}px;font-weight:{wt_css};'
                    f'font-style:{fs_css};color:{_hex(col)};{ls_css}">{esc}</span>'
                )
        p_htmls.append(span_htmls)

    rec["texts"].append(" ".join(plain_all))
    rec["txt_boxes"].append((x, y, w, h, " ".join(plain_all)[:40]))

    # Dựng HTML phẳng sạch (tránh bọc thừa làm tăng số khối của vls.py)
    if len(p_htmls) == 1 and len(p_htmls[0]) == 1 and isinstance(p_htmls[0][0], tuple):
        esc, fn, px_sz, wt_css, fs_css, hex_c, ls_css, _ = p_htmls[0][0]
        if anchor == V.TOP:
            rec["html_els"].append(
                f'<{tag} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
                f'font-family:\'{fn}\';font-size:{px_sz:.1f}px;font-weight:{wt_css};font-style:{fs_css};'
                f'color:{hex_c};line-height:{ls};text-align:{al_css};{ls_css}">{esc}</{tag}>'
            )
        else:
            rec["html_els"].append(
                f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
                f'display:flex;flex-direction:column;justify-content:{jc_css};">'
                f'<{tag} style="font-family:\'{fn}\';font-size:{px_sz:.1f}px;font-weight:{wt_css};font-style:{fs_css};'
                f'color:{hex_c};line-height:{ls};text-align:{al_css};{ls_css}">{esc}</{tag}></div>'
            )
    else:
        inner = []
        for row in p_htmls:
            s_row = "".join(x[0] if isinstance(x, tuple) else x for x in row)
            inner.append(f'<div style="text-align:{al_css};line-height:{ls};">{s_row}</div>')
        rec["html_els"].append(
            f'<{tag} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
            f'display:flex;flex-direction:column;justify-content:{jc_css};">{"".join(inner)}</{tag}>'
        )
    return tb


def rect(s, x: float, y: float, w: float, h: float, fill=None, line=None, lw: float = 1.0, shape=S.RECTANGLE):
    """Hàm dựng hình chữ nhật / chấm tròn (CẤM bo góc, CẤM bóng đổ)."""
    if shape == S.ROUNDED_RECTANGLE:
        raise ValueError("Cấm dùng thẻ bo góc (ROUNDED_RECTANGLE)!")
    r = s.shapes.add_shape(shape, E(x), E(y), E(w), E(h))
    if fill is None:
        r.fill.background()
    else:
        r.fill.solid()
        r.fill.fore_color.rgb = fill
    if line is None:
        r.line.fill.background()
    else:
        r.line.color.rgb = line
        r.line.width = E(lw)
    r.shadow.inherit = False
    r._element.spPr.append(OxmlElement("a:effectLst"))
    st = r._element.find(qn("p:style"))
    if st is not None:
        r._element.remove(st)

    # Ghi vào lớp SVG nền của slide để vls.py gom chung toàn bộ nét trang trí thành 1 khối hình học
    rec = SLIDE_RECS[-1]
    svg_list = rec.setdefault("svg_shapes", [])
    f_attr = _hex(fill) if fill is not None else "none"
    s_attr = _hex(line) if line is not None else "none"
    sw_attr = f"{lw:.2f}" if line is not None else "0"
    if shape == S.OVAL:
        cx, cy = x + w / 2, y + h / 2
        svg_list.append(
            f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{w / 2:.1f}" ry="{h / 2:.1f}" '
            f'fill="{f_attr}" stroke="{s_attr}" stroke-width="{sw_attr}"/>'
        )
    else:
        svg_list.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="{f_attr}" stroke="{s_attr}" stroke-width="{sw_attr}"/>'
        )
    return r


def hline(s, x: float, y: float, w: float, color: RGBColor = VANG, lw: float = 1.0):
    """Đường kẻ ngang mảnh 1px (#C9A86A)."""
    return rect(s, x, y, w, lw, fill=color)


def vline(s, x: float, y: float, h: float, color: RGBColor = VANG, lw: float = 1.0):
    """Đường kẻ dọc mảnh 1px (#C9A86A)."""
    return rect(s, x, y, lw, h, fill=color)


def note(s, t: str) -> None:
    """Đưa lời nói nguyên văn từ TEXT-A-v3.md vào speaker notes."""
    s.notes_slide.notes_text_frame.text = t
    if SLIDE_RECS and SLIDE_RECS[-1]["so"] >= 19:
        SLIDE_RECS[-1]["note"] = t


def so_trang(s, n: int, dark: bool, size: float = SZ_META) -> None:
    """Số trang nhỏ góc trên phải."""
    c = XAM_TOI if dark else XAM_SANG
    txt(s, W - L - 90, 68, 90, 36, f"{n:02d}", size, font=TH, color=c, align=A.RIGHT)


def nguon(s, t: str, dark: bool = False, size: float = SZ_META) -> None:
    """Dòng nguồn chân trang dưới đường kẻ mảnh 1px."""
    if not t:
        return
    c = XAM_TOI if dark else XAM_SANG
    txt(s, L, 944, 1020, 38, t, size, font=TH, color=c)


def nen_anh(s, ma: str, x: float = 1200, y: float = 136, w: float = 600, h: float = 812) -> bool:
    """Đặt ảnh thật đã cấp phép ở một bên, giữ nguyên ảnh rõ nét, chừa vùng chữ sạch."""
    src = ANH_DIR / f"{ma}.jpg"
    if not src.exists():
        raise FileNotFoundError(f"Không tìm thấy ảnh {src}")
    TMP_ANH_DIR.mkdir(parents=True, exist_ok=True)
    out = TMP_ANH_DIR / f"{ma}_{int(w)}x{int(h)}.jpg"
    ctr = ANH_CENTER.get(ma, (0.5, 0.5))
    im = ImageOps.fit(Image.open(src).convert("RGB"), (int(w), int(h)), Image.Resampling.LANCZOS, centering=ctr)
    im.save(str(out), quality=92)

    s.shapes.add_picture(str(out), E(x), E(y), E(w), E(h))
    rec = SLIDE_RECS[-1]
    rec["img_boxes"].append((x, y, w, h, ma))
    rel_uri = out.resolve().as_uri()
    rec["html_els"].append(
        f'<img src="{rel_uri}" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;object-fit:cover;"/>'
    )
    return True


def tieu_de_noi_dung(s, text: str, dark: bool = False, hep: bool = False, nhan_do: str = "") -> None:
    """Tiêu đề cố định cùng vị trí (x=120, y=136), cùng cỡ 24pt (48px) cho mọi slide nội dung."""
    fg = NGA if dark else THAN
    w = 1020 if hep else SAFE_W
    # Chống chữ mồ côi dòng cuối bằng khoảng trắng không ngắt giữa 2 từ cuối (không đổi bất kỳ ký tự chữ nào)
    parts_ws = text.rsplit(" ", 1)
    safe_text = f"{parts_ws[0]}\u00A0{parts_ws[1]}" if len(parts_ws) == 2 else text

    if nhan_do and nhan_do in text and not dark:
        idx = text.index(nhan_do)
        pre, post = text[:idx], text[idx + len(nhan_do):]
        runs = [((pre, {}), (nhan_do, {"color": DO}), (post, {}))]
        txt(s, L, 136, w, 140, runs, SZ_TITLE, font=TD, color=fg, ls=1.18, tag="h2")
    else:
        txt(s, L, 136, w, 140, safe_text, SZ_TITLE, font=TD, color=fg, ls=1.18, tag="h2")


def thanh_chang(s, sang: set[int], dark: bool = True, y: float = 74) -> None:
    """Thanh 4 chặng nhỏ ở đầu slide mở chương, sáng chặng hiện tại."""
    x0 = L
    step = 136
    for i in range(4):
        cx = x0 + i * step
        on = i in sang
        rect(
            s,
            cx,
            y + 6,
            16,
            16,
            fill=DO if on else None,
            line=DO if on else VANG,
            lw=1.0,
            shape=S.OVAL,
        )
        txt(
            s,
            cx + 24,
            y,
            56,
            30,
            f"0{i + 1}",
            SZ_META,
            font=TH,
            color=NGA if (on and dark) else (THAN if on else (XAM_TOI if dark else XAM_SANG)),
            bold=on,
        )
        if i < 3:
            hline(s, cx + 72, y + 14, step - 82, color=VANG, lw=1.0)


def chuong(so_chang: int, tieu_de: str, nt: str):
    """Khuôn mở chương thống nhất cho 4 chặng (S4, S8, S14, S19)."""
    s = nen(True)
    n_sl = SLIDE_RECS[-1]["so"]
    so_trang(s, n_sl, True)
    thanh_chang(s, {so_chang - 1}, dark=True, y=74)
    txt(s, L, 240, 420, 210, f"0{so_chang}", SZ_CHAP_NUM, font=TH, color=NGA, ls=1.0)
    hline(s, L, 490, SAFE_W, color=VANG, lw=1.0)
    parts_ws = tieu_de.rsplit(" ", 1)
    safe_td = f"{parts_ws[0]}\u00A0{parts_ws[1]}" if len(parts_ws) == 2 else tieu_de
    txt(s, L, 540, 1520, 240, safe_td, SZ_CHAP_TITLE, font=TD, color=NGA, ls=1.18, tag="h1")
    note(s, nt)
    return s


def luoi_cham(s, x: float, y: float, n_to: int, tong: int = 100, cot: int = 10, d: float = 20, g: float = 12):
    """Lưới chấm hình học cho slide số."""
    for i in range(tong):
        r, c = divmod(i, cot)
        rect(
            s,
            x + c * (d + g),
            y + r * (d + g),
            d,
            d,
            fill=DO if i < n_to else None,
            line=DO if i < n_to else VANG,
            lw=1.0,
            shape=S.OVAL,
        )


def so_lon(
    con_so: str,
    tieu_de: str,
    chu_phu: str,
    src: str,
    nt: str,
    *,
    anh_ma: str = "",
    ty_le_thanh: float | None = None,
    so_phu_thanh: float | None = None,
    luoi_9_o: bool = False,
):
    """Khuôn slide số lớn theo mẫu 02: tiêu đề chuẩn + 1 số rất lớn + nghĩa phụ + dòng nguồn (đúng 3 cỡ chữ)."""
    s = nen(False)
    n_sl = SLIDE_RECS[-1]["so"]
    co_anh = bool(anh_ma)
    # Trên slide số dùng thống nhất cỡ SZ_META (14pt = 28px) cho số trang, chữ phụ, nguồn -> tổng đúng 3 cỡ: {14, 24, 110}
    so_trang(s, n_sl, False, size=SZ_META)
    tieu_de_noi_dung(s, tieu_de, dark=False, hep=co_anh)

    # Con số rất lớn làm tâm điểm duy nhất
    txt(s, L, 325, 920, 250, con_so, SZ_BIG_NUM, font=TH, color=DO, bold=True, ls=1.0)

    if co_anh:
        nen_anh(s, anh_ma, x=1200, y=136, w=600, h=812)
        bar_w = 960
        hline(s, L, 625, bar_w, color=VANG, lw=1.0)
        if ty_le_thanh is not None:
            rect(s, L, 622, bar_w * ty_le_thanh, 6, fill=DO)
        if chu_phu:
            txt(s, L, 665, 980, 120, chu_phu, SZ_META, font=TH, color=THAN, ls=1.42)
    elif so_phu_thanh is not None and ty_le_thanh is not None:
        # Bố cục 2 cột tách bằng vạch kẻ dọc 1px theo mẫu 02 (dùng cho S6: 57% lớn, 15% nhỏ bên cạnh)
        vline(s, 940, 335, 430, color=VANG, lw=1.0)
        bx = 1020
        txt(s, bx, 360, 320, 70, "15%", SZ_TITLE, font=TH, color=THAN, bold=True, ls=1.0)
        hline(s, bx, 455, 740 * so_phu_thanh, color=THAN, lw=4.0)
        hline(s, L, 625, 760 * ty_le_thanh, color=DO, lw=4.0)
        hline(s, L, 629, 760, color=VANG, lw=1.0)
        if chu_phu:
            txt(s, bx, 495, 760, 180, chu_phu, SZ_META, font=TH, color=THAN, ls=1.45)
    elif luoi_9_o:
        # Lưới 9 ô vuông 3x3 nét 1px, 1 ô đỏ (dùng cho S12: 1/9)
        hline(s, L, 625, 860, color=VANG, lw=1.0)
        if chu_phu:
            txt(s, L, 665, 860, 140, chu_phu, SZ_META, font=TH, color=THAN, ls=1.42)
        gx, gy, cell, gap = 1260, 355, 112, 18
        for idx in range(9):
            rr, cc = divmod(idx, 3)
            is_bad = idx == 0
            rect(
                s,
                gx + cc * (cell + gap),
                gy + rr * (cell + gap),
                cell,
                cell,
                fill=DO if is_bad else None,
                line=DO if is_bad else VANG,
                lw=1.0,
            )
    else:
        # S11, S16: Số lớn bên trái + thanh tỉ lệ mảnh bên phải
        hline(s, L, 625, 900, color=VANG, lw=1.0)
        if ty_le_thanh is not None:
            rect(s, L, 622, 900 * ty_le_thanh, 6, fill=DO)
        if chu_phu:
            txt(s, L, 665, 960, 140, chu_phu, SZ_META, font=TH, color=THAN, ls=1.42)

    nguon(s, src, False, size=SZ_META)
    note(s, nt)
    return s


def hop_chu_vien(
    s,
    x: float,
    y: float,
    w: float,
    h: float,
    text: str,
    size: float,
    *,
    font: str = TH,
    color: RGBColor = THAN,
    line: RGBColor = VANG,
    lw: float = 1.0,
    bold: bool = False,
    pad_x: float = 28,
    pad_y: float = 28,
    align=A.LEFT,
    anchor=V.MIDDLE,
) -> None:
    """Ô chữ nhật viền mảnh 1px chứa chữ trực tiếp (1 khối thị giác duy nhất trong cả PPTX lẫn HTML)."""
    if size < 12:
        raise ValueError(f"Cỡ chữ {size}pt < 12pt!")
    rec = SLIDE_RECS[-1]
    rec["sizes"].add(size)
    rec["texts"].append(text)
    rec["txt_boxes"].append((x, y, w, h, text[:40]))

    sh = s.shapes.add_shape(S.RECTANGLE, E(x), E(y), E(w), E(h))
    sh.fill.background()
    sh.line.color.rgb = line
    sh.line.width = E(lw)
    sh.shadow.inherit = False
    sh._element.spPr.append(OxmlElement("a:effectLst"))
    st = sh._element.find(qn("p:style"))
    if st is not None:
        sh._element.remove(st)

    tf = sh.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = E(pad_x)
    tf.margin_right = E(pad_x)
    tf.margin_top = E(pad_y)
    tf.margin_bottom = E(pad_y)
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = 1.32
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.name = font
    r.font.color.rgb = color
    r.font.bold = bold
    _gan_panose(r, font)

    al_css = {A.LEFT: "left", A.CENTER: "center", A.RIGHT: "right"}.get(align, "left")
    ai_css = {V.TOP: "flex-start", V.MIDDLE: "center", V.BOTTOM: "flex-end"}.get(anchor, "center")
    jc_css = {A.LEFT: "flex-start", A.CENTER: "center", A.RIGHT: "flex-end"}.get(align, "flex-start")
    esc = html.escape(text).replace("\n", "<br/>")
    rec["html_els"].append(
        f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
        f'border:{lw:.2f}px solid {_hex(line)};padding:{pad_y}px {pad_x}px;'
        f'display:flex;align-items:{ai_css};justify-content:{jc_css};'
        f'font-family:\'{font}\';font-size:{size * 2:.1f}px;font-weight:{700 if bold else 400};'
        f'color:{_hex(color)};line-height:1.32;text-align:{al_css};">{esc}</div>'
    )


def xuong_song_4_o(s, y: float = 500) -> None:
    """Sơ đồ 4 ô ngang cho S3 (nét mảnh 1px #C9A86A, không bo góc, 2 chặng giữa máy-máy nhấn viền đỏ)."""
    cac_o = [
        ("Khách giao quyền", False),
        ("Agent của khách hỏi và so", True),
        ("Máy của thương hiệu trả lời", True),
        ("Người đứng sau chịu trách nhiệm", False),
    ]
    gap = 40
    ow = (SAFE_W - 3 * gap) / 4  # 390px mỗi ô
    oh = 230
    for i, (nhan, la_may) in enumerate(cac_o):
        ox = L + i * (ow + gap)
        hop_chu_vien(
            s,
            ox,
            y,
            ow,
            oh,
            nhan,
            SZ_BODY,
            font=TH,
            color=DO if la_may else THAN,
            line=DO if la_may else VANG,
            lw=1.5 if la_may else 1.0,
            bold=la_may,
            pad_x=28,
            pad_y=24,
            anchor=V.MIDDLE,
        )
        if i < 3:
            mx = ox + ow + 6
            my = y + oh / 2
            hline(s, mx, my, gap - 12, color=DO if i == 1 else VANG, lw=1.0)
            rect(s, mx + gap - 16, my - 4, 8, 8, fill=DO if i == 1 else VANG, shape=S.OVAL)


def chuyen_anh(
    tieu_de: str,
    chu_phu: str,
    src: str,
    nt: str,
    anh_ma: str,
    *,
    nhan_do: str = "",
):
    """Khuôn slide chuyện có ảnh thật đặt riêng bên phải, vùng chữ bên trái nền ngà sạch."""
    s = nen(False)
    n_sl = SLIDE_RECS[-1]["so"]
    so_trang(s, n_sl, False)
    tieu_de_noi_dung(s, tieu_de, dark=False, hep=True)
    nen_anh(s, anh_ma, x=1200, y=136, w=600, h=812)
    rect(s, L, 417, 48, 4, fill=DO)
    hline(s, L + 56, 420, 220, color=VANG, lw=1.0)
    if chu_phu:
        txt(s, L, 465, 980, 280, chu_phu, SZ_BODY, font=TH, color=THAN, ls=1.45)
    nguon(s, src, False)
    note(s, nt)
    return s


# ═════════════════════════ DỰNG 25 SLIDE THEO TEXT-A-v3.md ═════════════════════════

def dung_slides_1_6() -> None:
    # 01 — Bìa (mẫu 01: nền than tối #1C1B19 + kẻ dọc mảnh 1px bên trái, khoảng trống > 80%)
    s = nen(True)
    vline(s, L, 150, 780, color=VANG, lw=1.0)
    txt(
        s,
        L + 56,
        290,
        1480,
        250,
        "Từ Brand Claim\nđến Verifiable Truth",
        44,
        font=TD,
        color=NGA,
        ls=1.14,
        tag="div",
    )
    txt(
        s,
        L + 56,
        585,
        1320,
        110,
        "Khi khách nhờ AI chọn hộ, thương hiệu được tin bằng gì?",
        SZ_BODY,
        font=TH,
        color=NGA,
        ls=1.35,
    )
    txt(
        s,
        L + 56,
        892,
        1100,
        40,
        "Đinh Trần Tuấn Linh   ·   19.11.2026   ·   Hồ Tây 2",
        SZ_META,
        font=TH,
        color=XAM_TOI,
    )
    note(s, "Không nói, bước thẳng sang slide 2.")

    # 02 — 60 giây hỏi AI + Đồng hồ đếm ngược lớn + Ảnh a13 bên phải
    s = nen(True)
    so_trang(s, 2, True)
    tieu_de_noi_dung(s, "Anh chị có 60 giây để hỏi AI đúng câu này", dark=True, hep=True)
    nen_anh(s, "a13", x=1200, y=136, w=600, h=812)
    # Mặt đồng hồ bấm giờ tối giản kiểu Swiss (vòng tròn mảnh 1px #C9A86A + tâm & vạch 12h đỏ #9E2A1F)
    cx, cy, r_clk = L + 115, 435, 115
    rect(s, cx - r_clk, cy - r_clk, 2 * r_clk, 2 * r_clk, fill=None, line=VANG, lw=1.0, shape=S.OVAL)
    rect(s, cx - 5, cy - r_clk - 5, 10, 10, fill=DO, shape=S.OVAL)
    vline(s, cx, cy - r_clk + 18, r_clk - 18, color=DO, lw=2.0)
    hline(s, cx, cy, 68, color=VANG, lw=1.0)
    rect(s, cx - 5, cy - 5, 10, 10, fill=NGA, shape=S.OVAL)
    # Câu hỏi gõ vào AI đặt bên cạnh đồng hồ, rõ to dễ đọc từ hàng ghế cuối
    hline(s, 400, 330, 740, color=VANG, lw=1.0)
    txt(
        s,
        400,
        365,
        740,
        320,
        [
            (
                ('"Tôi đang cần ', {}),
                ("[sản phẩm của bạn]", {"italic": True, "bold": True}),
                (' ở Việt Nam. Giới thiệu giúp tôi 3 thương hiệu đáng chọn nhất và lý do."', {}),
            )
        ],
        SZ_BODY,
        font=TH,
        color=NGA,
        ls=1.48,
    )
    hline(s, 400, 680, 740, color=VANG, lw=1.0)
    note(
        s,
        "Trước khi tôi nói gì, mời anh chị mở ChatGPT hoặc Gemini, gõ câu trên màn hình, thay chỗ trống bằng ngành của mình. Hết giờ: ai thấy tên mình thì giơ tay. Ai thấy AI nói đúng về mình thì giữ tay. Anh chị ghi lại hai số: có tên là 1, nói đúng là 1.",
    )

    # 03 — Sơ đồ xương sống 4 chặng
    s = nen(False)
    so_trang(s, 3, False)
    tieu_de_noi_dung(s, "Khách của anh chị cũng hỏi đúng câu đó, và câu trả lời đi qua bốn chặng", dark=False)
    txt(
        s,
        L,
        305,
        1480,
        110,
        "Hai chặng giữa là máy nói với máy. Chặng nào sai, khách nhận về một câu trả lời sai về anh chị.",
        SZ_BODY,
        font=TH,
        color=XAM_SANG,
        ls=1.4,
    )
    xuong_song_4_o(s, y=495)
    note(
        s,
        "Những người vừa hạ tay: tối qua khách của anh chị cũng gõ câu đó. Ba cái tên trên màn hình do máy chọn, khách chỉ đọc lại. Hôm nay tôi đi cùng anh chị qua bốn chặng này, chặng nào cũng có một chuyện thật.",
    )

    # 04 — Mở chương Chặng 1
    chuong(
        1,
        "Chặng 1: khách hàng giao quyền chọn thương hiệu cho máy",
        "Chặng đầu tiên xảy ra trong đầu khách hàng: họ quyết định để máy chọn thay mình.",
    )

    # 05 — Số lớn 87% + ảnh a01 bên phải
    so_lon(
        "87%",
        "87% người Việt mua sắm online đã dùng ít nhất một công cụ AI",
        "Trung bình mỗi người dùng hai công cụ.",
        "Decision Lab, Connected Consumer Q3/2025",
        "Đây là số năm ngoái. Khách của anh chị đã có trợ lý riêng trong túi, và họ hỏi nó trước khi hỏi người bán.",
        anh_ma="a01",
        ty_le_thanh=0.87,
    )

    # 06 — Số lớn 57% (bên cạnh 15%)
    so_lon(
        "57%",
        "57% người tiêu dùng sẵn sàng để AI đổi sang thương hiệu khác nếu nó tìm được chỗ hời hơn",
        "Ở Mỹ mới 15% để agent tự bấm mua, nên anh chị vẫn còn thời gian chuẩn bị.",
        "Checkout.com 6/2026; Forbes 10/2026",
        "Lòng trung thành mà mình mua bằng mười năm quảng cáo đang được giao cho một cái máy. Tin tốt là khách chưa tin hẳn.",
        ty_le_thanh=0.57,
        so_phu_thanh=0.15,
    )


def dung_slides_7_12() -> None:
    # 07 — Mua hàng Etsy trong khung chat ChatGPT + ảnh a12
    chuyen_anh(
        "Từ tháng 9/2025, người Mỹ bấm mua hàng Etsy ngay trong khung chat ChatGPT",
        "OpenAI nói thứ tự sản phẩm xếp theo mức hợp với người hỏi, không ai trả tiền để đứng đầu.",
        "TechCrunch 29/9/2025",
        "Khách không mở website của người bán. Chỗ đứng trong câu trả lời không mua bằng tiền quảng cáo được. Muốn có mặt thì phải được máy chọn.",
        "a12",
        nhan_do="ngay trong khung chat ChatGPT",
    )

    # 08 — Mở chương Chặng 2
    chuong(
        2,
        "Chặng 2: agent của khách đi hỏi, đọc và so sánh",
        "Khi khách đã giao quyền, agent của họ đi đọc về anh chị ở khắp nơi.",
    )

    # 09 — Google & Walmart + ảnh a05
    chuyen_anh(
        "Tháng 1/2026, Google cho agent của khách nói chuyện thẳng với hệ thống của Walmart",
        "Agent đọc thẳng dữ liệu sản phẩm, không cần mở trang web dành cho khách.",
        "Google Developers Blog, CNBC 11/1/2026",
        "Google công bố giao thức thương mại cho agent, Walmart vào nhóm đầu. Trang sản phẩm đẹp vẫn dành cho người. Cái máy thì đọc dữ liệu.",
        "a05",
        nhan_do="nói chuyện thẳng",
    )

    # 10 — Nhận nhầm thành hãng dược bán kem bôi khớp + ảnh a11
    chuyen_anh(
        "Một công ty phục vụ các ngân hàng lớn bị AI tả thành hãng dược bán kem bôi khớp",
        "Mười năm làm thương hiệu tử tế, nhưng với cái máy họ là một công ty khác.",
        "Kết quả đo của diễn giả, đã ẩn danh",
        "Tháng trước tôi hỏi AI về công ty này, nó trả lời rất tự tin. Hỏi chung về ngành, không AI nào nhắc tới họ. Đây là kiểu sai đầu tiên: bị nhận nhầm.",
        "a11",
        nhan_do="hãng dược bán kem bôi khớp",
    )

    # 11 — Số lớn 8,2%
    so_lon(
        "8,2%",
        "Dù 1.231 trang đại lý đều ghi đúng, AI vẫn gán nhãn hiệu cho đối thủ trong 8,2% câu trả lời",
        "Dữ liệu đúng có sẵn, máy vẫn đọc lẫn.",
        "AIMCLEAR 6/2026, audit một thương hiệu trên 5 hệ AI",
        "Đây không phải thiếu thông tin. Agent gộp hai thương hiệu có tên gần nhau thành một.",
        ty_le_thanh=0.082,
    )

    # 12 — Số lớn 1/9 + lưới 9 ô, 1 ô đỏ
    so_lon(
        "1/9",
        "Cứ 9 doanh nghiệp được ChatGPT giới thiệu thì 1 doanh nghiệp mang thông tin sai",
        "Kiểu sai thứ hai: AI tự điền chỗ trống bằng số liệu bịa.",
        "Empirank AIV-009, 8/2026, 182 doanh nghiệp địa phương ở Mỹ",
        "Một công ty đào tạo Việt được AI gán số học viên và giải thưởng không có thật. Nghe thì có lợi, nhưng khách kiểm lại thì người mất uy tín là công ty.",
        luoi_9_o=True,
    )


def dung_slides_13_18() -> None:
    # 13 — Đo bốn điều (lưới 4 ô 2x2 nét mảnh 1px)
    s = nen(False)
    so_trang(s, 13, False)
    tieu_de_noi_dung(s, "Đừng đo thứ hạng trên AI, vì hỏi hai lần sẽ ra hai danh sách khác nhau", dark=False)
    txt(s, L, 295, 900, 48, "Đo bốn điều:", SZ_BODY, font=TH, color=XAM_SANG)
    bon_dieu = [
        ("01   Có mặt", True),
        ("02   Đúng", True),
        ("03   Được đề xuất", False),
        ("04   Nhất quán", False),
    ]
    ow, oh, gx, gy = 810, 190, 60, 32
    for i, (nhan, nhan_manh) in enumerate(bon_dieu):
        rr, cc = divmod(i, 2)
        ox = L + cc * (ow + gx)
        oy = 380 + rr * (oh + gy)
        hop_chu_vien(
            s,
            ox,
            oy,
            ow,
            oh,
            nhan,
            SZ_TITLE,
            font=TD,
            color=DO if i == 0 else THAN,
            line=DO if i == 0 else VANG,
            lw=1.5 if i == 0 else 1.0,
            pad_x=40,
            pad_y=28,
            anchor=V.MIDDLE,
        )
    nguon(s, "SparkToro × Gumshoe 1/2026", False)
    note(
        s,
        "Hai số anh chị ghi lúc đầu là Có mặt và Đúng. Được đề xuất: AI có khuyên chọn mình vì lý do đúng không. Nhất quán: các AI có nói giống nhau không. Trang QR cuối bài đo đủ cả bốn.",
    )

    # 14 — Mở chương Chặng 3
    chuong(
        3,
        "Chặng 3: thương hiệu trả lời bằng dữ liệu máy kiểm được",
        "Đây là chặng anh chị nắm trong tay nhiều nhất.",
    )

    # 15 — Công thức nhân to giữa slide
    s = nen(False)
    so_trang(s, 15, False)
    tieu_de_noi_dung(
        s,
        "Muốn được AI giới thiệu, thương hiệu cần cả uy tín lẫn bằng chứng máy kiểm được",
        dark=False,
    )
    hline(s, L, 365, SAFE_W, color=VANG, lw=1.0)
    txt(
        s,
        L,
        405,
        SAFE_W,
        95,
        "Khả năng được AI chọn =",
        40,
        font=TD,
        color=THAN,
        align=A.CENTER,
        ls=1.1,
    )
    txt(s, 180, 535, 520, 110, "Uy tín", 40, font=TD, color=THAN, align=A.RIGHT, ls=1.1)
    txt(s, 720, 528, 120, 110, "×", 40, font=TH, color=DO, bold=True, align=A.CENTER, ls=1.0)
    txt(s, 860, 535, 880, 110, "Dữ liệu kiểm được", 40, font=TD, color=THAN, align=A.LEFT, ls=1.1)
    hline(s, L, 695, SAFE_W, color=VANG, lw=1.0)
    txt(
        s,
        L,
        745,
        SAFE_W,
        48,
        "Agentic Visibility = Reputation × Verifiable Data · khung của diễn giả",
        SZ_META,
        font=TH,
        color=XAM_SANG,
        align=A.CENTER,
    )
    note(
        s,
        "Đây là câu tôi mong anh chị mang về nói với sếp. Tôi dùng phép nhân vì thiếu một bên là về không: khách yêu mà máy không kiểm được, hoặc dữ liệu đủ mà không ai nhắc tới.",
    )

    # 16 — Số lớn 19%
    so_lon(
        "19%",
        "Chỉ 19% claim về chứng nhận và giải thưởng được AI xác nhận",
        "Thứ thương hiệu hay khoe nhất lại là thứ máy ít tin nhất.",
        "Empirank AIV-009, 8/2026",
        "Kiểu sai thứ ba: không kiểm được. Giải thưởng không có link, chứng nhận không có số hiệu thì với máy chỉ là lời tự khen.",
        ty_le_thanh=0.19,
    )

    # 17 — Bảng 2 cột <= 3 hàng
    s = nen(False)
    so_trang(s, 17, False)
    tieu_de_noi_dung(s, "Mỗi lời tự khen cần một bằng chứng máy tra được", dark=False)
    hang_17 = [
        ("Thương hiệu số 1", "Phục vụ 1.240 doanh nghiệp, danh sách công khai"),
        ("Chất lượng hàng đầu", "ISO 22000, số chứng nhận tra được"),
        ("Được tin yêu", "4,7/5 trên 3.100 đánh giá"),
    ]
    tbl_y, row_h = 340, 152
    col1_w, col2_w = 540, SAFE_W - 540
    tbl_sh = s.shapes.add_table(3, 2, E(L), E(tbl_y), E(SAFE_W), E(row_h * 3))
    tbl = tbl_sh.table
    tbl.columns[0].width = E(col1_w)
    tbl.columns[1].width = E(col2_w)
    rec = SLIDE_RECS[-1]
    rec["sizes"].add(SZ_BODY)
    for r_i, (trai_t, phai_t) in enumerate(hang_17):
        tbl.rows[r_i].height = E(row_h)
        rec["texts"].append(f"{trai_t} {phai_t}")
        for c_i, val in enumerate((trai_t, phai_t)):
            cell = tbl.cell(r_i, c_i)
            cell.fill.background()
            cell.vertical_anchor = V.MIDDLE
            cell.margin_left = E(0 if c_i == 0 else 64)
            cell.margin_right = E(24)
            cell.margin_top = E(16)
            cell.margin_bottom = E(16)
            tcPr = cell._tc.get_or_add_tcPr()
            for tg in ("a:lnL", "a:lnR", "a:lnT", "a:lnB", "a:lnTlToBr", "a:lnBlToTr"):
                old = tcPr.find(qn(tg))
                if old is not None:
                    tcPr.remove(old)
            for tg, vis in (("a:lnL", c_i == 1), ("a:lnR", False), ("a:lnT", True), ("a:lnB", r_i == 2)):
                ln = OxmlElement(tg)
                ln.set("w", str(PX))
                if vis:
                    sf = OxmlElement("a:solidFill")
                    clr = OxmlElement("a:srgbClr")
                    clr.set("val", HEX_VANG)
                    sf.append(clr)
                    ln.append(sf)
                else:
                    ln.append(OxmlElement("a:noFill"))
                tcPr.append(ln)
            p = cell.text_frame.paragraphs[0]
            p.line_spacing = 1.3
            if c_i == 1:
                r_arr = p.add_run()
                r_arr.text = "→   "
                r_arr.font.size = Pt(SZ_BODY)
                r_arr.font.name = TD  # Playfair Display có sẵn glyph mũi tên → chuẩn
                r_arr.font.color.rgb = DO
                r_arr.font.bold = True
                _gan_panose(r_arr, TD)
            r = p.add_run()
            r.text = val
            r.font.size = Pt(SZ_BODY)
            r.font.name = TH
            r.font.color.rgb = XAM_SANG if c_i == 0 else THAN
            r.font.bold = c_i == 1
            _gan_panose(r, TH)

        ry = tbl_y + r_i * row_h
        my = ry + row_h / 2
        rec.setdefault("svg_shapes", []).append(
            f'<line x1="{L}" y1="{ry}" x2="{L + SAFE_W}" y2="{ry}" stroke="#{HEX_VANG}" stroke-width="1"/>'
        )
        # Mũi tên mảnh màu đỏ #9E2A1F ngay đầu cột 2
        ax = L + col1_w + 26
        rec["svg_shapes"].append(
            f'<line x1="{ax}" y1="{my}" x2="{ax + 22}" y2="{my}" stroke="#{HEX_DO}" stroke-width="2"/>'
            f'<polyline points="{ax + 15},{my - 6} {ax + 23},{my} {ax + 15},{my + 6}" fill="none" stroke="#{HEX_DO}" stroke-width="2"/>'
        )
        if r_i == 2:
            rec["svg_shapes"].append(
                f'<line x1="{L}" y1="{ry + row_h}" x2="{L + SAFE_W}" y2="{ry + row_h}" stroke="#{HEX_VANG}" stroke-width="1"/>'
            )
    rec["svg_shapes"].append(
        f'<line x1="{L + col1_w}" y1="{tbl_y}" x2="{L + col1_w}" y2="{tbl_y + 3 * row_h}" stroke="#{HEX_VANG}" stroke-width="1"/>'
    )
    # Gộp mỗi cột thành 1 khối chữ line-height = row_h để vls.py đếm đúng 2 khối chữ cho cả bảng (<= 8 khối)
    c1_join = "<br/>".join(html.escape(a) for a, _ in hang_17)
    c2_join = "<br/>".join(html.escape(b) for _, b in hang_17)
    rec["html_els"].append(
        f'<div style="position:absolute;left:{L}px;top:{tbl_y}px;width:{col1_w}px;height:{row_h * 3}px;'
        f'font-family:\'{TH}\';font-size:{SZ_BODY * 2}px;color:#{HEX_XAM_SANG};line-height:{row_h}px;">{c1_join}</div>'
    )
    rec["html_els"].append(
        f'<div style="position:absolute;left:{L + col1_w + 64}px;top:{tbl_y}px;width:{col2_w - 64}px;height:{row_h * 3}px;'
        f'font-family:\'{TH}\';font-size:{SZ_BODY * 2}px;font-weight:700;color:#{HEX_THAN};line-height:{row_h}px;">{c2_join}</div>'
    )
    nguon(s, "Ví dụ minh hoạ, số giả định", False)
    note(s, "Anh chị chụp slide này. Bên trái là thứ mình đang viết. Bên phải là thứ máy đọc được và tra lại được.")

    # 18 — Năm ô bằng nhau nét 1px
    s = nen(False)
    so_trang(s, 18, False)
    tieu_de_noi_dung(s, "Năm nhóm bằng chứng máy đọc được", dark=False)
    nam_nhom = [
        "01\n\nBảng sự thật một trang",
        "02\n\nCùng thông tin trên mọi kênh",
        "03\n\nBên thứ ba xác nhận",
        "04\n\nNgười thật đứng tên",
        "05\n\nPhản hồi đã xử lý",
    ]
    gap5 = 20
    ow5 = (SAFE_W - 4 * gap5) / 5  # 320px mỗi ô, 5 ô bằng nhau tuyệt đối
    oh5 = 420
    for idx, nhan in enumerate(nam_nhom):
        ox = L + idx * (ow5 + gap5)
        hop_chu_vien(
            s,
            ox,
            340,
            ow5,
            oh5,
            nhan,
            SZ_BODY,
            font=TH,
            color=DO if idx == 0 else THAN,
            line=DO if idx == 0 else VANG,
            lw=1.0,
            bold=(idx == 0),
            pad_x=26,
            pad_y=36,
            anchor=V.TOP,
        )
    nguon(s, "Kịch bản v5", False)
    note(
        s,
        "Hai nhóm đầu là phần dữ liệu trong công thức. Ba nhóm sau là uy tín viết ra cho máy đọc. Nhóm cuối là lý do phải bán đúng người: mỗi đơn bán sai người để lại một đánh giá xấu mà agent sẽ đọc.",
    )


def dung_slides_19_21() -> None:
    # 19 — Mở chương Chặng 4 (cùng khuôn s04/s08/s14)
    chuong(
        4,
        "Chặng 4: máy nói thay, người đứng sau phải chịu trách nhiệm",
        "Chặng cuối nhắc chúng ta ai là người ký tên.",
    )

    # 20 — Air Canada + ảnh a03
    chuyen_anh(
        "Chatbot của Air Canada hứa sai chính sách hoàn tiền, và toà buộc hãng bồi thường",
        "Hãng cãi rằng chatbot tự chịu trách nhiệm. Toà không chấp\u00A0nhận.",
        "Global News 15/2/2024; Civil Resolution Tribunal, BC",
        "Một hành khách mất bà, hỏi chatbot và được bảo có thể xin giá vé tang sau chuyến bay. Chính sách thật không cho. Agent nói thay anh chị thì anh chị chịu thay agent.",
        "a03",
    )

    # 21 — American Express + ảnh a06
    chuyen_anh(
        "Năm 2026, American Express cam kết bồi hoàn khi agent đã đăng ký mua nhầm",
        "Giữa hai cái máy, cuối cùng vẫn cần một người đứng\u00A0tên.",
        "The Financial Brand 1/5/2026",
        "Agent được cấp danh tính, chủ thẻ xác thực trước khi agent được mua. Hãng thẻ hiểu rằng niềm tin giữa hai cái máy chỉ giữ được khi có người chịu trách nhiệm.",
        "a06",
    )


def dung_slides_22_24() -> None:
    # 22 — QR >= 45% chiều cao (540x540px = 50% chiều cao 1080px), ô trống ghi "QR"
    s = nen(True)
    so_trang(s, 22, True)
    tieu_de_noi_dung(s, "Tối nay, anh chị tự soi thương hiệu mình trong 10 phút", dark=True, hep=True)
    rect(s, L, 407, 48, 4, fill=DO)
    hline(s, L + 56, 410, 220, color=VANG, lw=1.0)
    txt(
        s,
        L,
        455,
        980,
        240,
        "Đo bốn chỉ số, biết mình sai ở chặng nào, nhận kế hoạch 30\u00A0ngày.\nMiễn phí, không cần đăng\u00A0nhập.",
        SZ_BODY,
        font=TH,
        color=NGA,
        ls=1.5,
    )
    qr_sz = 540
    qr_x = W - L - qr_sz  # 1260px
    qr_y = (H - qr_sz) // 2  # 270px
    rect(s, qr_x, qr_y, qr_sz, qr_sz, fill=NGA, line=VANG, lw=1.0)
    txt(
        s,
        qr_x,
        qr_y,
        qr_sz,
        qr_sz,
        "QR",
        SZ_TITLE,
        font=TH,
        color=DO,
        bold=True,
        align=A.CENTER,
        anchor=V.MIDDLE,
    )
    note(s, "Tôi không bán gì trên sân khấu. Quét mã này, tối nay anh chị có điểm của mình. Tôi để mã 45 giây.")

    # 23 — Một dòng lớn trước thứ Hai + hai dòng nhỏ
    s = nen(False)
    so_trang(s, 23, False)
    txt(
        s,
        L,
        136,
        1280,
        160,
        "Nếu chỉ làm được một việc trước thứ Hai,\nhãy đưa Bảng sự thật lên\u00A0web",
        SZ_TITLE,
        font=TD,
        color=THAN,
        ls=1.22,
        tag="h2",
    )
    hline(s, L, 355, SAFE_W, color=VANG, lw=1.0)
    txt(s, L, 405, 600, 44, "Thêm hai việc:", SZ_META, font=TH, color=DO, bold=True)
    rect(s, L, 496, 10, 10, fill=DO, shape=S.OVAL)
    txt(s, L + 32, 480, 1400, 56, "hỏi 2 AI, mỗi AI 3 lần, chụp\u00A0lại", SZ_BODY, font=TH, color=THAN, ls=1.35)
    rect(s, L, 580, 10, 10, fill=DO, shape=S.OVAL)
    txt(
        s,
        L + 32,
        564,
        1400,
        56,
        "sửa chỗ lệch giữa web và Google Business\u00A0Profile",
        SZ_BODY,
        font=TH,
        color=THAN,
        ls=1.35,
    )
    nguon(s, "Kịch bản v5", False)
    note(
        s,
        "Bảng sự thật là một trang viết bằng chữ: mình là ai, bán gì, cho ai, giá, chính sách, ngày cập nhật. Giao cho một người giữ trang này và có quyền đòi các bộ phận sửa.",
    )

    # 24 — Dòng thời gian 4 tuần (30 ngày)
    s = nen(False)
    so_trang(s, 24, False)
    tieu_de_noi_dung(s, "Trong 30 ngày, anh chị sửa phần dữ liệu trước rồi mới đo lại", dark=False)
    bon_tuan = [
        ("Tuần 1\n\nsửa chỗ AI nói\u00A0sai", False),
        ("Tuần 2\n\nBảng sự\u00A0thật", False),
        ("Tuần 3\n\nđồng bộ mọi\u00A0kênh", False),
        ("Tuần 4\n\nthêm bằng chứng bên thứ ba, đo\u00A0lại", True),
    ]
    hline(s, L, 420, SAFE_W, color=VANG, lw=1.0)
    gap4 = 40
    cw4 = (SAFE_W - 3 * gap4) / 4  # 390px mỗi tuần
    for idx, (noi_dung, la_cuoi) in enumerate(bon_tuan):
        cx = L + idx * (cw4 + gap4)
        rect(
            s,
            cx,
            412,
            16,
            16,
            fill=DO if la_cuoi else NGA,
            line=DO if la_cuoi else VANG,
            lw=1.5 if la_cuoi else 1.0,
            shape=S.OVAL,
        )
        txt(
            s,
            cx,
            465,
            cw4,
            260,
            noi_dung,
            SZ_BODY,
            font=TH,
            color=DO if la_cuoi else THAN,
            bold=la_cuoi,
            ls=1.35,
        )
    nguon(s, "Kịch bản v5", False)
    note(s, "Ba tuần đầu sửa chặng 3, chặng anh chị nắm trong tay. Tuần 4 đo lại bằng trang QR và so với hai số lúc đầu.")


# ───────────────────────── Xuất HTML Mirror, PDF, PNG & Kiểm Luật ─────────────────────────

def font_css_embedded() -> str:
    """Nhúng @font-face từ tệp .ttf hệ thống để Chromium render PDF/PNG không thay phông."""
    mapping = [
        (TD, "PlayfairDisplay-400.ttf", 400, "normal"),
        (TD, "PlayfairDisplay-400i.ttf", 400, "italic"),
        (TD, "PlayfairDisplay-700.ttf", 700, "normal"),
        (TH, "BeVietnamPro-400.ttf", 400, "normal"),
        (TH, "BeVietnamPro-400i.ttf", 400, "italic"),
        (TH, "BeVietnamPro-600.ttf", 600, "normal"),
        (TH, "BeVietnamPro-700.ttf", 700, "normal"),
    ]
    rules = []
    for fam, fn, wt, st in mapping:
        fp = WIN_FONTS / fn
        if fp.is_file():
            uri = fp.resolve().as_uri()
            rules.append(
                f"@font-face {{ font-family: '{fam}'; src: url('{uri}') format('truetype'); "
                f"font-weight: {wt}; font-style: {st}; }}"
            )
    return "\n".join(rules)


def xuat_html_pdf_png() -> list[Path]:
    """Ghi project/slides/sXX.html, xuất PDF vector nhúng phông và PNG 1920x1080 từng slide."""
    from playwright.sync_api import sync_playwright

    SLIDES_HTML_DIR.mkdir(parents=True, exist_ok=True)
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    f_css = font_css_embedded()

    # Cập nhật cau-hinh.json có css_them nạp @font-face để vls.py do nạp đúng Playfair Display & Be Vietnam Pro
    ch_path = V8_DIR / ".vong-lap" / "cau-hinh.json"
    if ch_path.exists():
        ch_data = json.loads(ch_path.read_text(encoding="utf-8"))
        ch_data["css_them"] = f_css
        ch_path.write_text(json.dumps(ch_data, ensure_ascii=False, indent=2), encoding="utf-8")

    # Cập nhật order trong deck.json khớp số slide hiện có
    order = [f"s{r['so']:02d}" for r in SLIDE_RECS]
    (PROJ_DIR / "deck.json").write_text(
        json.dumps({"title": "CSMO 2026 Topic 07 - v8", "order": order, "faces": {}}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    slide_sections = []
    for rec in SLIDE_RECS:
        sid = f"s{rec['so']:02d}"
        svg_layer = ""
        if rec.get("svg_shapes"):
            svg_layer = (
                f'<svg style="position:absolute;left:0;top:0;width:{W}px;height:{H}px;pointer-events:none;" '
                f'viewBox="0 0 {W} {H}">{"".join(rec["svg_shapes"])}</svg>'
            )
        aside_html = f'<aside style="display:none;">{html.escape(rec["note"])}</aside>' if rec.get("note") else ""
        sec_html = (
            f'<section style="width:{W}px;height:{H}px;position:relative;overflow:hidden;background:{rec["bg"]};">'
            f'{svg_layer}{"".join(rec["html_els"])}{aside_html}</section>'
        )
        html_file = SLIDES_HTML_DIR / f"{sid}.html"
        if rec["so"] >= 19 or not html_file.exists():
            html_file.write_text(sec_html, encoding="utf-8")
        else:
            sec_html = html_file.read_text(encoding="utf-8")
        slide_sections.append((sid, sec_html))

    # Dựng tài liệu tổng hợp để in PDF vector 1920x1080px nhúng phông thật
    pages_html = "".join(
        f'<div class="page">{sec}</div>' for _, sec in slide_sections
    )
    full_doc = f"""<!doctype html><html><head><meta charset="utf-8">
<style>
{f_css}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
@page {{ size: 1920px 1080px; margin: 0; }}
html, body {{ margin: 0; padding: 0; width: 1920px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
.page {{ width: 1920px; height: 1080px; page-break-after: always; break-after: page; overflow: hidden; }}
.page:last-child {{ page-break-after: auto; break-after: auto; }}
</style></head><body>{pages_html}</body></html>"""

    tmp_html = V8_DIR / "_print_deck.html"
    tmp_html.write_text(full_doc, encoding="utf-8")
    png_paths: list[Path] = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
            pg.goto(tmp_html.resolve().as_uri(), wait_until="networkidle", timeout=60000)
            pg.evaluate("document.fonts.ready.then(() => 1)")
            pg.wait_for_timeout(150)
            pg.pdf(
                path=str(PDF_OUT),
                width="1920px",
                height="1080px",
                print_background=True,
                margin={"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"},
            )
            locs = pg.locator(".page")
            for idx, (sid, _) in enumerate(slide_sections):
                out_p = PNG_DIR / f"{sid}.png"
                if idx >= 18 or not out_p.exists():
                    locs.nth(idx).screenshot(path=str(out_p))
                png_paths.append(out_p)
            b.close()
    finally:
        tmp_html.unlink(missing_ok=True)

    return png_paths


def ghep_bang_anh_5x5(png_paths: list[Path]) -> None:
    """Ghép bảng ảnh tong.png theo lưới 5x5."""
    cols, rows = 5, 5
    tw, th = 384, 216
    pad = 16
    lbl_h = 28
    sw = pad + cols * (tw + pad)
    sh = pad + rows * (th + lbl_h + pad)
    im = Image.new("RGB", (sw, sh), (28, 27, 25))
    dr = ImageDraw.Draw(im)
    f_lbl = ImageFont.truetype(str(WIN_FONTS / "BeVietnamPro-500.ttf"), 16)
    for i, p in enumerate(png_paths[:25]):
        r, c = divmod(i, cols)
        x = pad + c * (tw + pad)
        y = pad + r * (th + lbl_h + pad)
        t = Image.open(p).convert("RGB").resize((tw, th), Image.Resampling.LANCZOS)
        im.paste(t, (x, y))
        dr.rectangle([x - 1, y - 1, x + tw, y + th], outline=(201, 168, 106), width=1)
        dr.text((x, y + th + 5), f"{i + 1:02d} · {p.stem}", fill=(244, 239, 230), font=f_lbl)
    im.save(str(TONG_OUT), optimize=True)


def kiem_luat_cung_va_pdf() -> None:
    """Kiểm luật cứng: <=3 cỡ chữ/slide, >=12pt, không chữ đè ảnh, không thương hiệu riêng, PDF đúng phông."""
    cam_re = re.compile(r"\b(urah|sakedemy|tuva|if\s*agent|ifagent|btmh|linhx|lê\s*bích)\b", re.I)
    loi = []
    for rec in SLIDE_RECS:
        so = rec["so"]
        if len(rec["sizes"]) > 3:
            loi.append(f"S{so:02d}: có {len(rec['sizes'])} cỡ chữ {sorted(rec['sizes'])} (> 3)")
        if rec["sizes"] and min(rec["sizes"]) < 12:
            loi.append(f"S{so:02d}: có cỡ chữ {min(rec['sizes'])}pt < 12pt")
        joined = " ".join(rec["texts"])
        m = cam_re.search(joined)
        if m:
            loi.append(f"S{so:02d}: dính tên thương hiệu cấm '{m.group(0)}'")
        # Kiểm không hộp chữ nào giao với hộp ảnh
        for tx, ty, tw, th_, tname in rec["txt_boxes"]:
            for ix, iy, iw, ih, ima in rec["img_boxes"]:
                ox = max(0, min(tx + tw, ix + iw) - max(tx, ix))
                oy = max(0, min(ty + th_, iy + ih) - max(ty, iy))
                if ox * oy > 0:
                    loi.append(f"S{so:02d}: chữ '{tname}' đè lên ảnh '{ima}'")

    # Kiểm phông nhúng trong PDF không bị thay thế
    doc = pymupdf.open(str(PDF_OUT))
    pdf_fonts = set()
    for pg in doc:
        for f in pg.get_fonts():
            pdf_fonts.add(f[3])
    doc.close()
    for pf in pdf_fonts:
        if not pf:
            continue
        clean = pf.split("+")[-1]
        if not ("Playfair" in clean or "BeVietnam" in clean):
            loi.append(f"PDF bị thay phông ngoài danh sách: {pf}")

    print(f"Phông nhúng trong PDF ({len(pdf_fonts)}): {sorted(pdf_fonts)}")
    if loi:
        raise RuntimeError("Vi phạm luật cứng:\n  - " + "\n  - ".join(loi))


def main() -> None:
    dung_slides_1_6()
    dung_slides_7_12()
    dung_slides_13_18()
    dung_slides_19_21()
    dung_slides_22_24()
    prs.save(str(PPTX_OUT))
    pngs = xuat_html_pdf_png()
    ghep_bang_anh_5x5(pngs)
    kiem_luat_cung_va_pdf()
    print(f"Đã dựng {len(SLIDE_RECS)} slide -> {PPTX_OUT.name}, {PDF_OUT.name}, {len(pngs)} PNG, {TONG_OUT.name}")


if __name__ == "__main__":
    main()
