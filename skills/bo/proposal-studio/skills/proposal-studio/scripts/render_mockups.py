#!/usr/bin/env python3
"""Render wireframe mockups (PNG) from mockups.json using Playwright/Chromium.

Usage: python render_mockups.py <project_dir> [--only id1,id2]
Reads  <project_dir>/mockups.json, writes <project_dir>/images/<id>.png
An image the user has already replaced (same stem, file marked in
<project_dir>/images/.locked or any non-.png extension newer than the png)
is NOT overwritten unless --force is given.
"""
import html, json, random, sys
from pathlib import Path

E = lambda s: html.escape(str(s or ""))
IMG_DIR = Path(".")
SIZES = {"showcase": (1920, 1080), "kiosk": (1080, 1920), "led": (1920, 1080), "tablet": (1600, 1000),
         "phone": (750, 1500), "diagram": (1920, 1080), "floorplan": (1920, 1200),
         "keyvisual": (1920, 1080)}


def css(t):
    return f"""
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;600;800;900&display=swap');
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Be Vietnam Pro',sans-serif;color:{t['text']};background:{t['bg']};overflow:hidden}}
.scr{{position:relative;width:100vw;height:100vh;overflow:hidden;
 background:radial-gradient(120% 80% at 50% 0%,{t['secondary']}33,transparent 60%),{t['bg']}}}
.top{{display:flex;justify-content:space-between;align-items:center;padding:36px 48px;font-weight:800;font-size:30px}}
.brand{{background:{t['primary']};color:#fff;padding:10px 26px;border-radius:40px}}
.pill{{background:{t['secondary']};color:{t['dark']};padding:22px 48px;border-radius:60px;font-weight:900;font-size:40px;display:inline-block}}
.h1{{font-weight:900;font-size:86px;line-height:1.05;color:{t['primary']}}}
.h2{{font-weight:800;font-size:52px;line-height:1.15}}
.sub{{font-size:34px;opacity:.8;line-height:1.35}}
.mascot{{border:3px solid {t['secondary']}aa;border-radius:48px;box-shadow:inset 0 0 80px {t['secondary']}55;display:flex;flex-direction:column;
 align-items:center;justify-content:center;background:{t['secondary']}22;color:{t['primary']};font-weight:800;text-align:center}}
.mascot .sil{{width:38%;aspect-ratio:1;border-radius:50%;background:{t['primary']}33;margin-bottom:4%}}
.mascot .body{{width:56%;height:22%;border-radius:40% 40% 12% 12%;background:{t['primary']}22;margin:-6% 0 5%}}
.card{{background:#fff;border-radius:36px;box-shadow:0 12px 40px #0002;padding:36px}}
.bubble{{padding:28px 36px;border-radius:36px;font-size:36px;line-height:1.35;max-width:82%}}
.ai{{background:#fff;box-shadow:0 8px 24px #0002;border-bottom-left-radius:8px}}
.me{{background:{t['primary']};color:#fff;margin-left:auto;border-bottom-right-radius:8px}}
.chip{{border:3px solid {t['primary']};color:{t['primary']};padding:16px 30px;border-radius:40px;font-size:30px;font-weight:700}}
.bar{{position:absolute;left:0;right:0;bottom:0;background:{t['dark']};color:#fff;padding:26px 48px;font-size:28px;display:flex;justify-content:space-between}}
.tag{{font-size:22px;letter-spacing:3px;text-transform:uppercase;font-weight:800;color:{t['primary']}}}
.qr{{display:grid;grid-template-columns:repeat(21,1fr);gap:0;width:300px;height:300px;background:#fff;padding:14px;border-radius:12px}}
.qr i{{background:{t['dark']}}}.qr b{{background:transparent}}
"""


MASCOT_URI = None  # data: URI of the client's official mascot file (mockups.json "mascot_image")


def mascot(w, h, label):
    if MASCOT_URI:
        return (f'<div style="width:{w};height:{h};display:flex;align-items:flex-end;justify-content:center">'
                f'<img src="{MASCOT_URI}" style="max-width:100%;max-height:100%;object-fit:contain;filter:drop-shadow(0 18px 30px #0004)"></div>')
    return (f'<div class="mascot" style="width:{w};height:{h}"><div class="sil"></div><div class="body"></div>'
            f'<div style="font-size:30px">{E(label)}</div><div style="font-size:22px;opacity:.7">vị trí đặt file mascot chính thức</div></div>')


