# Dựng trang G4 + G5 vòng 1 + Điểm chờ chốt cho Unikon (1920x1080 PNG). Chạy: python -I unikon_g45.py
import math, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(r"D:\LINHX\LAB\LAB122-BRAND-ID-4BU\UNIKON")
LOGO = pathlib.Path(r"D:\LINHX\LAB\LAB043-DESIGN-ONBRAND\brands\unikon\01-logo")
FONT = pathlib.Path(r"D:\LINHX\LAB\LAB043-DESIGN-ONBRAND\nguon-logo-linh-19-10\if agent\Fonts\Montserrat-VariableFont_wght.ttf").as_uri()

# Màu đo từ logo gốc (stop-color trong SVG xuất từ logo_Unikon_done)
C = dict(vang="#FBA916", cam="#F7941D", hong="#EF2951", magenta="#E6155F", man="#A02487",
         tim="#5113A4", xanh="#255FB0", chu="#58595B", dem="#160B2A", kem="#FAF7F4")
GRAD = f"linear-gradient(90deg,{C['xanh']},{C['tim']},{C['man']},{C['magenta']},{C['cam']},{C['vang']})"

CSS = f"""
@font-face{{font-family:M;src:url('{FONT}');font-weight:100 900}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1920px;height:1080px;font-family:M,sans-serif;color:{C['dem']};background:{C['kem']};overflow:hidden;position:relative}}
.pad{{position:absolute;inset:96px 120px}}
.kick{{font-size:22px;letter-spacing:.18em;text-transform:uppercase;font-weight:600;color:{C['man']}}}
h1{{font-size:64px;font-weight:700;line-height:1.1;margin-top:20px}}
.bar{{height:10px;border-radius:5px;background:{GRAD}}}
.foot{{position:absolute;left:120px;right:120px;bottom:48px;display:flex;justify-content:space-between;font-size:18px;color:{C['chu']}}}
.src{{font-size:17px;color:{C['chu']};line-height:1.5}}
"""

def defs():
    return f"""<defs><linearGradient id="g" x1="0" y1="1" x2="1" y2="0">
<stop offset="0" stop-color="{C['tim']}"/><stop offset=".45" stop-color="{C['magenta']}"/>
<stop offset=".75" stop-color="{C['cam']}"/><stop offset="1" stop-color="{C['vang']}"/></linearGradient>
<linearGradient id="gh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C['xanh']}"/>
<stop offset=".3" stop-color="{C['tim']}"/><stop offset=".55" stop-color="{C['magenta']}"/>
<stop offset=".8" stop-color="{C['cam']}"/><stop offset="1" stop-color="{C['vang']}"/></linearGradient></defs>"""

def crescent(cx, cy, r, rot, fill, op=1):
    # vành khuyết: đường tròn ngoài trừ đường tròn lệch (DNA vành trăng của biểu tượng)
    o = r * 0.38
    return (f'<path transform="rotate({rot} {cx} {cy})" fill="{fill}" opacity="{op}" fill-rule="evenodd" '
            f'd="M{cx-r},{cy} a{r},{r} 0 1,0 {2*r},0 a{r},{r} 0 1,0 {-2*r},0 Z '
            f'M{cx-r*0.86+o},{cy-o*0.5} a{r*0.86},{r*0.86} 0 1,0 {2*r*0.86},0 a{r*0.86},{r*0.86} 0 1,0 {-2*r*0.86},0 Z"/>')

def pat(kind, w, h, nen):
    ink = "#FFFFFF" if nen != "kem" else C["dem"]
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{defs()}']
    bg = {"kem": C["kem"], "mau": "url(#g)", "toi": C["dem"]}[nen]
    s.append(f'<rect width="{w}" height="{h}" fill="{bg}"/>')
    if kind == "A":  # Vành khuyết: lưới vành lặp (quy mô lớn), một vành màu nổi (độc nhất)
        r = h / 7; i = 0
        for row in range(5):
            for col in range(int(w / (r * 2.6)) + 2):
                cx = col * r * 2.6 + (r * 1.3 if row % 2 else 0); cy = r * 0.9 + row * r * 1.55
                hero = (row == 2 and col == 2)
                fill = ("url(#g)" if nen != "mau" else "#FFFFFF") if hero else ink
                s.append(crescent(cx, cy, r * (1.05 if hero else 0.62), 25 + (row * 37 + col * 53) % 90 if not hero else 20, fill, 1 if hero else 0.14))
                i += 1
    elif kind == "B":  # Tia sừng: nét thon chéo theo góc sừng, nhịp dày, một tia màu dài
        ang = math.radians(62); step = w / 26
        for k in range(-8, 34):
            x0 = k * step; L = h * (0.35 + ((k * 7) % 5) * 0.12); y0 = h * (0.95 - ((k * 3) % 4) * 0.08)
            hero = (k == 9)
            x1 = x0 + math.cos(ang) * (L * (1.6 if hero else 1)); y1 = y0 - math.sin(ang) * (L * (1.6 if hero else 1))
            wd = step * (0.42 if hero else 0.22)
            nx, ny = math.sin(ang) * wd, math.cos(ang) * wd
            fill = ("url(#g)" if nen != "mau" else "#FFFFFF") if hero else ink
            s.append(f'<path d="M{x0-nx:.1f},{y0-ny:.1f} L{x0+nx:.1f},{y0+ny:.1f} L{x1:.1f},{y1:.1f} Z" fill="{fill}" opacity="{1 if hero else 0.16}"/>')
    else:  # C Dải phổ: các vạch bo tròn dài ngắn như dòng nội dung, một vạch mang dải phổ đầy đủ
        lh = h / 11
        for row in range(10):
            x = 0
            seq = [(row * 5 + j * 3) % 7 for j in range(12)]
            for j, q in enumerate(seq):
                ln = w * (0.05 + q * 0.035)
                hero = (row == 5 and j == 1)
                fill = ("url(#gh)" if nen != "mau" else "#FFFFFF") if hero else ink
                s.append(f'<rect x="{x:.1f}" y="{lh*0.7+row*lh:.1f}" width="{ln*(2.2 if hero else 1):.1f}" height="{lh*0.42:.1f}" rx="{lh*0.21:.1f}" fill="{fill}" opacity="{1 if hero else 0.13}"/>')
                x += ln * (2.2 if hero else 1) + lh * 0.5
                if x > w: break
    s.append("</svg>")
    return "".join(s)

