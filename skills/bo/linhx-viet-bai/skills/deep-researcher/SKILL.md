---
name: deep-researcher
description: "Skill nghiên cứu chuyên sâu cho bài viết. Trigger khi chạy bước 3-4 của pipeline hoặc khi cần tìm kiếm dữ liệu, số liệu, trích dẫn triết học cho một chủ đề. Tạo 03_Research_Plan.md và 04_Raw_Research_Data.json."
---

> Luật luôn bật: đọc `${CLAUDE_PLUGIN_ROOT}/references/goc/rules/` trước khi chạy (bản Antigravity gốc để ở `.agent/rules/`, Always On). Prompt gốc ở `${CLAUDE_PLUGIN_ROOT}/references/goc/prompts/`.


# Deep Researcher — Bước 3 & 4

## Mục đích
Chuyển đổi context expansion thành kế hoạch nghiên cứu và thực thi thu thập dữ liệu.

## Quy trình

### Bước 3: Research Plan (Architect Agent)
Input: `02_Context_Expansion.json` — ưu tiên các mục có `priority: true`

1. Extract **keywords** từ 3 priority insights
2. Tạo 3 nhóm tìm kiếm:
   - **Triết học**: Tìm quan điểm của Byung-Chul Han, Bauman, Barthes liên quan
   - **Số liệu**: Tìm statistics, surveys, research papers
   - **Case study**: Tìm câu chuyện thực tế, sự kiện minh họa

Lưu `03_Research_Plan.md` — danh sách keywords + questions.

### Bước 4: Scout (Research Execution)
Input: `03_Research_Plan.md`

Sử dụng công cụ tìm kiếm (web search) để thu thập:
- Số liệu cụ thể (năm, %, con số)
- Quan điểm triết học có nguồn
- Case study thực tế
- Trích dẫn nguyên văn

**Output format bắt buộc** — `04_Raw_Research_Data.json`:
```json
[
  {
    "source": "URL hoặc tên sách",
    "type": "stat|quote|theory|case_study",
    "content": "nội dung trích xuất",
    "relevance": "ghi chú ngắn về độ liên quan"
  }
]
```

**Target**: Thu thập tối thiểu **15 items** đa dạng type.

### Logging Protocol (xem chi tiết: `agent-logging.md`)
1. **Trước khi bắt đầu**: Ghi timestamp bắt đầu vào `_agent_log.md` + `_timelog.json`
2. **Sau Bước 3**: Log entry cho Research Plan (số keywords, nhóm tìm kiếm)
3. **Sau Bước 4**: Log entry cho Scout (số items thu thập, phân bố type)
4. **Lessons Learned**: Ghi vào `_lessons_learned.md`:
   - Nguồn nào cho chất lượng tốt nhất?
   - Keywords nào hiệu quả, keywords nào trả về noise?
   - Có gap nào trong data không? (thiếu stat? thiếu quote?)
   - Gợi ý keywords tốt hơn cho lần sau
5. **Cập nhật**: `_status.json` → `current_step: 5`, `_timelog.json` → tổng duration

## Lưu ý
- Ưu tiên nguồn uy tín (academic, sách, báo chính thống)
- Giữ nguyên ngôn ngữ gốc cho trích dẫn triết học
- Nếu web search không khả dụng, sử dụng LLM knowledge với disclaimer
