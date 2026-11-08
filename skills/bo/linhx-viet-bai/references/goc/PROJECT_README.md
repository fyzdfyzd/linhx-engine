# 🚀 Antigravity Writing Engine — FLOW v FM

> Dự án viết bài tự động theo phong cách **Đinh Trần Tuấn Linh** (Byung-Chul Han style).
> Chạy trên nền tảng **Antigravity** — mỗi conversation = 1 bài viết.

---

## Cách Sử Dụng

### Tạo bài mới
Mở conversation mới trong workspace này và gõ:
```
/new-article Sự cô đơn trong thời đại luôn kết nối
```

### Tiếp tục bài dở
```
/resume-article Idea_20260207_0800_Co_Don_Ket_Noi
```

### Cải thiện bài đã viết
```
/review-article Idea_20260207_0800_Co_Don_Ket_Noi
```

---

## Pipeline (9 Bước)

| Bước | Skill | Output |
|:---:|:---|:---|
| 1-2 | `idea-seeder` | `01_Seed_Input.json` + `02_Context_Expansion.json` |
| 3-4 | `deep-researcher` | `03_Research_Plan.md` + `04_Raw_Research_Data.json` |
| 5-6 | `content-synthesizer` | `05_Synthesis_Insights.md` + `06_AI_Curated_List.json` |
| 7-9 | `critic-loop-writer` | `07_The_Critic_Loop/` + `08_Final_Output.md` |

---

## Cấu Trúc Workspace

```
D:\@WF\TOOL\00_WRITING\
├── spec.md                    ← Đặc tả kỹ thuật gốc
├── PROJECT_README.md          ← File này
├── _templates/                ← JSON templates
├── .agent/
│   ├── rules/                 ← 4 rules (Always On)
│   ├── skills/                ← 4 skills
│   └── workflows/             ← 3 workflows
└── Idea_{Timestamp}_{Slug}/   ← Mỗi bài viết = 1 folder
```

---

## Specs
- Chi tiết kỹ thuật: xem `spec.md`
- Persona & tone: xem `.agent/rules/writing-identity.md`
- Chất lượng: xem `.agent/rules/quality-standards.md`
