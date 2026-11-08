---
name: proposal-ideas
description: Researches world event technology and proposes 4–6 scored activation ideas for a brief (including IFAGENT talking-character ideas where they fit), before the full proposal is built. Use when the user says "đề xuất ý tưởng", "brainstorm hoạt động", "ý tưởng cho mascot", "có ý tưởng gì cho event", "nghiên cứu công nghệ event".
---

# Ideas before the proposal

1. Make sure a brief analysis exists (run the `proposal-brief` steps if not).
2. Research: read `${CLAUDE_PLUGIN_ROOT}/skills/proposal-studio/references/event-tech-library.md`, then run 3–5 fresh searches (this year's CES/Cannes/experiential trends, same-category brand activations, local market cases). Record source and date for each example.
3. Write 4–6 ideas. For each: name (Vietnamese, catchy, ≤ 4 words), one-line mechanic, technology, insight it answers, rough ops need. At least one idea uses IFAGENT capabilities from `references/ifagent-capabilities.md`; do not promise features listed under "Not built yet" without marking them custom work.
4. Score with the table in `references/proposal-outline.md` and recommend a combined journey (big idea: name + tagline + 4–6 steps) plus add-ons per budget package.
5. Save into `01-phan-tich-y-tuong.md` (sections: phân tích brief, nghiên cứu, ý tưởng, chấm điểm, khuyến nghị, nguồn).
6. Present the ideas briefly in chat and ask which to build – unless the user already said to continue, then go straight to `proposal-studio` step 5 with the recommendation.
