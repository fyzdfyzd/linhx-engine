may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 40
khong_tien_phut: 25
tu_sua: 1
theo_doi: C:\linhx\ifagent-wt\T1
phu_thuoc: yl-gop-a1d
nhan: may-2 2026-11-15T11:06:57+0700

Phiếu T1 Yên Lam: CHỈ viết test mới, KHÔNG sửa code sản phẩm. Chạy mọi lệnh ở tiền cảnh; mỗi 5 phút phải có file mới hoặc commit trong C:\linhx\ifagent-wt\T1.
1. `git -C C:\linhx\ifagent fetch --all`. Nếu origin/agy/yl-a1-gop-b chưa có thì dừng, ghi CHUA_CO_NEN. `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\T1 -b agy/yl-test-t1 origin/agy/yl-a1-gop-b`, rồi `git checkout origin/claude/nop-phat-hanh -- .handoff/yen-lam-dong-hanh/NOP` (lấy TIEU-CHUAN-NGHIEM-THU.md, CHUAN/, KHUNG/; không sửa các file này).
2. Đọc NOP/**/TIEU-CHUAN-NGHIEM-THU.md, mục "test mới phải viết và khoá trước khi sửa". Viết đúng 3 nhóm, mỗi test có comment đầu "Tiêu chí: ..." trích nguyên câu tiêu chuẩn:
   (1) A3 cách ly: với MỖI API /api/yl/v1/khach/*, khách A không đọc/sửa/xoá được dữ liệu khách B (hồ sơ, ảnh, bìa, tạp chí, phiên, lịch sử chat); khách không gọi được /api/yl/v1/qt/*; phiên quản trị chỉ thấy đúng quyền vai đó. Một test cho mỗi API.
   (2) A2 kiosk Nhắn Lam, mỗi ý một E2E Playwright 1080×1920: (a) gửi câu chữ → câu trả lời chữ hiện trong lịch sử ≤ 8 giây; (b) gửi câu 2 khi Lam đang nói → được nhận hoặc hiện đúng "Lam đang nói, chờ chút nhé", không nằm im trong ô; (c) mở bàn phím → logo và đầu Lam vẫn trong khung, trang không trượt (boundingBox trước/sau); (d) "Lịch sử trò chuyện" đủ các lượt vừa nói; (e) hỏi "Lễ khai mạc lúc mấy giờ?" → mở thẻ Khai mạc, không mở thẻ Vé.
   (3) A6 script đo mức 9, xuất bảng số, số trượt là đỏ: mỗi màn khách ≤ 12 từ; chữ kiosk ≥ 28 px; nút kiosk ≥ 96 px, vùng chạm ≥ 72 px (điện thoại ≥ 48 px); tương phản ≥ 4,5:1 (axe 0 lỗi nặng); chuyển màn 200–400 ms; CLS ≤ 0,1; so ảnh với KHUNG/2c-K-AM lệch bố cục ≤ 2%. Ngưỡng đúng như trên, không tự đổi.
   Không đụng màn chờ AM-03b (đã có kịch bản trong 43921412).
   Đặt test vào thư mục test mới riêng (vd `apps/lab/test/nghiem-thu-rc6/`), không đụng test có sẵn.
3. Trước khi chạy test lab: `npm i --no-save ws` trong packages/character. Chạy cả 3 nhóm trên code hiện tại. Kỳ vọng: (2) ĐỎ cả 5; (1),(3) đỏ hay xanh đều ghi thật. Test nào xanh mà lỗi vẫn còn theo bài chấm RC5 thì test đó sai, viết lại.
4. Ghi `sha256` từng file test vào `apps/lab/test/nghiem-thu-rc6/KHOA.sha256`. Commit, push `agy/yl-test-t1`.
CẤM: sửa code sản phẩm, sửa test cũ, sửa TIEU-CHUAN/CHUAN/KHUNG, deploy, in khoá/mật khẩu. Trạng thái cao nhất REVIEW.
Trả lời KET-QUA.md (ngắn): SHA đỉnh; bảng file test | số test | đỏ/xanh trên code hiện tại | tiêu chí trích; ngưỡng chuẩn 9 lấy từ file nào.

nhip: 11:19 12p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
