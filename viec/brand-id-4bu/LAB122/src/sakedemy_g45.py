# Dựng trang G4 + G5 vòng 1 + Điểm chờ chốt cho Sakédemy (1920x1080 PNG). Chạy: python -I sakedemy_g45.py
# Luật Linh: xanh lá nhã, KHÔNG hồng, mọi hoạ tiết là LÁ. Viết "Sakédemy".
import math, pathlib, random
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(r"D:\LINHX\LAB\LAB122-BRAND-ID-4BU\SAKEDEMY")
LOGO = pathlib.Path(r"D:\LINHX\LAB\LAB043-DESIGN-ONBRAND\brands\sakedemy\01-logo")
FONT = pathlib.Path(r"D:\LINHX\LAB\LAB043-DESIGN-ONBRAND\nguon-logo-linh-19-10\if agent\Fonts\Montserrat-VariableFont_wght.ttf").as_uri()
# Màu file gốc người thiết kế (LAB043 4.2 E) + rêu đậm từ logo xanh đậm
C = dict(la="#1CA571", ngoc="#23B7AC", lanon="#66BC66", choi="#A3D34F", reu="#02403B", chu="#414141", kem="#F5F8F2")
for v in C.values():
    r, g, b = int(v[1:3], 16), int(v[3:5], 16), int(v[5:7], 16)
    assert not (r > g + 40 and r > 150), f"màu nghi hồng/đỏ: {v}"
GRAD = f"linear-gradient(90deg,{C['ngoc']},{C['la']},{C['lanon']},{C['choi']})"
CSS = f"""
@font-face{{font-family:M;src:url('{FONT}');font-weight:100 900}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1920px;height:1080px;font-family:M,sans-serif;color:{C['reu']};background:{C['kem']};overflow:hidden;position:relative}}
.pad{{position:absolute;inset:96px 120px}}
.kick{{font-size:22px;letter-spacing:.18em;text-transform:uppercase;font-weight:600;color:{C['la']}}}
h1{{font-size:64px;font-weight:700;line-height:1.1;margin-top:20px}}
.bar{{height:10px;border-radius:5px;background:{GRAD}}}
.foot{{position:absolute;left:120px;right:120px;bottom:48px;display:flex;justify-content:space-between;font-size:18px;color:{C['chu']}}}
.src{{font-size:17px;color:{C['chu']};line-height:1.5}}
"""
DEFS = f"""<defs><linearGradient id="g" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="{C['ngoc']}"/>
<stop offset=".5" stop-color="{C['la']}"/><stop offset="1" stop-color="{C['choi']}"/></linearGradient></defs>"""

