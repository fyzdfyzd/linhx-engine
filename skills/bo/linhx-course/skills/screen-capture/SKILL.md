---
name: screen-capture
description: Dùng khi bài học có phần thực hành hoặc minh hoạ trực quan cần chụp ảnh hoặc quay lại màn hình trình duyệt, giao diện dòng lệnh và chèn vào slide hoặc ghép vào video bài giảng.
---
# Quay màn hình và chụp minh hoạ thao tác (`screen-capture`)

Skill này hỗ trợ ghi lại các bước thao tác thực tế (trên trình duyệt web qua Playwright hoặc giao diện dòng lệnh/cấu trúc thư mục) thành ảnh chụp sắc nét hoặc đoạn clip ngắn `1920x1080` không tiếng để nhúng vào bài học kiểu `demo`.

## 1. File đầu vào
- Kịch bản thao tác demo của bài học trong `work/course/04-lessons/<L>/slides.md` hoặc mô tả các bước cần minh hoạ.
- Đường dẫn Node.js và trình duyệt Chromium đã cấu hình trong `work/course/engine.json` (`PLAYWRIGHT_BROWSERS_PATH`).

## 2. File đầu ra
- Ảnh chụp màn hình minh hoạ đặt tại `work/course/04-lessons/<L>/assets/capture-<ten>.png` hoặc trực tiếp thay thế/nhúng vào khung hình `work/course/04-lessons/<L>/frames/<seg_id>.png`.
- Hoặc đoạn video quay màn hình thao tác đặt tại `work/course/04-lessons/<L>/assets/capture-<ten>.mp4` (chuẩn `1920x1080`, `25 fps`, định dạng `yuv420p`) để chèn vào bài giảng khi ghép video.

## 3. Lệnh engine và quy trình thực hiện
1. **Cách 1 — Quay hoặc chụp giao diện bằng Playwright**:
   Sử dụng Playwright Chromium sẵn có trong môi trường cục bộ với kích thước viewport `1920x1080` (`recordVideo` hoặc `page.screenshot`) để ghi lại giao diện thực tế (ví dụ: hiển thị cấu trúc file skill, giao diện chạy thử hoặc trình phát bài học).
2. **Cách 2 — Chuẩn hoá clip quay màn hình bằng `ffmpeg`**:
   Mọi đoạn clip quay màn hình (từ `.webm` của Playwright hoặc công cụ ghi màn hình) đều được chuyển đổi về chuẩn `1920x1080`, `25 fps` bằng lệnh:
   ```text
   ffmpeg -y -i raw_capture.webm -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=25" -an -c:v libx264 -pix_fmt yuv420p work/course/04-lessons/<L>/assets/capture-demo.mp4
   ```
3. **Ghép vào bài học**:
   - Có thể nhúng ảnh/clip vào slide Slidev trước khi chạy `lesson-slides`, hoặc trích xuất khung hình chuẩn `1920x1080` vào `frames/` để `compose.py` đồng bộ với lời giảng của phân đoạn tương ứng.

## 4. Cổng duyệt
- Kiểm tra độ rõ nét của chữ trong ảnh chụp/video quay màn hình: cỡ chữ hiển thị trên màn hình quay phải đủ lớn (tối thiểu tương đương `24px–32px` trên khung `1920x1080`) để học viên xem trên điện thoại vẫn đọc rõ tên file và lệnh.
- Đảm bảo không làm lộ thông tin nhạy cảm (khoá bí mật, đường dẫn cá nhân ngoài phạm vi bài học) trên màn hình quay.

## 5. Lỗi hay gặp và cách xử lý (từ thực tế vận hành)
- **Lỗi khung hình đen ở đầu hoặc cuối đoạn quay Playwright**: Khi mở trang mới trong Playwright, trang có thể trắng hoặc đen trong vài trăm mili-giây đầu. Cần chờ `networkidle` hoặc cắt bỏ 0,5 giây đầu bằng `ffmpeg -ss 0.5` để tránh lỗi `blackdetect > 1.0s` khi nghiệm thu video.
- **Lỗi lệch tốc độ khung hình (`fps`) và độ phân giải khi nối video**: Bộ ghép `compose.py` xuất video ở `1920x1080` và `25 fps`. Mọi tư liệu từ `screen-capture` phải ép đúng `scale=1920:1080,fps=25,format=yuv420p` để không gây lỗi hỏng luồng hình khi ghép.
- **Lỗi thiếu trình duyệt khi chạy Playwright độc lập**: Nhớ truyền biến môi trường `PLAYWRIGHT_BROWSERS_PATH` trỏ tới `local\.pw-browsers` để tái sử dụng bản Chromium đã cài sẵn.
