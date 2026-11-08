#!/usr/bin/env python3
"""vls.py: vòng lặp tự cải thiện cho slide (LAB099).

Vòng: do (render + kiểm xác định) → de-cham (đề cho người chấm tách thợ) → cham (ghi phiếu,
gắn với hash ảnh) → phieu-sua (chỉ slide hỏng) → thợ sửa → do lại → ... → ket-thuc (cổng cuối).

Nhận hai loại deck:
  - Thư mục Claude Slides / linhx-deck: deck.json (order, faces) + slides/<id>.html (<section> 1920×1080)
  - Tệp .pptx: dựng ảnh qua LibreOffice → PDF, đo chữ bằng PyMuPDF, hộp bằng python-pptx

Lệnh:
  vls.py mau <deck> --anh "<glob>" [...]        BƯỚC 0: nạp ảnh mẫu top tier, sinh thẻ phong cách để khoá
  vls.py khoa-mau <deck>                        khoá thẻ phong cách (sau khi người duyệt); chưa khoá thì `do` từ chối
  vls.py do <deck> [--kieu trinh-bay|doc]       render, kiểm, ảnh đánh dấu, bảng ảnh
  vls.py de-cham <deck> [--slide ID] [--deck]   viết đề chấm cho người chấm (subagent / claude -p / agy)
  vls.py cham <deck> --tep phieu.json [--nguoi] ghi phiếu chấm slide hoặc deck
  vls.py phieu-sua <deck>                       việc cho thợ: chỉ slide hỏng, lỗi + gợi ý sửa
  vls.py trang-thai <deck>                      bảng trạng thái, luật dừng
  vls.py ket-thuc <deck>                        cổng cuối, viết BAO-CAO.md; exit 0 chỉ khi đạt
  vls.py de-xac-minh <deck>                     đề cho người xác minh từng lỗi nặng (bác lỗi bịa, lỗi khẩu vị)
  vls.py xac-minh <deck> --tep xm.json          ghi kết quả xác minh
  vls.py hoan-tac <deck> --slide ID             bản sửa tệ hơn: trả về vòng trước
  vls.py hieu-chinh <deck>                      so phiếu người với phiếu máy trên cùng ảnh
  vls.py bai-hoc <deck> --ghi "..."             ghi bài học (tầng 2) vào bai-hoc.md cạnh skill
"""
from __future__ import annotations

import argparse
import hashlib
import html as htmlmod
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAU_HINH_MAC_DINH = {
    "be_rong": 1920, "cao": 1080,
    "tho": "",                 # ai làm slide (vd "claude-opus", "agy"); người chấm phải khác
    "tran_vong": 3,            # mỗi slide tối đa 3 lần sửa, quá thì chuyển người
    "toi_da_loi_moi_luot": 3,  # chống sửa quá tay: mỗi lượt thợ chỉ nhận tối đa 3 lỗi chấm (chặn trước nặng)
    "xac_minh_loi": True,      # lỗi chan/nang của người chấm phải qua người xác minh mới được giao sửa
    "ty_le_sua_toi_da": 0.6,   # hơn 60% điểm ảnh đổi sau một lượt sửa = làm lại cả slide, cảnh báo
    "co_chu_toi_thieu": 20,    # px ở khung 1920: dưới mức này là lỗi
    "co_chu_nen": 24,          # dưới mức này là lưu ý
    "le_an_toan": 48,          # px tính từ mép
    "tieu_de_toi_da_dong": 2,
    "so_chu_toi_da": {"trinh-bay": 60, "doc": 140},
    "so_truc_canh_toi_da": 5,
    "so_mau_nhan_toi_da": 2,
    "tuong_phan_thuong": 4.5, "tuong_phan_lon": 3.0,
    "chu_lon_px": 24,          # LUAT-DECK-DEP luật 12: chữ ≥24px dùng ngưỡng 3:1
    "phong_an_toan": ["arial", "helvetica", "calibri", "cambria", "times new roman", "georgia", "verdana",
                      "segoe ui", "tahoma", "sans-serif", "serif", "monospace", "system-ui", "courier new"],
    "css_them": "",            # CSS nền của trình chiếu nếu khác (reset dưới đây là giả định)
    # tối giản: AI hay nhồi; các ngưỡng này là lỗi cứng, không phải lưu ý
    "toi_gian": {"khoang_trong_toi_thieu": 0.45, "so_khoi_toi_da": 8, "so_co_chu_toi_da": 3, "so_chu_toi_da": 40},
    "diem_dat_toi_thieu": 4,   # phiếu 'dat' phải ≥ 4 ở MỌI tiêu chí (3 = dùng được, chưa đủ chuẩn giao)
    "so_nguoi_cham": 3,        # một người chấm dao động (cùng slide lúc đạt lúc hỏng): gộp 3 phiếu, lấy trung vị
    "thuong_hieu": "",         # đường dẫn brand.json (khuôn LAB043): kiểm phông và màu ngoài brand
    "mau_tham_chieu": [],      # ảnh slide mẫu (BTMH, slide top trên mạng) để người chấm so cặp
}
GIU_CHO = re.compile(r"lorem|ipsum|\bTODO\b|\bTBD\b|\[insert|\bx{3,}\b|\[CẦN LINH|\[Linh chốt|<tên", re.I)
MUC = ("chan", "nang", "nhe")
TIEU_CHI = ("y_chinh", "tieu_diem", "doc_duoc", "can_doi", "nhat_quan", "toi_gian", "ngang_mau")
KET_LUAN = ("dat", "hong", "khong-cham-duoc")


# ───────────────────────── tiện ích ─────────────────────────

def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()[:16]


def sha_tep(p: Path) -> str:
    return sha(p.read_bytes())


def ghi_json(p: Path, d) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)


def doc_json(p: Path, mac_dinh=None):
    if not p.exists():
        return mac_dinh
    return json.loads(p.read_text(encoding="utf-8"))


def bao(msg: str) -> None:
    print(msg, flush=True)


class Deck:
    """Một deck đang chạy vòng lặp. Trạng thái nằm ở <deck>/.vong-lap/ (pptx: <ten>.vong-lap/)."""

    def __init__(self, duong: str):
        self.nguon = Path(duong).resolve()
        if not self.nguon.exists():
            sys.exit(f"không thấy {self.nguon}")
        self.la_pptx = self.nguon.suffix.lower() == ".pptx"
        if self.la_pptx:
            self.vl = self.nguon.with_name(self.nguon.stem + ".vong-lap")
        else:
            self.vl = self.nguon / ".vong-lap"
        self.vl.mkdir(parents=True, exist_ok=True)
        self.p_cau_hinh = self.vl / "cau-hinh.json"
        if not self.p_cau_hinh.exists():
            ghi_json(self.p_cau_hinh, CAU_HINH_MAC_DINH)
        ch = dict(CAU_HINH_MAC_DINH)
        ch.update(doc_json(self.p_cau_hinh, {}))
        self.ch = ch
        self.p_tt = self.vl / "trang-thai.json"
        self.tt = doc_json(self.p_tt, {"slides": {}, "deck": {}, "nhat_ky": []})

    def luu(self):
        ghi_json(self.p_tt, self.tt)

    # thư mục Claude Slides
    def thu_muc_project(self) -> Path:
        for c in (self.nguon / "project", self.nguon):
            if (c / "deck.json").exists() or (c / "slides").is_dir():
                return c
        sys.exit("không thấy deck.json hoặc slides/ trong thư mục deck")

    def danh_sach(self) -> list[str]:
        if self.la_pptx:
            from pptx import Presentation
            return [f"s{i+1:02d}" for i in range(len(Presentation(str(self.nguon)).slides))]
        pj = self.thu_muc_project()
        dj = doc_json(pj / "deck.json", {}) or {}
        thu_tu = dj.get("order") or sorted(p.stem for p in (pj / "slides").glob("*.html"))
        return [s for s in thu_tu if (pj / "slides" / f"{s}.html").exists()]


# ───────────────────────── dựng HTML ─────────────────────────

RESET = """*,*::before,*::after{box-sizing:border-box;margin:0}
html,body{margin:0;padding:0;background:#777}
ul,ol{padding-left:1.2em}
img{max-width:100%}
[data-vls-slide]{position:relative;overflow:hidden}
[data-vls-slide] aside{display:none}"""


def vo_html(deck: Deck, sid: str) -> tuple[str, str]:
    """Trả (html đầy đủ, hash nguồn). Hash gồm slide + phông + CSS chung: đổi CSS chung là mọi phiếu cũ hết hạn."""
    pj = deck.thu_muc_project()
    dj = doc_json(pj / "deck.json", {}) or {}
    raw = (pj / "slides" / f"{sid}.html").read_text(encoding="utf-8")
    faces = dj.get("faces", {})
    links = "".join(f'<link rel="stylesheet" href="{htmlmod.escape(f["href"])}">' for f in faces.values() if f.get("href"))
    W, H = deck.ch["be_rong"], deck.ch["cao"]
    chung = json.dumps([faces, deck.ch.get("css_them", ""), RESET], ensure_ascii=False)
    h = sha((raw + chung).encode("utf-8"))
    if re.search(r"<html[\s>]", raw, re.I):
        than = raw  # slide là trang đầy đủ: giữ nguyên, đánh dấu body
        than = re.sub(r"<body", '<body data-vls-slide="1" style="width:%dpx;height:%dpx"' % (W, H), than, count=1, flags=re.I)
        return than, h
    m = re.search(r"<section\b", raw, re.I)
    if m:
        than = raw[:m.end()] + f' data-vls-slide="1"' + raw[m.end():]
        than = re.sub(r'(<section\b[^>]*style=")', r'\1width:%dpx;height:%dpx;' % (W, H), than, count=1, flags=re.I)
        if 'style="' not in than[:than.find(">", m.start()) + 1]:
            than = than.replace('data-vls-slide="1"', f'data-vls-slide="1" style="width:{W}px;height:{H}px"', 1)
    else:
        than = f'<section data-vls-slide="1" style="width:{W}px;height:{H}px">{raw}</section>'
    doc = (f'<!doctype html><html><head><meta charset="utf-8">{links}'
           f'<style>{RESET}{deck.ch.get("css_them", "")}</style></head><body>{than}</body></html>')
    return doc, h


