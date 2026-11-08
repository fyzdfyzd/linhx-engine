---
name: so-nguon
description: Dùng trước mọi lần thu link cho kho minh hoạ ý tưởng: kiểm nguồn có trong sổ, thêm nguồn hoặc hoạ sĩ hạt giống mới, kiểm link hoạ sĩ.
---
# Sổ nguồn kho minh hoạ ý tưởng

- `sources.json`: nguồn được phép. Skill khác CHỈ thu từ nguồn `"allowed": true`.
- `hat-giong.json`: hoạ sĩ/kênh tiêu biểu theo họ phong cách (id họ trong `../../schemas/tu-dien-y-tuong.json`).

## Kiểm hạt giống (`kiem` khác `da-kiem`)
1. Mở `web` bằng Chrome (máy Linh). Xác nhận tên hoạ sĩ, tìm link Instagram chính chủ trên trang.
2. Sai người (vd `almargen.com.ar` là tạp chí) thì xoá `web`, tìm lại bằng tên + "illustrator".
3. Ghi `kiem: "da-kiem"` và ngày vào `ghi_chu`. Ghi `giay_phep` nếu trang có (vd Sketchplanations CC BY-NC).

## Thêm nguồn
Đọc robots.txt và điều khoản, ghi 1 dòng vào `terms_note`, `delay_s` tối thiểu 4. Nguồn cần đăng nhập chỉ dùng tài khoản của Linh.

Luật chung: xem README của plugin.
