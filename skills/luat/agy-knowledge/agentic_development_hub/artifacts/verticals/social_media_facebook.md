# Social Media Automation (Facebook)

A specialized vertical implementation of agentic browser automation.

## 1. Scraping Logic
- **Infinite Scrolling**: Use scroll-to-bottom loops with wait pauses to handle dynamic content loading.
- **Data Capture**: Extract post content, timestamps, and engagement metrics into standardized JSON/CSV formats.

## 2. Safety & Risk Mitigation
- **Throttling**: Implement human-like delay intervals between scrolls and clicks.
- **Account Protection**: Limit scraping frequency and volume to avoid triggering platform anti-automation flags (e.g., "Ban" or "Checkpoint").
- **Manual Handover**: Use the "Manual Login Pattern" for initial authentication.

## 3. Implementation Checklist
- [ ] Connect via Chrome CDP to use local profile.
- [ ] Implement robust selectors (using data-attributes or aria-labels).
- [ ] Handle modal popups and "See More" expansions.
- [ ] Export to persisted storage with deduplication logic.
