# Bố cục ảnh và slide (học từ deck đẹp, 13/10/2026)

Nguồn: 18 bố cục slide toàn trang xem trên Dribbble và Pinterest (Behance cần đăng nhập lại nên bỏ qua). Ảnh chụp lưu ở `du-lieu/bo-cuc/<id>.jpg`, nguồn từng ảnh trong `du-lieu/bo-cuc/thu-vien.json`; chỉ tham chiếu nội bộ.

Điểm chung của các deck đẹp: **ảnh là nền kể chuyện, không phải vật thể dán vào khung**. Chữ đứng trên vùng trống của chính ảnh; một tiêu điểm; màu nhấn dùng một lần.

| id | Bố cục | Khi dùng | Ảnh cần | Công thức (renderer, chỉ CSS nội tuyến được Claude Slides nhận) |
|---|---|---|---|---|
| `toan-trang` | Ảnh tràn cả slide, chữ ở phía tối/trống | bìa, chương, kết, khẳng định có ảnh | 16:9, chủ thể 1/3 phải, 2/3 trái trơn cùng tông nền | `<img position:absolute 0,0,1920×1080 object-fit:cover>` đứng đầu; `<div>` phủ `linear-gradient(90deg, nền 100% 0%, nền 94% 30%, nền 60% 50%, trong suốt 72%)`; khối chữ `position:relative` rộng 880px. Màu nền = trung vị điểm ảnh 30% bên trái của ảnh (đo khi xuất) để nền slide và ảnh liền nhau |
| `nua-trang` | Ảnh tràn mép phải, mép trái tan vào nền | hai cột, bối cảnh, trích dẫn | 16:9 hoặc 4:5, cạnh giáp chữ trơn | `<img>` 1040×1080 tại left:880; dải `linear-gradient(90deg, nền → trong suốt)` rộng 360px phủ mép trái ảnh |
| `so-lon-hero` | Một con số rất to | số lớn, kết quả | không | số chính 220px màu nhấn; số phụ 64px xám, viền trái mảnh |
| `nen-mem` | Nền chuyển sắc mềm, không vật thể | slide nghỉ, khẳng định, tóm tắt | không (hoặc ảnh neo mờ) | `radial-gradient(ellipse at 82% 22%, nhấn 22–38%, nền 0% 62%)`; tông tối khi căng, sáng khi nhẹ (10b) |
| `the-nhan-manh` | Hàng thẻ, một thẻ đậm | thẻ, so sánh, lộ trình, đội ngũ | không | thẻ chính nền tối, flex 1.45, viền trên màu nhấn; thẻ phụ nền xen, chữ phụ |
| `bieu-do-hero` | Biểu đồ chiếm 60%, cột chính màu nhấn | biểu đồ | không | cột/thanh bằng `div`; cột chính màu nhấn, còn lại xám 32%; nhãn số trên cột; đường dùng `svg polyline` không chữ trong svg |
| `bang-nhan-dong` | Bảng nhạt, một dòng nhấn | bảng | không | dòng chính nền xen, chữ đậm màu tiêu đề, viền trái màu nhấn ở ô đầu; dòng khác chữ phụ |

## Prompt ảnh nền (bước 11)

Thứ tự: **bối cảnh → chủ thể → chi tiết → ràng buộc**. Nói rõ chủ thể ở đâu (1/3 phải) và tả vùng trống cụ thể ("2/3 trái trơn, cùng tông #0E2A47"). Luôn: "no frame, no plinth, no border, no rounded box, nothing cut off", "no text, letters, numbers, logos or watermarks". Ánh sáng theo cảm xúc của slide (10b): căng → lạnh, tối; nhẹ nhõm → ấm, sáng.

## H10 (cổng 12)

Ảnh nền đạt khi: 16:9 tràn mép; chủ thể ở một phần ba; phía chữ trơn và cùng tông nền; không khung, bệ, viền, bo góc; mép ảnh không lộ thành một hộp khi đặt lên slide.
