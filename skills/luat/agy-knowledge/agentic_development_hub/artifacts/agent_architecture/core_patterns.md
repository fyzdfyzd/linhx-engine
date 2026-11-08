# Agentic Development Patterns

Core architectural patterns for building robust AI agents and automated systems.

## 1. Browser Automation Patterns
When building agents that interact with web interfaces:

### Browser Connection (CDP)
Connect to existing browser instances to bypass automated detection or maintain session state.
```python
async with async_playwright() as p:
    browser = await p.chromium.connect_over_cdp("http://localhost:9222")
    # ...
```

### Manual Login Handover
For sites with complex MFA or detection, allow the user to perform the login manually, then the agent detects the session success (e.g., finding a "Home" button) before proceeding.

### Universal Scrapers
Implement "Infinite Scroll" scrapers using robust selectors that wait for visibility and use `evaluate` scripts for reliable DOM extraction.

## 2. Verification Fallbacks
In restricted environments (e.g., CI/CD, limited-permission containers) where full browser engines (Playwright/Puppeteer) fail to initialize (common error: `$HOME environment variable is not set`):

- **Connectivity Checks**: Use `read_url_content` or `curl` on `localhost` to verify the development server is serving content.
- **HTML Validation**: Inspect the raw HTML returned from connectivity checks to verify the presence of key mounting points (e.g., `<div id="root"></div>`) and script bundles.

## 3. Gemini Agent Core
A standard "Base Agent" pattern for Gemini-driven systems:
- **Tool Mapping**: Explicit mapping between natural language requests and specific agentic skills.
- **Context Management**: Passing historical session state and current environment metadata to the model.
- **Retry Logic**: Wrapping tool calls in retry loops specifically for "System Error" or "Refusal" edge cases.

## 4. Workforce Orchestration
A advanced pattern for managing multi-agent teams using a structured file system "Living Organism" model.
- **Directory Isolation**: Dividing the workspace into `/01_DATA`, `/02_WORKFORCE`, and `/03_PROJECTS`.
- **Phased Lifecycle**: Genesis (Setup), Runtime (Execution), and Evolution (Self-correction).
- **Immutable Core**: Keeping system definitions and source data read-only during task execution to prevent drift.
- **Strict Logging**: Using `work_log.md` with Pre/In/Post stages in every task folder.

For details, see the `workforce_orchestration` Knowledge Item.
