---
name: gemini-lay-cham
description: Lấy kết quả một nhiệm vụ Gemini Task về máy (zip, CSV, PDF, câu trả lời), bỏ trùng, giải nén, chấm bằng máy rồi chấm tay và cho điểm Argon. Dùng khi Linh nhắn "lấy kết quả <mã>", "check Gemini", "Argon xong rồi".
---

# Lấy kết quả và chấm

## 1. Lấy về (phiên có Chrome của Linh)
1. Đọc link trong `<thư mục nhiệm vụ>/CHAY.md` hoặc `gt.py so --con-mo`. Mở link trong tab mới.
2. Nhiệm vụ chưa xong: ghi `gt.py trang-thai <thư mục> dang-chay --ghi-chu "<đang ở bước nào>"`, báo Linh, dừng.
3. Tải mọi thẻ file (zip, csv, pdf, ảnh, mp4) về `<thư mục>/files/`. Thư mục tải mặc định của Chrome là `%USERPROFILE%\Downloads`: chuyển file vừa tải sang `files/`.
4. Lưu câu trả lời: nút Export/Chia sẻ → Markdown nếu có, hoặc chép chữ câu trả lời, ghi `<thư mục>/TRA-LOI.md`. Kết quả nằm trong canvas thì mở canvas, chép ra file; không mở được thì ghi rõ "mất bảng trong canvas" vào CHAY.md.
5. `python "${CLAUDE_PLUGIN_ROOT}/scripts/gt.py" lay <thư mục>`: bỏ file trùng theo hash, giải nén zip vào `giai-nen/`, tách các khối `### FILE:` trong TRA-LOI.md.

## 2. Chấm máy
`gt.py kiem <thư mục>` theo `yeu-cau.json`, ghi `KIEM-MAY.md`: đủ file, đủ cột, đủ dòng; đoạn văn nghi cắt cứng; URL bọc google; file trùng tên thư viện (dấu hiệu test giả); danh sách số tự khai cần đối chiếu; 10 URL mẫu.

## 3. Chấm tay (Claude)
- Mở 10 URL mẫu (WebFetch hoặc tab mới): còn sống không, có đúng nội dung dòng ghi không. Ghi tỷ lệ.
- Đọc 5 dòng ngẫu nhiên mỗi bảng chính: tiếng Việt tự nhiên chưa, có câu phán/doạ, có bịa không.
- Đối chiếu số tự khai trong TONG-KET.md với số `gt.py kiem` đếm được.
- Test Argon viết: **không chạy code Argon trên máy Linh**. Muốn chạy thì chép sang thread cloud và chạy `python -I -m unittest discover` trong thư mục tạm.
- Điểm 1–5 cho: độ rộng, độ tin nguồn, chất lượng data, prototype/đầu ra, trung thực (tự khai có đúng không). Ghi `<thư mục>/CHAM.md`, rồi `gt.py trang-thai <thư mục> da-cham`.

## 4. Bài học
Lỗi mới của Argon thành luật mới: thêm một dòng vào `templates/may-argon.txt` và bảng "Luật viết đề" trong skill `gemini-task`, để đề sau tránh được.
