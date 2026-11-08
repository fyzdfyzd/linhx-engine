---
name: proposal-studio
description: Turns an event/activation brief into a complete, replaceable proposal package – brief analysis, world event-tech research, solution ideas (using IFAGENT tech where it fits), gameplay flow, per-screen specs with mockup images, technical illustration, image prompts for ChatGPT/Google Flow, and an editable PPTX deck rebuilt from JSON. Use when the user says "viết proposal", "làm đề xuất", "làm proposal từ brief", "pitch activation", "đề xuất sự kiện", "proposal cho mascot", "build lại proposal", or pastes a client brief and wants a proposal.
---

# Proposal Studio

Produce a proposal the way an event agency pitches: understand the brief, research, propose ideas, show exactly how it works, then deliver a deck the team can edit and re-skin. Every output lives in one project folder so text and images can be swapped and rebuilt.

## Project folder (always the same shape)

```
proposals/<client>-<yyyy>/
  brief.md                  input brief (or the assumed brief, clearly marked)
  01-phan-tich-y-tuong.md   brief analysis + research + ideas + scoring (step 1–4)
  proposal.json             ALL deck content → build_deck.py
  mockups.json              screen/diagram/floorplan specs → render_mockups.py
  images/<stem>.png|jpg|webp   one file per stem; newest file per stem wins
  image-prompts.md          prompts per stem for ChatGPT Plus / Google Flow
  <file>.pptx               built deck (editable)
  <file>-noi-dung.md        plain text of every slide (for review / copy)
```

Put the folder inside the user's connected folder (default `proposals/`) unless told otherwise. Images always sit in `images/` next to `proposal.json` so the deck finds them.

## Workflow

Run the steps in order. When the user only asks for ideas first, stop after step 4 and present the ideas; build the proposal after they pick (or, if unattended, with the recommended combination).

1. **Read the brief.** Extract: brand, objective, audience, time, locations, budget, KPI, constraints, mandatory elements (mascot, ambassador, product). If there is no brief, research the brand (step 2) and write an assumed brief, marking every assumption with `[ ]`. Use the `proposal-brief` checklist in `references/proposal-outline.md` → "Brief còn thiếu gì" to list questions for the client; these become a slide, never block the work.
2. **Research.** WebSearch/WebFetch: brand's recent campaigns, store count, positioning, mascot usage, competitor activations; then world event tech (see `references/event-tech-library.md`, refresh with 3–5 searches for the current year). Keep every number with its source and date; unsourced numbers do not go in the deck.
3. **Ideate.** 4–6 ideas, each: name, one-line mechanic, tech, why it fits the insight. Include at least one idea built on IFAGENT (see `references/ifagent-capabilities.md`) when a talking character, kiosk, remote control or live dashboard helps. Never claim an IFAGENT feature that is not in that file.
4. **Score and choose.** Score 1–5 on brand fit, participation, data capture, cost, ease of ops (`references/proposal-outline.md` → scoring). Recommend a combined journey (big idea) plus optional add-ons per budget. Write `01-phan-tich-y-tuong.md`.
5. **Specify the experience.** For the big idea write: how it works (5–7 steps), player journey table (step, duration, guest action, system action, data captured), every screen (purpose, content, interactions, rules), operator screens (control, dashboard), technical architecture, floor plan, equipment list.
6. **Mockups.** Write `mockups.json` (layouts in `references/json-schema.md`) and run:
   `python3 scripts/render_mockups.py <project_dir>` → PNGs in `images/`. Placeholder key visuals use layout `keyvisual`.
6b. **Showcase mockups.** Add `showcase` entries (UI screens in kiosk/tablet/LED frames over an on-brand photo) and use them on `full` slides; these are the pretty presentation mockups.
7. **Image prompts.** Write `image-prompts.md` following `references/image-prompting.md`. If Claude in Chrome is connected, generate the photos in the user's ChatGPT (workflow in that file) and save them into `images/` — do not leave the deck with placeholder key visuals. Mascot = official client file only, composited via `mascot_image`.
8. **Deck.** Write `proposal.json` following the standard outline in `references/proposal-outline.md` (cover → executive summary → brief → analysis → questions → trends → case studies → ideas → scoring → big idea → how it works → journey → screens → operator screens → tech → floor plan → equipment → ops → KPI → timeline → budget packages → risks → legal/data → why us → sources → next steps). Then run:
   `python3 scripts/build_deck.py <project_dir>`.
9. **Verify.** Convert to PDF (`soffice --headless --convert-to pdf`), rasterise (`pdftoppm -r 55 -png`), look at every slide: no overlapping text, no cropped headline, no missing-image boxes except intended ones, numbers match sources. Fix JSON and rebuild.
10. **Deliver.** Save the whole project folder to the user's folder (commit each file; images included). Tell the user which images are placeholders and which prompt makes each.

## Rules

- **Replaceable by design.** All wording lives in `proposal.json`; all visuals are referenced by stem. Never hard-code content in the scripts. To re-skin for another client: copy the folder, change `theme`, `meta`, texts, and images.
- **Images keep their stem.** When the user saves a ChatGPT/Flow image as `images/<stem>.jpg`, the newest file for that stem wins. `render_mockups.py` skips a stem when a newer non-PNG exists or the stem is listed in `images/.locked`; pass `--force` to overwrite.
- **Brand IP.** Do not draw a client's mascot or logo. Mockups use the dashed "MASCOT" placeholder; prompts tell the user to upload the official asset as reference. Do not use a celebrity's likeness or cloned voice without a contract – list it as a question instead.
- **Numbers.** Budgets and targets the client has not given stay as `[ ]`. Capacity numbers may be derived (duration per turn × hours) and must show the formula.
- **Always add the parts briefs forget:** KPI and measurement, operations and staffing, timeline with approvals, budget packages, risks with fallback (noise, network, queue, AI error, brand error, stock-out), personal-data and child-safety compliance, promotion law, sources, next steps.
- Write for the client in Vietnamese unless the brief is in another language. Short sentences, concrete nouns, no hype words.

## Rebuilding after edits

When the user says "build lại", "đã thay ảnh", "sửa slide …": stage the changed files from their folder (or edit in place), edit `proposal.json`/`mockups.json` if needed, re-run step 6 only for changed stems (`--only=a,b`), re-run step 8, verify, commit the new `.pptx` and `-noi-dung.md` back.

## Files in this skill

- `scripts/build_deck.py` – JSON → PPTX (slide types: cover, section, bullets, cards, steps, screens, visual, table, bigidea, closing).
- `scripts/render_mockups.py` – JSON → PNG (layouts: attract, chat, menu, game, quiz, photo, reward, leaderboard, dashboard, control, diagram, floorplan, keyvisual).
- `references/proposal-outline.md` – standard section list, brief checklist, scoring.
- `references/json-schema.md` – fields for every slide type and mockup layout.
- `references/ifagent-capabilities.md` – what IFAGENT can truthfully offer.
- `references/event-tech-library.md` – event technology catalogue with sources.
- `references/image-prompting.md` – ChatGPT Plus / Google Flow prompt rules and naming.
- `examples/jollibee-2026/` – complete worked example (brief, JSON, prompts).
