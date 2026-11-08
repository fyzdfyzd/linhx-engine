# Antigravity Workforce Lifecycle

The Antigravity (AG) system evolves through three primary phases, transitioning between Architecting (Genesis/Evolution) and Operating (Runtime).

---

## 1. Genesis Phase (Creation)
In this phase, the system acts as an **Architect** to build the `/02_WORKFORCE` directory (the "DNA" of the workforce).

### Population Rules (Waterfall Strategy)
1.  **Departments**: Define functions in `/Org_Chart/manifest.md`.
2.  **Agents**: Create persona profiles in `/Agents_Roster`.
3.  **Skills**: Define atomic actions in `/Skill_Matrix`.
4.  **Workflows**: Connect agents and skills via SOPs in `/Workflows`.
5.  **Skill Importation**: Selectively import production-ready skills from global repositories.
6.  **Activation**: Sync definitions from `/02_WORKFORCE` to the system's `.agent/` config.

### Agent Persona Requirements
- **Identity**: Personality, tone, and mission.
- **Permissions**: Explicit data access levels.
- **Skill Set**: Mapped atomic actions.

---

## 2. Runtime Phase (Operation)
During execution, the system acts as an **Operator** managing specific tasks with rigid discipline.

### Task Execution Loop
1.  **Isolation**: Create unique task containers under `/03_PROJECTS/{Project}/Tasks/{Task_ID}/`.
2.  **Invocation**: Assign personas from `/Agents_Roster`.
3.  **Execution**: Work exclusively within the task folder.
4.  **Context Maintenance**: Update `00_SESSION_STATE.md` with active project/task pointers.

### The Work Log (`work_log.md`)
Every task folder must maintain a log covering:
- **Pre-work**: Problem definition and reference identification.
- **In-progress**: Chain of Thought, tool usage, and self-corrections.
- **Post-work**: Final outputs and artifact inventory.

---

## 3. Evolution Phase (Learning)
The "Living Organism" learns from completed work to improve its core definitions.

### The Feedback Loop
1.  **Memory Capture**: Agents record insights to `/02_WORKFORCE/Learning_Logs/`.
2.  **Optimization Trigger**: System identifies more efficient methods or tool improvements.
3.  **Governance**: Updates to the `Workflows` or `Skill_Matrix` require validation to prevent logic degradation.
4.  **Immutability Violation**: Structural updates are performed ONLY in **BUILDER_MODE**.
