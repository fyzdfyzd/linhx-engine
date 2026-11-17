may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\ifagent-wt\bhc-quan-tri
nhan: may-2 2026-11-17T09:38:46+0700

Lưu ý máy: KHÔNG dùng background task, subagent hay thợ con; mọi lệnh chạy tiền cảnh. Gọi `npm.cmd`/`npx.cmd`. Push sau MỖI commit. Server chạy bằng Start-Process, tắt đúng PID.
Brand health check: dựng trang quản trị thật theo khung apps/brand-health/bao-cao/khung/B-quan-tri/ (đã duyệt nội bộ 8/10).
1. Worktree C:\linhx\ifagent-wt\bhc-quan-tri, nhánh agy/bhc-quan-tri từ origin/agy/bhc-nen (ffb6143).
2. Route /quan-tri/ (noindex, Referrer-Policy no-referrer). Đăng nhập bằng ADMIN_CODE (so sánh hằng thời gian, khoá 5 lần sai/15 phút theo IP), phiên bằng cookie HttpOnly SameSite=Strict, hết hạn 8 giờ. Mọi API quản trị /api/quan-tri/* đòi phiên; API cũ x-admin-code giữ nguyên.
3. Màn và API thật, đúng bố cục khung, BỎ mọi nhãn "số mẫu", "Màn B ·", đường dẫn kỹ thuật kiểu "bao-cao/bien-tap":
   b) Tổng quan hôm nay: lượt quét/đang chờ/lỗi/lead mới từ store + jobs; chi phí AI hôm nay ước từ số lần hỏi × đơn giá cấu hình (biến BH_GIA_*), so với trần BH_TRAN_CHI_PHI_NGAY; nút tạm dừng nhận lượt mới (lưu vào data/, khách mới thấy câu báo dễ hiểu).
   c) Danh sách lượt quét, lọc ngày/trạng thái, phân trang 50.
   d) Chi tiết lượt: sửa bảng sự thật (lưu), "Chấm lại" theo sự thật mới (không hỏi AI lại), "Quét lại" (tạo lượt mới vào hàng đợi), Xuất bản / Ẩn báo cáo (báo cáo ẩn thì /bao-cao/<mã>/ trả trang "Báo cáo chưa công khai").
   e) Lead: danh sách, tải CSV, nút "Gửi sang đội event" chỉ ghi trạng thái đã gửi + thời điểm (chưa gọi hệ thống ngoài).
   f) Cài đặt: trần lượt/IP, trần lượt/ngày, trần chi phí/ngày, bật/tắt từng làn mô hình, quét nhanh/đầy đủ; lưu data/cai-dat.json, áp dụng ngay không cần khởi động lại.
4. Test: E2E Playwright đăng nhập sai/đúng, mỗi màn mở được, sửa sự thật → chấm lại đổi điểm, ẩn báo cáo → khách thấy "chưa công khai", tạm dừng → khách không quét được, cài đặt trần áp dụng ngay, API quản trị không phiên trả 401. Không dùng chờ theo thời gian cố định. npm.cmd run verify xanh 2 lần.
5. Bằng chứng bang-chung/bhc-quan-tri/: 6 màn 1280 + màn b, c, e 360 trên app thật, ghep-1280.png.
CẤM: deploy, gọi AI thật, in khoá/mã quản trị vào log hay ảnh, đụng apps/event, apps/lab, packages/. Trạng thái cao nhất REVIEW. Hết giờ thì push phần đã xong và ghi rõ còn thiếu.
KET-QUA.md: `dat: co|khong`; SHA; E2E quản trị pass/fail; verify 2 lần; phần còn thiếu.
