# Đề A/B model agy: hàm đọc giờ tiếng Việt

Dùng để so model cũ (gemini-4-argon-high) với Gemini 4 Neon trên cùng một việc. Hai phiếu làm cùng đề, clone riêng.

## Mục tiêu
Viết `viec/neon-ab/lam/lich.py` có hàm `doc_gio(chuoi: str, goc: datetime) -> datetime` đọc câu hẹn giờ tiếng Việt, qua hết `viec/neon-ab/nghiem-thu/test_lich.py` (29 test).

## Luật
- Có dấu hoặc không dấu, hoa thường, thừa dấu cách đều phải hiểu.
- Buổi mặc định: sáng 8:00, trưa 12:00, chiều 14:00, tối 19:00. Có ngày mà không có giờ, không có buổi: 9:00.
- "chiều"/"tối" + giờ < 12 thì cộng 12.
- Chỉ có giờ: hôm nay nếu còn sau `goc`, không thì ngày mai.
- `dd/mm` đã qua trong năm thì sang năm sau. Thứ trùng hôm nay thì tuần sau. "thứ 2".."thứ 7", "chủ nhật", "mai", "ngày kia", "nay", "N tiếng nữa", "N phút nữa".
- Câu không hiểu, ngày/giờ sai, chuỗi rỗng: `ValueError`.
- Chỉ dùng thư viện chuẩn Python. Không sửa `goc`.

## Định nghĩa xong
`python -m pytest viec/neon-ab/nghiem-thu -q` ra 29 passed, không sửa file test hay `.khoa`.
