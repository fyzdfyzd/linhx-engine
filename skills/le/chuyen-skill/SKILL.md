---
name: chuyen-skill
description: Chuyển một skill hoặc plugin Claude Code (SKILL.md, commands, agents) sang GitHub Copilot, Gemini CLI và Antigravity, kèm bảng cảnh báo chỗ chỉ Claude hiểu. Dùng khi Linh nói "chuyển skill sang Copilot/Gemini/agy", "cho skill chạy đa nền".
---

# Chuyển skill sang nền khác

Phần chép và đổi cú pháp do `scripts/chuyen_skill.py` làm, 0 token. Phần LLM chỉ là đọc bảng cảnh báo và sửa thân skill khi cần.

1. Chạy `python scripts/chuyen_skill.py <thư mục skill hoặc plugin> <gốc repo đích> --kieu tat-ca`.
   - `chung`: `.agents/skills/<ten>/`. Copilot, Gemini CLI, Antigravity đều đọc chỗ này. Mặc định chọn cái này.
   - `copilot`: thêm `.github/prompts/*.prompt.md` (từ commands) và `.github/agents/*.agent.md`.
   - `gemini-ext`: một extension `gemini-ext/<plugin>/` cài bằng `gemini extensions install <đường dẫn>`.
2. Đọc từng dòng `!` script in ra. Dòng nào là "tên tool riêng", "subagent kiểu Claude", "chèn lệnh động" thì viết lại câu đó bằng lời trung tính ("hỏi Linh", "giao agent phan-bien").
3. Agent: script bỏ `tools` và `model` vì tên khác nhau giữa các nền. Cần giới hạn quyền thì tự thêm lại theo tên tool của nền đó.
4. Kiểm: `gemini skills list` (Gemini CLI), `/skills` trong Copilot CLI hoặc VS Code agent mode, panel Customizations trong Antigravity.

Không chuyển được: hook, MCP config, `!` lệnh động, `context: fork`. Ghi rõ trong bàn giao.
