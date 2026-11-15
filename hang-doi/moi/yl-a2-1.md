may: may-2
loai: code
tran_phut: 40
theo_doi: C:\linhx\ifagent-wt\yl-a2-1
phu_thuoc: yl-a1-gop-b

Phiếu A2 Yên Lam, kiosk "Nhắn Lam" (/yen-lam/csmo/kiosk-lam). Chạy mọi lệnh ở tiền cảnh, mỗi 5 phút phải có file mới hoặc commit trong thư mục theo_doi.
1. `git -C C:\linhx\ifagent fetch --all`. Nếu origin/agy/yl-a1-gop-b chưa có thì dừng ngay, ghi CHUA_CO_NEN. `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\yl-a2-1 -b agy/yl-a2-1 origin/agy/yl-a1-gop-b`.
2. Đọc khung đã duyệt: `git -C C:\linhx\ifagent show origin/claude/nop-phat-hanh:.handoff/yen-lam-dong-hanh/NOP/` (thư mục 2c-K-AM và CHU-TREN-MAN, chép ra C:\linhx\ifagent-wt\yl-a2-1-khung). Màn nào không có khung duyệt thì KHÔNG build, ghi CHUA_CO_KHUNG.
3. Việc (mỗi ý một commit, tiêu đề commit bắt đầu bằng "A2(<ý>)"):
   (a) Câu trả lời của Lam phải hiện bằng chữ trên màn (song song với tiếng nói), đúng vị trí trong khung.
   (b) Khách gửi được câu thứ 2 khi Lam đang nói: câu mới vào hàng, Lam dừng hoặc trả lời nối, không mất câu.
4. Mỗi ý có một test E2E Playwright mới trong file riêng `apps/lab/test/a2-kiosk-<ý>.test.js` (hoặc thư mục E2E sẵn có), đỏ trước khi sửa, xanh sau khi sửa. Không sửa test có sẵn.
5. Chạy server lab cục bộ, chụp ảnh 1080×1920 mỗi ý và quay 1 video một lượt (Playwright recordVideo) vào C:\linhx\ifagent-wt\yl-a2-1-bang-chung\. Không tự sinh ảnh/video sản phẩm bằng AI.
6. Chạy test lab đủ (`node --test --test-concurrency=2 --test-timeout=120000 test/*.test.js`), log thô vào thư mục bằng chứng. Lỗi mới ngoài 7 lỗi môi trường đã biết thì sửa code, không sửa test.
7. Push `agy/yl-a2-1`. Không push nền qdzzr4. Chép ảnh + video vào G:\My Drive\yen-lam\yl-a2-1\ nếu có ổ G:, ghi đường dẫn vào dòng drive.
CẤM: deploy, gửi mail, in khoá/mật khẩu, xoá dữ liệu, sửa test cũ, đụng file ngoài phạm vi kiosk-lam (và route API kiosk nếu cần). Trạng thái cao nhất REVIEW.
Trả lời KET-QUA.md (ngắn): từng ý | SHA commit | test E2E đỏ→xanh | ảnh; pass/fail lab đủ; SHA đỉnh; ĐẠT/KHÔNG từng ý.
