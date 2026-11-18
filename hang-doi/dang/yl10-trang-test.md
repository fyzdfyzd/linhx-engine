may: may-3
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: D:\linhx\nhat-ky\yl10-trang-test; D:\linhx\ifagent-wt\yl10-trang-test
nhan: may-3 2026-11-18T07:28:17+0700

Phiếu Yên Lam sửa nhanh `yl10-trang-test`. ĐỌC TRƯỚC: `viec/yen-lam-v09/DE-BAI-SUA-NHANH.md` và `viec/yen-lam-v09/DE-BAI.md` (git pull hàng đợi trước).
Chạy mọi lệnh ở tiền cảnh. Tạo `D:\linhx\nhat-ky\yl10-trang-test\`, ghi 1 dòng vào `tien-do.log` sau mỗi bước.
0. `git -C D:\linhx\ifagent fetch --all` (chưa có clone thì clone https://github.com/fyzdfyzd/ifagent vào D:\linhx\ifagent). `git -C D:\linhx\ifagent worktree add D:\linhx\ifagent-wt\yl10-trang-test -b agy/yl10-trang-test origin/agy/yl09-gop`. Cài phụ thuộc apps/lab (dùng lại node_modules sẵn có nếu được).
Trang KỸ THUẬT để test nhanh, sửa nhanh (Linh cần không phải đăng nhập):
1. Ghi LOG CHAT mọi lượt Lam (kiosk + đồng hành): thời gian, máy/phiên, khách nói gì (chữ), Lam trả gì, widget nào hiện, độ trễ, lỗi. Lưu DB staging, giữ 7 ngày.
2. Trang `/yen-lam/ky-thuat/<ma>`: <ma> là chuỗi ngẫu nhiên ≥ 24 ký tự đọc từ biến môi trường hoặc tệp cấu hình staging (KHÔNG commit giá trị, KHÔNG in). Không có mã đúng thì 404. Chỉ bật khi NODE_ENV/biến cho biết là staging; prod mặc định TẮT. Đó là cách "không cần đăng nhập" mà vẫn không lộ công khai.
3. Trang có 3 khối: (a) Log chat: lọc theo máy, tìm chữ, tự làm mới 5s; (b) Sửa tri thức: xem + sửa nguồn tri thức Lam (bản nén), lưu là có hiệu lực ngay cho lượt sau, giữ lịch sử 20 bản, nút quay về bản trước; (c) Bình luận: gắn bình luận vào một lượt chat hoặc một mục tri thức (người viết tự gõ tên), danh sách bình luận mới nhất.
4. Giao diện dùng lại CSS kính sẵn có, đọc tốt ở 1280×800 và 390×844.
Test: unit cho kiểm mã (sai → 404, prod → 404), lưu/khôi phục tri thức, ghi log. Ảnh 3 khối.
Trong KET-QUA ghi tên biến/tệp cấu hình chứa mã (KHÔNG ghi giá trị).
Cuối: commit + push `agy/yl10-trang-test`. CẤM như DE-BAI-SUA-NHANH. Trạng thái cao nhất REVIEW. KET-QUA theo DE-BAI-SUA-NHANH.

nhip: 07:55 27p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
