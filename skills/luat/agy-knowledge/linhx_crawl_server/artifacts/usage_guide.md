# API Usage Guide

The server is typically hosted at `http://localhost:8000`.

## Endpoints

### 1. Single Crawl (`POST /crawl`)
Request body (JSON):
```json
{
    "url": "https://example.com",
    "output_format": "markdown",
    "preferred_tier": null, 
    "screenshot": false,
    "wait_for": ".selector"
}
```
*Note: `preferred_tier` skips the waterfall.*

### 2. Batch Crawl (`POST /batch`)
Request body (JSON):
```json
{
    "urls": ["url1", "url2"],
    "max_concurrency": 5
}
```

### 3. Sitemap Discovery (`POST /sitemap?url=...`)
Discovers all internal links and images. Uses multiple strategies:
- `robots.txt` parsing.
- Common path probing (`/sitemap.xml`, `/sitemap_index.xml`).
- Direct HTML spidering of the homepage.

### 4. Runtime Logs (`GET /runtime`)
Lists recent crawl IDs and their meta-data.
Fetch details with `GET /runtime/{crawl_id}`.

## Agent Skill Pattern
Agents should prefer the `/crawl` endpoint without a `preferred_tier` to allow the server to optimize. If a site is known to be JS-heavy (e.g., Ticketbox, Facebook), agents should set `preferred_tier: "t2_crawl4ai"`.
