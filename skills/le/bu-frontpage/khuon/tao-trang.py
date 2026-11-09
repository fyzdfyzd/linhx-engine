#!/usr/bin/env python3
"""Sinh trang con từ nguon/*.json dùng chung đầu/chân với trang chủ. Chạy: python3 tao-trang.py"""
import json, html, pathlib, re
GOC = pathlib.Path(__file__).parent
PUB = GOC / "public"
SITE = "https://event.ifagent.net"

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
<meta name="theme-color" content="#0D1117">
<link rel="canonical" href="{site}{path}">{robots}
<link rel="icon" href="/img/icon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/site.css?v=3">
<script type="application/ld+json">{ld}</script>
</head>
<body>
<a class="skip" href="#noi-dung">Bỏ qua, tới nội dung</a>
<header class="top">
  <div class="wrap nav">
    <a href="/" class="logo" aria-label="IF Agent Event, trang chủ"><img src="/img/logo.svg" alt="IF Agent" width="132" height="43"></a>
    <nav aria-label="Mục chính">
      <a href="/#giai-phap">Giải pháp</a>
      <a href="/goi/">Gói</a>
      <a href="/cong-nghe-su-kien/">Cẩm nang</a>
      <a href="/#hoi-dap">Hỏi đáp</a>
    </nav>
    <a class="btn btn-ghost nav-cta" href="/?kenh={kenh}#brief">Gửi brief</a>
  </div>
</header>
<main id="noi-dung">
"""
CHAN = """</main>
<footer class="foot">
  <div class="wrap">
    <div class="foot-cot">
      <div><img src="/img/logo.svg" alt="IF Agent" width="110" height="36"><p>Công nghệ AI tương tác cho sự kiện.</p><p>Zalo <a href="https://zalo.me/0904106143">0904 106 143</a><br><a href="mailto:hangnt@ifagent.vn">hangnt@ifagent.vn</a></p></div>
      <nav aria-label="Giải pháp"><b>Giải pháp</b><a href="/giai-phap/nhan-vat-ai/">Nhân vật AI</a><a href="/giai-phap/photobooth/">AI Photobooth</a><a href="/giai-phap/minigame/">Minigame QR</a><a href="/goi/">Gói và giá</a><a href="/mau-bao-cao/">Mẫu báo cáo 24 giờ</a></nav>
      <nav aria-label="Theo sự kiện"><b>Theo sự kiện</b><a href="/su-kien/hoi-cho-trien-lam/">Hội chợ, triển lãm</a><a href="/su-kien/ra-mat-san-pham/">Ra mắt sản phẩm</a><a href="/su-kien/hoi-nghi/">Hội nghị, summit</a><a href="/agency/">Cho agency</a></nav>
      <nav aria-label="Công ty"><b>IF Agent</b><a href="/gioi-thieu/">Giới thiệu</a><a href="/du-an/">Dự án</a><a href="/cam-nang/">Cẩm nang</a><a href="/hoi-dap/">Hỏi đáp</a><a href="/lien-he/">Liên hệ</a></nav>
    </div>
    <div class="foot-in"><p data-cfg="phap_nhan">© 2026 IF Agent</p><p><a href="/chinh-sach-du-lieu/">Chính sách dữ liệu</a> · <a href="https://demo.ifagent.net">demo.ifagent.net</a></p></div>
  </div>
</footer>
<script src="/app.js?v=3" defer></script>
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
        g.append({"@type": "Service", "name": t["h1"], "serviceType": "Event technology", "areaServed": "VN", "description": t["desc"], "provider": {"@type": "Organization", "name": "IF Agent", "url": SITE + "/"}})
    if t.get("loai") == "article":
        g.append({"@type": "Article", "headline": t["h1"], "description": t["desc"], "inLanguage": "vi", "author": {"@type": "Organization", "name": "IF Agent"}, "publisher": {"@type": "Organization", "name": "IF Agent", "logo": {"@type": "ImageObject", "url": SITE + "/img/logo.svg"}}, "datePublished": t.get("ngay", "2026-11-10"), "mainEntityOfPage": SITE + t["path"]})
    if t.get("hoi_dap"):
        g.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t["hoi_dap"]]})
    return json.dumps({"@context": "https://schema.org", "@graph": g}, ensure_ascii=False)

def tao(t):
    kenh = t.get("kenh", "trang")
    s = DAU.format(title=html.escape(t["title"]), desc=html.escape(t["desc"]), ogtype="article" if t.get("loai") == "article" else "website",
                   site=SITE, path=t["path"], ld=ld_cho(t), kenh=kenh, robots='\n<meta name="robots" content="noindex">' if t.get("noindex") or t["path"] == "/404.html" else "")
    vet = " · ".join([f'<a href="/">Trang chủ</a>'] + [f'<a href="{u}">{html.escape(n)}</a>' for n, u in t.get("vet", [])[:-1]])
    s += f'<article class="doc wrap">\n<p class="vet">{vet}</p>\n<h1>{html.escape(t["h1"])}</h1>\n'
    if t.get("mo"): s += f'<p class="mo">{md_inline(t["mo"])}</p>\n'
    if t.get("ghi_chu"): s += f'<p class="ghi-chu">{md_inline(t["ghi_chu"])}</p>\n'
    s += md(t["than"]) + "\n"
    if t.get("form"):
        idx = (PUB / "index.html").read_text(encoding="utf-8")
        s += '<div class="form-rieng">' + re.search(r'<form id="form-brief".*?</form>', idx, re.S).group(0) + "</div>\n"
    if t.get("cam_on"):
        s += '<p class="ma-lead" id="ma-lead" hidden></p><script>(function(){var m=/[?&]ma=([A-Z0-9-]{6,20})/.exec(location.search);if(m){var e=document.getElementById("ma-lead");e.textContent="Mã brief của bạn: "+m[1];e.hidden=false}})()</script>\n'
    if t.get("hoi_dap"):
        s += '<section class="faq"><h2 id="hoi-dap">Câu hỏi hay gặp</h2>' + "".join(f"<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>" for q, a in t["hoi_dap"]) + "</section>\n"
    if t.get("cta", True):
        s += f'<aside class="cta-cuoi"><h2>Có sự kiện sắp tới?</h2><p>Gửi brief, bạn nhận lại ý tưởng, demo chạy được với logo của bạn và báo giá trong 1 ngày làm việc.</p><div class="cta-row"><a class="btn btn-main" href="/?kenh={kenh}#brief">Gửi brief</a><a class="btn btn-ghost" href="https://demo.ifagent.net/?kenh={kenh}" target="_blank" rel="noopener">Thử demo</a></div></aside>\n'
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
