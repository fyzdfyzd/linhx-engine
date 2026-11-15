phieu: hd-code-model-b
may: may-2
trang_thai: xong
tep_doi: (khong)
drive: (khong)
phut: 32.85
token: vao=440114 ra=93065

Đã hoàn thành trực tiếp trên `C:\linhx\wt-model` và push lên nhánh `claude/project-thread-jowxv1` (không đụng `C:\linhx\hang-doi`).

### 1. Cờ model thật & các file đã cập nhật
- **Cờ headless thật của `agy`**: `--model <id>` (kiểm từ `agy --help` và chạy thật).
- **Các file chính**:
  - [model-theo-loai.json](file:///C:/linhx/wt-model/runner/model-theo-loai.json): bảng ánh xạ 8 tiền tố loại việc `<du-an>-<loai>-<viec>` (`dp`, `code`, `test`, `trien`, `gop`, `do`, `td`, `kiem`).
  - [linhx_runner.py](file:///C:/linhx/wt-model/runner/linhx_runner.py): chọn model theo thứ tự `model:` header → tiền tố đoạn thứ 2 trong tên phiếu → `LINHX_MODEL` trong `tho.env` → giữ `AGY_ARGS` cũ; kiểm tên model chỉ nhận `[A-Za-z0-9._-]` (chặn tiêm cờ); model lạ không có trong `agy models` thì ghi cảnh báo vào `KET-QUA.md` và chạy mặc định (`mac-dinh`); tự chèn câu nhắc chạy tiền cảnh vào cuối mọi đề; bộ canh mặc định `khong_tien_phut = 20`, tính là có tiến khi có file đổi đệ quy trong `theo_doi` hoặc tổng CPU cây tiến trình `agy` tăng trong 2 phút gần nhất.
  - [hang_doi_git.py](file:///C:/linhx/wt-model/runner/hang_doi_git.py): ghi dòng `model: <id thật dùng>` lên đầu `KET-QUA.md` mỗi phiếu và kèm cảnh báo nếu rơi về mặc định.
  - [test_model_phieu.py](file:///C:/linhx/wt-model/runner/test_model_phi
...[cat bot]...
0839d29b4606e7bef18a25d220`

### 5. Kết quả chạy thử tiền cảnh 2 model thật
- **`gemini-pro-orchestrator`** (`agy -p "trả lời: ok" --model gemini-pro-orchestrator --output-format json`): **NHẬN** (`exit 0`, `status: "SUCCESS"`, `response: "ok\n"`, `duration_seconds: 6.81`, `input_tokens: 15887`, `output_tokens: 187`).
- **`gemini-4-hydrogen-low`** (`agy -p "trả lời: ok" --model gemini-4-hydrogen-low --output-format json`): **NHẬN** (`exit 0`, `status: "SUCCESS"`, `response: "ok\n"`, `duration_seconds: 2.18`, `input_tokens: 15644`, `output_tokens: 30`).
