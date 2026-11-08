---
name: bien-tap
description: Chuyển bản làm mượt sang plugin linhx-bien-tap (hồ sơ Vân Anh) để biên tập, rồi sửa theo phiếu. Dùng sau bước làm mượt nháp của Linh.
---

# Biên tập (chuyển sang plugin linhx-bien-tap)

1. Chuẩn bị trong thư mục bài: `04-ban-muot.md`, `03-nhap.md` (nháp của Linh), `02-du-lieu.md` làm kho nguồn, sổ hồi quy nếu có.
2. Gọi skill `bien-tap-bai` của plugin biên tập với hồ sơ `van-anh`. Đưa cả nháp của Linh: biên tập viên được so bài với nháp, chỗ nào máy thêm ngoài nháp là lỗi.
3. Sửa đúng những câu phiếu nêu, không viết lại cả bài. Chỗ phiếu nói ý yếu hay thiếu chuyện thì hỏi Linh, không tự bịa.
4. Dừng khi phiếu ghi "GIAO ĐƯỢC" hoặc sau ba vòng.

## Khi chưa cài plugin biên tập
Biên tập viên chạy ở ngữ cảnh riêng, nhận bài như bài cộng tác viên, đối chiếu mọi số với kho, soát tám lỗi trong `ho-so-bien-tap/van-anh/LUAT.md`, trả tối đa 12 chỗ sửa cụ thể. Chạy `scripts/cham_cau.py` và `scripts/kiem_nhap.py bai` trước khi giao.
