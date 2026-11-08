---
name: cham-khoang-trong
description: B6 radar khoảng trống. Chấm và xếp hạng cụm nhu cầu theo điểm khoảng trống = cầu nguồn × chuyển giao được × (1 − độ phủ VN) × thời điểm, kèm lý do và rủi ro. Dùng sau B5 của LAB029.
---

# B6. Khoảng trống

1. `python gapscan.py cham` → `06-khoang-trong.json`, `06-khoang-trong.md`.
2. Đọc bảng, rồi thêm vào cuối `06-khoang-trong.md` mục **Nhận định** cho 3 cụm đầu:
   - Vì sao điểm cao (một số đo phía nguồn, một quan sát phía VN, có link).
   - Rủi ro: cần chuyên môn gì, pháp lý, văn hoá, cạnh tranh có thể tới nhanh không.
   - Cụm điểm cao vì `chua_quet` nhiều thì ghi rõ và hạ xuống.
3. `python gapscan.py kiem b6`.
4. Báo Linh 3 cụm đầu, mỗi cụm một câu, hỏi Linh chọn 1 đến 2 cụm để làm B7 (đợi 10 phút, không trả lời thì lấy cụm điểm cao nhất).

Điểm là để xếp thứ tự, không phải xác suất thành công. Công thức và ngưỡng trong `references/cong-thuc.md`.
