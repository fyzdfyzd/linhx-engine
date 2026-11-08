---
name: tham-dinh-su-kien
description: Thẩm định một sự kiện trước khi đi: agenda, diễn giả đáng nghe, ai nên gặp, câu hỏi mang theo, có đáng tiền và thời gian không. Dùng khi Linh hỏi "event X có nên đi không", "chuẩn bị đi event", "ai nói ở event này".
---

# Thẩm định sự kiện

Đầu vào: tên hoặc id sự kiện (tra `data/su-kien.db` bảng `event`), hoặc link Linh gửi.

1. Đọc trang chính thức và trang đăng ký (WebFetch). Lấy agenda, danh sách diễn giả, nhà tài trợ, giá vé, hạn đăng ký. Cập nhật vào kho bằng một file seed (`radar-su-kien/references/schema.md`) rồi `eventscan.py seed` và `score`.
2. Với từng diễn giả: tra `person` trong kho (đã nghe chưa, điểm hay), tìm 1 đến 2 bài nói hoặc bài viết gần nhất (WebSearch) để biết họ hay nói gì. Đánh dấu người **mới** (chưa từng gặp ở sự kiện khác) và người **lặp lại** (nói cùng nội dung ở nhiều nơi, nghe một lần là đủ).
3. Ai nên gặp: nhà tài trợ, BTC, diễn giả trùng với `doi_tuong_muon_gap` trong `profile.json` hoặc có điểm cao trong radar cộng đồng LAB035 (`lab035_db`). Mỗi người một dòng: vì sao gặp, LINHX có gì cho họ.
4. Viết `output/tham-dinh/<id>.md` (tối đa 1 trang):
   - Kết luận: Đi / Cân nhắc / Xem bản ghi / Bỏ, một câu lý do.
   - 3 phiên nên nghe (giờ, phòng, ai), 2 phiên có thể bỏ.
   - 3 người nên gặp và câu mở lời một dòng (nháp, Linh tự gửi).
   - 5 câu hỏi mang theo, gắn với pain point đang nổi trong `output/BAN-DO-CHU-DE.md`.
   - Chi phí: vé, đi lại, nửa ngày hay cả ngày.
5. Nếu Linh quyết đi: `eventscan.py mark <id> "đăng ký"` (sau khi Linh tự đăng ký). Nhắc Linh ghi chú hoặc chụp slide để chạy `hap-thu-su-kien` sau.

Không tự đăng ký, không nhắn diễn giả hay BTC.
