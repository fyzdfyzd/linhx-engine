#!/usr/bin/env python3
"""thiet_ke.py: dựng ấn phẩm đúng ngôn ngữ thiết kế của brand từ khuôn HTML, xuất PNG.

Lệnh:
  token  <brand-dir>                                   sinh <brand-dir>/09-khuon/token.css từ brand.json (màu, font, hoạ tiết)
  dung   <brand-dir> <khuon.html> <noi-dung.json> --ra <out.png> [--co 1080x1080]
                                                       điền nội dung vào khuôn, render PNG (kèm file .html cạnh PNG)
  ds     <brand-dir>                                   liệt kê khuôn và các ô {{...}} cần điền

Render bằng Chrome/Edge/Chromium headless (Windows tự tìm msedge.exe hoặc chrome.exe).
Khuôn là HTML thường, dùng biến CSS trong token.css và ô {{ten_o}}. Ô có tiền tố "anh_" nhận đường dẫn ảnh.
"""
import argparse, html, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

def slug(s):
    s = re.sub(r"\(render\)", "", s).strip().lower()
    for a, b in (("đ", "d"),):
        s = s.replace(a, b)
    import unicodedata
    s = unicodedata.normalize("NFD", s); s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

def lenh_token(a):
    d = Path(a.brand_dir); b = json.loads((d / "brand.json").read_text("utf8"))
    out = ["/* sinh tự động từ brand.json bởi thiet_ke.py token; đừng sửa tay */", ":root {"]
    for nhom in ("chinh", "phu", "nhan"):
        for c in b["mau"].get(nhom, []):
            out.append(f"  --{slug(c['ten'])}: {c['hex']};")
    out.append("}")
    # font: mọi file .ttf/.otf trong 03-chu
    for f in sorted((d / "03-chu").glob("*.[to]tf")):
        ten = f.stem; nang = {"thin": 100, "extralight": 200, "light": 300, "regular": 400, "medium": 500,
                             "semibold": 600, "bold": 700, "extrabold": 800, "black": 900}
        m = re.search(r"[-_ ]?(Thin|ExtraLight|Light|Regular|Medium|SemiBold|ExtraBold|Bold|Black)(Italic)?$", ten, flags=re.I)
        ho = ten[:m.start()] if m else ten
        w = nang[m.group(1).lower()] if m else 400
        out.append(f"@font-face {{ font-family: '{ho}'; src: url('../03-chu/{f.name}'); font-weight: {w}; }}")
    hoa = sorted((d / "05-icon").glob("hoa-tiet*.svg"))
    if hoa:
        out.append(":root {")
        for f in hoa:
            out.append(f"  --{slug(f.stem)}: url('../05-icon/{f.name}');")
        out.append("}")
    (d / "09-khuon").mkdir(exist_ok=True)
    p = d / "09-khuon" / "token.css"; p.write_text("\n".join(out) + "\n", encoding="utf8"); print(p)

