# Quy trình E2E trên giao diện · Brand Health Check (17/11/2026)

Chạy trên nhánh agy/bhc-theo-doi (19457bc trở về sau), máy chủ thật `npm.cmd start` cổng 3020, AI giả (không gọi AI thật), mỗi lần chạy một thư mục dữ liệu trắng. Trình duyệt Playwright thật: bấm, gõ, chờ như người dùng. Chạy 2 lần độc lập, so kết quả.
Mỗi bước: ảnh 1280×800 và 360×780 (chụp cả trang), ghi console lỗi, thời gian phản hồi. Quay video webm cho luồng K và Q.

## Luồng K · Khách hàng
- K1 Trang chủ: đọc được trong 5 giây, nút chính rõ, hai báo cáo mẫu bấm được.
- K2 Nhập Vinamilk (Sữa tươi, vinamilk.com.vn) → bảng sự thật gốc: hiện 4–6 dòng, sửa được 1 dòng.
- K3 Bấm quét → màn đang quét: có tiến độ theo từng trợ lý, không đứng hình.
- K4 Kết quả: landing có 3 chỉ số, câu chốt, "Xem nguyên văn" mở được.
- K5 Tải PDF Light (4 trang) và Full (40 trang): mở được, đúng số trang, số khớp landing.
- K6 Để lại email → thư (Resend giả) có link tuyệt đối mở đúng báo cáo; link huỷ nhận thư chạy.
- K7 Thương hiệu mới không có mẫu (Highlands Coffee, cà phê, highlandscoffee.com.vn): đi hết K2–K5.
- K8 Lỗi: bỏ trống tên; website sai dạng; vượt giới hạn lượt theo IP; một trợ lý quá giờ. Mỗi lỗi có câu tiếng Việt lịch sự, không chữ kỹ thuật, không mất dữ liệu đã nhập.
- K9 Chuyển Sáng/Đêm ở mỗi màn chính.

## Luồng Q · Quản trị
- Q1 Đăng nhập sai mã → báo lỗi; đúng mã → vào tổng quan.
- Q2 Tổng quan: số lượt, hàng đợi, chi phí hôm nay so với trần.
- Q3 Lượt quét: lọc trạng thái, thấy lượt K2 và K7.
- Q4 Chi tiết: sửa sự thật → chấm lại → điểm đổi; ẩn rồi xuất bản báo cáo → landing công khai đổi theo.
- Q5 Lead: thấy email K6, tải CSV mở được, dấu tiếng Việt đúng.
- Q6 Cài đặt: tắt một trợ lý → lượt quét mới không còn làn đó; hạ trần ngày → lượt mới bị hoãn kèm lý do.
- Q7 Theo dõi tháng: bật cho Vinamilk, tua đồng hồ giả tới ngày hẹn → lượt mới chạy → trang so sánh 2 kỳ đúng số, không có câu "đổi" khi không đổi.

## Thang chấm (10 điểm, chấm khó tính; dưới 9 là chưa đạt)
| Nhóm | Trọng số | Đạt 9–10 khi |
|---|---|---|
| Chạy đúng chức năng | 30% | mọi bước K, Q xong, 2 lần cùng kết quả |
| Số liệu khớp | 15% | landing = PDF = quản trị = thư |
| Giao diện 1280 | 15% | sang, chỉn chu, khoảng thở, không đè chữ |
| Giao diện 360 | 15% | không tràn ngang, chữ ≥ 14px, nút ≥ 44px |
| Chữ cho người xem | 10% | không chữ kỹ thuật, dấu tiếng Việt đúng, nhất quán |
| Lỗi và trường hợp biên | 10% | K8 lịch sự, không mất dữ liệu |
| Tốc độ | 5% | mỗi màn < 2 giây với AI giả |

Ca hỏng được ghi theo mã (K4-360, Q6…), mức nghiêm trọng (chặn / nặng / nhẹ), ảnh chứng, cách sửa đề xuất.
