may: may-3
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: D:\linhx\nhat-ky\yl09-dh-bang-tin-cua-toi; D:\linhx\ifagent-wt\yl09-dh-bang-tin-cua-toi
phu_thuoc: yl09-dh-khung
nhan: may-3 2026-11-18T02:45:15+0700

Phiếu Yên Lam v0.9 `yl09-dh-bang-tin-cua-toi`. ĐỌC TRƯỚC: `viec/yen-lam-v09/DE-BAI.md` (luật chung 1–9, bắt buộc) trong thư mục hàng đợi của máy này (`git pull` trước). Khung bố cục: `viec/yen-lam-v09/khung/` ảnh P5-bang-tin, P6-cua-toi (chỉ bố cục, GIỮ CSS kính hiện có).
Lượt 2 (lượt 1 bị huỷ dây chuyền hoặc quá giờ). Chạy mọi lệnh ở tiền cảnh, KHÔNG background task. Tạo `D:\linhx\nhat-ky\yl09-dh-bang-tin-cua-toi\` và ghi 1 dòng tiến độ vào `tien-do.log` ở đó sau mỗi bước (ít nhất 5 phút một lần). COMMIT + PUSH sau mỗi ý nhỏ, phút 35 phải push dù chưa xong.
1. `git -C D:\linhx\ifagent fetch --all` (chưa có clone thì `git clone https://github.com/fyzdfyzd/ifagent D:\linhx\ifagent`). Nếu `origin/agy/yl09-dh-khung` chưa có thì dừng, ghi CHUA_CO_NEN. `git -C D:\linhx\ifagent worktree add D:\linhx\ifagent-wt\yl09-dh-bang-tin-cua-toi -b agy/yl09-dh-bang-tin-cua-toi origin/agy/yl09-dh-khung`. Cài phụ thuộc apps/lab theo README.
2. Việc: (a) Tab Bảng tin: một bảng tin duy nhất (gộp tường ảnh, tường chung, thông báo BTC; thread teabreak/check-in của Diễn đàn chuyển thành thông báo BTC). Thông báo BTC ghim đầu. Lọc Tất cả / Có bạn / Ảnh BTC / Bìa / Khách có đếm. Lưới 3 cột 4:5, tải 30 ảnh một lần (cuộn tới cuối tải tiếp), ảnh nhỏ webp 300px. Nút + Đăng ảnh (đi qua lọc an toàn + BTC duyệt như hiện có), nút báo cáo. Thử với ≥ 300 ảnh giả lập: cuộn không giật, lần tải đầu ≤ 1,5 MB. (b) Tab Của tôi: thứ tự bìa (Lưu ảnh, Chia sẻ) → nút Tạo tạp chí (chỉ là lối vào, luồng làm ở phiếu yl09-tap-chi) → 4 ô Mã QR của tôi · Ảnh có tôi · Gặp gỡ · Đã lưu → hồ sơ (sửa tên, nghề, avatar tải lên) → Email giữ trang · Lam nhớ gì · Quên tôi. Thêm công tắc "Cho kiosk nhận ra mặt tôi" (đồng ý sinh trắc riêng, tắt là xoá đặc trưng mặt). Gặp gỡ chỉ lộ liên hệ khi hai bên đồng ý (giữ logic có sẵn). Không mục nào trùng.
3. Duyệt bằng mắt trên pixel theo DE-BAI luật 7 cho mọi màn đụng tới; ảnh và ảnh ghép commit vào `bang-chung/yl09-dh-bang-tin-cua-toi/` (PNG ≤ 600 KB).
4. Chạy test lab đủ (`node --test --test-concurrency=2 --test-timeout=120000 test/*.test.js` trong apps/lab) và test khoá nghiem-thu-*; không thêm lỗi mới so với nền. Hết giờ thì commit + push phần dở, ghi CON_LAI.
5. Push `agy/yl09-dh-bang-tin-cua-toi`.
CẤM: như DE-BAI luật 5. Trạng thái cao nhất REVIEW.
Trả lời KET-QUA.md theo DE-BAI luật 9.
