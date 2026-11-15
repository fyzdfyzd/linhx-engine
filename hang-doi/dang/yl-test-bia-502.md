may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 30
khong_tien_phut: 20
tu_sua: 1
theo_doi: C:\linhx\ifagent-wt\yl-test-bia-502
nhan: may-2 2026-11-15T13:36:40+0700

LUẬT CHẠY: KHÔNG chạy `npm run dev`/server riêng; test tự dựng createApp trong tiến trình; mọi lệnh tiền cảnh, bọc timeout ≤ 300 s; mỗi 5 phút có file mới/commit trong theo_doi.

Phiếu TEST (chỉ viết test, KHÔNG sửa code sản phẩm) cho lỗi agy chấm RC5 bắt: `POST /agentic-me/tao` mất 22–67 s, proxy cắt trả 502, màn khách báo lỗi dù bìa đã tạo xong.
1. `git -C C:\linhx\ifagent fetch --all`, `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\yl-test-bia-502 -b agy/yl-test-bia-502 origin/agy/yl-test-t1`.
2. Đọc route tạo bìa (tìm `agentic-me/tao` trong apps/lab), màn chờ AM-03b (`.handoff/yen-lam-dong-hanh/NOP/2c-BAN-GIAO/am03b/AM-03b-DEM-LUI.md`), cấu hình proxy/Caddy trong infra (timeout). Ghi bảng file:dòng.
3. Viết `apps/lab/test/nghiem-thu-rc6/04-bia-khong-502.test.js` (comment đầu "Tiêu chí: Tạo bìa lâu tới 90 giây không làm màn khách báo lỗi; khách luôn nhận đúng bìa của mình."), giả lập máy tạo bìa chậm 70 s (thay hàm tạo bằng hàm chờ, không gọi AI thật), mỗi ý một test:
   (a) mọi yêu cầu HTTP của luồng tạo bìa trả lời ≤ 10 s (không request nào treo tới ngưỡng proxy);
   (b) màn khách (Playwright 1080×1920) hiện màn chờ đếm lùi suốt 70 s, không hiện chữ lỗi;
   (c) khi xong, màn hiện đúng bìa của khách đó (không bìa mẫu, không bìa người khác);
   (d) tải lại trang giữa chừng thì vẫn quay về đúng việc đang tạo.
4. Chạy trên code hiện tại: ghi đỏ/xanh thật. Kỳ vọng (a) đỏ. Ghi sha256 file mới vào thêm 1 dòng KHOA.sha256 (không đổi 3 dòng cũ). Commit, push `agy/yl-test-bia-502`.
CẤM: sửa code sản phẩm, sửa test cũ, deploy, gọi AI thật, in khoá. Trạng thái cao nhất REVIEW.
Trả lời KET-QUA.md (ngắn): dòng đầu `dat: co`/`dat: khong`; SHA; bảng route/proxy file:dòng; bảng test đỏ/xanh.

nhip: 13:51 15p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
