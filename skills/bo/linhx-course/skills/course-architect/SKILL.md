---
name: course-architect
description: Dùng khi cần thiết kế khung chương trình khoá học theo phương pháp Backward Design: xác định chân dung người học, viết mục tiêu theo thang Bloom, thiết kế bộ câu hỏi quiz và bài tập thực hành có rubric trước khi lập đề cương chi tiết.
---
# Thiết kế kiến trúc khoá học (`course-architect`)

Skill này áp dụng phương pháp thiết kế ngược (Backward Design) kết hợp nguyên lý Merrill để bảo đảm mọi nội dung giảng dạy đều phục vụ trực tiếp cho mục tiêu đầu ra đo lường được. Agent chỉ soạn thảo các file văn bản cấu trúc YAML và Markdown, tuyệt đối không viết kịch bản chi tiết khi chưa chốt xong đánh giá.

## 1. File đầu vào
- Chủ đề khoá học, chân dung học viên mục tiêu, trình độ đầu vào và thời lượng mong muốn mỗi bài học.
- Nếu làm từ khoá mẫu có sẵn, đọc dữ liệu gốc từ `seed/course/` và sao chép sang `work/course/` để chỉnh sửa.

## 2. File đầu ra
Toàn bộ file đầu ra đặt trong thư mục `work/course/` theo đúng bố cục chuẩn:
- `work/course/00-brief.yaml`: mô tả tổng quan khoá học, `audience` (`persona`, `level`, `context`), ngôn ngữ `vi`, thời lượng mục tiêu mỗi bài (`duration_target_min: 5`), thông tin giảng viên và thương hiệu.
- `work/course/01-objectives/L01.yaml`, `L02.yaml`, `L03.yaml`: mỗi bài có tối thiểu 2 mục tiêu học tập. Mỗi mục tiêu gồm `{id, statement, bloom, measurable_by}`. Trường `bloom` chỉ nhận một trong sáu mức: `remember`, `understand`, `apply`, `analyze`, `evaluate`, `create`. Động từ trong `statement` phải đo đếm được (nhận diện, giải thích, phân biệt, viết, đóng gói...), không dùng từ mơ hồ như "hiểu" hay "nắm được".
- `work/course/03-assessment/quiz-L01.yaml`, `quiz-L02.yaml`, `quiz-L03.yaml`: mỗi bài có tối thiểu 3 câu hỏi (`mcq`, `tf`, hoặc `multi`). Mỗi câu hỏi phải khai báo rõ `objective` (trỏ tới mã mục tiêu trong `01-objectives/<L>.yaml`), có cùng mức `bloom` với mục tiêu đó, và có `feedback` giải thích cụ thể vì sao đúng hoặc sai.
- `work/course/03-assessment/exercise-L01.md`, `exercise-L02.md`, `exercise-L03.md`: bài tập thực hành gắn với công việc thực tế của người học, có mã bài tập (`E1`, `E2`...) khớp với `measurable_by` trong file mục tiêu và kèm bảng tiêu chí chấm điểm (rubric 4 mức).
- `work/course/02-outline.yaml`: danh sách các bài học trong module, mỗi bài nêu rõ mã bài, tên bài, danh sách mục tiêu, thời lượng dự kiến (5 phút, tương ứng 1.000–1.500 âm tiết) và phân loại bài (`concept+demo` hoặc `demo`).

## 3. Lệnh engine cần chạy
Skill này thuần tuý thiết kế nội dung văn bản nên không cần gọi script render hay GPU. Sau khi tạo xong các file YAML/MD, có thể kiểm tra tính toàn vẹn của cấu trúc bằng lệnh kiểm tra môi trường hoặc kiểm tra cú pháp YAML:
```text
python src/plugin/linhx-course/engine/doctor.py work/course
```

## 4. Cổng duyệt
- **Cổng duyệt 1 (Duyệt thiết kế khoá học)**: Sau khi tạo đủ `00-brief.yaml`, `01-objectives/*.yaml`, `03-assessment/*` và `02-outline.yaml`, dừng lại và trình bày bảng đối chiếu Mục tiêu ↔ Câu hỏi/Bài tập ↔ Mức Bloom để người dùng duyệt trước khi chuyển sang bước viết lời giảng (`lesson-script`).

## 5. Lỗi hay gặp và cách xử lý (từ thực tế vận hành)
- **Lỗi lệch mức Bloom giữa mục tiêu và câu hỏi**: Nếu mục tiêu `O1` ở mức `understand` và khai báo `measurable_by: [Q1]`, thì câu hỏi `Q1` trong `quiz-<L>.yaml` bắt buộc phải có `bloom: understand` và `objective: O1`.
- **Lỗi thiếu mã bài tập trong file Markdown**: Khi một mục tiêu có `measurable_by: [E1]`, chuỗi `E1` bắt buộc phải xuất hiện rõ ràng trong tiêu đề hoặc nội dung của file `03-assessment/exercise-<L>.md`.
- **Lỗi ước lượng thời lượng theo tiếng Anh**: Tiếng Việt có tốc độ đọc VieNeu-TTS khoảng 4,3 âm tiết/giây; do đó một bài học 5 phút cần thiết kế khung nội dung đủ cho khoảng 1.000–1.500 âm tiết (từ đơn cách nhau bởi khoảng trắng), không dùng mốc 450 từ của tiếng Anh.
