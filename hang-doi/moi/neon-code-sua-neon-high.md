may: may-2
loai: code
model: gemini-4-neon-high
tran_phut: 30
theo_doi: C:\linhx\wt-neon-sua-neon-high
khoa: viec/neon-ab/nghiem-thu-sua/test_sua.py.khoa
lenh_kiem: python -m pytest viec/neon-ab/nghiem-thu-sua -q
vung: viec/neon-ab/sua/**

## Mục tiêu
`viec/neon-ab/sua/lich.py` có nhiều lỗi. Sửa cho đúng ĐẶC TẢ `viec/neon-ab/DE-BAI.md` (không chỉ cho qua test: còn lỗi mà test không bắt, Claude sẽ chấm bằng test ẩn). Sửa tối thiểu, giữ cấu trúc cũ.
## Chuẩn bị
Chạy tiền cảnh: `git clone -b claude/project-thread-ptzcqp https://github.com/fyzdfyzd/linhx-engine C:\linhx\wt-neon-sua-neon-high` (có rồi thì pull). Làm trong thư mục đó.
## File được sửa
Chỉ `viec/neon-ab/sua/lich.py`. Commit cục bộ một lần, rồi push: `git push origin HEAD:refs/heads/agy/neon-sua-neon-high`. Push lỗi đăng nhập: ghi CAN-LINH, vẫn tính xong.
## Cấm động
Không sửa `viec/neon-ab/nghiem-thu*/**`, `.khoa`, file khác; không cài thư viện, không chạy nền, không thợ con. Kẹt quá 20 phút: DỪNG, ghi lỗi còn lại.
## Test bằng chứng
`python -m pytest viec/neon-ab/nghiem-thu-sua -q` phải `29 passed`. KET-QUA ≤ 12 dòng: danh sách lỗi đã sửa (mỗi lỗi 1 dòng, số dòng), số lần chạy test, sha commit.
