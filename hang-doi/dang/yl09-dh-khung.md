may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\ifagent-wt\yl09-dh-khung
nhan: may-2 2026-11-17T22:56:23+0700

Phiếu Yên Lam v0.9 `yl09-dh-khung`. ĐỌC TRƯỚC: `viec/yen-lam-v09/DE-BAI.md` (luật chung 1–9, bắt buộc) trong thư mục hàng đợi của máy này (`git pull` trước). Khung bố cục: `viec/yen-lam-v09/khung/` ảnh P1-tab-lam, P6-cua-toi (chỉ bố cục, GIỮ CSS kính hiện có).
Chạy mọi lệnh ở tiền cảnh, KHÔNG background task; mỗi 5 phút phải có file mới hoặc commit trong thư mục theo_doi.
1. `git -C C:\linhx\ifagent fetch --all` (chưa có clone thì `git clone https://github.com/fyzdfyzd/ifagent C:\linhx\ifagent`). Nếu `origin/yl-full-17-11` chưa có thì dừng, ghi CHUA_CO_NEN. `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\yl09-dh-khung -b agy/yl09-dh-khung origin/yl-full-17-11`. Cài phụ thuộc apps/lab theo README.
2. Việc: Khung đồng hành mới. (a) `/yen-lam/` phục vụ đồng hành (không còn trang chủ riêng); 5 lối vào (link Zalo/email, QR standee, QR bìa kiosk `?bia=`, link `/b/:ma`, quay lại) đều đáp vào cùng app: chưa có hồ sơ → tab Lam chào lần đầu; có → chào tên; `?bia=` → mở tab Của tôi, bìa ở đầu. (b) Bỏ màn đồng ý đầu trang, sửa lỗi 401 `/khach/toi/dong-y` khi mở lần đầu (context trình duyệt mới phải 0 lỗi 4xx). Xin quyền đúng lúc: nhắc khi bấm Lưu, email khi nhận tạp chí, sinh trắc khi bật nhận mặt. (c) Thanh 4 tab cố định Lam · Lịch · Bảng tin · Của tôi; mỗi tab một route (`#lam`, `#lich`, `#bang-tin`, `#cua-toi`), sửa lỗi bấm "Của tôi" vẫn hiện Diễn đàn; bỏ các điểm đến khác khỏi thanh điều hướng (Ngày sinh, Diễn đàn...) nhưng không xoá code. Trang con có nút quay lại, không mở tab mới. (d) Video/ảnh Lam lớn chỉ ở tab Lam; tab khác là avatar Lam 34px ở đầu trang. Test mới: Playwright bấm lần lượt 4 tab, mỗi tab đúng nội dung; context mới 0 lỗi 4xx.
3. Duyệt bằng mắt trên pixel theo DE-BAI luật 7 cho mọi màn đụng tới; ảnh và ảnh ghép commit vào `bang-chung/yl09-dh-khung/` (PNG ≤ 600 KB).
4. Chạy test lab đủ (`node --test --test-concurrency=2 --test-timeout=120000 test/*.test.js` trong apps/lab) và test khoá nghiem-thu-*; không thêm lỗi mới so với nền. Hết giờ thì commit + push phần dở, ghi CON_LAI.
5. Push `agy/yl09-dh-khung`.
CẤM: như DE-BAI luật 5. Trạng thái cao nhất REVIEW.
Trả lời KET-QUA.md theo DE-BAI luật 9.

nhip: 23:08 12p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
