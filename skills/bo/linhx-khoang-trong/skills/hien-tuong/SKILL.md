---
name: hien-tuong
description: B1 radar khoảng trống. Quét top bài, top tác giả, top kênh trên Substack, Medium, kênh quan điểm (LinkedIn, X, Threads, Facebook), podcast, YouTube, cả quốc tế và Việt Nam, ghi vào 01-hien-tuong.jsonl. Dùng khi cần lấy dữ liệu hiện tượng cho LAB029.
---

# B1. Hiện tượng

Mục tiêu: mẫu KHÔNG lệch theo sở thích Linh. Đi từ bảng xếp hạng và tag công khai, không từ feed cá nhân (For you, Following).

## Nguồn và adapter
| Nguồn | Thị trường | Adapter | Chạy ở đâu |
|---|---|---|---|
| Substack (bảng xếp hạng mọi chủ đề + bản tin tiếng Việt) | quốc tế + vn | `adapters/trinh-duyet/substack_bxh.js` (đối tượng `SB`) | Chrome, tab substack.com |
| Medium (khoảng 60 tag phủ các mảng đời sống + Staff Picks) | quốc tế | `adapters/trinh-duyet/medium_tag.js` (`MT`) | Chrome đã đăng nhập, tab medium.com |
| LinkedIn, Facebook, Threads, X, YouTube | tuỳ trang | `adapters/trinh-duyet/doc_feed.js` (`DF`), thử nghiệm | Chrome, trang Linh mở |
| Apple Podcasts | vn, us | `python adapters/apple_podcast.py vn 100` | máy Linh |
| Snapshot cũ của vault | | `gapscan.py nhap <scan.txt> <raw.json.gz>` | máy Linh |

Trang cho kênh quan điểm (gợi ý, Linh chỉnh): LinkedIn Top Voices và trang hoạt động của 10 đến 20 người có tiếng ở mỗi thị trường; Facebook trang cá nhân của các cây bút Linh chỉ định; Threads, X: trang tìm kiếm theo từ khoá của cụm; YouTube: tìm kiếm từ khoá tiếng Việt, lọc "lượt xem".

## Các bước
1. Tạo thư mục lượt, `python gapscan.py init`.
2. Với mỗi adapter trình duyệt: mở trang, dán nội dung file JS bằng `javascript_tool`, gọi `X.start(...)` hoặc `DF.cuon(...)`, gọi `status()` lặp lại (mỗi lần dưới 45 giây) đến khi `done: true`, rồi `copyButton()` và bấm nút; trên máy Linh: `Get-Clipboard -Raw | Out-File -Encoding utf8 b1-<nguồn>.jsonl`. Tab ẩn làm clipboard lỗi thì lấy theo khúc `X.chunk(0)`, `X.chunk(1)`...
3. `python gapscan.py nhap b1-*.jsonl` (thêm `--thi-truong vn` cho tệp chỉ có dữ liệu Việt Nam từ `doc_feed`).
4. `python gapscan.py kiem b1`.

## Dự phòng khi adapter đọc ra 0 bài
Giao diện LinkedIn, Facebook, Threads đổi thường xuyên. Khi `DF.status()` báo 0 bài: dùng `get_page_text` trên trang, tự tách từng bài theo schema (`references/schema.md`), mỗi dòng một JSON, ghi `b1-<nguồn>-tay.jsonl`, thêm `"ghi_chu": "đọc tay"`. Báo Linh để chỉnh selector trong `doc_feed.js`.

## Luật
- Không đăng nhập thay Linh, không nhập mật khẩu. Trang đòi đăng nhập thì dừng và báo.
- Mỗi phiên LinkedIn, Facebook tối đa 5 trang, cuộn tối đa 20 lần mỗi trang.
- Ghi vào `nhat-ky.md`: nguồn nào chạy, bao nhiêu bản ghi, nguồn nào lỗi.
