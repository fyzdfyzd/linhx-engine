# Hạng rủi ro hộp thư

Chỉ số chính: **xanh** tự gửi ở mức tự chủ 3 · **vàng** luôn cần duyệt · **đỏ** chỉ Linh xử lý · luật khớp theo thứ tự, luật đầu tiên trúng thì dừng.

Agent được sửa nhãn bằng `hop-thu-gan` khi luật bắt sai, kèm lý do; lý do được ghi để Linh xem lại và chỉnh luật.

```json
{
 "nhan": [
  {"nhan": "spam", "hang": "do", "hanh_dong": "an", "mau": ["http://", "https://", "bit.ly", "kiếm 5 triệu", "inbox mình link", "tại nhà"]},
  {"nhan": "brand", "hang": "do", "hanh_dong": "chuyen_linh", "mau": ["hợp tác", "booking", "báo giá", "quảng cáo", "tài trợ"]},
  {"nhan": "hoi_ai", "hang": "vang", "mau": ["ai thật", "là người thật", "có người đứng sau", "bot à", "là máy à"]},
  {"nhan": "phan_nan", "hang": "vang", "mau": ["thất vọng", "nhàm", "chán quá", "tệ", "lừa"]},
  {"nhan": "hoi", "hang": "vang", "mau": ["?", "được không", "sai ở đâu", "làm sao"]},
  {"nhan": "khen", "hang": "xanh", "mau": ["hay quá", "cảm ơn", "lưu lại", "❤️", "😂", "đúng cảnh"]}
 ],
 "mac_dinh": {"nhan": "khac", "hang": "vang"}
}
```
