# event.ifagent.net · bản dựng vòng 1 (9/11)

**19 trang**, 2 form lead (brief đầy đủ + gọi lại nhanh), nút Zalo nổi trên điện thoại, trang cảm ơn có mã. Sửa nội dung trang con ở `nguon/*.json` (hoặc `nguon/_trang-bu.py`, `nguon/_bai-tru.py`) rồi chạy `python3 tao-trang.py`. Own media ở `../own-media/`.

Trang tĩnh + máy nhận lead nhỏ, không đụng lõi engine. Đã chạy thử từ đầu đến cuối: tính gói → điền form → lead ghi vào `leads/leads.jsonl` có mã, nguồn (`?kenh=`, utm), gói, và dấu vết đồng ý. 5 cỡ màn hình (1280/1024/768/390/360) không tràn ngang, mọi chỗ bấm ≥ 44px.

## Chạy
```
node server.mjs            # Node ≥ 18, không cần cài gói. Mặc định cổng 8080
PORT=80 LEAD_DIR=/var/leads node server.mjs
```
Báo tin (tuỳ chọn): `TG_TOKEN` + `TG_CHAT` (Telegram), `SHEET_WEBHOOK` (Google Apps Script ghi Sheet).
Linh chốt phương án A (9/11). B và C cất ở `_phuong-an-bo/`. Cổng máy: `node kiem/kiem.cjs http://localhost:8080` (cần Playwright). Giao diện đã khoá: `DESIGN.md`, `DESIGN.khoa`, `khoa/anh-chuan/`.

## Linh / chị Hằng cần điền (ở `public/cau-hinh.json`, để null thì trang giữ chữ an toàn)
- Giá từng gói (đang ghi "Báo giá trong 1 ngày").
- Thời gian dựng thật từng gói (đang ghi 5 / 10 / 15 ngày, **giả định, chờ xác nhận**).
- Cam kết phản hồi brief trong 1 ngày làm việc.
- Case có số + ảnh thật + khách được nêu tên (chưa có, nên trang chưa có khối case).

## Triển khai (sau CSMO 20/11, theo wiki h31)
1. Chép thư mục lên VM, chạy `node server.mjs` sau Caddy/Nginx (HTTPS).
2. Trỏ DNS event.ifagent.net; giữ đường dẫn cũ bằng 301.
3. Khi engine C2 xong: sửa hàm `guiDi()` trong `server.mjs` để đẩy lead sang engine. Trang không đổi.
