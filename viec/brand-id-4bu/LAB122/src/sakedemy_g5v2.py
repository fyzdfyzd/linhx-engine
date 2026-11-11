# G5 vòng 2 Sakédemy: 3 option phát triển từ A Gân lá (signature, Linh duyệt 11/11 06:59), 3 nền + 2 ấn phẩm.
import math, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from playwright.sync_api import sync_playwright
from sakedemy_g45 import C, CSS, DEFS, vein, leaf_tile, LOGO, ROOT

def svg(w, h, body, bg):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%" preserveAspectRatio="xMidYMid slice">{DEFS}<rect width="{w}" height="{h}" fill="{bg}"/>{body}</svg>'

def opt(k, w, h, nen, free=None):
    ink = C["reu"] if nen == "kem" else "#FFFFFF"
    main = "#FFFFFF" if nen == "mau" else C["la"]
    sub = C["reu"] if nen == "mau" else C["choi"]
    bg = {"kem": C["kem"], "mau": "url(#g)", "toi": C["reu"]}[nen]
    def ok(x, y, r):
        if not free: return True
        x0, y0, x1, y1 = free
        return not (x + r > x0 and x - r < x1 and y + r > y0 and y - r < y1)
    out = []
    if k == "A1":  # Lưới gân: lưới gân nhỏ nhạt, một gân lớn màu ở vùng 1/3
        for row in range(5):
            for col in range(9):
                x = col * w / 7.5 - 20 + (w / 15 if row % 2 else 0); y = h * 0.25 + row * h * 0.22
                if ok(x, y, h * 0.2): out.append(vein(x, y, h * 0.24, 45, h / 220, ink, 0.15))
        out.append(vein(w * (0.6 if free else 0.38), h * 0.85, h * 0.7, 45, h / 90, main, 1))
    elif k == "A2":  # Gân chính – gân phụ: một gân chính dài xuyên khung (văn hoá sáng tạo), gân phụ màu chồi (AI)
        a = math.radians(38); x0, y0 = (w * 0.42, h * 1.05) if free else (-w * 0.05, h * 1.05)
        L = math.hypot(w, h) * 1.1; dx, dy = math.cos(a), -math.sin(a)
        out.append(f'<line x1="{x0}" y1="{y0}" x2="{x0+dx*L:.0f}" y2="{y0+dy*L:.0f}" stroke="{main}" stroke-width="{h/45:.1f}" stroke-linecap="round"/>')
        for i in range(1, 9):
            px, py = x0 + dx * L * i / 9, y0 + dy * L * i / 9
            for side in (1, -1):
                b = a + side * math.radians(50); bl = h * (0.22 if side > 0 else 0.16)
                out.append(f'<line x1="{px:.0f}" y1="{py:.0f}" x2="{px+math.cos(b)*bl:.0f}" y2="{py-math.sin(b)*bl:.0f}" stroke="{sub}" stroke-width="{h/120:.1f}" stroke-linecap="round" opacity=".9"/>')
    else:  # A3 Gân trong lá: ô lá bo của biểu tượng, mỗi ô có gân; một lá màu
        r = h / 7
        for row in range(4):
            for col in range(int(w / (r * 2.8)) + 2):
                cx = col * r * 2.8 + (r * 1.4 if row % 2 else 0); cy = r * 1.1 + row * r * 2.3
                if not ok(cx, cy, r): continue
                out.append(leaf_tile(cx, cy, r * 0.8, 0, ink, 0.1))
                out.append(vein(cx - r * 0.55, cy + r * 0.55, r * 1.45, 45, r / 18, ink, 0.25))
        hx, hy = (w * 0.74, h * 0.55) if free else (w * 0.5, h * 0.5)
        out.append(leaf_tile(hx, hy, r * 1.4, 0, "#FFFFFF" if nen == "mau" else "url(#g)", 1))
        out.append(vein(hx - r * 1.0, hy + r * 1.0, r * 2.6, 45, r / 10, C["reu"] if nen == "mau" else "#FFFFFF", 1))
    return svg(w, h, "".join(out), bg)

