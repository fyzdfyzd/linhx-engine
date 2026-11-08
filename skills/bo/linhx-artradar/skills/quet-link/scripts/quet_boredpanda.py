"""Quét bài Bored Panda về nghệ thuật/truyện tranh: chỉ lấy metadata + link nghệ sĩ, không tải ảnh.

Dùng:
  python quet_boredpanda.py --out data/records.jsonl --max 50
  python quet_boredpanda.py --urls ds-bai.txt --out data/records.jsonl

Chỉ dùng thư viện chuẩn Python 3.9+.
"""
import argparse
import gzip
import http.cookiejar
import json
import re
import sys
import time
import urllib.error
import urllib.request
import urllib.robotparser
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = "https://www.boredpanda.com"
UA = "LINHX-LAB-artradar/0.1 (research; metadata and links only)"
# Khớp theo TỪ trong slug (tách bằng "-"), từ khoá là tiền tố: "comic" khớp "comics", "art" chỉ
# khớp "art/arts/artist/artwork" chứ không khớp "party", "start". Bỏ "cat" (khớp "education").
KEYWORDS = ["art", "arts", "artist", "artwork", "illustrat", "comic", "webcomic", "drawing", "draws",
            "painting", "painter", "character-design", "doodle", "sketch", "cartoon", "anime", "manga"]
# Chỉ các gốc này mới khớp tiền tố (illustrat-ion/-or, comic-al, cartoon-ist...); còn lại khớp nguyên từ
# hoặc thêm "s" ("manga" không được khớp "manganiello").
STEMS = {"illustrat", "comic", "webcomic", "cartoon", "doodle", "sketch", "drawing", "painting", "painter"}
# Slug có các cụm này là bài game/tin/meme, không phải bài nghệ sĩ.
SKIP_SLUG = re.compile(r"guess-the|main-character|fictional-character|bio-and|memes?(-|$)|photograph|net-worth")
NOAI = ("noai", "noimageai")

# Domain -> nhãn; link sang các domain này được coi là link của nghệ sĩ.
ARTIST_DOMAINS = {
    "instagram.com": "instagram", "artstation.com": "artstation", "behance.net": "behance",
    "deviantart.com": "deviantart", "twitter.com": "x", "x.com": "x", "tiktok.com": "tiktok",
    "patreon.com": "patreon", "webtoons.com": "webtoon", "tapas.io": "tapas",
    "youtube.com": "youtube", "facebook.com": "facebook", "tumblr.com": "tumblr",
    "etsy.com": "etsy", "linktr.ee": "linktree", "pixiv.net": "pixiv", "threads.net": "threads",
    "bsky.app": "bluesky", "reddit.com": "reddit", "ko-fi.com": "kofi", "gumroad.com": "gumroad",
}
SKIP_HOSTS = ("boredpanda", "google.", "doubleclick", "apple.com", "play.google", "amazon.",
              "cloudflare", "gstatic", "wp.com", "gravatar", "onesignal", "disqus")
SKIP_PATHS = ("/sharer", "/intent/", "/share", "/pin/create", "/dialog/", "/plugins/", "/tr?")
SKIP_HANDLES = {"p", "reel", "reels", "explore", "stories", "tv", "accounts", "watch", "hashtag",
                "home", "search", "i", "intent", "share", "boredpanda", "boredpandacom"}


# Bored Panda trả 302 về chính URL để đặt cookie khách bp_visitor_id; không giữ cookie thì urllib
# lặp redirect vô hạn. Cookie jar chỉ sống trong 1 lần chạy, không đăng nhập.
OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def fetch(url, delay):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
    time.sleep(delay)
    with OPENER.open(req, timeout=30) as r:
        body = r.read()
        if r.headers.get("Content-Encoding") == "gzip" or url.endswith(".gz"):
            body = gzip.decompress(body)
        return body.decode("utf-8", "replace"), r.headers


