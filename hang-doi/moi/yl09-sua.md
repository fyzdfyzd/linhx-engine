may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\ifagent-wt\yl09-sua
phu_thuoc: yl09-e2e

Phiếu Yên Lam v0.9 `yl09-sua`. ĐỌC TRƯỚC: `viec/yen-lam-v09/DE-BAI.md` (luật chung 1–9, bắt buộc) trong thư mục hàng đợi của máy này (`git pull` trước).
Chạy mọi lệnh ở tiền cảnh, KHÔNG background task; mỗi 5 phút phải có file mới hoặc commit trong thư mục theo_doi.
1. `git -C C:\linhx\ifagent fetch --all` (chưa có clone thì `git clone https://github.com/fyzdfyzd/ifagent C:\linhx\ifagent`). Nếu `origin/agy/yl09-e2e` chưa có thì dừng, ghi CHUA_CO_NEN. `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\yl09-sua -b agy/yl09-sua origin/agy/yl09-e2e`. Cài phụ thuộc apps/lab theo README.
2. Việc: Sửa lỗi từ KET-QUA của yl09-e2e (đọc `xong/yl09-e2e/KET-QUA.md` trong hàng đợi và ảnh trong nhánh agy/yl09-e2e). Nhánh `agy/yl09-sua` từ `agy/yl09-gop`. Sửa hết lỗi CHẶN rồi NẶNG trong 40 phút, mỗi lỗi một commit + ảnh ghép trước/sau. Chạy lại test như yl09-gop. Xanh thì DEPLOY STAGING lại. KHÔNG deploy prod. KET-QUA: lỗi đã sửa / còn lại, SHA staging.
3. Duyệt bằng mắt trên pixel theo DE-BAI luật 7 cho mọi màn đụng tới; ảnh và ảnh ghép commit vào `bang-chung/yl09-sua/` (PNG ≤ 600 KB).
4. Chạy test lab đủ (`node --test --test-concurrency=2 --test-timeout=120000 test/*.test.js` trong apps/lab) và test khoá nghiem-thu-*; không thêm lỗi mới so với nền. Hết giờ thì commit + push phần dở, ghi CON_LAI.
5. Push `agy/yl09-sua`.
CẤM: như DE-BAI luật 5. Trạng thái cao nhất REVIEW.
Trả lời KET-QUA.md theo DE-BAI luật 9.
