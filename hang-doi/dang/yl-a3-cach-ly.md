may: may-2
loai: code
tran_phut: 40
theo_doi: C:\linhx\ifagent-wt\A3
phu_thuoc: yl-a1-gop
nhan: may-2 2026-11-15T08:40:17+0700

Phiếu A3 Yên Lam: test cách ly dữ liệu khách. Chạy mọi lệnh ở tiền cảnh. Được dùng thợ con nhưng tất cả làm trong C:\linhx\ifagent-wt\A3.
1. `git -C C:\linhx\ifagent fetch --all`, `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\A3 -b agy/yl-a3-cach-ly origin/agy/yl-a1-gop`.
2. Tìm trong apps/lab mọi API trả dữ liệu của một khách: ảnh, bìa AGENTIC:ME, tạp chí, phiên; và mọi API quản trị (/quan-tri, btc). Lập bảng route → file:dòng.
3. Viết test mới `apps/lab/test/a3-cach-ly.test.js` (node:test, chạy server test như các test sẵn có): với mỗi API, khách A (phiên/cookie A) gọi tài nguyên của khách B → phải 403/404, không lộ dữ liệu B; khách thường gọi API quản trị → 401/403.
4. Test đỏ ở route nào thì SỬA route đó (kiểm quyền sở hữu), mỗi route một commit. Không sửa test sẵn có, không nới test mới cho xanh.
5. Chạy test mới + test lab đủ (`node --test --test-concurrency=2 --test-timeout=120000 test/*.test.js`), lưu log thô vào thư mục phiếu.
6. Push `agy/yl-a3-cach-ly`. Không push nền.
CẤM: deploy, gửi mail, in khoá/mật khẩu, xoá dữ liệu, sửa test cũ. Trạng thái cao nhất REVIEW.
Trả lời KET-QUA.md: bảng route | có test | trước sửa | sau sửa; SHA đỉnh; số pass/fail lab đủ; tiêu chí "mỗi API có test và xanh" ĐẠT/KHÔNG.
