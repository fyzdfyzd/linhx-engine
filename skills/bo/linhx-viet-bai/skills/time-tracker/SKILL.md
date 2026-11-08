---
name: time-tracker
description: "Skill đo thời gian thực thi pipeline bằng cách đọc file timestamps. Trigger khi cần tạo timelog cho một project, hoặc khi chạy /resume-article cần biết bước cuối chạy lúc nào. Đọc mtime của các file output trong Idea folder."
---

> Luật luôn bật: đọc `${CLAUDE_PLUGIN_ROOT}/references/goc/rules/` trước khi chạy (bản Antigravity gốc để ở `.agent/rules/`, Always On). Prompt gốc ở `${CLAUDE_PLUGIN_ROOT}/references/goc/prompts/`.


# Time Tracker — Đo Thời Gian Pipeline

## Mục đích
Tính toán thời gian thực thi từng bước dựa trên **file modification timestamps** (mtime) của OS.

## Cách hoạt động
AG agent không có đồng hồ nội bộ đáng tin cậy. Thay vào đó, khi mỗi bước lưu file output xuống disk, **OS tự động ghi nhận thời gian sửa đổi (mtime)**. Skill này đọc mtime đó để tính duration.

## Quy trình

### 1. Thu thập timestamps
Chạy lệnh PowerShell trong project folder:
```powershell
Get-ChildItem -Path "." -File | Where-Object { $_.Name -notlike "_*" } | Sort-Object LastWriteTime | ForEach-Object { [PSCustomObject]@{ File = $_.Name; Timestamp = $_.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss"); UnixMs = [long]($_.LastWriteTime - [datetime]'1970-01-01').TotalMilliseconds } } | Format-Table -AutoSize
```

### 2. Tính duration giữa các bước
Thời gian mỗi bước = `mtime(file_output_bước_N)` - `mtime(file_output_bước_N-1)`

Mapping file → bước:
| File | Bước |
|:---|:---|
| `01_Seed_Input.json` | Start (baseline) |
| `02_Context_Expansion.json` | Bước 2 |
| `03_Research_Plan.md` | Bước 3 |
| `04_Raw_Research_Data.json` | Bước 4 |
| `05_Synthesis_Insights.md` | Bước 5 |
| `06_AI_Curated_List.json` | Bước 6 |
| `07_The_Critic_Loop/Loop_01/draft.md` | Bước 7 (Loop 1) |
| `07_The_Critic_Loop/Loop_01/critic_feedback.json` | Bước 8 (Loop 1) |
| `08_Final_Output.md` | Bước 9 (Final) |

### 3. Ghi kết quả vào `_timelog.json`
```json
{
  "project_slug": "Slug_Name",
  "generated_at": "ISO 8601",
  "total_duration_seconds": 0,
  "steps": [
    {
      "step": 1,
      "file": "01_Seed_Input.json",
      "timestamp": "2026-02-07 09:20:15",
      "duration_from_previous_seconds": 0,
      "note": "baseline"
    },
    {
      "step": 2,
      "file": "02_Context_Expansion.json",
      "timestamp": "2026-02-07 09:21:43",
      "duration_from_previous_seconds": 88,
      "note": ""
    }
  ]
}
```

### 4. Đọc timestamps cho Critic Loop
Critic Loop có nhiều sub-files, cần đọc recursively:
```powershell
Get-ChildItem -Path "07_The_Critic_Loop" -Recurse -File | Sort-Object LastWriteTime | ForEach-Object { [PSCustomObject]@{ File = $_.FullName.Replace((Get-Location).Path + "\", ""); Timestamp = $_.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss") } } | Format-Table -AutoSize
```

## Khi nào trigger
- Sau khi pipeline hoàn thành (Bước 9) → auto-generate timelog
- Khi user gõ `/resume-article` → đọc timestamp file cuối để biết bước dở dang
- Khi user muốn xem performance report
