# Dựng trang G4 + G5 vòng 1 + Điểm chờ chốt cho cungai (1920x1080 PNG). Chạy: python -I cungai_g45.py
# Tên trong câu văn: "cungai" (chữ thường, Linh chốt 11/11 07:36); logo giữ CUNGAI. Định vị: "Sống cùng AI".
import pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(r"D:\LINHX\LAB\LAB122-BRAND-ID-4BU\CUNGAI")
SRC = pathlib.Path(r"D:\LINHX\LAB\LAB043-DESIGN-ONBRAND\nguon-logo-linh-19-10\cung ai")
FONT = pathlib.Path(r"D:\LINHX\LAB\LAB043-DESIGN-ONBRAND\nguon-logo-linh-19-10\if agent\Fonts\Montserrat-VariableFont_wght.ttf").as_uri()
# Màu đếm pixel từ "Logo có màu.png" gốc
C = dict(xanh="#2878CE", luc="#49AF53", vang="#F6D200", tim="#B2B4D8", dem="#0F2A4D", kem="#F6F8FC", chu="#4A5568")
CSS = f"""
@font-face{{font-family:M;src:url('{FONT}');font-weight:100 900}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1920px;height:1080px;font-family:M,sans-serif;color:{C['dem']};background:{C['kem']};overflow:hidden;position:relative}}
.pad{{position:absolute;inset:96px 120px}}
.kick{{font-size:22px;letter-spacing:.18em;text-transform:uppercase;font-weight:600;color:{C['xanh']}}}
h1{{font-size:64px;font-weight:700;line-height:1.1;margin-top:20px}}
.foot{{position:absolute;left:120px;right:120px;bottom:48px;display:flex;justify-content:space-between;font-size:18px;color:{C['chu']}}}
.src{{font-size:17px;color:{C['chu']};line-height:1.5}}
.bars{{display:flex;gap:10px;align-items:center}}.bars i{{display:block;height:14px;border-radius:7px}}
"""
BAR = f"<div class='bars'><i style='width:16px;background:{C['luc']}'></i><i style='width:120px;background:{C['xanh']}'></i><i style='width:16px;background:{C['xanh']}'></i><i style='width:60px;background:{C['vang']}'></i></div>"

def bar(x, y, L, hgt, fill, op):
    return f'<rect x="{x:.0f}" y="{y:.0f}" width="{L:.0f}" height="{hgt:.0f}" rx="{hgt/2:.0f}" fill="{fill}" opacity="{op}"/>'

def dot(x, y, hgt, fill, op):
    return f'<circle cx="{x+hgt/2:.0f}" cy="{y+hgt/2:.0f}" r="{hgt/2:.0f}" fill="{fill}" opacity="{op}"/>'

def bubble(x, y, s, ink, op, col=None):
    # bóng thoại kiểu logo: 3 dòng vạch + chấm, đuôi tam giác bo
    h = s * 0.13; out = []
    rows = [(0.05, [("b", 0.55)]), (0.3, [("d", 0), ("b", 0.32), ("b", 0.38)]), (0.55, [("b", 0.32), ("d", 0), ("b", 0.2)])]
    pal = [C["xanh"], C["luc"], C["vang"]] if col else [ink] * 3
    for i, (yy, items) in enumerate(rows):
        xx = x + s * (0.1 if i else 0.25)
        for j, (k, L) in enumerate(items):
            f = pal[(i + j) % 3] if col else ink
            if k == "d": out.append(dot(xx, y + yy * s, h, f, op)); xx += h * 1.6
            else: out.append(bar(xx, y + yy * s, L * s, h, f, op)); xx += L * s + h * 0.6
    tx, ty = x + s * 0.55, y + s * 0.8
    out.append(f'<path d="M{tx:.0f},{ty:.0f} l{s*0.22:.0f},0 l0,{s*0.2:.0f} z" fill="{C["vang"] if col else ink}" opacity="{op}"/>')
    return "".join(out)