def qr(seed):
    r = random.Random(seed)
    cells = []
    for y in range(21):
        for x in range(21):
            finder = any(x0 <= x < x0 + 7 and y0 <= y < y0 + 7 for x0, y0 in ((0, 0), (14, 0), (0, 14)))
            if finder:
                fx, fy = x % 7 if x < 7 else (x - 14) % 7, y % 7 if y < 7 else (y - 14) % 7
                on = fx in (0, 6) or fy in (0, 6) or (2 <= fx <= 4 and 2 <= fy <= 4)
            else:
                on = r.random() < 0.5
            cells.append("<i></i>" if on else "<b></b>")
    return f'<div class="qr">{"".join(cells)}</div>'


def topbar(s, cfg):
    return f'<div class="top"><span class="brand">{E(cfg.get("brand_name"))}</span><span>{E(s.get("corner", ""))}</span></div>'


def footer(s):
    return f'<div class="bar"><span>{E(s.get("footer_left", ""))}</span><span>{E(s.get("footer_right", ""))}</span></div>' if s.get("footer_left") or s.get("footer_right") else ""


def L_attract(s, c):
    return f"""{topbar(s,c)}<div style="padding:20px 60px;text-align:center">
<div class="tag">{E(s.get('kicker'))}</div><div class="h1" style="margin:18px 0">{E(s.get('headline'))}</div>
<div class="sub">{E(s.get('sub'))}</div></div>
<div style="display:flex;justify-content:center;margin-top:30px">{mascot('78%','860px',c['mascot_label'])}</div>
<div style="text-align:center;margin-top:50px"><span class="pill">{E(s.get('cta'))}</span></div>{footer(s)}"""


def L_chat(s, c):
    msgs = "".join(f'<div class="bubble {"me" if m.get("who")=="guest" else "ai"}" style="margin-bottom:24px">{E(m.get("text"))}</div>'
                   for m in s.get("messages", []))
    chips = "".join(f'<span class="chip">{E(x)}</span>' for x in s.get("chips", []))
    return f"""{topbar(s,c)}<div style="display:flex;justify-content:center">{mascot('70%','720px',c['mascot_label'])}</div>
<div style="padding:40px 60px">{msgs}</div><div style="display:flex;flex-wrap:wrap;gap:18px;padding:0 60px">{chips}</div>
<div style="position:absolute;bottom:130px;left:0;right:0;text-align:center;font-size:30px;font-weight:700;color:{c['theme']['primary']}">
● {E(s.get('mic', 'Đang nghe…'))}</div>{footer(s)}"""


def L_menu(s, c):
    opts = "".join(f'<div class="card" style="text-align:center"><div style="font-size:90px;font-weight:900;color:{c["theme"]["primary"]}">{E(o.get("icon"))}</div>'
                   f'<div class="h2" style="font-size:44px;margin-top:12px">{E(o.get("label"))}</div><div class="sub" style="font-size:28px;margin-top:8px">{E(o.get("sub"))}</div></div>'
                   for o in s.get("options", []))
    return f"""{topbar(s,c)}<div style="display:flex;gap:30px;align-items:center;padding:10px 60px">{mascot('300px','360px','Mascot')}
<div><div class="tag">{E(s.get('kicker'))}</div><div class="h2" style="margin-top:12px">{E(s.get('headline'))}</div></div></div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:36px;padding:50px 60px">{opts}</div>{footer(s)}"""


