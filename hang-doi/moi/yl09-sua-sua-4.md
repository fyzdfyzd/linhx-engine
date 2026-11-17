may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\nhat-ky\yl09-sua; C:\linhx\ifagent-wt\yl09-sua
phu_thuoc: yl09-e2e

Phiếu Yên Lam v0.9 `yl09-sua`. ĐỌC TRƯỚC: `viec/yen-lam-v09/DE-BAI.md` (luật chung 1–9, bắt buộc) trong thư mục hàng đợi của máy này (`git pull` trước).
Lượt 4. Lượt trước quá 40 phút vì chờ bộ test đầy đủ: KHÔNG chạy cả bộ test lab, chỉ chạy test mới của phiếu + `apps/lab/test/nghiem-thu-*` liên quan, mỗi lệnh test có timeout ≤ 8 phút. Chạy mọi lệnh ở tiền cảnh, KHÔNG background task. Tạo `C:\linhx\nhat-ky\yl09-sua\` và ghi 1 dòng tiến độ vào `tien-do.log` ở đó sau mỗi bước (ít nhất 5 phút một lần). COMMIT + PUSH sau mỗi ý nhỏ, phút 35 phải push dù chưa xong.
1. `git -C C:\linhx\ifagent fetch --all` (chưa có clone thì `git clone https://github.com/fyzdfyzd/ifagent C:\linhx\ifagent`). Nếu `origin/agy/yl09-e2e` chưa có thì dừng, ghi CHUA_CO_NEN. `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\yl09-sua -b agy/yl09-sua origin/agy/yl09-e2e`. Cài phụ thuộc apps/lab theo README.
2. Việc: Sửa lỗi từ KET-QUA của yl09-e2e (đọc `xong/yl09-e2e/KET-QUA.md` trong hàng đợi và ảnh trong nhánh agy/yl09-e2e). Nhánh `agy/yl09-sua` từ `agy/yl09-gop`. Sửa hết lỗi CHẶN rồi NẶNG trong 40 phút, mỗi lỗi một commit + ảnh ghép trước/sau. Chạy lại test như yl09-gop. Xanh thì DEPLOY STAGING lại. KHÔNG deploy prod. KET-QUA: lỗi đã sửa / còn lại, SHA staging.
3. Duyệt bằng mắt trên pixel theo DE-BAI luật 7 cho mọi màn đụng tới; ảnh và ảnh ghép commit vào `bang-chung/yl09-sua/` (PNG ≤ 600 KB).
4. Chạy test mới của phiếu + test khoá liên quan (KHÔNG cả bộ, mỗi lệnh ≤ 8 phút, tiền cảnh). Hết giờ thì commit + push phần dở, ghi CON_LAI.
5. Push `agy/yl09-sua`.
LUẬT CHỐNG CHUYỂN NỀN: mỗi lệnh test hay Playwright chỉ chạy 1 tệp, ghi log ra tệp. Nếu công cụ báo lệnh đã chuyển nền thì KHÔNG kết thúc lượt và KHÔNG ngồi chờ: gọi trạng thái lệnh đó liên tục tới khi xong (lượt trước của yl09-gop bị dừng vì ngồi chờ).
CẤM: như DE-BAI luật 5. Trạng thái cao nhất REVIEW.
Trả lời KET-QUA.md theo DE-BAI luật 9.
