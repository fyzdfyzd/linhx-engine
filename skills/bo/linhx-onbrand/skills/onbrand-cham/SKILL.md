---
name: onbrand-cham
description: Chấm một thiết kế (PNG, JPG, PDF, PPTX, HTML) có bám brand guideline không, thang 100 điểm theo 5 mục màu, chữ, logo, hình/bố cục, nội dung, kèm chỗ sai và cách sửa. Dùng khi cần duyệt ấn phẩm trước khi đăng hoặc giao khách.
---

# Chấm onbrand một thiết kế

Cần: `brands/<brand-id>/brand.json` (chưa có thì chạy skill onbrand-nap trước).

## Bước
1. Máy đo: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/onbrand.py cham <brand.json> <file> --ra <ket-qua.json>`
   - Màu (30): đo vùng đồ hoạ phẳng có màu, bỏ ảnh chụp và nền trắng/đen; tỉ lệ thuộc bảng màu theo ΔE2000 ≤ ngưỡng; liệt kê màu lệch kèm màu chuẩn gần nhất.
   - Chữ (20): font nhúng trong PDF, PPTX, HTML so với `font_cho_phep`.
   - Nội dung (10): từ cấm (lorem ipsum, tên template cũ...).
2. Claude nhìn: mở file thiết kế và các logo trong `01-logo/`, chấm theo `${CLAUDE_PLUGIN_ROOT}/data/rubric-nhin.md` (logo 25, hình/bố cục 15; với file ảnh chấm thêm chữ và nội dung). Ghi `diem-nhin.json`.
3. Gộp: `onbrand.py gop <ket-qua.json> <diem-nhin.json>`.
4. Báo cáo: `onbrand.py bao-cao <ket-qua.json> --ra <bao-cao.html>`.
5. Trả lời người dùng: điểm, xếp loại (≥85 ĐẠT CHUẨN, 70–84 SỬA NHẸ, <70 LỆCH CHUẨN), tối đa 3 lỗi nặng nhất, mỗi lỗi một câu sửa cụ thể (ví dụ "đổi #3E9642 sang Green #00B579").

## Lưu ý
- Màu lệch nhỏ (ΔE 8–12) thường do xuất CMYK ↔ RGB: nói rõ là "có thể do hệ màu", không kết luận designer sai.
- File ảnh không đọc được font: nói rõ điểm chữ là Claude nhìn, độ tin thấp hơn.
- Không chấm cảm tính "đẹp/xấu"; chỉ chấm có bám chuẩn hay không.
