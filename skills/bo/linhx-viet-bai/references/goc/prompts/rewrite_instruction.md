# Hướng dẫn Rewrite — Sửa lỗi triển khai (Stage 2: Editorial QA)

## Nguyên tắc
Antigravity nhận file `editorial_feedback.json` từ Editorial QA (Gemini độc lập). File này chứa feedback về CHẤT LƯỢNG TRIỂN KHAI từ một biên tập viên KHÔNG biết gì về quá trình viết.

**LƯU Ý**: Bài viết đã được quét sạch AI pattern ở Stage 1. Ở đây chỉ sửa các lỗi hành văn và triển khai.

## Cách đọc feedback

1. **Xem `verdict`**:
   - `"PUBLISH"` → Không cần sửa. Xuất bản.
   - `"REVISE"` → Đọc `weaknesses`, sửa chính xác các điểm đó.
   - `"MAJOR_REVISE"` → Cần rewrite phần lớn bài viết. Đọc kỹ `summary`.

2. **Xem `weaknesses`** — Sửa TỪNG weakness theo thứ tự paragraph:
   - Đọc `issue` để hiểu vấn đề
   - Đọc `fix` để xem gợi ý thay thế cụ thể
   - Sửa trực tiếp trong bài, giữ nguyên flow

3. **Xem `breakdown`** — Xác định điểm yếu chính:
   - Tiêu chí nào 0 điểm → ưu tiên sửa
   - `insight_originality = 0` → cần thêm góc nhìn mới, không chỉ diễn đạt lại
   - `literary_quality = 0` → cần viết lại câu cho sắc nét hơn
   - `philosophical_depth = 0` → trích dẫn đang trang trí, cần tích hợp sâu hơn
   - `personal_anecdotes = 0` → thêm chi tiết cụ thể (tên, nơi, thời gian)
   - `statistics_sources = 0` → thêm nguồn cụ thể cho số liệu
   - `structure_rhythm = 0` → cần cải thiện nhịp, có thể đoạn nào đó quá dài
   - `haunting_ending = 0` → viết lại kết bài, tránh motivational

4. **Xem `strengths`** — KHÔNG sửa các đoạn được khen. Giữ nguyên.

## Quan trọng
- KHÔNG được tranh luận với reviewer. Feedback là final.
- KHÔNG được đọc lại prompt của reviewer hay cố "đoán" reviewer muốn gì.
- Chỉ đọc feedback JSON và sửa theo.
- KHÔNG thay đổi giọng văn — giữ identity của tác giả.
- Sau khi sửa xong → bài sẽ được review lại. Loop cho đến khi `PUBLISH`.
