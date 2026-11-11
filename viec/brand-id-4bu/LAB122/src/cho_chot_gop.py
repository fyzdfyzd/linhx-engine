# Trang chờ chốt gộp Sakédemy + TUVA (11/11/2026). Chạy: python -I cho_chot_gop.py
import pathlib
from playwright.sync_api import sync_playwright
OUT = pathlib.Path(r"D:\LINHX\LAB\LAB122-BRAND-ID-4BU\output")
FONT = pathlib.Path(r"D:\LINHX\LAB\LAB043-DESIGN-ONBRAND\nguon-logo-linh-19-10\if agent\Fonts\Montserrat-VariableFont_wght.ttf").as_uri()
Q = [("S3", "#1CA571", "Sakédemy · câu định vị", ["A · Không gian học tập văn hoá sáng tạo, nơi mỗi người thể hiện bản thân một cách chân thực.", "B · Đào tạo sáng tạo: giữ authentic và mindset.", "C · Văn hoá sáng tạo là gân chính; AI trong sáng tạo là gân phụ."], "A", "Chữ của hồ sơ; \"chân thực\" là authentic. AI ở nhánh phụ."),
     ("S5", "#1CA571", "Sakédemy · pattern vòng 2 (từ Gân lá)", ["A1 Lưới gân · A2 Gân chính – gân phụ · A3 Gân trong lá"], "A2", "Kể đúng kiến trúc: văn hoá sáng tạo là chính, AI là nhánh."),
     ("T2", "#FAA71B", "TUVA · vế công nghệ Decent AI cho giá trị cốt lõi", ["A · Tự do — Bình đẳng — Bao dung — AI tử tế", "B · Tự do (dữ liệu mở) · Bình đẳng (AI cho mọi tổ chức) · Bao dung (AI có trách nhiệm)", "C · Giữ bộ ba + Cam kết Decent AI: AI tử tế, minh bạch, có trách nhiệm"], "C", "Giữ nhịp ba giá trị gốc; công nghệ thành lời hứa."),
     ("T3", "#FAA71B", "TUVA · câu tiếng Việt đi cùng REACHING OUT", ["A · Vác tù và hàng tổng, bằng AI tử tế", "B · Ăn cơm nhà, vác tù và số", "C · Vươn tới cộng đồng, bằng dữ liệu và AI tử tế"], "A", "Giữ tinh thần câu gốc, thêm nghĩa công nghệ."),
     ("T5", "#FAA71B", "TUVA · pattern vòng 2 (từ Sóng xoắn)", ["B1 Sóng hàng · B2 Sóng dữ liệu · B3 Sóng lớn"], "B2", "Sóng chấm như tín hiệu số: cộng đồng × công nghệ.")]
rows = "".join(f"""<div style='display:flex;gap:28px;padding:18px 0;border-top:1px solid #0002'>
<div style='width:84px;font-size:34px;font-weight:800;color:{c}'>{k}</div>
<div style='flex:1'><div style='font-size:24px;font-weight:700'>{t}</div><div style='font-size:19px;line-height:1.5;margin-top:4px'>{'<br>'.join(o)}</div></div>
<div style='width:430px'><div style='font-size:28px;font-weight:800'>★ {s}</div><div style='font-size:17px;color:#555;margin-top:4px'>{l}</div></div></div>""" for k, c, t, o, s, l in Q)
html = f"""<!doctype html><html><head><meta charset='utf-8'><style>@font-face{{font-family:M;src:url('{FONT}');font-weight:100 900}}
*{{margin:0;padding:0;box-sizing:border-box}}body{{width:1920px;height:1080px;font-family:M;background:#F7F5F1;color:#1d1d1d;position:relative}}</style></head><body>
<div style='position:absolute;inset:56px 110px'>
<div style='font-size:20px;letter-spacing:.18em;font-weight:600;color:#777'>ĐIỂM CHỜ CHỐT GỘP · SAKÉDEMY + TUVA COMMUNICATION · 11/11/2026</div>
<div style='font-size:46px;font-weight:800;margin:10px 0 18px'>Linh trả lời kiểu: S3A S5A2 T2C T3A T5B2</div>{rows}
<p style='font-size:17px;color:#666;margin-top:14px'>Đã chốt: Unikon 1B, tagline "Agentic content at mass scale", vòng 2 A1 · Sakédemy tầm nhìn A (2 nhóm), giá trị A, Gân lá · TUVA định vị A, Sóng xoắn. Các câu T2, T3 là đề xuất mới, không phải lời nguồn.</p></div></body></html>"""
if __name__ == "__main__":
    OUT.mkdir(exist_ok=True); f = OUT / "_CHO-CHOT-GOP.html"; f.write_text(html, encoding="utf-8")
    with sync_playwright() as p:
        b = p.chromium.launch(channel="msedge"); pg = b.new_page(viewport={"width": 1920, "height": 1080})
        pg.goto(f.as_uri()); pg.wait_for_timeout(400); pg.screenshot(path=str(OUT / "CHO-CHOT-GOP.png")); b.close()
    print(OUT / "CHO-CHOT-GOP.png")
