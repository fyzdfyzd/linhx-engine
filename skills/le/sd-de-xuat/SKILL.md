---
name: sd-de-xuat
description: Bước 0b Flow Pack. Từ bản nghiên cứu, đưa 3 hướng phim khác hẳn nhau kèm ước tính credit và một đoạn mẫu 8 giây cho mỗi hướng, để Linh chọn hoặc trộn. Dùng sau sd-nghien-cuu, trước sd-series.
metadata:
  version: "0.1.0"
---

# sd-de-xuat: 3 hướng để chọn

Học từ `proposal-director` của OpenMontage: luôn đưa nhiều hướng thật sự khác nhau, mời trộn, và có mẫu nhỏ trước khi cam kết cả tập.

**Đầu vào:** `data/series/NGHIEN-CUU.md` đã qua trạm `nghien_cuu`.
**Đầu ra:** `data/series/DE-XUAT.md`. Trạm duyệt: `de_xuat`.

## Mỗi hướng (đúng 3 hướng)
- Tên và logline 1 câu.
- Khác các hướng kia ở ít nhất 2 trong 4 trục: thể loại, giọng kể, phong cách hình, cấu trúc tập.
- Phong cách hình: 1 câu khoá style (tiếng Anh) sẽ dùng làm `khoa_phong_cach`.
- Nhân vật chính (≤ 3) và bối cảnh chính (≤ 3); càng ít càng giữ nhân vật dễ.
- **Ước tính credit** 1 tập 60 giây theo `src/tools/credit.json` (số đoạn × model × lượt dự kiến), ghi rõ gói Ultra/Pro.
- Rủi ro Veo của hướng đó (ví dụ: đám đông, hành động nhanh, chữ trên hình).
- **Đoạn mẫu**: prompt cho 1 đoạn 8 giây tiêu biểu. Ultra: Linh chạy bằng Lite Lower Priority (0 credit). Pro: Lite (10 credit).

## Trình cho Linh
Bảng so sánh 3 hướng (1 dòng/hướng), đánh dấu hướng Claude khuyến nghị và lý do; nói rõ có thể trộn (ví dụ: truyện hướng 1, hình hướng 3).

## Sau khi Linh chọn
Ghi quyết định và trạm:
```
python LAB016-PHIM-NGAN-AI/src/tools/nhat_ky.py LAB016-PHIM-NGAN-AI/data/<tap> ghi --buoc de_xuat --loai huong_truyen \
  --chu-de "Hướng series" --chon h2 --phuong-an "h1: ..." "h2: ..." "h3: ..." --ly-do "<lời Linh>" --linh-duyet
python LAB016-PHIM-NGAN-AI/src/tools/nhat_ky.py LAB016-PHIM-NGAN-AI/data/<tap> duyet de_xuat --nguoi Linh
```
Rồi sang `sd-series`.
