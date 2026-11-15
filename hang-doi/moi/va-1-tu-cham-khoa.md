may: may-2
loai: code
tran_phut: 40
theo_doi: C:\linhx\wt-va1
khong_tien_phut: 25
tu_sua: 1
phu_thuoc: runner-chon-model

KHÔNG chạy lệnh nền hay subagent nền: mọi lệnh tiền cảnh, làm tuần tự.
Repo: `C:\linhx\wt-va1` (chưa có: `git clone -b claude/project-thread-jowxv1 https://github.com/fyzdfyzd/linhx-engine C:\linhx\wt-va1`; có rồi: `git pull`). KHÔNG sửa C:\linhx\hang-doi. Đọc trước `viec/ra-quy-trinh/SO-SANH.md` (khâu liên quan).

Vá 1, tự chấm máy bằng bộ khoá: header mới `lenh_kiem: <lệnh>` và `khoa: <đường dẫn file .khoa>` (tương đối với thư mục theo_doi đầu tiên). Sau khi agy xong, runner (không phải agy) kiểm sha256 các file test khớp .khoa (lệch → `loi` "sửa test khoá") rồi chạy lenh_kiem trong thư mục đó, trần 15 phút; mã thoát khác 0 → `loi`, kèm 1500 ký tự cuối log vào KET-QUA. Chỉ khi đạt mới `xong`. Tham khảo cách làm của `canh/cong_kiem.py` nếu repo có. Không có header thì như cũ.
Test trong runner/ (không conftest, không mạng). `python -m pytest runner -q` đạt hết trừ test đường dẫn chỉ Windows. Cập nhật `skills/le/hang-doi-may/SKILL.md` (mục Phiếu hoặc Bài học, ngắn). `git pull --rebase`, push nhánh. Trả lời ≤1200 ký tự: làm gì, số test, hash.
Trước khi push chạy cả `python -m pytest tests/nghiem-thu -q` (CI chặn chuỗi giống bí mật, kể cả token giả trong test: ghép chuỗi lúc chạy).
