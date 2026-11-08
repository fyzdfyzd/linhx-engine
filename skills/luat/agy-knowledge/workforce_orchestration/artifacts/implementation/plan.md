# Workforce Orchestration Implementation Plan

This plan outlines the technical steps to realize the "Living Organism" concept on the Antigravity (AG) platform.

## 1. Technical Mapping
To maintain the distinction between human-readable management (/02_WORKFORCE) and system execution (.agent), we use a **Mirroring Strategy**.

### The Mirroring Mechanism
1. **Source of Truth**: All Skill and Workflow definitions are authored as Markdown or YAML files in `/02_WORKFORCE/Skill_Matrix` and `/02_WORKFORCE/Workflows`.
2. **Runtime Sync**: A system script or AG-native workflow automatically synchronizes these files to `.agent/skills/` and `.agent/workflows/`.
3. **Format Enforcement**:
   - Each Skill must be in a folder with a `SKILL.md` file containing YAML frontmatter.
   - Workflows must follow the AG engine's native graph or step definition format.

## 2. Operation Cycle
### Genesis (Scaffolding)
- `Architect Agent` initializes the directory tree.
- Core personas and atomic skills are populated in `/02_WORKFORCE`.
- Initial `Sync` triggers to enable system capabilities.

### Runtime (Execution)
- `Operator Agent` creates isolated task folders in `/03_PROJECTS/{Project}/Tasks/{Task_ID}`.
- Agents adopt personas by reading `/02_WORKFORCE/Agents_Roster/{Agent}.md`.
- Every action is logged in `work_log.md` within the task folder.
- **Handoffs**: When switching roles, the agent preserves context by reading the `Brief` and `work_log.md`.

### Evolution (Learning)
- `Auditor Agent` analyzes `Learning_Logs` and `work_log.md` files.
- Suggestions for Skill or Workflow improvements are proposed for Admin approval.

## 3. Tooling Requirements
- **Watcher Script**: To auto-sync changes from the workforce definition to the system configuration.
- **Isolator**: To enforce that agents only write within their assigned Task folder.
- **Logger**: A standardized tool/skill for agents to write structured thoughts to `work_log.md`.
