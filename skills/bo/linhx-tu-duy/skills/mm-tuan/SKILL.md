---
name: mm-tuan
description: "Buổi chấm tuần cho bộ mental model của Linh: liệt kê quyết định tới hạn để chấm trước, thẻ đã dùng, độ phủ 30 ngày, thẻ bị bỏ quên, và hiệu chỉnh độ chắc so với kết quả. Cuối tháng thì đề xuất heuristic riêng từ nhật ký. Dùng khi Linh gõ /mm-tuan, \"chấm tuần\", \"review mental model\", hoặc khi lịch Chủ nhật chạy."
---

# Chấm tuần

Lệnh: `node "${CLAUDE_PLUGIN_ROOT}/scripts/tu-duy.js" tuan`

Thứ tự luôn là **chấm trước, đọc sau**:

1. **Quyết định tới hạn.** Với từng quyết định, hỏi Linh kết quả và đúng điều trong "Đổi ý nếu", rồi gọi `cham` (xem skill mm-quyet). Chưa chấm xong thì chưa sang bước 2.
2. **Thẻ đã dùng và độ phủ.** Nói một câu nhận xét. Nếu độ phủ dưới 60%, đề nghị tuần sau bốc ưu tiên các thẻ bị bỏ quên.
3. **Hiệu chỉnh.** So độ chắc với tỷ lệ đúng.
   - Ví dụ: ghi 70% mà đúng 95% nghĩa là đang quá thận trọng. Ghi 90% mà đúng 50% nghĩa là quá tự tin.
   - Chỉ nhận xét khi đã có ít nhất 5 quyết định được chấm.
4. **Nút thắt tuần (M14).** Hỏi Linh một câu: "Nút thắt tuần này là gì?" Ghi câu trả lời bằng `vi-du M14 "..."`.

**Cuối tháng** (lần chấm tuần cuối cùng của tháng), làm thêm bước rút heuristic riêng:
- Đọc `nhat-ky-quyet-dinh.md` và `the-hang-ngay.md` trong thư mục dữ liệu.
- Tìm mẫu lặp lại, ví dụ 3 lần lấn cấn cùng một kiểu đối tác.
- Đề xuất **một** heuristic của Linh dạng "Nếu ___ thì ___". Kiểm 3 điều:
  - có lặp ở ít nhất 2 bối cảnh khác nhau
  - có dự đoán được việc sau không
  - có phải của riêng Linh, hay chỉ là thẻ có sẵn đổi tên
- Đạt cả 3 điều thì đề nghị tạo thẻ riêng `L<n>` trong `the-rieng/`. Dùng cùng frontmatter với thẻ gốc, đặt `bo: "rieng"`, `trang_thai: nhap`.
- Chỉ tạo file khi Linh đồng ý.

Giữ báo cáo dưới 20 dòng.
