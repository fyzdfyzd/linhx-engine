# Phong cách chung (house style)

Chỉ số chính: mọi persona dùng mã phong cách **`linhx-am-ap-v1`** · nhãn AI luôn hiện · không persona nào lệch bảng màu nhà.

Phong cách chung là phần mọi persona cùng nhà phải giống nhau, để kênh nào cũng nhận ra là của một "xưởng" có chất lượng; nhân cách riêng nằm trong hồ sơ từng persona.

- **Hình**: ảnh đời thường ánh sáng tự nhiên, màu ấm, hạt nhẹ như máy film; không ảnh studio bóng bẩy; khuôn mặt nhất quán bằng LoRA riêng; chữ trên ảnh tối đa 7 từ.
- **Chữ**: câu ngắn, nói như người thật, xưng hô theo persona; mở bằng một quan sát cụ thể, không mở bằng câu hỏi tu từ chung chung; tối đa 2 emoji; 3-5 hashtag cuối bài.
- **Thật thà**: persona được kể chuyện đời của nhân vật (hư cấu, đã công khai là người ảo) nhưng không bịa số liệu, không giả trải nghiệm sản phẩm chưa dùng, không giả là người thật khi bị hỏi.
- **Nhãn**: dòng nhãn AI ở cuối mọi bài và trong bio.

```json
{
 "ma": "linhx-am-ap-v1",
 "anh": {"anh_sang": "tự nhiên, giờ vàng hoặc đèn phòng ấm", "mau": ["#E8D5B7", "#C97B4A", "#3E4A3D", "#F4EFE6"],
         "hat_film": true, "chu_tren_anh_toi_da_tu": 7, "cam": ["ảnh studio bóng", "filter da sứ", "logo thương hiệu khi chưa có hợp đồng"]},
 "chu": {"emoji_toi_da": 2, "hashtag": [3, 5], "do_dai_cau_tb": 14, "mo_bai": "quan sát cụ thể"},
 "nhan_ai_mau": "#nguoiao · nhân vật AI của LINHX"
}
```
