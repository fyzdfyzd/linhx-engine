# LinhX Crawl Server Overview

## Concept
The **LinhX Crawl Server** is a specialized FastAPI application designed for robust web data extraction in data-intensive research projects. Its primary innovation is the **Waterfall Fallback Pattern**, which optimizes for speed and cost by trying lighter scraping methods before escalating to heavier browser-based rendering.

## System Architecture

The server implements a **Waterfall Orchestration Pattern**, attempting tiers in order of increasing resource intensity and stopping at the first success.

### The 4 Tiers
1.  **Tier 1: `t1_httpx`**: Fast, lightweight direct HTTP fetch. Best for static sites and REST APIs.
2.  **Tier 2: `t2_crawl4ai`**: Playwright-based rendering with specialized content filtering and markdown extraction.
3.  **Tier 3: `t3_firecrawl`**: Self-hosted Docker instance for deep scraping and sitemap processing.
4.  **Tier 4: `t4_playwright`**: Full direct browser control. Used for heavy JS, login flows, or as a final fallback.

### Execution Flow
1.  **Request**: URL + (Optional) `preferred_tier`.
2.  **Orchestrator**: If `preferred_tier` is set, execute only that tier. Otherwise, start Waterfall.
3.  **Waterfall Loop**: T1 ➔ T2 ➔ T3 ➔ T4.
4.  **Verification**: After each attempt, check for `success` and `content_length` (> 200 chars).
5.  **Logging**: Full execution logs and results are stored in `runtime/{crawl_id}/`.

## Key Features
- **4-Tier Waterfall**: httpx ➔ Crawl4AI ➔ Firecrawl ➔ Playwright.
- **100% Self-Hosted**: Zero reliance on paid external APIs (Firecrawl is used via a self-hosted Docker instance).
- **Structured Output**: Returns cleaned Markdown (default), JSON, or raw HTML.
- **Batch Processing**: Supports concurrent crawling of up to 50 URLs per request.
- **Sitemap Discovery**: Automated crawling to build a map of a website's URLs and image assets.
- **Runtime Logging**: Every crawl generates a unique ID and persists logs, requests, and results in a `runtime/` directory for debugging.

## Core Components
- `waterfall.py`: Orchestrator logic that manages tier switching and fallback.
- `tiers/`: Modular implementation of each scraping method.
- `api/routes.py`: FastAPI endpoints for integration with AI agents.
- `utils/sitemap.py`: Logic for parsing robots.txt, probing common paths, and XML parsing.
