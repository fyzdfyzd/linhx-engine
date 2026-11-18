may: may-3
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: D:\linhx\nhat-ky\yl12-email-vao; D:\linhx\ifagent-wt\yl12-email-vao
nhan: may-3 2026-11-18T15:01:16+0700

Phiếu Yên Lam `yl12-email-vao` (Linh 14:58 18/11): ĐỒNG HÀNH vào bằng EMAIL, không mật khẩu, để BTC thu được danh sách khách. ĐỌC TRƯỚC `viec/yen-lam-v09/DE-BAI-SUA-NHANH.md` (luật chung, chống chuyển nền, cấm).
Chạy tiền cảnh, ghi `D:\linhx\nhat-ky\yl12-email-vao\tien-do.log`, mỗi mục xong COMMIT + PUSH. Phút 30 dừng việc mới, chụp ảnh, push, ghi CON_LAI.
0. fetch; `git -C D:\linhx\ifagent worktree add D:\linhx\ifagent-wt\yl12-email-vao -b agy/yl12-email-vao origin/agy/yl10-gop` (b375c03b). Nối node_modules.
Hiện trạng (đã đọc code): danh tính = cookie thiết bị `yl_tb` → hồ sơ `khach` trong SQLite server; email xác nhận bằng mã 6 số (`server/v1/khach/email.js`, bảng `email_xac_nhan`), chỉ bắt ở hỏi/bình luận phiên và tạp chí; đăng ảnh, lưu phiên, chat Yên Lam KHÔNG cần email.
VIỆC:
1. Cổng email đơn giản: lần đầu khách làm việc tương tác (gửi chat Yên Lam, Đăng ảnh, Lưu phiên, hỏi/bình luận, tạo tạp chí, Của tôi) thì hiện tấm nhỏ "Nhập email để tiếp tục" (1 ô email + tên tuỳ chọn + 1 nút, có dòng đồng ý lưu thông tin cho BTC). KHÔNG mật khẩu, KHÔNG bắt nhập mã. Xem lịch, bảng tin, diễn giả vẫn xem tự do không cần email.
2. Lưu email vào hồ sơ `khach` của thiết bị (server, SQLite; cột email + thời điểm + nguồn), KHÔNG lưu email ở localStorage (localStorage chỉ giữ cờ giao diện). Mọi dữ liệu khách tạo (ảnh đăng bảng tin, chat, phiên đã lưu, câu hỏi, tạp chí) đã gắn khach_id, nên gắn theo email qua hồ sơ. Ảnh bảng tin hiện tên/chữ đầu email đã che (vd "li***@gmail.com" không hiện, chỉ hiện tên nếu có).
3. AN TOÀN: email CHƯA xác nhận chỉ gắn vào hồ sơ của thiết bị đang dùng; KHÔNG gộp sang hồ sơ khác và KHÔNG cho xem dữ liệu của hồ sơ khác cùng email. Muốn mở lại hồ sơ trên máy khác thì mới dùng mã 6 số sẵn có (giữ luồng cũ, là tuỳ chọn trong Của tôi).
4. Admin: trang quản trị BTC có mục "Khách" liệt kê email, tên, thời điểm, số ảnh/câu hỏi/phiên lưu, nút xuất CSV (dùng lại lien-he.csv nếu hợp). Chỉ BTC đã đăng nhập xem được.
5. Không đổi CSS kính; tấm email dùng class sẵn có, chụp 390×844 @2x trước/sau: chat lần đầu → tấm email → gửi được.
Test mới: (a) chưa email thì POST chat/ảnh/lưu trả mã yêu cầu email, có email thì qua; (b) email lưu server, không có trong localStorage; (c) hai thiết bị cùng email chưa xác nhận KHÔNG thấy dữ liệu của nhau; (d) CSV admin có email. Chạy thêm test khoá liên quan từng tệp.
Cuối: push `agy/yl12-email-vao`. KHÔNG deploy. KET-QUA theo DE-BAI-SUA-NHANH.

nhip: 15:40 39p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
