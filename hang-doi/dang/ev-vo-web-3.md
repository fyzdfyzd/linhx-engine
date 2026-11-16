may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 1
theo_doi: C:\linhx\ifagent-wt\ev-vo-web-3
phu_thuoc: ev-gop-nen-2
nhan: may-2 2026-11-16T23:06:07+0700

Phiếu cụm event.ifagent.net (ev-vo-web-3). Bàn giao: C:\linhx\hang-doi\viec\event-ifagent\BAN-GIAO.md (nhánh hang-doi, chỉ đọc). Khung đã duyệt + chữ đã duyệt: C:\linhx\hang-doi\viec\event-ifagent\khung\ (TK-3/4/5 và SP-DOC-CHU-TK-*). Chữ trên màn lấy nguyên văn từ SP-DOC-CHU.
0. `git -C C:\linhx\ifagent fetch --all`. `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\ev-vo-web-3 -b agy/ev-vo-web-3 origin/agy/ev-gop-nen-2`. Nếu origin/agy/ev-gop-nen-2 chưa có thì dừng, ghi CHUA_CO_NEN. Trong apps/event: `npm ci` (hoặc npm i nếu ci lỗi).
1. Làm mục 2–5 "Việc còn lại" trong apps/event theo NOP/BAN-GIAO-BUILD-TRUONG-LIEU.md (Phụ lục A trong BAN-GIAO.md): TK-5 gồm 404 (câu phụ, nút Về trang chủ + Thử cho công ty bạn), trang lỗi chung 500 (try/catch quanh trangMoi), thẻ demo Sắp ra mắt 3 trạng thái (lead nhan demo-cho-<slug>, localStorage), OG 1200×630 (scripts/web-og.js chụp, gắn t.og cho blog/case/demo); mail lienhe@ifagent.net ở chân trang và /lien-he; đường gọn /tao/ → /tao/index.html và /agency → /tao/agency.html. Chữ đúng nguyên văn trong bàn giao, không tự viết chữ mới.
2. Mỗi ý một commit có test e2e mới (đỏ trước, xanh sau) trong test/e2e/.
3. npm test + `node --test test/e2e/web-vo.test.js` + test mới. Push agy/ev-vo-web-3.

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

nhip: 23:27 21p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
