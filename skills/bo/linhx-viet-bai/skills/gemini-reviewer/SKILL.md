---
name: gemini-reviewer
description: "Module duyệt bài độc lập bằng Gemini CLI. 2-stage pipeline: AI Detector → Editorial QA. Antigravity gọi trực tiếp gemini CLI qua run_command. Fallback bằng Python REST API nếu CLI fail."
---

> Luật luôn bật: đọc `${CLAUDE_PLUGIN_ROOT}/references/goc/rules/` trước khi chạy (bản Antigravity gốc để ở `.agent/rules/`, Always On). Prompt gốc ở `${CLAUDE_PLUGIN_ROOT}/references/goc/prompts/`.


# Gemini Reviewer — 2-Stage Editorial Pipeline

## Kiến trúc

```
Stage 1 (AI Detector):   Scan AI patterns → verdict CLEAN/AI_DETECTED
Stage 2 (Editorial QA):  Chấm chất lượng → verdict PUBLISH/REVISE/MAJOR_REVISE

Pipeline:
  Draft → [Stage 1 loop] → Clean draft → [Stage 2 loop] → Final draft

PRIMARY:   Antigravity → run_command → gemini.cmd --prompt "..." < draft
FALLBACK:  Antigravity → run_command → python reviewer.py review --force-fallback <draft>
```

## Cách dùng

### Single Stage (tách riêng)

```powershell
# Stage 1: AI Detector
python D:\@WF\TOOL\00_WRITING\.agent\scripts\gemini-reviewer\reviewer.py review "<draft_path>" --stage ai-detector

# Stage 2: Editorial QA
python D:\@WF\TOOL\00_WRITING\.agent\scripts\gemini-reviewer\reviewer.py review "<draft_path>" --stage editorial-qa
```

### Full Pipeline (cả 2 stage)

```powershell
python D:\@WF\TOOL\00_WRITING\.agent\scripts\gemini-reviewer\reviewer.py full-editorial "<draft_path>"
```

### Quy trình chi tiết (khi Antigravity gọi trực tiếp CLI)

#### Bước 1: Đọc key từ key_pool.json

```python
key_pool_path = "D:\\@WF\\TOOL\\00_WRITING\\.agent\\scripts\\gemini-reviewer\\key_pool.json"
# Chọn key đầu tiên có fails < max_fails_before_skip
```

#### Bước 2: Đọc prompt theo stage

```
Stage 1: D:\@WF\TOOL\00_WRITING\.agent\scripts\gemini-reviewer\prompts\ai_detector_system.md
Stage 2: D:\@WF\TOOL\00_WRITING\.agent\scripts\gemini-reviewer\prompts\critic_system.md
```

#### Bước 3: Gọi Gemini CLI qua run_command

```powershell
$env:GEMINI_API_KEY="<api_key>"; Get-Content "<draft_path>" -Raw | gemini.cmd --prompt "<prompt>"
```

**Quan trọng:**
- **KHÔNG chỉ `--model`** → CLI tự chọn model mới nhất
- Dùng `gemini.cmd` (không phải `gemini` hay `gemini.ps1`) trên Windows
- Timeout nên set ~180 giây cho bài dài
- Prompt nên yêu cầu trả lời **CHỈ bằng JSON**

#### Bước 4: Parse JSON response

Output từ gemini CLI là text. Parse JSON từ output:
- Thử `json.loads()` trực tiếp
- Nếu fail: tìm block ```json ... ``` 
- Nếu fail: tìm `{ ... }` pattern

#### Bước 5: Lưu feedback

Lưu vào thư mục task (variant dir hoặc loop dir):
- **Stage 1**: `ai_detector_feedback.json`
- **Stage 2**: `editorial_feedback.json`
- CLI log: `gemini_cli_<stage>_<timestamp>_<key>_<status>.log`

## Tích hợp với Critic Loop (Step 8)

### Stage 1: AI Detector Loop

1. Tìm draft mới nhất
2. Gọi Gemini (stage: ai-detector)
3. Nếu verdict = `AI_DETECTED`:
   - Antigravity đọc `ai_detector_feedback.json`
   - Rewrite theo `prompts/ai_detector_rewrite.md`
   - Lặp lại từ bước 2
4. Nếu verdict = `CLEAN` → chuyển sang Stage 2

### Stage 2: Editorial QA Loop

1. Lấy draft đã clean từ Stage 1
2. Gọi Gemini (stage: editorial-qa)
3. Nếu verdict = `REVISE` hoặc `MAJOR_REVISE`:
   - Antigravity đọc `editorial_feedback.json`
   - Rewrite theo `prompts/rewrite_instruction.md`
   - Lặp lại từ bước 2
4. Nếu verdict = `PUBLISH` → Done!

**Tối đa 3 vòng mỗi stage** (tổng tối đa 6 vòng review).

## Fallback (Python REST API)

Chỉ dùng khi CLI fail:

```powershell
python D:\@WF\TOOL\00_WRITING\.agent\scripts\gemini-reviewer\reviewer.py review --force-fallback "<draft_path>" --stage ai-detector
python D:\@WF\TOOL\00_WRITING\.agent\scripts\gemini-reviewer\reviewer.py review --force-fallback "<draft_path>" --stage editorial-qa
```

Exit codes:
- `0` = Pass (CLEAN/PUBLISH)
- `1` = Needs work (AI_DETECTED/REVISE)
- `2` = Error

## File Structure

```
.agent/scripts/gemini-reviewer/
├── reviewer.py              # 2-stage pipeline + fallback REST API + key rotation
├── key_pool.json            # Pool 18 API keys
└── prompts/
    ├── ai_detector_system.md     # Stage 1: AI pattern detection prompt
    ├── ai_detector_rewrite.md    # Stage 1: Rewrite instructions for AI fixes
    ├── critic_system.md          # Stage 2: Editorial QA prompt
    └── rewrite_instruction.md    # Stage 2: Rewrite instructions for quality fixes
```

## Key Pool Settings

```json
{
  "cli_model": null,
  "api_fallback_model": "gemini-2.5-pro",
  "max_fails_before_skip": 3,
  "cooldown_seconds": 60,
  "request_timeout_seconds": 180
}
```
