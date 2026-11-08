---
name: content-synthesizer
description: "Skill tổng hợp và chọn lọc nội dung theo persona tác giả. Trigger khi chạy bước 5-6 của pipeline hoặc khi cần nén dữ liệu nghiên cứu thành insights có chọn lọc. Tạo 05_Synthesis_Insights.md và 06_AI_Curated_List.json."
---

> Luật luôn bật: đọc `${CLAUDE_PLUGIN_ROOT}/references/goc/rules/` trước khi chạy (bản Antigravity gốc để ở `.agent/rules/`, Always On). Prompt gốc ở `${CLAUDE_PLUGIN_ROOT}/references/goc/prompts/`.


# Content Synthesizer — Bước 5 & 6

## Mục đích
Nén dữ liệu thô thành insights, sau đó tạo **3 phương án triển khai khác nhau** từ cùng một bộ insights.

## Quy trình

### Bước 5: Analyst Agent
Input: `04_Raw_Research_Data.json`

Nén toàn bộ dữ liệu thành **30 Insights**:
- Mỗi insight = 1-2 câu, chứa 1 "tứ" rõ ràng
- Phân loại: `fact`, `paradox`, `metaphor`, `provocation`
- Format: Markdown bullet points

Lưu `05_Synthesis_Insights.md`

### Bước 6: AI Curation — 3 VARIANTS
**QUAN TRỌNG**: Đây là bước tạo **3 hướng triển khai khác biệt** từ cùng 30 insights.

Đóng vai **Đinh Trần Tuấn Linh** — đọc 30 insights và tạo **3 phương án** (A, B, C):

#### Nguyên tắc tách biệt 3 phương án
Mỗi variant PHẢI khác nhau ở **ít nhất 2 trong 3 yếu tố**:

| Yếu tố | Ví dụ |
|:---|:---|
| **Góc nhìn** | Triết học vs. Xã hội học vs. Cá nhân hóa |
| **Tone** | Mỉa mai cay đắng vs. Buồn lặng lẽ vs. Giận dữ lạnh |
| **Cấu trúc** | Tuyến tính vs. Lồng ghép vs. Đối lập A/B |

#### Cho mỗi variant (A, B, C):

1. **SÀNG LỌC**: Chọn **10-12 ý** — mỗi variant chọn **tập ý khác nhau**
   - Cho phép overlap tối đa **3 ý** giữa các variant
   - Ưu tiên ý tạo nghịch lý, gây khó chịu, phản trực giác

2. **SÁNG TẠO**: Viết **2-3 Personal Anecdotes** riêng cho mỗi variant
   - Phải cụ thể: địa điểm, thời gian, chi tiết cảm giác
   - Anecdotes phải phù hợp với góc nhìn của variant đó

3. **SẮP XẾP**: Gợi ý narrative arc riêng cho mỗi variant

#### Output — 3 files riêng biệt:
- `Variant_A/06_AI_Curated_List.json`
- `Variant_B/06_AI_Curated_List.json`
- `Variant_C/06_AI_Curated_List.json`

Mỗi file theo format:
```json
{
  "variant": "A",
  "variant_angle": "Mô tả ngắn góc nhìn của variant này",
  "variant_tone": "Mô tả tone riêng",
  "selected_insights": [
    {"id": 1, "content": "...", "type": "paradox", "note": "dùng làm mở bài"}
  ],
  "personal_anecdotes": [
    {"content": "...", "placement_hint": "giữa bài, khi nói về..."}
  ],
  "suggested_flow": ["opening_paradox", "anecdote_1", "philosophical_depth", "..."],
  "rejected_insights": [3, 7, 15],
  "rejection_reasons": "Quá hiển nhiên cho góc nhìn này"
}
```

### Logging Protocol (xem chi tiết: `agent-logging.md`)
1. **Sau Bước 5**: Log entry cho Analyst (30 insights → phân bố type)
2. **Sau Bước 6**: Log entry cho 3 variants (overlap count, điểm khác biệt)
3. **Lessons Learned**: Ghi vào `_lessons_learned.md`:
   - 3 variant có thực sự khác biệt không? Overlap quá nhiều?
   - Variant nào có tiềm năng nhất (cảm tính)?
   - Rejected insights có pattern gì chung giữa 3 variant?
4. **Cập nhật**: `_status.json` → `current_step: 7`

## Lưu ý
- Persona phải nhất quán với `writing-identity.md`
- Anecdotes phải tự nhiên, không gượng ép
- 3 variant KHÔNG PHẢI copy-paste + sửa nhẹ — phải có góc nhìn thực sự khác
