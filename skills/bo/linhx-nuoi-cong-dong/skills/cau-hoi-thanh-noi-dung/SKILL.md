---
name: cau-hoi-thanh-noi-dung
description: Vòng nhỏ của khung: gom câu hỏi lặp lại trong cộng đồng 14 ngày qua thành 3 đề bài nội dung trụ cho tuần sau (bài LinkedIn/Facebook, bản tin, buổi Zoom). Dùng khi Linh hỏi "tuần sau viết gì", "học viên đang hỏi gì".
---

# Câu hỏi → nội dung

1. Lấy câu hỏi: mục cuối `output/BAO-CAO-TUAN.md` hoặc `sqlite3 data/cong-dong.db "select noi_dung, count(*) from event where loai='hoi' and ngay>=date('now','-14 day') group by noi_dung order by 2 desc"`.
2. Gom thành cụm theo việc thật (không theo công cụ). Đếm số người hỏi mỗi cụm.
3. Chọn 3 cụm: hỏi nhiều nhất, gần offer nhất, có dữ liệu riêng của Linh (case lớp, số giờ tiết kiệm).
4. Mỗi đề bài: tiêu đề, người đọc, 3 ý, 1 case ẩn danh từ cộng đồng (chỉ khi đã xin phép), lời mời cuối bài dẫn về bậc 0 của thang offer (CLB, Zoom), link có mã nguồn (`nuoi.py link tao --kenh ... --chien-dich ...`).
5. Có plugin `linhx-viet-bai` (LAB025) thì chuyển đề bài sang đó để viết; không thì dừng ở đề bài.
