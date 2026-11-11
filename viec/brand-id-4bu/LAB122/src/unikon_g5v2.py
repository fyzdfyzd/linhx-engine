# G5 vòng 2 Unikon: 3 option phát triển từ hướng A Vành khuyết (Linh đi theo ★ 11/11), mỗi option trên 3 nền + 2 ấn phẩm.
import random, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from playwright.sync_api import sync_playwright
from unikon_g45 import C, CSS, defs, crescent, LOGO, ROOT

def svg(w, h, body, bg):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%" preserveAspectRatio="xMidYMid slice">{defs()}<rect width="{w}" height="{h}" fill="{bg}"/>{body}</svg>'

def opt(k, w, h, nen, free=None):
    """free = (x0,y0,x1,y1) vùng trống cho logo/chữ: không vẽ vành trong đó."""
    ink = "#FFFFFF" if nen != "kem" else C["dem"]
    hero = "#FFFFFF" if nen == "mau" else "url(#g)"
    bg = {"kem": C["kem"], "mau": "url(#g)", "toi": C["dem"]}[nen]
    out = []
    def ok(x, y, r):
        if not free: return True
        x0, y0, x1, y1 = free
        return not (x + r > x0 and x - r < x1 and y + r > y0 and y - r < y1)
    if k == "A1":  # Lưới vành: lưới so le đều, một vành màu lớn (bản vòng 1, siết nhịp)
        r = h / 8
        for row in range(6):
            for col in range(int(w / (r * 2.4)) + 2):
                cx = col * r * 2.4 + (r * 1.2 if row % 2 else 0); cy = r * 0.8 + row * r * 1.45
                if ok(cx, cy, r * 0.6): out.append(crescent(cx, cy, r * 0.55, 30, ink, 0.13))
        hx, hy = (w * 0.78, h * 0.62) if free else (w * 0.5, h * 0.5)
        out.append(crescent(hx, hy, h * 0.2, 20, hero, 1))
    elif k == "A2":  # Vành xoay: một hàng vành xoay dần như khung hình chuyển động (tác tử đang làm việc)
        n = 9; r = h * 0.075
        for row in range(4):
            for i in range(n + 2):
                cx = (i + 0.5) * w / n; cy = h * (0.18 + row * 0.22)
                if ok(cx, cy, r):
                    on = (row == 2 and i == 6)
                    out.append(crescent(cx, cy, r * (1.25 if on else 1), i * 40 + row * 20, hero if on else ink, 1 if on else 0.15))
    else:  # A3 Vành lớn: một vành khổng lồ cắt góc + lưới vành nhỏ mờ dần về phía đối diện (quy mô)
        rnd = random.Random(3); r = h * 0.05
        for row in range(9):
            for col in range(int(w / (r * 3)) + 1):
                cx = col * r * 3 + r; cy = row * r * 2.6 + r
                op = 0.18 * max(0, 1 - (cx / w + cy / h) / 1.4)
                if op > 0.02 and ok(cx, cy, r): out.append(crescent(cx, cy, r, 30, ink, op))
        out.append(crescent(w * 0.98, h * 0.98, h * 0.62, 200, hero, 1))
    return svg(w, h, "".join(out), bg)

logo = (LOGO / "logo-ngang-mau.svg").as_uri(); logo_t = (LOGO / "logo-ngang-mau-nen-toi.svg").as_uri()

def post(k):  # ấn phẩm 1: bài mạng xã hội 1:1, nền tối, logo + tagline ở vùng trống trên-trái
    return (f"<div style='position:relative;width:226px;height:226px;border-radius:12px;overflow:hidden'>{opt(k,1080,1080,'toi',free=(0,0,760,420))}"
            f"<div style='position:absolute;left:16px;top:16px;color:#fff'><img src='{logo_t}' style='height:22px'>"
            f"<div style='font-size:17px;font-weight:800;line-height:1.15;margin-top:12px;width:150px'>Agentic content at mass scale</div></div></div>")

def cover(k):  # ấn phẩm 2: bìa slide 16:9 nền kem, logo + định vị bên trái
    return (f"<div style='position:relative;width:402px;height:226px;border-radius:12px;overflow:hidden;box-shadow:0 0 0 1px #0001'>{opt(k,1920,1080,'kem',free=(0,0,1050,1080))}"
            f"<div style='position:absolute;left:20px;top:22px'><img src='{logo}' style='height:24px'>"
            f"<div style='font-size:15px;font-weight:800;line-height:1.2;margin-top:60px;width:200px;color:{C['dem']}'>Leading AI Campaign Sub-Agency for Big Agencies &amp; Brands in Vietnam</div></div></div>")

rows = [("A1", "Lưới vành", "Lưới so le đều; một vành màu lớn đặt ở vùng 1/3.", True),
        ("A2", "Vành xoay", "Vành xoay dần như khung chuyển động: tác tử đang làm việc.", False),
        ("A3", "Vành lớn", "Một vành lớn cắt góc, lưới nhỏ mờ dần: quy mô.", False)]
cells = ""
for k, ten, ly, star in rows:
    tiles = "".join(f"<div style='width:300px;height:226px;border-radius:12px;overflow:hidden;box-shadow:0 0 0 1px #0001'>{opt(k,1600,1200,n)}</div>" for n in ("kem", "mau", "toi"))
    cells += (f"<div style='display:flex;align-items:center;gap:22px;margin-top:24px'><div style='width:230px'>"
              f"<div style='font-size:36px;font-weight:800'>{k}{' ★' if star else ''}</div><div style='font-size:26px;font-weight:700'>{ten}</div>"
              f"<div style='font-size:17px;line-height:1.45;color:{C['chu']};margin-top:6px'>{ly}</div></div>{tiles}{post(k)}{cover(k)}</div>")
html = (f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body><div class='pad' style='inset:56px 100px'>"
        f"<div class='kick'>Pattern · vòng 2 · từ A Vành khuyết</div><h1 style='font-size:46px'>Ba option phát triển, trên 3 nền và 2 ấn phẩm</h1>"
        f"<div style='display:flex;gap:22px;margin:16px 0 0 252px;font-size:16px;color:{C['chu']}'><span style='width:300px'>Nền kem</span><span style='width:300px'>Nền gradient</span><span style='width:300px'>Nền đêm tím</span><span style='width:226px'>Bài 1:1</span><span>Bìa slide 16:9</span></div>"
        f"{cells}</div><div class='foot' style='left:100px;right:100px'><span>Unikon · Brand ID · G5 vòng 2 · đi theo ★ vòng 1, chưa duyệt · 11/11/2026</span><span>★ A1</span></div></body></html>")

if __name__ == "__main__":
    f = ROOT / "_G5-pattern-vong2.html"; f.write_text(html, encoding="utf-8")
    with sync_playwright() as p:
        b = p.chromium.launch(channel="msedge"); pg = b.new_page(viewport={"width": 1920, "height": 1080})
        pg.goto(f.as_uri()); pg.wait_for_timeout(500)
        out = ROOT / "05-pattern" / "G5-pattern-vong2.png"; pg.screenshot(path=str(out)); print(out); b.close()
