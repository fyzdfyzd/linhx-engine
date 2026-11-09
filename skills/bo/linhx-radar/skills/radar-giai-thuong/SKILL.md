---
name: radar-giai-thuong
description: "Radar giải thưởng ở Việt Nam cho doanh nghiệp và cá nhân: giải nào LINHX, TUVA hoặc Linh nộp được, giải nào uy tín hay trả phí là có, ai vừa đoạt giải (danh sách khách hàng, đối tác tiềm năng), lễ trao giải nào nên dự. Dùng khi Linh hỏi \"có giải thưởng nào\", \"giải cho doanh nghiệp\", \"ai vừa đoạt giải X\", \"nên nộp giải nào\"."
---

# Radar giải thưởng

Cùng thư mục radar và CSDL với `radar-su-kien` (bảng `award`; người đoạt giải nằm ở bảng `role` với `event_id = "award:<id>"`).
Giải cá nhân về viết lách, báo chí, văn chương thuộc LAB022 (`linhx-cuoc-thi`): nhập sang để chấm chung bằng `eventscan.py import-lab022 <đường dẫn LAB022>\data\seed-contests.json`; kiểm điều kiện và viết bài dự thi vẫn làm ở LAB022.

## Ba câu hỏi radar trả lời
1. **Nộp giải nào** (nhãn Nộp / Cân nhắc nộp): khớp `ung_vien` trong `profile.json` (Linh cá nhân, LINHX, TUVA), lĩnh vực hợp, uy tín đủ, còn hạn.
2. **Ai vừa thắng** (nhãn Theo dõi người thắng): danh sách DN và người đoạt giải là tín hiệu ai đang chi cho thương hiệu, đổi mới, nhân sự. Đẩy sang radar cộng đồng LAB035 bằng `export-lab035`.
3. **Lễ trao giải nào nên dự**: lễ trao có ngày cụ thể tự thành sự kiện `le-trao-<id>` và được chấm như sự kiện khác.

## Quy trình
1. Quét bằng tìm kiếm web (giải ít khi có RSS): "giải thưởng 2027 phát động", "nhận hồ sơ giải thưởng doanh nghiệp", "awards Vietnam 2027 call for entries", tên các giải đã có trong kho + năm tới. Mở trang thể lệ chính thức.
2. Ghi `data/giai-<ngày>.json` dạng `{"awards": [...]}` theo `radar-su-kien/references/schema.md` mục Giải thưởng. `uy_tin` 1 đến 5 kèm `ly_do_uy_tin`; `tra_phi_de_nhan: true` chỉ khi có bằng chứng (phí "thẩm định", "vinh danh" bắt buộc, gói truyền thông kèm danh hiệu, danh sách người thắng dài bất thường).
3. Sau lễ trao: thêm `nguoi_doat_gan_nhat` (tên, loại, năm, hạng mục) từ thông cáo hoặc báo.
4. `eventscan.py seed data/giai-<ngày>.json` rồi `eventscan.py all --no-fetch`. Đọc `output/GIAI-THUONG.md`.
5. Thẩm định giải trước khi Linh quyết nộp (`output/tham-dinh/giai-<id>.md`, 1 trang): điều kiện (năm hoạt động, doanh thu, pháp nhân; TUVA là tổ chức phi lợi nhuận có được nộp không), hồ sơ cần gì, chi phí thật, ai từng thắng, giá trị branding, kết luận Nộp/Không.
6. Báo Linh: giải sắp hạn trong 45 ngày, 3 giải nên nộp, giải nghi trả phí nên tránh, DN mới đoạt giải đáng chú ý.

Giai đoạn: `mới | theo dõi | chuẩn bị hồ sơ | đã nộp | vào vòng sau | đoạt giải | trượt | bỏ` qua `eventscan.py mark <id> <giai đoạn>`.
Không nộp hồ sơ, không trả phí, không liên hệ BTC thay Linh.
