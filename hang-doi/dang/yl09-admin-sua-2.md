may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
phu_thuoc: yl09-widget
theo_doi: C:\linhx\nhat-ky\yl09-admin; C:\linhx\ifagent-wt\yl09-admin
nhan: may-2 2026-11-18T04:42:00+0700

Phiếu Yên Lam v0.9 `yl09-admin`. ĐỌC TRƯỚC: `viec/yen-lam-v09/DE-BAI.md` (luật chung 1–9, bắt buộc) trong thư mục hàng đợi của máy này (`git pull` trước). Khung bố cục: `viec/yen-lam-v09/khung/` ảnh A1-admin-mot-man (chỉ bố cục, GIỮ CSS kính hiện có).
Lượt 3. Lượt trước quá 40 phút vì chờ bộ test đầy đủ: KHÔNG chạy cả bộ test lab, chỉ chạy test mới của phiếu + `apps/lab/test/nghiem-thu-*` liên quan, mỗi lệnh test có timeout ≤ 8 phút. Chạy mọi lệnh ở tiền cảnh, KHÔNG background task. Tạo `C:\linhx\nhat-ky\yl09-admin\` và ghi 1 dòng tiến độ vào `tien-do.log` ở đó sau mỗi bước (ít nhất 5 phút một lần). COMMIT + PUSH sau mỗi ý nhỏ, phút 35 phải push dù chưa xong.
1. `git -C C:\linhx\ifagent fetch --all` (chưa có clone thì `git clone https://github.com/fyzdfyzd/ifagent C:\linhx\ifagent`). Nếu `origin/agy/yl09-widget` chưa có thì dừng, ghi CHUA_CO_NEN. `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\yl09-admin -b agy/yl09-admin origin/agy/yl09-widget`, rồi `git merge origin/agy/yl09-dh-bang-tin-cua-toi` (để thông báo hiện ở Bảng tin). Cài phụ thuộc apps/lab theo README.
2. Việc: Admin BTC một màn (nền là bản lite 5 tab hiện có). Sau đăng nhập test-btc: 4 khối. Cần duyệt: tab Ảnh / Câu hỏi có đếm, lưới ảnh nhỏ chọn nhiều + "Duyệt N" / "Ẩn", ảnh bị lọc an toàn gắn cờ (vd trẻ em) có nhãn. Kiosk & widget: danh sách máy (lượt, bìa, mất kết nối bao lâu), chọn máy → công tắc từng widget (dùng API phiếu yl09-widget), cấp mã máy. Gửi thông báo: soạn, chọn nơi nhận (điện thoại, kiosk), gửi ngay / hẹn giờ → hiện ở Bảng tin (ghim) và widget Thông báo BTC. Hôm nay: khách mở đồng hành, bìa đã chụp, câu hỏi, % ngân sách AI. Mọi tab cũ gom vào menu "Nâng cao". Đăng nhập dùng tài khoản test có sẵn trên máy (không in mật khẩu). Test mới: E2E đăng nhập → duyệt 2 ảnh → tắt 1 widget → gửi 1 thông báo, đều thấy kết quả ở phía khách/kiosk.
3. Duyệt bằng mắt trên pixel theo DE-BAI luật 7 cho mọi màn đụng tới; ảnh và ảnh ghép commit vào `bang-chung/yl09-admin/` (PNG ≤ 600 KB).
4. Chạy test mới của phiếu + test khoá liên quan (KHÔNG cả bộ, mỗi lệnh ≤ 8 phút, tiền cảnh). Hết giờ thì commit + push phần dở, ghi CON_LAI.
5. Push `agy/yl09-admin`.
CẤM: như DE-BAI luật 5. Trạng thái cao nhất REVIEW.
Trả lời KET-QUA.md theo DE-BAI luật 9.

nhip: 05:12 30p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
