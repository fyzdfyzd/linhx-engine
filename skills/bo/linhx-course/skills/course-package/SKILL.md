---
name: course-package
description: Dùng khi cần đóng gói toàn bộ khoá học (video bài giảng, phụ đề WebVTT, bài trắc nghiệm tương tác) thành gói chuẩn SCORM 1.2 (.zip), kiểm thử tự động trên LMS giả bằng Playwright và xuất báo cáo QA tổng hợp.
---
# Đóng gói SCORM 1.2 và kiểm thử LMS (`course-package`)

Skill này hoàn thiện khâu xuất bản cuối cùng: tạo giao diện học tập HTML cho từng bài (tích hợp trình phát video có phụ đề VTT và bài kiểm tra trắc nghiệm từ file YAML), đóng gói chuẩn SCORM 1.2 với `imsmanifest.xml`, chạy kiểm thử tự động trên LMS giả (`scorm-again` + Playwright) và lập báo cáo đảm bảo chất lượng (`05-qa-report.md`).

## 1. File đầu vào
- `work/course/00-brief.yaml`, `work/course/02-outline.yaml`, `work/course/course.json`.
- `work/course/01-objectives/L01.yaml`, `L02.yaml`, `L03.yaml`.
- `work/course/03-assessment/quiz-L01.yaml`, `quiz-L02.yaml`, `quiz-L03.yaml` và `exercise-L0x.md`.
- `work/course/04-lessons/<L>/build/lesson.mp4` và `lesson.vtt` của tất cả các bài trong module.

## 2. File đầu ra
- `work/course/06-package/<ten-khoa>.zip`: gói SCORM 1.2 hoàn chỉnh chứa `imsmanifest.xml` ở thư mục gốc (`schemaversion` là `1.2`), đủ 3 SCO tương ứng với 3 bài học (`L01`, `L02`, `L03`), kèm video `.mp4`, phụ đề `.vtt`, trang HTML bài học và lớp giao tiếp SCORM 1.2 API.
- `work/course/06-package/lms-test.json`: kết quả chạy kiểm thử tự động từng SCO trên LMS giả bằng trình duyệt Playwright, ghi lại điểm số thực tế (`score_raw`) và trạng thái hoàn thành (`lesson_status`: `passed`, `completed`, hoặc `failed`) đọc từ SCORM runtime API.
- `work/course/05-qa-report.md`: báo cáo kiểm định chất lượng toàn khoá học gồm bảng ma trận đối chiếu Mục tiêu ↔ Câu hỏi ↔ Mức Bloom, thống kê thời lượng từng bài, số cue phụ đề, độ lớn âm thanh, sai số ASR và kết quả chạy thử LMS.

## 3. Lệnh engine cần chạy
Chạy script đóng gói và kiểm thử SCORM 1.2 tự động:
```text
python src/plugin/linhx-course/engine/scorm_pack.py work/course
```
Script này sẽ thực hiện tuần tự:
1. Sinh các trang HTML bài học + giao diện làm bài quiz có phản hồi (`feedback`) từng phương án và gửi điểm qua `window.API` chuẩn SCORM 1.2 (`LMSInitialize`, `LMSSetValue("cmi.core.score.raw", ...)`, `LMSSetValue("cmi.core.lesson_status", ...)`, `LMSCommit`, `LMSFinish`).
2. Nén video (hoặc đưa video bài học) và đóng gói thành `work/course/06-package/<ten-khoa>.zip` có `imsmanifest.xml` hợp lệ ở gốc file nén.
3. Khởi chạy máy chủ HTTP cục bộ kèm trang LMS giả tích hợp `scorm-again`, mở bằng Playwright Chromium để tự động tua/xem hết video, chọn đáp án bài tập trắc nghiệm, nộp bài và trích xuất dữ liệu từ runtime API ra `work/course/06-package/lms-test.json`.
4. Tổng hợp số liệu và xuất file `work/course/05-qa-report.md`.

## 4. Cổng duyệt
- Kiểm tra file `work/course/06-package/lms-test.json` để xác nhận cả 3 SCO (`L01`, `L02`, `L03`) đều trả về `score_raw` kiểu số và `lesson_status` đạt `passed` hoặc `completed`.
- Đọc rà soát `work/course/05-qa-report.md` trước khi bàn giao gói `.zip` cho quản trị viên LMS.

## 5. Lỗi hay gặp và cách xử lý (từ thực tế vận hành)
- **Lỗi đường dẫn dấu gạch chéo ngược (`\`) trên Windows khi tạo file `.zip`**: Chuẩn ZIP và `imsmanifest.xml` yêu cầu mọi đường dẫn bên trong file nén phải dùng dấu gạch chéo xuôi (`/`), và `imsmanifest.xml` phải nằm ngay ở gốc của file `.zip` (không bọc thêm một tầng thư mục cha).
- **Lỗi trình duyệt chặn tải phụ đề `.vtt` qua giao thức `file://`**: Khi kiểm thử LMS giả bằng Playwright, phải phục vụ trang LMS và các SCO qua máy chủ HTTP nội bộ (`http://127.0.0.1:<port>`) để thẻ `<track kind="subtitles">` nạp được file `.vtt` mà không bị lỗi CORS.
- **Lỗi SCO không tìm thấy đối tượng `API` của SCORM 1.2**: Trang bài học cần tìm kiếm `window.API` ở cả `window.parent` và `window.opener` theo đúng thuật toán chuẩn SCORM 1.2 để tương thích với cả iframe lẫn cửa sổ popup.
