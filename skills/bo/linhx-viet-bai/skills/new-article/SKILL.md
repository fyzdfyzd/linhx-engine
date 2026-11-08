---
name: new-article
description: "Viết bài mới theo quy trình LinhX Write 9 bước của Linh (FLOW v FM): gieo ý → 11 câu hỏi Deep Inquiry → nghiên cứu → 30 tứ → 3 phương án A/B/C → viết → phản biện 2 tầng (AI Detector + Editorial QA) → chọn bản tốt nhất. Dùng khi Linh nói /new-article, \"viết bài về…\", hoặc đưa một ý tưởng thô cần thành bài."
---

# /new-article: LinhX Write 9 bước

Đây là quy trình gốc của Linh ở `D:\@WF\TOOL\00_WRITING` (Antigravity, 02/2026), chuyển nguyên sang plugin. Đặc tả gốc: `${CLAUDE_PLUGIN_ROOT}/references/goc/spec.md`. Bản dùng cho CafeBiz (AI Opinion) nằm ở `D:\@WF\OPERATION\CONTENT_MARKETING_OS\hubs\AI4Biz_Cafebiz\EDITOR_RULE\Workflow\03_workflow_y_kien_chuyen_gia.md`.

## Luật luôn bật (đọc trước khi chạy)

Trong Antigravity đây là rules Always On. Đọc hết `${CLAUDE_PLUGIN_ROOT}/references/goc/rules/`:
- `writing-identity.md`: persona Đinh Trần Tuấn Linh (lạnh, mỉa mai, triết luận, nghịch lý; cấm self-help, cấm kết bài học, cấm emoji, cấm CTA)
- `quality-standards.md`: 3 phương án, độ dài, rubric 10 điểm, ≥9 mới xuất
- `project-structure.md`, `state-preservation.md`, `context-isolation.md`, `agent-logging.md`

## Cách dùng

```
/new-article Sự cô đơn trong thời đại luôn kết nối
```

## Bước 1 (người duy nhất phải làm): Gieo mầm

Tạo `Idea_{YYYYMMDD_HHmm}_{Slug}/01_Seed_Input.json`. Ý tưởng càng dày thì bài càng ra giọng Linh. Mẫu tốt nhất là lượt "Cập nhật phiên bản" (`${CLAUDE_PLUGIN_ROOT}/references/vi-du/Idea_20260409_2215_Cap_Nhat_Phien_Ban_V2/01_Seed_Input.json`):

```json
{
  "idea": "ý tưởng thô, có hình ảnh mở đầu, mạch ý, các cú hài đen Linh đã nghĩ sẵn",
  "author_angle": "DARK_HUMOR × DIGITAL_SOCIETY × PSYCHOLOGY_LOVE",
  "tone": "Hài đen, tự giễu, u ám mở đầu, Byung-Chul Han + Lê Bích style",
  "constraints": ["Mở đầu với hình ảnh…", "Flow: … → …", "Nhiều story/anecdote cá nhân"],
  "timestamp": "ISO 8601"
}
```

Nếu Linh chỉ đưa một câu, vẫn chạy (đặc tả gốc cho phép), nhưng hỏi thêm một lần: "có hình ảnh mở đầu hay cú hài nào đã nghĩ sẵn không?".

## Bước 2–9

| Bước | Skill | Ra file |
|:---:|:---|:---|
| 1–2 | `idea-seeder` | `01_Seed_Input.json`, `02_Context_Expansion.json` (11 câu, 3 câu `priority`) |
| 3–4 | `deep-researcher` | `03_Research_Plan.md`, `04_Raw_Research_Data.json` (≥15 mục) |
| 5–6 | `content-synthesizer` | `05_Synthesis_Insights.md` (30 tứ), `Variant_A|B|C/06_AI_Curated_List.json` |
| 7–9 | `critic-loop-writer` + `gemini-reviewer` | `Variant_X/07_The_Critic_Loop/Loop_XX/`, `Variant_X/08_Final_Output.md` |
| 10 | `critic-loop-writer` | `_best_pick.md` |

Chạy tự động từ đầu đến cuối, không chờ Linh ở giữa (nguyên tắc Automation First). Ghi log theo `agent-logging.md`; dừng giữa chừng thì `/resume-article`.

Vòng phản biện bước 8 dùng module ngoài: `python D:\@WF\TOOL\00_WRITING\.agent\scripts\gemini-reviewer\reviewer.py review <draft> --stage ai-detector`, rồi `--stage editorial-qa`. Writer không được tự chấm bài mình. Nếu không gọi được Gemini (không ở máy Linh, hết key), dùng một subagent độc lập đọc đúng prompt gốc `${CLAUDE_PLUGIN_ROOT}/references/goc/prompts/ai_detector_system.md` và `critic_system.md`, và ghi rõ trong `_best_pick.md` là đã duyệt bằng subagent.

## Bổ sung của LAB025 (ngoài bản gốc, đánh dấu để Linh bỏ nếu không muốn)

1. **Đánh dấu chuyện giả lập.** Bước 6 gốc dặn tự viết 2–3 "Personal Anecdotes" giả lập. Giữ nguyên, nhưng trong bài mỗi chuyện giả lập kết thúc bằng `[GIẢ LẬP]` để Linh biết chỗ nào cần thay bằng chuyện thật trước khi gửi báo. Con số và trích dẫn thì không được giả lập: phải có nguồn trong `04_Raw_Research_Data.json`.
2. **Checklist 12 điểm của Linh.** Sau Stage 8b, đối chiếu bản cuối với `${CLAUDE_PLUGIN_ROOT}/references/EDITORIAL_CHECKLIST.md` (Linh rút ra khi tự sửa bài "Cập nhật phiên bản"; bản Linh sửa: `references/vi-du/BAN-LINH-SUA-cap-nhat-phien-ban.md`). Ghi kết quả vào `_best_pick.md`.
3. **Độ dài theo kênh.** Gốc là ≥3.500 chữ mỗi phương án. Nếu `constraints` ghi độ dài (ví dụ "Bloomberg 1.500 chữ"), theo `constraints`.
