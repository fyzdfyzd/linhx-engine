may: may-3
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: D:\linhx\nhat-ky\yl09-gop; D:\linhx\ifagent-wt\yl09-gop
nhan: may-3 2026-11-18T06:33:16+0700

Phiếu Yên Lam v0.9 `yl09-gop`. ĐỌC TRƯỚC: `viec/yen-lam-v09/DE-BAI.md` (luật chung 1–9, bắt buộc) trong thư mục hàng đợi của máy này (`git pull` trước).
Lượt 5 (máy 3, vì agy máy 2 không khởi động được lúc 06:09), CHẠY TIẾP, KHÔNG GỘP LẠI. Lượt 3 đã gộp xong 10 nhánh và push `origin/agy/yl09-gop`; test yl09-* đã chạy; bị runner dừng ở bước chạy test khoá vì lệnh `node --test test/nghiem-thu-rc6/*.test.js test/nghiem-thu-rc7/*.test.js` chạy quá lâu, công cụ tự chuyển nền và agy ngồi chờ.

LUẬT CHỐNG CHUYỂN NỀN (bắt buộc):
- Mỗi lệnh test chỉ chạy 1 tệp: `node --test --test-timeout=60000 test/nghiem-thu-rc6/01-....test.js > D:\linhx\nhat-ky\yl09-gop\t-<ten>.log 2>&1; Select-String -Path ... -Pattern "^# (pass|fail)"`. Không dùng `*` gộp nhiều tệp.
- Nếu công cụ báo lệnh đã chuyển nền: KHÔNG kết thúc lượt, KHÔNG ngồi chờ. Gọi ngay trạng thái lệnh đó liên tục cho tới khi xong rồi làm tiếp.
- Ghi 1 dòng vào `D:\linhx\nhat-ky\yl09-gop\tien-do.log` sau mỗi tệp test.

Việc:
1. `git -C D:\linhx\ifagent-wt\yl09-gop fetch origin`; `git -C D:\linhx\ifagent-wt\yl09-gop status`. Worktree phải ở `agy/yl09-gop` khớp origin (có thay đổi chưa commit thì commit + push trước). Máy 3 chưa có worktree thì `git -C D:\linhx\ifagent fetch --all` (chưa có clone thì clone https://github.com/fyzdfyzd/ifagent vào D:\linhx\ifagent, cài phụ thuộc apps/lab theo README) rồi `git -C D:\linhx\ifagent worktree add D:\linhx\ifagent-wt\yl09-gop agy/yl09-gop`.
2. Nếu `origin/agy/yl09-tap-chi` (đỉnh mới 11471173) hoặc `origin/agy/yl09-clip-t147` (bf5e4173) mới hơn bản đã gộp thì merge thêm, push.
3. Chạy test khoá `apps/lab/test/nghiem-thu-rc6/` và `nghiem-thu-rc7/` TỪNG TỆP theo luật trên. Đỏ thì so với nền `6291514e` (cùng tệp đó có đỏ sẵn trên nền thì ghi DO_SAN, bỏ qua); đỏ mới thì sửa code (không sửa test khoá), commit + push.
4. Tới phút 25 dù test chưa hết: nếu không có đỏ mới nào đã thấy thì DEPLOY STAGING `agy/yl09-gop` (được phép, chỉ khi máy này ĐÃ có gcloud đăng nhập sẵn và quyền SSH VM staging; nếu chưa thì KHÔNG cài, KHÔNG đăng nhập, KHÔNG đi tìm khoá: push nhánh, ghi CAN_DEPLOY_MAY2 rồi kết thúc), kiểm `/healthz` đúng SHA. KHÔNG deploy prod. Phần test chưa chạy ghi CON_LAI.
5. Chụp nhanh 2 màn sau deploy (điện thoại `/yen-lam/` 390×844, kiosk 1080×1920) vào `bang-chung/yl09-gop/`, push.
KET-QUA: dòng đầu `dat: co|khong`, SHA gộp, SHA staging, bảng test từng tệp (pass/fail/DO_SAN), CON_LAI.
CẤM: như DE-BAI luật 5. Trạng thái cao nhất REVIEW.

nhip: 06:54 21p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
