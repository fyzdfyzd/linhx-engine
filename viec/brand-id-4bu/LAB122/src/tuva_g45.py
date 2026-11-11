# Dựng trang G4 + G5 vòng 1 + Điểm chờ chốt cho TUVA (1920x1080 PNG). Chạy: python -I tuva_g45.py
# Luật Linh: mọi hoạ tiết là XOẮN ỐC (sóng, vỏ ốc, tù và), KHÔNG vòng đồng tâm. Nâu #2A1F1B + cam #FAA71B.
import math, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(r"D:\LINHX\LAB\LAB122-BRAND-ID-4BU\TUVA")
LOGO = pathlib.Path(r"D:\LINHX\LAB\LAB043-DESIGN-ONBRAND\brands\tuva\01-logo")
FONT = pathlib.Path(r"D:\LINHX\LAB\LAB043-DESIGN-ONBRAND\nguon-logo-linh-19-10\if agent\Fonts\Montserrat-VariableFont_wght.ttf").as_uri()
C = dict(nau="#2A1F1B", cam="#FAA71B", kem="#F4EFE8", dat="#6B5B4F", chu="#4A3F39")
CSS = f"""
@font-face{{font-family:M;src:url('{FONT}');font-weight:100 900}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1920px;height:1080px;font-family:M,sans-serif;color:{C['nau']};background:{C['kem']};overflow:hidden;position:relative}}
.pad{{position:absolute;inset:96px 120px}}
.kick{{font-size:22px;letter-spacing:.18em;text-transform:uppercase;font-weight:600;color:{C['cam']}}}
h1{{font-size:64px;font-weight:700;line-height:1.1;margin-top:20px}}
.bar{{height:6px;border-radius:3px;background:{C['cam']}}}
.foot{{position:absolute;left:120px;right:120px;bottom:48px;display:flex;justify-content:space-between;font-size:18px;color:{C['dat']}}}
.src{{font-size:17px;color:{C['dat']};line-height:1.5}}
"""

def spiral(cx, cy, R, rot, lines, col, sw, op, turns=1.6):
    """Tù và: nhiều nét xoắn logarit lệch pha, cuộn vào tâm (không phải vòng đồng tâm)."""
    out = []
    for j in range(lines):
        pts = []; k = 1 - j / (lines + 1.5)
        for i in range(120):
            t = i / 119; th = math.radians(rot) + t * turns * 2 * math.pi
            r = R * k * math.exp(-2.1 * (1 - t)) * (0.35 + 0.65 * t)
            pts.append(f"{cx + r*math.cos(th):.1f},{cy + r*math.sin(th):.1f}")
        out.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" opacity="{op}"/>')
    return "".join(out)

def wave(x0, y, w, amp, col, sw, op):
    """Sóng xoắn: đường sóng, mỗi đỉnh cuộn thành một xoắn nhỏ."""
    out = []; L = amp * 6
    n = int(w / L) + 2
    d = f"M{x0},{y}"
    for i in range(n):
        x = x0 + i * L
        d += f" C{x+L*0.3},{y} {x+L*0.4},{y-amp} {x+L*0.6},{y-amp}"
        d += f" C{x+L*0.8},{y-amp} {x+L*0.85},{y} {x+L},{y}"
        out.append(spiral(x + L * 0.62, y - amp * 1.05, amp * 0.9, 180, 1, col, sw, op, turns=1.2))
    out.insert(0, f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw}" opacity="{op}"/>')
    return "".join(out)

def pat(kind, w, h, nen):
    ink = C["nau"] if nen == "kem" else "#FFFFFF"
    hero = C["nau"] if nen == "mau" else C["cam"]
    bg = {"kem": C["kem"], "mau": C["cam"], "toi": C["nau"]}[nen]
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}"><rect width="{w}" height="{h}" fill="{bg}"/>']
    if kind == "A":  # Tù và: lưới tù và nhỏ nhạt, một tù và lớn màu
        r = h / 9
        for row in range(5):
            for col in range(10):
                cx = col * r * 2.4 + (r * 1.2 if row % 2 else 0); cy = r + row * r * 2
                s.append(spiral(cx, cy, r * 0.75, (row * 50 + col * 70) % 360, 4, ink, 1.6, 0.16))
        s.append(spiral(w * 0.5, h * 0.5, h * 0.36, 30, 9, hero, 3.2, 1))
    elif kind == "B":  # Sóng xoắn: các hàng sóng cuộn đỉnh
        for row in range(6):
            s.append(wave(-40 + (row % 2) * 30, h * (0.16 + row * 0.15), w + 80, h * 0.035, ink, 2, 0.18))
        s.append(wave(-40, h * 0.62, w + 80, h * 0.07, hero, 4, 1))
    else:  # C Xoắn lớn cắt khung: một tù và khổng lồ từ góc, nhiều nét mảnh
        s.append(spiral(w * 0.78, h * 0.62, h * 1.25, 160, 16, ink, 1.8, 0.28, turns=1.9))
        s.append(spiral(w * 0.78, h * 0.62, h * 1.25, 160, 1, hero, 5, 1, turns=1.9))
    return "".join(s) + "</svg>"

