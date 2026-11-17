may: may-3
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: D:\linhx\nhat-ky\yl09-chia-se-don; D:\linhx\ifagent-wt\yl09-chia-se-don
nhan: may-3 2026-11-18T02:04:16+0700

Phiếu Yên Lam v0.9 `yl09-chia-se-don`. ĐỌC TRƯỚC: `viec/yen-lam-v09/DE-BAI.md` (luật chung 1–9, bắt buộc) trong thư mục hàng đợi của máy này (`git pull` trước). Khung bố cục: `viec/yen-lam-v09/khung/` ảnh P6-cua-toi (chỉ bố cục, GIỮ CSS kính hiện có).
Chạy mọi lệnh ở tiền cảnh, KHÔNG background task; mỗi 5 phút phải có file mới hoặc commit trong thư mục theo_doi.
1. `git -C D:\linhx\ifagent fetch --all` (chưa có clone thì `git clone https://github.com/fyzdfyzd/ifagent D:\linhx\ifagent`). Nếu `origin/yl-full-17-11` chưa có thì dừng, ghi CHUA_CO_NEN. `git -C D:\linhx\ifagent worktree add D:\linhx\nhat-ky\yl09-chia-se-don; D:\linhx\ifagent-wt\yl09-chia-se-don -b agy/yl09-chia-se-don origin/yl-full-17-11`. Cài phụ thuộc apps/lab theo README.
2. Việc: (a) Link chia sẻ bìa `/b/:ma`: trang xem bìa + nút "Mở đồng hành", có og:image (chính bìa, 1200×630 cắt từ bìa), og:title, og:description. (b) favicon, apple-touch-icon, manifest.webmanifest cho /yen-lam/. (c) Gỡ 15 route v0 (/yen-lam/toi, /moi, /sau, /sanh, /quay, /kenh, /btc, /tong-quan, /san-khau, /nha-tai-tro/crm, /proposal, /ntt, /teaser, /thu-giong, /live) và route `/yen-lam/kiosk` dùng bộ clip `assets/ylk/` (KHÔNG phải Yên Lam): trả 302 về /yen-lam/ (trừ route admin cần giữ thì ghi rõ). Không xoá file asset, chỉ chặn route. (d) Lam nói "đại sứ" ở chỗ nào khác ngoài cover-ai thì liệt kê (không sửa cover-ai, phiếu dh-lam làm). Test mới: 15/15 route trả 302; /b/:ma có thẻ og đủ.
3. Duyệt bằng mắt trên pixel theo DE-BAI luật 7 cho mọi màn đụng tới; ảnh và ảnh ghép commit vào `bang-chung/yl09-chia-se-don/` (PNG ≤ 600 KB).
4. Chạy test lab đủ (`node --test --test-concurrency=2 --test-timeout=120000 test/*.test.js` trong apps/lab) và test khoá nghiem-thu-*; không thêm lỗi mới so với nền. Hết giờ thì commit + push phần dở, ghi CON_LAI.
5. Push `agy/yl09-chia-se-don`.
CẤM: như DE-BAI luật 5. Trạng thái cao nhất REVIEW.
Trả lời KET-QUA.md theo DE-BAI luật 9.

nhip: 02:22 18p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