def tim_trinh_duyet():
    for c in (os.environ.get("ONBRAND_BROWSER"), "/opt/pw-browsers/chromium", "chromium", "chromium-browser", "google-chrome",
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Google\Chrome\Application\chrome.exe"):
        if c and (Path(c).exists() or shutil.which(c)):
            return shutil.which(c) or c
    sys.exit("Không tìm thấy Chrome/Edge/Chromium. Đặt biến ONBRAND_BROWSER trỏ tới file chạy.")

def render(html_path, png, w, h):
    br = tim_trinh_duyet()
    cmd = [br, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
           "--force-device-scale-factor=1", f"--window-size={w},{h + 240}", f"--screenshot={Path(png).resolve()}",
           "--virtual-time-budget=3000", Path(html_path).resolve().as_uri()]
    subprocess.run(cmd, capture_output=True, timeout=120)
    if not Path(png).exists():
        sys.exit("Render thất bại: " + " ".join(cmd))
    # cửa sổ headless hụt chiều cao vài chục px tuỳ máy: render dư rồi cắt đúng khổ
    from PIL import Image
    im = Image.open(png); im.crop((0, 0, w, h)).save(png)

def lenh_dung(a):
    d = Path(a.brand_dir).resolve(); khuon = Path(a.khuon)
    if not khuon.is_absolute() and not khuon.exists():
        khuon = d / "09-khuon" / khuon
    tpl = khuon.read_text("utf8"); nd = json.loads(Path(a.noi_dung).read_text("utf8"))
    m = re.search(r'data-co="(\d+)x(\d+)"', tpl)
    w, h = map(int, (a.co or (m and f"{m.group(1)}x{m.group(2)}") or "1080x1080").split("x"))
    def thay(mo):
        k = mo.group(1); v = nd.get(k, "")
        if k.startswith("anh_") and v:
            p = Path(v); p = p if p.is_absolute() else (d / v)
            return p.resolve().as_uri()
        return html.escape(str(v)).replace("\n", "<br>")
    thieu = sorted({k for k in re.findall(r"\{\{(\w+)\}\}", tpl) if k not in nd})
    out_html = Path(a.ra).with_suffix(".html")
    s = re.sub(r"\{\{(\w+)\}\}", thay, tpl)
    # đường dẫn "../" trong khuôn tính từ 09-khuon: đổi thành đường dẫn tuyệt đối; token.css chép cạnh file ra
    s = re.sub(r'(src|href)="\.\./', lambda mo: f'{mo.group(1)}="{d.as_uri()}/', s)
    s = s.replace("url('../", f"url('{d.as_uri()}/")
    out_html.parent.mkdir(parents=True, exist_ok=True); out_html.write_text(s, encoding="utf8")
    css = (d / "09-khuon" / "token.css").read_text("utf8").replace("url('../", f"url('{d.as_uri()}/")
    (out_html.parent / "token.css").write_text(css, encoding="utf8")
    render(out_html, a.ra, w, h)
    # bản mặt nạ: vùng ảnh chụp (.anh hoặc [data-anh]) tô hồng #FF00FF để onbrand.py cham bỏ qua khi đo màu
    mask_html = out_html.with_name(out_html.stem + ".mask.html")
    mask_html.write_text(s.replace("</head>", "<style>.anh,[data-anh]{background:#FF00FF!important}.anh::after,.anh::before,[data-anh]::after{display:none!important}</style></head>"), encoding="utf8")
    render(mask_html, str(Path(a.ra).with_suffix(".mask.png")), w, h); mask_html.unlink()
    print(json.dumps({"png": a.ra, "html": str(out_html), "co": f"{w}x{h}", "o_thieu": thieu}, ensure_ascii=False))

def lenh_ds(a):
    d = Path(a.brand_dir) / "09-khuon"
    for f in sorted(d.glob("*.html")):
        t = f.read_text("utf8"); m = re.search(r'data-co="(\d+x\d+)"', t); mo = re.search(r"<!--\s*(.*?)\s*-->", t, re.S)
        o = ", ".join(dict.fromkeys(re.findall(r"\{\{(\w+)\}\}", t)))
        print(f"{f.name}  [{m.group(1) if m else '?'}]  ô: {o}")
        if mo: print("   " + mo.group(1).splitlines()[0])

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="lenh", required=True)
    t = s.add_parser("token"); t.add_argument("brand_dir"); t.set_defaults(f=lenh_token)
    u = s.add_parser("dung"); u.add_argument("brand_dir"); u.add_argument("khuon"); u.add_argument("noi_dung"); u.add_argument("--ra", required=True); u.add_argument("--co"); u.set_defaults(f=lenh_dung)
    l = s.add_parser("ds"); l.add_argument("brand_dir"); l.set_defaults(f=lenh_ds)
    a = p.parse_args(); a.f(a)

if __name__ == "__main__":
    main()