def L_game(s, c):
    t = c["theme"]
    dots = "".join(f'<div style="position:absolute;left:{x}%;top:{y}%;width:28px;height:28px;border-radius:50%;background:{t["secondary"]};box-shadow:0 0 18px {t["secondary"]}"></div>'
                   for x, y in [(50, 18), (50, 30), (38, 32), (62, 32), (30, 45), (70, 22), (50, 50), (42, 70), (58, 70), (40, 88), (60, 88)])
    return f"""{topbar(s,c)}<div style="display:flex;justify-content:space-around;font-weight:900;font-size:56px;color:{t['primary']}">
<span>⏱ {E(s.get('timer'))}</span><span>★ {E(s.get('score'))}</span><span>{E(s.get('combo'))}</span></div>
<div style="position:relative;margin:30px 60px;height:1180px;border-radius:40px;background:#1b1b1b;overflow:hidden">
<div style="position:absolute;inset:0;background:linear-gradient(180deg,#333,#111)"></div>{dots}
<div style="position:absolute;right:30px;top:30px">{mascot('280px','360px','Mascot mẫu')}</div>
<div style="position:absolute;left:30px;bottom:30px;color:#fff;font-size:26px;opacity:.7">Camera · nhận dạng khung xương trên thiết bị</div></div>
<div style="text-align:center"><span class="pill">{E(s.get('prompt'))}</span></div>{footer(s)}"""


def L_quiz(s, c):
    ans = "".join(f'<div class="card" style="font-size:40px;font-weight:700;margin-bottom:28px;{"outline:8px solid "+c["theme"]["secondary"] if i==s.get("correct") else ""}">{chr(65+i)}. {E(a)}</div>'
                  for i, a in enumerate(s.get("answers", [])))
    return f"""{topbar(s,c)}<div style="display:flex;justify-content:center">{mascot('60%','620px',c['mascot_label'])}</div>
<div style="padding:40px 60px"><div class="tag">{E(s.get('kicker'))}</div><div class="h2" style="margin:16px 0 40px">{E(s.get('question'))}</div>{ans}</div>{footer(s)}"""


def L_photo(s, c):
    t = c["theme"]
    return f"""{topbar(s,c)}<div style="position:relative;margin:10px 60px;height:1360px;border-radius:40px;overflow:hidden;
background:linear-gradient(160deg,#666,#222);border:24px solid {t['primary']}">
<div style="position:absolute;left:8%;bottom:0;width:26%;height:55%;border-radius:45% 45% 0 0;background:#999"></div>
<div style="position:absolute;left:37%;bottom:0;width:26%;height:65%;border-radius:45% 45% 0 0;background:#aaa"></div>
<div style="position:absolute;right:4%;bottom:0">{mascot('300px','520px','Mascot (asset)')}</div>
<div style="position:absolute;top:0;left:0;right:0;background:{t['secondary']};color:{t['dark']};text-align:center;font-weight:900;font-size:48px;padding:18px">{E(s.get('frame_title'))}</div>
<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:260px;font-weight:900;color:#fff;text-shadow:0 8px 30px #000">{E(s.get('countdown'))}</div></div>
<div style="text-align:center;margin-top:40px" class="sub">{E(s.get('sub'))}</div>{footer(s)}"""


def L_reward(s, c):
    t = c["theme"]
    return f"""{topbar(s,c)}<div style="padding:10px 60px;text-align:center"><div class="tag">{E(s.get('kicker'))}</div>
<div class="h1" style="font-size:72px;margin:14px 0">{E(s.get('headline'))}</div></div>
<div class="card" style="margin:30px 60px;border:6px dashed {t['primary']};text-align:center">
<div style="font-size:120px;font-weight:900;color:{t['primary']}">{E(s.get('value'))}</div>
<div class="h2" style="font-size:40px">{E(s.get('voucher'))}</div>
<div style="display:flex;justify-content:center;margin:34px 0">{qr(s['id'])}</div>
<div class="sub" style="font-size:28px">{E(s.get('qr_note'))}</div></div>
<div style="margin:10px 60px;font-size:28px;line-height:1.5">☐ {E(s.get('consent'))}</div>
<div style="text-align:center;margin-top:30px"><span class="pill">{E(s.get('cta'))}</span></div>{footer(s)}"""


