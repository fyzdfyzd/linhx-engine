---
name: nguon-radar
description: Dùng trước mọi lần quét art/nhân vật/IP để kiểm nguồn có trong sổ nguồn, đọc luật robots, giới hạn tốc độ và điều khoản; thêm nguồn mới vào sổ.
---
# Sổ nguồn LAB020

Sổ nguồn là `sources.json` cạnh file này. Skill khác CHỈ quét nguồn có `"allowed": true`.

Khi thêm nguồn mới:
1. Đọc `robots.txt` và trang điều khoản của nguồn; ghi tóm tắt 1 dòng vào `terms_note`, ngày đọc vào `checked`.
2. Chọn `method`: `sitemap` (trang báo/blog như Bored Panda), `gallery-dl` (trang ảnh có extractor), `api` (AniList, Bangumi, Wikidata, Fandom), `manual` (chỉ đọc tay).
3. `delay_s` tối thiểu 3. Nguồn cần đăng nhập: `allowed` chỉ true nếu là tài khoản của Linh.
4. Nguồn ghi rõ cấm thu thập hoặc cấm AI: `allowed: false`, ghi lý do.

Luật chung (áp cho mọi skill trong plugin):
- Chỉ lưu metadata, link, mô tả do ta viết, số đo. Không lưu ảnh, không đăng lại ảnh.
- Bỏ mục có header `X-Robots-Tag: noai|noimageai`, meta `noai`, tag NoAI, hoặc tác giả ghi không cho AI.
- Không dùng dữ liệu để train/LoRA. Không đưa tên hoạ sĩ còn sống vào prompt sinh ảnh.