def vein(x, y, L, ang, sw, col, op):
    # gân lá: gân chính chéo + gân phụ hai bên (DNA biểu tượng)
    a = math.radians(ang); dx, dy = math.cos(a), -math.sin(a)
    s = [f'<g stroke="{col}" stroke-width="{sw}" stroke-linecap="round" opacity="{op}" fill="none">',
         f'<line x1="{x}" y1="{y}" x2="{x+dx*L:.1f}" y2="{y+dy*L:.1f}"/>']
    for k in range(1, 5):
        px, py = x + dx * L * k / 5.2, y + dy * L * k / 5.2; bl = L * 0.32 * (1 - k * 0.12)
        for side in (1, -1):
            b = a + side * math.radians(48)
            s.append(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{px+math.cos(b)*bl:.1f}" y2="{py-math.sin(b)*bl:.1f}"/>')
    return "".join(s) + "</g>"

def leaf_tile(cx, cy, r, rot, fill, op):
    # lá vuông bo: ba góc bo tròn, một góc nhọn (đầu lá) như biểu tượng
    k = r * 0.55
    d = (f"M{cx-r},{cy-r+k} Q{cx-r},{cy-r} {cx-r+k},{cy-r} L{cx+r},{cy-r} L{cx+r},{cy+r-k} "
         f"Q{cx+r},{cy+r} {cx+r-k},{cy+r} L{cx-r+k},{cy+r} Q{cx-r},{cy+r} {cx-r},{cy+r-k} Z")
    return f'<path transform="rotate({rot} {cx} {cy})" d="{d}" fill="{fill}" opacity="{op}"/>'

def leaf(cx, cy, L, rot, fill, op):
    # lá hình thoi cong (vesica)
    return (f'<path transform="rotate({rot} {cx} {cy})" d="M{cx-L/2},{cy} Q{cx},{cy-L*0.42} {cx+L/2},{cy} '
            f'Q{cx},{cy+L*0.42} {cx-L/2},{cy} Z" fill="{fill}" opacity="{op}"/>')

def pat(kind, w, h, nen):
    ink = C["reu"] if nen == "kem" else "#FFFFFF"
    hero = "#FFFFFF" if nen == "mau" else "url(#g)"
    bg = {"kem": C["kem"], "mau": "url(#g)", "toi": C["reu"]}[nen]
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{DEFS}<rect width="{w}" height="{h}" fill="{bg}"/>']
    if kind == "A":  # Gân lá: lưới gân lặp nhạt, một gân màu lớn
        for row in range(4):
            for col in range(7):
                x = col * w / 6 - 20 + (30 if row % 2 else 0); y = h * 0.28 + row * h * 0.26
                s.append(vein(x, y, h * 0.3, 45, 3, ink, 0.16))
        s.append(vein(w * 0.38, h * 0.82, h * 0.75, 45, 9, "#FFFFFF" if nen == "mau" else C["la"], 1))
    elif kind == "B":  # Lá vuông: ô lá bo lặp xoay nhẹ, một lá màu
        r = h / 9
        for row in range(5):
            for col in range(9):
                cx = col * r * 2.7 + (r * 1.35 if row % 2 else 0); cy = r * 0.9 + row * r * 2.1
                s.append(leaf_tile(cx, cy, r * 0.62, (row * 17 + col * 29) % 40 - 20, ink, 0.13))
        s.append(leaf_tile(w * 0.5, h * 0.5, r * 1.5, -8, hero, 1))
    else:  # C Lá rơi: lá nhỏ rải thưa + chấm, một lá lớn
        rnd = random.Random(7)
        for _ in range(38):
            s.append(leaf(rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(18, 34), rnd.uniform(0, 180), ink, 0.17))
        for _ in range(26):
            s.append(f'<circle cx="{rnd.uniform(0,w):.0f}" cy="{rnd.uniform(0,h):.0f}" r="3.5" fill="{ink}" opacity=".2"/>')
        s.append(leaf(w * 0.55, h * 0.48, h * 0.62, -35, hero, 1))
    return "".join(s) + "</svg>"

def page(body, name):
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>", name

def foot(n):
    return f"<div class='foot'><span>Sakédemy · Brand ID · bản nháp G4–G5 vòng 1 · 11/11/2026</span><span>{n}</span></div>"

logo = (LOGO / "logo-ngang-mau.svg").as_uri()
icon = (LOGO / "bieu-tuong-mau.svg").as_uri()
pages = []
pages.append(page(f"""<div class='pad'><img src='{logo}' style='height:100px'>
<div class='kick' style='margin-top:90px'>Về thương hiệu</div>
<h1 style='font-size:58px;max-width:1550px'>Không gian học tập văn hoá sáng tạo, nơi mỗi người thể hiện bản thân một cách chân thực.</h1>
<div class='src' style='margin-top:14px'>Định vị phương án A ★ · bám lời Linh 11/11 và hồ sơ "Chương trình đào tạo" tr.3–4 · chờ chốt câu 3</div>
<div class='bar' style='width:420px;margin:56px 0'></div>
<div style='display:flex;gap:56px;align-items:stretch'>
 <div style='flex:1.6;border-left:8px solid {C['la']};padding-left:28px'><div class='kick'>Mảng chính · Sáng tạo văn hoá</div>
 <p style='font-size:26px;line-height:1.5;margin-top:12px;font-weight:500'>Sakédemy được thành lập với tầm nhìn tạo ra các không gian học tập phong phú, nhấn mạnh sự phát triển cá nhân và thể hiện bản thân một cách chân thực.</p>
 <div class='src' style='margin-top:8px'>Authentic · mindset · từ 2016: viết, vẽ, nghệ thuật, kịch bản</div></div>
 <div style='flex:1;border-left:3px solid {C['choi']};padding-left:24px'><div class='kick' style='color:{C['lanon']}'>Nhánh phụ · AI và công nghệ trong sáng tạo và văn hoá</div>
 <p style='font-size:21px;line-height:1.55;margin-top:12px'>Từ 2024: e-learning, khoá học ứng dụng AI, lớp chuyên sâu về tích hợp AI trong giáo dục, truyền thông và sáng tạo nội dung.</p></div>
</div></div>{foot('G4 · 1/2')}""", "G4-1-ve-thuong-hieu"))

pages.append(page(f"""<div style='position:absolute;inset:0;background:{C['reu']};color:#fff'><div class='pad'>
<div class='kick' style='color:{C['choi']}'>Tinh thần nhận diện · gân chính và gân phụ</div>
<div style='display:flex;align-items:center;gap:80px;margin-top:150px'>
 <img src='{icon}' style='height:330px'>
 <div style='flex:1'>
  <div style='font-size:100px;font-weight:800;line-height:1'>Văn hoá sáng tạo</div>
  <p style='font-size:30px;line-height:1.5;margin-top:22px;opacity:.92'>Gân chính. Tiếng nói của riêng mình, thể hiện bản thân một cách chân thực, chiều sâu thẩm mỹ.</p>
  <div style='display:flex;align-items:baseline;gap:22px;margin-top:46px;padding-top:26px;border-top:2px solid #ffffff33'>
   <div style='font-size:40px;font-weight:700;color:{C['choi']}'>AI trong sáng tạo</div>
   <p style='font-size:22px;opacity:.8'>Gân phụ: công cụ đi kèm, không thay mảng chính.</p></div>
 </div></div>
<p style='font-size:20px;margin-top:90px;opacity:.7'>Hệ quả: gân chính 45° làm trục mọi bố cục · nhánh AI dùng màu chồi, cỡ nhỏ hơn một bậc · ảnh người đang làm thật, không ảnh AI chân dung.</p>
</div><div class='foot' style='color:#cfe'><span>Sakédemy · Brand ID · bản nháp</span><span>G4 · 2/2</span></div></div>""", "G4-2-tinh-than"))


rows = [("A", "Gân lá", "Gân chính 45° và gân phụ của biểu tượng, lặp nhạt; một gân màu lớn.", True),
        ("B", "Lá vuông", "Hình lá bo ba góc của biểu tượng, lặp lưới xoay nhẹ; một lá màu.", False),
        ("C", "Lá rơi", "Lá nhỏ và chấm rải thưa, thoáng; một lá lớn làm điểm nhấn.", False)]
cells = ""
for k, ten, ly, star in rows:
    tiles = "".join(f"<div style='border-radius:14px;overflow:hidden;box-shadow:0 0 0 1px #0001'>{pat(k, 400, 225, n)}</div>" for n in ("kem", "mau", "toi"))
    cells += (f"<div style='display:flex;align-items:center;gap:28px;margin-top:26px'><div style='width:330px'>"
              f"<div style='font-size:40px;font-weight:800'>{k}{' ★' if star else ''}</div><div style='font-size:28px;font-weight:700'>{ten}</div>"
              f"<div style='font-size:18px;line-height:1.45;color:{C['chu']};margin-top:6px'>{ly}</div></div>{tiles}</div>")
pages.append(page(f"""<div class='pad' style='inset:64px 120px'><div class='kick'>Pattern · vòng 1</div>
<h1 style='font-size:48px'>Ba hệ lá rút từ DNA logo Sakédemy</h1>
<div style='display:flex;gap:28px;margin:18px 0 0 358px;font-size:17px;color:{C['chu']}'><span style='width:400px'>Nền kem</span><span style='width:400px'>Nền gradient lá</span><span style='width:400px'>Nền rêu đậm</span></div>
{cells}</div>{foot('G5 · vòng 1')}""", "G5-pattern-vong1"))

qs = [("1", "Tầm nhìn · đã chốt A", "Câu hồ sơ PDF, bao 2 nhóm: sáng tạo văn hoá ·", "AI và công nghệ trong sáng tạo và văn hoá", "✓", "Linh chốt 11/11 06:59."),
      ("3", "Câu định vị (mới)", "A · Không gian học tập văn hoá sáng tạo, nơi mỗi người thể hiện bản thân một cách chân thực", "B · Đào tạo sáng tạo: giữ authentic và mindset · C · Văn hoá sáng tạo là gân chính; AI là gân phụ", "A", "Dùng đúng chữ hồ sơ; \"chân thực\" là authentic."),
      ("5", "Pattern vòng 2 (từ Gân lá)", "A1 Lưới gân · A2 Gân chính – gân phụ · A3 Gân trong lá", "", "A2", "Kể đúng kiến trúc 2 mảng: chính và nhánh phụ."),
      ("2·4", "Đã chốt", "Giá trị cốt lõi A · Pattern A Gân lá là signature", "", "✓", "Linh chốt 11/11 06:59.")]
q = "".join(f"<div style='display:flex;gap:30px;padding:26px 0;border-top:1px solid #0002'><div style='font-size:44px;font-weight:800;width:60px;color:{C['la']}'>{n}</div>"
            f"<div style='flex:1'><div style='font-size:30px;font-weight:700'>{t}</div><div style='font-size:22px;margin-top:8px;line-height:1.5'>{a}<br>{b}</div></div>"
            f"<div style='width:520px'><div style='font-size:30px;font-weight:800'>★ {s}</div><div style='font-size:20px;color:{C['chu']};margin-top:6px'>{l}</div></div></div>" for n, t, a, b, s, l in qs)
pages.append(page(f"""<div class='pad' style='inset:72px 120px'><div style='display:flex;justify-content:space-between;align-items:center'>
<div><div class='kick'>Điểm chờ chốt · Sakédemy</div><h1 style='font-size:52px'>Còn chờ: 3 và 5 · trả lời kiểu 3A 5A2</h1></div><img src='{logo}' style='height:70px'></div>
<div style='margin-top:30px'>{q}</div>
<p style='font-size:20px;color:{C['chu']};margin-top:10px'>Logo giữ bản gốc logo_SAKE.ai đã chốt 19/10. Màu theo file gốc người thiết kế. Im 10 phút thì đi theo ★ (ghi "đi theo ★, chưa duyệt").</p></div>{foot('Chờ chốt')}""", "CHO-CHOT"))

if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch(channel="msedge"); pg = b.new_page(viewport={"width": 1920, "height": 1080})
        for html, name in pages:
            f = ROOT / f"_{name}.html"; f.write_text(html, encoding="utf-8")
            pg.goto(f.as_uri()); pg.wait_for_timeout(400)
            sub = "" if name == "CHO-CHOT" else ("04-tinh-than/" if name.startswith("G4") else "05-pattern/")
            out = ROOT / f"{sub}{name}.png"; out.parent.mkdir(exist_ok=True); pg.screenshot(path=str(out)); print(out)
        b.close()
