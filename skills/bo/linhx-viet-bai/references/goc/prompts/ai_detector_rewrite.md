# Hướng dẫn Rewrite — Sửa lỗi AI Pattern (Stage 1)

## Nguyên tắc
Antigravity nhận file `ai_detector_feedback.json` từ AI Detector (Gemini độc lập). File này CHỈ chứa các pattern AI cần sửa — KHÔNG liên quan đến chất lượng nội dung.

## Mục tiêu
Làm cho bài viết **có giọng con người hơn** — không phải viết lại nội dung, mà phá vỡ các pattern đặc trưng của AI.

## Cách đọc feedback

1. **Xem `verdict`**:
   - `"CLEAN"` → Không cần sửa. Chuyển sang Stage 2 (Editorial QA).
   - `"AI_DETECTED"` → Đọc từng issue bên dưới và sửa.

2. **Xem `red_flags`** — Sửa NGAY, theo thứ tự:

   | Code | Cách sửa |
   |------|----------|
   | R1 - Cấu trúc liệt kê đều | Phá vỡ cấu trúc: gộp 2 ý thành 1, tách 1 ý thành đoạn riêng, xen kẽ anecdote giữa các ý |
   | R2 - Transition quá mượt | Xóa transition phrase, bắt đầu câu mới đột ngột. Hoặc dùng câu ngắn 2-3 từ làm bridge |
   | R3 - Tone motivational | Xóa hoàn toàn câu motivational. Thay bằng câu mở hoặc câu hỏi tu từ lạnh |
   | R4 - Bài tròn trịa quá | Cố tình để 1-2 đoạn "lỏng" — ý chưa hoàn chỉnh, câu bỏ lửng |
   | R5 - Summary ở kết | Xóa recap. Kết bằng hình ảnh, câu hỏi, hoặc paradox mới |
   | R6 - Emotional escalation đều | Tạo "đáy" ở giữa bài — đoạn nhẹ nhàng/hài hước xen vào giữa 2 đoạn nặng |

3. **Xem `yellow_flags`** — Nên sửa:

   | Code | Cách sửa |
   |------|----------|
   | Y1 - Thiếu lỗi con người | Thêm 2-3 câu rất ngắn (3-5 từ). Thêm 1 ý bỏ lửng bằng dấu "—" |
   | Y2 - Đoạn văn đều nhau | Tạo 1-2 đoạn cực ngắn (1-2 câu) xen kẽ đoạn dài |
   | Y3 - Từ nối đơn điệu | Đa dạng hóa: dùng câu hỏi, câu cảm thán, hoặc bỏ từ nối hoàn toàn |
   | Y4 - Giọng neutral quá | Thêm mỉa mai, châm biếm nhẹ, hoặc nhận xét cá nhân sắc nét |
   | Y5 - Danh sách ẩn | Gộp các ý liệt kê thành narrative liền mạch |

4. **Xem `cliches`** — Thay thế theo suggestion trong feedback. Nếu không có suggestion, viết lại ý bằng cách diễn đạt mới hoàn toàn.

5. **Xem `repeated_insights`** — Giữ lần xuất hiện tốt nhất, xóa hoặc phát triển thêm các lần khác.

## Quan trọng
- KHÔNG thay đổi NỘI DUNG hoặc LUẬN ĐIỂM. Chỉ thay đổi CÁCH DIỄN ĐẠT.
- KHÔNG thêm ý mới. Chỉ phá vỡ pattern AI.
- Mục tiêu: đọc lại bài sau khi sửa phải cảm thấy "con người viết cái này".
- Sau khi sửa xong → bài sẽ được scan lại bởi AI Detector. Loop cho đến khi `CLEAN`.
