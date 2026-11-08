---
name: resume-article
description: "Tiếp tục viết bài dở dang từ checkpoint. Hỗ trợ --variant flag để chạy 1 variant cụ thể (dùng cho parallel execution)."
---

> Luật luôn bật: đọc `${CLAUDE_PLUGIN_ROOT}/references/goc/rules/` trước khi chạy (bản Antigravity gốc để ở `.agent/rules/`, Always On). Prompt gốc ở `${CLAUDE_PLUGIN_ROOT}/references/goc/prompts/`.


# /resume-article — Tiếp Tục Bài Dở Dang

## Cách dùng
```
/resume-article Idea_20260207_0800_Co_Don_Ket_Noi
/resume-article Idea_20260207_0800_Co_Don_Ket_Noi --variant A
```

Hoặc không kèm tên → agent sẽ list tất cả folder `Idea_*/` và hỏi user chọn.

## Quy trình

### 1. Tìm project
- Nếu user cung cấp tên folder → mở trực tiếp
- Nếu không → `list_dir` workspace, liệt kê tất cả `Idea_*/`
- Hiển thị danh sách kèm `current_step` từ `_status.json`

### 2. Đọc trạng thái
- Đọc `_status.json` trong folder project
- Xác định `current_step` + trạng thái từng variant (A, B, C)
- Verify: tất cả file của bước trước phải tồn tại

### 3. Chạy tiếp
// turbo
- Nếu `current_step` ≤ 5 → chạy tiếp pipeline chung (chưa tới variant)
- Nếu `current_step` ≥ 6 và có `--variant X`:
  - Chỉ chạy Variant X (dùng cho parallel: mỗi conv 1 variant)
  - Đọc `Variant_X/06_AI_Curated_List.json` → chạy critic-loop-writer
- Nếu `current_step` ≥ 6 và KHÔNG có `--variant`:
  - Kiểm tra variant nào chưa xong → chạy tiếp variant đó
  - Nếu cả 3 variant xong → tạo `_best_pick.md`
- Nếu `current_step` = 10 → thông báo bài đã hoàn thành

### 4. Báo cáo kết quả
- Hiển thị bảng so sánh 3 variant (score, word count)
- Đề xuất bản tốt nhất từ `_best_pick.md`
