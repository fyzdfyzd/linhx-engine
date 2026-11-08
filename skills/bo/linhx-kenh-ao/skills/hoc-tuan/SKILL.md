---
name: hoc-tuan
description: Vòng học hằng tuần: kéo số liệu, chạy retro, viết giả thuyết có kiểm cỡ mẫu, đề luật viết và điều chỉnh. Dùng Chủ nhật hoặc khi Linh hỏi "tuần này học được gì".
---

# Học hằng tuần

Gọi CLI là `python "${CLAUDE_PLUGIN_ROOT}/scripts/kenhao.py" --home <kênh>`.

1. `so-lieu` rồi `retro` → `bao-cao/RETRO-<ngày>.md` (số theo hook, giờ, trụ cột, cảm xúc; vòng quan hệ; lý do bị chặn; lần sửa chưa thành luật).
2. Viết phần "Phần agent viết" ngay trong file RETRO:
   - Ba giả thuyết. Mỗi cái chạy `can-mau --p <tỷ lệ nền> --d <chênh muốn thấy>`; nếu kênh chưa đủ view thì ghi "chưa kiểm được" thay vì kết luận.
   - Luật viết mới từ các lần sửa (`luat-viet`).
   - 5 người trong vòng nên đầu tư tuần tới và vì sao (dựa thang quan hệ, điểm tin).
   - Đề xuất chỉnh luật gốc (hạn mức, giai đoạn, trọng số) nếu có lý do; chỉ đề xuất, Linh sửa.
3. Báo Linh 5 dòng: một điều học được, một điều sẽ đổi, một điều cần Linh quyết.

Tín hiệu yếu thì nói là yếu. Không đổi chiến lược theo một bài viral.
