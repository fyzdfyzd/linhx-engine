# G5 vòng 2 TUVA: 3 option phát triển từ B Sóng xoắn (Linh duyệt 11/11 07:01), 3 nền + 2 ấn phẩm. Mọi hình là xoắn/sóng, không vòng đồng tâm.
import math, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from playwright.sync_api import sync_playwright
from tuva_g45 import C, CSS, spiral, wave, LOGO, ROOT

def svg(w, h, body, bg):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%" preserveAspectRatio="xMidYMid slice"><rect width="{w}" height="{h}" fill="{bg}"/>{body}</svg>'

def opt(k, w, h, nen, free=None):
    ink = C["nau"] if nen == "kem" else "#FFFFFF"
    hero = C["nau"] if nen == "mau" else C["cam"]
    bg = {"kem": C["kem"], "mau": C["cam"], "toi": C["nau"]}[nen]
    top = (free[3] / h) if free else 0  # vùng trống phía trên cho logo/chữ
    out = []
    if k == "B1":  # Sóng hàng: các hàng sóng cuộn đều, một làn cam
        n = 7
        for row in range(n):
            y = h * (max(top + 0.08, 0.12) + row * (0.86 - max(top, 0.04)) / n)
            out.append(wave(-40 + (row % 2) * 40, y, w + 80, h * 0.03, ink, h / 200, 0.3))
        out.append(wave(-40, h * (0.62 if not free else 0.8), w + 80, h * 0.06, hero, h / 200, 1))
    elif k == "B2":  # Sóng dữ liệu: sóng đứt thành chấm như tín hiệu số, đỉnh vẫn cuộn xoắn
        n = 4; amp = h * 0.035; Lw = amp * 6  # Linh 11/11: sóng chỉ một bên (nửa dưới), nửa trên để trống
        for row in range(n):
            y = h * (max(top + 0.1, 0.56) + row * (0.94 - max(top + 0.1, 0.56)) / n)
            for i in range(int(w / Lw) + 2):
                x = -20 + i * Lw + (row % 2) * Lw / 2
                for t in range(10):
                    tt = t / 9; px = x + tt * Lw; py = y - amp * math.sin(tt * math.pi) ** 2
                    out.append(f'<circle cx="{px:.0f}" cy="{py:.0f}" r="{h/150:.1f}" fill="{ink}" opacity=".38"/>')
                out.append(spiral(x + Lw * 0.55, y - amp * 1.1, amp * 0.8, 180, 1, ink, h / 260, 0.4, turns=1.2))
        out.append(wave(-40, h * 0.8, w + 80, h * 0.06, hero, h / 200, 1))
    else:  # B3 Sóng lớn: một con sóng lớn cuộn thành tù và ở góc, các làn nhỏ mờ phía sau
        for row in range(5):
            y = h * (max(top + 0.1, 0.12) + row * 0.12)
            out.append(wave(-40, y, w * 0.8, h * 0.025, ink, h / 220, 0.26))
        cx, cy, R = w * 0.82, h * 0.78, h * 0.5
        out.append(f'<path d="M{-20},{h*0.98} C{w*0.3},{h*0.98} {w*0.5},{cy-R*0.2} {cx-R*0.707:.0f},{cy-R*0.707:.0f}" fill="none" stroke="{hero}" stroke-width="{h/110:.1f}" stroke-linecap="round"/>')
        out.append(spiral(cx, cy, R, 45, 6, hero, h / 160, 1, turns=1.5))
    return svg(w, h, "".join(out), bg)

logo = (LOGO / "logo-ngang-mau.svg").as_uri(); logo_am = (LOGO / "logo-ngang-am-ban.svg").as_uri()

def post(k):
    return (f"<div style='position:relative;width:226px;height:226px;border-radius:12px;overflow:hidden'>{opt(k,1080,1080,'toi',free=(0,0,1080,360))}"
            f"<div style='position:absolute;left:16px;top:14px;color:#fff'><img src='{logo_am}' style='height:22px'>"
            f"<div style='font-size:15px;font-weight:800;line-height:1.2;margin-top:10px;width:190px'>AI-enabled fundraising partner</div></div></div>")

def cover(k):
    return (f"<div style='position:relative;width:402px;height:226px;border-radius:12px;overflow:hidden;box-shadow:0 0 0 1px #0001'>{opt(k,1920,1080,'kem',free=(0,0,1920,430))}"
            f"<div style='position:absolute;left:20px;top:18px'><img src='{logo}' style='height:22px'>"
            f"<div style='font-size:14px;font-weight:800;line-height:1.25;margin-top:10px;width:330px;color:{C['nau']}'>Strategic narrative &amp; AI-enabled fundraising partner</div></div></div>")

rows = [("B1", "Sóng hàng", "Hàng sóng cuộn đều; một làn cam dẫn mắt.", False),
        ("B2", "Sóng dữ liệu", "Sóng đứt thành chấm như tín hiệu số, đỉnh vẫn cuộn: cộng đồng × công nghệ.", True),
        ("B3", "Sóng lớn", "Một con sóng lớn cuộn thành tù và ở góc.", False)]
cells = ""
for k, ten, ly, star in rows:
    tiles = "".join(f"<div style='width:300px;height:226px;border-radius:12px;overflow:hidden;box-shadow:0 0 0 1px #0001'>{opt(k,1600,1200,n)}</div>" for n in ("kem", "mau", "toi"))
    cells += (f"<div style='display:flex;align-items:center;gap:22px;margin-top:24px'><div style='width:230px'>"
              f"<div style='font-size:36px;font-weight:800'>{k}{' ★' if star else ''}</div><div style='font-size:25px;font-weight:700'>{ten}</div>"
              f"<div style='font-size:17px;line-height:1.45;color:{C['dat']};margin-top:6px'>{ly}</div></div>{tiles}{post(k)}{cover(k)}</div>")
html = (f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body><div class='pad' style='inset:56px 100px'>"
        f"<div class='kick'>Pattern · vòng 2 · từ B Sóng xoắn</div><h1 style='font-size:46px'>Ba option phát triển, trên 3 nền và 2 ấn phẩm</h1>"
        f"<div style='display:flex;gap:22px;margin:16px 0 0 252px;font-size:16px;color:{C['dat']}'><span style='width:300px'>Nền kem</span><span style='width:300px'>Nền cam</span><span style='width:300px'>Nền nâu đất</span><span style='width:226px'>Bài 1:1</span><span>Bìa slide 16:9</span></div>"
        f"{cells}</div><div class='foot' style='left:100px;right:100px'><span>TUVA Communication · Brand ID · G5 vòng 2 · 11/11/2026</span><span>★ B2</span></div></body></html>")

if __name__ == "__main__":
    f = ROOT / "_G5-pattern-vong2.html"; f.write_text(html, encoding="utf-8")
    with sync_playwright() as p:
        b = p.chromium.launch(channel="msedge"); pg = b.new_page(viewport={"width": 1920, "height": 1080})
        pg.goto(f.as_uri()); pg.wait_for_timeout(500)
        out = ROOT / "05-pattern" / "G5-pattern-vong2.png"; pg.screenshot(path=str(out)); print(out); b.close()
