#!/usr/bin/env python3
"""Sinh trang con từ nguon/*.json dùng chung đầu/chân với trang chủ. Chạy: python3 tao-trang.py"""
import json, html, pathlib, re
GOC = pathlib.Path(__file__).parent
PUB = GOC / "public"
SITE = "https://tuva.work"
TEN = "TUVA Communication"

NAV = {
 "vi": dict(skip="Bỏ qua, tới nội dung", nhan="TUVA Communication, trang chủ", goc="/",
   links='<a href="/#dich-vu">Dịch vụ</a>\n      <a href="/de-xuat-tai-tro/">Đề xuất tài trợ</a>\n      <a href="/bo-quy-tac-ai/">Bộ quy tắc AI</a>\n      <a href="/cam-nang/">Cẩm nang</a>\n      <a href="/en/" hreflang="en" lang="en">English</a>',
   cta="Trao đổi dự án", cta_href="/?kenh={kenh}#brief", vet="Trang chủ"),
 "en": dict(skip="Skip to content", nhan="TUVA Communication, home", goc="/en/",
   links='<a href="/en/#services">Services</a>\n      <a href="/en/#proposals">Proposals</a>\n      <a href="/en/#ai-rules">AI rules</a>\n      <a href="/" hreflang="vi" lang="vi">Tiếng Việt</a>',
   cta="Talk to us", cta_href="/en/?kenh={kenh}#brief", vet="Home"),
}

DAU = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="{ogtype}">
<meta property="og:image" content="{site}/img/og.png">
<meta name="theme-color" content="#2A1E1A">
<link rel="canonical" href="{site}{path}">{robots}
<link rel="icon" href="/img/icon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/site.css?v=1">
<script type="application/ld+json">{ld}</script>
</head>
<body>
<a class="skip" href="#noi-dung">{skip}</a>
<header class="top">
  <div class="wrap nav">
    <a href="{goc}" class="logo" aria-label="{nhan}"><img src="/img/logo-ngang-am-ban.svg" alt="TUVA Communication, Reaching out" width="212" height="34"></a>
    <nav aria-label="Menu">
      {links}
    </nav>
    <a class="btn btn-main nav-cta" href="{cta_href}">{cta}</a>
  </div>
</header>
<main id="noi-dung">
"""
CHAN = {
 "vi": """</main>
<footer class="foot">
  <div class="wrap">
    <div class="foot-cot">
      <div><img src="/img/logo-ngang-am-ban.svg" alt="TUVA Communication" width="200" height="32"><p>Truyền thông và AI cho các dự án phát triển ở Việt Nam.</p><p data-cfg="lien_he_chan">Để lại thông tin ở form, chúng tôi liên hệ lại.</p></div>
      <nav aria-label="Dịch vụ"><b>Dịch vụ</b><a href="/giai-phap/ai-cho-ngo/">AI cho NGO</a><a href="/giai-phap/truyen-thong-du-an/">Truyền thông dự án</a><a href="/giai-phap/lang-nghe-du-lieu/">Lắng nghe dữ liệu</a><a href="/de-xuat-tai-tro/">Đề xuất tài trợ</a></nav>
      <nav aria-label="Tài nguyên"><b>Tài nguyên</b><a href="/bo-quy-tac-ai/">Bộ quy tắc AI</a><a href="/tu-cham-ai/">Tự chấm mức sẵn sàng AI</a><a href="/decent-ai/">Decent AI</a><a href="/cam-nang/">Cẩm nang</a></nav>
      <nav aria-label="TUVA"><b>TUVA</b><a href="/gioi-thieu/">Giới thiệu</a><a href="/linh-vuc/">Lĩnh vực</a><a href="/hoi-dap/">Hỏi đáp</a><a href="/lien-he/">Liên hệ</a><a href="/en/" hreflang="en" lang="en">English</a></nav>
    </div>
    <div class="foot-in"><p data-cfg="phap_nhan">© 2026 TUVA Communication</p><p><a href="/chinh-sach-du-lieu/">Chính sách dữ liệu</a> · <a href="https://listening.vn/?kenh=tuva-chan-trang&amp;utm_source=tuva.work&amp;utm_medium=referral&amp;utm_campaign=chan-trang" target="_blank" rel="noopener">Listening Vietnam</a></p></div>
  </div>
</footer>
<script src="/app.js?v=1" defer></script>
</body>
</html>
""",
 "en": """</main>
<footer class="foot">
  <div class="wrap">
    <div class="foot-cot">
      <div><img src="/img/logo-ngang-am-ban.svg" alt="TUVA Communication" width="200" height="32"><p>Communication and AI for development projects in Vietnam.</p><p data-cfg="en_lien_he">Leave your details in the form and we will get back to you.</p></div>
      <nav aria-label="Services"><b>Services</b><a href="/en/#services">AI for NGOs</a><a href="/en/#services">Project communication</a><a href="/en/#services">Social listening</a></nav>
      <nav aria-label="Proposals"><b>Proposals</b><a href="/en/#proposals">Concept note, budget, logframe</a><a href="/en/#ai-rules">AI rules for organisations</a><a href="/en/#brief">Talk to us</a></nav>
      <nav aria-label="TUVA"><b>TUVA</b><a href="/" hreflang="vi" lang="vi">Tiếng Việt</a><a href="/gioi-thieu/" hreflang="vi">About (Vietnamese)</a></nav>
    </div>
    <div class="foot-in"><p data-cfg="phap_nhan">© 2026 TUVA Communication</p><p><a href="/chinh-sach-du-lieu/" hreflang="vi">Data policy (Vietnamese)</a></p></div>
  </div>
