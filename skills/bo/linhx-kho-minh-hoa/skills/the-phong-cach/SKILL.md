---
name: the-phong-cach
description: Gom các thẻ ảnh cùng họ trong kho minh hoạ ý tưởng thành thẻ phong cách có định nghĩa, dấu hiệu nhận diện, khi dùng, khi tránh và công thức prompt {y_tuong} không dùng tên hoạ sĩ.
---
# Thẻ phong cách (M5)

Một phong cách = một thư mục `KHO/phong-cach/<id>/` (mẫu JimmyLv/awesome-nano-banana):
- `phong-cach.json` theo `../../schemas/the-phong-cach.schema.json`
- `GHI-CONG.md`: hoạ sĩ tiêu biểu (link từ `so-nguon/hat-giong.json`), link các thẻ ảnh làm bằng chứng, giấy phép nếu có
- `mau/`: ảnh tự sinh (skill `tai-tao`)

## Khi nào tạo
Họ có ≥ 5 thẻ ảnh độ chắc 3. Một họ có thể tách nhiều phong cách nếu dấu hiệu khác rõ (vd `an-du-toi-gian` tách "phẳng 2 màu" và "giấy cắt đổ bóng").

## Viết công thức (quan trọng nhất)
- Khuôn `{y_tuong}` như sdxl_prompt_styler: `"<mô tả phong cách> depicting {y_tuong}. <bố cục>. <màu>. <điều cấm>"`.
- Chỉ tả tính chất nhìn thấy: số màu, kiểu nét, khoảng trắng, nhân vật, ánh sáng, chất liệu. **Không** "in the style of <tên người>", không tên hoạ sĩ, không tên tài khoản.
- Có `negative`: những thứ làm hỏng phong cách (gradient, chi tiết thừa, chữ…).
- `co_che_hop`: cơ chế ý tưởng hay đi cùng phong cách này (đếm từ thẻ ảnh).
- `loi_hay_gap`: lỗi mô hình sinh ảnh hay mắc với phong cách này (điền sau khi `tai-tao`).

Mẫu đã viết sẵn: `mau-the/` cạnh file này (3 thẻ khởi đầu, viết từ hiểu biết, cần đối chiếu thẻ ảnh thật).
