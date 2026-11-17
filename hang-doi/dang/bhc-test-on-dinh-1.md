may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 30
khong_tien_phut: 20
theo_doi: C:\linhx\ifagent-wt\bhc-on-dinh
nhan: may-2 2026-11-17T09:38:48+0700

Lưu ý máy: KHÔNG dùng background task, subagent hay thợ con; mọi lệnh chạy tiền cảnh. Gọi `npm.cmd`/`npx.cmd`. Push sau MỖI commit. Server chạy bằng Start-Process, tắt đúng PID.
Brand health check: test E2E-04 chập chờn. Claude chạy lại trên agy/bhc-nen (ffb6143) 2 lần: lần 1 đỏ, lần 2 xanh. Nguyên nhân: test/e2e-dau-cuoi.test.js dùng AI giả trễ cố định delayMs: 35, lượt 1 có thể xong trước khi lượt 2 được gửi nên lượt 2 không bao giờ phải xếp hàng.
1. Worktree C:\linhx\ifagent-wt\bhc-on-dinh, nhánh agy/bhc-on-dinh từ origin/agy/bhc-nen.
2. Sửa test (chỉ phần test và AI giả): AI giả có "cửa chặn" do test mở (vd hàm moCua()), lượt 1 bị giữ ở trạng thái running cho tới khi test đã thấy lượt 2 ở queued #1, rồi mới mở. Không dùng setTimeout/độ trễ cố định để quyết định thứ tự. Rà mọi test E2E khác có kiểu chờ theo thời gian tương tự và sửa cùng cách.
3. Luật khoá chống chập chờn: thêm script npm "test:lap" chạy các file test/e2e-*.test.js 5 lần liên tiếp, có ca nào đổi kết quả giữa các lần thì thoát lỗi với thông báo "Test chập chờn: <tên> đổi kết quả giữa lần a và b. Thay chờ theo thời gian bằng cửa chặn trong AI giả." Thêm luật lint: cấm chữ "delayMs" trong test/e2e-*.test.js, thông báo chỉ cách sửa như trên.
4. Chạy test:lap 5/5 xanh và npm.cmd run verify xanh. Log vào bang-chung/bhc-on-dinh/.
CẤM: sửa code sản phẩm ngoài AI giả, deploy, gọi AI thật, đụng apps/event, apps/lab, packages/. Trạng thái cao nhất REVIEW.
KET-QUA.md: `dat: co|khong`; SHA; test:lap 5 lần; verify.

nhip: 09:56 18p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
