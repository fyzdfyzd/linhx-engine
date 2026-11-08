---
name: lesson-slides
description: Dùng khi cần kết xuất file slides.md của Slidev thành bộ ảnh PNG độ phân giải 1920x1080 theo từng bước click và sinh file segments.json đồng bộ từng khung hình với từng đoạn lời giảng.
---
# Kết xuất Slide và tạo phân đoạn (`lesson-slides`)

Skill này biến file Markdown của Slidev thành các khung hình tĩnh chuẩn Full HD (`1920x1080`) theo từng hiệu ứng click và ghép nối chính xác với từng đoạn lời giảng để chuẩn bị cho bước tổng hợp giọng nói và dựng video.

## 1. File đầu vào
- `work/course/04-lessons/<L>/slides.md`: kịch bản và bố cục slide Slidev.
- `work/course/04-lessons/<L>/style.css`: định dạng giao diện và font chữ tiếng Việt `Be Vietnam Pro`.
- `work/course/engine.json`: chứa đường dẫn tới bản Node.js portable (`>= 22.12.0`), thư mục cache npm và trình duyệt Playwright Chromium.

## 2. File đầu ra
- `work/course/04-lessons/<L>/frames/*.png`: bộ ảnh PNG độ phân giải `1920x1080`, đặt tên theo quy chuẩn `<số_slide_3_chữ_số>-<số_click_2_chữ_số>.png` (ví dụ `001-01.png`, `002-01.png`, `002-02.png`).
- `work/course/04-lessons/<L>/segments.json`: danh sách các phân đoạn của bài học, mỗi phần tử gồm `{"seg_id": "001-01", "slide": 1, "click": 0, "png": "001-01.png", "text": "..."}`.

## 3. Lệnh engine cần chạy
Bước 1 — Thiết lập biến môi trường dùng Node 22.12 portable và chạy Slidev export (có thể tái sử dụng `node_modules` đã cài sẵn `@slidev/cli`, `@slidev/theme-default`, `playwright-chromium`, `@fontsource/be-vietnam-pro`):
```text
npx slidev export slides.md --format png --with-clicks --scale 1 --output frames
```
Bước 2 — Ghép các khung ảnh PNG vừa xuất với lời giảng trong `slides.md` để tạo `segments.json`:
```text
python src/plugin/linhx-course/engine/make_segments.py work/course/04-lessons/<L>/slides.md work/course/04-lessons/<L>/frames work/course/04-lessons/<L>/segments.json
```

## 4. Cổng duyệt
- Kiểm tra nhanh đầu ra của `make_segments.py`: đảm bảo tổng số đoạn, tổng số âm tiết nằm trong khoảng `1.000–1.500` âm tiết và không có đoạn nào dài quá `60` âm tiết.
- Mở xem hoặc ghép lưới ảnh thu nhỏ (contact sheet) từ thư mục `frames/` để kiểm tra chữ tiếng Việt không bị lỗi dấu, nội dung không tràn khung và vùng góc dưới bên phải (`520x520` px) thông thoáng cho trường hợp chèn avatar.

## 5. Lỗi hay gặp và cách xử lý (từ thực tế vận hành)
- **Lỗi Node hệ thống quá cũ (`Node 21.7.1`)**: Vite 8 và Rolldown 1.2 của Slidev mới yêu cầu Node `^20.19` hoặc `>=22.12`. Nếu chạy bằng Node 21.7 của hệ thống sẽ gặp lỗi `Cannot find native binding` hoặc `styleText ERR_INVALID_ARG_VALUE`. Cách xử lý: luôn đưa đường dẫn `local\.node\node-v22.12.0-win-x64` lên đầu biến `PATH` trước khi gọi `npm` hoặc `npx`.
- **Lỗi Playwright không tìm thấy trình duyệt**: Luôn đặt biến môi trường `PLAYWRIGHT_BROWSERS_PATH` trỏ tới `local\.pw-browsers` (nơi đã cài sẵn Chromium) để tránh tải lại trình duyệt ra thư mục người dùng.
- **Cảnh báo `Failed to patch FloatingVue` khi export**: Đây là cảnh báo vô hại của plugin twoslash trong Slidev, không ảnh hưởng tới ảnh PNG xuất ra.
- **Lỗi lệch số khung và số đoạn lời**: Nếu `make_segments.py` báo lỗi `Slide X: A đoạn lời nhưng B khung`, hãy kiểm tra lại số thẻ `v-click` / `<v-clicks>` trên slide `X` so với số dấu `[click]` trong khối chú thích `<!-- ... -->` của slide đó.
