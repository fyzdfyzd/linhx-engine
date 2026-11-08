# Image prompts for ChatGPT Plus / Google Flow

## File naming (the contract with the deck)
- One stem per image, same as in `proposal.json` / `mockups.json` (e.g. `kv_hero`, `idea_02_dance`).
- User saves the generated file into `images/` as `<stem>.png|.jpg|.webp`. Newest wins; the deck picks it up on rebuild.
- To stop the mockup renderer overwriting a PNG the user made, add the stem to `images/.locked` (one per line/space).

## Prompt block format in image-prompts.md
```
## <PROMPT-ID> · `<stem>` · <ratio> · <where it is used>
Công cụ: ChatGPT Plus | Google Flow
<prompt in English, 60–120 words>
```
Add at the top: how to use (upload reference, ratio, rename, rebuild) and a shared suffix.

## Writing the prompt
1. Scene first: place, time, season, who (age, number), what they are doing.
2. The hero object: kiosk / LED / photobooth with its size.
3. The character: "the uploaded mascot" – never describe a trademarked character's look; the reference image carries it.
4. Brand colours as hex; lighting; camera/style ("photorealistic commercial", "3D isometric render").
5. Composition: where to leave empty space for headline text (e.g. "left third kept clean").
6. Ratio: 16:9 for slides, 9:16 for kiosk screens, 1:1 for social.
7. Shared suffix: keep mascot exact, no extra text, no real celebrity likeness.

## Which images to generate
- Always: cover/key visual, one per idea, booth 3D render (optional replacement for the floor plan).
- Keep generated-by-script: UI screens, diagram, floor plan (they must match the real product). Better replacement: screenshots from the real IFAGENT demo.
- Optional: 8-second Google Flow (Veo) clips for a demo reel – not placed in the deck automatically.

## Brand and IP rules
- Only the client's official mascot/logo files as references, only for that client's proposal.
- No celebrity or ambassador faces/voices unless the client confirms rights.
- Do not generate fake testimonials, fake press or invented results.

## Generating in the user's ChatGPT (Claude in Chrome) — proven workflow
1. Open chatgpt.com in a new tab (user must already be signed in; never sign in for them). One chat per project; first message sets style + palette, later messages say "Next image, same style, 16:9 …".
2. Each prompt: scene, people, brand hex colours, empty screens/frames/spots where the mascot will be composited, and "No readable text, no logo, no mascot or cartoon character".
3. Wait ~90–120 s; if "Image generation failed", click Try again.
4. Save: run in the page a small script that fetches the largest displayed image blob and triggers a download named `<prefix>_<stem>.png` (goes to the user's Downloads). Ask once for access to the Downloads folder, stage the files, copy to `images/<stem>.png`, add the stem to `images/.locked`.
5. Rebuild showcases (`render_mockups.py --only=show_…`) and the deck.
Never ask the image tool to draw a client's mascot, logo or a real person from web references; composite the official files instead (`mascot_image`).