def L_leaderboard(s, c):
    t = c["theme"]
    rows = "".join(f'<div style="display:flex;justify-content:space-between;padding:22px 40px;margin-bottom:14px;border-radius:24px;font-size:42px;font-weight:800;'
                   f'background:{t["secondary"] if i==0 else "#ffffff"};color:{t["dark"]}"><span>#{i+1}  {E(r[0])}</span><span>{E(r[1])}</span></div>'
                   for i, r in enumerate(s.get("rows", [])))
    return f"""{topbar(s,c)}<div style="display:grid;grid-template-columns:1fr 1.3fr;gap:60px;padding:20px 80px;align-items:center">
{mascot('100%','760px',c['mascot_label'])}<div><div class="tag">{E(s.get('kicker'))}</div>
<div class="h1" style="font-size:80px;margin:14px 0 36px">{E(s.get('headline'))}</div>{rows}</div></div>{footer(s)}"""


def L_dashboard(s, c):
    t = c["theme"]
    tiles = "".join(f'<div class="card"><div class="sub" style="font-size:22px">{E(k)}</div><div style="font-size:54px;font-weight:900;color:{t["primary"]}">{E(v)}</div></div>'
                    for k, v in s.get("tiles", []))
    mx = max([v for _, v in s.get("bars", [])] or [1])
    bars = "".join(f'<div style="display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:100%">'
                   f'<div style="width:46px;height:{int(v/mx*100)}%;background:{t["primary"]};border-radius:8px 8px 0 0"></div><div style="font-size:18px;margin-top:6px">{E(k)}</div></div>'
                   for k, v in s.get("bars", []))
    rows = "".join(f'<div style="display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px solid #0001;font-size:22px"><span>{E(a)}</span><b>{E(b)}</b></div>'
                   for a, b in s.get("list", []))
    return f"""<div class="top" style="padding:28px 40px"><span class="brand">{E(s.get('title'))}</span><span style="font-size:22px">{E(s.get('corner'))}</span></div>
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:24px;padding:0 40px">{tiles}</div>
<div style="display:grid;grid-template-columns:1.6fr 1fr;gap:24px;padding:24px 40px">
<div class="card" style="height:560px"><div class="tag">{E(s.get('chart_title'))} · dữ liệu minh hoạ</div><div style="display:flex;gap:10px;height:440px;margin-top:20px">{bars}</div></div>
<div class="card" style="height:560px"><div class="tag">{E(s.get('list_title'))}</div><div style="margin-top:14px">{rows}</div></div></div>"""


def L_control(s, c):
    t = c["theme"]
    groups = "".join(f'<div class="card"><div class="tag">{E(g.get("title"))}</div><div style="display:flex;flex-wrap:wrap;gap:14px;margin-top:18px">'
                     + "".join(f'<span class="chip" style="font-size:24px">{E(b)}</span>' for b in g.get("buttons", [])) + "</div></div>"
                     for g in s.get("groups", []))
    return f"""<div class="top" style="padding:28px 40px"><span class="brand">{E(s.get('title'))}</span><span style="font-size:22px;color:{t['primary']}">● {E(s.get('corner'))}</span></div>
<div style="display:grid;grid-template-columns:420px 1fr;gap:28px;padding:0 40px">
<div>{mascot('100%','640px','Xem trước kiosk')}</div><div style="display:grid;grid-template-columns:1fr 1fr;gap:24px">{groups}</div></div>"""


def L_diagram(s, c):
    t = c["theme"]
    cols = s.get("columns", [])
    parts = []
    for i, col in enumerate(cols):
        nodes = "".join(f'<div class="card" style="padding:30px 30px;margin-bottom:24px;border-left:10px solid {t["primary"] if i%2==0 else t["secondary"]}">'
                        f'<div style="font-weight:800;font-size:34px">{E(n.get("title"))}</div><div style="font-size:25px;opacity:.75;margin-top:6px">{E(n.get("text"))}</div></div>'
                        for n in col.get("nodes", []))
        parts.append(f'<div style="flex:1"><div class="tag" style="margin-bottom:18px">{E(col.get("title"))}</div>{nodes}</div>')
        if i < len(cols) - 1:
            parts.append(f'<div style="display:flex;align-items:center;font-size:70px;color:{t["primary"]};font-weight:900">→</div>')
    return f"""<div style="padding:44px 60px 10px"><div class="tag">{E(s.get('kicker'))}</div><div class="h2" style="margin-top:8px">{E(s.get('title'))}</div></div>
<div style="display:flex;gap:26px;padding:26px 60px">{''.join(parts)}</div>
<div style="position:absolute;bottom:30px;left:60px;right:60px;font-size:22px;opacity:.7">{E(s.get('note'))}</div>"""


