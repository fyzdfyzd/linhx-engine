may: may-2
loai: kiem
tran_phut: 10
nhan: may-2 2026-11-21T10:07:22+0700

## Mục tiêu
Xác minh agy trên máy này có model Gemini 4 Neon (ra 18/11/2026) chưa, lấy đúng id để dùng với cờ `--model`.
## File được sửa
Không sửa file nào trong repo. Chỉ được chạy lệnh cập nhật agy nếu bước 2 cần.
## Cấm động
Không sửa repo, không đổi tho.env, không đụng phiếu khác, không chạy nền. Lệnh cập nhật lỗi hoặc cần quyền Admin/đăng nhập: DỪNG, trả `CAN-LINH: ...; LENH: ...`.
## Test bằng chứng
1. Chạy tiền cảnh: `agy --version` và `agy models`. Chép NGUYÊN danh sách model.
2. Không thấy id nào chứa `neon`: chạy `agy update` (hoặc lệnh cập nhật mà `agy --help` chỉ), rồi chạy lại bước 1.
3. KET-QUA ≤ 15 dòng: dòng `NEON_ID: <id hoặc KHONG_CO>`, phiên bản agy trước/sau, danh sách model đầy đủ (một dòng, cách nhau dấu phẩy), các mức (low/high/xhigh) nếu có.
