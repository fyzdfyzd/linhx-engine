# IFAGENT – capabilities that may be offered in proposals

Source: Live Character codebase (event.ifagent.net). Offer only what is listed; anything else is "phát triển thêm" with its own line in the budget.

## Live Character (talking character on a kiosk)
- Virtual character speaking Vietnamese in real time (Gemini Live), on vertical 1080×1920 or horizontal 16:9 kiosks.
- Video/image gesture matrix from the client's official assets (idle, talk, wave, heart…); the AI can change emotion/pose.
- Auto greeting when a guest arrives (on-device camera detection, no images sent to the server).
- No microphone or too noisy → automatic text chat on screen.
- Knowledge base (RAG) from approved documents only (.docx/.txt/.md): menu, FAQ, promotions; answers "lookup_info" on the server.
- AI tools: `set_emotion`, `show_widget`, `hide_widget`, `get_data`, `open_lead_form`.
- Overlay widgets (13 types: stat, line, bar, cta, …) shown on schedule, by rule, by AI, or manually.

## Operations
- Studio: create/edit characters, kiosks, overlay scenes, data sources (login).
- Control page (`/control.html`): MC/staff remote-controls pose, scene, spoken line (`say`), session start/end, reload, switch to chat — per kiosk, over SSE.
- Versioned releases: kiosks run the approved version; previews run the draft.
- Automatic bulletins pushed to kiosks.
- Windows kiosk installer.

## Tracking
- Dashboard: kiosks online/offline alerts, audience funnel, per hour, conversation history.
- Insights: popular questions, unanswered questions, minutes and AI cost, AI weekly report.
- Viewer role (read-only tracking).

## Data & safety
- Secrets only on the server; browsers never call the AI directly; the server builds prompt, knowledge and tools.
- Public API never exposes prompts or knowledge.
- Conversation logs mask phone numbers, emails, long digit strings; deleted after N days.
- Lead form: mandatory consent, Vietnamese phone validation, monthly JSONL, masked for viewers.

## Onboarding
- 8-stage process with approval gates: intake → research → concept → knowledge → features → assets → integration → launch.

## Not built yet (quote as custom work)
Motion/dance game engine, photobooth + printing, QR stamp hunt, hologram hardware, voucher/CRM/Zalo integration, LED leaderboard feed. These are usually delivered by partners or custom development and integrated with IFAGENT via overlay/widgets and data sources.
