# Tiêu chuẩn chấm thiết kế slide (bản 1, 17/11/2026)

Chấm bằng mắt trên ảnh 1920×1080 của từng slide và bảng ảnh cả deck. 3 người chấm (Claude subagent, ChatGPT, Gemini), mỗi người mở ảnh mẫu top tier trước rồi mới nhìn slide. Đạt khi **mọi tiêu chí ≥ 4** theo trung vị. Ba vòng: chấm → sửa → chấm.

## Nguồn luật
- Skill `vong-lap-slide` (linhx-engine/skills/le/vong-lap-slide): 7 tiêu chí, máy đo tràn chữ, tương phản, tối giản.
- Linh 30/10: chuẩn tối thiểu là slide BTMH Guideline 2026 và slide top tier; tối giản, nhiều khoảng trống; AI hay nhồi.
- Bài học dự án chị Quỳnh Hương (BTMH, Long Thành): artwork (hình) là trung tâm, chữ theo sau; văn thuần Việt; giữ mọi phiên bản cho khách so, bản đầu có thể hay hơn bản sửa.
- Linh 14/10: không để AI vẽ cả slide có chữ; ảnh nền không chữ, chữ dựng bằng code.
- Phông phải đủ 134 chữ Việt dựng sẵn (`vls.py phong`).
- Linh 16/11: cần nhiều hình ảnh ấn tượng của brand, mạch Người → Agent → Agent → Người rõ, kể chuyện.

## Tiêu chí (1–5)

| Mã | Tiêu chí | 5 điểm trông thế nào |
|---|---|---|
| V1 | Ý chính đọc trong 3 giây | Nhìn từ hàng ghế cuối, biết slide nói gì trước khi diễn giả mở miệng |
| V2 | Một tâm điểm | Mắt rơi vào đúng một chỗ: con số, ảnh, hoặc câu tiêu đề |
| V3 | Hình là trung tâm | Slide chuyện có ảnh thật đủ lớn, đúng chuyện, không phải ảnh minh hoạ chung; slide số có hình số (lưới chấm, thanh) |
| V4 | Tối giản | ≤ 3 cỡ chữ, ≤ 8 khối, khoảng trống ≥ 45% (slide không ảnh), không vạch trang trí, không khung thừa |
| V5 | Đọc được trên máy chiếu | Chữ nhỏ nhất ≥ 24px ở 1920; tương phản ≥ 4.5:1 (≥ 3:1 cho chữ ≥ 40px); không chữ đè ảnh rối |
| V6 | Nhất quán | Tiêu đề cùng vị trí, cùng cỡ; màu nhấn một màu; nhịp sáng tối theo chương |
| V7 | Ngang mẫu | Đặt cạnh mẫu top tier không thấy kém; không có dấu hiệu "AI làm vội" (thẻ bo góc xếp hàng, icon chung chung, gradient tím) |
| V8 | Chữ Việt sạch | Không lỗi dấu, không phông mượn cho chữ có dấu, không ngắt dòng mồ côi một chữ |

Cấp deck: nhịp (không 3 slide nặng liền nhau), xương sống 4 chặng nhìn thấy được, slide mở chương nhận ra ngay.

## Cách chấm
Mỗi người chấm trả: điểm V1–V8 cho từng slide, mỗi lỗi chỉ đúng vùng trên ảnh và đề xuất **bỏ bớt** trước khi đề xuất thêm. Thợ chỉ sửa lỗi nặng đã được ≥ 2 người chấm cùng bắt, tối đa 3 lỗi một slide mỗi vòng. Slide tệ hơn sau khi sửa thì hoàn tác.
