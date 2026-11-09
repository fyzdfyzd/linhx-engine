# D2 · Ba hướng cho brandai.ifagent.net

Cả ba hướng giữ **luồng mua của Chiêm Tinh Số** (Linh 9/11: "làm giao diện như chiemtinh"): một trang, nút đi thẳng tới biểu mẫu ngắn, màn QR lớn có "Tải ảnh QR", trạng thái "Đang chờ chuyển khoản · Giữ đơn 30 phút", bảng số tiền, nội dung, người nhận, mỗi dòng có nút Sao chép, trả xong tự chuyển trang. Màu và chữ theo `brand-ifagent`. Ba hướng chỉ khác nhau ở **màn đầu**, tức là cách gỡ rào cản "trả 499k nhận file chung chung thì sao" (xem `../prep/KHACH-SAN-PHAM.md`).

Mọi số và câu trích trong ảnh phác là **chữ giữ chỗ**. Bản dựng thật chỉ dùng số của báo cáo mẫu thật đã ẩn danh.

| | A · Tờ báo cáo | B · Bảng số đo | C · Một câu AI nói sai |
|---|---|---|---|
| Màn đầu | Sáng, tiêu đề serif kiểu Chiêm Tinh Số, giá to ngay dưới, một trang báo cáo mẫu đặt nghiêng | Tối (chế độ mặc định của ifAgent), 3 số đo lớn lấy từ báo cáo mẫu, rồi mới tới tiêu đề | Nửa trên tối với một câu AI trả lời sai, trích nguyên văn, nửa dưới sáng |
| Gỡ rào cản bằng | Cho xem sản phẩm thật trước | Cho thấy đây là phép đo có số | Cho thấy cái giá của việc không biết |
| Gần Chiêm Tinh Số | **Gần nhất** (nhịp, serif, nền sáng) | Xa nhất | Vừa |
| Hợp khách | Chủ doanh nghiệp nhỏ, khách từ bài viết của Linh | Marketer quen dashboard, khách từ T1 Khám | Khách lướt mạng xã hội, cần cú hích |
| Rủi ro | Nhạt nếu báo cáo mẫu không có chỗ sai đáng nói | Số đo của người khác dễ bị hiểu là số của mình | Dễ thành giọng doạ (cấm theo luật brand-check) |
| Ảnh phác | `phac-A-390.png` | `phac-B-390.png` | `phac-C-390.png` |

**Khuyến nghị: A.** A đúng ý "như Chiêm Tinh Số" nhất, và gỡ rào cản lớn nhất bằng thứ các trang audit tốt đều có (báo cáo mẫu thật). Có thể mượn của C một dòng trích nguyên văn đặt trong tờ báo cáo mẫu.

Sau D2: viết phiếu feature cho engine (`PHIEU-AGY.md`), sửa `front/` ở hàm `trangChu()` và màn QR. Agy dựng, Claude chấm theo máy đo trong `../DE-BAI.md`.
