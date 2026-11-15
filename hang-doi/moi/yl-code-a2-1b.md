may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 1
theo_doi: C:\linhx\ifagent-wt\yl-code-a2-1b
phu_thuoc: yl-khoa-t1

LUẬT CHẠY (bắt buộc, lượt trước mất 80 phút vì treo chờ tác vụ nền): KHÔNG chạy `npm run dev`, `npm start` hay server lab riêng. Test khoá tự dựng server trong tiến trình (createApp), cứ chạy `node --test --test-timeout=120000 <file>` tiền cảnh. Chụp ảnh/quay video: viết 1 script node tự dựng createApp trong tiến trình, chụp xong tự đóng server và thoát (process.exit), chạy tiền cảnh. Mọi lệnh bọc timeout ≤ 300 s. Nếu buộc phải chạy nền: ghi log vào thư mục theo_doi và tự tắt khi xong.

Phiếu A2 Yên Lam, kiosk "Nhắn Lam" (/yen-lam/csmo/kiosk-lam), ý a,b. Chạy mọi lệnh ở tiền cảnh, KHÔNG dùng background task, mỗi 5 phút phải có file mới hoặc commit trong thư mục theo_doi.
1. `git -C C:\linhx\ifagent fetch --all`. Nếu origin/agy/yl-test-t1 chưa có thì dừng, ghi CHUA_CO_NEN. `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\yl-code-a2-1b -b agy/yl-code-a2-1b origin/agy/yl-test-t1`, rồi `git checkout origin/claude/nop-phat-hanh -- .handoff/yen-lam-dong-hanh/NOP` (chỉ đọc).
2. Đọc khung 2c-K-AM và CHU-TREN-MAN trong NOP/KHUNG, RUBRIC.md, LOI-DA-BAT.md.
3. Việc (mỗi ý một commit, tiêu đề "A2(a,b): ..."): (a) câu trả lời của Lam hiện bằng chữ trong lịch sử ≤ 8 giây, đúng vị trí khung; (b) gửi câu 2 khi Lam đang nói thì được nhận hoặc hiện đúng "Lam đang nói, chờ chút nhé", không nằm im trong ô.
4. Giữ nguyên các móc test: window.__kl.may.{hoiChu,tiengDau,clipHet,trangThai}, window.__kl.moChat (test khoá gọi chúng). Không cần làm xanh 03-a6-do-muc-9 (đang viết lại riêng). Test khoá: các test ý a,b trong apps/lab/test/nghiem-thu-rc6/ phải từ ĐỎ thành XANH. Chỉ sửa code sản phẩm. Thiếu test thì viết test mới ngoài nghiem-thu-rc6.
5. Bằng chứng trong C:\linhx\ifagent-wt\yl-code-a2-1b\bang-chung\yl-code-a2-1b\ và commit vào nhánh: ảnh 1080×1920 mỗi ý (PNG ≤ 600 KB), ẢNH GHÉP khung|bản dựng cạnh nhau cùng tỉ lệ (`ghep-<ý>.png`), 1 video Playwright recordVideo một lượt (để ngoài git, chép G:\My Drive\yen-lam\yl-code-a2-1b\ nếu có ổ G:).
6. Chạy test lab đủ (`node --test --test-concurrency=2 --test-timeout=120000 test/*.test.js`, trước đó `npm i --no-save ws` trong packages/character), log thô vào bang-chung. Lỗi mới ngoài 9 lỗi môi trường đã biết (7 unikon-e2e/luna/t134 + 2 CRLF/path.resolve Windows) thì sửa code.
7. Push `agy/yl-code-a2-1b`.
CẤM: deploy, gửi mail, in khoá/mật khẩu, xoá dữ liệu, sửa test cũ, sửa bất kỳ file nào trong apps/lab/test/nghiem-thu-rc6/ (kiểm `sha256sum -c apps/lab/test/nghiem-thu-rc6/KHOA.sha256` trước khi push, lệch là tự trượt), sửa TIEU-CHUAN/CHUAN/KHUNG, tự sinh ảnh/video sản phẩm bằng AI, push nền qdzzr4. Màn chưa có khung duyệt thì không build, ghi CHUA_CO_KHUNG. Trạng thái cao nhất REVIEW.
Trả lời KET-QUA.md (ngắn): dòng đầu `dat: co` hoặc `dat: khong`; SHA đỉnh; bảng test khoá ý a,b trước/sau; số pass/fail lab đủ; đường dẫn ảnh ghép; sha256sum -c OK/KHÔNG.
