may: may-2
loai: kiem
tran_phut: 6

## Mục tiêu
Kiểm nhanh các việc từng chặn phiếu trên máy này còn chặn không.
## File được sửa
Không sửa file nào.
## Cấm động
Chỉ chạy lệnh đọc dưới đây, tiền cảnh. Không đăng nhập, không cài, không in khoá/token/cookie. Lệnh nào treo quá 30 giây thì bỏ, ghi TREO. Chạy từng lệnh ở TIỀN CẢNH, tuyệt đối không tác vụ nền, không chờ nền.
## Test bằng chứng
1. `gh auth status` (OK nếu đã đăng nhập, chỉ ghi tên tài khoản).
2. `git ls-remote https://github.com/fyzdfyzd/ifagent HEAD` (OK nếu ra 1 dòng sha).
KET-QUA ≤ 8 dòng, mỗi lệnh một dòng: `<việc> OK|CHAN|TREO <1 cụm lý do>`.
