may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 1
theo_doi: C:\linhx\ifagent-wt\ev-xuong-4
phu_thuoc: ev-vo-web-3
nhan: may-2 2026-11-16T23:57:34+0700

Phiếu cụm event.ifagent.net (ev-xuong-4). Bàn giao: C:\linhx\hang-doi\viec\event-ifagent\BAN-GIAO.md (nhánh hang-doi, chỉ đọc). Khung đã duyệt + chữ đã duyệt: C:\linhx\hang-doi\viec\event-ifagent\khung\ (TK-3/4/5 và SP-DOC-CHU-TK-*). Chữ trên màn lấy nguyên văn từ SP-DOC-CHU.
0. `git -C C:\linhx\ifagent fetch --all`. `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\ev-xuong-4 -b agy/ev-xuong-4 origin/agy/ev-vo-web-3`. Nếu origin/agy/ev-vo-web-3 chưa có thì dừng, ghi CHUA_CO_NEN. Trong apps/event: `npm ci` (hoặc npm i nếu ci lỗi).
1. Merge --no-ff origin/claude/project-thread-9fhyvw (xưởng ý tưởng Tuân Du 194e6299). Xung đột: lõi theo nền hiện tại, giữ route xưởng.
2. Hoàn tất: nút tải PDF đề xuất (pdfkit, khung 15) và gửi PDF qua mail dùng lớp mail giả lập trong test (không gửi thật).
3. /thu nhận ?nguon=yen-lam&ma=<mã>: gọi đổi mã theo lõi (GET /api/yl/v1/ngoai/sang-event/:ma qua EVENT_IFAGENT_KEY, test dùng giả lập) để điền sẵn tên, công ty, email; mã sai/hết hạn thì form trống, không lỗi. /thu và /de-xuat KHÔNG còn 404, nút "Thử cho công ty bạn" dẫn vào xưởng thật (bỏ dẫn về Sắp ra mắt cho xưởng; 3 demo Idea Generation thành chạy).
4. Test e2e mới cho 2 và 3. npm test + e2e xưởng. Push agy/ev-xuong-4.

LUẬT CHUNG cụm event (mọi phiếu ev-*):
- Chạy mọi lệnh ở TIỀN CẢNH, KHÔNG background task, không chờ tiến trình nền. Mỗi 5 phút phải có file mới hoặc commit trong thư mục theo_doi.
- Chỉ làm trong worktree của phiếu này. Chỉ sửa apps/event/ và infra/staging/stg-event/. KHÔNG đụng apps/lab, packages/, nhánh Yên Lam (qdzzr4, agy/yl-*), việc brand, thư mục worktree khác.
- `git fetch` báo lock thì đợi 20 giây thử lại (thợ khác dùng chung clone gốc).
- Merge thường, không force-push, không rebase nhánh người khác. Push nhánh agy/<mã phiếu> của mình.
- CẤM: deploy (staging hay prod), gửi mail thật, in khoá/mật khẩu, xoá dữ liệu, sửa/xoá test cũ, tự sinh ảnh/video bằng AI, gọi AI thật (dùng giả lập như test). Màn chưa có khung duyệt (NOP thiết kế TK-1..TK-5) thì không dựng, ghi CHUA_CO_KHUNG.
- Lỗi môi trường đã biết của npm test: 9 lỗi (clip nhân vật không trong git, Mùi Phở). Lỗi mới khác thì sửa code, không sửa test.
- Playwright: dùng chromium có sẵn trên máy; nếu playwright đòi bản khác, đặt PW_CHROMIUM tới chrome.exe có sẵn.
- Ảnh bằng chứng: PNG fullPage ở 1280 và 360 rộng, ≤ 600 KB mỗi tấm, đặt trong bang-chung/<mã phiếu>/ của nhánh và commit.
- KET-QUA.md ngắn: dòng đầu `dat: co` hoặc `dat: khong`; SHA đỉnh; số pass/fail npm test và e2e (nếu chạy); danh sách xung đột đã gỡ (tệp + cách gỡ); việc còn dở.
- Bộ quét bí mật của runner đang báo nhầm các dòng CŨ (apps/lab/..., apps/event/test/e2e/platform.test.js:38, apps/veew-booth/..., infra/staging/stg-event/...) vì mốc so sánh là HEAD clone gốc. KHÔNG sửa/xoá các tệp đó. Không thêm khoá thật vào bất kỳ tệp nào. Nếu phiếu bị đánh "phát hiện bí mật" chỉ với các dòng cũ này thì phiếu sửa chỉ cần kiểm `git diff <base phiếu>..HEAD` không có bí mật mới, ghi vào KET-QUA, xong.

nhip: 00:18 21p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