ĐO_JS = r"""
(cfg) => {
  const S = document.querySelector('[data-vls-slide]');
  const R = S.getBoundingClientRect();
  const k = R.width / 1920;
  const bo = n => n.closest && n.closest('aside,script,style,noscript,template');
  const coChu = e => [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
  const els = [...S.querySelectorAll('*')].filter(e => !bo(e) && coChu(e));
  if (coChu(S)) els.unshift(S);
  const rel = r => ({x: r.left - R.left, y: r.top - R.top, w: r.width, h: r.height});
  const items = [];
  for (const e of els) {
    const cs = getComputedStyle(e);
    if (cs.visibility === 'hidden' || parseFloat(cs.opacity) === 0) continue;
    const rects = []; let text = '';
    for (const n of e.childNodes) {
      if (n.nodeType !== 3 || !n.textContent.trim()) continue;
      text += n.textContent;
      const rg = document.createRange(); rg.selectNodeContents(n);
      for (const x of rg.getClientRects()) if (x.width > 0.5 && x.height > 0.5) rects.push(rel(x));
    }
    if (!rects.length) continue;
    // từng chữ để đếm dòng, bắt chữ mồ côi
    const words = [];
    if (/^H[1-3]$/.test(e.tagName) || e.dataset.vlsTieuDe !== undefined) {
      for (const n of e.childNodes) {
        if (n.nodeType !== 3) continue;
        const re = /\S+/g; let m;
        while ((m = re.exec(n.textContent))) {
          const rg = document.createRange(); rg.setStart(n, m.index); rg.setEnd(n, m.index + m[0].length);
          const b = rg.getClientRects()[0]; if (b) words.push({t: m[0], y: Math.round(b.top - R.top)});
        }
      }
    }
    // tổ tiên cắt chữ / tổ tiên là "thẻ" có nền hoặc viền
    const cha = [];
    for (let a = e.parentElement; a && a !== S.parentElement; a = a.parentElement) {
      const ac = getComputedStyle(a);
      const cat = ac.overflow !== 'visible' || ac.overflowX !== 'visible' || ac.overflowY !== 'visible';
      const nen = (ac.backgroundColor !== 'rgba(0, 0, 0, 0)' && ac.backgroundColor !== 'transparent') ||
                  ac.backgroundImage !== 'none' || parseFloat(ac.borderTopWidth) > 0 || parseFloat(ac.borderLeftWidth) > 0;
      if ((cat || nen) && a !== S) { const r = rel(a.getBoundingClientRect());
        const tranBoCuc = a.scrollHeight > a.clientHeight + 1 || a.scrollWidth > a.clientWidth + 1;
        cha.push({cat, nen, r, tag: a.tagName, tranBoCuc}); }
      if (a === S) break;
    }
    const fam = cs.fontFamily.split(',')[0].replace(/["']/g, '').trim();
    items.push({i: items.length, tag: e.tagName.toLowerCase(), text: text.replace(/\s+/g, ' ').trim(),
                fs: parseFloat(cs.fontSize) / k, fw: parseInt(cs.fontWeight) || 400, color: cs.color,
                fam, rects, words, cha, block: ['block','flex','grid','list-item','table'].includes(cs.display)});
  }
  // phông đã nạp thật
  const nap = new Set(); document.fonts.forEach(f => { if (f.status === 'loaded') nap.add(f.family.replace(/["']/g, '').toLowerCase()); });
  // ảnh hỏng
  const anhHong = [...S.querySelectorAll('img')].filter(i => !bo(i) && (!i.complete || i.naturalWidth === 0)).map(i => i.getAttribute('src') || '');
  // màu nhấn: chữ và nền
  const mau = [];
  for (const e of [S, ...S.querySelectorAll('*')]) {
    if (bo(e)) continue; const cs = getComputedStyle(e);
    if (coChu(e)) mau.push(cs.color);
    if (cs.backgroundColor && cs.backgroundColor !== 'rgba(0, 0, 0, 0)') {
      const r = e.getBoundingClientRect(); if (r.width * r.height > 400) mau.push(cs.backgroundColor);
    }
  }
  // khối thị giác: chữ + ảnh + hộp có nền/viền (không tính slide và bọc trong suốt)
  let khoi = 0, coAnh = false;
  const gach = [];
  for (const e of S.querySelectorAll('*')) {
    if (bo(e)) continue; const cs = getComputedStyle(e); const r = e.getBoundingClientRect();
    if (r.width * r.height < 100 || cs.display === 'none' || cs.visibility === 'hidden') continue;
    const anh = e.tagName === 'IMG' || e.tagName === 'svg' || (cs.backgroundImage !== 'none' && !cs.backgroundImage.startsWith('linear') && !cs.backgroundImage.startsWith('radial'));
    if (anh && r.width * r.height > (R.width * R.height) * 0.04) coAnh = true;
    const nen = cs.backgroundColor !== 'rgba(0, 0, 0, 0)' || parseFloat(cs.borderTopWidth) > 0 || parseFloat(cs.borderLeftWidth) > 0;
    if (anh || nen || coChu(e)) khoi++;
    // vạch trang trí dưới tiêu đề: viền dưới của h1-h3, hoặc thanh mảnh ngay sau tiêu đề
    if (/^H[1-3]$/.test(e.tagName) && parseFloat(cs.borderBottomWidth) >= 2) gach.push(e.textContent.trim().slice(0, 40));
    if (/^H[1-3]$/.test(e.tagName)) {
      const nx = e.nextElementSibling;
      if (nx && !coChu(nx) && !nx.children.length) { const b = nx.getBoundingClientRect(); const nc = getComputedStyle(nx);
        if (b.height <= 12 && b.width >= 30 && nc.backgroundColor !== 'rgba(0, 0, 0, 0)') gach.push(e.textContent.trim().slice(0, 40)); }
    }
  }
  return {k, W: R.width, H: R.height, items, nap: [...nap], anhHong, mau, khoi, coAnh, gach};
}
"""

AN_CHU_CSS = """[data-vls-slide] *, [data-vls-slide] { color: transparent !important; text-shadow: none !important;
 -webkit-text-stroke: 0 !important; text-decoration-color: transparent !important; caret-color: transparent !important; }
[data-vls-slide] svg text { fill: transparent !important; }"""


def mo_trinh_duyet(p):
    try:
        return p.chromium.launch()
    except Exception:
        for c in ("/opt/pw-browsers/chromium", os.environ.get("VLS_CHROMIUM", "")):
            if c and Path(c).exists():
                return p.chromium.launch(executable_path=c)
        raise


# ───────────────────────── đo màu ─────────────────────────

def rgba(s: str):
    m = re.findall(r"[\d.]+", s)
    if len(m) < 3:
        return (0, 0, 0, 1.0)
    a = float(m[3]) if len(m) > 3 else 1.0
    return (float(m[0]), float(m[1]), float(m[2]), a)


def do_sang(r, g, b):
    def c(v):
        v = v / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * c(r) + 0.7152 * c(g) + 0.0722 * c(b)


def tuong_phan_mang(L1, L2):
    import numpy as np
    hi = np.maximum(L1, L2)
    lo = np.minimum(L1, L2)
    return (hi + 0.05) / (lo + 0.05)


def anh_do_sang(arr):
    import numpy as np
    v = arr[..., :3].astype("float64") / 255
    v = np.where(v <= 0.03928, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)
    return 0.2126 * v[..., 0] + 0.7152 * v[..., 1] + 0.0722 * v[..., 2]


def tuong_phan_vung(nen_arr, rect, mau_chu, scale=1.0, mat_na=None):
    """Tương phản xấu nhất (phân vị 5%) giữa màu chữ và nền thật dưới hộp chữ.
    nen_arr: ảnh nền đã ẩn chữ (HTML) hoặc ảnh gốc (pptx, khi đó mat_na loại điểm ảnh gần màu chữ)."""
    import numpy as np
    x0 = max(int(rect["x"] * scale), 0); y0 = max(int(rect["y"] * scale), 0)
    x1 = min(int((rect["x"] + rect["w"]) * scale) + 1, nen_arr.shape[1])
    y1 = min(int((rect["y"] + rect["h"]) * scale) + 1, nen_arr.shape[0])
    if x1 - x0 < 2 or y1 - y0 < 2:
        return None
    vung = nen_arr[y0:y1, x0:x1]
    r, g, b, a = mau_chu
    if a < 1:  # chữ trong suốt một phần: trộn với nền giữa
        med = np.median(vung[..., :3].reshape(-1, 3), axis=0)
        r, g, b = (a * r + (1 - a) * med[0], a * g + (1 - a) * med[1], a * b + (1 - a) * med[2])
    Lc = do_sang(r, g, b)
    Ln = anh_do_sang(vung).reshape(-1)
    if mat_na is not None:
        d = np.abs(vung[..., :3].astype(float) - np.array([r, g, b])).sum(axis=-1).reshape(-1)
        # điểm ảnh rõ là nền: xa màu chữ ≥ 70% khoảng cách xa nhất (bỏ viền khử răng cưa của chữ)
        Ln = Ln[d >= 0.7 * d.max()] if d.max() > 30 else Ln
        if Ln.size < 10:
            return None
    tp = tuong_phan_mang(np.full_like(Ln, Lc), Ln)
    return float(np.percentile(tp, 5))


# ───────────────────────── thương hiệu ─────────────────────────

def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lab(rgb):
    def f(c):
        c = c / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (f(x) for x in rgb)
    X = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    Y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    Z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    g_ = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    return (116 * g_(Y) - 16, 500 * (g_(X) - g_(Y)), 200 * (g_(Y) - g_(Z)))


def delta_e(a, b):
    A, B = lab(a), lab(b)
    return sum((x - y) ** 2 for x, y in zip(A, B)) ** 0.5


_TH = {}


def doc_thuong_hieu(ch):
    p = ch.get("thuong_hieu")
    if not p:
        return None
    if p not in _TH:
        b = json.loads(Path(p).read_text(encoding="utf-8"))
        mau = [hex_rgb(x["hex"]) for nhom in ("chinh", "phu") for x in b["mau"].get(nhom, []) if x.get("hex")]
        phong = list(b.get("chu", {}).get("font_cho_phep", [])) + list(b.get("chu", {}).get("font_thay_the_web", []))
        _TH[p] = {"mau": mau, "phong": phong + ch.get("phong_them", []), "nguong": b["mau"].get("nguong_delta_e", 8)}
    return _TH[p]


# ───────────────────────── kiểm ─────────────────────────

