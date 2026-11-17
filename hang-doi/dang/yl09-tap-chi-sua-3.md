may: may-3
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: D:\linhx\nhat-ky\yl09-tap-chi; D:\linhx\ifagent-wt\yl09-tap-chi
nhan: may-3 2026-11-18T04:49:15+0700

Phiếu Yên Lam v0.9 `yl09-tap-chi`. ĐỌC TRƯỚC: `viec/yen-lam-v09/DE-BAI.md` (luật chung 1–9, bắt buộc) trong thư mục hàng đợi của máy này (`git pull` trước). Khung bố cục: `viec/yen-lam-v09/khung/` ảnh P7-tao-tap-chi, P8-xem-truoc-tap-chi (chỉ bố cục, GIỮ CSS kính hiện có).
Lượt 4: TIẾP phần dở trên nhánh agy/yl09-tap-chi (worktree đã có thì vào, commit + push phần chưa commit, làm tiếp, KHÔNG tạo lại). Lượt trước quá 40 phút vì chờ bộ test đầy đủ: KHÔNG chạy cả bộ test lab, chỉ chạy test mới của phiếu + `apps/lab/test/nghiem-thu-*` liên quan, mỗi lệnh test có timeout ≤ 8 phút. Chạy mọi lệnh ở tiền cảnh, KHÔNG background task. Tạo `D:\linhx\nhat-ky\yl09-tap-chi\` và ghi 1 dòng tiến độ vào `tien-do.log` ở đó sau mỗi bước (ít nhất 5 phút một lần). COMMIT + PUSH sau mỗi ý nhỏ, phút 35 phải push dù chưa xong.
1. `git -C D:\linhx\ifagent fetch --all` (chưa có clone thì `git clone https://github.com/fyzdfyzd/ifagent D:\linhx\ifagent`). Nếu `origin/agy/yl09-dh-bang-tin-cua-toi` chưa có thì dừng, ghi CHUA_CO_NEN. `git -C D:\linhx\ifagent worktree add D:\linhx\ifagent-wt\yl09-tap-chi -b agy/yl09-tap-chi origin/agy/yl09-dh-bang-tin-cua-toi`. Cài phụ thuộc apps/lab theo README.
2. Việc: Luồng tạo tạp chí trên điện thoại, MODULE RIÊNG (thư mục riêng, trang kiosk không nạp script tạp chí: kiểm bằng test đọc HTML kiosk). Ẩn thanh tab khi đang làm. (a) Chưa có email thì xin email + đồng ý nhận. (b) 3 câu, thanh tiến độ: track quan tâm; diễn giả nhớ nhất (gợi ý trước người trong phiên khách đã lưu/đã hỏi, kèm ô tìm cả 48 người, không đổ cả 48 lên màn đầu); điều muốn mang về. Thoát giữa chừng giữ câu đã trả lời. (c) Xong 3 câu là CÓ TẠP CHÍ NGAY: xem trước 8 trang (bìa, lộ trình, diễn giả nhớ, câu đã hỏi, ảnh có bạn, điều mang về...), mỗi trang ghi nguồn dữ liệu, tóm phiên chỉ từ mô tả BTC. (d) Tối 20/11 (20:00) tự cập nhật thêm phiên/ảnh, gửi email + thông báo, có PDF A5 (dùng code tạp chí có sẵn agentic-me/csmo nếu được, chỉ tách gọi lại). Test mới: luồng 3 câu → có 8 trang; trang kiosk không tải module tạp chí.
3. Duyệt bằng mắt trên pixel theo DE-BAI luật 7 cho mọi màn đụng tới; ảnh và ảnh ghép commit vào `bang-chung/yl09-tap-chi/` (PNG ≤ 600 KB).
4. Chạy test mới của phiếu + test khoá liên quan (KHÔNG cả bộ, mỗi lệnh ≤ 8 phút, tiền cảnh). Hết giờ thì commit + push phần dở, ghi CON_LAI.
5. Push `agy/yl09-tap-chi`.
CẤM: như DE-BAI luật 5. Trạng thái cao nhất REVIEW.
Trả lời KET-QUA.md theo DE-BAI luật 9.

nhip: 05:10 21p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
