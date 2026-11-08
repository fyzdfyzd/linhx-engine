# Skill Definition Template (Reference Grade)

Skills defined in `/02_WORKFORCE/Skill_Matrix/` must be placed in a subfolder and contain a `SKILL.md` file. This template follows the high-quality standard found in the Antigravity Skills repository.

```markdown
---
name: [skill_unique_id]
description: [Concise description of the skill's purpose for LLM discovery. Max 2-3 sentences.]
---

# [Skill Display Name]

[A one-paragraph master overview of the skill and the domain it covers.]

## Use this skill when

- [Scenario 1: Primary use case]
- [Scenario 2: Context where this tool shines]
- [Scenario 3: Specific task type]

## Do not use this skill when

- [Scenario 1: When logic or another tool is better]
- [Scenario 2: When data is already in internal knowledge base]
- [Scenario 3: Scope limitation]

## Instructions

1.  **[Step Title]**: [Brief description of action].
2.  **[Step Title]**: [Brief description of action].
3.  **[Step Title]**: [Brief description of action].
4.  **[Step Title]**: [Brief description of action].

## Best Practices

### [Category A: e.g., Query Optimization / Logic Improvement]
- [Actionable tip 1]
- [Actionable tip 2]

### [Category B: e.g., Verification / Quality Control]
- [Actionable tip 1]
- [Actionable tip 2]

## Example Usage

**Goal**: "[Specific result desired by user]"

**Process**:
1.  *Query/Action*: "[Specific input passed to tool]"
2.  *Tool Invocation*: `[tool_name]([parameters])`
3.  *Synthesis*: [Description of how the agent combines results into the final output]
```
