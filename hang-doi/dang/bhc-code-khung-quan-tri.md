may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\ifagent-wt\bhc-code-khung-quan-tri
nhan: may-2 2026-11-17T07:40:22+0700

Lưu ý máy: KHÔNG dùng background task, subagent hay thợ con; mọi lệnh chạy tiền cảnh. Gọi `npm.cmd`/`npx.cmd`. Push sau MỖI commit. Server chạy bằng Start-Process, tắt đúng PID.
Brand health check: VẼ KHUNG trang quản trị (chưa nối app). Hiện app chỉ có mã ADMIN_CODE qua header để tải leads.csv và xem lịch sử, không có giao diện.
1. Worktree C:\linhx\ifagent-wt\bhc-code-khung-quan-tri, nhánh agy/bhc-code-khung-quan-tri từ origin/agy/bhc-code-noi-app.
2. HTML tĩnh trong apps/brand-health/bao-cao/khung/B-quan-tri/, cùng token màu, font, logo, Sáng/Đêm của khung B-trang-chu. Màn:
   a) Đăng nhập bằng mã quản trị.
   b) Tổng quan hôm nay: số lượt quét, đang chờ, lỗi, lead mới, chi phí AI hôm nay so với trần ngày, nút tạm dừng nhận lượt mới.
   c) Danh sách lượt quét: thương hiệu, giờ, trạng thái, 3 chỉ số, chi phí; lọc theo ngày/trạng thái; mở chi tiết.
   d) Chi tiết lượt: bảng sự thật khách khai (sửa được), nút quét lại, nút "Xuất bản báo cáo" / "Ẩn báo cáo", link /bao-cao/<mã>/, tải PDF.
   e) Lead: danh sách, đồng ý liên hệ có/không, tải CSV, nút "Gửi sang đội event".
   f) Cài đặt: trần lượt/IP, trần lượt/ngày, trần chi phí/ngày, bật/tắt từng mô hình AI (Gemini; ChatGPT, Claude, Perplexity qua OpenRouter khi có khoá), chế độ quét nhanh/đầy đủ.
   Dùng số mẫu Vinamilk/IF Agent thật trong bao-cao/bien-tap; còn lại ghi rõ "số mẫu". Chạy được ở 1280 (chính) và 360 không tràn. Không chữ kỹ thuật thô (mã model, JSON).
3. Test khung: 6 file có, lề 360 ≥ 16 px, không tràn ngang, không chuỗi mã model thô. npm.cmd run verify xanh.
4. Bằng chứng bang-chung/bhc-code-khung-quan-tri/: 6 màn × 1280, 3 màn (b, c, e) × 360, ghep-1280.png. ≤ 600 KB/ảnh.
CẤM: sửa server/, nối app, deploy, sinh ảnh AI, đụng apps/event, apps/lab, packages/. Trạng thái cao nhất REVIEW.
KET-QUA.md: `dat: co|khong`; SHA; verify; danh sách ảnh.
