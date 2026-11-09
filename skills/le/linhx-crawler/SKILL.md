---
name: linhx-crawler
description: Crawl web content via LinhX Lab's self-hosted multi-tier FastAPI server. Supports waterfall fallback (httpx → Crawl4AI → Firecrawl → Playwright) for maximum reliability. Use for fetching article content, discovering sitemaps, batch crawling, and extracting media assets.
metadata:
  version: "0.1.0"
---

# LinhX Crawler

A self-hosted web crawling service running on `http://localhost:8080`. It uses a **4-tier waterfall pattern** — starting from the lightest tool and escalating only when needed — to crawl any website reliably.

## Use this skill when

- You need to **fetch the full content** of a web page (article, blog, docs, news)
- You need to **discover all URLs** on a website via sitemap
- You need to **batch crawl** multiple URLs at once
- You need to **extract media** (images, videos, PDFs) from a page
- A previous `read_url_content` call returned incomplete/empty content (JS-heavy site)

## Do not use this skill when

- The content is already available in the local knowledge base
- You only need a quick Google search (use `search_web` instead)
- The URL is a direct file download (PDF, image) — just download it
- The site requires login (Tier 4 Playwright can handle basic auth, but not complex 2FA)

## Instructions

### Prerequisites
The crawl server must be running. If not:
```powershell
cd "H:\My Drive\WORKFORCE\TOOL\CRAWLER"
python -m uvicorn main:app --host 0.0.0.0 --port 8080
```

### 1. Crawl a Single URL

Use the `run_command` tool to call the `/crawl` endpoint:

```powershell
python -c "import httpx,json; r=httpx.post('http://localhost:8080/crawl', json={'url':'TARGET_URL'}, timeout=30); d=r.json(); print(json.dumps({k:v for k,v in d.items() if k!='content'},indent=2)); print('---CONTENT---'); print(d.get('content','')[:2000])"
```

**Replace** `TARGET_URL` with the actual URL you want to crawl.

**Response includes:**
- `content` — full page content as markdown
- `tier_used` — which tier handled the request
- `media` — dict with `images`, `videos`, `pdfs`, `documents` found in the page
- `metadata.crawl_id` — unique ID, full logs saved to `runtime/{crawl_id}/`

### 2. Force a Specific Tier

If you know a site is JS-heavy, skip directly to Crawl4AI or Playwright:

```json
{
    "url": "https://react-spa-site.com",
    "preferred_tier": "t2_crawl4ai"
}
```

Available tiers: `t1_httpx`, `t2_crawl4ai`, `t3_firecrawl`, `t4_playwright`

### 3. Discover All URLs on a Website (Sitemap)

First discover all URLs, then batch crawl from the list:

```powershell
python -c "import httpx,json; r=httpx.post('http://localhost:8080/sitemap?url=https://example.com&max_pages=500', timeout=30); d=r.json(); print(f'Total URLs: {d[\"total_urls\"]}'); print(json.dumps(d['urls'][:20],indent=2))"
```

This tries: `robots.txt` → common sitemap paths → XML sitemap parsing → HTML link spider.

### 4. Batch Crawl Multiple URLs

After getting a URL list from sitemap or manually:

```powershell
python -c "import httpx,json; r=httpx.post('http://localhost:8080/batch', json={'urls':['URL1','URL2','URL3'], 'max_concurrency':5}, timeout=60); d=r.json(); print(f'Succeeded: {d[\"succeeded\"]}/{d[\"total\"]}'); [print(f'  {x[\"url\"]}: {x.get(\"tier_used\")} ({x.get(\"content_length\")} chars)') for x in d['results']]"
```

### 5. Check Past Crawl Logs

Every crawl is saved to `runtime/{crawl_id}/` with request, response, content, and log files:

```powershell
# List recent crawls
python -c "import httpx,json; r=httpx.get('http://localhost:8080/runtime?limit=10'); [print(f'{x[\"id\"]} | {x.get(\"url\",\"?\")[:50]} | success={x.get(\"success\")}') for x in r.json()['runs']]"

# Get specific crawl detail
python -c "import httpx,json; r=httpx.get('http://localhost:8080/runtime/CRAWL_ID'); d=r.json(); print(d.get('log',''))"
```

### 6. Extract Media from a Page

Media is automatically included in every `/crawl` response under the `media` field:

```json
{
    "media": {
        "images": ["https://example.com/photo.jpg", "..."],
        "videos": ["https://youtube.com/embed/abc", "..."],
        "pdfs": ["https://example.com/report.pdf"],
        "documents": [],
        "total_images": 12,
        "total_videos": 2,
        "total_pdfs": 1,
        "total_documents": 0
    }
}
```

Sources checked: `<img>`, `<video>`, `<iframe>` (YouTube/Vimeo), `<a href>` to files, CSS backgrounds, `og:image`, `og:video`.

## Best Practices

### Efficiency
- Always let the waterfall auto-select — it picks the lightest tier that works
- Use `preferred_tier` only when you **know** the site needs JS rendering
- For bulk work: use `/sitemap` first to build a list, then `/batch` to crawl

### Reliability
- If a crawl returns `success: false`, check `attempts` to see which tiers were tried and why they failed
- Check `runtime/{crawl_id}/log.txt` for detailed tier-by-tier execution logs
- Short content (< 200 chars) is auto-rejected — the waterfall tries the next tier

### Data Projects Workflow
1. **Discover**: `POST /sitemap?url=...` → get all page URLs
2. **Filter**: Pick relevant URLs from the list
3. **Crawl**: `POST /batch` with selected URLs
4. **Extract**: Each result has `content` (markdown) + `media` (assets)
5. **Review**: Check `GET /runtime` for logs and quality

## Example Usage

**Goal**: "Crawl all articles from bemiagent.com and extract images"

**Process**:
1. *Sitemap*: `POST /sitemap?url=https://bemiagent.com` → Returns 47 URLs
2. *Filter*: Select URLs containing `/news/` → 12 article URLs
3. *Batch*: `POST /batch` with the 12 URLs → All succeed via Tier 1
4. *Result*: Each article has markdown content + media dict with images
5. *Verify*: `GET /runtime` → 12 crawl logs saved, all green
