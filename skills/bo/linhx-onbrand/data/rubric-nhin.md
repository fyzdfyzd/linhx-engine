# Rubric Claude nhìn (logo 25 điểm, hình ảnh và bố cục 15 điểm)

Mở ảnh thiết kế cạnh `01-logo/` và `06-ung-dung/` của brand. Mỗi câu chấm 0, 0.5 hoặc 1. Điểm mục = trung bình × tối đa.
Không đoán: chỗ nào không nhìn rõ thì ghi "không xác định" và chấm 0.5.

## Logo (25)
1. Đúng hình logo gốc: không vẽ lại, không méo tỉ lệ, không xoay.
2. Đúng biến thể theo nền (màu trên nền tối, một màu trắng trên nền xanh, v.v. theo `logo.bien_the`).
3. Màu các phần logo đúng chuẩn, không đổi màu tuỳ ý.
4. Chừa vùng an toàn quanh logo, không bị chữ, ảnh hay mép khung lấn.
5. Kích thước đủ đọc, vị trí hợp lý (thường là góc hoặc trục giữa), không có hiệu ứng cấm (bóng, viền, gradient).

## Hình ảnh và bố cục (15)
1. Ảnh người đúng phong cách `hinh_anh.phong_cach`.
2. Hoạ tiết, icon đúng `do_hoa` (không dùng hoạ tiết lạ).
3. Phân cấp chữ rõ: một tiêu đề chính, chữ phụ nhỏ hơn, không quá 3 cỡ.
4. Bố cục thoáng, căn lề nhất quán, giống tinh thần ấn phẩm mẫu.

## Chữ và nội dung khi là file ảnh
Script không đọc được font trong PNG/JPG. Khi đó Claude chấm thêm:
- chu (20): kiểu chữ có giống font chuẩn không (nét, độ rộng, trọng lượng). 1 = giống, 0.5 = gần, 0 = khác hẳn.
- noi_dung (10): đọc chữ trên ảnh, còn chữ trong `noi_dung.tu_cam` thì trừ 0.25 mỗi từ; sai chính tả trừ 0.1 mỗi lỗi.

## Ghi kết quả
Viết `diem-nhin.json` rồi chạy `onbrand.py gop`:
```json
{"logo": {"diem_ty_le": 0.8, "nhan_xet": ["Logo sát mép phải, phạm vùng an toàn"]},
 "hinh_bo_cuc": {"diem_ty_le": 0.75, "nhan_xet": ["Dùng hoạ tiết sóng đúng chuẩn", "3 cỡ chữ tiêu đề, hơi rối"]}}
```
