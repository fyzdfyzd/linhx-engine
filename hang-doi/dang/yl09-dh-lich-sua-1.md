may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\nhat-ky\yl09-dh-lich; C:\linhx\ifagent-wt\yl09-dh-lich
phu_thuoc: yl09-dh-khung
nhan: may-2 2026-11-18T02:39:52+0700

Phiếu Yên Lam v0.9 `yl09-dh-lich`. ĐỌC TRƯỚC: `viec/yen-lam-v09/DE-BAI.md` (luật chung 1–9, bắt buộc) trong thư mục hàng đợi của máy này (`git pull` trước). Khung bố cục: `viec/yen-lam-v09/khung/` ảnh P2-lich-phien, P3-lich-dien-gia, P4-trang-phien (chỉ bố cục, GIỮ CSS kính hiện có).
Lượt 2 (lượt 1 bị huỷ dây chuyền hoặc quá giờ). Chạy mọi lệnh ở tiền cảnh, KHÔNG background task. Tạo `C:\linhx\nhat-ky\yl09-dh-lich\` và ghi 1 dòng tiến độ vào `tien-do.log` ở đó sau mỗi bước (ít nhất 5 phút một lần). COMMIT + PUSH sau mỗi ý nhỏ, phút 35 phải push dù chưa xong.
1. `git -C C:\linhx\ifagent fetch --all` (chưa có clone thì `git clone https://github.com/fyzdfyzd/ifagent C:\linhx\ifagent`). Nếu `origin/agy/yl09-dh-khung` chưa có thì dừng, ghi CHUA_CO_NEN. `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\yl09-dh-lich -b agy/yl09-dh-lich origin/agy/yl09-dh-khung`. Cài phụ thuộc apps/lab theo README.
2. Việc: Tab Lịch gộp phiên + diễn giả + đã lưu (gộp /lich, /dien-gia, lịch riêng). (a) Đoạn chọn Phiên / Diễn giả / Đã lưu. (b) Phiên: chọn ngày (19/11: 21 phiên, 20/11: 20), chip track có đếm, ô tìm (phiên, diễn giả, chủ đề), nhóm theo khung giờ; khung có nhiều phiên song song thì hàng vuốt ngang; tự cuộn tới khung "Đang diễn ra" (giả lập giờ bằng `?gio=2026-11-19T13:24`). Màn đầu phải thấy ≥ 3 khung giờ, không bị video Lam chiếm chỗ. (c) Diễn giả: lưới 3 cột, ảnh 80px, thiếu ảnh hiện chữ cái đầu trên nền kính sẵn có; tìm trong 48 người; lọc Diễn giả / Dẫn dắt. Ảnh nhỏ webp ≤ 20 KB, lazy. (d) Trang phiên: tiêu đề đầy đủ, track · phòng · giờ, người nói, nút Lưu và nhắc, Thêm vào lịch máy (.ics tải được, mở đúng trên iOS/Android: kiểm định dạng VEVENT, TZID Asia/Ho_Chi_Minh), câu hỏi cho diễn giả có bình chọn (qua lọc an toàn + BTC duyệt như hiện có), thảo luận. Test mới: .ics hợp lệ; 41 phiên hiện đủ; tìm "GEO" ra đúng phiên.
3. Duyệt bằng mắt trên pixel theo DE-BAI luật 7 cho mọi màn đụng tới; ảnh và ảnh ghép commit vào `bang-chung/yl09-dh-lich/` (PNG ≤ 600 KB).
4. Chạy test lab đủ (`node --test --test-concurrency=2 --test-timeout=120000 test/*.test.js` trong apps/lab) và test khoá nghiem-thu-*; không thêm lỗi mới so với nền. Hết giờ thì commit + push phần dở, ghi CON_LAI.
5. Push `agy/yl09-dh-lich`.
CẤM: như DE-BAI luật 5. Trạng thái cao nhất REVIEW.
Trả lời KET-QUA.md theo DE-BAI luật 9.

nhip: 03:17 38p đang chờ nền · log cuối 0 phút trước [log_cuoi=2026-11-18T03:17:17+0700] · root agent idle; waiting up to 40m0s for 1 ba
