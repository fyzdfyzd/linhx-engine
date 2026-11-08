# Antigravity Workforce Orchestration Overview

This framework treats the entire workspace as a **"Living Organism"** operating within a rigid, read-only directory structure for core data and system definitions.

## Core Philosophy
- **Immutability at Runtime**: Antigravity (AG) does not change the core Data or Workforce structure during task execution.
- **Isolation**: Every task runs in its own sandbox (Task Folder).
- **Transparency**: Strict logging protocols ensure every thought and action is recorded.
- **Evolution**: The system learns from completed tasks and updates its core knowledge periodically.

## Directory Structure
The workspace is divided into three primary roots:
- `/01_DATA`: Immutable enterprise documents and knowledge base.
- `/02_WORKFORCE`: System definitions (Org Chart, Roster, Skills, Workflows) that are mirrored to the system's `.agent` folder for execution.
- `/03_PROJECTS`: The execution sandbox where tasks are performed.

## Core Components
- **Standardized Rosters**: Pre-defined agent personas (Technical core: Architect, Planner, Coder; Specialty squads: Personal Branding) with specialized responsibilities.
- **Reference-Grade Skills**: Integration of high-performance skills from the Antigravity library (e.g., ADRs, Planning-with-files).
- **Mirroring Mechanism**: Seamless sync between human-readable definitions in `/02_WORKFORCE` and system configs in `.agent`.
