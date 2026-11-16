# Kế hoạch cài 3 máy công ty

## Sáng 14/11: agy dựng runner (máy công ty DESKTOP-PVHR2CD)
1. Claude mở Remote Control trên máy công ty và giao agy H1, sau đó H2, H3, H4 chạy song song. Mất khoảng 2 giờ.
2. Claude chấm rồi mở PR runner. Linh merge trước tối nay.

## Tối 14/11: Linh cài, khoảng 15 phút mỗi máy
Làm máy công ty hiện tại trước, chạy thử ổn rồi mới làm 2 máy kia.

**0. Chuẩn bị máy** (computer use cần màn hình luôn mở)
- Windows tự đăng nhập, tắt khoá màn hình, đặt Power ở chế độ Never sleep.
- Cài Git, Python 3.12, Google Drive for desktop (ổ G:, đăng nhập cùng một tài khoản Google trên cả 3 máy).
- agy đã đăng nhập (xem mục "Cần chốt").

**1. Cài runner** (mở PowerShell thường, không cần quyền Admin)
```
git clone https://github.com/fyzdfyzd/linhx-engine D:\linhx\hang-doi
cd D:\linhx\hang-doi
powershell -ExecutionPolicy Bypass -File runner\cai-may.ps1 -May may-1
```
Lần đầu git sẽ hỏi đăng nhập GitHub, chọn đăng nhập qua trình duyệt. Máy 2 và máy 3 dùng `-May may-2`, `-May may-3`.
(`cai-may.ps1` tự clone vào `D:\linhx\hang-doi` nếu thư mục chưa có, chặn nhầm sang `D:\LINHX\LINHX-ENGINE`, tạo `runner\tho.env`, giới hạn `agy` trong `D:\linhx` và đăng ký lịch `LINHX-HangDoi` chạy mỗi phút khi user đã đăng nhập qua `chay-an-tho.vbs`.)

**2. Thử**: nhắn Claude "ping may-1" (mẫu tại `runner/phieu-mau/ping.md`, đẩy lên `hang-doi/moi/ping-may-1.md`). Trong 3 phút sẽ có `hang-doi/xong/ping-may-1/KET-QUA.md` trả về.

## Cần chốt trước khi cài
- Tên Windows của 2 máy mới.
- agy dùng tài khoản nào trên mỗi máy. Nếu cả 3 máy chung một gói thì cũng chung hạn mức: hết một lần là cả 3 máy cùng dừng (lỗi 429 đã gặp ngày 10/11).
