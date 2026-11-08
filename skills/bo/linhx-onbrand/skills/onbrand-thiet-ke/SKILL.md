---
name: onbrand-thiet-ke
description: Thiết kế ấn phẩm (social, story, banner, slide, poster) đúng ngôn ngữ thiết kế của một brand đã nạp, dùng logo vector, font, hoạ tiết, ảnh thật của brand, xuất PNG và tự chấm onbrand đến khi đạt. Dùng khi cần làm ấn phẩm mới cho [DOANH NGHIỆP BÁN LẺ ĐÃ ẨN DANH], Listening Vietnam hoặc brand khác trong brands/.
---

# Thiết kế đúng ngôn ngữ brand

Cần: `brands/<brand-id>/` có `brand.json` (mục `ngon_ngu_thiet_ke`), `01-logo/*.svg`, `03-chu/` font, `05-icon/hoa-tiet*.svg`, `04-hinh-anh/`.
Máy cần Chrome, Edge hoặc Chromium (Windows tự tìm Edge) và Python có Pillow.

## Bước
1. Đọc `brand.json` phần `ngon_ngu_thiet_ke`, `logo`, `mau.ty_le`, và xem 2–3 trang trong `06-ung-dung/` để nắm tinh thần.
2. Sinh token (chỉ lần đầu hoặc khi brand.json đổi):
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/thiet_ke.py token brands/<id>`
3. Chọn khuôn: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/thiet_ke.py ds brands/<id>` liệt kê khuôn trong `09-khuon/` và các ô cần điền.
   - Chưa có khuôn hợp khổ: viết khuôn mới vào `09-khuon/<ten>.html` theo luật dưới, rồi dùng như khuôn sẵn.
4. Viết nội dung vào `noi-dung.json` (ô `anh_*` là đường dẫn tương đối từ thư mục brand, ví dụ `04-hinh-anh/anh-thoi-vang-nen-do.jpg`). Chữ ngắn, đúng giới hạn ký tự ghi trong chú thích khuôn. Không bịa số liệu, giá, cam kết.
5. Dựng: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/thiet_ke.py dung brands/<id> <khuon>.html noi-dung.json --ra brands/<id>/07-bai-thi/claude-thiet-ke/<ten>.png`
   Ra PNG, HTML để sửa tay, và `.mask.png` (vùng ảnh chụp) để bước chấm bỏ ảnh khỏi phép đo màu.
6. Mở PNG ra xem. Tự chấm bằng skill onbrand-cham (máy đo + rubric nhìn). Dưới 85 thì sửa khuôn hoặc nội dung, dựng lại; tối đa 3 vòng, vẫn chưa đạt thì báo người dùng chỗ vướng.
7. Giao: PNG + điểm + 1 câu về lựa chọn bố cục. Nói rõ điểm do Claude tự chấm, cần người duyệt bằng mắt.

## Luật viết khuôn mới
- Dòng 2 là chú thích: dùng cho việc gì, danh sách ô và giới hạn ký tự. Thẻ `<html data-co="RỘNGxCAO">`.
- Chỉ dùng biến màu trong `token.css` (`var(--...)`), không gõ mã màu tay, trừ rgba của chính màu brand để làm lớp phủ.
- Font chỉ lấy tên trong `@font-face` của token.css. Logo chỉ lấy file trong `../01-logo/` đúng biến thể theo nền (`brand.json > logo.bien_the`).
- Ảnh chụp đặt trong phần tử class `anh` (hoặc thuộc tính `data-anh`) để mặt nạ nhận ra.
- Hoạ tiết qua biến `var(--hoa-tiet-...)`, chỉ làm dải, góc, vách; không đè chữ.
- Tuân `ngon_ngu_thiet_ke.bo_cuc`, `co_chu`, `khong_lam` của brand.

## Lưu ý
- Font bản quyền trong `03-chu/` chỉ dùng nội bộ; không gửi file font ra ngoài.
- Ảnh trong `04-hinh-anh/` nhiều ảnh cắt từ PDF, độ phân giải thấp: dùng thật thì thay ảnh gốc.
- Sản phẩm của thương hiệu con (ví dụ Kim Gia Bảo) đặt dưới logo mẹ cần người duyệt.
