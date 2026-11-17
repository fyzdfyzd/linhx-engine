may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\ifagent-wt\yl09-widget
phu_thuoc: yl09-kiosk

Phiếu Yên Lam v0.9 `yl09-widget`. ĐỌC TRƯỚC: `viec/yen-lam-v09/DE-BAI.md` (luật chung 1–9, bắt buộc) trong thư mục hàng đợi của máy này (`git pull` trước). Khung bố cục: `viec/yen-lam-v09/khung/` ảnh K1-tro-chuyen, A1-admin-mot-man (chỉ bố cục, GIỮ CSS kính hiện có).
Chạy mọi lệnh ở tiền cảnh, KHÔNG background task; mỗi 5 phút phải có file mới hoặc commit trong thư mục theo_doi.
1. `git -C C:\linhx\ifagent fetch --all` (chưa có clone thì `git clone https://github.com/fyzdfyzd/ifagent C:\linhx\ifagent`). Nếu `origin/agy/yl09-kiosk` chưa có thì dừng, ghi CHUA_CO_NEN. `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\yl09-widget -b agy/yl09-widget origin/agy/yl09-kiosk`. Cài phụ thuộc apps/lab theo README.
2. Việc: Widget kiosk. 8 loại: Sắp diễn ra (các phiên song song khung kế tiếp, từ agenda thật), Diễn giả nổi bật (đổi 20 s, ảnh thật hoặc chữ cái đầu), Wifi, Sơ đồ tầng, Bìa vừa chụp, Bảng tin, QR đồng hành, Thông báo BTC. Tối đa 3 widget trên màn. Cấu hình theo từng máy kiosk (mã máy có sẵn), lưu server; API đọc/ghi cho admin (quyền BTC). Kiosk hỏi cấu hình mỗi 10 s hoặc nhận đẩy: tắt trong admin thì kiosk ẩn trong ≤ 10 s. Widget sáng lên khi Lam nhắc tới phiên đó. Test mới: đổi cấu hình qua API → kiosk giả lập đổi trong ≤ 10 s; bật 4 widget thì chỉ hiện 3 (ưu tiên theo thứ tự).
3. Duyệt bằng mắt trên pixel theo DE-BAI luật 7 cho mọi màn đụng tới; ảnh và ảnh ghép commit vào `bang-chung/yl09-widget/` (PNG ≤ 600 KB).
4. Chạy test lab đủ (`node --test --test-concurrency=2 --test-timeout=120000 test/*.test.js` trong apps/lab) và test khoá nghiem-thu-*; không thêm lỗi mới so với nền. Hết giờ thì commit + push phần dở, ghi CON_LAI.
5. Push `agy/yl09-widget`.
CẤM: như DE-BAI luật 5. Trạng thái cao nhất REVIEW.
Trả lời KET-QUA.md theo DE-BAI luật 9.