def sitemap_urls(xml_text):
    """Trả (là_index, [(loc, lastmod)])."""
    root = ET.fromstring(xml_text.encode("utf-8"))
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    is_index = root.tag.endswith("sitemapindex")
    tag = "s:sitemap" if is_index else "s:url"
    out = []
    for node in root.findall(tag, ns):
        loc = node.findtext("s:loc", default="", namespaces=ns).strip()
        lastmod = node.findtext("s:lastmod", default="", namespaces=ns).strip()
        if loc:
            out.append((loc, lastmod))
    return is_index, out


def pick_articles(rp, delay, maximum, keywords, sitemap_hint):
    maps = [sitemap_hint] if sitemap_hint else (rp.site_maps() or [ROOT + "/sitemap.xml"])
    found, queue, seen_maps = [], list(maps), set()
    while queue and len(found) < maximum:
        sm = queue.pop(0)
        if sm in seen_maps:
            continue
        seen_maps.add(sm)
        try:
            text, _ = fetch(sm, delay)
            is_index, items = sitemap_urls(text)
        except Exception as e:  # noqa: BLE001
            print(f"[bỏ sitemap] {sm}: {e}", file=sys.stderr)
            continue
        items.sort(key=lambda x: x[1], reverse=True)
        if is_index:
            # Ưu tiên sitemap bài viết, mới nhất trước; bỏ sitemap tag/category/author/games.
            posts = [loc for loc, _ in items if re.search(r"post|article", loc)
                     and not re.search(r"tag|categor|author|game|hub|news", loc)]
            queue.extend(posts or [loc for loc, _ in items])
            continue
        for loc, lastmod in items:
            if loc not in found and slug_match(loc, keywords) and rp.can_fetch(UA, loc):
                found.append(loc)
                if len(found) >= maximum:
                    break
    return found


def slug_match(url, keywords):
    slug = urlparse(url).path.strip("/").lower()
    # Bỏ trang chuyên mục (/art/, /comics/): slug bài thật có ít nhất 3 từ.
    if not slug or "/" in slug or slug.count("-") < 2 or SKIP_SLUG.search(slug):
        return False
    words = slug.split("-")
    for k in keywords:
        if "-" in k:
            if k in slug:
                return True
        elif any(w == k or w == k + "s" or (k in STEMS and w.startswith(k)) for w in words):
            return True
    return False


def article_body(html):
    """Cắt phần thân bài: từ <h1 tới dòng post-submission-line (trước hộp tác giả, bình luận,
    footer). Phần JSON-LD và hộp tác giả Bored Panda chứa link mạng xã hội của người viết bài,
    không phải của nghệ sĩ."""
    start = html.find("<h1")
    end = html.find("post-submission-line", max(start, 0))
    if end < 0:
        end = html.rfind("</article>")
    if start < 0 or end <= start:
        return html
    return html[start:end]


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta, self.links, self.in_script = {}, [], False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta":
            key = a.get("property") or a.get("name")
            if key and "content" in a:
                self.meta.setdefault(key.lower(), a["content"])
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"])


def classify(href):
    u = urlparse(href)
    if u.scheme not in ("http", "https"):
        return None
    host = u.netloc.lower().removeprefix("www.").removeprefix("m.")
    if any(s in host for s in SKIP_HOSTS) or any(s in href for s in SKIP_PATHS):
        return None
    for dom, label in ARTIST_DOMAINS.items():
        if host == dom or host.endswith("." + dom):
            parts = [p for p in u.path.split("/") if p]
            if label in ("instagram", "x", "tiktok", "threads", "artstation", "behance",
                         "patreon", "deviantart", "kofi", "linktree") and parts:
                handle = parts[0].lstrip("@").lower()
                if handle in SKIP_HANDLES or "boredpanda" in handle:
                    return None
                return label, f"https://{dom}/{parts[0]}"
            if label == "tumblr" and host != dom:
                return label, f"https://{host}"
            return label, f"{u.scheme}://{host}{u.path}".rstrip("/")
    return "web", f"{u.scheme}://{host}{u.path}".rstrip("/")


