May: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 60
khong_tien_phut: 10
theo_doi: C:\linhx\ifagent-wt\bhc-gd
nhan: may-2 2026-11-19T13:54:22+0700

Lưu ý máy: KHÔNG background task/subagent; MỖI LỆNH XONG TRONG 3 PHÚT. KHÔNG deploy, KHÔNG đụng VM. Làm trên nhánh mới agy/bhc-gd-1 tách từ agy/bhc-mau-csmo-tc. Chỉ thêm file bản phác trong apps/brand-health/phac-thao/ (không sửa public/ đang chạy).
Đề (Linh 13:53 VN 19/11): "cho tôi giao diện đẹp, hấp dẫn hơn với call to action và hình ảnh nhập form, có nơi lấy email". Luật Linh: 2 phương án, chấm điểm, CHỜ DUYỆT mới build. Chỉn chu, sang trọng, tối giản. Giữ logo IF Agent, font và màu thương hiệu hiện có, tiếng Việt đủ dấu, chữ cho khách không có từ kỹ thuật.
Làm 2 trang tĩnh phac-thao/pa-a.html và pa-b.html (dùng lại chung/landing.css + thêm css riêng), cùng nội dung trang chủ hiện tại nhưng:
- Màn đầu có CTA chính rõ, một câu, nút lớn ("Kiểm tra thương hiệu của bạn miễn phí" hoặc tương đương), CTA phụ "Xem báo cáo mẫu CSMO".
- Form nhập có hình minh hoạ SINH BẰNG AI (công cụ tạo ảnh của agy/Gemini; TUYỆT ĐỐI không vẽ bằng SVG/CSS/canvas). Ảnh sinh đúng tỉ lệ khung đặt, không crop. Chủ đề: các trợ lý AI đang trả lời về một thương hiệu, tông sáng sang trọng hợp màu xanh IF Agent, không chữ trong ảnh, không logo hãng thật.
- Form thêm ô Email (bắt buộc) + tuỳ chọn Số điện thoại, ghi chú nhỏ "Chúng tôi gửi báo cáo và liên hệ khi bạn cần bản Full".
- PA A: hero 2 cột, ảnh lớn bên phải sau form nổi. PA B: hero một cột giữa trang, ảnh nền rộng nhẹ, form thẻ trắng ở dưới, thêm dải 3 bước "Nhập → AI trả lời → Nhận báo cáo".
- Giữ dải 2 thẻ mẫu Vinamilk + CSMO.
Chụp bằng playwright mỗi PA ở 1280x900 (màn đầu) + 1280 toàn trang + 360 toàn trang, 0 yêu cầu lỗi ≥400. Lưu ảnh + ảnh sinh vào bang-chung/bhc-gd-1/.
KET-QUA: đường dẫn ảnh, prompt dùng sinh ảnh, tự chấm mỗi PA /10 theo: rõ CTA, đẹp/sang, đọc tốt 360, lấy email.

nhip: 14:12 18p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
