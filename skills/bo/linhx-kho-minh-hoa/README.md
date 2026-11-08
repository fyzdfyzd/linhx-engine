# linhx-kho-minh-hoa v0.1

Kho phong cách minh hoạ ý tưởng của LINHX. Plugin Claude Code, dùng được với Antigravity (agy đọc SKILL.md như hướng dẫn).

## Cài
1. Chép thư mục này vào `D:\LINHX\LAB\LAB031-KHO-MINH-HOA\src\plugin\linhx-kho-minh-hoa`.
2. `pip install gallery-dl pillow` (một lần).
3. Trong Claude Code: `/plugin install` trỏ tới thư mục, hoặc chép `skills/*` vào `.claude/skills/`.
4. Đặt biến `KHO_MINH_HOA` nếu muốn kho ở chỗ khác (mặc định `D:\LINHX\KHO-MINH-HOA`).

## Kho trông thế nào
```
KHO-MINH-HOA/
  nguon/records.jsonl        # M2: metadata thô, chỉ link
  anh/the-anh.jsonl          # M4: thẻ ảnh đã phân loại
  anh/cho-duyet.jsonl        # M4: mục Claude không chắc
  phong-cach/<id>/phong-cach.json   # M5: thẻ phong cách
  phong-cach/<id>/mau/*.png         # M6: ảnh tự sinh
  phong-cach/<id>/GHI-CONG.md       # nguồn cảm hứng, link gốc
  xem/index.html             # M7: trang xem kho
  _tam/                      # ảnh tạm, xoá sau mỗi lần chạy
```

## Luồng
`so-nguon` → `thu-link` → `loc` → `phan-loai` → `the-phong-cach` → `tai-tao` → `xem-kho`; dùng hằng ngày: `minh-hoa-y`.

## Luật chung (mọi skill)
1. Chỉ lưu metadata, link bài gốc, mô tả do ta viết. Ảnh tạm trong `_tam/` xoá ngay sau khi lọc/phân loại.
2. Bỏ mục có NoAI/`noai` hoặc tác giả ghi không cho AI.
3. Công thức sinh ảnh không dùng tên hoạ sĩ còn sống.
4. Không quét hàng loạt trang Instagram người khác; chỉ đọc bộ sưu tập Linh tự lưu.
5. Repost phải truy về tác giả gốc; không tìm được thì ghi "chưa rõ tác giả".
