---
name: theo-doi-ket-qua
description: Theo dõi kết quả các bài Linh đã nộp, cập nhật pipeline và sổ giải thưởng, rồi lên kế hoạch khai thác branding khi đạt giải. Dùng khi hỏi "kết quả cuộc thi", "đã có giải chưa", hoặc chạy định kỳ sau ngày công bố.
---

# Theo dõi kết quả và khai thác giải

1. `python ".../contestscan.py" results`: với mỗi bài ở giai đoạn `đã nộp` / `chờ kết quả` / `vào vòng sau`, script tải `results_url` (hoặc trang thể lệ), báo **THẤY TÊN** nếu gặp tên trong `profile.json → watch_names` hoặc tên bài, hoặc "trang đã đổi".
2. Trang không đổi nhưng đã qua `results_date`: WebSearch "<tên cuộc thi> <năm> kết quả" / "trao giải", và trang Facebook của đơn vị tổ chức. Đọc danh sách giải gốc, không tin bài tóm tắt.
3. Cập nhật: `mark <id> "vào vòng sau" | "đạt giải" --prize "Giải Ba" | "trượt"`. Khi `đạt giải`, script ghi `output/GIAI-THUONG.md` (sổ giải, có nguồn) để dùng cho bio và hồ sơ diễn giả.
4. **Khai thác branding** khi đạt giải (ghi `output/khai-thac/<id>.md`, Linh duyệt rồi tự đăng):
   - một bài LinkedIn/Facebook kể chuyện bài dự thi (không khoe suông: vì sao viết, một ý đáng nhớ, cảm ơn BTC, link bài báo);
   - dòng bio mới và dòng cho hồ sơ diễn giả;
   - đề xuất tái dùng bài thắng: Substack, bài giảng, talk.
   Sau đó `mark <id> "đã khai thác"`.
5. Trượt: ghi một dòng bài học vào `note` (tiêu chí nào hụt) để lần sau chọn cuộc thi tốt hơn.

Không đăng gì ra ngoài thay Linh.
