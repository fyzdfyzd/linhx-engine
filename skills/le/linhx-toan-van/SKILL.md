---
name: linhx-toan-van
description: Lấy toàn văn bài (Medium, Substack, web) theo danh sách URL bằng extension LINHX_CRAWLER trong Chrome đã đăng nhập của Linh, 0 token; tự bật server, lưu mỗi bài một file md.
---

# Lấy toàn văn bài qua LINHX_CRAWLER

Dùng khi cần **toàn văn** nhiều bài (case Medium, bài Substack, bài báo), không chỉ tiêu đề và đoạn RSS. Máy tải, agent chỉ đọc file đã lưu hoặc đoạn đã lọc. **Không** để agent tự mở từng trang trong Chrome: cách đó tốn 4–6 nghìn token mỗi bài (đo 18–19/10/2026).

## Ai chạy được
- **Antigravity** hoặc **Claude Code chạy trên máy Linh** (kể cả phiên Remote Control): chạy lệnh trực tiếp.
- Claude ở cloud và máy ảo thư mục **không** gọi được `127.0.0.1:8000` trên máy Linh. Phải mở phiên Remote Control vào `D:\LINHX_CRAWLER` hoặc giao cho Antigravity.

## Cần có
- Chrome của Linh đang mở, đã đăng nhập Medium/Substack, extension `D:\LINHX_CRAWLER\extension` đang bật.
- Danh sách URL: `.txt` mỗi dòng 1 URL, hoặc `.csv` có cột `url` (cột `stt` nếu có thì dùng làm tên file).

## Chạy
```
cd D:\LINHX_CRAWLER
powershell -File scripts\toan-van.ps1 -DanhSach <file> -Nhan <MÃ-VIỆC> -Ra <thư mục ra> [-GioiHan 61] [-Phut 60]
```
Script làm 4 bước:
1. Bật server :8000 nếu chưa chạy.
2. Dùng Chrome đang mở. Nếu Chrome chưa mở thì mở Chrome mặc định có extension.
3. Nạp task có nhãn `<MÃ-VIỆC>` rồi chờ extension đọc xong.
4. Xuất kết quả.

Server chỉ bị tắt nếu chính script đã bật nó. Chrome của Linh không bị tắt.

Muốn chạy từng bước thì dùng `scripts\lay_toan_van.py nap|cho|xuat` (xem đầu file).

## Đầu ra
- `<Ra>/<stt>.md`: tiêu đề, URL, toàn văn.
- `<Ra>/_trang-thai.csv`: trạng thái mỗi bài.
  - `du`: đủ bài.
  - `thieu-paywall`: bài member-only, chỉ có phần trang cho xem.
  - `ngan`: dưới 1.500 ký tự, nên kiểm lại.
  - `chua-co`: extension chưa đọc được. Có thể do vượt giới hạn trong ngày hoặc do tên miền riêng.

## Sau khi có toàn văn: đọc tiết kiệm
- Đừng đọc cả thư mục vào context. Dùng script lọc đoạn (ví dụ `source\RADAR-KINH-DOANH\toan-van\loc_doan.py`, khoảng 400 token/bài) rồi chỉ đọc file lọc.
- Ước token trước khi đọc: số bài × khoảng 400 (đọc file lọc) hoặc × khoảng 3.000 (đọc toàn văn). Nếu vượt 100 nghìn token thì báo Linh trước.

## Luật (theo AGENTS.md)
- Chỉ đọc: không like, clap, follow, save, bình luận.
- Không vượt paywall, không đọc hay in cookie, token.
- Tốc độ và số bài mỗi ngày theo `extension/config/limits.json`. Medium hiện tối đa 100 bài/ngày, mỗi bài cách nhau 4–10 giây, 1 tab. Danh sách dài hơn thì chạy làm nhiều ngày bằng `-GioiHan`.
- Bài ở tên miền riêng của Medium được chuyển sang `medium.com/p/<id>`. Nếu vẫn ra `chua-co` thì ghi lại, không thử cách khác.
- Không xoá dữ liệu trong `crawler_data.db`.
