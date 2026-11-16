may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 0
theo_doi: C:\linhx\ifagent-wt\ev-gop-nen-2
nhan: may-2 2026-11-16T23:03:12+0700
moc: 069917e4a23596caff0a3bfa9190019b43afa14b

Phiếu cụm event.ifagent.net (ev-gop-nen-2). Bàn giao: C:\linhx\hang-doi\viec\event-ifagent\BAN-GIAO.md (nhánh hang-doi, chỉ đọc). Khung đã duyệt + chữ đã duyệt: C:\linhx\hang-doi\viec\event-ifagent\khung\ (TK-3/4/5 và SP-DOC-CHU-TK-*). Chữ trên màn lấy nguyên văn từ SP-DOC-CHU.
0. `git -C C:\linhx\ifagent fetch --all`. `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\ev-gop-nen-2 -b agy/ev-gop-nen-2 origin/claude/project-thread-es2prv`. Nếu origin/claude/project-thread-es2prv chưa có thì dừng, ghi CHUA_CO_NEN. Trong apps/event: `npm ci` (hoặc npm i nếu ci lỗi).
1. Merge --no-ff lần lượt (mỗi lần một commit "gộp: <phần> <sha>"): origin/claude/project-thread-en6gul (lõi 935d69ec), origin/claude/project-thread-939spi (Mãn Sủng 2e855f45), origin/claude/project-thread-2oqsoe (Hứa Chử 3682b414), origin/claude/project-thread-a9kpr7 (Tào Nhân 59938a3e), origin/claude/project-thread-fyw6pv (vỏ web 51c39a05), origin/claude/event-noi-dung (nội dung 7c09dd0). KHÔNG gộp project-thread-9fhyvw (xưởng, phiếu sau).
2. Xung đột: giữ cả hai ý; catalog/ theo Mãn Sủng; server/routes/api.js theo lõi en6gul; noi-dung/blog + case theo event-noi-dung; package-lock thì chạy lại npm i. Ghi từng xung đột vào KET-QUA.
3. Trong apps/event chạy `npm run test:audit` và `npm test` (tiền cảnh, log thô vào bang-chung/ev-gop-nen-2/). Lỗi mới do gộp thì sửa code.
4. Push agy/ev-gop-nen-2.

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

## Lần trước trượt vì:
model: gemini-4-hydrogen-high
phieu: ev-gop-nen-2
may: may-2
trang_thai: loi
tep_doi: KET-QUA.md
drive: (khong)
phut: 5.28
token: vao=130973 ra=12737

phát hiện bí mật: apps/event/test/e2e/platform.test.js:38, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:73, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:86, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:111, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:212, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:265, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:275, apps/lab/test/agentic-me-luot.test.js:126, apps/lab/test/agentic-me-noi-dung.test.js:71, apps/lab/test/agentic-me-su-kien.test.js:35, apps/lab/test/t148-quan-tri-chung.test.js:18, apps/lab/test/yen-lam-t101.test.js:13, apps/veew-booth/server/setup-kiosks.js:7, infra/staging/stg-event/GOI-LENH-DEPLOY-16-11.md:53, infra/staging/stg-event/chay-cloud.sh:23
