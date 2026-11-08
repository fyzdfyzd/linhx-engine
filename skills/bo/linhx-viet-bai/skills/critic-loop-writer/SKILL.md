---
name: critic-loop-writer
description: "Skill viết và cải thiện bài viết qua vòng lặp Writer-Critic 2 giai đoạn. Trigger khi chạy bước 7-8-9 của pipeline hoặc khi cần viết/rewrite một bài dựa trên curated list. Tạo drafts trong 07_The_Critic_Loop/ và 08_Final_Output.md."
---

> Luật luôn bật: đọc `${CLAUDE_PLUGIN_ROOT}/references/goc/rules/` trước khi chạy (bản Antigravity gốc để ở `.agent/rules/`, Always On). Prompt gốc ở `${CLAUDE_PLUGIN_ROOT}/references/goc/prompts/`.


# Critic Loop Writer — Bước 7, 8 & 9

## Mục đích
Viết bài hoàn chỉnh và cải thiện qua vòng lặp phản biện **2 giai đoạn**. **Chạy 3 lần** — 1 lần cho mỗi Variant (A, B, C).

> [!IMPORTANT]
> **Bước 8** sử dụng **module duyệt ngoài** (`gemini-reviewer`) với **2-stage pipeline**.
> Antigravity **KHÔNG ĐƯỢC** tự đóng vai Critic Agent hay AI Detector.
> Xem chi tiết: `.agent/skills/gemini-reviewer/SKILL.md`

## Quy trình

### Chạy tuần tự: Variant_A → Variant_B → Variant_C

Với mỗi variant:

### Bước 7: Writer Agent — Draft v1
Input: `Variant_X/06_AI_Curated_List.json`

Viết bài theo yêu cầu:
- **≥3500 từ**
- Tuân thủ `suggested_flow` từ curated list
- Đặt Personal Anecdotes vào vị trí gợi ý
- Giọng văn theo `variant_tone` + `writing-identity.md`

Lưu: `Variant_X/07_The_Critic_Loop/Loop_01/draft.md`

### Bước 8: 2-Stage Editorial Review (MODULE NGOÀI)

> **Pipeline mới**: AI Detector → Editorial QA, mỗi stage gọi Gemini độc lập.

#### Stage 8a: AI Detector Loop

**Mục đích**: Quét sạch pattern AI trong bản thảo.

1. Gọi Gemini (stage: `ai-detector`):
   ```powershell
   python D:\@WF\TOOL\00_WRITING\.agent\scripts\gemini-reviewer\reviewer.py review "<draft>" --stage ai-detector
   ```
2. Đọc `ai_detector_feedback.json`
3. Nếu verdict = `AI_DETECTED`:
   - Đọc feedback, rewrite theo `prompts/ai_detector_rewrite.md`
   - **Chỉ sửa CÁCH DIỄN ĐẠT, không thay đổi nội dung**
   - Scan lại
4. Nếu verdict = `CLEAN` → chuyển sang Stage 8b
5. **Tối đa 3 vòng**. Nếu sau 3 vòng vẫn AI_DETECTED → dùng bản ít lỗi nhất.

#### Stage 8b: Editorial QA Loop

**Mục đích**: Đánh giá chất lượng triển khai hành văn.

1. Gọi Gemini (stage: `editorial-qa`):
   ```powershell
   python D:\@WF\TOOL\00_WRITING\.agent\scripts\gemini-reviewer\reviewer.py review "<draft>" --stage editorial-qa
   ```
2. Đọc `editorial_feedback.json`
3. Nếu verdict = `REVISE` hoặc `MAJOR_REVISE`:
   - Đọc feedback, rewrite theo `prompts/rewrite_instruction.md`
   - Sửa theo weaknesses + breakdown
   - Review lại
4. Nếu verdict = `PUBLISH` → chuyển sang Bước 9
5. **Tối đa 3 vòng**. Nếu sau 3 vòng vẫn chưa đạt → chọn bản score cao nhất.

**Rubric** (chấm bởi Stage 8b, KHÔNG tự chấm):

