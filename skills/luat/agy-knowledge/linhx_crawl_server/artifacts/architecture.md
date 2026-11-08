# Waterfall Fallback Architecture

The server attempts to crawl a URL using a sequence of "Tiers" from lightest (fastest, static) to heaviest (slowest, full browser rendering).

| Tier | Technology | Characteristics | Best For |
| :--- | :--- | :--- | :--- |
| **Tier 1** | `httpx` | Direct GET request. Fastest (ms). | Static sites, blogs, news, REST APIs. |
| **Tier 2** | `Crawl4AI` | Optimized JS rendering + content filtering. Fast (2-5s). | Modern SPAs, dynamic content, sites needing cleanup. |
| **Tier 3** | `Firecrawl` | Self-hosted Docker service. Robust extraction. (3-8s). | Complex nested pages, deep scraping. |
| **Tier 4** | `Playwright` | Direct browser (Chromium). Heavy (5s+). | Hard-to-scrape sites, login walls, complex interactions. |

## Orchestration Logic
1. **Tier 1 Attempt**: If response > 200 chars and status 200, return immediately.
2. **Fallback to Tier 2**: If Tier 1 fails or returns insufficient content.
3. **Escalation**: Continue through tiers until success.
4. **Result Consolidation**: Extract media assets (images, videos, PDFs) from the raw HTML regardless of the tier used.
