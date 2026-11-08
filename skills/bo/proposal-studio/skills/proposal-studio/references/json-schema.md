# JSON formats

## proposal.json

```json
{
  "meta": {"title": "...", "client": "...", "file": "Client-Project-Proposal", "footer": "...", "version": "v0.1"},
  "theme": {"primary": "#D7141A", "secondary": "#FFC20E", "dark": "#5A0B0E", "text": "#2A1A12",
            "bg": "#FFF8EC", "light": "#FFF1D6", "muted": "#6B5A4E", "line": "#EAD9C0",
            "font_head": "Segoe UI", "font_body": "Segoe UI"},
  "slides": [ { "type": "...", ... } ]
}
```
Every slide accepts `notes` (speaker notes) and `hidden: true` (skip). `kicker` = small label above the title. `image` = stem in `images/`.

| type | fields |
|---|---|
| cover | image, kicker, title, subtitle, meta |
| section | number, title, subtitle, image |
| bullets | kicker, title, lead, bullets[], image?, mode (cover/contain), size |
| cards | kicker, title, lead?, cols, size, title_size, cards[{title, text, tag?, image?}] |
| steps | kicker, title, steps[{title, text}], note?, image? |
| screens | kicker, title, screens[{image, tag, title, points[], portrait (default true)}] — 2–3 per slide |
| visual | kicker, title, image, bullets[], mode (default contain) |
| table | kicker, title, lead?, columns[], rows[][], col_widths[], size, note?, bold_first |
| bigidea | image, kicker, title, text |
| closing | title, bullets[], contact, image? |
| full | image, title (for the text export), caption? — full-bleed image (showcase mockups, 3D renders) |

Keep titles ≤ 52 characters (longer titles shrink to 24pt). Cards: ≤ 6 per slide, text ≤ 220 characters. Table: ≤ 8 rows.

## mockups.json

```json
{"brand_name": "Brand · Project", "mascot_label": "MASCOT",
 "theme": {"primary": "#...", "secondary": "#...", "dark": "#...", "text": "#...", "bg": "#..."},
 "screens": [ {"id": "scr01_attract", "device": "kiosk", "layout": "attract", ...} ]}
```
`device` sets pixel size: kiosk 1080×1920, led 1920×1080, tablet 1600×1000, phone 750×1500, diagram 1920×1080, floorplan 1920×1200, keyvisual 1920×1080; or give `size: [w, h]`.
Kiosk layouts share `corner`, `footer_left`, `footer_right`.

| layout | fields |
|---|---|
| attract | kicker, headline, sub, cta |
| chat | messages[{who: ai/guest, text}], chips[], mic |
| menu | kicker, headline, options[{icon, label, sub}] (4) |
| game | timer, score, combo, prompt |
| quiz | kicker, question, answers[], correct (index) |
| photo | frame_title, countdown, sub |
| reward | kicker, headline, value, voucher, qr_note, consent, cta |
| leaderboard | kicker, headline, rows[[name, score]] |
| dashboard | title, corner, tiles[[label, value]], chart_title, bars[[label, number]], list_title, list[[a, b]] |
| control | title, corner, groups[{title, buttons[]}] |
| diagram | kicker, title, columns[{title, nodes[{title, text}]}], note |
| floorplan | kicker, title, dims, zones[{x, y, w, h (percent), label, text, strong?, color?}] |
| keyvisual | prompt_ref, label? — placeholder for an AI image, no headline |
| showcase | device "showcase"; bg (photo stem), kicker, title, items[{image, device kiosk/tablet/led, label, w}], gap, bottom — real UI screens in device frames over an on-brand photo |

Top-level `mascot_image` (e.g. `mascot/ong-bee-idle.png`, path relative to the project): when the file exists, every mascot slot renders the client's official file instead of the placeholder.

Name stems by role: `kv_hero`, `idea_0N_<slug>`, `scr0N_<slug>`, `tech_architecture`, `booth_layout`.
