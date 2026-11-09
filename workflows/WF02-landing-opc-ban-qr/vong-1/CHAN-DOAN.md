# Chẩn đoán trang Q1 hiện tại (linhx-engine `front/index.html`, 9/11)

Chụp bằng Playwright, API giả lập (giá thử 499.000đ, QR giả). Ảnh và số đo ở `kiem/` (`q1-hien-tai-*.png`, `do.json`).

Số đo máy: không tràn ngang ở 360/390/1280 · 2 chạm tới QR (đạt ≤ 3) · **không có ô đồng ý** · chân trang chỉ ghi "LINHX Engine 0.1 · báo cáo do trợ lý AI lập…".

## Ba lỗi nặng nhất (sửa theo thứ tự)
1. **Không có lý do để tin, nên không ai trả tiền.** Trang chỉ có một đoạn mô tả và ba thẻ giống hệt nhau (kiểu "đóng hộp", mục A2 của chong-mui-ai). Không có báo cáo mẫu, không biết ai đứng sau, không thấy giá trước khi kéo tới biểu mẫu. Đầu trang ghi "LINHX · Báo cáo · Engine", tức là khách nhìn thấy công cụ nội bộ, không thấy một thương hiệu. → Cần: báo cáo mẫu thật (ảnh), người đứng sau, giá ngay ở hero, bỏ bộ ba thẻ.
2. **Hở pháp chế, chạm cổng đỏ.** Không có ô đồng ý xử lý dữ liệu. Chân trang không có tên chủ, địa chỉ, mã số thuế (NĐ 248/2026 Điều 4). Không có link Bảo mật hay Hoàn tiền. Email để tuỳ chọn, nên khách trả tiền xong có thể không có kênh nhận báo cáo. → Cần: 2 ô đồng ý tách mục đích, email bắt buộc, chân trang định danh, trang chính sách.
3. **Sau khi hiện QR, khách bị bỏ lại.** Khối QR chỉ có ảnh và một dòng chữ nhỏ (mã đơn, số tiền, nội dung chuyển khoản dính nhau). Không hiện tên người nhận tiền, không có trạng thái "đang chờ chuyển khoản" tự cập nhật, không có nút "tôi đã chuyển", không nói trả xong thì nhận gì, bao lâu. → Cần: màn chờ tự hỏi trạng thái đơn, số tiền to, nút chép nội dung chuyển khoản, tên tài khoản nhận, bước tiếp theo.

## Lỗi nhỏ hơn (để vòng sau)
- Nút xanh `#1f4fd6` trên nền kem là màu mặc định của công cụ, chưa theo brand.
- Phần "Thêm thông tin" gập lại là đúng (giữ ít ô), nhưng chữ tóm tắt quá dài.
- Không có `<title>` riêng và mô tả chia sẻ (khách đến từ Zalo hay Facebook sẽ thấy "LINHX Engine").

## Tham chiếu cần tìm (nhắm vào 3 lỗi)
- Lỗi 1: trang bán báo cáo hoặc audit có ảnh báo cáo mẫu ở hero (Co–Star, các trang audit SEO hay GEO bán một lần).
- Lỗi 3: màn chờ thanh toán QR tốt (Stripe, trang QR của SePay, Chiêm Tinh Số bản `01-man-qr-natal-360.png` đã có "Giữ đơn 30 phút" và trạng thái chờ, nên dùng lại).
