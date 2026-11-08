# Synchronization Mechanism (Mirroring)

To maintain a clean separation between human-readable management and technical execution, the Workforce Orchestration framework uses a mirroring mechanism.

## Overview
The "Source of Truth" for all agents, skills, and workflows resides in `/02_WORKFORCE`. However, the Antigravity engine natively expects these configurations in a hidden or system-specific directory (typically `.agent/`).

The sync mechanism ensures that any updates made to the workforce definitions are automatically or manually propagated to the system configuration.

## PowerShell Implementation (`sync_workforce.ps1`)

The following script is used to synchronize the `/02_WORKFORCE` definitions to the `.agent` directory.

```powershell
# Sync Workforce to System Config
# Copy 02_WORKFORCE content to .agent/ for Antigravity consumption

$WorkforcePath = "$PSScriptRoot\02_WORKFORCE"
$SystemPath = "$PSScriptRoot\.agent"

Write-Host "Starting Workforce Sync..." -ForegroundColor Cyan

# 1. Sync Skills
$SourceSkills = "$WorkforcePath\Skill_Matrix"
$DestSkills = "$SystemPath\skills"

if (Test-Path $SourceSkills) {
    Write-Host "Syncing Skills..."
    # Copy recursively, force overwrite
    Copy-Item -Path "$SourceSkills\*" -Destination $DestSkills -Recurse -Force -ea SilentlyContinue
    Write-Host "Skills Synced." -ForegroundColor Green
} else {
    Write-Host "Warning: Skill_Matrix folder not found." -ForegroundColor Yellow
}

# 2. Sync Workflows
$SourceWorkflows = "$WorkforcePath\Workflows"
$DestWorkflows = "$SystemPath\workflows"

if (Test-Path $SourceWorkflows) {
    Write-Host "Syncing Workflows..."
    Copy-Item -Path "$SourceWorkflows\*" -Destination $DestWorkflows -Recurse -Force -ea SilentlyContinue
    Write-Host "Workflows Synced." -ForegroundColor Green
} else {
    Write-Host "Warning: Workflows folder not found." -ForegroundColor Yellow
}

# 3. Sync Native Rules
$SourceRules = "$WorkforcePath\Rules"
$DestRules = "$SystemPath\rules"

if (Test-Path $SourceRules) {
    Write-Host "Syncing Rules..."
    Copy-Item -Path "$SourceRules\*" -Destination $DestRules -Recurse -Force -ea SilentlyContinue
    Write-Host "Rules Synced." -ForegroundColor Green
}

# 4. Sync Session State
$SourceState = "$PSScriptRoot\00_SESSION_STATE.md"
if (Test-Path $SourceState) {
    Copy-Item -Path $SourceState -Destination "$SystemPath\SESSION_STATE.md" -Force
    Write-Host "Session State Synced." -ForegroundColor Green
}

Write-Host "Sync Complete. Workforce is now live." -ForegroundColor Cyan
```

## Usage in Lifecycle
- **Genesis Phase**: Run once after initial population to activate the workforce.
- **Maintenance**: Run whenever a skill definition or workflow is modified in `/02_WORKFORCE`.
- **Automated Trigger**: Can be integrated into a CI/CD pipeline or a "Watcher" agent that monitors the directory for changes.

## Verification Protocol
To ensure the workforce is "live," perform the following checks:
1.  **Skills Verification**: Check for the existence of `SKILL.md` files in `.agent/skills/{skill_name}/`.
2.  **Workflow Verification**: Check for the existence of workflow definitions in `.agent/workflows/`.
3.  **Command Test**: Run a directory check (e.g., `dir .agent/skills`) to confirm file presence.

## Sync Type Distinction
- **Hard-Sync (Skills & Workflows)**: These are "installed" into the AG system config via mirroring. They define the *capabilities* of the engine.
- **Native Rules Sync**: Markdown files in `/02_WORKFORCE/Rules` are mirrored to `.agent/rules/`. These provide the engine with its governing constitution and operational guidelines.
- **Pulse Sync (Session State)**: The `00_SESSION_STATE.md` is synced to the `.agent` root to provide the engine with its current operational context.
- **Soft-Sync (Agent Personas)**: Personas in `/02_WORKFORCE/Agents_Roster` are not copied to `.agent`. Instead, the AG engine (acting as the Operator) reads these files dynamically at runtime to "adopt" the character.