logo = (LOGO / "logo-ngang-mau.svg").as_uri(); logo_t = (LOGO / "logo-ngang-nen-toi.svg").as_uri()

def post(k):
    return (f"<div style='position:relative;width:226px;height:226px;border-radius:12px;overflow:hidden'>{opt(k,1080,1080,'toi',free=(0,0,700,430))}"
            f"<div style='position:absolute;left:16px;top:16px;color:#fff'><img src='{logo_t}' style='height:20px'>"
            f"<div style='font-size:16px;font-weight:800;line-height:1.2;margin-top:12px;width:140px'>Văn hoá sáng tạo</div></div></div>")

def cover(k):
    return (f"<div style='position:relative;width:402px;height:226px;border-radius:12px;overflow:hidden;box-shadow:0 0 0 1px #0001'>{opt(k,1920,1080,'kem',free=(0,0,1000,1080))}"
            f"<div style='position:absolute;left:20px;top:22px'><img src='{logo}' style='height:24px'>"
            f"<div style='font-size:14px;font-weight:800;line-height:1.25;margin-top:56px;width:190px;color:{C['reu']}'>Không gian học tập văn hoá sáng tạo</div></div></div>")

rows = [("A1", "Lưới gân", "Gân nhỏ lặp nhạt, một gân lớn ở vùng 1/3.", False),
        ("A2", "Gân chính – phụ", "Gân chính xuyên khung là văn hoá sáng tạo; gân phụ màu chồi là AI.", True),
        ("A3", "Gân trong lá", "Ô lá của biểu tượng, mỗi ô một gân; một lá màu.", False)]
cells = ""
for k, ten, ly, star in rows:
    tiles = "".join(f"<div style='width:300px;height:226px;border-radius:12px;overflow:hidden;box-shadow:0 0 0 1px #0001'>{opt(k,1600,1200,n)}</div>" for n in ("kem", "mau", "toi"))
    cells += (f"<div style='display:flex;align-items:center;gap:22px;margin-top:24px'><div style='width:230px'>"
              f"<div style='font-size:36px;font-weight:800'>{k}{' ★' if star else ''}</div><div style='font-size:25px;font-weight:700'>{ten}</div>"
              f"<div style='font-size:17px;line-height:1.45;color:{C['chu']};margin-top:6px'>{ly}</div></div>{tiles}{post(k)}{cover(k)}</div>")
html = (f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body><div class='pad' style='inset:56px 100px'>"
        f"<div class='kick'>Pattern · vòng 2 · từ A Gân lá (signature)</div><h1 style='font-size:46px'>Ba option phát triển, trên 3 nền và 2 ấn phẩm</h1>"
        f"<div style='display:flex;gap:22px;margin:16px 0 0 252px;font-size:16px;color:{C['chu']}'><span style='width:300px'>Nền kem</span><span style='width:300px'>Nền gradient lá</span><span style='width:300px'>Nền rêu đậm</span><span style='width:226px'>Bài 1:1</span><span>Bìa slide 16:9</span></div>"
        f"{cells}</div><div class='foot' style='left:100px;right:100px'><span>Sakédemy · Brand ID · G5 vòng 2 · 11/11/2026</span><span>★ A2</span></div></body></html>")

if __name__ == "__main__":
    f = ROOT / "_G5-pattern-vong2.html"; f.write_text(html, encoding="utf-8")
    with sync_playwright() as p:
        b = p.chromium.launch(channel="msedge"); pg = b.new_page(viewport={"width": 1920, "height": 1080})
        pg.goto(f.as_uri()); pg.wait_for_timeout(500)
        out = ROOT / "05-pattern" / "G5-pattern-vong2.png"; pg.screenshot(path=str(out)); print(out); b.close()