</footer>
<script src="/app.js?v=1" defer></script>
</body>
</html>
""",
}

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
    goc = NAV[t.get("lang", "vi")]
    g = [{"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate([(goc["vet"], goc["goc"])] + t.get("vet", []))]}]
    org = {"@type": "Organization", "name": TEN, "url": SITE + "/"}
    if t.get("loai") == "service":
        g.append({"@type": "Service", "name": t["h1"], "serviceType": "AI and communication for development", "areaServed": "VN", "description": t["desc"], "provider": org, "audience": {"@type": "Audience", "audienceType": "NGO, cơ quan Liên Hợp Quốc, nhà tài trợ"}})
    if t.get("loai") == "article":
        g.append({"@type": "Article", "headline": t["h1"], "description": t["desc"], "inLanguage": t.get("lang", "vi"), "author": org, "publisher": dict(org, logo={"@type": "ImageObject", "url": SITE + "/img/logo-ngang-mau.svg"}), "datePublished": t.get("ngay", "2026-11-10"), "mainEntityOfPage": SITE + t["path"]})
    if t.get("hoi_dap"):
        g.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t["hoi_dap"]]})
    return json.dumps({"@context": "https://schema.org", "@graph": g}, ensure_ascii=False)

def cat(idx, mau):
    return re.search(mau, idx, re.S).group(0)

def tao(t):
    kenh, lang = t.get("kenh", "trang"), t.get("lang", "vi")
    n = NAV[lang]
    s = DAU.format(lang=lang, title=html.escape(t["title"]), desc=html.escape(t["desc"]), ogtype="article" if t.get("loai") == "article" else "website",
                   site=SITE, path=t["path"], ld=ld_cho(t), skip=n["skip"], nhan=n["nhan"], goc=n["goc"], links=n["links"], cta=n["cta"],
                   cta_href=n["cta_href"].format(kenh=kenh), robots='\n<meta name="robots" content="noindex">' if t.get("noindex") or t["path"] == "/404.html" else "")
    vet = " · ".join([f'<a href="{n["goc"]}">{n["vet"]}</a>'] + [f'<a href="{u}">{html.escape(x)}</a>' for x, u in t.get("vet", [])[:-1]])
    s += f'<article class="doc wrap">\n<p class="vet">{vet}</p>\n<h1>{html.escape(t["h1"])}</h1>\n'
    if t.get("mo"): s += f'<p class="mo">{md_inline(t["mo"])}</p>\n'
    if t.get("ghi_chu"): s += f'<p class="ghi-chu">{md_inline(t["ghi_chu"])}</p>\n'
    idx = (PUB / ("en/index.html" if lang == "en" else "index.html")).read_text(encoding="utf-8")
    if t.get("cham"):
        s += '<div class="cham-rieng">' + cat(idx, r'<div class="cham" id="cham".*?<button type="button" class="cham-lui" hidden>.*?</button>\s*</div>') + "</div>\n"
    s += md(t["than"]) + "\n"
    if t.get("form_tai"):
        s += '<div class="form-rieng" id="bo-quy-tac">' + cat(idx, r'<form id="form-tai".*?</form>') + "</div>\n"
    if t.get("form"):
        s += '<div class="form-rieng" id="brief">' + cat(idx, r'<form id="form-brief".*?</form>') + "</div>\n"
    if t.get("cam_on"):
        nhan = "Your reference code: " if lang == "en" else "Mã của bạn: "
        s += '<p class="ma-lead" id="ma-lead" hidden></p><script>(function(){var m=/[?&]ma=([A-Z0-9-]{6,20})/.exec(location.search);if(m){var e=document.getElementById("ma-lead");e.textContent="' + nhan + '"+m[1];e.hidden=false}})()</script>\n'
    if t.get("hoi_dap"):
        s += '<section class="faq"><h2 id="hoi-dap">Câu hỏi hay gặp</h2>' + "".join(f"<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>" for q, a in t["hoi_dap"]) + "</section>\n"
    if t.get("cta", True):
        s += (f'<aside class="cta-cuoi"><h2>Có dự án hoặc đề xuất sắp nộp?</h2><p>Gửi lĩnh vực, nhà tài trợ và hạn nộp. Chúng tôi gợi ý hạng mục truyền thông và AI, khung ngân sách và chỉ số cho logframe.</p>'
              f'<div class="cta-row"><a class="btn btn-main" href="/?kenh={kenh}#brief">Trao đổi một dự án</a><a class="btn btn-sang" href="/bo-quy-tac-ai/?kenh={kenh}">Tải bộ quy tắc AI</a></div></aside>\n')
    s += "</article>\n" + CHAN[lang]
    dich = PUB / t["path"].strip("/") / "index.html" if t["path"] != "/404.html" else PUB / "404.html"
    dich.parent.mkdir(parents=True, exist_ok=True); dich.write_text(s, encoding="utf-8")
    return t["path"]

def sitemap(paths):
    u = "".join(f"<url><loc>{SITE}{p}</loc><lastmod>2026-11-10</lastmod></url>" for p in ["/", "/en/"] + paths if p not in ("/404.html", "/cam-on/", "/en/thank-you/"))
    (PUB / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{u}</urlset>\n', encoding="utf-8")

if __name__ == "__main__":
    ps = [tao(json.loads(f.read_text(encoding="utf-8"))) for f in sorted((GOC / "nguon").glob("*.json"))]
    sitemap(ps); print("\n".join(ps))
