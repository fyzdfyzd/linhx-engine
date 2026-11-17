may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\nhat-ky\yl09-dh-lam; C:\linhx\ifagent-wt\yl09-dh-lam
phu_thuoc: yl09-dh-khung
nhan: may-2 2026-11-18T02:39:50+0700

Phiếu Yên Lam v0.9 `yl09-dh-lam`. ĐỌC TRƯỚC: `viec/yen-lam-v09/DE-BAI.md` (luật chung 1–9, bắt buộc) trong thư mục hàng đợi của máy này (`git pull` trước). Khung bố cục: `viec/yen-lam-v09/khung/` ảnh P1-tab-lam, P1b-chat-widget (chỉ bố cục, GIỮ CSS kính hiện có).
Lượt 2 (lượt 1 bị huỷ dây chuyền hoặc quá giờ). Chạy mọi lệnh ở tiền cảnh, KHÔNG background task. Tạo `C:\linhx\nhat-ky\yl09-dh-lam\` và ghi 1 dòng tiến độ vào `tien-do.log` ở đó sau mỗi bước (ít nhất 5 phút một lần). COMMIT + PUSH sau mỗi ý nhỏ, phút 35 phải push dù chưa xong.
1. `git -C C:\linhx\ifagent fetch --all` (chưa có clone thì `git clone https://github.com/fyzdfyzd/ifagent C:\linhx\ifagent`). Nếu `origin/agy/yl09-dh-khung` chưa có thì dừng, ghi CHUA_CO_NEN. `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\yl09-dh-lam -b agy/yl09-dh-lam origin/agy/yl09-dh-khung`. Cài phụ thuộc apps/lab theo README.
2. Việc: Tab Lam = chat giọng + chữ (Linh chốt). (a) Ô nhập chữ + nút mic trong cùng thanh; giữ 10 lượt gần nhất; làm quen trong chat (hỏi tên, rồi 3-4 chip track), bỏ qua vẫn dùng được. Chip gợi ý đổi theo giờ (trước 19/11, trong ngày, tối 20/11, sau sự kiện). (b) Widget trong chat kiểu A2UI tự làm gọn: Lam gọi công cụ, server trả JSON `{loai, du_lieu}`, client vẽ thẻ. Tối thiểu 4 loại: `the_phien(id)` (track, phòng, giờ, diễn giả, nút Lưu và nhắc / Xem phiên), `the_dien_gia(slug)`, `anh_co_ban()` (dải ảnh BTC đã gắn khách), `ma_qr()`. Dữ liệu lấy từ agenda.json/dien-gia.json, AI không tự viết giờ/phòng. (c) Prompt: `server/v1/lam/tra-loi.js` giữ luật PROMPT-CHUAN mục A; sửa `modules/bia/cover-ai.js` ~dòng 496 bỏ "đại sứ" → "Lam, trợ lý AI của VSMCamp & CSMOSummit 2026"; trường tom/ins chỉ lấy từ `mo` của MENU, không có thì để trống. Test mới: 3 câu bẫy ("bạn là đại sứ chính thức à", "tóm giúp bài của Nguyễn Trần Quang", "giới thiệu nhà tài trợ") trả đúng luật; câu "chiều nay có gì về GEO" trả ≥1 widget the_phien có id thật.
3. Duyệt bằng mắt trên pixel theo DE-BAI luật 7 cho mọi màn đụng tới; ảnh và ảnh ghép commit vào `bang-chung/yl09-dh-lam/` (PNG ≤ 600 KB).
4. Chạy test lab đủ (`node --test --test-concurrency=2 --test-timeout=120000 test/*.test.js` trong apps/lab) và test khoá nghiem-thu-*; không thêm lỗi mới so với nền. Hết giờ thì commit + push phần dở, ghi CON_LAI.
5. Push `agy/yl09-dh-lam`.
CẤM: như DE-BAI luật 5. Trạng thái cao nhất REVIEW.
Trả lời KET-QUA.md theo DE-BAI luật 9.

nhip: 02:48 9p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
