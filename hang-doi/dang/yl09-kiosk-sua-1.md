may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\nhat-ky\yl09-kiosk; C:\linhx\ifagent-wt\yl09-kiosk
nhan: may-2 2026-11-18T02:04:24+0700

Phiếu Yên Lam v0.9 `yl09-kiosk`. ĐỌC TRƯỚC: `viec/yen-lam-v09/DE-BAI.md` (luật chung 1–9, bắt buộc) trong thư mục hàng đợi của máy này (`git pull` trước). Khung bố cục: `viec/yen-lam-v09/khung/` ảnh K1-tro-chuyen, K2-nhan-ra-khach, K3-chup, K3b-chon-track, K4-bia-qr (chỉ bố cục, GIỮ CSS kính hiện có).
Lượt 2 (lượt 1 bị huỷ dây chuyền hoặc quá giờ). Chạy mọi lệnh ở tiền cảnh, KHÔNG background task. Tạo `C:\linhx\nhat-ky\yl09-kiosk\` và ghi 1 dòng tiến độ vào `tien-do.log` ở đó sau mỗi bước (ít nhất 5 phút một lần). COMMIT + PUSH sau mỗi ý nhỏ, phút 35 phải push dù chưa xong.
1. Worktree `C:\linhx\ifagent-wt\yl09-kiosk` ĐÃ CÓ từ lượt 1 (nhánh agy/yl09-kiosk). Vào đó, `git status`; có thay đổi chưa commit thì commit "lượt 1 dở" + push ngay. Đọc `hang-doi/xong/yl09-kiosk/NHAT-KY.md` để biết đã làm gì, chỉ làm phần còn thiếu. Không có worktree thì tạo lại từ origin/agy/yl09-kiosk (hoặc origin/yl-full-17-11 nếu nhánh chưa có).
2. Việc: Kiosk MỘT trang (gộp kiosk-lam và chụp bìa booth thành một luồng, route chính `/yen-lam/csmo/kiosk-lam`; route booth cũ chuyển hướng về đây). Giữ logo Le Bros. Không gỡ cờ thu_nghiem. (a) Chờ → K1 trò chuyện giọng (Live hiện có), lời Lam ≥ 54px, bong bóng kính; nút lớn "Chụp bìa cùng Lam". 90 s im lặng về chờ, xoá lịch sử chat phiên khách. (b) K2 nhận ra khách: nhận mặt bằng YuNet/SFace có sẵn (modules/bia), ĐẶC TRƯNG MẶT NẠP SẴN vào kiosk lúc khởi động và làm mới mỗi 5 phút, CHỈ của khách đã bật đồng ý sinh trắc (API trả danh sách đặc trưng, không trả ảnh); khớp thì Lam chào tên + phiên đã lưu sắp tới. QR đồng hành giơ vào camera là đường dự phòng. (c) Chụp: màn đồng ý 2 nút lớn ("Đồng ý, chụp thôi" / "Để sau"), câu "Ảnh chỉ dùng làm bìa của bạn, tự xoá sau 30 ngày" → đếm 3-2-1 → không thấy mặt/đứng xa thì Lam "Lại gần chút nhé" và đếm lại. (d) K3b chờ bìa 10–15 s: Lam hỏi "bạn quan tâm mảng nào", 4 nút track lớn (Toàn thể, Olive, Lavender, Iris), chọn hoặc nói; KHÔNG bắt chọn trong 48 diễn giả. Lỗi tạo bìa: Lam xin lỗi, mời chụp lại. (e) K4 bìa lớn + QR (mở đồng hành `?bia=` vào tab Của tôi), 60 s về chờ. (f) Tải trước asset (clip Lam t146, ảnh, font) theo phiên bản, màn "đang chuẩn bị", mở lần 2 < 1 s không khung đen. Test mới: một lượt chụp giả lập ≤ 60 s; khớp mặt giả lập chào đúng tên; khách chưa đồng ý không có trong danh sách nạp.
3. Duyệt bằng mắt trên pixel theo DE-BAI luật 7 cho mọi màn đụng tới; ảnh và ảnh ghép commit vào `bang-chung/yl09-kiosk/` (PNG ≤ 600 KB).
4. Chạy test lab đủ (`node --test --test-concurrency=2 --test-timeout=120000 test/*.test.js` trong apps/lab) và test khoá nghiem-thu-*; không thêm lỗi mới so với nền. Hết giờ thì commit + push phần dở, ghi CON_LAI.
5. Push `agy/yl09-kiosk`.
CẤM: như DE-BAI luật 5. Trạng thái cao nhất REVIEW.
Trả lời KET-QUA.md theo DE-BAI luật 9.

nhip: 02:19 15p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
