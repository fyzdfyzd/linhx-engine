may: may-3
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: D:\linhx\nhat-ky\yl09-e2e; D:\linhx\ifagent-wt\yl09-e2e
phu_thuoc: yl09-gop

Phiếu Yên Lam v0.9 `yl09-e2e`. ĐỌC TRƯỚC: `viec/yen-lam-v09/DE-BAI.md` (luật chung 1–9, bắt buộc) trong thư mục hàng đợi của máy này (`git pull` trước).
Lượt 5. Lượt trước quá 40 phút vì chờ bộ test đầy đủ: KHÔNG chạy cả bộ test lab, chỉ chạy test mới của phiếu + `apps/lab/test/nghiem-thu-*` liên quan, mỗi lệnh test có timeout ≤ 8 phút. Chạy mọi lệnh ở tiền cảnh, KHÔNG background task. Tạo `D:\linhx\nhat-ky\yl09-e2e\` và ghi 1 dòng tiến độ vào `tien-do.log` ở đó sau mỗi bước (ít nhất 5 phút một lần). COMMIT + PUSH sau mỗi ý nhỏ, phút 35 phải push dù chưa xong.
1. `git -C D:\linhx\ifagent fetch --all` (chưa có clone thì `git clone https://github.com/fyzdfyzd/ifagent D:\linhx\ifagent`). Nếu KET-QUA yl09-gop ghi CAN_DEPLOY_MAY2 (staging chưa lên bản gộp) thì dừng, ghi CHUA_CO_STAGING. `git -C D:\linhx\ifagent worktree add D:\linhx\ifagent-wt\yl09-e2e -b agy/yl09-e2e origin/agy/yl09-gop`. Cài phụ thuộc apps/lab theo README.
2. Việc: E2E trên staging bản yl09-gop, duyệt bằng mắt trên pixel. Không sửa code. Ba vai: (1) khách mới trên điện thoại 390×844 (Chrome Android giả lập + Safari iPhone 14 nếu có webkit): mở /yen-lam/ → làm quen → hỏi Lam 5 câu (có câu ra widget) → Lịch (ngày, track, tìm, trang phiên, lưu, .ics) → Diễn giả → Bảng tin cuộn 3 lần → Của tôi → tạo tạp chí 3 câu → xem 8 trang; (2) khách tại kiosk 1080×1920: chờ → nói chuyện → chụp (đồng ý, 3-2-1, giả lập lỗi xa) → chọn track → bìa + QR → quét QR mở điện thoại; nhận mặt giả lập; (3) BTC admin: đăng nhập test-btc, duyệt, tắt widget, gửi thông báo, thấy ở kiosk/điện thoại. Mỗi màn chụp PNG đúng khung và ghép cạnh `khung/*.jpg` tương ứng. Soi từng ảnh ở 100% theo DE-BAI luật 7. KET-QUA: bảng mỗi màn (đạt/lỗi, điểm 1–10, ảnh ghép), danh sách lỗi xếp CHẶN/NẶNG/NHẸ có bước lặp lại, tối đa 15 lỗi, lỗi CHẶN trước. Ảnh để `bang-chung/yl09-e2e/` trong nhánh `agy/yl09-e2e` (PNG ≤ 600 KB).
3. Duyệt bằng mắt trên pixel theo DE-BAI luật 7 cho mọi màn đụng tới; ảnh và ảnh ghép commit vào `bang-chung/yl09-e2e/` (PNG ≤ 600 KB).
4. Chạy test mới của phiếu + test khoá liên quan (KHÔNG cả bộ, mỗi lệnh ≤ 8 phút, tiền cảnh). Hết giờ thì commit + push phần dở, ghi CON_LAI.
5. Push `agy/yl09-e2e`.
Máy 3 không có tài khoản test-btc thì bỏ vai (3), ghi THIEU_TK_BTC, KHÔNG đi tìm hay in mật khẩu.
LUẬT CHỐNG CHUYỂN NỀN: mỗi lệnh test hay Playwright chỉ chạy 1 tệp, ghi log ra tệp. Nếu công cụ báo lệnh đã chuyển nền thì KHÔNG kết thúc lượt và KHÔNG ngồi chờ: gọi trạng thái lệnh đó liên tục tới khi xong (lượt trước của yl09-gop bị dừng vì ngồi chờ).
CẤM: như DE-BAI luật 5. Trạng thái cao nhất REVIEW.
Trả lời KET-QUA.md theo DE-BAI luật 9.
