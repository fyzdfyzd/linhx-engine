---
name: tai-tao
description: Sinh ảnh mẫu cho từng thẻ phong cách trong kho minh hoạ ý tưởng bằng công thức {y_tuong} với 3 đề chuẩn, để xem nhanh và so sánh công bằng; ghi lỗi hay gặp.
---
# Tái tạo ảnh mẫu (M6)

Ảnh trong kho là ảnh **ta tự sinh**, không phải ảnh của hoạ sĩ (cách của JimmyLv/awesome-nano-banana).

## 3 đề chuẩn (giữ nguyên để so phong cách với nhau)
1. `de-1-qua-tai`: "một người làm việc quá sức, kiệt sức vì deadline"
2. `de-2-ai-con-nguoi`: "con người và AI cùng làm việc"
3. `de-3-tiet-kiem`: "tiết kiệm tiền từng chút một"

## Mỗi thẻ phong cách
1. Với mỗi đề, Claude chọn 1 cơ chế trong `co_che_hop` và viết ý hình cụ thể (vd đề 1 + `a-la-b`: "người là cây nến cháy cả hai đầu"). Thay vào `{y_tuong}`.
2. Sinh ảnh bằng công cụ Linh đang có: Google Flow / Nano Banana, ChatGPT Image, hoặc agy. Không thêm tên hoạ sĩ vào prompt dù công cụ gợi ý.
3. Lưu `KHO/phong-cach/<id>/mau/<de>.png`, ghi prompt cuối cùng vào `mau/<de>.txt`.
4. Linh chấm mỗi ảnh "đúng chất / gần / sai". Sai thì sửa công thức, ghi vào `loi_hay_gap`, thêm mô hình vào `mo_hinh_da_thu`.
5. Phong cách có giấy phép yêu cầu ghi nguồn khi phỏng theo (vd Sketchplanations) thì ghi dòng nguồn ngay trên ảnh.
