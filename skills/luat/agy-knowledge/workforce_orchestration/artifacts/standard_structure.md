# Standard Directory Tree

The following structure is strictly maintained to ensure isolation and organization.

/ROOT_WORKSPACE
├── 00_SESSION_STATE.md     # [The Heart] Active task/project pointer
├── 00_WORKFORCE_RULES.md    # [The Laws] System Constitution
├── .agent/                 # [System] Native AG configuration
│   ├── skills/             # Mirror links to /02_WORKFORCE/Skill_Matrix
│   └── workflows/          # Mirror links to /02_WORKFORCE/Workflows
│
├── /01_DATA (Read-only)
│   ├── /Enterprise_Docs    # Enterprise documents, fixed processes
│   ├── /Knowledge_Base     # Industrial/specialized expertise
│   └── /Assets             # Brand assets, templates
│
├── /02_WORKFORCE (System Definition)
│   ├── /Org_Chart          # Departments & Reporting lines
│   ├── /Agents_Roster      # Agent personas and roles
│   ├── /Skill_Matrix       # Atomic actions/functions (tools)
│   ├── /Workflows          # SOPs and coordination logic
│   └── /Learning_Logs      # (Write-allowed) Experience repository
│
└── /03_PROJECTS (Execution Sandbox)
    ├── /Project_A
    │   ├── /Brief          # Project requirements
    │   ├── /Tasks          # Active task containers
    │   └── /Artifacts      # Final deliverables
    └── /Project_B ...
```

## Folder Roles

### 00_SESSION_STATE.md
The workspace "Bookmark". It contains a direct link to the active task's `work_log.md`, ensuring that new agent sessions can instantly restore context without searching.

### .agent
The system-facing configuration. To keep the workspace human-readable and maintainable, agents don't directly edit here. Instead, a **Mirroring Mechanism** syncs definitions from `/02_WORKFORCE` into `.agent` so the AG core can recognize them as native skills and workflows.

### /01_DATA
Serving as the "Long-term Memory/Identity", these files are read-only to prevent agents from polluting the source of truth.

### /02_WORKFORCE
The "Brain/Central Nervous System". It defines who is available (Roster), what they can do (Skills), and how they work together (Workflows).

### /03_PROJECTS
The "Working Memory". All writes happen here, specifically within task-scoped subfolders.

---

## The Physics (Data Pillars)
The system's integrity is governed by the **[System Constitution](implementation/system_constitution.md)**, which maps these directories to biological metaphors (Heart, Memory, Genome, Workspace) and defines the mandatory **Operating Modes** (Builder vs Runtime).
