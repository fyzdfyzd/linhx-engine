may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 1
theo_doi: C:\linhx\ifagent-wt\ev-de-xuat-11
nhan: may-2 2026-11-17T10:42:45+0700

Phiếu ev-de-xuat-11 (vòng 3, cuối): bộ slide đang 8.5, cần 9. COMMIT + PUSH SAU MỖI Ý.
0. `git -C C:\linhx\ifagent fetch --all`. `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\ev-de-xuat-11 -b agy/ev-de-xuat-11 origin/agy/ev-de-xuat-10`. Trong apps/event: `npm ci`.
1. Khối nội dung chính của slide 4, 6, 7 phải căn giữa theo chiều dọc phần dưới tiêu đề và to lên cho đầy khung: slide 4 thẻ cao ≥ 360 px với số ≥ 120 px và chữ bước ≥ 36 px; slide 6 hộp mốc chữ ≥ 30 px, dòng thời gian ở giữa dọc; slide 7 tên chỉ số ≥ 80 px, cả hàng ở giữa dọc. Không còn khoảng trống dọc liền mạch > 22% chiều cao khung (sửa ngưỡng trong ca test khoảng trống của de-xuat-slide.test.js từ 30% xuống 22% — đây là ca do chính chuỗi phiếu ev-de-xuat thêm, được phép siết).
2. Slide 5: ảnh thẻ giải pháp KHÔNG được trùng ảnh bìa (slide 1) hay ảnh ý tưởng (slide 3). Lấy ảnh riêng của từng giải pháp đang có trong public/web (ảnh trang /giai-phap/<slug>), thêm ca test: src ảnh slide 5 khác src ảnh slide 1 và 3.
3. Slide 4: thêm mũi tên mảnh hoặc đường nối giữa 4 thẻ để đọc thành hành trình (không chữ mới).
4. Chạy từng tệp test tiền cảnh: de-xuat-slide, xuong-ev4, xuong-pdf-mail, khong-tran-ngang; npm test sau cùng. Bằng chứng bang-chung/ev-de-xuat-11/: slide-1..8, pdf-1..8 (1920×1080), TONG-SLIDE.png. Push agy/ev-de-xuat-11.

LUẬT CHUNG cụm event: chạy TIỀN CẢNH, không background task; chỉ sửa apps/event/ và bang-chung/ev-de-xuat-11/; không đụng apps/lab, packages/, bang-chung cụm khác, nhánh Yên Lam/brand; không deploy, không mail thật, không in khoá, không sửa/xoá test cũ ngoài ý 1, không sinh ảnh AI, không gọi AI thật, không viết chữ mới. Bộ quét bí mật runner báo nhầm dòng CŨ: không sửa các tệp đó; chỉ xác nhận `git diff origin/agy/ev-de-xuat-10..HEAD` không có bí mật mới. KET-QUA ngắn: dat co/khong; SHA; test đỏ→xanh; pass/fail; TONG-SLIDE.png.

nhip: 11:21 39p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
