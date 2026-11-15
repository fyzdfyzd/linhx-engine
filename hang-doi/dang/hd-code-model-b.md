may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 40
khong_tien_phut: 25
tu_sua: 1
theo_doi: C:\linhx\wt-model
nhan: may-2 2026-11-15T09:36:13+0700

KHÔNG dùng background task, KHÔNG sinh thợ con: tự làm trực tiếp, mọi lệnh chạy tiền cảnh và chờ xong. (Lần trước phiếu runner-chon-model bị dừng vì agy chờ 1 background task tới 10 phút.)
Repo: `C:\linhx\wt-model` (chưa có: `git clone -b claude/project-thread-jowxv1 https://github.com/fyzdfyzd/linhx-engine C:\linhx\wt-model`; có rồi: `git pull`, giữ phần lần trước đã làm nếu đúng). KHÔNG sửa C:\linhx\hang-doi.

1. Chọn model theo phiếu (`runner/linhx_runner.py`), thứ tự ưu tiên: header `model:` → tiền tố loại việc trong tên phiếu → biến `LINHX_MODEL` trong tho.env → giữ AGY_ARGS như cũ. Cờ headless là `--model <id>` (kiểm bằng `agy --help`, `agy models`; ghi cờ thật). Tên model chỉ nhận chữ, số, `-`, `.`, `_`.
2. Bảng tiền tố ở file `runner/model-theo-loai.json` (tên phiếu dạng `<du-an>-<loai>-<viec>`, lấy đoạn thứ 2):
   {"dp":"gemini-pro-orchestrator","code":"gemini-pro-orchestrator","test":"gemini-4-argon-high","trien":"gemini-4-argon-high","gop":"gemini-4-hydrogen-high","do":"gemini-4-hydrogen-high","td":"gemini-4-hydrogen-high","kiem":"gemini-4-hydrogen-low"}
   Model không có trong `agy models` thì ghi cảnh báo vào KET-QUA và chạy model mặc định, không lỗi.
3. Ghi dòng `model: <id thật dùng>` vào đầu KET-QUA.md mỗi phiếu.
4. Chống dừng oan: runner tự chèn cuối mọi đề câu "Không dùng background task hay thợ con trừ khi phiếu cho phép; chạy lệnh tiền cảnh." Bộ canh "không tiến" tính là CÓ tiến khi: có file đổi trong theo_doi (đệ quy) HOẶC tổng CPU của cây tiến trình agy tăng trong 2 phút gần nhất. Mặc định khong_tien_phut = 20.
5. Test trong runner/ (không conftest, không mạng): header, tiền tố, biến môi trường, không gì, tên độc bị từ chối, model lạ → mặc định, câu chèn có trong đề, CPU tăng = có tiến. `python -m pytest runner -q` và `python -m pytest tests/nghiem-thu -q` đạt (trừ test đường dẫn chỉ Windows nếu chạy ngoài Windows).
6. Chạy thật tiền cảnh: `agy -p "trả lời: ok" --model gemini-pro-orchestrator --output-format json` và với gemini-4-hydrogen-low; báo nhận hay không.
7. Sửa mục Phiếu trong `skills/le/hang-doi-may/SKILL.md`: dòng `model:`, quy ước tên `<du-an>-<loai>-<viec>`, bảng tiền tố.
`git pull --rebase`, push claude/project-thread-jowxv1. Trả lời: cờ model thật, danh sách `agy models`, số test, hash, kết quả chạy thử 2 model.
