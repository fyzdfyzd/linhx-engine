may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 0
theo_doi: C:\linhx\ifagent-wt\ev-do-luong-5
phu_thuoc: ev-xuong-4
nhan: may-2 2026-11-17T01:16:01+0700
moc: 92abf865283599bdb128cdba81573bbcb8caa1a1

Phiếu cụm event.ifagent.net (ev-do-luong-5). Bàn giao: C:\linhx\hang-doi\viec\event-ifagent\BAN-GIAO.md (nhánh hang-doi, chỉ đọc). Khung đã duyệt + chữ đã duyệt: C:\linhx\hang-doi\viec\event-ifagent\khung\ (TK-3/4/5 và SP-DOC-CHU-TK-*). Chữ trên màn lấy nguyên văn từ SP-DOC-CHU.
0. `git -C C:\linhx\ifagent fetch --all`. `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\ev-do-luong-5 -b agy/ev-do-luong-5 origin/agy/ev-xuong-4`. Nếu origin/agy/ev-xuong-4 chưa có thì dừng, ghi CHUA_CO_NEN. Trong apps/event: `npm ci` (hoặc npm i nếu ci lỗi).
1. V2 tường ảnh: chỉ khi /khoi/ai-data-viz/tuong-anh có trên nhánh này: catalog/chien-dich/rap-phim-tuong-anh.json đổi trangThai "chay", campaign.name "Rạp phim mẫu · Bước vào phim"; thêm e2e /play/rap-phim-tuong-anh chuyển tới /khoi/ai-data-viz/tuong-anh. Nếu chưa có màn thì giữ sắp ra mắt, ghi CHUA_CO_MAN.
2. Đối chiếu bảng đường dẫn /khoi/... cho V1, V3, T1–T3 với route thật, ghi bảng vào bang-chung/ev-do-luong-5/duong-dan.md (không sửa tài liệu SP).
3. Hứa Chử: AR, vòng quay (vong-quay-lead, /quay), game đông người: chỉ dựng màn nào có khung TK-4 đã duyệt trong khung\ (TK-4-HOAT-DONG.md + ảnh hoat-dong); màn khác ghi CHUA_CO_KHUNG. Mỗi màn một commit + e2e.
4. npm test + e2e các khối đụng tới. Push agy/ev-do-luong-5.

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

## Lần trước trượt vì:
model: gemini-4-hydrogen-high
phieu: ev-do-luong-5
may: may-2
trang_thai: loi
tep_doi: KET-QUA.md
drive: (khong)
phut: 28.48
token: vao=567808 ra=130606

phát hiện bí mật: apps/event/test/e2e/platform.test.js:38, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:73, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:86, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:111, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:212, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:265, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:275, apps/lab/test/agentic-me-luot.test.js:126, apps/lab/test/agentic-me-noi-dung.test.js:71, apps/lab/test/agentic-me-su-kien.test.js:35, apps/lab/test/t148-quan-tri-chung.test.js:18, apps/lab/test/yen-lam-t101.test.js:13, apps/veew-booth/server/setup-kiosks.js:7, infra/staging/stg-event/GOI-LENH-DEPLOY-16-11.md:53, infra/staging/stg-event/chay-cloud.sh:23

nhip: 01:17 2p đang chờ nền · log cuối 0 phút trước [log_cuoi=2026-11-17T01:17:56+0700] · root agent idle; waiting up to 40m0s for 1 ba
