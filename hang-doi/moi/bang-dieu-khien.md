may: may-2
loai: code
tran_phut: 40
theo_doi: C:\linhx\wt-bang

Dựng bảng theo dõi web cho hàng đợi, chạy thường trực trên máy này (may-2).
Repo: `C:\linhx\wt-bang` (chưa có: `git clone -b claude/project-thread-jowxv1 https://github.com/fyzdfyzd/linhx-engine C:\linhx\wt-bang`; có rồi: `git pull`).
Yêu cầu:
- `runner/bang/bang.py`: Python stdlib (không cài thêm gói), cổng 8090, chỉ đọc. Mỗi 30 giây `git fetch` nhánh `hang-doi` vào một clone riêng `C:\linhx\bang-hang-doi`, đọc `hang-doi/moi`, `dang`, `xong/*/KET-QUA.md`.
- Một trang tối giản, tiếng Việt, tự làm mới 30 giây: (1) Đang chạy: phiếu, máy, chạy bao lâu; (2) Đang chờ; (3) Xong gần nhất 20 phiếu: trạng thái (xong/loi/dung tô màu), phút, token; (4) Mỗi máy: lần cuối nhận hoặc xong phiếu lúc nào (quá 30 phút không hoạt động thì đỏ). Bấm vào phiếu xem KET-QUA.
- Có `/api/trang-thai` trả JSON cùng dữ liệu.
- `runner/bang/cai-bang.ps1`: đăng ký Task Scheduler chạy khi đăng nhập, ẩn (dùng lại cách của chay-an-tho.vbs), mở cổng 8090 trên tường lửa cho mạng nội bộ (Private).
- Test `runner/bang/test_bang.py` với dữ liệu giả (không gọi mạng, không dùng conftest.py), chạy ở tiền cảnh, đạt hết; `python -m pytest runner -q` vẫn đạt.
- Chạy `cai-bang.ps1` trên máy này, mở http://localhost:8090 kiểm, ghi địa chỉ IP nội bộ của máy.
Chỉ đụng `runner/bang/`. Commit, push.
Trả lời: địa chỉ http://<IP>:8090, số test đạt, hash commit.
