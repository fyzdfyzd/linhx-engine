---
name: course
description: Dùng khi người dùng muốn biến một chủ đề thành khoá học e-learning hoàn chỉnh hoặc kiểm tra tiến độ hiện tại của khoá học để điều phối sang các skill thành phần.
---
# Điều phối sản xuất khoá học E-Learning (`course`)

Skill này đóng vai trò nhạc trưởng điều phối toàn bộ quy trình sản xuất khoá học từ ý tưởng ban đầu cho tới gói SCORM 1.2 hoàn chỉnh. Trạng thái của toàn bộ khoá học được lưu trực tiếp trên ổ đĩa trong thư mục làm việc (mặc định là `work/course/`).

## 1. File đầu vào
- Yêu cầu chủ đề khoá học, đối tượng người học, thời lượng mục tiêu từ người dùng (nếu khởi tạo mới).
- File cấu hình môi trường `work/course/engine.json` (tạo từ `src/plugin/linhx-course/engine/config.example.json` nếu chưa có).
- File trạng thái `work/course/course.json` (nếu khoá học đang làm dở).

## 2. File đầu ra
- `work/course/course.json`: lưu tên khoá học, danh sách các bài (`L01`, `L02`, `L03`...), bước hiện tại của từng bài, cấu hình giọng đọc (`preset:Hải Đăng` hoặc `clone:linh`) và cấu hình giảng viên ảo (`off`, `clip:linh`, hoặc `photo:linh`).
- `work/course/doctor.json`: kết quả kiểm tra môi trường phần cứng và phần mềm (`ffmpeg`, `node`, `vieneu_python`, `musetalk_python`, `gpu`).

## 3. Lệnh engine cần chạy
Trước khi bắt đầu sản xuất, luôn chạy lệnh kiểm tra môi trường:
```text
python src/plugin/linhx-course/engine/doctor.py work/course
```
Sau đó kiểm tra sự tồn tại của các file trên đĩa để gọi tiếp các skill theo thứ tự:
1. Chưa có `00-brief.yaml`, `01-objectives/<L>.yaml`, `03-assessment/quiz-<L>.yaml`, `02-outline.yaml` -> gọi skill `course-architect`.
2. Chưa có `04-lessons/<L>/slides.md` và `pronunciation.yaml` -> gọi skill `lesson-script`.
3. Cần chèn đoạn quay màn hình thao tác thực tế -> gọi skill `screen-capture`.
4. Chưa có `04-lessons/<L>/frames/*.png` và `segments.json` -> gọi skill `lesson-slides`.
5. Chưa có `04-lessons/<L>/audio/*.wav`, `timing.json`, `asr.json` -> gọi skill `instructor-voice`.
6. Nếu bật avatar và chưa có `04-lessons/<L>/avatar.mp4` -> gọi skill `instructor-avatar`.
7. Chưa có `04-lessons/<L>/build/lesson.mp4` và `lesson.vtt` -> gọi skill `lesson-compose`.
8. Chưa có `05-qa-report.md` và `06-package/*.zip` -> gọi skill `course-package`.

## 4. Cổng duyệt
- **Cổng duyệt 1 (Sau `course-architect`)**: Dừng lại để người dùng duyệt đề cương (`02-outline.yaml`), mục tiêu học tập (`01-objectives/`) và bộ câu hỏi đánh giá (`03-assessment/`).
- **Cổng duyệt 2 (Sau `lesson-script`)**: Dừng lại để người dùng đọc duyệt lời giảng trong `04-lessons/<L>/slides.md` trước khi chạy TTS và render tốn tài nguyên GPU.
- **Cổng duyệt 3 (Trước `instructor-avatar`)**: Hỏi xác nhận trước khi chạy các tác vụ nặng trên GPU (MuseTalk, FlashHead, JoyVASA) và ưu tiên dựng trọn vẹn một bài pilot trước khi chạy hàng loạt.

## 5. Lỗi hay gặp và cách xử lý (từ thực tế vận hành)
- **Lỗi xung đột bộ nhớ GPU 8 GB**: Không bao giờ chạy song song hai tác vụ GPU (ví dụ vừa chạy VieNeu-TTS hoặc ASR vừa chạy MuseTalk) vì MuseTalk chiếm tới 6,9 GiB VRAM trên card 8 GB.
- **Lỗi `nvidia-smi` báo 0 MiB trên laptop Optimus/WDDM**: Không dựa vào `nvidia-smi` để đo VRAM của tiến trình Python; sử dụng `torch.cuda.max_memory_allocated()` bên trong tiến trình chạy model.
- **Lỗi thiếu biến môi trường cache cục bộ**: Luôn đảm bảo `HF_HOME`, `npm_config_cache`, `PLAYWRIGHT_BROWSERS_PATH` trỏ về thư mục cục bộ được khai báo trong `engine.json`.