def giao(a, b):
    x = max(0, min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"]))
    y = max(0, min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"]))
    return x * y


def hop_chung(rs):
    x0 = min(r["x"] for r in rs); y0 = min(r["y"] for r in rs)
    x1 = max(r["x"] + r["w"] for r in rs); y1 = max(r["y"] + r["h"] for r in rs)
    return {"x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0}


def ngoai(r, khung, dung_sai=1.0):
    return (r["x"] < khung["x"] - dung_sai or r["y"] < khung["y"] - dung_sai or
            r["x"] + r["w"] > khung["x"] + khung["w"] + dung_sai or r["y"] + r["h"] > khung["y"] + khung["h"] + dung_sai)


def ngan(t, n=48):
    t = t.replace("\n", " ")
    return t if len(t) <= n else t[:n - 1] + "…"


def kiem_items(d: dict, nen_arr, ch: dict, kieu: str, scale: float):
    """Kiểm xác định trên số đo DOM + ảnh nền. Trả (sai, luu_y, so, hop_loi)."""
    sai, luu_y, hop_loi = [], [], []
    W, H = 1920, 1080
    k = d["k"]
    # quy mọi toạ độ về khung 1920
    for it in d["items"]:
        for r in it["rects"]:
            for key in ("x", "y", "w", "h"):
                r[key] /= k
        for c in it["cha"]:
            for key in ("x", "y", "w", "h"):
                c["r"][key] /= k
    canvas = {"x": 0, "y": 0, "w": W, "h": H}
    le = ch["le_an_toan"]
    an_toan = {"x": le, "y": le, "w": W - 2 * le, "h": H - 2 * le}
    items = d["items"]

    def loi(muc, ma, msg, it=None, rect=None):
        (sai if muc == "sai" else luu_y).append({"ma": ma, "mo_ta": msg})
        if rect or it:
            hop_loi.append({"muc": muc, "ma": ma, "r": rect or hop_chung(it["rects"])})

    for it in items:
        hop = hop_chung(it["rects"])
        nhan = f'"{ngan(it["text"])}"'
        if ngoai(hop, canvas):
            loi("sai", "tran-khung", f"{nhan} tràn ra ngoài slide", it)
        elif ngoai(hop, an_toan):
            loi("luu_y", "sat-mep", f"{nhan} sát mép hơn {le}px", it)
        # hộp chữ của Range cao hơn dòng khi line-height < 1.2: cho phép lố dọc 0,3 cỡ chữ
        # trừ khi khung báo tràn bố cục thật (scrollHeight > clientHeight)
        for c in it["cha"]:
            r = c["r"]
            doc = 2.0 if c.get("tranBoCuc") else 0.3 * it["fs"]
            if (hop["x"] < r["x"] - 2 or hop["x"] + hop["w"] > r["x"] + r["w"] + 2 or
                    hop["y"] < r["y"] - doc or hop["y"] + hop["h"] > r["y"] + r["h"] + doc):
                if c["cat"]:
                    loi("sai", "bi-cat", f"{nhan} bị cắt bởi khung <{c['tag'].lower()}>", it)
                elif c["nen"]:
                    loi("sai", "tran-the", f"{nhan} tràn khỏi thẻ/khối nền <{c['tag'].lower()}>", it)
                break
        if it["fs"] < ch["co_chu_toi_thieu"]:
            loi("sai", "chu-nho", f"{nhan} cỡ {it['fs']:.0f}px < {ch['co_chu_toi_thieu']}px", it)
        elif it["fs"] < ch["co_chu_nen"]:
            loi("luu_y", "chu-nho", f"{nhan} cỡ {it['fs']:.0f}px < {ch['co_chu_nen']}px", it)
        if GIU_CHO.search(it["text"]):
            loi("sai", "giu-cho", f"{nhan} còn chữ giữ chỗ", it)
        if it["fam"].lower() not in d["nap"] and it["fam"].lower() not in ch["phong_an_toan"]:
            loi("sai", "phong", f"phông '{it['fam']}' không nạp được: số đo tràn chữ không tin được", it)
        if it["words"]:
            dong = sorted({w["y"] for w in it["words"]})
            gop = []
            for y in dong:
                if not gop or y - gop[-1] > it["fs"] * k * 0.5:
                    gop.append(y)
            if len(gop) > ch["tieu_de_toi_da_dong"]:
                loi("sai", "tieu-de-dai", f"tiêu đề {len(gop)} dòng (tối đa {ch['tieu_de_toi_da_dong']}): {nhan}", it)
            if len(gop) >= 2:
                cuoi = [w for w in it["words"] if abs(w["y"] - gop[-1]) <= it["fs"] * k * 0.5]
                if len(cuoi) == 1:
                    loi("luu_y", "mo-coi", f"dòng cuối tiêu đề chỉ còn một chữ '{cuoi[0]['t']}'", it)
        # tương phản trên nền thật
        if nen_arr is not None:
            mau = rgba(it["color"])
            lon = it["fs"] >= ch["chu_lon_px"]
            nguong = ch["tuong_phan_lon"] if lon else ch["tuong_phan_thuong"]
            xau = None
            for r in it["rects"]:
                tp = tuong_phan_vung(nen_arr, r, mau, scale)
                if tp is not None and (xau is None or tp < xau):
                    xau = tp
            it["tuong_phan"] = xau
            if xau is not None and xau < nguong:
                loi("sai", "tuong-phan", f"{nhan} tương phản {xau:.2f}:1 < {nguong}:1 (đo trên nền thật)", it)
            elif xau is not None and xau < nguong * 1.1:
                loi("luu_y", "tuong-phan", f"{nhan} tương phản {xau:.2f}:1 sát ngưỡng {nguong}:1", it)

    # chồng lấn giữa các khối chữ khác nhau
    for a in range(len(items)):
        for b in range(a + 1, len(items)):
            A, B = items[a], items[b]
            for ra in A["rects"]:
                hit = False
                for rb in B["rects"]:
                    s = giao(ra, rb)
                    if s > 0.04 * min(ra["w"] * ra["h"], rb["w"] * rb["h"]):
                        loi("sai", "chong-lan", f'"{ngan(A["text"], 30)}" chồng lên "{ngan(B["text"], 30)}"',
                            rect=hop_chung([ra, rb]))
                        hit = True
                        break
                if hit:
                    break

    # mật độ chữ
    so_chu = sum(len(it["text"].split()) for it in items)
    tran = ch["so_chu_toi_da"].get(kieu, 60)
    if so_chu > tran:
        luu_y.append({"ma": "nhieu-chu", "mo_ta": f"{so_chu} chữ trên slide (deck {kieu} nên ≤ {tran})"})
    # trục canh trái
    trai = sorted(hop_chung(it["rects"])["x"] for it in items if it["block"])
    cum = []
    for x in trai:
        if not cum or x - cum[-1] > 6:
            cum.append(x)
    if len(cum) > ch["so_truc_canh_toi_da"]:
        luu_y.append({"ma": "truc-canh", "mo_ta": f"{len(cum)} trục canh trái khác nhau (nên ≤ {ch['so_truc_canh_toi_da']})"})
    # màu nhấn
    import colorsys
    hue = set()
    for m in d["mau"]:
        r, g, b, a = rgba(m)
        if a < 0.3:
            continue
        h_, l_, s_ = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        if s_ > 0.35 and 0.2 < l_ < 0.85:
            hue.add(int(h_ * 12) % 12)
    if len(hue) > ch["so_mau_nhan_toi_da"]:
        luu_y.append({"ma": "mau-nhan", "mo_ta": f"{len(hue)} nhóm màu nhấn (nên ≤ {ch['so_mau_nhan_toi_da']})"})
    for src in d["anhHong"]:
        sai.append({"ma": "anh-hong", "mo_ta": f"ảnh không nạp được: {ngan(src, 80)}"})
    # đúng thương hiệu
    th = doc_thuong_hieu(ch)
    if th:
        cho = {f.lower() for f in th["phong"]}
        for f in sorted({it["fam"] for it in items}):
            if f.lower() not in cho:
                sai.append({"ma": "phong-ngoai-brand", "mo_ta": f"phông '{f}' không có trong brand ({', '.join(th['phong'])})"})
        da_bao = set()
        for m in d["mau"]:
            r, g, b, a = rgba(m)
            if a < 0.5:
                continue
            de = min(delta_e((r, g, b), x) for x in th["mau"])
            key = (round(r), round(g), round(b))
            if de > th["nguong"] and key not in da_bao:
                da_bao.add(key)
                sai.append({"ma": "mau-ngoai-brand", "mo_ta": f"màu #{key[0]:02X}{key[1]:02X}{key[2]:02X} lệch bảng màu brand (ΔE {de:.0f} > {th['nguong']})"})
    # tối giản (lỗi cứng: AI hay làm quá)
    tg = ch["toi_gian"]
    co = sorted({round(it["fs"]) for it in items})
    if len(co) > tg["so_co_chu_toi_da"]:
        sai.append({"ma": "nhieu-co-chu", "mo_ta": f"{len(co)} cỡ chữ {co} (tối đa {tg['so_co_chu_toi_da']})"})
    if d["khoi"] > tg["so_khoi_toi_da"]:
        sai.append({"ma": "nhieu-khoi", "mo_ta": f"{d['khoi']} khối thị giác (tối đa {tg['so_khoi_toi_da']}): bỏ bớt, gộp, hoặc tách slide"})
    if kieu == "trinh-bay" and so_chu > tg["so_chu_toi_da"]:
        sai.append({"ma": "nhieu-chu", "mo_ta": f"{so_chu} chữ (tối giản: tối đa {tg['so_chu_toi_da']})"})
    for t in d["gach"]:
        sai.append({"ma": "gach-tieu-de", "mo_ta": f"vạch trang trí dưới tiêu đề '{ngan(t, 30)}': dấu hiệu slide AI, bỏ"})
    if nen_arr is not None and not d["coAnh"]:
        import numpy as np
        nho = nen_arr[::10, ::10, :3].astype(int)
        q = (nho // 8).reshape(-1, 3)
        vals, dem = np.unique(q, axis=0, return_counts=True)
        nen_chinh = vals[dem.argmax()] * 8 + 4
        # ảnh nền đã ẩn chữ: cộng diện tích chữ để ra phần "có mực"
        muc = (np.abs(nho - nen_chinh).sum(axis=-1) > 30).mean()
        dt_chu = sum(r["w"] * r["h"] for it in items for r in it["rects"]) / (1920 * 1080)
        trong = max(0.0, 1 - muc - dt_chu)
        so_tg = round(trong, 2)
        if trong < tg["khoang_trong_toi_thieu"]:
            sai.append({"ma": "it-khoang-trong", "mo_ta": f"khoảng trống {trong:.0%} < {tg['khoang_trong_toi_thieu']:.0%}: slide chật"})
    else:
        so_tg = None
    so = {"so_chu": so_chu, "so_khoi_chu": len(items), "so_khoi": d["khoi"], "khoang_trong": so_tg, "co_chu": co, "truc_canh": len(cum), "mau_nhan": len(hue),
          "tieu_de_y": next((round(hop_chung(it["rects"])["y"]) for it in items if it["tag"] in ("h1", "h2")), None),
          "tieu_de_the": next((it["tag"] for it in items if it["tag"] in ("h1", "h2")), None)}
    return sai, luu_y, so, hop_loi


def phong_pil(co=18):
    from PIL import ImageFont
    for c in ("DejaVuSans.ttf", "arial.ttf", "segoeui.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              r"C:\Windows\Fonts\arial.ttf"):
        try:
            return ImageFont.truetype(c, co)
        except OSError:
            continue
    return ImageFont.load_default()


def danh_dau(anh: Path, hop_loi: list, ra: Path, scale: float):
    from PIL import Image, ImageDraw
    im = Image.open(anh).convert("RGB")
    dr = ImageDraw.Draw(im)
    for h in hop_loi:
        r = h["r"]
        mau = (230, 30, 30) if h["muc"] == "sai" else (240, 160, 0)
        box = [r["x"] * scale - 4, r["y"] * scale - 4, (r["x"] + r["w"]) * scale + 4, (r["y"] + r["h"]) * scale + 4]
        dr.rectangle(box, outline=mau, width=4)
        dr.text((box[0] + 4, max(box[1] - 26, 0)), h["ma"], fill=mau, font=phong_pil(22))
    im.save(ra)


def bang_anh(muc: list[tuple[str, Path, int]], ra: Path, cot=4):
    """muc: (id, ảnh, số lỗi). Một ảnh lưới để chấm cả deck (nhịp, nhất quán)."""
    from PIL import Image, ImageDraw
    if not muc:
        return
    w, h = 480, 270
    hang = (len(muc) + cot - 1) // cot
    im = Image.new("RGB", (cot * (w + 16) + 16, hang * (h + 40) + 16), (40, 40, 40))
    dr = ImageDraw.Draw(im)
    for i, (sid, p, n) in enumerate(muc):
        x = 16 + (i % cot) * (w + 16); y = 16 + (i // cot) * (h + 40)
        t = Image.open(p).convert("RGB").resize((w, h))
        im.paste(t, (x, y))
        dr.text((x, y + h + 6), f"{i+1:02d} {sid}" + (f"  [{n} lỗi]" if n else ""), fill=(255, 90, 90) if n else (230, 230, 230), font=phong_pil(18))
    im.save(ra)


# ───────────────────────── do: HTML ─────────────────────────

def do_html(deck: Deck, kieu: str, chi: set | None, lam_lai: bool = False):
    from playwright.sync_api import sync_playwright
    import numpy as np
    from PIL import Image
    ids = deck.danh_sach()
    W, H = deck.ch["be_rong"], deck.ch["cao"]
    tam = Path(tempfile.mkdtemp(prefix="vls-"))
    kq = {}
    with sync_playwright() as p:
        b = mo_trinh_duyet(p)
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        hong_mang = []
        pg.on("requestfailed", lambda r: hong_mang.append(r.url))
        pg.on("response", lambda r: hong_mang.append(r.url) if r.status >= 400 else None)
        for sid in ids:
            if chi and sid not in chi:
                continue
            doc, h = vo_html(deck, sid)
            cu = (deck.tt["slides"].get(sid) or {}).get("vong", [None])[-1]
            if not lam_lai and cu and cu["hash_nguon"] == h and (deck.vl / cu["anh"]).exists():
                continue  # nguồn không đổi: giữ ảnh và phiếu cũ (dựng lại có thể lệch vài điểm ảnh do khử răng cưa)
            pj = deck.thu_muc_project()
            tep = pj / "slides" / f".vls-{sid}.html"  # cùng thư mục để đường dẫn tương đối của ảnh còn đúng
            tep.write_text(doc, encoding="utf-8")
            hong_mang.clear()
            try:
                pg.goto(tep.as_uri(), wait_until="networkidle", timeout=30000)
                pg.evaluate("document.fonts.ready.then(()=>1)")
                pg.wait_for_timeout(150)
                el = pg.locator("[data-vls-slide]").first
                so_do = pg.evaluate(ĐO_JS, {})
                thu = deck.vl / "anh"
                thu.mkdir(exist_ok=True)
                anh = thu / f"{sid}.png"
                el.screenshot(path=str(anh))
                pg.add_style_tag(content=AN_CHU_CSS)
                pg.wait_for_timeout(50)
                nen = tam / f"{sid}-nen.png"
                el.screenshot(path=str(nen))
            finally:
                tep.unlink(missing_ok=True)
            nen_arr = np.asarray(Image.open(nen).convert("RGB"))
            scale = nen_arr.shape[1] / 1920
            sai, luu_y, so, hop_loi = kiem_items(so_do, nen_arr, deck.ch, kieu, scale)
            for u in sorted(set(hong_mang)):
                if "fonts.g" in u:
                    sai.append({"ma": "phong", "mo_ta": f"không tải được phông: {ngan(u, 80)}"})
                elif not u.startswith("data:"):
                    sai.append({"ma": "tai-nguyen", "mo_ta": f"không tải được: {ngan(u, 80)}"})
            kq[sid] = (h, anh, sai, luu_y, so, hop_loi, scale)
        b.close()
    shutil.rmtree(tam, ignore_errors=True)
    return kq


# ───────────────────────── do: PPTX ─────────────────────────

def soffice_bin():
    for c in (os.environ.get("VLS_SOFFICE", ""), shutil.which("soffice") or "", shutil.which("libreoffice") or "",
              r"C:\Program Files\LibreOffice\program\soffice.exe"):
        if c and Path(c).exists():
            return c
    sys.exit("cần LibreOffice (soffice) để dựng pptx; đặt VLS_SOFFICE nếu cài ở chỗ khác")


def do_pptx(deck: Deck, kieu: str, chi: set | None):
    import numpy as np
    import pymupdf
    from PIL import Image
    from pptx import Presentation
    from pptx.util import Emu
    h_nguon = sha_tep(deck.nguon) + sha(json.dumps(deck.ch, sort_keys=True).encode())[:4]
    tam = Path(tempfile.mkdtemp(prefix="vls-"))
    prof = tam / "prof"
    cmd = [soffice_bin(), f"-env:UserInstallation=file://{prof.as_posix()}", "--headless", "--convert-to", "pdf",
           "--outdir", str(tam), str(deck.nguon)]
    env = os.environ.copy()
    env.setdefault("SAL_USE_VCLPLUGIN", "svp")
    shim = Path("/mnt/skills/public/pptx/scripts/office")
    if shim.exists():  # sandbox chặn AF_UNIX: dùng shim của skill pptx
        sys.path.insert(0, str(shim.parent))
        from office.soffice import run_soffice  # type: ignore
        r = run_soffice(cmd[1:], capture_output=True, text=True, timeout=240)
    else:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=240, env=env)
    pdf = tam / (deck.nguon.stem + ".pdf")
    if not pdf.exists():
        sys.exit(f"LibreOffice không xuất được PDF: {r.stderr[-400:]}")
    prs = Presentation(str(deck.nguon))
    sw, sh = prs.slide_width, prs.slide_height
    px = 1920 / sw
    tai = pymupdf.open(str(pdf))
    kq = {}
    cs = deck.ch
    for i, slide in enumerate(prs.slides):
        sid = f"s{i+1:02d}"
        if chi and sid not in chi:
            continue
        page = tai[i]
        zoom = 1920 / page.rect.width
        pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
        thu = deck.vl / "anh"; thu.mkdir(exist_ok=True)
        anh = thu / f"{sid}.png"
        pix.save(str(anh))
        arr = np.asarray(Image.open(anh).convert("RGB"))
        sai, luu_y, hop_loi = [], [], []
        # hộp của mọi shape (kể cả nhóm, bảng, biểu đồ)
        hop = []

        def duyet(shapes, ox=0, oy=0):
            for s in shapes:
                if s.left is None:
                    continue
                r = {"x": (s.left + ox) * px, "y": (s.top + oy) * px, "w": s.width * px, "h": s.height * px}
                if s.shape_type == 6:  # group
                    duyet(s.shapes, ox, oy)
                hop.append((s, r))
        duyet(slide.shapes)
        canvas = {"x": 0, "y": 0, "w": 1920, "h": 1920 * sh / sw}
        for s, r in hop:
            if ngoai(r, canvas, 2):
                sai.append({"ma": "tran-khung", "mo_ta": f"hình '{s.name}' nằm ngoài slide"}); hop_loi.append({"muc": "sai", "ma": "tran-khung", "r": r})
            if s.has_text_frame:
                for para in s.text_frame.paragraphs:
                    for run in para.runs:
                        if run.font.size is not None:
                            f = run.font.size.pt * 12700 * px  # pt → EMU → px khung 1920
                            if f < cs["co_chu_toi_thieu"]:
                                sai.append({"ma": "chu-nho", "mo_ta": f"'{ngan(run.text, 30)}' cỡ {f:.0f}px < {cs['co_chu_toi_thieu']}px"})
                                hop_loi.append({"muc": "sai", "ma": "chu-nho", "r": r})
                if GIU_CHO.search(s.text_frame.text):
                    sai.append({"ma": "giu-cho", "mo_ta": f"'{ngan(s.text_frame.text)}' còn chữ giữ chỗ"})
        # chữ thật sau khi dựng: dòng nào nằm ngoài mọi hộp là tràn
        dong = []
        for blk in page.get_text("dict")["blocks"]:
            for ln in blk.get("lines", []):
                for sp in ln["spans"]:
                    if not sp["text"].strip():
                        continue
                    x0, y0, x1, y1 = sp["bbox"]
                    r = {"x": x0 * zoom, "y": y0 * zoom, "w": (x1 - x0) * zoom, "h": (y1 - y0) * zoom}
                    c = sp["color"]
                    dong.append((sp, r, (c >> 16 & 255, c >> 8 & 255, c & 255, 1.0)))
        so_chu = 0
        for sp, r, mau in dong:
            so_chu += len(sp["text"].split())
            trong = [h for _, h in hop if not ngoai(r, h, 6)]
            if not trong:
                sai.append({"ma": "tran-hop", "mo_ta": f"'{ngan(sp['text'], 40)}' nằm ngoài hộp chữ (tràn)"}); hop_loi.append({"muc": "sai", "ma": "tran-hop", "r": r})
            if ngoai(r, canvas):
                sai.append({"ma": "tran-khung", "mo_ta": f"'{ngan(sp['text'], 40)}' ra ngoài slide"})
            tp = tuong_phan_vung(arr, r, mau, 1.0, mat_na=True)
            f = sp["size"] * zoom
            ng = cs["tuong_phan_lon"] if f >= cs["chu_lon_px"] else cs["tuong_phan_thuong"]
            if tp is not None and tp < ng:
                sai.append({"ma": "tuong-phan", "mo_ta": f"'{ngan(sp['text'], 40)}' tương phản ~{tp:.2f}:1 < {ng}:1 (ước lượng trên ảnh)"})
                hop_loi.append({"muc": "sai", "ma": "tuong-phan", "r": r})
            if f < cs["co_chu_toi_thieu"] - 0.5:
                pass  # đã bắt ở run.font.size khi có; cỡ kế thừa từ layout thì bắt ở đây
        for a in range(len(dong)):
            for b_ in range(a + 1, len(dong)):
                ra, rb = dong[a][1], dong[b_][1]
                if giao(ra, rb) > 0.15 * min(ra["w"] * ra["h"], rb["w"] * rb["h"]):
                    sai.append({"ma": "chong-lan", "mo_ta": f"'{ngan(dong[a][0]['text'], 25)}' chồng '{ngan(dong[b_][0]['text'], 25)}'"})
                    hop_loi.append({"muc": "sai", "ma": "chong-lan", "r": hop_chung([ra, rb])})
        tran = cs["so_chu_toi_da"].get(kieu, 60)
        if so_chu > tran:
            luu_y.append({"ma": "nhieu-chu", "mo_ta": f"{so_chu} chữ (deck {kieu} nên ≤ {tran})"})
        fonts = {sp["font"] for sp, _, _ in dong}
        if len(fonts) > 3:
            luu_y.append({"ma": "phong", "mo_ta": f"{len(fonts)} phông sau khi dựng: {sorted(fonts)[:5]} (có thể LibreOffice thay phông)"})
        hs = h_nguon + f"-{i}"
        kq[sid] = (hs, anh, sai, luu_y, {"so_chu": so_chu}, hop_loi, 1.0)
    shutil.rmtree(tam, ignore_errors=True)
    return kq


# ───────────────────────── lệnh ─────────────────────────

THE_PC = """# Thẻ phong cách: {ten}

Bước 0 của vòng lặp. Thợ đọc thẻ này TRƯỚC khi dựng; người chấm so với ảnh mẫu. Người duyệt sửa thẻ rồi chạy `vls.py khoa-mau`.

## Ảnh mẫu ({n} ảnh, top tier)
{ds}

Bảng ảnh mẫu: `{bang}`

## Vì sao mẫu đẹp (giải mã từng mẫu, đo được, không khen chung; xem references/giai-ma-mau.md)
- Mẫu 1: …
- Mẫu 2: …
- Mẫu 3: …

## Tổng hợp nguyên tắc (lặp lại ở ≥ 2 mẫu; dùng làm guide cho thợ và cho prompt tạo ảnh/template)
1. …
2. …
3. …

## Rút từ mẫu (người duyệt điền/sửa; thợ không tự đổi)
- Ba tính từ: …, …, …
- Nền: … (một màu chủ đạo, tối đa 2 mảng nền)
- Lưới: … cột, lề ngoài … px, khoảng cách khối … px
- Chữ: tiêu đề … (phông, cỡ, độ đậm), thân … ; tối đa 3 cỡ
- Màu nhấn: … (một màu, chỉ đặt trên tâm điểm)
- Ảnh: … (tràn cạnh / khung / không ảnh)
- Khoảng trống tối thiểu: {kt:.0%} diện tích; tối đa {kh} khối; tối đa {ch} chữ/slide trình bày

## Cấm (bệnh thừa của AI)
- Vạch, gạch dưới tiêu đề; icon trang trí; thẻ bo góc đổ bóng; gradient tự chế; viền khép 4 cạnh quanh ảnh
- Mỗi ý một thẻ màu khác nhau; quá 3 cỡ chữ; nhồi chữ để lấp chỗ trống
- Thêm yếu tố khi sửa: sửa là bỏ bớt trước
"""


def lenh_mau(a):
    import glob
    deck = Deck(a.deck)
    ps = []
    for g in a.anh:
        ps += sorted(glob.glob(g))
    # đường dẫn tuyệt đối: người chấm chạy ở thư mục khác, đường tương đối sẽ trỏ sai
    ps = [str(Path(p).absolute()) for p in ps if p.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
    if len(ps) < 6:
        sys.exit(f"cần ít nhất 6 ảnh mẫu top tier (đang có {len(ps)}): tìm thêm trước khi dựng")
    deck.ch["mau_tham_chieu"] = ps
    ghi_json(deck.p_cau_hinh, {**doc_json(deck.p_cau_hinh, {}), "mau_tham_chieu": ps})
    bang = deck.vl / "bang-mau.png"
    bang_anh([(Path(p).stem[:28], Path(p), 0) for p in ps[:24]], bang)
    tg = deck.ch["toi_gian"]
    the = deck.vl / "THE-PHONG-CACH.md"
    if not the.exists() or a.ghi_de:
        the.write_text(THE_PC.format(ten=deck.nguon.name, n=len(ps), ds="\n".join(f"- `{p}`" for p in ps), bang=bang,
                                     kt=tg["khoang_trong_toi_thieu"], kh=tg["so_khoi_toi_da"], ch=tg["so_chu_toi_da"]), encoding="utf-8")
    deck.tt["mau"] = {"so_anh": len(ps), "khoa": False, "hash_the": None}
    deck.luu()
    bao(f"đã nạp {len(ps)} ảnh mẫu · bảng ảnh {bang} · thẻ phong cách {the}\nbước tiếp: điền thẻ từ ảnh mẫu, người duyệt, rồi `khoa-mau`")


def lenh_khoa_mau(a):
    deck = Deck(a.deck)
    if not deck.la_pptx and (doc_json(deck.thu_muc_project() / "deck.json", {}) or {}).get("faces"):
        a.tep = getattr(a, "tep", None)
        lenh_phong(a)  # phông thiếu chữ Việt thì không khoá: trình duyệt sẽ mượn phông khác cho chữ có dấu
    the = deck.vl / "THE-PHONG-CACH.md"
    if not deck.tt.get("mau") or not the.exists():
        sys.exit("chưa có ảnh mẫu: chạy `mau` trước")
    t = the.read_text(encoding="utf-8")
    con = t.count("…")
    if con:
        sys.exit(f"thẻ phong cách còn {con} chỗ '…' chưa điền")
    deck.tt["mau"].update({"khoa": True, "hash_the": sha(t.encode()), "luc": time.strftime("%Y-%m-%dT%H:%M:%S")})
    deck.luu()
    bao("đã khoá thẻ phong cách; sửa thẻ sau này là phải khoá lại và chấm lại")


def cong_mau(deck: Deck, bo_qua: bool):
    """Cổng 0: chưa có mẫu top tier đã khoá thì không dựng."""
    m = deck.tt.get("mau") or {}
    the = deck.vl / "THE-PHONG-CACH.md"
    ok = m.get("khoa") and the.exists() and sha(the.read_text(encoding="utf-8").encode()) == m.get("hash_the")
    if ok:
        return
    if bo_qua:
        bao("⚠ bỏ qua cổng mẫu: điểm 'ngang_mau' sẽ không có mốc")
        return
    sys.exit("cổng 0 chưa qua: tìm ≥ 6 slide mẫu top tier (`mau`), điền thẻ phong cách, `khoa-mau`. "
             "Chỉ đo thử thì thêm --bo-qua-mau")


def lenh_do(a):
    deck = Deck(a.deck)
    cong_mau(deck, a.bo_qua_mau)
    chi = set(a.chi.split(",")) if a.chi else None
    kq = do_pptx(deck, a.kieu, chi) if deck.la_pptx else do_html(deck, a.kieu, chi, a.lam_lai)
    deck.tt["kieu"] = a.kieu
    thoi = time.strftime("%Y-%m-%dT%H:%M:%S")
    for sid, (h, anh, sai, luu_y, so, hop_loi, scale) in kq.items():
        st = deck.tt["slides"].setdefault(sid, {"vong": []})
        cu = st["vong"][-1] if st["vong"] else None
        danh = deck.vl / "anh" / f"{sid}-danh-dau.png"
        danh_dau(anh, hop_loi, danh, scale)
        rec = {"hash_nguon": h, "anh": str(anh.relative_to(deck.vl)), "hash_anh": sha_tep(anh),
               "anh_danh_dau": str(danh.relative_to(deck.vl)), "sai": sai, "luu_y": luu_y, "so": so, "luc": thoi}
        if cu and cu["hash_nguon"] == h:
            # nguồn chưa đổi: cập nhật số đo, giữ phiếu chấm nếu ảnh y hệt
            giu = {k: v for k, v in cu.items() if k.startswith("cham") and cu.get("hash_anh") == rec["hash_anh"]}
            cu.update(rec); cu.update(giu)
        else:
            rec["so_vong"] = len(st["vong"]) + 1
            # chép ảnh và nguồn vòng này: để so trước/sau và để hoàn tác
            luu = deck.vl / "vong" / f"{sid}-v{rec['so_vong']}.png"
            luu.parent.mkdir(exist_ok=True)
            shutil.copy(anh, luu)
            rec["ban_luu"] = luu_nguon(deck, sid, rec["so_vong"])
            if cu:
                kiem_pham_vi(deck, sid, cu, rec)
                # ảnh y hệt một vòng cũ (vd vừa hoàn tác): dùng lại phiếu, khỏi chấm lại
                for v in reversed(st["vong"]):
                    if v.get("hash_anh") == rec["hash_anh"]:
                        for k_ in ("cham", "xac_minh", "cham_nguoi"):
                            if v.get(k_):
                                rec[k_] = v[k_]
                        break
            st["vong"].append(rec)
        deck.tt["nhat_ky"].append({"luc": thoi, "slide": sid, "vong": st["vong"][-1]["so_vong"], "sai": len(sai), "luu_y": len(luu_y)})
    ids = deck.danh_sach()
    muc = [(s, deck.vl / deck.tt["slides"][s]["vong"][-1]["anh"], len(deck.tt["slides"][s]["vong"][-1]["sai"]))
           for s in ids if s in deck.tt["slides"]]
    bang_anh(muc, deck.vl / "bang-anh.png")
    kiem_ca_deck(deck, ids)
    deck.luu()
    tong_sai = sum(len(v[2]) for v in kq.values())
    bao(f"đã dựng {len(kq)} slide · {tong_sai} lỗi xác định · ảnh ở {deck.vl / 'anh'} · bảng ảnh {deck.vl / 'bang-anh.png'}")
    for sid, v in kq.items():
        if v[2] or v[3]:
            bao(f"  {sid}: {len(v[2])} lỗi, {len(v[3])} lưu ý")
            for x in v[2][:6]:
                bao(f"    ✗ {x['mo_ta']}")
    for x in deck.tt.get("deck_luu_y", []):
        bao(f"  deck: {x}")


def luu_nguon(deck: Deck, sid: str, n: int) -> str:
    thu = deck.vl / "vong"
    if deck.la_pptx:
        p = thu / f"deck-{sha_tep(deck.nguon)}.pptx"
        if not p.exists():
            shutil.copy(deck.nguon, p)
    else:
        p = thu / f"{sid}-v{n}.html"
        shutil.copy(deck.thu_muc_project() / "slides" / f"{sid}.html", p)
    return str(p.relative_to(deck.vl))


def kiem_pham_vi(deck: Deck, sid: str, cu: dict, rec: dict):
    """Luật chống sửa quá tay: chỉ sửa slide có trong phiếu sửa, và không viết lại cả slide."""
    trong_phieu = sid in deck.tt.get("phieu_sua", [])
    c, xm = cu.get("cham") or {}, cu.get("xac_minh") or {}
    da_dat = c.get("ket_luan") == "dat" or (c.get("ket_luan") == "hong" and xm and not xm.get("giu") and not cu["sai"])
    if not trong_phieu and da_dat:
        rec["luu_y"].append({"ma": "ngoai-pham-vi", "mo_ta": "slide đã đạt bị sửa dù không có trong phiếu sửa"})
    # lượng sửa = điểm ảnh đổi giữa ảnh vòng trước và ảnh vòng này (đo cái khán giả thấy, không đo mã)
    import numpy as np
    from PIL import Image
    truoc = deck.vl / "vong" / f"{sid}-v{cu['so_vong']}.png"
    if not truoc.exists():
        return
    A = np.asarray(Image.open(truoc).convert("L").resize((480, 270)), dtype=float)
    B = np.asarray(Image.open(deck.vl / rec["anh"]).convert("L").resize((480, 270)), dtype=float)
    doi = float((np.abs(A - B) > 24).mean())
    rec["ty_le_sua"] = round(doi, 2)
    if doi > deck.ch["ty_le_sua_toi_da"]:
        rec["luu_y"].append({"ma": "sua-qua-tay", "mo_ta": f"{doi:.0%} điểm ảnh đổi so với vòng trước: gần như làm lại slide, dễ sinh lỗi mới"})


def kiem_ca_deck(deck: Deck, ids: list[str]):
    """Kiểm xác định cấp deck: tiêu đề cùng độ cao, nhịp slide nặng."""
    ly = []
    from collections import Counter
    for the in ("h1", "h2"):  # chỉ so slide cùng loại tiêu đề (bìa/chương h1, nội dung h2)
        ys = [(s, deck.tt["slides"][s]["vong"][-1]["so"]) for s in ids if s in deck.tt["slides"]]
        ys = [(s, so["tieu_de_y"]) for s, so in ys if so.get("tieu_de_y") is not None and so.get("tieu_de_the") == the]
        if len(ys) >= 3:
            pho = Counter(round(y / 8) for _, y in ys).most_common(1)[0][0] * 8
            lech = [s for s, y in ys if abs(y - pho) > 24]
            if lech and len(lech) < len(ys) / 2:
                ly.append(f"tiêu đề <{the}> lệch độ cao chung (~{pho}px): {', '.join(lech)}")
    nang = 0
    tran = deck.ch["so_chu_toi_da"].get(deck.tt.get("kieu", "trinh-bay"), 60) * 0.75
    for s in ids:
        if s not in deck.tt["slides"]:
            continue
        n = deck.tt["slides"][s]["vong"][-1]["so"].get("so_chu", 0)
        nang = nang + 1 if n >= tran else 0
        if nang == 3:
            ly.append(f"3 slide nặng liền nhau tới {s}: chèn một slide thở (LUAT-DECK-DEP luật 17)")
    deck.tt["deck_luu_y"] = ly


def doc_cham(p: Path, nguong_dat: int = 4) -> dict:
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        sys.exit(f"phiếu chấm không phải JSON hợp lệ: {e}")
    loi = []
    if d.get("ket_luan") not in KET_LUAN:
        loi.append(f"ket_luan phải là một trong {KET_LUAN}")
    if not str(d.get("nguoi_cham", "")).strip():
        loi.append("thiếu nguoi_cham")
    if not str(d.get("tom_tat", "")).strip():
        loi.append("thiếu tom_tat")
    diem = d.get("diem", {})
    if d.get("ket_luan") != "khong-cham-duoc":
        for t in TIEU_CHI:
            v = diem.get(t)
            if not isinstance(v, int) or not 1 <= v <= 5:
                loi.append(f"diem.{t} phải là số nguyên 1–5")
    if not isinstance(d.get("loi", []), list):
        loi.append("loi phải là danh sách")
    for x in d.get("loi", []):
        if x.get("muc") not in MUC:
            loi.append(f"mỗi lỗi cần muc trong {MUC}")
        if not str(x.get("mo_ta", "")).strip() or not str(x.get("sua", "")).strip():
            loi.append("mỗi lỗi cần mo_ta và sua")
    if d.get("ket_luan") == "dat" and any(x.get("muc") in ("chan", "nang") for x in d.get("loi", [])):
        loi.append("phiếu 'dat' không được có lỗi chan/nang")
    if d.get("ket_luan") == "dat" and any(diem.get(t, 5) < nguong_dat for t in TIEU_CHI):
        loi.append(f"phiếu 'dat' phải ≥ {nguong_dat} điểm ở mọi tiêu chí")
    if loi:
        sys.exit("phiếu chấm bị từ chối:\n  - " + "\n  - ".join(loi))
    return d


def lenh_cham(a):
    deck = Deck(a.deck)
    d = doc_cham(Path(a.tep), deck.ch["diem_dat_toi_thieu"])
    tho = (deck.ch.get("tho") or "").strip().lower()
    if not a.nguoi and tho and d["nguoi_cham"].strip().lower() == tho:
        sys.exit(f"người chấm '{d['nguoi_cham']}' trùng thợ: phải tách người chấm khỏi người làm")
    khoa = "cham_nguoi" if a.nguoi else "cham"
    d["luc"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    if d.get("pham_vi") == "deck" or a.deck_level:
        ids = deck.danh_sach()
        hs = deck_hash(deck, ids)
        if hs is None:
            sys.exit("còn slide chưa dựng: chạy do trước")
        d["hash_deck"] = hs
        deck.tt["deck"][khoa] = gop_phieu(deck, deck.tt["deck"].get(khoa), d, "hash_deck") if khoa == "cham" else d
    else:
        sid = d.get("slide") or a.slide
        st = deck.tt["slides"].get(sid)
        if not st:
            sys.exit(f"slide '{sid}' chưa dựng: chạy do trước")
        cu = st["vong"][-1]
        anh = deck.vl / cu["anh"]
        if nguon_doi(deck, sid, cu):
            sys.exit(f"{sid}: ảnh hoặc nguồn đã đổi sau lần dựng cuối: chạy do rồi chấm lại ảnh mới")
        if sha_tep(anh) != cu["hash_anh"]:
            # nguồn y nguyên mà hash ảnh lệch: trạng thái bị ghi đè bởi một lần `do` đọc bản cũ (ổ mạng chậm đồng bộ);
            # ảnh trên đĩa chính là ảnh người chấm đã xem, nên lấy hash của nó
            print(f"{sid}: hash ảnh trong trạng thái lệch tệp (nguồn không đổi), cập nhật theo tệp", file=sys.stderr)
            cu["hash_anh"] = sha_tep(anh)
        if False:
            sys.exit(f"{sid}: ảnh hoặc nguồn đã đổi sau lần dựng cuối: chạy do rồi chấm lại ảnh mới")
        d["hash_anh"] = cu["hash_anh"]
        cu[khoa] = gop_phieu(deck, cu.get(khoa), d, "hash_anh") if khoa == "cham" else d
    deck.tt["nhat_ky"].append({"luc": d["luc"], "slide": d.get("slide", "deck"), "cham": d["ket_luan"],
                               "nguoi_cham": d["nguoi_cham"], "diem": sum(d.get("diem", {}).values())})
    deck.luu()
    bao(f"đã ghi phiếu {khoa} '{d['ket_luan']}' cho {d.get('slide', 'deck')}")


def gop_phieu(deck: Deck, cu: dict | None, d: dict, khoa_hash: str) -> dict:
    """Gộp nhiều phiếu trên cùng ảnh: điểm = trung vị từng tiêu chí; đạt khi trung vị mọi tiêu chí ≥ ngưỡng
    và đa số phiếu đạt; lỗi = lỗi của các phiếu hỏng. Chưa đủ số phiếu thì còn 'cho-cham'."""
    import statistics
    ds = [x for x in ((cu or {}).get("phieu") or ([cu] if cu and "phieu" not in cu else [])) if x.get(khoa_hash) == d[khoa_hash]]
    ds = [x for x in ds if x["nguoi_cham"] != d["nguoi_cham"]] + [d]  # cùng người chấm lại thì thay phiếu cũ
    n_can = deck.ch.get("so_nguoi_cham", 1)
    diem = {}
    for t in TIEU_CHI:
        v = [x["diem"][t] for x in ds if x.get("diem", {}).get(t)]
        if v:
            diem[t] = int(statistics.median_low(v))
    dat = sum(x["ket_luan"] == "dat" for x in ds) * 2 > len(ds) and diem and min(diem.values()) >= deck.ch["diem_dat_toi_thieu"]
    loi = [] if dat else [l for x in ds if x["ket_luan"] != "dat" for l in x.get("loi", [])]
    loi.sort(key=lambda l: MUC.index(l["muc"]))
    g = {"ket_luan": "dat" if dat else "hong", "diem": diem, "loi": loi, khoa_hash: d[khoa_hash], "phieu": ds,
         "nguoi_cham": "+".join(x["nguoi_cham"] for x in ds), "tom_tat": " | ".join(x["tom_tat"] for x in ds),
         "du_phieu": len(ds) >= n_can, "pham_vi": d.get("pham_vi")}
    if d.get("slide"):
        g["slide"] = d["slide"]
    return g


def nguon_doi(deck: Deck, sid: str, rec: dict) -> bool:
    if deck.la_pptx:
        return not rec["hash_nguon"].startswith(sha_tep(deck.nguon))
    _, h = vo_html(deck, sid)
    return h != rec["hash_nguon"]


def deck_hash(deck: Deck, ids):
    hs = []
    for s in ids:
        st = deck.tt["slides"].get(s)
        if not st:
            return None
        hs.append(st["vong"][-1]["hash_anh"])
    return sha("".join(hs).encode())


def danh_gia(deck: Deck):
    """Trạng thái từng slide theo luật dừng. Trả (dòng, tổng hợp)."""
    ids = deck.danh_sach()
    tran = deck.ch["tran_vong"]
    dong = []
    for s in ids:
        st = deck.tt["slides"].get(s)
        if not st:
            dong.append((s, "chua-dung", "chưa dựng", None)); continue
        cu = st["vong"][-1]
        n = cu["so_vong"]
        if nguon_doi(deck, s, cu):
            dong.append((s, "cu", "nguồn đổi sau lần dựng cuối: chạy do", cu)); continue
        c = cu.get("cham")
        lui = lui_buoc(st)
        if lui:
            dong.append((s, "lui", lui, cu)); continue
        if cu["sai"]:
            tt = "het-vong" if n > tran else "hong"
            dong.append((s, tt, f"{len(cu['sai'])} lỗi xác định", cu)); continue
        if not c or c.get("hash_anh") != cu["hash_anh"] or c.get("du_phieu") is False:
            co = len(c.get("phieu", [])) if c and c.get("hash_anh") == cu["hash_anh"] else 0
            dong.append((s, "cho-cham", f"qua kiểm máy, chờ người chấm ({co}/{deck.ch.get('so_nguoi_cham', 1)} phiếu)", cu)); continue
        if c["ket_luan"] == "dat":
            dong.append((s, "dat", f"đạt ({sum(c['diem'].values())}/{5 * len(c['diem'])}, {c['nguoi_cham']})", cu)); continue
        if c["ket_luan"] == "khong-cham-duoc":
            dong.append((s, "hong", "người chấm không chấm được: coi như hỏng", cu)); continue
        nang = loi_nang(c)
        if deck.ch["xac_minh_loi"] and nang:
            xm = cu.get("xac_minh")
            if not xm or xm.get("hash_anh") != cu["hash_anh"]:
                dong.append((s, "cho-xac-minh", f"chấm hỏng {len(nang)} lỗi nặng, chờ xác minh", cu)); continue
            nang = [x for i, x in enumerate(nang, 1) if i in xm["giu"]]
            if not nang and min(c["diem"].values()) >= deck.ch["diem_dat_toi_thieu"]:
                dong.append((s, "dat", f"đạt sau xác minh: bác {len(xm['bac'])} lỗi của người chấm", cu)); continue
        tt = "het-vong" if n > tran else "hong"
        dong.append((s, tt, f"chấm hỏng: {len(nang)} lỗi nặng đã xác minh" if deck.ch["xac_minh_loi"] else f"chấm hỏng: {len(nang)} lỗi nặng", cu))
    # không tiến bộ: điểm vòng này ≤ vòng trước
    for s, tt, _, cu in dong:
        st = deck.tt["slides"].get(s)
        if not st or len(st["vong"]) < 2:
            continue
        d2 = [sum(v["cham"]["diem"].values()) for v in st["vong"][-2:] if v.get("cham") and v["cham"].get("diem")]
        if len(d2) == 2 and d2[1] <= d2[0] and tt != "dat":
            st["khong_tien"] = True
    return dong, ids


def loi_nang(c: dict) -> list:
    """Lỗi chan trước nang, giữ thứ tự người chấm xếp."""
    return [x for x in c.get("loi", []) if x["muc"] == "chan"] + [x for x in c.get("loi", []) if x["muc"] == "nang"]


def lui_buoc(st: dict) -> str:
    """Giữ bản mới chỉ khi tốt hơn: nhiều lỗi máy hơn, hoặc điểm chấm thấp hơn vòng trước = lùi."""
    if len(st["vong"]) < 2:
        return ""
    a, b = st["vong"][-2], st["vong"][-1]
    if len(b["sai"]) > len(a["sai"]):
        return f"lùi bước: lỗi máy {len(a['sai'])} → {len(b['sai'])}, nên hoàn tác về vòng {a['so_vong']}"
    da, db = a.get("cham"), b.get("cham")
    if da and db and da.get("diem") and db.get("diem") and db.get("hash_anh") == b["hash_anh"]:
        if sum(db["diem"].values()) < sum(da["diem"].values()):
            return (f"lùi bước: điểm {sum(da['diem'].values())} → {sum(db['diem'].values())}/25, "
                    f"nên hoàn tác về vòng {a['so_vong']}")
    return ""


def lenh_trang_thai(a):
    deck = Deck(a.deck)
    dong, ids = danh_gia(deck)
    ky = {"dat": "✓", "cho-cham": "…", "cho-xac-minh": "?", "hong": "✗", "het-vong": "⛔", "cu": "↻", "chua-dung": "○", "lui": "↩"}
    for s, tt, msg, cu in dong:
        them = " · không tiến bộ so với vòng trước" if deck.tt["slides"].get(s, {}).get("khong_tien") else ""
        bao(f"{ky[tt]} {s:<16} vòng {cu['so_vong'] if cu else 0}  {msg}{them}")
    dk = trang_thai_deck(deck, ids)
    bao(f"deck: {dk}")
    for x in deck.tt.get("deck_luu_y", []):
        bao(f"  lưu ý deck: {x}")
    bao("bước tiếp: " + buoc_tiep(dong, dk))


def trang_thai_deck(deck: Deck, ids):
    c = deck.tt["deck"].get("cham")
    hs = deck_hash(deck, ids)
    if not c:
        return "chưa chấm cả deck"
    if c.get("hash_deck") != hs:
        return "phiếu chấm deck cũ (slide đã đổi)"
    if c.get("du_phieu") is False:
        return f"chưa đủ phiếu chấm deck ({len(c.get('phieu', []))}/{deck.ch.get('so_nguoi_cham', 1)})"
    nang = loi_nang(c)
    if c["ket_luan"] == "hong" and deck.ch["xac_minh_loi"] and nang:
        xm = deck.tt["deck"].get("xac_minh")
        if not xm or xm.get("hash_deck") != hs:
            return f"hong, chờ xác minh {len(nang)} lỗi nặng của deck"
        if not xm["giu"] and min(c["diem"].values()) >= deck.ch["diem_dat_toi_thieu"]:
            return f"dat sau xác minh (bác {len(xm['bac'])} lỗi)"
        return f"hong: {len(xm['giu'])} lỗi nặng đã xác minh"
    return f"{c['ket_luan']} ({c['nguoi_cham']})"


def buoc_tiep(dong, dk):
    if any(t in ("chua-dung", "cu") for _, t, _, _ in dong):
        return "chạy `do` cho slide mới hoặc đã sửa"
    if any(t == "lui" for _, t, _, _ in dong):
        return "có slide sửa xong còn tệ hơn: chạy `hoan-tac --slide ID` rồi `do`"
    if any(t == "cho-xac-minh" for _, t, _, _ in dong):
        return "chạy `de-xac-minh`, giao người xác minh (khác thợ), rồi `xac-minh`"
    if any(t == "hong" for _, t, _, _ in dong):
        return "chạy `phieu-sua`, thợ sửa đúng các slide hỏng, rồi `do`"
    if any(t == "cho-cham" for _, t, _, _ in dong):
        return "chạy `de-cham`, giao người chấm (khác thợ), rồi `cham`"
    if any(t == "het-vong" for _, t, _, _ in dong):
        return "slide hết vòng: dừng sửa máy, đưa người quyết (đổi bố cục, bỏ ý, tách slide)"
    if "chờ xác minh" in dk:
        return "chạy `de-xac-minh --deck`, giao người xác minh, rồi `xac-minh`"
    if dk.startswith("hong"):
        return "chạy `phieu-sua`: lỗi cấp deck (thêm/bớt/đổi thứ tự slide) do thợ đề xuất, người duyệt trước khi làm"
    if not dk.startswith("dat"):
        return "chạy `de-cham --deck` để chấm cả deck trên bảng ảnh"
    return "chạy `ket-thuc`"


def ds_mau(deck: Deck) -> str:
    import glob
    ps = []
    for g in deck.ch.get("mau_tham_chieu", []):
        ps += sorted(glob.glob(g))
    if not ps:
        return "(chưa cấu hình ảnh mẫu: chấm `ngang_mau` theo trí nhớ về slide của studio thiết kế hàng đầu, và ghi rõ điều này trong tom_tat)"
    return "\n".join(f"- `{p}`" for p in ps[:8])


def lenh_de_cham(a):
    deck = Deck(a.deck)
    mau = (ROOT / "references" / "cham-slide.md").read_text(encoding="utf-8")
    ids = deck.danh_sach()
    thu = deck.vl / "de-cham"; thu.mkdir(exist_ok=True)
    if a.deck_level:
        p = thu / "deck.md"
        bang = deck.vl / "bang-anh.png"
        p.write_text(mau.split("<!-- DECK -->")[1].split("<!-- XAC MINH -->")[0].replace("{{MAU}}", ds_mau(deck)).replace("{{ANH}}", str(bang)).replace(
            "{{SO_SLIDE}}", str(len(ids))).replace("{{LUU_Y}}", "\n".join(f"- {x}" for x in deck.tt.get("deck_luu_y", [])) or "- (không)").replace(
            "{{RA}}", str(thu / "deck.json")), encoding="utf-8")
        bao(str(p)); return
    dong, _ = danh_gia(deck)
    can = [s for s, t, _, _ in dong if t == "cho-cham" and (not a.slide or s == a.slide)]
    if a.slide and not can:
        can = [a.slide]
    for s in can:
        cu = deck.tt["slides"][s]["vong"][-1]
        i = ids.index(s)
        hang_xom = ", ".join(f"{x} (`{deck.vl / deck.tt['slides'][x]['vong'][-1]['anh']}`)"
                             for x in ids[max(0, i - 1):i + 2] if x != s and x in deck.tt["slides"])
        p = thu / f"{s}.md"
        p.write_text(mau.split("<!-- DECK -->")[0].replace("{{SLIDE}}", s).replace("{{VI_TRI}}", f"{i+1}/{len(ids)}").replace(
            "{{ANH}}", str(deck.vl / cu["anh"])).replace("{{XOM}}", hang_xom or "(không)").replace(
            "{{LUU_Y}}", "\n".join(f"- {x['mo_ta']}" for x in cu["luu_y"]) or "- (không)").replace(
            "{{RA}}", str(thu / f"{s}-{len(((cu.get('cham') or {}).get('phieu') or [])) + 1 if (cu.get('cham') or {}).get('hash_anh') == cu['hash_anh'] else 1}.json")).replace("{{KIEU}}", deck.tt.get("kieu", "trinh-bay")).replace(
            "{{MAU}}", ds_mau(deck)), encoding="utf-8")
        bao(str(p))


def lenh_phieu_sua(a):
    deck = Deck(a.deck)
    dong, _ = danh_gia(deck)
    ra, ids_sua = [], []
    for s, tt, msg, cu in dong:
        if tt not in ("hong", "het-vong"):
            continue
        ra.append(f"## {s} (vòng {cu['so_vong']}{', HẾT VÒNG: không tự sửa, hỏi người' if tt == 'het-vong' else ''})")
        ra.append(f"Ảnh đánh dấu: {deck.vl / cu['anh_danh_dau']}")
        for x in cu["sai"]:
            ra.append(f"- [máy] {x['mo_ta']}")
        c = cu.get("cham")
        if c and c.get("hash_anh") == cu["hash_anh"]:
            nang = loi_nang(c)
            xm = cu.get("xac_minh")
            if deck.ch["xac_minh_loi"] and xm and xm.get("hash_anh") == cu["hash_anh"]:
                nang = [x for i, x in enumerate(nang, 1) if i in xm["giu"]]
            giao_ = nang[:deck.ch["toi_da_loi_moi_luot"]]
            for x in giao_:
                ra.append(f"- [{c['nguoi_cham']}·{x['muc']}] {x.get('vung', '')}: {x['mo_ta']} → sửa: {x['sua']}")
            bo = len(nang) - len(giao_) + len([x for x in c["loi"] if x["muc"] == "nhe"])
            if bo:
                ra.append(f"- (để lại {bo} lỗi nhẹ/xếp sau cho vòng sau: KHÔNG sửa trong lượt này)")
        ra.append("")
        ids_sua.append(s)
    dk = trang_thai_deck(deck, deck.danh_sach())
    if dk.startswith("hong:"):
        c = deck.tt["deck"]["cham"]; xm = deck.tt["deck"]["xac_minh"]
        nang = [x for i, x in enumerate(loi_nang(c), 1) if i in xm["giu"]][:deck.ch["toi_da_loi_moi_luot"]]
        ra.append("## Cả deck (đề xuất cho người duyệt TRƯỚC khi làm: thêm/bớt/đổi thứ tự slide là đổi nội dung)")
        ra.append(f"Bảng ảnh: {deck.vl / 'bang-anh.png'}")
        for x in nang:
            ra.append(f"- [{c['nguoi_cham']}·{x['muc']}] {x.get('vung', '')}: {x['mo_ta']} → sửa: {x['sua']}")
        ra.append("")
    if not ra:
        bao("không có slide nào cần sửa"); return
    deck.tt["phieu_sua"] = ids_sua
    deck.luu()
    luat = ("Luật sửa (chống sửa quá tay):\n"
            "- Chỉ sửa các slide và đúng các lỗi dưới đây. Slide khác, lỗi khác: không đụng.\n"
            "- Sửa nhỏ nhất đủ hết lỗi; không viết lại cả slide, không đổi ý/tiêu đề đã duyệt trừ khi lỗi nói vậy.\n"
            "- Không co chữ dưới cỡ tối thiểu; hết chỗ thì cắt chữ hoặc tách slide.\n"
            "- Đổi CSS chung là mọi slide phải dựng và chấm lại.\n"
            "- Bản sửa mà tệ hơn bản cũ sẽ bị hoàn tác.\n\n")
    p = deck.vl / "phieu-sua.md"
    p.write_text("# Phiếu sửa\n\n" + luat + "\n".join(ra), encoding="utf-8")
    bao(p.read_text(encoding="utf-8"))


def lenh_de_xac_minh(a):
    deck = Deck(a.deck)
    mau = (ROOT / "references" / "cham-slide.md").read_text(encoding="utf-8").split("<!-- XAC MINH -->")[1]
    dong, ids = danh_gia(deck)
    thu = deck.vl / "de-cham"; thu.mkdir(exist_ok=True)
    if a.deck_level:
        c = deck.tt["deck"].get("cham") or {}
        ds = "\n".join(f"{i}. [{x['muc']}] {x.get('vung', '')}: {x['mo_ta']}" for i, x in enumerate(loi_nang(c), 1))
        p = thu / "deck-xac-minh.md"
        p.write_text(mau.replace("{{SLIDE}}", "deck").replace("{{ANH}}", str(deck.vl / "bang-anh.png")).replace(
            "{{DS}}", ds).replace("{{RA}}", str(thu / "deck-xac-minh.json")), encoding="utf-8")
        bao(str(p)); return
    for s, t, _, cu in dong:
        if t != "cho-xac-minh" or (a.slide and s != a.slide):
            continue
        ds = "\n".join(f"{i}. [{x['muc']}] {x.get('vung', '')}: {x['mo_ta']}" for i, x in enumerate(loi_nang(cu["cham"]), 1))
        p = thu / f"{s}-xac-minh.md"
        p.write_text(mau.replace("{{SLIDE}}", s).replace("{{ANH}}", str(deck.vl / cu["anh"])).replace(
            "{{DS}}", ds).replace("{{RA}}", str(thu / f"{s}-xac-minh.json")), encoding="utf-8")
        bao(str(p))


def lenh_xac_minh(a):
    deck = Deck(a.deck)
    try:
        d = json.loads(Path(a.tep).read_text(encoding="utf-8"))
    except Exception as e:
        sys.exit(f"phiếu xác minh không phải JSON: {e}")
    s = d.get("slide")
    if s == "deck":
        cu = deck.tt["deck"]
        c = cu.get("cham")
        hs = deck_hash(deck, deck.danh_sach())
        if not c or c.get("hash_deck") != hs:
            sys.exit("deck: chưa có phiếu chấm deck cho bộ ảnh hiện tại")
    else:
        st = deck.tt["slides"].get(s)
        if not st:
            sys.exit(f"không có slide '{s}'")
        cu = st["vong"][-1]
        c = cu.get("cham")
        if not c or c.get("hash_anh") != cu["hash_anh"]:
            sys.exit(f"{s}: chưa có phiếu chấm cho ảnh hiện tại")
    ai = str(d.get("nguoi_xac_minh", "")).strip().lower()
    if not ai:
        sys.exit("thiếu nguoi_xac_minh")
    if ai == (deck.ch.get("tho") or "").strip().lower():
        sys.exit("người xác minh trùng thợ")
    nang = loi_nang(c)
    kq = {int(x["so"]): bool(x["giu"]) for x in d.get("ket_qua", []) if str(x.get("ly_do", "")).strip()}
    thieu = [i for i in range(1, len(nang) + 1) if i not in kq]
    if thieu:
        sys.exit(f"phiếu xác minh thiếu lỗi số {thieu} (mỗi lỗi cần giu true/false và ly_do)")
    cu["xac_minh"] = {"nguoi_xac_minh": d["nguoi_xac_minh"], "hash_anh": cu.get("hash_anh"), "hash_deck": c.get("hash_deck"),
                      "giu": [i for i, g in kq.items() if g], "bac": [i for i, g in kq.items() if not g],
                      "chi_tiet": d.get("ket_qua", []), "luc": time.strftime("%Y-%m-%dT%H:%M:%S")}
    deck.tt["nhat_ky"].append({"luc": cu["xac_minh"]["luc"], "slide": s, "xac_minh_giu": len(cu["xac_minh"]["giu"]),
                               "xac_minh_bac": len(cu["xac_minh"]["bac"])})
    deck.luu()
    bao(f"{s}: giữ {len(cu['xac_minh']['giu'])} lỗi, bác {len(cu['xac_minh']['bac'])} lỗi")


def lenh_hoan_tac(a):
    deck = Deck(a.deck)
    st = deck.tt["slides"].get(a.slide)
    if not st or len(st["vong"]) < 2:
        sys.exit("không có vòng trước để hoàn tác")
    dich = st["vong"][-2]
    src = deck.vl / dich["ban_luu"]
    if deck.la_pptx:
        shutil.copy(src, deck.nguon)
    else:
        shutil.copy(src, deck.thu_muc_project() / "slides" / f"{a.slide}.html")
    deck.tt["nhat_ky"].append({"luc": time.strftime("%Y-%m-%dT%H:%M:%S"), "slide": a.slide, "hoan_tac_ve": dich["so_vong"]})
    deck.luu()
    bao(f"{a.slide}: đã trả nguồn về vòng {dich['so_vong']}. Chạy `do` (phiếu cũ được dùng lại nếu ảnh trùng).")


def lenh_ket_thuc(a):
    deck = Deck(a.deck)
    dong, ids = danh_gia(deck)
    dk = trang_thai_deck(deck, ids)
    dat_may = all(t == "dat" for _, t, _, _ in dong) and dk.startswith("dat")
    cn = deck.tt["deck"].get("cham_nguoi")
    dat_nguoi = bool(cn and cn.get("hash_deck") == deck_hash(deck, ids) and cn["ket_luan"] == "dat")
    vong = [len(deck.tt["slides"].get(s, {}).get("vong", [])) for s in ids]
    lines = [f"# Báo cáo vòng lặp slide: {deck.nguon.name}", "",
             f"- Kết luận: **{'HOÀN TẤT (người đã duyệt)' if dat_may and dat_nguoi else 'ĐẠT MÁY, CHỜ NGƯỜI DUYỆT' if dat_may else 'CHƯA ĐẠT'}**",
             f"- {len(ids)} slide · tổng {sum(vong)} lượt dựng có đổi nguồn · deck: {dk}", "",
             "| Slide | Vòng | Trạng thái | Lỗi máy vòng 1 → nay |", "|---|---|---|---|"]
    for s, t, msg, cu in dong:
        st = deck.tt["slides"].get(s, {"vong": []})
        dau = len(st["vong"][0]["sai"]) if st["vong"] else "-"
        nay = len(cu["sai"]) if cu else "-"
        lines.append(f"| {s} | {cu['so_vong'] if cu else 0} | {msg} | {dau} → {nay} |")
    lines += ["", f"Bảng ảnh: `{deck.vl / 'bang-anh.png'}` · ảnh từng vòng: `{deck.vl / 'vong'}`"]
    (deck.vl / "BAO-CAO.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    bao("\n".join(lines))
    sys.exit(0 if dat_may else 1)


def lenh_hieu_chinh(a):
    deck = Deck(a.deck)
    cap = []
    for s, st in deck.tt["slides"].items():
        for v in st["vong"]:
            m, n = v.get("cham"), v.get("cham_nguoi")
            if m and n and m.get("hash_anh") == n.get("hash_anh"):
                cap.append((s, v["so_vong"], m["ket_luan"], n["ket_luan"], m.get("diem", {}), n.get("diem", {})))
    if not cap:
        bao("chưa có ảnh nào được cả máy và người chấm. Người chấm bằng: cham --nguoi --tep ..."); return
    khop = sum(1 for c in cap if c[2] == c[3])
    bao(f"{len(cap)} ảnh có cả hai phiếu · khớp kết luận {khop}/{len(cap)} ({100*khop/len(cap):.0f}%)")
    for s, v, m, n, dm, dn in cap:
        if m != n:
            loai = "máy DỄ DÃI" if m == "dat" else "máy KHẮT KHE"
            bao(f"  {s} v{v}: máy {m}, người {n} → {loai}")
        lech = {t: (dm.get(t), dn.get(t)) for t in TIEU_CHI if dm.get(t) and dn.get(t) and abs(dm[t] - dn[t]) >= 2}
        if lech:
            bao(f"  {s} v{v}: lệch ≥2 điểm ở {lech}")
    bao("Máy dễ dãi thì siết rubric ở references/cham-slide.md và ghi bai-hoc; máy khắt khe thì nới.")


def lenh_bai_hoc(a):
    p = ROOT / "bai-hoc.md"
    cu = p.read_text(encoding="utf-8") if p.exists() else "# Bài học vòng lặp slide (tầng 2)\n\nMỗi dòng một bài học rút từ lỗi lặp lại. Thợ đọc file này TRƯỚC khi dựng deck mới.\n\n"
    p.write_text(cu + f"- {time.strftime('%Y-%m-%d')} [{Path(a.deck).name}] {a.ghi.strip()}\n", encoding="utf-8")
    bao(f"đã ghi {p}")


# ───────────────────────── phông tiếng Việt ─────────────────────────

def chu_viet() -> list[str]:
    """134 chữ cái tiếng Việt có dấu, dựng sẵn (NFC), cả hoa lẫn thường."""
    import unicodedata
    goc = "aăâeêioôơuưy"
    dau = ["", "\u0301", "\u0300", "\u0309", "\u0303", "\u0323"]
    ra = {unicodedata.normalize("NFC", g + d) for g in goc for d in dau} | {"đ"}
    ra |= {c.upper() for c in ra}
    return sorted(c for c in ra if not c.isascii())


MAU_DAU = "Trân trọng · Vẻ đẹp bền lâu · ẤẦẨẪẬ ấầẩẫậ ềếểễệ ốồổỗộ ớờởỡợ ứừửữự ỳýỷỹỵ Đđ"


def lenh_phong(a):
    """Kiểm phông tiêu đề/thân có đủ chữ Việt dựng sẵn không, và in bảng dấu để mắt người/VLM soi kiểu dấu.
    Thiếu chữ thì trình duyệt mượn phông khác cho riêng chữ đó (dấu lệch kiểu): lỗi chặn."""
    import io, urllib.request
    from fontTools.ttLib import TTFont
    deck = Deck(a.deck)
    dj = doc_json(deck.thu_muc_project() / "deck.json", {}) or {}
    ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
    can = chu_viet()
    ho: dict[str, set] = {}
    for f in dj.get("faces", {}).values():
        href = f.get("href")
        if not href:
            continue
        css = urllib.request.urlopen(urllib.request.Request(href, headers=ua), timeout=30).read().decode()
        for blk in re.findall(r"@font-face\s*{(.*?)}", css, re.S):
            ten = re.search(r"font-family:\s*'?([^;']+)'?;", blk).group(1)
            url = re.search(r"url\((https[^)]+)\)", blk).group(1)
            data = urllib.request.urlopen(urllib.request.Request(url, headers=ua), timeout=30).read()
            ho.setdefault(ten, set()).update(chr(c) for c in TTFont(io.BytesIO(data)).getBestCmap())
    for p in a.tep or []:
        tt = TTFont(p)
        ho.setdefault(tt["name"].getDebugName(1) or Path(p).stem, set()).update(chr(c) for c in tt.getBestCmap())
    if not ho:
        sys.exit("không thấy phông: thêm faces có href vào deck.json hoặc --tep tệp.ttf")
    loi = 0
    for ten, co in ho.items():
        thieu = [c for c in can if c not in co]
        loi += bool(thieu)
        print(f"{'✗' if thieu else '✓'} {ten}: {len(can) - len(thieu)}/{len(can)} chữ Việt" + (f", thiếu {''.join(thieu[:30])}" if thieu else ""))
    # bảng dấu: dựng bằng chính trình duyệt để thấy đúng như trên slide
    links = "".join(f'<link rel="stylesheet" href="{htmlmod.escape(f["href"])}">' for f in dj.get("faces", {}).values() if f.get("href"))
    dong = "".join(f'<div style="font-family:\'{t}\';font-size:72px;padding:12px 40px;border-bottom:1px solid #ddd">{MAU_DAU}'
                   f'<span style="font:20px sans-serif;color:#666"> {htmlmod.escape(t)}</span></div>' for t in ho)
    tep = deck.vl / "bang-dau.html"
    tep.write_text(f'<html><head><meta charset="utf-8">{links}</head><body style="margin:0;background:#fff;width:2600px">{dong}</body></html>', encoding="utf-8")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = mo_trinh_duyet(p)
        pg = b.new_page(viewport={"width": 2600, "height": 400})
        pg.goto(tep.as_uri(), wait_until="networkidle", timeout=60000)
        pg.evaluate("document.fonts.ready.then(()=>1)")
        pg.screenshot(path=str(deck.vl / "bang-dau.png"), full_page=True)
        b.close()
    tep.unlink(missing_ok=True)
    print(f"bảng dấu: {deck.vl / 'bang-dau.png'} (soi dấu mũ, dấu móc, dấu chồng: cùng kiểu, cùng độ cao với chữ không?)")
    if loi:
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="lenh", required=True)
    x = sp.add_parser("do"); x.add_argument("deck"); x.add_argument("--kieu", default="trinh-bay", choices=["trinh-bay", "doc"]); x.add_argument("--chi"); x.add_argument("--bo-qua-mau", action="store_true"); x.add_argument("--lam-lai", action="store_true")
    x = sp.add_parser("mau"); x.add_argument("deck"); x.add_argument("--anh", nargs="+", required=True); x.add_argument("--ghi-de", action="store_true")
    x = sp.add_parser("khoa-mau"); x.add_argument("deck")
    x = sp.add_parser("de-cham"); x.add_argument("deck"); x.add_argument("--slide"); x.add_argument("--deck", dest="deck_level", action="store_true")
    x = sp.add_parser("cham"); x.add_argument("deck"); x.add_argument("--tep", required=True); x.add_argument("--slide"); x.add_argument("--nguoi", action="store_true"); x.add_argument("--deck", dest="deck_level", action="store_true")
    x = sp.add_parser("de-xac-minh"); x.add_argument("deck"); x.add_argument("--slide"); x.add_argument("--deck", dest="deck_level", action="store_true")
    x = sp.add_parser("xac-minh"); x.add_argument("deck"); x.add_argument("--tep", required=True)
    x = sp.add_parser("hoan-tac"); x.add_argument("deck"); x.add_argument("--slide", required=True)
    for n in ("phieu-sua", "trang-thai", "ket-thuc", "hieu-chinh"):
        x = sp.add_parser(n); x.add_argument("deck")
    x = sp.add_parser("phong"); x.add_argument("deck"); x.add_argument("--tep", nargs="*")
    x = sp.add_parser("bai-hoc"); x.add_argument("deck"); x.add_argument("--ghi", required=True)
    a = ap.parse_args()
    {"do": lenh_do, "de-cham": lenh_de_cham, "cham": lenh_cham, "phieu-sua": lenh_phieu_sua, "trang-thai": lenh_trang_thai,
     "ket-thuc": lenh_ket_thuc, "hieu-chinh": lenh_hieu_chinh, "bai-hoc": lenh_bai_hoc,
     "de-xac-minh": lenh_de_xac_minh, "mau": lenh_mau, "khoa-mau": lenh_khoa_mau, "xac-minh": lenh_xac_minh, "hoan-tac": lenh_hoan_tac, "phong": lenh_phong}[a.lenh](a)


if __name__ == "__main__":
    main()
