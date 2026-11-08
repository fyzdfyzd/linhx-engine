# Phương án A · Code Thuần (`03_OPC_OS/A_CODE/`)

## 1. Nguyên tắc Kiến trúc
- Toàn bộ luồng vận hành được nối cứng bằng code tất định thông qua Event Bus:
  `Tạo đơn -> Sinh QR VietQR -> Xác thực Webhook SePay -> Tính lá số (astro-engine) -> Ghép kho lời giải (report-core) -> Gọi API mô hình AI đúng 1 lượt ở bước viết lời dẫn -> Kiểm 17 luật + Chống AI slop -> Xuất PDF -> Hiển thị PDF trên trang đơn -> Ghi sổ S1a-HKD & Báo đỏ 400 triệu`.
- **Ưu điểm**: Tốc độ nhanh, chi phí token AI cực thấp (chỉ 1 lượt gọi mỗi đơn), độ ổn định và tính tái lập (determinism) đạt 100%.
- **Nhược điểm**: Khi gặp ca lạ ngoài kịch bản (khách nhắn tin báo sửa giờ sinh bằng ngôn ngữ tự nhiên hoặc hỏi sâu về mối liên hệ giữa các hành tinh trong báo cáo vừa mua), mẫu trả lời tĩnh không giải quyết triệt để mà phải đẩy lên hàng đợi cho người thật.

## 2. Cách chạy
```powershell
D:\LINHX\LINHX-OPC\OPC001-CHIEMTINH-VN\src\astro-engine\.venv\Scripts\python.exe A_CODE/chay_a.py
```
