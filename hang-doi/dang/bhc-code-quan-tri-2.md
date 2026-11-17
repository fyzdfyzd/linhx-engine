may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\ifagent-wt\bhc-quan-tri
nhan: may-2 2026-11-17T10:30:48+0700
moc: ffb61433c27629d5c726241516cddc4066e66290

Lưu ý máy: KHÔNG dùng background task, subagent hay thợ con; mọi lệnh chạy tiền cảnh. Gọi `npm.cmd`/`npx.cmd`. Server chạy bằng Start-Process, tắt đúng PID.
LUẬT MỚI (lần trước quá 40 phút mà 0 commit, mất dấu): commit + push ít nhất mỗi 10 phút, kể cả khi test chưa xanh (tiêu đề ghi "WIP"). Việc đầu tiên trong 3 phút: vào C:\linhx\ifagent-wt\bhc-quan-tri, `git status`, commit toàn bộ phần đã làm ở phiếu bhc-code-quan-tri-1 với tiêu đề "WIP quản trị: phần làm từ phiếu 1", push nhánh agy/bhc-quan-tri (worktree chưa có thì tạo từ origin/agy/bhc-nen).
Tiếp tục đề phiếu bhc-code-quan-tri-1 (đọc lại trong hang-doi/xong/... hoặc dang/ nếu cần), CHỈ làm phần A trong phiếu này:
A1. Đăng nhập /quan-tri/ bằng ADMIN_CODE, khoá 5 lần sai/15 phút, cookie phiên HttpOnly SameSite=Strict 8 giờ, /api/quan-tri/* không phiên trả 401.
A2. Màn Tổng quan (số thật từ store + jobs, chi phí ước theo BH_GIA_*, trần BH_TRAN_CHI_PHI_NGAY, nút tạm dừng nhận lượt).
A3. Màn Danh sách lượt quét (lọc ngày/trạng thái, phân trang 50).
Bỏ mọi nhãn "số mẫu", "Màn B ·", đường dẫn kỹ thuật. E2E cho A1–A3 (không chờ theo thời gian cố định). npm.cmd run verify xanh. Ảnh 1280 + 360 của A2, A3 trên app thật vào bang-chung/bhc-quan-tri/.
Phần B (chi tiết, lead, cài đặt) để phiếu sau, ghi vào KET-QUA "còn phần B".
CẤM: deploy, gọi AI thật, in mã quản trị/khoá, đụng apps/event, apps/lab, packages/. Trạng thái cao nhất REVIEW.
KET-QUA.md: `dat: co|khong`; SHA; E2E A1–A3; verify.

nhip: 10:45 15p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