| Tiêu chí | /Điểm |
|:---|:---:|
| Insight originality | /2 |
| Literary quality | /2 |
| Philosophical depth | /2 |
| Personal Anecdotes | /1 |
| Statistics + sources | /1 |
| Structure & rhythm | /1 |
| Haunting ending | /1 |

**Nếu score < 8**: Module ngoài trả feedback → Writer viết lại
**Nếu score ≥ 8**: Verdict = `"PUBLISH"`

Feedback lưu tại: `Variant_X/07_The_Critic_Loop/Loop_XX/`
- `ai_detector_feedback.json` (Stage 8a)
- `editorial_feedback.json` (Stage 8b)

### Vòng lặp tổng thể
```
Loop 1: Write → [AI Detector scan] → Fix AI → [AI Detector re-scan]
                → Clean → [Editorial QA] → Fix quality → [Editorial QA re-review]
Loop 2: Rewrite → [AI Detector] → [Editorial QA] → ...
Loop 3: Final attempt
```

**Tối đa 3 vòng lớn per variant**. Mỗi vòng lớn có tối đa 3 sub-loops mỗi stage.

### Bước 9: Final Output (per variant)
- Copy bản draft tốt nhất ra `Variant_X/08_Final_Output.md`
- Header bao gồm metadata:
```markdown
---
title: "Tiêu đề bài viết"
author: Đinh Trần Tuấn Linh
variant: "A|B|C"
variant_angle: "Mô tả góc nhìn"
date: YYYY-MM-DD
editorial_score: X/10
ai_clean: true|false
loops_completed: N
word_count: XXXX
reviewed_by: "gemini-reviewer 2-stage (external)"
---
```

### Bước 10: Best Pick — So sánh & Chọn bản tốt nhất
Sau khi hoàn thành cả 3 variant, tạo `_best_pick.md`:

```markdown
# Best Pick — So Sánh 3 Phương Án

## Bảng so sánh
| Tiêu chí | Variant A | Variant B | Variant C |
|:---|:---:|:---:|:---:|
| Góc nhìn | ... | ... | ... |
| AI Clean | ✅/❌ | ✅/❌ | ✅/❌ |
| Editorial Score | X/10 | X/10 | X/10 |
| Word Count | XXXX | XXXX | XXXX |
| Total Loops | N | N | N |
| Điểm mạnh | ... | ... | ... |
| Điểm yếu | ... | ... | ... |

## Đề xuất
**Bản tốt nhất**: Variant X
**Lý do**: ...
```

### Logging Protocol (xem chi tiết: `agent-logging.md`)
1. **Sau mỗi Draft**: Log entry (variant, word count)
2. **Sau mỗi AI Detector**: Log entry (variant, verdict, issues_count, reviewer: "ai-detector")
3. **Sau mỗi Editorial QA**: Log entry (variant, score, verdict, reviewer: "editorial-qa")
4. **Lessons Learned** (ghi sau MỖI variant hoàn thành)
5. **Final Lessons** (sau `_best_pick.md`)
6. **Cập nhật**: `_status.json` → `current_step: 10` (done)

## Writer Prompt Template
```
ROLE: Bạn là Đinh Trần Tuấn Linh.
INPUT: Đọc Variant_X/06_AI_Curated_List.json.
VARIANT: {variant_angle} — {variant_tone}
TASK: Viết một bài dài (≥3500 từ) theo góc nhìn và tone của variant này.
REQUIREMENTS:
- Mở bài bằng paradox
- Xen kẽ Personal Anecdotes tự nhiên
- Kết bài gây ám ảnh (không kết luận tích cực)
- Trích dẫn triết gia giữ nguyên ngữ
```

## Critic — ĐÃ CHUYỂN RA MODULE NGOÀI (2-STAGE)
```
⚠️ KHÔNG SỬ DỤNG PROMPT NÀY TRONG ANTIGRAVITY
2-Stage pipeline chạy qua:
  Stage 1: python .agent/scripts/gemini-reviewer/reviewer.py review <draft> --stage ai-detector
  Stage 2: python .agent/scripts/gemini-reviewer/reviewer.py review <draft> --stage editorial-qa
  Both:    python .agent/scripts/gemini-reviewer/reviewer.py full-editorial <draft>
```
