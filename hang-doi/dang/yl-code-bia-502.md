may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 1
theo_doi: C:\linhx\ifagent-wt\yl-code-bia-502
phu_thuoc: yl-khoa-bia-502
nhan: may-2 2026-11-15T14:05:06+0700

Phiếu sửa lỗi 502 khi tạo bìa (kiosk Agentic Me, Yên Lam). Chạy mọi lệnh ở tiền cảnh, KHÔNG dùng background task, KHÔNG dựng server riêng (test tự createApp trong tiến trình), mỗi lệnh test timeout ≤ 300 s, mỗi 5 phút phải có file mới hoặc commit trong thư mục theo_doi.
1. `git -C C:\linhx\ifagent fetch --all`. `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\yl-code-bia-502 -b agy/yl-code-bia-502 origin/agy/yl-test-bia-502`.
2. Đọc apps/lab/demos/yen-lam/modules/agentic-me/routes.js (chayLuot L118-155, POST /tao L181-218) và màn chờ AM-03b phía client.
3. Việc (mỗi ý một commit, tiêu đề "BIA502: ..."):
   (a) POST /yen-lam/csmo/api/agentic-me/tao LUÔN trả lời ≤ 10 s (mặc định chạy nền như nhánh nen:true, trả 202 + sid), không còn đường await chayLuot đồng bộ. Client hỏi trạng thái qua GET tap-chi/:sid.
   (b) Màn khách giữ đếm lùi AM-03b suốt thời gian tạo (tới 90 s), không hiện chữ lỗi; xong thì sang K6 đúng bìa.
   (d) Tải lại trang giữa chừng: đọc sid đang tạo (sessionStorage/URL hoặc hỏi server) và quay về AM-03b của đúng việc đó, không tạo sid mới, không gọi GH.ketThuc().
   Lỗi thật (AI hỏng) vẫn phải hiện màn lỗi sau khi việc nền báo hỏng, không im lặng.
4. Test khoá apps/lab/test/nghiem-thu-rc6/04-bia-khong-502.test.js phải XANH đủ (a)(b)(c)(d). Chạy cả 01 và 02 xem không đỏ thêm so với trước. Chỉ sửa code sản phẩm.
5. Chạy test lab đủ (`npm i --no-save ws` trong packages/character; `cd apps/lab && node --test --test-concurrency=2 --test-timeout=120000 test/*.test.js`), log thô vào bang-chung\yl-code-bia-502\. Lỗi mới ngoài 9 lỗi môi trường đã biết thì sửa.
6. Push `agy/yl-code-bia-502`.
CẤM: deploy, gửi mail, in khoá/mật khẩu, xoá dữ liệu, sửa test cũ, sửa bất kỳ file nào trong apps/lab/test/nghiem-thu-rc6/ (chạy `sha256sum -c apps/lab/test/nghiem-thu-rc6/KHOA.sha256` trước khi push, lệch là tự trượt), sửa TIEU-CHUAN/CHUAN/KHUNG, gọi AI thật, push nền qdzzr4. Trạng thái cao nhất REVIEW.
Trả lời KET-QUA.md (ngắn): dòng đầu `dat: co` hoặc `dat: khong`; SHA đỉnh; bảng 04 (a)(b)(c)(d) trước/sau; 01/02 trước/sau; số pass/fail lab đủ; sha256sum -c OK/KHÔNG.

nhip: 14:11 6p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
