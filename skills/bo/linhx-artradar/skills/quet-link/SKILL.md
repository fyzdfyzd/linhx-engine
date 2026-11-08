---
name: quet-link
description: Dùng khi cần quét bài/hồ sơ nghệ thuật (Bored Panda, ArtStation, Behance, Reddit, Tumblr, Lofter…) để lấy metadata và link nghệ sĩ vào records.jsonl, không tải ảnh.
---
# Quét link (M2)

Trước khi quét: mở skill `nguon-radar`, chỉ quét nguồn `allowed: true`, dùng `delay_s` của nguồn.

## Bored Panda (sitemap)
```
python scripts/quet_boredpanda.py --out <lab>/data/records.jsonl --max 50
```
- Lấy sitemap từ robots.txt, chọn bài có từ khoá nghệ thuật trong slug (sửa bằng `--keywords`, khớp theo từ, không theo chuỗi con), kiểm robots từng URL.
- Chỉ lấy link trong thân bài (từ `<h1` tới `post-submission-line`); hộp tác giả và footer là link của người viết Bored Panda.
- Bài tổng hợp (>15 link hoặc >5 link Reddit) được gắn `tong_hop: true`; `gom_nghe_si.py` bỏ qua.
- Mỗi bài: tiêu đề, mô tả, ngày, og:image (link), dòng "Image credits / More info", link ra Instagram/ArtStation/Behance/web, cờ `noai`.
- Chạy lại an toàn: bỏ qua URL đã có trong file. Có danh sách bài sẵn thì dùng `--urls file.txt`.

## Trang có extractor gallery-dl
```
pip install gallery-dl
python scripts/quet_gallerydl.py --out <lab>/data/records.jsonl --limit 20 https://www.artstation.com/<user>
```
- Gọi `gallery-dl -j` (chỉ xuất JSON, không tải), bỏ mục có NoAI trong tag/tiêu đề. ArtStation: NoAI nằm trong mảng `tags` (giá trị `"NoAI"`), không có field riêng.
- ArtStation: `--limit` đếm theo ảnh, không theo project (`--limit 10` chỉ ra 1-4 project); muốn ~10 project thì đặt `--limit 40`. Delay mặc định 4s (`--delay`).
- gallery-dl là GPL: chỉ gọi CLI, không chép code vào plugin.

## Sau khi quét
- In tóm tắt: số bài, số link, số mục NoAI bị bỏ, lỗi.
- Không mở/tải ảnh ở bước này. Chuyển sang skill `the-nghe-si`.