def page(body, name):
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>", name

def foot(n, col=None):
    st = f" style='color:{col}'" if col else ""
    return f"<div class='foot'{st}><span>TUVA Communication · Brand ID · bản nháp G4–G5 vòng 1 · 11/11/2026</span><span>{n}</span></div>"

logo = (LOGO / "logo-ngang-mau.svg").as_uri(); logo_am = (LOGO / "logo-ngang-am-ban.svg").as_uri()
icon_t = (LOGO / "bieu-tuong-trang.svg").as_uri()
pages = []
pages.append(page(f"""<div class='pad'><img src='{logo}' style='height:96px'>
<div class='kick' style='margin-top:96px'>Về thương hiệu</div>
<h1 style='font-size:68px;max-width:1500px'>Strategic narrative &amp;<br>AI-enabled fundraising partner</h1>
<div class='src' style='margin-top:14px'>Định vị · chiến lược TUVA 2026–2029 · Linh chốt 11/11</div>
<div class='bar' style='width:300px;margin:56px 0'></div>
<div style='display:flex;gap:64px'>
 <div style='flex:1.2'><div class='kick'>Nguồn gốc</div><p style='font-size:25px;line-height:1.55;margin-top:14px;font-weight:500'>Từ 2017: đơn vị truyền thông đồng hành cùng các dự án xã hội. "Ăn cơm nhà vác tù và hàng tổng."</p>
 <div class='src' style='margin-top:8px'>Hồ sơ năng lực TUVA Communication 2022, trang 5–6</div></div>
 <div style='flex:1'><div class='kick'>Giá trị cốt lõi</div><p style='font-size:34px;font-weight:700;margin-top:14px'>Tự do · Bình đẳng · Bao dung</p>
 <p style='font-size:21px;margin-top:12px;color:{C['dat']}'>Vế công nghệ Decent AI: chờ Linh chọn (câu 2)</p></div>
</div></div>{foot('G4 · 1/2')}""", "G4-1-ve-thuong-hieu"))

pages.append(page(f"""<div style='position:absolute;inset:0;background:{C['nau']};color:#fff'><div class='pad'>
<div class='kick'>Tinh thần nhận diện · REACHING OUT</div>
<div style='display:flex;align-items:center;justify-content:space-between;margin-top:170px'>
 <div style='width:620px'><div style='font-size:80px;font-weight:800;line-height:1.05'>Cộng đồng</div>
 <p style='font-size:28px;line-height:1.5;margin-top:22px;opacity:.9'>"Ăn cơm nhà vác tù và hàng tổng": gốc ở cộng đồng, cất tiếng cho việc chung.</p>
 <p style='font-size:20px;margin-top:20px;opacity:.65'>Hệ quả: nền nâu đất · ảnh tư liệu thật có đồng ý · khoảng thở rộng</p></div>
 <img src='{icon_t}' style='height:290px'>
 <div style='width:620px;text-align:right'><div style='font-size:80px;font-weight:800;line-height:1.05'>Công nghệ</div>
 <p style='font-size:28px;line-height:1.5;margin-top:22px;opacity:.9'>Dữ liệu và AI tử tế (decent AI): tiếng tù và đi xa hơn, đúng người hơn.</p>
 <p style='font-size:20px;margin-top:20px;opacity:.65'>Hệ quả: sóng xoắn làm nhịp · cam chỉ làm điểm nhấn · dữ liệu vẽ bằng sóng</p></div>
</div><div class='bar' style='margin-top:110px'></div>
<p style='font-size:22px;margin-top:22px;opacity:.8'>REACHING OUT mang hai nghĩa: vươn tới cộng đồng, và vươn xa bằng công nghệ. Câu tiếng Việt đi kèm: chờ Linh chọn (câu 3).</p>
</div>{foot('G4 · 2/2', '#cbbfb5')}</div>""", "G4-2-tinh-than"))


