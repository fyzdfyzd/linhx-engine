# Task Execution Hygiene

To maintain isolation and traceability, agents must follow strict file management protocols within the `/03_PROJECTS` sandbox.

## 1. Output Placement Convention

When executing a task, all generated files—including drafts, logs, and interim artifacts—should be stored **within the specific task folder** under `/03_PROJECTS/{Project_Name}/Tasks/{Task_ID}/`.

### Why this exists:
- **Isolation**: Prevents different tasks within the same project from overwriting each other's work or polluting the project-level `Artifacts` folder before data is finalized.
- **Traceability**: All context related to a specific task remains in one place for future audit or continuation by another agent.
- **Human Guidance**: The user expects to find current work results in the task folder as the "active" work area.

## 2. Generic Artifacts vs. Task Folders
- **Task Folder**: For *active* work, drafts, and task-specific logs.
- **Project Artifacts Folder**: Only for *finalized* deliverables that have been reviewed and accepted. Transfers to this folder should be a conscious "graduation" step.

## 3. Work Log Management (`work_log.md`)
Every task folder MUST contain a `work_log.md`. This is the single source of truth for:
1.  **Status**: Current phase of the task.
2.  **File Inventory**: A list of files created within the task folder.
3.  **Next Steps**: Clear hand-off instructions if the session expires.

## 4. User Interaction Pattern
If a user asks "where are the instructions" or "where is the file", the agent should immediately:
1.  Locate the active `work_log.md`.
2.  Summarize its contents.
3.  Correct the file path if a file was accidentally stored in a project-level directory instead of the task-level directory.

## 5. Workspace vs. System Paths (Critical Execution Rule)
Agents must distinguish between the **Internal Brain** and the **User Workspace**:

- **DO NOT** manually write deliverables to paths starting with `C:\Users\Admin\.gemini\antigravity\brain\`. This is a system-internal storage for task state and artifact mirroring.
- **ALWAYS** set `TargetFile` to a path within the user's mapped workspace (e.g., `d:\@work\AGWORKSPACE\03_PROJECTS\...`).
- The system automatically mirrors workspace artifacts into the brain, but writing directly to the brain path bypasses the user's project structure and causes "file not found" friction for the human.

## 6. Instruction Hierarchy
To avoid confusion during execution, agents must know where to look for "The Truth":

- **Level 1: Project Brief** (`/03_PROJECTS/{Project}/Brief/`): Contains the overarching mission, brand voice, and high-level milestones. Read this to understand "Why" and "What".
- **Level 2: Task Work Log** (`/03_PROJECTS/{Project}/Tasks/{Task}/work_log.md`): Contains the immediate "Next Step" and current inventory. Read this to understand "Now".
- **Level 3: Session State** (`/00_SESSION_STATE.md`): Contains the global task/agent pointer. Read this to understand "Who" and "Where".