def page(body, name):
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>", name

def foot(n):
    return f"<div class='foot'><span>Unikon · Brand ID · bản nháp G4–G5 vòng 1 · 11/11/2026</span><span>{n}</span></div>"

logo = (LOGO / "logo-ngang-mau.svg").as_uri()
logo_t = (LOGO / "logo-ngang-mau-nen-toi.svg").as_uri()

pages = []
# P1 Về thương hiệu (câu nguồn nguyên văn)
pages.append(page(f"""<div class='pad'>
<img src='{logo}' style='height:96px'>
<div class='kick' style='margin-top:80px'>Về thương hiệu</div>
<h1 style='max-width:1500px'>Leading AI Campaign Sub-Agency<br>for Big Agencies &amp; Brands in Vietnam</h1>
<div class='src' style='margin-top:14px'>Định vị · chiến lược Unikon 2026 (v2.0, 25/02/2026) · Linh chốt 11/11</div>
<div class='bar' style='width:420px;margin:56px 0'></div>
<div style='display:flex;gap:64px'>
 <div style='flex:1.3'><div class='kick'>Tầm nhìn</div><p style='font-size:30px;line-height:1.45;margin-top:16px;font-weight:500'>Chúng tôi giúp khách hàng tự động hóa truyền thông bằng nền tảng content marketing tự động.</p>
 <p style='font-size:40px;font-weight:700;margin-top:18px;color:{C['magenta']}'>Agentic content at mass scale</p></div>
 <div style='flex:1'><div class='kick'>Analyse · Generate · Distribute</div>
 <p style='font-size:24px;line-height:1.55;margin-top:16px'><b>Analyse</b> · our machine analyses and collects relevant insights<br><b>Generate</b> · automatically create trendy unique content in all formats<br><b>Distribute</b> · deliver content to social channels</p>
 <div class='src' style='margin-top:12px'>Nguyên văn Credentials 2025, slide 10–11</div></div>
</div></div>{foot('G4 · 1/2')}""", "G4-1-ve-thuong-hieu"))

# P2 Tinh thần nhận diện: hai vế từ chính tầm nhìn "Unique content at mass scale"
pages.append(page(f"""<div style='position:absolute;inset:0;background:{C['dem']};color:#fff'>
<div class='pad'>
<div class='kick' style='color:{C['vang']}'>Tinh thần nhận diện</div>
<div style='display:flex;align-items:center;justify-content:space-between;margin-top:200px'>
 <div style='width:640px'><div style='font-size:92px;font-weight:800'>Agentic</div>
 <p style='font-size:28px;line-height:1.5;margin-top:20px;opacity:.9'>Tác tử AI tự làm việc: một chủ thể chủ động, có hướng; biểu tượng kỳ lân dẫn mắt.</p>
 <p style='font-size:20px;margin-top:20px;opacity:.65'>Hệ quả: 1 điểm nhấn màu có hướng / trang · khoảng trống ≥ 40% · một chủ thể</p></div>
 <img src='{(LOGO / "bieu-tuong-mau.svg").as_uri()}' style='height:300px'>
 <div style='width:640px;text-align:right'><div style='font-size:92px;font-weight:800'>Mass scale</div>
 <p style='font-size:28px;line-height:1.5;margin-top:20px;opacity:.9'>Nhịp lặp đều của hệ thống: lưới, pattern lặp, nội dung nhân bản tự động.</p>
 <p style='font-size:20px;margin-top:20px;opacity:.65'>Hệ quả: lưới 12 cột · pattern lặp độ mờ 10–16% · chữ không chân</p></div>
</div>
<div class='bar' style='margin-top:170px'></div>
<p style='font-size:22px;margin-top:22px;opacity:.75'>Chữ nguồn: tagline "Agentic content at mass scale" (Linh chốt 11/11/2026). Biểu tượng đứng giữa làm điểm nối hai vế.</p>
</div><div class='foot' style='color:#bbb'><span>Unikon · Brand ID · bản nháp</span><span>G4 · 2/2</span></div></div>""", "G4-2-tinh-than"))

