#!/usr/bin/env python3
"""Sinh trang con từ nguon/*.json dùng chung đầu/chân với trang chủ. Chạy: python3 tao-trang.py"""
import json, html, pathlib, re
GOC = pathlib.Path(__file__).parent
PUB = GOC / "public"
SITE = "https://sakedemy.com"

DAU = """<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="{ogtype}">
<meta property="og:image" content="{site}/img/og.png">
<meta name="theme-color" content="#02403B">
<link rel="canonical" href="{site}{path}">{robots}
<link rel="icon" href="/img/icon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/site.css?v=1">
<script type="application/ld+json">{ld}</script>
</head>
<body>
<a class="skip" href="#noi-dung">Bỏ qua, tới nội dung</a>
<header class="top">
  <div class="wrap nav">
    <a href="/" class="logo" aria-label="Sakédemy, trang chủ"><img src="/img/logo.svg" alt="Sakédemy" width="124" height="56"></a>
    <nav aria-label="Mục chính">
      <a href="/chuong-trinh/">Chương trình</a>
      <a href="/lop-doanh-nghiep/">Lớp doanh nghiệp</a>
      <a href="/giang-vien/">Giảng viên</a>
      <a href="/khoa-ca-nhan/">Học cá nhân</a>
      <a href="/cam-nang/">Cẩm nang</a>
    </nav>
    <a class="btn btn-main nav-cta" href="/?kenh={kenh}#dang-ky">Đăng ký tư vấn</a>
  </div>
</header>
<main id="noi-dung">
"""
CHAN = """</main>
<footer class="foot">
  <div class="wrap">
    <div class="foot-cot">
      <div><img src="/img/logo.svg" alt="Sakédemy" width="124" height="56"><p>Khi sáng tạo gặp công nghệ.</p><p data-cfg="lien_he_chan">Liên hệ trực tiếp đang cập nhật. Để lại thông tin ở form, chúng tôi liên hệ.</p></div>
      <nav aria-label="Chương trình"><b>Chương trình</b><a href="/chuong-trinh/marketing-truyen-thong/">Marketing, truyền thông</a><a href="/chuong-trinh/kinh-doanh-cham-soc-khach/">Kinh doanh, CSKH</a><a href="/chuong-trinh/van-hanh-hanh-chinh/">Vận hành, hành chính</a><a href="/chuong-trinh/ban-lanh-dao/">Ban lãnh đạo</a><a href="/chuong-trinh/chi-nhanh-ngan-hang/">Chi nhánh ngân hàng</a></nav>
      <nav aria-label="Học"><b>Học</b><a href="/lop-doanh-nghiep/">Lớp doanh nghiệp</a><a href="/hoc-thu/">Bài học thử</a><a href="/khoa-ca-nhan/">Khoá cá nhân</a><a href="/khoa-ai-ung-dung-uy-tin/">Chọn khoá AI ứng dụng</a><a href="/cam-nang/">Cẩm nang</a></nav>
      <nav aria-label="Sakédemy"><b>Sakédemy</b><a href="/gioi-thieu/">Giới thiệu</a><a href="/giang-vien/">Giảng viên</a><a href="/hoi-dap/">Hỏi đáp</a><a href="/lien-he/">Liên hệ</a><a href="/chinh-sach-du-lieu/">Chính sách dữ liệu</a></nav>
    </div>
    <div class="foot-in"><p data-cfg="phap_nhan">© 2026 Sakédemy</p><p class="web">SAKEDEMY.COM</p></div>
  </div>
</footer>
<script src="/app.js?v=1" defer></script>
</body>
</html>
"""

def md_inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', t)
    return t

def md(txt):
    """Markdown tối giản: ## h2, ### h3, -, 1., bảng |, đoạn."""
    out, lines, i = [], txt.strip().split("\n"), 0
    while i < len(lines):
        l = lines[i].rstrip()
        if not l: i += 1; continue
        if l.startswith("### "): out.append(f"<h3>{md_inline(l[4:])}</h3>"); i += 1; continue
        if l.startswith("## "):
            t = l[3:]; sid = re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")[:40]
            out.append(f'<h2 id="{sid}">{md_inline(t)}</h2>'); i += 1; continue
        if l.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                if not re.match(r"^\|[\s:|-]+\|$", lines[i]): rows.append([c.strip() for c in lines[i].strip("|").split("|")])
                i += 1
            h = "".join(f"<th>{md_inline(c)}</th>" for c in rows[0])
            b = "".join("<tr>" + "".join(f"<td>{md_inline(c)}</td>" for c in r) + "</tr>" for r in rows[1:])
            out.append(f'<div class="bang"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'); continue
        if re.match(r"^(-|\d+\.) ", l):
            ol = l[0].isdigit(); items = []
            while i < len(lines) and re.match(r"^(-|\d+\.) ", lines[i]):
                items.append(re.sub(r"^(-|\d+\.) ", "", lines[i])); i += 1
            tag = "ol" if ol else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{md_inline(x)}</li>" for x in items) + f"</{tag}>"); continue
        para = [l]; i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#|\||-|\d+\.)", lines[i]): para.append(lines[i]); i += 1
        out.append(f"<p>{md_inline(' '.join(para))}</p>")
    return "\n".join(out)

