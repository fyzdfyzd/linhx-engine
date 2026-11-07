---
name: wiki-linhx
description: Đọc và ghi wiki chung LINHX (lõi LINHX ENGINE, các unit, BU, dự án, đề bài, quyết định). Dùng trước mọi việc thuộc LINHX để khỏi mù thông tin, và sau mọi việc làm đổi quyết định, trạng thái, đường dẫn hay đề bài. Lệnh: "nạp wiki", "hỏi wiki", "rà wiki".
---

# Wiki LINHX

Wiki nằm ở `wiki/` của repo `fyzdfyzd/linhx-engine` (máy cty: thư mục clone repo này). Luật đầy đủ: `wiki/AGENTS.md`.

## Trước khi làm
1. Đọc `wiki/INDEX.md`.
2. Đọc `wiki/trang/tong-quan.md` nếu chưa biết bức tranh, rồi trang đúng việc (dự án, nhóm hệ thống, lõi).
3. Đọc 10 dòng cuối `wiki/LOG.md`.

## Sau khi làm (nếu sự thật thay đổi)
1. Sửa trang liên quan trong `wiki/trang/`, đổi `cap_nhat`.
2. Quyết định của Linh: thêm dòng `wiki/trang/quyet-dinh.md`. Việc chờ Linh: sửa `wiki/trang/cho-linh.md`.
3. Tài liệu gốc mới: chép vào `wiki/nguon/YYYY-MM-DD-TEN.md`, không sửa file cũ.
4. Thêm một dòng cuối `wiki/LOG.md`.
5. Chạy `python scripts/ra_wiki.py`, sửa hết LỖI.
6. Commit riêng, tiêu đề bắt đầu bằng `wiki:`.

## Cấm
Không ghi bí mật (chỉ ghi nằm ở đâu). Không xoá trang. agy không tự sửa `quyet-dinh.md`, chỉ ghi `de-xuat` vào LOG. Trang có `sinh_tu_dong` thì không sửa tay: sửa ở bảng nguồn rồi chạy `scripts/wiki_tu_bang.py`.
