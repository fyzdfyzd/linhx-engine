# Context Anchoring (Session State)

Ensuring that a multi-agent workforce maintains continuity across separate user sessions or conversation starts is critical for production reliability. The **Context Anchoring** pattern solves this by using a standardized pointer file in the workspace root.

## The `00_SESSION_STATE.md` File

This file acts as a "Neo ngữ cảnh" (Context Anchor). It is the first file any arriving agent should read to understand what is currently happening.

### Required Structure
```markdown
# ANTIGRAVITY SESSION STATE
> DO NOT DELETE. This file tracks the active context for the Workforce.

**Last Updated**: [Timestamp]
**Current Active Project**: [Project Name]
**Current Active Task**: [Task_ID]

## Context Restoration Instructions
If you are a new Agent entering this workspace:
1.  **READ** the Work Log below immediately:
    `[Path to the active task folder]\work_log.md`
2.  **ADOPT** the persona currently assigned in that log.
3.  **CONTINUE** the specific 'Next Step' listed in the log.

## Quick Links
- [Project Brief]([Path to brief])
- [Workforce Definitions](02_WORKFORCE)
```

## Local Persistence Principle

To ensure that the state is visible and persistent:
- **No Hidden Vaults**: Do not store the primary `work_log.md` or `00_SESSION_STATE.md` inside a hidden system folder (like a `.agent` or `.gemini` folder).
- **Project Scope**: All task progress logs must reside in the `/03_PROJECTS/.../Tasks/{Task_ID}/` directory.
- **Root Pointer**: The pointer (`00_SESSION_STATE.md`) must reside at the top level of the workspace for easy discovery by any tool or agent.

## Restoration Workflow

1.  **Initialization**: User starts a new conversation.
2.  **Discovery**: Agent (or system instruction) performs a search or listing of the root directory and identifies `00_SESSION_STATE.md`.
3.  **Handoff**: Agent reads the pointer, navigates to the indicated `work_log.md`, and reads the execution history.
4.  **Resumption**: Agent adopt the required persona and continues the work from the last recorded step.
