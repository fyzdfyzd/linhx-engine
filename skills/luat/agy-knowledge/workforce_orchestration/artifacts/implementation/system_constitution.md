# Antigravity Workforce Constitution

> **VERSION**: 2.2 (Native Rule Format Aligned)
> **PURPOSE**: Defines the operating laws of the Antigravity "Living Organism", adhering to the core tenets of the Google Antigravity Framework and using native rule schemas.

---

## 1. Core Tenets

Every agent within the system must embody these four principles:

1.  **TRUST**: Agents don't just complete work; they *prove* it with artifacts and verification results.
2.  **AUTONOMY**: Agents autonomously plan and solve problems via `implementation_plan.md` without requiring micro-management.
3.  **FEEDBACK**: Agents seek and incorporate intuitive user feedback throughout the execution process.
4.  **SELF-IMPROVEMENT**: Learning is a core primitive. Insights are preserved in the knowledge base to improve future task sequences.

---

## 2. The Physics (Data Pillars)

The system exists across three immutable data pillars. Every agent must strictly adhere to this map.

*   **`00_SESSION_STATE.md` (The Heart)**: Contains the current pulse of the system. Tracks the active task, project, and operating mode. This file is the primary context anchor.
*   **`/02_WORKFORCE/Rules/` (The Laws)**: Contains native Antigravity rules (Markdown with frontmatter) that define constraints and behaviors. These are mirrored to `.agent/rules`.
*   **`/01_DATA` (Long-term Memory)**: Immutable enterprise documents and reference knowledge. Read-only in Runtime.
*   **`/02_WORKFORCE` (Genome/DNA)**: Definitions of Agents, Skills, and Workflows. Modifying this changes the "nature" of the workforce.
*   **`/03_PROJECTS` (Working Memory/Workspace)**: The only area where transformation and production occur during Runtime.

---

## 3. Operating Modes

The system operates in two distinct states, toggled via `00_SESSION_STATE.md`.

### 🅰️ BUILDER_MODE (Creation/Evolution)
*   **Trigger**: Activated when re-architecting system rules, defining new skills, or structural maintenance.
*   **Authority**: **God Mode**. Agents are permitted to modify `/02_WORKFORCE` and `/01_DATA` (if needed for maintenance).
*   **Priority**: Structure and System Integrity.
*   **Logging**: High-level system changelogs rather than per-step task logs.

### 🅱️ RUNTIME_MODE (Execution/Disciplined Production)
*   **Trigger**: Activated during the execution of specific project tasks.
*   **Authority**: **Restricted**. `/01_DATA` and `/02_WORKFORCE` are strictly **Read-Only**.
*   **Priority**: Task completion, consistency, and traceability.
*   **Logging**: **Steel Discipline**. Every significant action must be recorded in the task's `work_log.md`.

---

## 4. The Primal Protocol (Wake-up Procedure)

When an agent session begins, the agent MUST follow this mandatory initialization sequence:

1.  **Check Pulse**: Read `00_SESSION_STATE.md`. Determine `CURRENT_MODE`, `ACTIVE_PROJECT`, and `ACTIVE_TASK`.
2.  **Load Identity**: If a task is active, internalize the assigned persona from `/02_WORKFORCE/Agents_Roster/`.
3.  **Sync Context**: Read the `work_log.md` of the active task to find "Where am I?".
4.  **Analyze Hierarchy**: Check the [Instruction Hierarchy](task_hygiene.md#5-instruction-hierarchy) (Brief > Work Log > Session State).
5.  **Execute**: Perform the "Next Step" as defined in the log.
6.  **Log & Sleep**: Update the `work_log.md` with findings and the *new* Next Step before terminating the turn.

---

## 4. The Artifact Loop (Task Protocol)

In **RUNTIME_MODE**, agents must follow a strictly mandated "Plan → Execute → Verify" loop for complex tasks:

1.  **Planning** (`task.md` & `implementation_plan.md`):
    *   Decompose the goal into a granular checklist in `task.md`.
    *   Create a detailed `implementation_plan.md` for any non-trivial architectural or code changes.
2.  **Execution** (Work Log & Production):
    *   Execute the plan while maintaining a strict `work_log.md`.
    *   Store all interim drafts within the task folder.
3.  **Verification** (`walkthrough.md`):
    *   Upon completion, generate a `walkthrough.md` to showcase and verify the work.
    *   Finalize and "graduate" artifacts only after successful verification.

---

## 5. Native Rules Schema

To ensure rules are correctly interpreted by the Antigravity engine, they must follow the Markdown frontmatter standard:

```markdown
---
description: [Natural language description of when/how this rule applies]
globs: [Glob pattern for target files, e.g., "**/*"]
always_on: [true|false]
---
# Rule Title
[Constraints and Instructions]
```

### Activation Types
*   **Always On**: Applied to every task and interaction.
*   **Model Decision**: The LLM decides to apply the rule based on the `description`.
*   **Glob-based**: Automatically applied when the agent interacts with matching files.
*   **Manual**: Triggered by `@RuleName` in the prompt.

---

## 6. Task Lifecycle

1.  **Genesis (Initiation)**:
    *   Create task container: `/03_PROJECTS/<Project>/Tasks/<Task_ID>/`.
    *   Initialize `work_log.md`.
    *   Link/Copy relevant Brief components.
2.  **Execution (Runtime)**:
    *   Perform work within the task folder.
    *   Maintain strict log discipline.
3.  **Termination (Closing)**:
    *   "Graduate" finalized Artifacts to the project-level `/Artifacts` folder.
    *   Clear the active task pointer in `00_SESSION_STATE.md`.
    *   Mark task as `DONE` in its log.
