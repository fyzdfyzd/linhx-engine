---
name: "dong-thread"
description: "Đóng một thread Claude Code đang dở: viết file bàn giao gọn để Antigravity (hoặc phiên mới) làm tiếp. Dùng khi Linh nói 'đóng thread', 'bàn giao', 'chuyển sang Antigravity'."
---

# Đóng thread và bàn giao

Mục tiêu: dừng thread hiện tại với chi phí thấp nhất, để lại MỘT file bàn giao đủ để Antigravity hoặc một phiên Claude mới làm tiếp mà không cần đọc lại lịch sử thread.

## Luật tiết kiệm (bắt buộc)
- Không nghiên cứu thêm, không chạy subagent, không WebSearch/WebFetch, không đọc lại file lớn. Chỉ dùng những gì đã có trong ngữ cảnh thread.
- Chỉ đọc lại một file khi cần kiểm đường dẫn hoặc trạng thái thật (ví dụ `.handoff/BANG.md`), và chỉ đọc phần cần.
- Trần cho cả việc đóng thread: khoảng 30k token. Nếu có việc còn chạy dở, dừng nó, ghi vào mục "Đang dở" thay vì làm cho xong.

## Các bước
1. Xác định thư mục dự án trên máy Linh (thường là `D:\LINHX\PRJ\<MÃ>`, `D:\LINHX\PROTOTYPE\<PRT>` hoặc `D:\LINHX\LAB\<LAB>`). Nếu không rõ, hỏi Linh một câu.
2. Viết file `<thư mục dự án>\.handoff\HANDOFF-<slug-thread>-<YYYY-MM-DD>.md` theo mẫu bên dưới. Tiếng Việt, ngắn, mỗi mục tối đa 8 dòng, tổng dưới 120 dòng.
3. Nếu dự án có `.handoff\BANG.md`: thêm/sửa đúng một dòng trỏ tới file bàn giao (đọc lại file ngay trước khi sửa, commit có kiểm mtime).
4. Ghi file lên máy bằng device_commit_files (hoặc device_bash nếu có). Máy không kết nối: gửi file bằng SendUserFile và ghi rõ là chưa chép lên máy.
5. Reply cho Linh tối đa 5 dòng: đường dẫn file bàn giao, 3 việc tiếp theo quan trọng nhất, việc cần Linh quyết, và câu "Có thể lưu trữ (archive) thread này."
6. Không tạo scheduled task, không hẹn giờ quay lại thread này.

## Mẫu file bàn giao

```markdown
# Bàn giao: <tên việc>
Thread gốc: <tên thread / kênh> · Ngày đóng: <YYYY-MM-DD> · Người nhận: Antigravity (hoặc phiên mới)

## 1. Mục tiêu
<1–2 câu: việc này để làm gì, đầu ra cuối cùng là gì>

## 2. Đã xong
- <kết quả> → <đường dẫn file / link>

## 3. Đang dở
- <việc> · đang ở bước nào · còn thiếu gì

## 4. Quyết định đã chốt (không bàn lại)
- <quyết định> · lý do ngắn · ai chốt, ngày nào

## 5. Việc tiếp theo (theo thứ tự)
1. <việc> · đầu vào · đầu ra · tiêu chí xong (kiểm được)
2. ...

## 6. File và lệnh quan trọng
- File chính: <đường dẫn>
- Chạy / kiểm: `<lệnh>`

## 7. Lưu ý và không được làm
- <rủi ro, giới hạn: không push main, không deploy, không đụng tiền/giá, không gửi khách, không ghi khoá API>

## 8. Câu lệnh mở đầu cho Antigravity
> Đọc `.handoff/HANDOFF-<slug>-<ngày>.md` và các file ở mục 6. Làm việc số 1 ở mục 5, dừng khi đạt tiêu chí xong và ghi kết quả vào cuối file này dưới mục "## Nhật ký tiếp nhận".
```

## Không làm
- Không chép lại lịch sử thread, không dán log dài, không dán nội dung bí mật (mật khẩu, token, khoá API, số điện thoại người phỏng vấn).
- Không bịa trạng thái: việc chưa kiểm được thì ghi "chưa kiểm".