def ld_cho(t):
    g = [{"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate([("Trang chủ", "/")] + t.get("vet", []))]}]
    if t.get("loai") == "service":
        g.append({"@type": "Service", "name": t["h1"], "serviceType": "Đào tạo AI ứng dụng cho doanh nghiệp", "areaServed": "VN", "description": t["desc"], "provider": {"@type": "Organization", "name": "Sakédemy", "url": SITE + "/"}})
    if t.get("loai") == "article":
        g.append({"@type": "Article", "headline": t["h1"], "description": t["desc"], "inLanguage": "vi", "author": {"@type": "Organization", "name": "Sakédemy"}, "publisher": {"@type": "Organization", "name": "Sakédemy", "logo": {"@type": "ImageObject", "url": SITE + "/img/logo.svg"}}, "datePublished": t.get("ngay", "2026-11-10"), "mainEntityOfPage": SITE + t["path"]})
    if t.get("hoi_dap"):
        g.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t["hoi_dap"]]})
    return json.dumps({"@context": "https://schema.org", "@graph": g}, ensure_ascii=False)

def idx_html():
    return (PUB / "index.html").read_text(encoding="utf-8")

def tao(t):
    kenh = t.get("kenh", "trang")
    s = DAU.format(title=html.escape(t["title"]), desc=html.escape(t["desc"]), ogtype="article" if t.get("loai") == "article" else "website",
                   site=SITE, path=t["path"], ld=ld_cho(t), kenh=kenh, robots='\n<meta name="robots" content="noindex">' if t.get("noindex") or t["path"] == "/404.html" else "")
    vet = " · ".join([f'<a href="/">Trang chủ</a>'] + [f'<a href="{u}">{html.escape(n)}</a>' for n, u in t.get("vet", [])[:-1]])
    s += f'<article class="doc wrap">\n<p class="vet">{vet}</p>\n<h1>{html.escape(t["h1"])}</h1>\n'
    if t.get("mo"): s += f'<p class="mo">{md_inline(t["mo"])}</p>\n'
    if t.get("anh"):
        s += f'<figure><img class="anh-doc" src="{t["anh"][0]}" alt="{html.escape(t["anh"][1])}" width="640" height="427"><figcaption class="chu-anh">{html.escape(t["anh"][1])}</figcaption></figure>\n'
    if t.get("ghi_chu"): s += f'<p class="ghi-chu">{md_inline(t["ghi_chu"])}</p>\n'
    s += md(t["than"]) + "\n"
    if t.get("form"):
        s += '<div class="form-rieng">' + re.search(r'<form id="form-brief".*?</form>', idx_html(), re.S).group(0) + "</div>\n"
    if t.get("form_hoc_thu"):
        s += '<div class="form-rieng">' + re.search(r'<form id="form-hoc-thu".*?</form>', idx_html(), re.S).group(0) + "</div>\n"
    if t.get("cam_on"):
        s += '<p class="ma-lead" id="ma-lead" hidden></p><script>(function(){var m=/[?&]ma=([A-Z0-9-]{6,20})/.exec(location.search);if(m){var e=document.getElementById("ma-lead");e.textContent="Mã đăng ký của bạn: "+m[1];e.hidden=false}})()</script>\n'
    if t.get("hoi_dap"):
        s += '<section class="faq"><h2 id="hoi-dap">Câu hỏi hay gặp</h2>' + "".join(f"<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>" for q, a in t["hoi_dap"]) + "</section>\n"
    if t.get("cta", True):
        s += f'<aside class="cta-cuoi"><h2>Cần lớp AI cho đội của bạn?</h2><p>Đăng ký tư vấn, bạn nhận bảng khảo sát đầu vào, đề cương theo phòng ban và báo giá.</p><div class="cta-row"><a class="btn btn-main" href="/?kenh={kenh}#dang-ky">Đăng ký tư vấn</a><a class="btn btn-ghost" href="/hoc-thu/?kenh={kenh}">Học thử một bài</a></div></aside>\n'
    s += "</article>\n" + CHAN
    dich = PUB / t["path"].strip("/") / "index.html" if t["path"] != "/404.html" else PUB / "404.html"
    dich.parent.mkdir(parents=True, exist_ok=True); dich.write_text(s, encoding="utf-8")
    return t["path"]

def sitemap(paths):
    u = "".join(f"<url><loc>{SITE}{p}</loc><lastmod>2026-11-10</lastmod></url>" for p in ["/"] + paths if p not in ("/404.html", "/cam-on/"))
    (PUB / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{u}</urlset>\n', encoding="utf-8")

if __name__ == "__main__":
    ps = [tao(json.loads(f.read_text(encoding="utf-8"))) for f in sorted((GOC / "nguon").glob("*.json"))]
    sitemap(ps); print("\n".join(ps))
