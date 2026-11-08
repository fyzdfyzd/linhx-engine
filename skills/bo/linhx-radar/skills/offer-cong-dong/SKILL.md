---
name: offer-cong-dong
description: Thiết kế gói chia sẻ và hợp tác LINHX cho một cộng đồng hoặc sự kiện (talk, workshop, báo cáo đồng thương hiệu, công cụ miễn phí cho hội viên, tài trợ hiện vật bằng dịch vụ agentic). Dùng khi Linh nói "làm offer cho CSMO", "đề xuất hợp tác với hội X".
---

# Offer cho cộng đồng

1. Đọc dòng cộng đồng trong `output/csv/cong-dong.csv` và các dòng của nó trong `pain-offer.csv`.
2. Kiểm lại pain point bằng nội dung mới nhất của cộng đồng (chủ đề mùa tới, bài đăng gần đây).
3. Đề xuất 3 mức, mỗi mức ghi rõ cộng đồng nhận gì, hội viên nhận gì, LINHX nhận gì (lead, uy tín, dữ liệu):
   - **Cho đi**: talk/bài viết/công cụ miễn phí (ví dụ quét Brand Truth qua QR, bản tin radar)
   - **Đồng tạo**: báo cáo/khảo sát đồng thương hiệu, workshop thực hành, recap AI sau sự kiện
   - **Đối tác**: tài trợ bằng dịch vụ agentic, gói ưu đãi hội viên, nhân vật AI tại sự kiện
4. Ghi `output/offer/<id-cong-dong>.md`. Nếu Linh cần deck, chuyển sang plugin `linhx-deck` (đề bài = file này).

Giá để `[Linh chốt]`. Không cam kết thay Linh với ban tổ chức.
