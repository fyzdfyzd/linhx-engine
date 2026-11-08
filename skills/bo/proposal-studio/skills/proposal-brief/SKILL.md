---
name: proposal-brief
description: Analyses a client brief for an event or activation proposal – extracts objectives, audience, constraints, insights and lists what the brief is missing. Use when the user says "phân tích brief", "đọc brief giúp", "brief này thiếu gì", "tóm tắt brief", or pastes a brief without asking for the full proposal yet.
---

# Brief analysis

1. Extract into a table: brand, objective, audience (primary/secondary), time, locations, budget, KPI, constraints, mandatory elements. Mark anything not stated as `[ ]` and label the row "giả định".
2. If the brief is thin, research the brand (recent campaigns, store count, positioning, mascot usage) with WebSearch/WebFetch; keep source + date for every fact.
3. Write 2–3 insights (what the audience wants that the brand can give) and one problem statement ("vui tại chỗ phải dẫn về … và đo được").
4. List questions for the client using the checklist in `${CLAUDE_PLUGIN_ROOT}/skills/proposal-studio/references/proposal-outline.md` → "Brief còn thiếu gì". Only ask what the brief does not answer.
5. Save as `brief.md` (the brief, assumed parts marked) and the first section of `01-phan-tich-y-tuong.md` in the project folder `proposals/<client>-<yyyy>/`.
6. Offer the next step: ideas (`proposal-ideas`) or the full proposal (`proposal-studio`).
