#!/usr/bin/env python3
"""Build an editable proposal deck (.pptx) from <project_dir>/proposal.json.

Usage: python build_deck.py <project_dir>
- Content lives in proposal.json (swap text there, rebuild).
- Images are looked up by stem in <project_dir>/images/: the newest of
  <stem>.png/.jpg/.jpeg/.webp wins, so saving a ChatGPT/Flow image with the
  same name replaces the mockup automatically. Missing images → labelled box.
Outputs <project_dir>/<file>.pptx and <file>-noi-dung.md (all slide text).
"""
import json, sys
from pathlib import Path
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

W, H = Inches(13.333), Inches(7.5)
M = Inches(0.6)
EXTS = (".png", ".jpg", ".jpeg", ".webp")


def rgb(h):
    h = h.lstrip("#")
    return RGBColor(int(h[:2], 16), int(h[2:4], 16), int(h[4:6], 16))


class Deck:
    def __init__(self, proj):
        self.proj = proj
        self.d = json.loads((proj / "proposal.json").read_text(encoding="utf-8"))
        self.t = self.d["theme"]
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = W, H
        self.md = [f"# {self.d['meta']['title']}\n"]
        self.n = 0

    # ---------- primitives ----------
    def img_path(self, stem):
        cands = [p for p in (self.proj / "images").glob(f"{stem}.*") if p.suffix.lower() in EXTS]
        if not cands:
            return None
        p = max(cands, key=lambda x: x.stat().st_mtime)
        if p.suffix.lower() == ".webp" or p.stat().st_size > 700_000:
            # keep the deck small: big PNG/WebP → JPEG ≤ 1920px (cached, originals untouched)
            cache = self.proj / "images" / "_cache"
            cache.mkdir(exist_ok=True)
            out = cache / f"{stem}.jpg"
            if not out.exists() or out.stat().st_mtime < p.stat().st_mtime:
                im = Image.open(p).convert("RGB")
                im.thumbnail((1920, 1920))
                im.save(out, quality=85, optimize=True)
            p = out
        return p

    def box(self, s, x, y, w, h, fill=None, line=None, shape=MSO_SHAPE.RECTANGLE, radius=None):
        sh = s.shapes.add_shape(shape, x, y, w, h)
        if radius is not None and shape == MSO_SHAPE.ROUNDED_RECTANGLE:
            sh.adjustments[0] = radius
        if fill:
            sh.fill.solid(); sh.fill.fore_color.rgb = rgb(fill)
        else:
            sh.fill.background()
        if line:
            sh.line.color.rgb = rgb(line); sh.line.width = Pt(1.25)
        else:
            sh.line.fill.background()
        sh.shadow.inherit = False
        return sh

    def text(self, s, x, y, w, h, txt, size=16, color=None, bold=False, font=None, align=PP_ALIGN.LEFT,
             anchor=MSO_ANCHOR.TOP, bullets=False, spacing=1.1):
        tb = s.shapes.add_textbox(x, y, w, h)
        tf = tb.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = anchor
        tf.margin_left = tf.margin_right = Inches(0.05)
        tf.margin_top = tf.margin_bottom = Inches(0.03)
        lines = txt if isinstance(txt, list) else [txt]
        for i, ln in enumerate(lines):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = align
            p.line_spacing = spacing
            if bullets:
                p.space_after = Pt(size * 0.5)
            r = p.add_run()
            r.text = ("•  " if bullets else "") + str(ln)
            f = r.font
            f.size = Pt(size); f.bold = bold
            f.name = font or self.t["font_body"]
            f.color.rgb = rgb(color or self.t["text"])
        return tb

    def picture(self, s, stem, x, y, w, h, mode="cover", border=None):
        p = self.img_path(stem) if stem else None
        if not p:
            self.box(s, x, y, w, h, fill=self.t["light"], line=self.t["primary"])
            self.text(s, x, y, w, h, f"[Thiếu ảnh: {stem}]", 12, self.t["primary"], True,
                      align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
            return
        iw, ih = Image.open(p).size
        if mode == "contain":
            r = min(w / iw, h / ih)
            nw, nh = int(iw * r), int(ih * r)
            pic = s.shapes.add_picture(str(p), x + (w - nw) // 2, y + (h - nh) // 2, nw, nh)
        else:
            pic = s.shapes.add_picture(str(p), x, y, w, h)
            ar_box, ar_img = w / h, iw / ih
            if ar_img > ar_box:
                c = (1 - ar_box / ar_img) / 2; pic.crop_left = pic.crop_right = c
            else:
                c = (1 - ar_img / ar_box) / 2; pic.crop_top = pic.crop_bottom = c
        if border:
            pic.line.color.rgb = rgb(border); pic.line.width = Pt(1.5)

    def new(self, sd, dark=False):
        s = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        self.n += 1
        self.box(s, 0, 0, W, H, fill=self.t["dark"] if dark else self.t["bg"])
        if sd.get("notes"):
            s.notes_slide.notes_text_frame.text = sd["notes"]
        return s

    def header(self, s, sd, dark=False):
        c = "#FFFFFF" if dark else self.t["text"]
        if sd.get("kicker"):
            self.text(s, M, Inches(0.42), Inches(10), Inches(0.35), sd["kicker"].upper(), 12,
                      self.t["secondary"] if dark else self.t["primary"], True)
        title = sd.get("title", "")
        self.text(s, M, Inches(0.72), W - 2 * M, Inches(0.9), title, 30 if len(title) <= 52 else 24, c, True,
                  font=self.t["font_head"])
        self.md.append(f"\n## {self.n}. {sd.get('title', '')}\n")

    def footer(self, s, dark=False):
        c = "#FFFFFF" if dark else self.t["muted"]
        self.box(s, 0, H - Inches(0.08), W, Inches(0.08), fill=self.t["primary"])
        self.text(s, M, H - Inches(0.45), Inches(8), Inches(0.3), self.d["meta"]["footer"], 10, c)
        self.text(s, W - M - Inches(1), H - Inches(0.45), Inches(1), Inches(0.3), str(self.n), 10, c,
                  align=PP_ALIGN.RIGHT)

    # ---------- slide types ----------
    def s_cover(self, sd):
        s = self.new(sd, dark=True)
        self.picture(s, sd.get("image"), 0, 0, W, H)
        self.box(s, 0, 0, Inches(7.4), H, fill=self.t["dark"])
        self.box(s, M, Inches(1.4), Inches(0.9), Inches(0.1), fill=self.t["secondary"])
        self.text(s, M, Inches(1.7), Inches(6.4), Inches(0.4), sd.get("kicker", "").upper(), 13, self.t["secondary"], True)
        self.text(s, M, Inches(2.1), Inches(6.4), Inches(2.6), sd["title"], 44, "#FFFFFF", True, font=self.t["font_head"], spacing=1.0)
        self.text(s, M, Inches(4.8), Inches(6.2), Inches(1.2), sd.get("subtitle", ""), 17, "#FFFFFF")
        self.text(s, M, Inches(6.4), Inches(6.2), Inches(0.5), sd.get("meta", ""), 12, self.t["secondary"])
        self.md.append(f"\n## {self.n}. {sd['title']}\n{sd.get('subtitle', '')}\n")

    def s_section(self, sd):
        s = self.new(sd, dark=True)
        if sd.get("image"):
            self.picture(s, sd["image"], Inches(7.2), 0, W - Inches(7.2), H)
        self.text(s, M, Inches(2.2), Inches(1.6), Inches(1.2), sd.get("number", ""), 60, self.t["secondary"], True, font=self.t["font_head"])
        self.text(s, M, Inches(3.4), Inches(6.2), Inches(1.4), sd["title"], 38, "#FFFFFF", True, font=self.t["font_head"])
        self.text(s, M, Inches(4.8), Inches(6.2), Inches(1.4), sd.get("subtitle", ""), 16, "#FFFFFFCC"[:7])
        self.md.append(f"\n## {self.n}. {sd['title']}\n{sd.get('subtitle', '')}\n")
        self.footer(s, dark=True)

    def s_bullets(self, sd):
        s = self.new(sd)
        self.header(s, sd)
        has_img = bool(sd.get("image"))
        tw = Inches(6.3) if has_img else W - 2 * M
        y = Inches(1.75)
        if sd.get("lead"):
            self.text(s, M, y, tw, Inches(0.9), sd["lead"], 17, self.t["primary"], True)
            y += Inches(0.95)
        self.text(s, M, y, tw, H - y - Inches(0.8), sd.get("bullets", []), sd.get("size", 16), bullets=True)
        if has_img:
            self.picture(s, sd["image"], Inches(7.3), Inches(1.75), W - Inches(7.3) - M, Inches(4.9), sd.get("mode", "cover"))
        self.md.append((sd.get("lead", "") + "\n") + "\n".join(f"- {b}" for b in sd.get("bullets", [])))
        self.footer(s)

    def s_cards(self, sd):
        s = self.new(sd)
        self.header(s, sd)
        cards = sd["cards"]
        cols = sd.get("cols", min(len(cards), 3))
        rows = (len(cards) + cols - 1) // cols
        gap = Inches(0.25)
        top = Inches(1.8) + (Inches(0.6) if sd.get("lead") else 0)
        if sd.get("lead"):
            self.text(s, M, Inches(1.7), W - 2 * M, Inches(0.6), sd["lead"], 15, self.t["muted"])
        cw = (W - 2 * M - gap * (cols - 1)) / cols
        ch = (H - top - Inches(0.75) - gap * (rows - 1)) / rows
        for i, c in enumerate(cards):
            x = M + (cw + gap) * (i % cols); y = top + (ch + gap) * (i // cols)
            self.box(s, int(x), int(y), int(cw), int(ch), fill="#FFFFFF", line=self.t["line"], shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.06)
            self.box(s, int(x), int(y), Inches(0.09), int(ch), fill=self.t["primary"] if i % 2 == 0 else self.t["secondary"])
            iy = y + Inches(0.18)
            if c.get("image"):
                ih = int(ch * 0.42)
                self.picture(s, c["image"], int(x + Inches(0.25)), int(iy), int(cw - Inches(0.4)), ih)
                iy += ih + Inches(0.1)
            if c.get("tag"):
                self.text(s, int(x + Inches(0.25)), int(iy), int(cw - Inches(0.4)), Inches(0.3), c["tag"].upper(), 10, self.t["primary"], True)
                iy += Inches(0.3)
            self.text(s, int(x + Inches(0.25)), int(iy), int(cw - Inches(0.4)), Inches(0.6), c["title"], sd.get("title_size", 16), self.t["text"], True, font=self.t["font_head"])
            ts = sd.get("title_size", 16)
            per_line = max(8, int((cw - Inches(0.4)) / 914400 * 72 / (ts * 0.62)))
            nlines = -(-len(c["title"]) // per_line)
            iy += int(Inches(nlines * ts * 1.3 / 72 + 0.12))
            self.text(s, int(x + Inches(0.25)), int(iy), int(cw - Inches(0.4)), int(y + ch - iy - Inches(0.1)), c.get("text", ""), sd.get("size", 13), self.t["muted"])
        self.md.append("\n".join(f"- **{c['title']}** — {c.get('text', '')}" for c in cards))
        self.footer(s)

    def s_steps(self, sd):
        s = self.new(sd)
        self.header(s, sd)
        steps = sd["steps"]
        n = len(steps)
        gap = Inches(0.2)
        cw = (W - 2 * M - gap * (n - 1)) / n
        top = Inches(2.0)
        if sd.get("image"):
            self.picture(s, sd["image"], M, Inches(4.75), W - 2 * M, Inches(2.0))
        for i, st in enumerate(steps):
            x = int(M + (cw + gap) * i)
            self.box(s, x, top, Inches(0.75), Inches(0.75), fill=self.t["primary"], shape=MSO_SHAPE.OVAL)
            self.text(s, x, top, Inches(0.75), Inches(0.75), str(i + 1), 20, "#FFFFFF", True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
            if i < n - 1:
                self.box(s, x + Inches(0.85), top + Inches(0.34), int(cw - Inches(0.75)), Inches(0.06), fill=self.t["secondary"])
            self.text(s, x, top + Inches(0.95), int(cw), Inches(0.7), st["title"], 15, self.t["text"], True, font=self.t["font_head"])
            hh = Inches(1.9) if sd.get("image") else Inches(2.0)
            self.text(s, x, top + Inches(1.6), int(cw), hh, st.get("text", ""), 11.5, self.t["muted"])
        if sd.get("note") and not sd.get("image"):
            self.box(s, M, Inches(5.75), W - 2 * M, Inches(0.8), fill=self.t["light"], shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.2)
            self.text(s, M + Inches(0.3), Inches(5.75), W - 2 * M - Inches(0.6), Inches(0.8), sd["note"], 15, self.t["primary"], True, anchor=MSO_ANCHOR.MIDDLE)
        self.md.append("\n".join(f"{i+1}. **{st['title']}** — {st.get('text', '')}" for i, st in enumerate(steps)))
        self.footer(s)

    def s_screens(self, sd):
        s = self.new(sd)
        self.header(s, sd)
        scr = sd["screens"]
        n = len(scr)
        gap = Inches(0.3)
        cw = (W - 2 * M - gap * (n - 1)) / n
        ih = Inches(4.9)
        for i, sc in enumerate(scr):
            x = int(M + (cw + gap) * i)
            iw = int(min(cw * 0.46, ih * 9 / 16)) if sc.get("portrait", True) else int(cw)
            self.picture(s, sc["image"], x, Inches(1.75), iw, ih if sc.get("portrait", True) else int(iw * 9 / 16), "contain", border=self.t["line"])
            tx = x + iw + Inches(0.2) if sc.get("portrait", True) else x
            ty = Inches(1.75) if sc.get("portrait", True) else Inches(1.75) + int(iw * 9 / 16) + Inches(0.1)
            tw = int(cw - iw - Inches(0.2)) if sc.get("portrait", True) else int(cw)
            self.text(s, tx, ty, tw, Inches(0.3), sc.get("tag", f"Màn hình {i+1}").upper(), 10, self.t["primary"], True)
            self.text(s, tx, ty + Inches(0.3), tw, Inches(0.7), sc["title"], 16, self.t["text"], True, font=self.t["font_head"])
            self.text(s, tx, ty + Inches(1.0), tw, Inches(3.9), sc.get("points", []), 11, self.t["muted"], bullets=True)
        self.md.append("\n".join(f"- **{sc['title']}** ({sc['image']}): " + "; ".join(sc.get("points", [])) for sc in scr))
        self.footer(s)

    def s_visual(self, sd):
        s = self.new(sd)
        self.header(s, sd)
        iw = Inches(8.3)
        self.picture(s, sd["image"], M, Inches(1.75), iw, Inches(4.9), sd.get("mode", "contain"), border=self.t["line"])
        x = M + iw + Inches(0.3)
        self.text(s, x, Inches(1.75), W - x - M, Inches(4.9), sd.get("bullets", []), 12.5, bullets=True)
        self.md.append(f"[ảnh: {sd['image']}]\n" + "\n".join(f"- {b}" for b in sd.get("bullets", [])))
        self.footer(s)

    def s_table(self, sd):
        s = self.new(sd)
        self.header(s, sd)
        cols, rows = sd["columns"], sd["rows"]
        top = Inches(1.8)
        if sd.get("lead"):
            self.text(s, M, Inches(1.65), W - 2 * M, Inches(0.5), sd["lead"], 13, self.t["muted"]); top = Inches(2.2)
        tw = W - 2 * M
        rh = min(Inches(0.52), int((H - top - Inches(0.9)) / (len(rows) + 1)))
        gt = s.shapes.add_table(len(rows) + 1, len(cols), M, top, tw, rh * (len(rows) + 1)).table
        widths = sd.get("col_widths") or [1] * len(cols)
        for i, w in enumerate(widths):
            gt.columns[i].width = int(tw * w / sum(widths))
        size = sd.get("size", 11)
        for r in range(len(rows) + 1):
            for c in range(len(cols)):
                cell = gt.cell(r, c)
                val = cols[c] if r == 0 else rows[r - 1][c]
                cell.text = str(val)
                cell.fill.solid()
                cell.fill.fore_color.rgb = rgb(self.t["primary"] if r == 0 else ("#FFFFFF" if r % 2 else self.t["light"]))
                for p in cell.text_frame.paragraphs:
                    for run in p.runs:
                        run.font.size = Pt(size); run.font.name = self.t["font_body"]
                        run.font.bold = r == 0 or (c == 0 and sd.get("bold_first", True))
                        run.font.color.rgb = rgb("#FFFFFF" if r == 0 else self.t["text"])
                cell.margin_left = cell.margin_right = Inches(0.08)
        if sd.get("note"):
            self.text(s, M, H - Inches(0.85), W - 2 * M, Inches(0.35), sd["note"], 10, self.t["muted"])
        self.md.append("| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n" +
                       "\n".join("| " + " | ".join(map(str, r)) + " |" for r in rows))
        self.footer(s)

    def s_bigidea(self, sd):
        s = self.new(sd, dark=True)
        self.picture(s, sd.get("image"), 0, 0, W, H)
        self.box(s, 0, Inches(3.9), W, Inches(3.6), fill=self.t["dark"])
        self.text(s, M, Inches(4.15), Inches(10), Inches(0.4), sd.get("kicker", "").upper(), 13, self.t["secondary"], True)
        self.text(s, M, Inches(4.55), W - 2 * M, Inches(1.2), sd["title"], 40, "#FFFFFF", True, font=self.t["font_head"])
        self.text(s, M, Inches(5.7), W - 2 * M, Inches(1.2), sd.get("text", ""), 16, "#FFFFFF")
        self.md.append(f"\n## {self.n}. {sd['title']}\n{sd.get('text', '')}\n")
        self.footer(s, dark=True)

    def s_full(self, sd):
        """Full-bleed image slide (showcase mockups, renders)."""
        s = self.new(sd, dark=True)
        self.picture(s, sd["image"], 0, 0, W, H)
        if sd.get("caption"):
            self.box(s, 0, H - Inches(0.6), W, Inches(0.6), fill=self.t["dark"])
            self.text(s, M, H - Inches(0.55), W - 2 * M, Inches(0.45), sd["caption"], 13, "#FFFFFF", anchor=MSO_ANCHOR.MIDDLE)
        self.md.append(f"\n## {self.n}. {sd.get('title', sd['image'])}\n[ảnh: {sd['image']}] {sd.get('caption', '')}\n")

    def s_closing(self, sd):
        s = self.new(sd, dark=True)
        if sd.get("image"):
            self.picture(s, sd["image"], Inches(7.6), 0, W - Inches(7.6), H)
        self.text(s, M, Inches(1.6), Inches(6.6), Inches(1.5), sd["title"], 40, "#FFFFFF", True, font=self.t["font_head"])
        self.text(s, M, Inches(3.2), Inches(6.6), Inches(2.6), sd.get("bullets", []), 15, "#FFFFFF", bullets=True)
        self.text(s, M, Inches(6.2), Inches(6.6), Inches(0.6), sd.get("contact", ""), 13, self.t["secondary"], True)
        self.md.append(f"\n## {self.n}. {sd['title']}\n" + "\n".join(f"- {b}" for b in sd.get("bullets", [])))

    def build(self):
        for sd in self.d["slides"]:
            if sd.get("hidden"):
                continue
            getattr(self, "s_" + sd["type"])(sd)
            if sd.get("notes"):
                self.md.append(f"\n> Ghi chú thuyết trình: {sd['notes']}")
        name = self.d["meta"]["file"]
        out = self.proj / f"{name}.pptx"
        self.prs.save(out)
        (self.proj / f"{name}-noi-dung.md").write_text("\n".join(self.md) + "\n", encoding="utf-8")
        print(f"ok {out} ({self.n} slides)")


if __name__ == "__main__":
    Deck(Path(sys.argv[1]).resolve()).build()
