---
name: idea-seeder
description: "Skill gieo mầm ý tưởng bài viết. Trigger khi user nhập một ý tưởng thô (seed idea) hoặc khi chạy bước 1-2 của pipeline viết bài. Tạo 01_Seed_Input.json và 02_Context_Expansion.json."
---

> Luật luôn bật: đọc `${CLAUDE_PLUGIN_ROOT}/references/goc/rules/` trước khi chạy (bản Antigravity gốc để ở `.agent/rules/`, Always On). Prompt gốc ở `${CLAUDE_PLUGIN_ROOT}/references/goc/prompts/`.


# Idea Seeder — Bước 1 & 2

## Mục đích
Nhận ý tưởng thô từ user, mở rộng thành bản đồ tư duy đa chiều.

## Quy trình

### Bước 1: Seed Input
1. Nhận ý tưởng từ user (1 câu)
2. Tạo folder `Idea_{YYYYMMDD_HHmm}_{Slug}/`
3. Lưu `01_Seed_Input.json`:
```json
{
  "idea": "câu ý tưởng gốc",
  "timestamp": "ISO 8601",
  "slug": "Slug_Name"
}
```

### Bước 2: Context Expansion (Cynical Observer)
Đóng vai **nhà quan sát xã hội sắc sảo** và tự trả lời 11 câu hỏi Deep Inquiry:

1. Paradox ẩn trong ý tưởng này là gì?
2. Ai hưởng lợi từ niềm tin này? Ai bị thiệt?
3. Điều ngược lại có đúng không?
4. Hiện tượng này 100 năm trước trông như thế nào?
5. Nếu đây là triệu chứng, bệnh gốc là gì?
6. Công nghệ đã thay đổi hiện tượng này ra sao?
7. Dữ liệu nào chứng minh? Dữ liệu nào phản bác?
8. Ai đã viết hay nhất về chủ đề này?
9. Mối liên hệ với xã hội tiêu dùng?
10. Câu chuyện cá nhân nào minh họa tốt nhất?
11. Nếu viết 1 cuốn sách về này, chương 1 là gì?

**QUAN TRỌNG**: Tự đánh giá và đánh dấu `"priority": true` cho **3 câu trả lời đột phá nhất**.

Lưu `02_Context_Expansion.json`.

### Logging Protocol (xem chi tiết: `agent-logging.md`)
1. **Trước khi bắt đầu**: Ghi timestamp bắt đầu vào `_agent_log.md` + `_timelog.json`
2. **Sau Bước 1**: Log entry cho Seed Input (thời gian, kết quả)
3. **Sau Bước 2**: Log entry cho Context Expansion (thời gian, số priority items)
4. **Lessons Learned**: Ghi vào `_lessons_learned.md`:
   - Ý tưởng có đủ "góc cạnh" để phát triển không?
   - 3 priority insights có thực sự đột phá không?
   - Gợi ý cải thiện cho lần gieo mầm sau
5. **Cập nhật**: `_status.json` → `current_step: 3`, `_timelog.json` → tổng duration

## Lưu ý
- Không chờ user confirm từng câu hỏi — chạy tự động
- Giọng trả lời phải cynical, không trung lập
