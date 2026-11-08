# Ngưỡng và trọng số (bản 0.1, mọi chuẩn ngành là [GIẢ ĐỊNH] tới khi có nguồn)

## Trọng số điểm sức khoẻ

Social: Nhịp 15, Tương tác 25, Trụ cột 15, Chất lượng bài 20, Đúng giọng 15, Rủi ro 10.
Brand: Nhận diện hình ảnh 25 (LAB043 onbrand.py), Nhất quán đa kênh 20, Giọng và thông điệp 20, Hiện diện trên AI 20 (LAB036 brandcheck.py), Social 15.
Điểm nhóm = 100 trừ Critical 25, High 12, Medium 6, Low 2. Nhóm chưa chấm bị bỏ khỏi mẫu số và ghi rõ.

## Chuẩn theo loại brand (đặt trong brand.json > social)

| Loại | nhip_tuan | er_chuan | Ghi chú |
|---|---|---|---|
| B2B đào tạo, tư vấn | 3 | 0.02 | [GIẢ ĐỊNH] |
| Bán lẻ, F&B | 5 | 0.03 | [GIẢ ĐỊNH] |
| Cá nhân, KOL | 5 | 0.04 | [GIẢ ĐỊNH] |

## Cổng

- Dưới 20 bài: MẪU NHỎ.
- Quãng im 14 ngày Medium, 21 ngày High.
- Hơn 25% bài dính dấu văn máy: High, chuyển linhx-bien-tap (LAB049).
- Từ cấm của brand: luôn Critical. Khẳng định tuyệt đối: High, người duyệt pháp lý quyết.
