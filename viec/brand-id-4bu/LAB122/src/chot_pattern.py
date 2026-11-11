# Bảng pattern ĐÃ CHỐT 11/11/2026 cho 4 BU: 3 nền + bài 1:1 + bìa 16:9 (cungai: 3 nền). Chạy: python -I chot_pattern.py
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from playwright.sync_api import sync_playwright
import unikon_g5v2 as U, sakedemy_g5v2 as S, tuva_g5v2 as T, cungai_g45 as G
L = pathlib.Path(r"D:\LINHX\LAB\LAB122-BRAND-ID-4BU")
def board(css, kick, title, tiles, foot):
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{css}</style></head><body><div class='pad' style='inset:72px 100px'>"
            f"<div class='kick'>{kick}</div><h1 style='font-size:52px'>{title}</h1>"
            f"<div style='display:flex;flex-wrap:wrap;gap:24px;margin-top:28px'>{tiles}</div></div>"
            f"<div class='foot' style='left:100px;right:100px'><span>{foot}</span><span>Linh chốt 11/11/2026</span></div></body></html>")
def t3(m, k, names):
    return "".join(f"<div style='display:flex;flex-direction:column;gap:8px'><div style='width:500px;height:375px;border-radius:14px;overflow:hidden;box-shadow:0 0 0 1px #0001'>{m.opt(k,1600,1200,n)}</div><span style='font-size:18px'>{lab}</span></div>" for n, lab in names)
def pub(m, k):
    return f"<div style='transform:scale(1.3);transform-origin:top left;width:294px;height:294px'>{m.post(k)}</div><div style='transform:scale(1.3);transform-origin:top left;width:523px;height:294px'>{m.cover(k)}</div>"
jobs = [
 ("UNIKON", U.CSS, "Pattern đã chốt · A3 Vành lớn", "Unikon · Vành lớn", t3(U, "A3", [("kem","Nền kem"),("mau","Nền gradient"),("toi","Nền đêm tím")]) + pub(U, "A3"), "Unikon · một vành lớn cắt góc, lưới vành nhỏ mờ dần"),
 ("SAKEDEMY", S.CSS, "Pattern đã chốt · A2 Gân chính – gân phụ", "Sakédemy · Gân lá (signature)", t3(S, "A2", [("kem","Nền kem"),("mau","Nền gradient lá"),("toi","Nền rêu đậm")]) + pub(S, "A2"), "Sakédemy · gân chính văn hoá sáng tạo, gân phụ AI"),
 ("TUVA", T.CSS, "Pattern đã chốt · B2 Sóng dữ liệu, một bên", "TUVA Communication · Sóng", t3(T, "B2", [("kem","Nền kem"),("mau","Nền cam"),("toi","Nền nâu đất")]) + pub(T, "B2"), "TUVA Communication · sóng chỉ ở một bên, nửa kia để trống"),
 ("CUNGAI", G.CSS, "Pattern đã chốt · A Dòng thoại", "cungai · Dòng thoại", "".join(f"<div style='display:flex;flex-direction:column;gap:8px'><div style='border-radius:14px;overflow:hidden;box-shadow:0 0 0 1px #0001;width:540px;height:304px'>{G.pat('A',540,304,n)}</div><span style='font-size:18px'>{lab}</span></div>" for n, lab in [("kem","Nền sáng"),("mau","Nền xanh"),("toi","Nền đêm")]), "cungai · vạch và chấm của bóng thoại"),
]
if __name__ == "__main__":
    with sync_playwright() as p:
        b = p.chromium.launch(channel="msedge"); pg = b.new_page(viewport={"width": 1920, "height": 1080})
        for bu, css, kick, title, tiles, foot in jobs:
            f = L / bu / "_PATTERN-CHOT.html"; f.write_text(board(css, kick, title, tiles, foot), encoding="utf-8")
            pg.goto(f.as_uri()); pg.wait_for_timeout(500)
            out = L / bu / "05-pattern" / "PATTERN-CHOT.png"; pg.screenshot(path=str(out)); print(out)
        b.close()
