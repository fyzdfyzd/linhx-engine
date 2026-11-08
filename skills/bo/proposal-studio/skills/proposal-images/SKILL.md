---
name: proposal-images
description: Writes the image prompt pack for a proposal (ChatGPT Plus / Google Flow), swaps generated images into the project folder by filename and rebuilds the deck. Use when the user says "viết prompt ảnh", "tạo ảnh cho proposal", "đã tạo ảnh xong", "thay ảnh", "build lại proposal", "ảnh đã lưu vào folder".
---

# Proposal images

Rules and prompt format: `${CLAUDE_PLUGIN_ROOT}/skills/proposal-studio/references/image-prompting.md`.

## Write prompts
1. Read `proposal.json` and `mockups.json`; list every image stem used by slides.
2. For stems that should be AI images (key visual, idea images, booth render), write prompt blocks into `image-prompts.md`. Keep UI screens, diagrams and floor plans as rendered mockups.
3. Tell the user: upload the official mascot as reference, generate, save into `images/` as `<stem>.<ext>`.

## Swap and rebuild
1. Get the new files: list the user's `images/` folder, stage only files newer than the last build.
2. Put them in the project `images/` (same stem; any of png/jpg/webp). Add stems the user made to `images/.locked`.
3. Run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/proposal-studio/scripts/build_deck.py <project_dir>`.
4. Render to PDF and check the slides that use the new images (cropping on cover/section slides: the left ~55% is covered by text panels; subjects should sit on the right).
5. Save the new `.pptx` and `-noi-dung.md` back into the user's folder next to `images/`.
