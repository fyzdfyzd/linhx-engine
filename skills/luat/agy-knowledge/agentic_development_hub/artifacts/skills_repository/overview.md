# Antigravity Awesome Skills Repository

The primary library of 600+ high-performance agentic skills.

## Core Categories
- **Architecture**: C4 models, ADRs, system design.
- **Business**: SEO, marketing, pricing analysis.
- **Data & AI**: RAG, prompt engineering, agent memory.
- **Development**: Language experts (Python, TypeScript, Go, etc.).
- **Security**: vulnerability scans, pentesting, compliance.
- **Workflow**: CI/CD, automation scripts.

## Installation & Discovery
1.  **Repository Setup**: Clone and organize skills into a central directory (e.g., `skills/`).
2.  **Recognition (SKILL.md)**: Each skill must contain a `SKILL.md` file following the standard format (name, description, risk, triggers) to be discoverable by agents.
3.  **Discovery**: Use `CATALOG.md` or natural language queries ("Use the @skill-name...") for invocation.

## Skill Format
```markdown
---
name: [skill-name]
description: [specific use cases and description]
risk: [safe/risky]
source: [internal/external]
---
# [Documentation]
```
