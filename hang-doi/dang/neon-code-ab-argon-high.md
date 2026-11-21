may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 30
theo_doi: C:\linhx\wt-neon-ab-argon-high
khoa: viec/neon-ab/nghiem-thu/test_lich.py.khoa
lenh_kiem: python -m pytest viec/neon-ab/nghiem-thu -q
vung: viec/neon-ab/lam/**
nhan: may-2 2026-11-21T10:10:26+0700

## Mục tiêu
Viết `viec/neon-ab/lam/lich.py` theo `viec/neon-ab/DE-BAI.md`, qua đủ 29 test trong `viec/neon-ab/nghiem-thu/test_lich.py`.
## Chuẩn bị
Chạy tiền cảnh: `git clone -b claude/project-thread-ptzcqp https://github.com/fyzdfyzd/linhx-engine C:\linhx\wt-neon-ab-argon-high` (đã có thì `git -C C:\linhx\wt-neon-ab-argon-high pull`). Làm mọi việc trong thư mục đó.
## File được sửa
Chỉ `viec/neon-ab/lam/lich.py` (tạo mới). Commit cục bộ một lần khi xong, KHÔNG push.
## Cấm động
Không sửa `viec/neon-ab/nghiem-thu/**` hay file `.khoa`, không cài thư viện, không chạy nền, không dùng thợ con. Kẹt quá 20 phút: DỪNG, ghi test nào còn trượt và vì sao.
## Test bằng chứng
`python -m pytest viec/neon-ab/nghiem-thu -q` trong clone, phải thấy `29 passed`. KET-QUA ≤ 10 dòng: số test đạt, số lần chạy test, số dòng lich.py.