def pat(kind, w, h, nen):
    ink = C["xanh"] if nen == "kem" else "#FFFFFF"
    bg = {"kem": C["kem"], "mau": C["xanh"], "toi": C["dem"]}[nen]
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}"><rect width="{w}" height="{h}" fill="{bg}"/>']
    hh = h / 22
    if kind == "A":  # Dòng thoại: các dòng vạch dài ngắn và chấm như tin nhắn; một dòng ba màu
        for row in range(11):
            x = -10 + (row % 3) * 18; y = hh * 0.8 + row * hh * 1.95
            seq = [(row * 7 + j * 5) % 6 for j in range(14)]
            for j, q in enumerate(seq):
                hero = row == 6
                f = [C["luc"], C["xanh"], C["vang"]][j % 3] if hero and nen != "mau" else ("#FFFFFF" if hero else ink)
                op = 1 if hero else 0.14
                if q == 0: s.append(dot(x, y, hh, f, op)); x += hh * 1.6
                else: L = hh * (2 + q * 1.6); s.append(bar(x, y, L, hh, f, op)); x += L + hh * 0.6
                if x > w: break
    elif kind == "B":  # Bóng thoại: lặp bóng thoại nhỏ; một bóng lớn ba màu
        sz = h / 4.2
        for row in range(5):
            for col in range(9):
                bx = col * sz * 1.35 - sz * 0.3 + (sz * 0.67 if row % 2 else 0); by = row * sz * 1.1 - sz * 0.2
                s.append(bubble(bx, by, sz * 0.7, ink, 0.12))
        s.append(bubble(w * 0.5 - h * 0.28, h * 0.22, h * 0.56, ink, 1, col=(nen != "mau")))
    else:  # C Nhịp chấm: cụm ba chấm như "đang gõ", rải thưa; một cụm ba màu
        import random
        rnd = random.Random(5)
        for _ in range(26):
            x, y = rnd.uniform(0, w), rnd.uniform(0, h)
            for k in range(3): s.append(dot(x + k * hh * 1.7, y, hh, ink, 0.16))
        cx, cy, r = w * 0.42, h * 0.45, h * 0.11
        for k, f in enumerate([C["luc"], C["xanh"], C["vang"]]):
            s.append(dot(cx + k * r * 1.5, cy, r, f if nen != "mau" else "#FFFFFF", 1))
    return "".join(s) + "</svg>"

def page(body, name):
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>", name

def foot(n, col=None):
    st = f" style='color:{col}'" if col else ""
    return f"<div class='foot'{st}><span>cungai · Brand ID · bản nháp G4–G5 vòng 1 · 11/11/2026</span><span>{n}</span></div>"

logo = (SRC / "Logo có màu.png").as_uri(); logo_t = (SRC / "Logo trắng.png").as_uri()
pages = []
pages.append(page(f"""<div class='pad'><div style='display:flex;gap:120px'>
<div style='flex:1'><div class='kick' style='margin-top:150px'>Về thương hiệu</div>
<h1 style='font-size:110px;margin-top:30px'>Sống cùng AI</h1>
<div class='src' style='margin-top:16px'>Định vị · Linh chốt 11/11/2026 · tên chương trình "Sống Cùng AI" trên VOV</div>
<div style='margin:56px 0'>{BAR}</div>
<p style='font-size:30px;line-height:1.5;font-weight:500;max-width:1000px'>Mọi thứ người Việt cần để dùng AI nằm ở một chỗ.</p>
<div class='src' style='margin-top:8px'>"cungai.vn · Plan 5 năm", mục 1 (10/11/2026)</div>
<p style='font-size:22px;line-height:1.6;margin-top:36px;max-width:1000px'>Nguồn gốc: mảng truyền thông AI của Sakédemy, 62+ số radio "Sống Cùng AI" trên VOV, điểm tin AI hằng tuần.</p></div>
<img src='{logo}' style='height:560px;margin-top:150px'></div></div>{foot('G4 · 1/2')}""", "G4-1-ve-thuong-hieu"))

pages.append(page(f"""<div style='position:absolute;inset:0;background:{C['dem']};color:#fff'><div class='pad'>
<div class='kick' style='color:{C['vang']}'>Tinh thần nhận diện · Sống cùng AI</div>
<div style='display:flex;align-items:center;justify-content:space-between;margin-top:240px'>
 <div style='width:620px'><div style='font-size:96px;font-weight:800'>Người</div>
 <p style='font-size:28px;line-height:1.5;margin-top:22px;opacity:.9'>Miễn phí cho cá nhân, nói bằng tiếng Việt, giữ hồ sơ AI của từng người.</p>
 <p style='font-size:20px;margin-top:20px;opacity:.65'>Hệ quả: chữ to, câu ngắn · bóng thoại làm khung · màu vui nhưng ít</p></div>
 <img src='{logo_t}' style='height:330px'>
 <div style='width:620px;text-align:right'><div style='font-size:96px;font-weight:800'>Agent</div>
 <p style='font-size:28px;line-height:1.5;margin-top:22px;opacity:.9'>Mở cho agent gọi và trích; dữ liệu Việt đã kiểm, công thức đã thử thật.</p>
 <p style='font-size:20px;margin-top:20px;opacity:.65'>Hệ quả: vạch và chấm như dòng dữ liệu · lưới rõ · số liệu có nguồn</p></div>
</div><div style='margin-top:120px;display:flex;justify-content:center'>{BAR}</div>
<p style='font-size:22px;margin-top:26px;opacity:.8;text-align:center'>Chữ nguồn: "Sống cùng AI" (Linh chốt) · luật chơi Plan 5 năm: miễn phí cho người, nguồn agent gọi và trích.</p>
</div>{foot('G4 · 2/2', '#a9b8cf')}</div>""", "G4-2-tinh-than"))

