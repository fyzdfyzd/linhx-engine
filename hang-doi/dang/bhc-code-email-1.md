may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\ifagent-wt\bhc-quan-tri
nhan: may-2 2026-11-17T12:20:22+0700
moc: 19584c76aeec95dddc890735e714ea5ec420bf4c

Lưu ý máy: KHÔNG dùng background task, subagent hay thợ con; mọi lệnh chạy tiền cảnh. Gọi `npm.cmd`/`npx.cmd`. Server chạy bằng Start-Process, tắt đúng PID.
LUẬT: commit + push ít nhất mỗi 10 phút. Commit đầu tiên trong 5 phút.
Brand health check: gửi báo cáo qua email cho khách để lại lead. Worktree C:\linhx\ifagent-wt\bhc-quan-tri, nhánh agy/bhc-quan-tri (đỉnh 19584c7, git pull trước).
1. server/lib/thu.js: gửi qua Resend HTTP API (https://api.resend.com/emails), khoá RESEND_API_KEY, người gửi BH_THU_TU (vd "IF Agent <baocao@ifagent.net>"). Không có khoá thì không gửi, ghi trạng thái "chưa gửi: chưa cấu hình" (không lỗi). Hàng đợi gửi riêng, thử lại 3 lần cách nhau tăng dần, không chặn luồng quét.
2. Khi khách để lại lead có đồng ý: gửi 1 thư tiếng Việt có dấu: tiêu đề "Báo cáo AI nói gì về <thương hiệu>", thân: 3 chỉ số, 1 câu chốt, nút mở /bao-cao/<mã>/ và link tải PDF Light; chân thư có cách huỷ nhận thư. Mẫu HTML theo token màu khung B, chạy tốt trên Gmail điện thoại (bảng, inline style, rộng ≤ 600 px). Báo cáo đang ẩn thì chưa gửi, gửi khi quản trị bấm Xuất bản.
3. Quản trị màn Lead: thêm cột trạng thái thư (chưa gửi / đã gửi giờ / lỗi + lý do dễ hiểu), nút "Gửi lại".
4. Test bằng Resend giả (server HTTP cục bộ, không gọi mạng thật): có khoá → gửi đúng 1 thư đúng người nhận + tiêu đề; không đồng ý → không gửi; báo cáo ẩn → chờ tới khi xuất bản; Resend trả 500 hai lần rồi 200 → thành công lần 3; không khoá → "chưa cấu hình". Không chờ theo thời gian cố định (dùng đồng hồ giả). test:lap 5/5, verify xanh.
5. Bằng chứng bang-chung/bhc-email/: ảnh thư HTML ở 600 px và 360 px, ảnh màn Lead có cột trạng thái.
CẤM: gọi Resend thật, in khoá, gửi thư thật, deploy, đụng apps/event, apps/lab, packages/. Trạng thái cao nhất REVIEW.
KET-QUA.md: `dat: co|khong`; SHA; test thư; test:lap; verify.

nhip: 12:38 18p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
