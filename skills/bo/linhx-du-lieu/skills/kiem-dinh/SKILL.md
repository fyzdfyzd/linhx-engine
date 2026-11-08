---
name: kiem-dinh
description: Kiểm định file dữ liệu đã dọn theo hậu điều kiện trong recipe, chấm lại trước/sau và quyết định dừng hay dọn tiếp theo rubric 4 chiều. Dùng sau /don-bang, khi Linh hỏi "đã sạch chưa", hoặc trước khi bàn giao cho khách.
---

# Kiểm định và quyết định dừng

Lệnh: `python "${CLAUDE_PLUGIN_ROOT}/scripts/du_lieu.py" <lệnh>`

1. `kiem <file.sach> <recipe> --goc <file gốc> --out kiem-dinh.md`. Mã thoát 0 = đạt hết.
2. `cham <file gốc>` và `cham <file.sach>` để có bảng trước/sau.
3. Đếm lý do trong `<tên>.can-duyet.csv` (nhóm theo `ly_do`).
4. Quyết định theo **rubric 4 chiều** (học từ AutoDCWorkflow):
   - **Đúng mục đích:** các cột phục vụ `muc_dich` đã hợp lệ chưa?
   - **Không phá dữ liệu:** số dòng giảm trong ngưỡng, không ô nào bị đoán giá trị.
   - **Còn gì máy sửa được:** lỗi còn lại có thao tác nào trong `ops` xử lý được không? Có thì quay lại `don-bang` (tối đa 3 vòng).
   - **Còn gì phải người:** phần còn lại là việc của người duyệt (SĐT cụt, CMND cũ, xã bị chia tách, mojibake không cứu được).
5. Viết **biên bản bàn giao** ngắn: điểm trước/sau, hậu điều kiện đạt/trượt và lý do trượt, số dòng cần khách xác nhận theo từng lý do, đường dẫn 4 file đầu ra. Hậu điều kiện trượt vì dữ liệu nguồn thiếu (không phải lỗi công cụ) thì ghi rõ như vậy, không nới ngưỡng để cho đạt.
