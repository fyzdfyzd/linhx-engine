---
name: sd-nhan-take
description: Bước 6 Flow Pack. Nhận clip Linh tải từ Flow về, khớp với phiếu, ghi sổ credit, xem contact sheet, chọn bản giữ, cảnh báo ngân sách. Dùng mỗi khi Linh báo đã render xong một lô.
---

# sd-nhan-take: nhận clip và ghi sổ

Chạy: `python LAB016-PHIM-NGAN-AI/src/tools/nhan_take.py LAB016-PHIM-NGAN-AI/data/<tap>`
- `--anh-xem`: tạo contact sheet 3 khung mỗi clip vào `anh-xem/` (cần ffmpeg). Mở ảnh để xem: nhân vật có đúng đoạn khoá không, đủ shot không, có chữ lạ không.
- `--giu E01-D03-t2 …`: đánh dấu bản giữ; các lượt khác của đoạn đó thành "bo".

## Quy tắc
- File nháp `-n1.mp4` không ghi sổ (0 credit). File sai tên bị bỏ qua: nhắc Linh đổi tên.
- Đoạn đã 2 lượt mà chưa giữ được: **dừng**, tìm nguyên nhân (keyframe, mô tả chuyển động, quá nhiều nhân vật), sửa JSON, chạy lại `flow_pack.py`; không bảo Linh thử lượt 3.
- Ngân sách ≥ 80%: báo Linh. ≥ 100%: không đề nghị render thêm khi Linh chưa duyệt lại.
- Sau mỗi lần chạy, ghi 1 mục vào `LOG.md`: số lượt, credit, tỉ lệ giữ, lỗi Veo gặp phải.