def L_floorplan(s, c):
    t = c["theme"]
    zones = "".join(f'<div style="position:absolute;left:{z["x"]}%;top:{z["y"]}%;width:{z["w"]}%;height:{z["h"]}%;border-radius:18px;'
                    f'background:{z.get("color", t["secondary"])}{"cc" if z.get("strong") else "55"};border:4px solid {t["primary"]};padding:18px">'
                    f'<div style="font-weight:900;font-size:36px">{E(z.get("label"))}</div><div style="font-size:26px;margin-top:4px">{E(z.get("text"))}</div></div>'
                    for z in s.get("zones", []))
    return f"""<div style="padding:36px 60px 0;display:flex;justify-content:space-between;align-items:end">
<div><div class="tag">{E(s.get('kicker'))}</div><div class="h2" style="margin-top:8px">{E(s.get('title'))}</div></div><div class="sub" style="font-size:24px">{E(s.get('dims'))}</div></div>
<div style="position:relative;margin:24px 60px;height:900px;border:6px solid {t['dark']};border-radius:10px;
background-image:linear-gradient(#0001 1px,transparent 1px),linear-gradient(90deg,#0001 1px,transparent 1px);background-size:60px 60px">{zones}</div>"""


def L_keyvisual(s, c):
    """Placeholder for an AI-generated image: no headline (the deck adds text),
    mascot box centred-right so cover/cropping still looks intentional."""
    t = c["theme"]
    return f"""<div style="position:absolute;inset:0;background:linear-gradient(135deg,{t['primary']},{t['dark']})"></div>
<div style="position:absolute;inset:0;background:radial-gradient(55% 60% at 62% 55%,{t['secondary']}88,transparent)"></div>
<div style="position:absolute;left:50%;top:50%;transform:translate(-40%,-50%)">{mascot('560px','760px',s.get('label') or c['mascot_label'])}</div>
<div style="position:absolute;left:50%;bottom:40px;transform:translateX(-40%);border:3px dashed #fff9;color:#fff;padding:14px 26px;border-radius:14px;font-size:26px;white-space:nowrap">
Ảnh tạm · tạo ảnh thật theo prompt {E(s.get('prompt_ref'))} rồi lưu đè cùng tên</div>"""


