---
name: loc
description: "Lọc bản ghi mới của kho minh hoạ ý tưởng: bỏ mục NoAI, tải ảnh tạm, đánh dấu bài đăng lại bằng dHash, đưa vào hàng chờ phân loại; dọn ảnh tạm sau khi xong."
---
# Lọc trước khi phân loại

1. `pip install pillow` (một lần).
2. `python scripts/loc.py` ngay sau `thu-link`.
3. Với mục có `trung_voi`: đây là bản đăng lại. Khi phân loại, mở cả hai link, giữ tác giả gốc (thường là tài khoản hoạ sĩ, không phải trang tổng hợp kiểu "art.daily"). Nếu không tìm được tác giả gốc, ghi `tac_gia.ten = "chưa rõ tác giả"`.
4. Sau khi skill `phan-loai` xong: `python scripts/loc.py --don-tam` để xoá ảnh tạm. Kho chỉ giữ mã băm `dhash.json`.
