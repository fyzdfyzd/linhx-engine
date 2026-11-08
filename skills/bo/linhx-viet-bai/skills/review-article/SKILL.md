---
name: review-article
description: "Chạy lại vòng Critic Loop 2-stage (AI Detector + Editorial QA) trên bài viết đã có. Hỗ trợ chọn variant cụ thể hoặc review toàn bộ."
---

> Luật luôn bật: đọc `${CLAUDE_PLUGIN_ROOT}/references/goc/rules/` trước khi chạy (bản Antigravity gốc để ở `.agent/rules/`, Always On). Prompt gốc ở `${CLAUDE_PLUGIN_ROOT}/references/goc/prompts/`.


# /review-article — Chạy Lại Critic Loop (2-Stage)

## Cách dùng
```
/review-article Idea_20260207_0800_Co_Don_Ket_Noi --variant A
/review-article Idea_20260207_0800_Co_Don_Ket_Noi --all
```

Nếu không chỉ định variant → hỏi user chọn variant nào hoặc chạy cả 3.

## Quy trình

### 1. Verify project
- Mở folder project
- Kiểm tra `Variant_X/06_AI_Curated_List.json` tồn tại
- Kiểm tra `Variant_X/08_Final_Output.md` hoặc draft cuối cùng tồn tại

### 2. Lưu backup
- Nếu `Variant_X/08_Final_Output.md` tồn tại → rename thành `08_Final_Output_backup_{timestamp}.md`
- Nếu `Variant_X/07_The_Critic_Loop/` có data → tạo subfolder mới (Loop_04, Loop_05...)

### 3. Stage 1 — AI Detector Loop (MODULE NGOÀI)
// turbo
- Gọi `run_command`:
  ```
  python D:\@WF\TOOL\00_WRITING\.agent\scripts\gemini-reviewer\reviewer.py review "Variant_X/07_The_Critic_Loop/Loop_XX/draft.md" --stage ai-detector
  ```
- Đọc `ai_detector_feedback.json`
- Nếu verdict = `AI_DETECTED`:
  - Writer Agent (Antigravity) rewrite dựa trên feedback, theo `prompts/ai_detector_rewrite.md`
  - Chỉ sửa cách diễn đạt, không thay đổi nội dung
  - Scan lại (tối đa 3 vòng)
- Nếu verdict = `CLEAN` → chuyển sang Stage 2
- Nếu CLI fail → thử lại với `--force-fallback`:
  ```
  python D:\@WF\TOOL\00_WRITING\.agent\scripts\gemini-reviewer\reviewer.py review --force-fallback "draft.md" --stage ai-detector
  ```

### 4. Stage 2 — Editorial QA Loop (MODULE NGOÀI)
// turbo
- Gọi `run_command`:
  ```
  python D:\@WF\TOOL\00_WRITING\.agent\scripts\gemini-reviewer\reviewer.py review "Variant_X/07_The_Critic_Loop/Loop_XX/draft.md" --stage editorial-qa
  ```
- Đọc `editorial_feedback.json`
- Nếu verdict = `REVISE` hoặc `MAJOR_REVISE`:
  - Writer Agent (Antigravity) rewrite dựa trên feedback, theo `prompts/rewrite_instruction.md`
  - Lặp tối đa 3 vòng
- Nếu verdict = `PUBLISH` → hoàn thành
- Nếu CLI fail → thử lại với `--force-fallback`
- **Chỉ đọc files trong Variant_X/** — không tham khảo variant khác

### 5. Xuất kết quả
- Lưu bản tốt nhất vào `Variant_X/08_Final_Output.md` (mới)
- Cập nhật `_status.json` → `variants.X.editorial_score` + `variants.X.ai_clean`
- Nếu `--all`: sau khi review cả 3, cập nhật lại `_best_pick.md`
- Thông báo: so sánh điểm cũ vs mới per variant, tình trạng AI clean
