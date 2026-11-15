may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 40
khong_tien_phut: 25
tu_sua: 1
theo_doi: C:\linhx\wt-model
phu_thuoc: hd-code-model-b
nhan: may-2 2026-11-15T10:09:12+0700

KHÔNG dùng background task, KHÔNG sinh thợ con; mọi lệnh tiền cảnh. Repo `C:\linhx\wt-model` (git pull nhánh claude/project-thread-jowxv1). KHÔNG sửa C:\linhx\hang-doi.
Vá bộ canh "không tiến" trong `runner/linhx_runner.py` (nối tiếp hd-code-model-b):
1. Kiểm `agy --help`: có `--output-format stream-json` (hoặc tương tự xuất sự kiện liên tục) không. Có thì runner chạy agy với luồng sự kiện, mỗi sự kiện mới = nhịp tim; ghi kết quả cuối như cũ (KET-QUA không đổi khuôn).
2. Agy in "waiting ... for N background task(s)" mà cây tiến trình còn CPU hoặc còn nhịp → coi là đang tiến, chờ tới tran_phut, không giết.
3. Chỉ dừng "không tiến" khi CẢ: không file đổi trong theo_doi, không nhịp, CPU cây tiến trình không tăng, trong khong_tien_phut phút.
4. Test trong runner/ (không mạng, giả lập tiến trình/luồng sự kiện). `python -m pytest runner -q` và `python -m pytest tests/nghiem-thu -q` đạt.
`git pull --rebase`, push. Trả lời: có cờ stream-json không (dòng help thật), số test, hash.