def _uri(stem):
    """data: URI for images/<stem>.* (newest file wins)."""
    import base64, mimetypes
    c = [p for p in IMG_DIR.glob(f"{stem}.*") if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")]
    if not c:
        return ""
    p = max(c, key=lambda x: x.stat().st_mtime)
    return f"data:{mimetypes.guess_type(str(p))[0] or 'image/png'};base64," + base64.b64encode(p.read_bytes()).decode()


def L_showcase(s, c):
    """Presentation mockup: real UI screens inside device frames over an on-brand photo."""
    t = c["theme"]
    devs = []
    for it in s.get("items", []):
        u = _uri(it["image"])
        d = it.get("device", "kiosk")
        if d == "kiosk":
            devs.append(f'''<div style="display:flex;flex-direction:column;align-items:center">
<div style="width:{it.get('w',380)}px;aspect-ratio:9/16;background:#111;border-radius:28px;padding:14px;box-shadow:0 40px 80px #0008,0 0 0 6px #fff">
<img src="{u}" style="width:100%;height:100%;object-fit:cover;border-radius:16px"></div>
<div style="width:{int(it.get('w',380)*0.55)}px;height:70px;background:linear-gradient(#fff,#e9e9e9);border-radius:0 0 18px 18px;box-shadow:0 20px 40px #0006"></div>
<div style="width:{int(it.get('w',380)*0.9)}px;height:22px;background:{t['primary']};border-radius:12px;margin-top:-4px"></div>
<div style="color:#fff;font-weight:800;font-size:24px;margin-top:18px;text-shadow:0 2px 8px #000">{E(it.get('label'))}</div></div>''')
        elif d == "tablet":
            devs.append(f'''<div style="display:flex;flex-direction:column;align-items:center"><div style="width:{it.get('w',640)}px;aspect-ratio:16/10;background:#111;border-radius:30px;padding:18px;box-shadow:0 40px 80px #0008">
<img src="{u}" style="width:100%;height:100%;object-fit:cover;border-radius:12px"></div>
<div style="color:#fff;font-weight:800;font-size:24px;margin-top:18px;text-shadow:0 2px 8px #000">{E(it.get('label'))}</div></div>''')
        else:
            devs.append(f'''<div style="display:flex;flex-direction:column;align-items:center"><div style="width:{it.get('w',820)}px;aspect-ratio:16/9;background:#050505;padding:10px;border-radius:6px;box-shadow:0 0 60px {t['secondary']}88,0 40px 80px #0008">
<img src="{u}" style="width:100%;height:100%;object-fit:cover"></div>
<div style="color:#fff;font-weight:800;font-size:24px;margin-top:18px;text-shadow:0 2px 8px #000">{E(it.get('label'))}</div></div>''')
    return f"""<div style="position:absolute;inset:-30px;background:url('{_uri(s['bg'])}') center/cover;filter:blur({s.get('blur',6)}px) brightness(.75)"></div>
<div style="position:absolute;inset:0;background:linear-gradient(180deg,{t['dark']}cc,transparent 35%,transparent 70%,{t['dark']}dd)"></div>
<div style="position:absolute;top:44px;left:70px;color:#fff"><div class="tag" style="color:{t['secondary']}">{E(s.get('kicker'))}</div>
<div style="font-weight:900;font-size:56px;margin-top:6px;text-shadow:0 4px 16px #0008">{E(s.get('title'))}</div></div>
<div style="position:absolute;left:0;right:0;bottom:{s.get('bottom',40)}px;display:flex;justify-content:center;align-items:flex-end;gap:{s.get('gap',60)}px">{''.join(devs)}</div>"""


LAYOUTS = {k[2:]: v for k, v in globals().items() if k.startswith("L_")}


def page(s, cfg):
    return f"<html><head><meta charset=utf-8><style>{css(cfg['theme'])}</style></head><body><div class='scr'>{LAYOUTS[s['layout']](s, cfg)}</div></body></html>"


def locked(img_dir, sid):
    lock = img_dir / ".locked"
    if lock.exists() and sid in lock.read_text(encoding="utf-8").split():
        return True
    png = img_dir / f"{sid}.png"
    others = [p for p in img_dir.glob(f"{sid}.*") if p.suffix.lower() != ".png"]
    return bool(png.exists() and others and max(p.stat().st_mtime for p in others) > png.stat().st_mtime)


def main():
    proj = Path(sys.argv[1]).resolve()
    only = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--only=")), None)
    force = "--force" in sys.argv
    cfg = json.loads((proj / "mockups.json").read_text(encoding="utf-8"))
    cfg.setdefault("mascot_label", "MASCOT")
    global MASCOT_URI
    mimg = cfg.get("mascot_image")
    if mimg and (proj / mimg).exists():
        import base64, mimetypes
        mt = mimetypes.guess_type(str(proj / mimg))[0] or "image/png"
        MASCOT_URI = f"data:{mt};base64," + base64.b64encode((proj / mimg).read_bytes()).decode()
        print("dùng mascot:", mimg)
    img_dir = proj / "images"
    global IMG_DIR
    IMG_DIR = img_dir
    img_dir.mkdir(exist_ok=True)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        for s in cfg["screens"]:
            if only and s["id"] not in only:
                continue
            if not force and locked(img_dir, s["id"]):
                print("skip (ảnh đã được thay):", s["id"]); continue
            w, h = s.get("size") or SIZES[s.get("device", "kiosk")]
            pg = b.new_page(viewport={"width": w, "height": h})
            pg.set_content(page(s, cfg), wait_until="networkidle")
            pg.wait_for_timeout(300)
            pg.screenshot(path=str(img_dir / f"{s['id']}.png"))
            pg.close()
            print("ok", s["id"])
        b.close()


if __name__ == "__main__":
    main()