CREDIT_RE = re.compile(r"(Image credits?|Image source|More info|Credit)\s*:\s*(.{1,200}?)(?:<br|</p|</div|\n)", re.I)


# Trang mới không có meta article:published_time; ngày nằm trong JSON-LD.
DATE_RE = re.compile(r'"datePublished"\s*:\s*"([^"]+)"')


def parse_article(url, html, headers):
    p = LinkParser()
    p.feed(html)  # meta lấy từ cả trang
    body = LinkParser()
    body.feed(article_body(html))
    xrobots = " ".join(headers.get_all("X-Robots-Tag") or []).lower()
    meta_robots = (p.meta.get("robots", "") + " " + p.meta.get("googlebot", "")).lower()
    links = {}
    for href in body.links:
        c = classify(unescape(href))
        if c:
            links.setdefault(c[0], [])
            if c[1] not in links[c[0]]:
                links[c[0]].append(c[1])
    credits, more_info = [], []
    for m in CREDIT_RE.finditer(article_body(html)):
        txt = re.sub(r"<[^>]+>", " ", m.group(2))
        txt = re.sub(r"\s+", " ", unescape(txt)).strip(" |")
        bucket = more_info if m.group(1).lower() == "more info" else credits
        if txt and txt not in bucket:
            bucket.append(txt)
    return {
        "source": "boredpanda",
        "url": url,
        "title": unescape(p.meta.get("og:title", "")),
        "description": unescape(p.meta.get("og:description", ""))[:300],
        "published": p.meta.get("article:published_time", "") or (DATE_RE.search(html) or [None, ""])[1],
        "thumb_url": p.meta.get("og:image", ""),
        "noai": any(k in xrobots or k in meta_robots for k in NOAI),
        "credits": credits[:20],
        "more_info": more_info[:5],
        "links": links,
        # Bài tổng hợp (ảnh của nhiều người từ Reddit…) không phải bài về 1 nghệ sĩ.
        "tong_hop": sum(map(len, links.values())) > 15 or len(links.get("reddit", [])) > 5,
        "scanned_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--max", type=int, default=50)
    ap.add_argument("--delay", type=float, default=4.0)
    ap.add_argument("--urls", help="file danh sách URL bài, mỗi dòng 1 URL (bỏ qua sitemap)")
    ap.add_argument("--sitemap", help="URL sitemap cụ thể (mặc định lấy từ robots.txt)")
    ap.add_argument("--keywords", default=",".join(KEYWORDS))
    a = ap.parse_args()

    rp = urllib.robotparser.RobotFileParser(ROOT + "/robots.txt")
    rp.read()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out.exists():
        for line in out.read_text(encoding="utf-8").splitlines():
            try:
                done.add(json.loads(line)["url"])
            except Exception:  # noqa: BLE001
                pass

    if a.urls:
        urls = [u.strip() for u in Path(a.urls).read_text(encoding="utf-8").splitlines() if u.strip()]
    else:
        urls = pick_articles(rp, a.delay, a.max + len(done), a.keywords.split(","), a.sitemap)
    urls = [u for u in dict.fromkeys(urls) if u not in done][: a.max]
    print(f"{len(urls)} bài cần quét", file=sys.stderr)

    n_ok = n_noai = 0
    with out.open("a", encoding="utf-8") as f:
        for i, url in enumerate(urls, 1):
            if not rp.can_fetch(UA, url):
                print(f"[robots chặn] {url}", file=sys.stderr)
                continue
            try:
                html, headers = fetch(url, a.delay)
            except urllib.error.URLError as e:
                print(f"[lỗi] {url}: {e}", file=sys.stderr)
                continue
            rec = parse_article(url, html, headers)
            n_noai += rec["noai"]
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n_ok += 1
            print(f"{i}/{len(urls)} {rec['title'][:70]} | {sum(map(len, rec['links'].values()))} link", file=sys.stderr)
    print(json.dumps({"scanned": n_ok, "noai": n_noai, "out": str(out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
