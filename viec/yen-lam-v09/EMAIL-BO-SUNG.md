# Bổ sung cho phiếu yl12-email-vao (rà code b375c03b, 15:05 18/11)
Phiếu đang chạy phải ĐỌC tệp này (git pull hàng đợi) và xử lý thêm:
1. Hiện có cột `khach.du_lieu.email`, bảng `email_xac_nhan`, `v09_tap_chi.email`; công tắc `otp_email_bat` đang TẮT (chỉ thu lead). Giữ tắt, cổng email theo phiếu là email không mã.
2. ĐỒNG Ý NGẦM: câu chat đầu đang tự gửi "đồng ý lưu hồ sơ" thay khách. Bỏ; tấm email có ô đồng ý rõ ràng (bắt buộc tick).
3. Kiểm email ở Hỏi đáp/bình chọn đang dựa header client `x-yl-yeu-cau-email` → gỡ header là qua. Chuyển kiểm sang SERVER cho mọi điểm cần email.
4. Chiếm email: hiện ai gõ email trước (chưa xác minh) được tính là chủ, xác minh sau bị gộp vào hồ sơ họ. Sửa: email chưa xác minh KHÔNG bao giờ là chủ, không gộp.
5. Lịch sử chat trên màn đọc từ localStorage; Lịch đã lưu (`da_luu`) gắn thiết bị. Chuyển đọc lịch sử chat từ server theo khach_id (`lam_luot`), localStorage chỉ là bộ đệm.
6. Link đăng nhập (khi OTP bật sau này) chép cookie thiết bị gốc + dùng lại 10 phút: ghi vào CON_LAI nếu không kịp, không bật OTP.
