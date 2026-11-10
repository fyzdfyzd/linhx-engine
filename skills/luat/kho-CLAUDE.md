@AGENTS.md

## Riêng cho Claude
- Skill nằm ở `.claude/skills/` (bản chép từ `_system/skills/`). Sửa skill thì sửa ở `_system/skills/` rồi chạy `_system/sync-skills.ps1`.
- Subagent (thợ) nằm ở `.claude/agents/` (bản chép từ `_system/agents/`, cùng script sync). Agent trưởng điều phối theo skill `agent-truong`.
- Khi giao việc code cho Antigravity, dùng `agy -p` trong thư mục EXP/PRJ và chỉ đọc report + `git diff --stat`, không đọc toàn bộ output.
- Dùng Claude in Chrome: đóng tab mình mở ngay khi xong bước, tối đa 5 tab, cuối việc đóng cả nhóm tab và kiểm danh sách rỗng (skill `dong-tab-chrome`).