# P3 Bảng 3 hệ pattern vòng 1
rows = [("A", "Vành khuyết", "Vành trăng ôm đầu kỳ lân, lặp thành lưới; một vành màu là tác tử \"agentic\".", True),
        ("B", "Tia sừng", "Nét thon theo góc sừng, nhịp dày như tốc độ; một tia màu dài.", False),
        ("C", "Dải phổ", "Thanh gradient dưới logo gốc, cắt thành dòng nội dung dài ngắn.", False)]
cells = ""
for k, ten, ly, star in rows:
    tiles = "".join(f"<div style='border-radius:14px;overflow:hidden;box-shadow:0 0 0 1px #0001'>{pat(k, 400, 225, n)}</div>" for n in ("kem", "mau", "toi"))
    cells += (f"<div style='display:flex;align-items:center;gap:28px;margin-top:26px'>"
              f"<div style='width:330px'><div style='font-size:40px;font-weight:800'>{k}{' ★' if star else ''}</div>"
              f"<div style='font-size:28px;font-weight:700'>{ten}</div><div style='font-size:18px;line-height:1.45;color:{C['chu']};margin-top:6px'>{ly}</div></div>{tiles}</div>")
pages.append(page(f"""<div class='pad' style='inset:64px 120px'><div class='kick'>Pattern · vòng 1</div>
<h1 style='font-size:48px'>Ba hệ rút từ DNA logo Unikon</h1>
<div style='display:flex;gap:28px;margin:18px 0 0 358px;font-size:17px;color:{C['chu']}'><span style='width:400px'>Nền kem</span><span style='width:400px'>Nền gradient</span><span style='width:400px'>Nền đêm tím</span></div>
{cells}</div>{foot('G5 · vòng 1')}""", "G5-pattern-vong1"))

# P4 Điểm chờ chốt
qs = [("1", "Định vị công khai", "A · Leading AI Campaign Service for Marketing in Vietnam", "B · Leading AI Campaign Sub-Agency for Big Agencies & Brands in Vietnam", "A", "Đang ở hồ sơ công ty; nói được với cả brand lẫn agency."),
      ("2", "Tầm nhìn trên guideline", "A · câu tiếng Việt 2021 (tagline mới: Agentic content at mass scale)", "B · câu tiếng Anh Credentials 2025", "A", "Có câu Việt và tagline riêng, làm gốc cho tinh thần."),
      ("3", "Giá trị cốt lõi", "A · để trống, ghi \"chờ CEO\"", "B · Linh hoặc CEO gửi nguyên văn", "A", "Tài liệu không có; không tự viết."),
      ("4", "Pattern vòng 1", "A Vành khuyết · B Tia sừng · C Dải phổ", "", "A", "Rõ DNA nhất, lặp được, một vành màu là tác tử \"agentic\".")]
q = "".join(f"<div style='display:flex;gap:30px;padding:26px 0;border-top:1px solid #0002'><div style='font-size:44px;font-weight:800;width:60px;color:{C['magenta']}'>{n}</div>"
            f"<div style='flex:1'><div style='font-size:30px;font-weight:700'>{t}</div><div style='font-size:22px;margin-top:8px;line-height:1.5'>{a}<br>{b}</div></div>"
            f"<div style='width:520px'><div style='font-size:30px;font-weight:800'>★ {s}</div><div style='font-size:20px;color:{C['chu']};margin-top:6px'>{l}</div></div></div>" for n, t, a, b, s, l in qs)
pages.append(page(f"""<div class='pad' style='inset:72px 120px'><div style='display:flex;justify-content:space-between;align-items:center'>
<div><div class='kick'>Điểm chờ chốt · Unikon</div><h1 style='font-size:52px'>Đã chốt 1B · 2A 3A 4A đi theo ★, chưa duyệt</h1></div><img src='{logo}' style='height:70px'></div>
<div style='margin-top:30px'>{q}</div>
<p style='font-size:20px;color:{C['chu']};margin-top:10px'>Logo giữ bản gốc đã chốt 19/10. Im 10 phút thì đi theo ★ (ghi "đi theo ★, chưa duyệt").</p></div>{foot('Chờ chốt')}""", "CHO-CHOT"))

if __name__ == '__main__':
  with sync_playwright() as p:
      b = p.chromium.launch(channel="msedge"); pg = b.new_page(viewport={"width": 1920, "height": 1080})
      for html, name in pages:
          f = ROOT / f"_{name}.html"; f.write_text(html, encoding="utf-8")
          pg.goto(f.as_uri()); pg.wait_for_timeout(400)
          out = ROOT / ("CHO-CHOT.png" if name == "CHO-CHOT" else ("04-tinh-than" if name.startswith("G4") else "05-pattern") + f"/{name}.png")
          pg.screenshot(path=str(out)); print(out)
      b.close()
