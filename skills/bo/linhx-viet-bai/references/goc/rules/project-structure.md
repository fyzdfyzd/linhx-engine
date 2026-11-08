# Project Structure — Quy Ước Thư Mục

## Folder Naming
Mỗi bài viết mới tạo folder theo format:
```
Idea_{YYYYMMDD_HHmm}_{Slug_Name}/
```
Ví dụ: `Idea_20260207_0800_Co_Don_Ket_Noi/`

## Required Files — 3-Variant Pipeline
```
Idea_{Timestamp}_{Slug}/
├── 01_Seed_Input.json              ← Ý tưởng gốc
├── 02_Context_Expansion.json       ← Mở rộng ngữ cảnh
├── 03_Research_Plan.md             ← Kế hoạch nghiên cứu
├── 04_Raw_Research_Data.json       ← Dữ liệu thô
├── 05_Synthesis_Insights.md        ← 30 insights nén từ data
│
├── Variant_A/                      ← Phương án A (góc nhìn khác biệt)
│   ├── 06_AI_Curated_List.json     ← Danh sách đã chọn lọc
│   ├── 07_The_Critic_Loop/
│   │   └── Loop_XX/
│   │       ├── draft.md
│   │       └── critic_feedback.json
│   └── 08_Final_Output.md
│
├── Variant_B/                      ← Phương án B
│   ├── 06_AI_Curated_List.json
│   ├── 07_The_Critic_Loop/
│   └── 08_Final_Output.md
│
├── Variant_C/                      ← Phương án C
│   ├── 06_AI_Curated_List.json
│   ├── 07_The_Critic_Loop/
│   └── 08_Final_Output.md
│
├── _best_pick.md                   ← So sánh 3 bản + chọn bản tốt nhất
├── _status.json
├── _agent_log.md
├── _lessons_learned.md
└── _timelog.json
```

## _status.json Schema
```json
{
  "idea": "raw idea text",
  "slug": "Slug_Name",
  "created_at": "ISO 8601",
  "current_step": 1,
  "steps_completed": [],
  "variants": {
    "A": { "status": "pending", "critic_score": null },
    "B": { "status": "pending", "critic_score": null },
    "C": { "status": "pending", "critic_score": null }
  },
  "best_variant": null,
  "total_duration_minutes": 0,
  "last_updated": "ISO 8601"
}
```

## Quy Tắc
- **KHÔNG** sửa file bước trước nếu đã chuyển sang bước sau
- Bước 1→5 là **CHUNG** cho cả 3 variant
- Bước 6→9 **tách riêng** vào Variant_A/, Variant_B/, Variant_C/
- `_agent_log.md`, `_lessons_learned.md`, `_timelog.json` là **append-only**
- 3 variant PHẢI có **GÓC NHÌN KHÁC BIỆT**, không phải copy paste cùng ý
