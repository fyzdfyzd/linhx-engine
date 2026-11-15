may: may-2
loai: code
tran_phut: 30
theo_doi: C:\linhx\wt-model
phu_thuoc: nhip-can-linh-b
nhan: may-2 2026-11-15T09:19:02+0700

KHÔNG chạy lệnh nền (background): mọi lệnh chạy tiền cảnh và chờ xong.
Repo: `C:\linhx\wt-model` (chưa có: `git clone -b claude/project-thread-jowxv1 https://github.com/fyzdfyzd/linhx-engine C:\linhx\wt-model`; có rồi: `git pull`). KHÔNG sửa C:\linhx\hang-doi.

Thêm header phiếu `model: <tên>` để chọn model agy theo từng phiếu (Linh cần `gemini-4-argon-high` cho dự án Yên Lam).
1. Chạy `agy --help` (và `agy -p --help` nếu cần) để tìm đúng cờ chọn model và tên model hợp lệ. Ghi lại cờ thật vào trả lời.
2. Trong `runner/linhx_runner.py`: đọc `model:` từ meta phiếu; có thì thêm cờ model vào lệnh agy (thay cờ model sẵn có trong AGY_ARGS nếu có). Không có header thì dùng biến `LINHX_MODEL` trong tho.env nếu có, không có nữa thì giữ như cũ. Tên model chỉ nhận chữ, số, `-`, `.`, `_` (chặn chèn lệnh).
3. Test trong runner/ (không conftest, không mạng): có header, có biến môi trường, không có gì, tên model độc bị từ chối. `python -m pytest runner -q` đạt hết trừ test đường dẫn chỉ Windows.
4. Chạy thử thật một lệnh `agy -p "trả lời: ok" <cờ model> gemini-4-argon-high --output-format json` tiền cảnh, báo model có nhận không.
5. Thêm dòng `model:` vào mục Phiếu của `skills/le/hang-doi-may/SKILL.md`.
`git pull --rebase`, push. Trả lời: cờ model thật, số test, hash, kết quả chạy thử.
