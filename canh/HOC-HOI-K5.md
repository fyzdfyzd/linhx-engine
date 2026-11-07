# K5 · Học từ đội thợ hàng đầu → luật cho thợ LINHX ENGINE (8/11/2026)

Đã đọc code thật (clone 8/11): karpathy/autoresearch (`program.md`), michael-harris/claude-code-multi-agent-dev-system (README, `agents/orchestration/scope-validator.md`, `autonomous-controller.md`, `hooks/`), rjmurillo/ai-agents (`AGENTS.md`, `docs/landing-workflow.md`, `docs/agent-metrics.md`, `docs/merge-guards.md`).

## 10 luật đưa vào bộ điều phối engine

| # | Luật | Học từ | Áp vào đâu |
|---|---|---|---|
| 1 | Một số đo duy nhất, máy đo, thợ không sửa được bộ đo | autoresearch: `prepare.py` chỉ đọc, `val_bpb` là sự thật | Đã có: nghiệm thu + `.khoa`. Giữ nguyên |
| 2 | Giữ hay bỏ: đạt thì tiến nhánh, không đạt thì `git reset` về mốc, không làm tiếp trên code hỏng | autoresearch vòng lặp keep/discard | K2: CHUA_DAT lần 3 thì lùi về mốc phiếu |
| 3 | Hộp giờ cứng: quá 2 lần hộp là giết, coi như trượt và lùi | autoresearch (5 phút, quá 10 phút là kill) | Phiếu 40 phút, quá 80 phút giết + lùi |
| 4 | Sổ kết quả một dòng mỗi lần thử: mã commit, số đo, giữ/bỏ/hỏng, mô tả | autoresearch `results.tsv` | VONG.md thêm cột `giu/bo/hong` |
| 5 | Đơn giản thắng: cải thiện nhỏ mà thêm nhiều dòng thì bỏ; xoá code mà vẫn đạt là thắng | autoresearch "simplicity criterion" | Review Claude: chấm thêm số dòng thêm/bớt |
| 6 | Phạm vi bằng danh sách trắng + trần số file đổi; người kiểm phạm vi có quyền phủ quyết | devteam scope-validator (`allowed_files`, `max_files_changed`, VETO) | K1: `vung` + `toi_da_file` (mặc định 8) |
| 7 | Leo thang khi kẹt, không nhả cho thợ khác làm lại y như cũ: lần 3 trượt thì đổi cách (chia nhỏ đề, hoặc hội đồng tìm lỗi) | devteam model escalation + Bug Council sau 3 lần | K2: lần 3 → CAN-LINH + Claude chia đề |
| 8 | Gộp nối tiếp một cửa: mỗi lúc chỉ một nhánh được cập nhật từ main, chạy test, gộp; xong mới tới nhánh sau | rjmurillo landing-workflow (41 nhánh song song làm hỏng 818 lượt chạy) | Bộ điều phối: thợ làm song song, GỘP nối tiếp |
| 9 | Đo sức khoẻ đội thợ bằng vài số cố định, xem theo tuần | rjmurillo agent-metrics (8 số) | W1 bảng thợ: tỉ lệ phiếu sửa, phút trung vị, token/phiếu, số lần chạm trần, % feature đạt lần đầu |
| 10 | Việc không hoàn tác được thì người duyệt; mơ hồ thì làm bản nhỏ nhất và gắn cờ | rjmurillo "Autonomy Guardrail" | Đã có luật Linh; ghi vào AGENTS.md engine |

## Không lấy
- 127 agent chuyên biệt (devteam): đội mình nhỏ, chuyên biệt rẻ nhất là phiếu bảo mật riêng (K4).
- "Không bao giờ dừng" của autoresearch: chỉ hợp vòng tối ưu một số đo, không hợp làm tính năng.
- Leo thang model haiku→opus: agy không chọn model theo phiếu được; thay bằng chia nhỏ đề.

## Cập nhật thợ
- Mỗi phiếu ghi phiên bản agy (`agy --version`) và bản bộ skill `D:\LINHX\SKILLS` (mã commit) vào VONG.md.
- Sáng thứ Hai: kiểm bản agy mới; cập nhật trên một thợ, chạy 3 phiếu mẫu, số đo không tụt mới cập nhật thợ còn lại.
- Luật mới từ lỗi thật ghi vào `HOC-HOI.md` của engine trong ngày, như CTS.
