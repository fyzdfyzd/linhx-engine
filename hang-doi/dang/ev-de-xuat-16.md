may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 1
phu_thuoc: ev-anh-ly-12f
theo_doi: C:\linhx\ifagent-wt\ev-de-xuat-16
nhan: may-2 2026-11-17T21:23:16+0700

Phiếu ev-de-xuat-16 (vòng 5): gắn ảnh ly cà phê vào slide đề xuất mẫu + cân slide 7. COMMIT + PUSH SAU MỖI Ý.
0. `git -C C:\linhx\ifagent fetch --all`. `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\ev-de-xuat-16 -b agy/ev-de-xuat-16 origin/agy/ev-de-xuat-13b`. Trong apps/event: `npm ci`. Lấy ảnh từ nhánh hang-doi linhx-engine: `xong/ev-anh-ly-12f/ly-ngang.*`, `ly-vuong.*`.
1. Chép thành `apps/event/public/web/anh/ds/ly-ca-phe-ngang.webp` và `ly-ca-phe-vuong.webp` (sharp, chất lượng 82, KHÔNG cắt, giữ tỉ lệ; ≤ 400 KB). Slide 3 (ý tưởng): thay ảnh rạp chiếu bằng ảnh ly cà phê; nếu chỉ có ảnh ngang thì dùng ảnh ngang cho slide 3, khung ảnh slide 3 đổi theo đúng tỉ lệ ảnh (không méo, không cắt mất ly). Slide 1 (bìa) GIỮ ảnh hiện tại. Thêm ca test: src ảnh slide 3 chứa `ly-ca-phe`, naturalWidth > 0, tỉ lệ khung chứa lệch tỉ lệ ảnh ≤ 5%.
2. Slide 7: 3 cột chỉ số rộng bằng nhau, tên chỉ số mỗi cột 1 dòng ("Lượt trò chuyện" không gãy dòng — giảm cỡ chữ đồng đều cả 3 cột nếu cần, vẫn ≥ 64 px), dòng phụ cùng một hàng chân. Thêm ca test: 3 cột chênh rộng ≤ 2%, mỗi tên chỉ số đúng 1 dòng.
3. Chạy tiền cảnh: de-xuat-slide, xuong-ev4, xuong-pdf-mail, khong-tran-ngang, giao-dien-sang; npm test sau cùng. Bằng chứng bang-chung/ev-de-xuat-16/: slide-1..8, pdf-1..8 (1920×1080), TONG-SLIDE.png. Push agy/ev-de-xuat-16.

LUẬT CHUNG cụm event: chạy TIỀN CẢNH, không background task; chỉ sửa apps/event/ và bang-chung/ev-de-xuat-16/; không đụng apps/lab, packages/, bang-chung cụm khác, nhánh Yên Lam/brand; không deploy, không mail thật, không in khoá, không sửa/xoá test cũ (chỉ thêm ca mới), không sinh ảnh AI, không gọi AI thật, không viết chữ mới. Bộ quét bí mật runner báo nhầm dòng CŨ: không sửa các tệp đó; chỉ xác nhận `git diff origin/agy/ev-de-xuat-13b..HEAD` không có bí mật mới. KET-QUA ngắn: dat co/khong; SHA; test đỏ→xanh; pass/fail; TONG-SLIDE.png.

nhip: 21:27 5p đang chờ nền · log cuối 2 phút trước [log_cuoi=2026-11-17T21:25:00+0700] · root agent idle; waiting up to 40m0s for 1 ba
