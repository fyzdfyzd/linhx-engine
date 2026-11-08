# Web Search Skill: Best Practices & Pattern

This document outlines the standard operating procedure for agents using the `web_search` skill to gather real-time information, market data, and trend analysis.

## 1. Core Workflow

1.  **Formulate Queries**: Create specific, targeted search queries. Avoid vague terms.
2.  **Execute Search**: Use the search tool with the formulated query.
3.  **Analyze Results**: Read snippets and titles carefully for relevance.
4.  **Deep Dive (Optional)**: If snippets are insufficient, use a browser tool or URL reader to fetch the full page content.
5.  **Synthesize**: Combine information from multiple results into a coherent answer.

## 2. Query Optimization
- **Keywords**: Use specific terms (e.g., "Generative AI trends forecast 2026 Gartner" instead of just "AI trends").
- **Resolution**: Start with broad overviews, then refine queries based on initial results to find niche data.
- **Verification**: Cross-reference facts across multiple domain authorities (official documentation, reputable news, established blogs).

## 3. Synthesis Pattern
A high-quality search synthesis should follow this structure:
- **Overview**: A high-level summary of the findings.
- **Key Findings**: Bullet points of the most important facts/data points.
- **Sources**: A list of URLs and titles for transparency and verification.

## 4. Usage Heuristics
- **When to Use**: Up-to-date info, market trends, fact-checking, broad synthesis.
- **Avoid When**: Pure logic/math tasks, info already in internal knowledge base (`/01_DATA`), or tasks requiring authenticated interaction.
