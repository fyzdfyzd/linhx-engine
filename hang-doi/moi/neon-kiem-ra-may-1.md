may: may-1
loai: kiem
tran_phut: 6

## Mục tiêu
Kiểm nhanh các việc từng chặn phiếu trên máy này còn chặn không.
## File được sửa
Không sửa file nào.
## Cấm động
Chỉ chạy lệnh đọc dưới đây, tiền cảnh. Không đăng nhập, không cài, không in khoá/token/cookie. Lệnh nào treo quá 30 giây thì bỏ, ghi TREO.
## Test bằng chứng
1. `browsentic status` (OK nếu bridge chạy và nối Chrome).
2. `Get-NetTCPConnection -LocalPort 8000 -State Listen` (ghi tên tiến trình đang giữ cổng 8000, hoặc TRONG).
3. `"D:\linhx\tools\rclone\rclone.exe" listremotes` (OK nếu có `hfcd:`).
KET-QUA ≤ 8 dòng, mỗi lệnh một dòng: `<việc> OK|CHAN|TREO <1 cụm lý do>`.
