# LINHX LAB Scanning Pattern

## Overview
The LINHX LAB Scanning Pattern is a standardized directory and data organization structure used for systematic research, scanning, and data collection across various domains (Advertising, Social Impact, Events, etc.). It is designed to facilitate parallel processing by AI agents and maintain consistency in metadata and classification.

## Core Principles
- **Standardized Configuration**: Centralized schema and taxonomy definitions.
- **Master Data Management**: A single source of truth for all tracked entities.
- **Artifact-to-Entity Mapping**: Each entity has its own profile directory with detailed markdown documentation and media.
- **Status Lifecycle**: Discovered → Researched → Analyzed → Verified.

## Standard Directory Structure
```
[PROJECT_ROOT]/
├── _CONFIG/
│   ├── schema.md          # Defines the structure for profile.md files
│   ├── taxonomy.md        # Classification codes (e.g., types, areas, scales)
│   ├── hub_registry.csv   # List of source websites/platforms to scan
│   └── [domain]_registry.csv # Specific lists (e.g., venue_registry)
├── _MASTER/
│   ├── master_list.csv    # Consolidated data for all entities
│   ├── hub_list.csv       # Summary of hub stats
│   └── [sub_lists].csv    # E.g., permanent programs
├── [ENTITIES_FOLDER]/     # Plural name (e.g., CAMPAIGNS, EVENTS, INITIATIVES)
│   └── [entity-slug]/
│       ├── profile.md     # Detailed metadata based on schema
│       ├── research.md    # Raw data, sources, logs
│       └── media/         # Images, videos, articles
├── REPORTS/               # Generated summaries and analysis
└── .agent/                # Agent configurations and logs
```

## Integrated Tooling
The pattern is supported by the **LinhX Crawl Server**, which uses a **Waterfall Fallback Pattern** (httpx ➔ Crawl4AI ➔ Firecrawl ➔ Playwright). This ensures that the scanning phase of the pattern is reliable, scalable, and cost-effective across various project domains.