rows = [("A", "Dòng thoại", "Vạch dài ngắn và chấm của logo, xếp thành dòng tin nhắn; một dòng ba màu.", True),
        ("B", "Bóng thoại", "Bóng thoại nhỏ của logo lặp lưới; một bóng lớn ba màu.", False),
        ("C", "Nhịp chấm", "Cụm ba chấm như \"đang gõ\", rải thưa; một cụm ba màu.", False)]
cells = ""
for k, ten, ly, star in rows:
    tiles = "".join(f"<div style='border-radius:14px;overflow:hidden;box-shadow:0 0 0 1px #0001'>{pat(k, 400, 225, n)}</div>" for n in ("kem", "mau", "toi"))
    cells += (f"<div style='display:flex;align-items:center;gap:28px;margin-top:26px'><div style='width:330px'>"
              f"<div style='font-size:40px;font-weight:800'>{k}{' ★' if star else ''}</div><div style='font-size:28px;font-weight:700'>{ten}</div>"
              f"<div style='font-size:18px;line-height:1.45;color:{C['chu']};margin-top:6px'>{ly}</div></div>{tiles}</div>")
pages.append(page(f"""<div class='pad' style='inset:64px 120px'><div class='kick'>Pattern · vòng 1</div>
<h1 style='font-size:48px'>Ba hệ rút từ vạch và chấm của bóng thoại cungai</h1>
<div style='display:flex;gap:28px;margin:18px 0 0 358px;font-size:17px;color:{C['chu']}'><span style='width:400px'>Nền sáng</span><span style='width:400px'>Nền xanh</span><span style='width:400px'>Nền đêm</span></div>
{cells}</div>{foot('G5 · vòng 1')}""", "G5-pattern-vong1"))

qs = [("C3", "Giá trị cốt lõi (Claude viết theo lời Linh)", "A · Miễn phí cho người · Mở cho agent · Đã thử thật · Bằng tiếng Việt", "B · Mở · Thật · Việt  ·  C · Ai cũng dùng được · Việc gì cũng đã thử · Câu nào cũng tiếng Việt", "A", "Giữ đúng 4 ý của Plan 5 năm."),
      ("C4", "Pattern vòng 1", "A Dòng thoại · B Bóng thoại · C Nhịp chấm", "", "A", "Gần nét logo nhất, đọc như dòng nội dung."),
      ("✓", "Đã chốt 07:36", "C1A tên \"cungai\" chữ thường trong câu · logo giữ CUNGAI", "C2B định vị \"Sống cùng AI\" · logo gốc đã chốt (6a)", "", "")]
q = "".join(f"<div style='display:flex;gap:30px;padding:26px 0;border-top:1px solid #0002'><div style='font-size:40px;font-weight:800;width:80px;color:{C['xanh']}'>{n}</div>"
            f"<div style='flex:1'><div style='font-size:30px;font-weight:700'>{t}</div><div style='font-size:22px;margin-top:8px;line-height:1.5'>{a}<br>{b}</div></div>"
            f"<div style='width:460px'><div style='font-size:30px;font-weight:800'>{'★ '+s if s else ''}</div><div style='font-size:20px;color:{C['chu']};margin-top:6px'>{l}</div></div></div>" for n, t, a, b, s, l in qs)
pages.append(page(f"""<div class='pad' style='inset:72px 120px'><div style='display:flex;justify-content:space-between;align-items:center'>
<div><div class='kick'>Điểm chờ chốt · cungai</div><h1 style='font-size:52px'>Linh trả lời kiểu: C3A C4A</h1></div><img src='{logo}' style='height:120px'></div>
<div style='margin-top:30px'>{q}</div>
<p style='font-size:20px;color:{C['chu']};margin-top:10px'>Im 10 phút thì đi theo ★ (ghi "đi theo ★, chưa duyệt").</p></div>{foot('Chờ chốt')}""", "CHO-CHOT"))

if __name__ == "__main__":
    with sync_playwright() as p:
        b = p.chromium.launch(channel="msedge"); pg = b.new_page(viewport={"width": 1920, "height": 1080})
        for html, name in pages:
            f = ROOT / f"_{name}.html"; f.write_text(html, encoding="utf-8")
            pg.goto(f.as_uri()); pg.wait_for_timeout(400)
            sub = "" if name == "CHO-CHOT" else ("04-tinh-than/" if name.startswith("G4") else "05-pattern/")
            out = ROOT / f"{sub}{name}.png"; out.parent.mkdir(exist_ok=True); pg.screenshot(path=str(out)); print(out)
        b.close()
