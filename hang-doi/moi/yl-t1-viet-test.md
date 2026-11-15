may: may-2
loai: code
tran_phut: 40
theo_doi: C:\linhx\ifagent-wt\T1
phu_thuoc: yl-a1-gop-b

Phiếu T1 Yên Lam: CHỈ viết test mới, KHÔNG sửa code sản phẩm. Chạy mọi lệnh ở tiền cảnh; mỗi 5 phút phải có file mới hoặc commit trong C:\linhx\ifagent-wt\T1.
1. `git -C C:\linhx\ifagent fetch --all`. Nếu origin/agy/yl-a1-gop-b chưa có thì dừng, ghi CHUA_CO_NEN. `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\T1 -b agy/yl-t1-test origin/agy/yl-a1-gop-b`, rồi `git checkout origin/claude/nop-phat-hanh -- .handoff/yen-lam-dong-hanh/NOP` (lấy TIEU-CHUAN-NGHIEM-THU.md, CHUAN/, KHUNG/; không sửa các file này).
2. Đọc NOP/**/TIEU-CHUAN-NGHIEM-THU.md, mục "test mới phải viết và khoá trước khi sửa". Viết đúng 3 nhóm, mỗi test có comment đầu "Tiêu chí: ..." trích nguyên câu tiêu chuẩn:
   (1) Cách ly khách A/B: ảnh, bìa, tạp chí, phiên; khách thường không vào API quản trị. Một test cho mỗi API.
   (2) 5 lỗi kiosk "Nhắn Lam": (a) không hiện câu trả lời chữ; (b) câu thứ 2 không gửi được khi Lam đang nói; (c) trang bị đẩy lên, mất logo, đầu Lam sát mép; (d) lịch sử trò chuyện trống; (e) câu khai mạc mở thẻ "Vé". Mỗi lỗi một E2E Playwright.
   (3) Script đo chuẩn 9 (số từ/màn, cỡ chữ, vùng chạm, tương phản, so ảnh với KHUNG/ 1080×1920) với ngưỡng lấy từ TIEU-CHUAN/CHUAN, không tự đặt ngưỡng.
   Đặt test vào thư mục test mới riêng (vd `apps/lab/test/nghiem-thu-rc6/`), không đụng test có sẵn.
3. Chạy cả 3 nhóm trên code hiện tại. Kỳ vọng: (2) ĐỎ cả 5; (1),(3) đỏ hay xanh đều ghi thật. Test nào xanh mà lỗi vẫn còn theo bài chấm RC5 thì test đó sai, viết lại.
4. Ghi `sha256` từng file test vào `apps/lab/test/nghiem-thu-rc6/KHOA.sha256`. Commit, push `agy/yl-t1-test`.
CẤM: sửa code sản phẩm, sửa test cũ, sửa TIEU-CHUAN/CHUAN/KHUNG, deploy, in khoá/mật khẩu. Trạng thái cao nhất REVIEW.
Trả lời KET-QUA.md (ngắn): SHA đỉnh; bảng file test | số test | đỏ/xanh trên code hiện tại | tiêu chí trích; ngưỡng chuẩn 9 lấy từ file nào.
