@AGENTS.md

## Riêng cho Claude tại `D:\LINHX\LAB`
- Luôn kiểm tra **Cổng bắt buộc đầu mỗi cuộc trò chuyện (Session Gate)** trong `AGENTS.md`: bắt đầu mỗi cuộc trò chuyện bằng `[Đang dùng: LABNNN-TEN-VIET-TAT]` hoặc `[Đã tạo mới: LABNNN-TEN-VIET-TAT]`.
- Skill dùng chung nằm ở `.claude/skills/` (`lab-moi`, `viet-overview`, `proto-moi`, `ra-soat-kho`, `kiem-chu-anh`).
- Khi giao việc code nặng cho Antigravity trong một LAB, ghi đề vào `LABNNN-TEN-VIET-TAT/.handoff/` và kiểm tra báo cáo nghiệm thu cùng `git diff --stat`.
- Dùng Claude in Chrome: đóng tab mình mở ngay khi xong bước, tối đa 5 tab, cuối việc đóng cả nhóm tab và kiểm danh sách rỗng (skill `dong-tab-chrome`).
