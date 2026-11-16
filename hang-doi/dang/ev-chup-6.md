may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 1
theo_doi: C:\linhx\ifagent-wt\ev-chup-6
phu_thuoc: ev-do-luong-5
nhan: may-2 2026-11-17T01:36:45+0700

Phiếu cụm event.ifagent.net (ev-chup-6). Bàn giao: C:\linhx\hang-doi\viec\event-ifagent\BAN-GIAO.md (nhánh hang-doi, chỉ đọc). Khung đã duyệt + chữ đã duyệt: C:\linhx\hang-doi\viec\event-ifagent\khung\ (TK-3/4/5 và SP-DOC-CHU-TK-*). Chữ trên màn lấy nguyên văn từ SP-DOC-CHU.
0. `git -C C:\linhx\ifagent fetch --all`. `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\ev-chup-6 -b agy/ev-chup-6 origin/agy/ev-do-luong-5`. Nếu origin/agy/ev-do-luong-5 chưa có thì dừng, ghi CHUA_CO_NEN. Trong apps/event: `npm ci` (hoặc npm i nếu ci lỗi).
1. Chạy đủ `npm run test:all` trong apps/event (tiền cảnh; nếu quá 25 phút thì chạy từng tệp e2e một, ghi log từng tệp). Log thô vào bang-chung/ev-chup-6/.
2. Chụp PNG fullPage ở 1280 và 360 (máy chủ test như scripts/web-chup.js, đổi bề rộng 390/1440 thành 360/1280 bằng tham số hoặc bản sao script trong bang-chung): /, /demo, /giai-phap, một trang giải pháp, một trang demo, /blog, một bài blog, /case, /lien-he, /goi, /mau, /thu, /de-xuat, /tao/, /tao/agency.html, /play/tiec-cuoi-nam, /play/rap-phim-photobooth, 404. Seed demo qua POST /api/admin/su-kien/demo/seed trên máy chủ test trước khi chụp /play.
3. Ghép tờ tổng quan bang-chung/ev-chup-6/TONG-1280.png và TONG-360.png (lưới thu nhỏ mọi trang, ≤ 2 MB mỗi tờ).
4. Push agy/ev-chup-6. KET-QUA thêm danh sách trang lỗi/trắng/tràn ngang ở 360.

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

nhip: 01:39 3p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
