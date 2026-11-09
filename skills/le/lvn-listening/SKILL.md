---
name: lvn-listening
description: Ra bản tin lắng nghe mạng xã hội tiếng Việt theo hồ sơ md (thương hiệu, ngành, chủ đề) từ dữ liệu LINHX_CRAWLER; 0 token cho phần số, ra BAO-CAO.md + feed.json cho agent.
metadata:
  version: "0.1.0"
---

# LVN listening (LAB053, bản nhỏ nhất)

Dùng khi Linh nói "ra bản tin lắng nghe", "listening tuần này cho <hồ sơ>", hoặc agent khác cần feed tín hiệu.

## Đầu vào
- `mentions.jsonl`: mỗi dòng một bài/bình luận công khai theo bản ghi chung của LINHX_CRAWLER
  (`platform, url, author, text, published_at, metrics{like,comment,share}`).
- `ho-so/<ten>.md`: thực thể và bí danh, từ loại trừ, khía cạnh, ngưỡng. Linh sửa file này, không sửa code.

## Các bước
1. Chạy `python scripts/bao_cao.py <mentions.jsonl> ho-so/<ten>.md output/<ten>-<ngay> --so-ngay 7`.
2. Mã 2 nghĩa là cổng chất lượng chặn (ít bài, crawler dừng, một nguồn): đọc `CANH-BAO.md`, báo Linh, không viết báo cáo tay.
3. Mã 0: `BAO-CAO.md` đã đủ để gửi. Muốn có đoạn bình luận chuyên gia thì agent chỉ đọc `feed.json`
   (vài trăm token), viết tối đa 5 câu vào mục "Nhận định", không đọc lại dữ liệu thô.
4. Agent khác (viết bài LAB025, radar LAB035) đọc `feed.json` mục `tin_hieu`.

## Giới hạn hiện tại
- Cảm xúc bằng từ điển + luật phủ định và "nhưng": đủ xem xu hướng, chưa đủ để bán. Bản bán cần model ViSoBERT/PhoBERT chạy máy.
- Báo cáo không ghi tên người viết; `author` chỉ dùng chống trùng.
- `tao_mau.py` sinh dữ liệu GIẢ LẬP để thử, không dùng cho báo cáo thật.