rows = [("A", "Tù và", "Xoắn nhiều nét của biểu tượng, lặp nhạt; một tù và lớn màu cam.", True),
        ("B", "Sóng xoắn", "Hàng sóng, mỗi đỉnh cuộn thành xoắn nhỏ; một làn sóng cam.", False),
        ("C", "Xoắn lớn", "Một tù và khổng lồ cắt khung, nét mảnh; một nét cam dẫn mắt.", False)]
cells = ""
for k, ten, ly, star in rows:
    tiles = "".join(f"<div style='border-radius:14px;overflow:hidden;box-shadow:0 0 0 1px #0001'>{pat(k, 400, 225, n)}</div>" for n in ("kem", "mau", "toi"))
    cells += (f"<div style='display:flex;align-items:center;gap:28px;margin-top:26px'><div style='width:330px'>"
              f"<div style='font-size:40px;font-weight:800'>{k}{' ★' if star else ''}</div><div style='font-size:28px;font-weight:700'>{ten}</div>"
              f"<div style='font-size:18px;line-height:1.45;color:{C['dat']};margin-top:6px'>{ly}</div></div>{tiles}</div>")
pages.append(page(f"""<div class='pad' style='inset:64px 120px'><div class='kick'>Pattern · vòng 1</div>
<h1 style='font-size:48px'>Ba hệ xoắn ốc rút từ biểu tượng tù và</h1>
<div style='display:flex;gap:28px;margin:18px 0 0 358px;font-size:17px;color:{C['dat']}'><span style='width:400px'>Nền kem</span><span style='width:400px'>Nền cam</span><span style='width:400px'>Nền nâu đất</span></div>
{cells}</div>{foot('G5 · vòng 1')}""", "G5-pattern-vong1"))

qs = [("1", "Định vị trên guideline", "A · strategic narrative &amp; AI-enabled fundraising partner (chiến lược 2026–2029)", "B · đơn vị truyền thông đồng hành cùng các dự án xã hội (hồ sơ 2022)", "B", "Câu công khai hiện tại; A ghi là tầm nhìn."),
      ("2", "Giá trị cốt lõi", "A · Tự do — Bình đẳng — Bao dung", "B · chờ Linh", "A", "Có ở hồ sơ công ty; cần Linh xác nhận."),
      ("3", "Câu Việt đi cùng REACHING OUT", "A · Ăn cơm nhà, vác tù và hàng tổng (hồ sơ 2022)", "B · đến với nhiều người hơn (chữ tự dịch)", "A", "Đúng chữ nguồn, không thêm câu mới."),
      ("4", "Pattern vòng 1", "A Tù và · B Sóng xoắn · C Xoắn lớn", "", "A", "Gần biểu tượng nhất, lặp được ở cỡ nhỏ.")]
q = "".join(f"<div style='display:flex;gap:30px;padding:24px 0;border-top:1px solid #0002'><div style='font-size:44px;font-weight:800;width:60px;color:{C['cam']}'>{n}</div>"
            f"<div style='flex:1'><div style='font-size:30px;font-weight:700'>{t}</div><div style='font-size:21px;margin-top:8px;line-height:1.5'>{a}<br>{b}</div></div>"
            f"<div style='width:480px'><div style='font-size:30px;font-weight:800'>★ {s}</div><div style='font-size:20px;color:{C['dat']};margin-top:6px'>{l}</div></div></div>" for n, t, a, b, s, l in qs)
pages.append(page(f"""<div class='pad' style='inset:72px 120px'><div style='display:flex;justify-content:space-between;align-items:center'>
<div><div class='kick'>Điểm chờ chốt · TUVA Communication</div><h1 style='font-size:52px'>Linh trả lời kiểu: 1B 2A 3A 4A</h1></div><img src='{logo}' style='height:70px'></div>
<div style='margin-top:26px'>{q}</div>
<p style='font-size:20px;color:{C['dat']};margin-top:10px'>Logo giữ bản gốc TUVA_Logo_done.ai đã chốt 19/10. Im 10 phút thì đi theo ★ (ghi "đi theo ★, chưa duyệt").</p></div>{foot('Chờ chốt')}""", "CHO-CHOT"))

if __name__ == "__main__":
    with sync_playwright() as p:
        b = p.chromium.launch(channel="msedge"); pg = b.new_page(viewport={"width": 1920, "height": 1080})
        for html, name in pages:
            f = ROOT / f"_{name}.html"; f.write_text(html, encoding="utf-8")
            pg.goto(f.as_uri()); pg.wait_for_timeout(400)
            sub = "" if name == "CHO-CHOT" else ("04-tinh-than/" if name.startswith("G4") else "05-pattern/")
            out = ROOT / f"{sub}{name}.png"; out.parent.mkdir(exist_ok=True); pg.screenshot(path=str(out)); print(out)
        b.close()
