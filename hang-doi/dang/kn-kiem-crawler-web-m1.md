may: may-1
loai: khac
tran_phut: 15
khong_tien_phut: 15
tu_sua: 0
nhan: may-1 2026-11-17T19:59:12+0700
nhan: may-1 2026-11-18T11:53:30+0700

# kn-kiem-crawler-web-m1
Đọc và làm theo luật chung `viec/kn-thu/DE-BAI.md` (bắt buộc).

Kỹ năng: gọi LINHX Crawler (server cũ D:\LINHX_CRAWLER, FastAPI cổng 8000 trên máy 1) quét web.
1. `curl -s http://127.0.0.1:8000/docs` hoặc /health. Tắt thì đọc README trong D:\LINHX_CRAWLER, bật server tiền cảnh có timeout, ghi lệnh đã dùng; xong việc tắt server nếu do mình bật.
2. Gọi API quét 2 URL: https://example.com và https://vnexpress.net (trang chủ). Lưu văn bản trích ra vào xong/<id>/web-1.txt, web-2.txt (cắt ≤ 20 KB).
ĐẠT khi: web-2 có ≥ 500 ký tự tiếng Việt. Trả: endpoint đã gọi, thời gian mỗi URL, số ký tự.
