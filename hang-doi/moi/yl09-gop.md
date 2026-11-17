may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\ifagent-wt\yl09-gop
phu_thuoc: yl09-dh-lam; yl09-dh-lich; yl09-tap-chi; yl09-admin; yl09-chia-se-don

Phiếu Yên Lam v0.9 `yl09-gop`. ĐỌC TRƯỚC: `viec/yen-lam-v09/DE-BAI.md` (luật chung 1–9, bắt buộc) trong thư mục hàng đợi của máy này (`git pull` trước).
Chạy mọi lệnh ở tiền cảnh, KHÔNG background task; mỗi 5 phút phải có file mới hoặc commit trong thư mục theo_doi.
1. `git -C C:\linhx\ifagent fetch --all`; `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\yl09-gop -b agy/yl09-gop origin/yl-full-17-11`.
2. Việc: Gộp v0.9. Tạo `agy/yl09-gop` từ nền `yl-full-17-11` (6291514e), merge lần lượt: dh-khung, dh-lam, dh-lich, dh-bang-tin-cua-toi, tap-chi, kiosk, widget, admin, chia-se-don (nhánh agy/yl09-*; nhánh nào thiếu thì ghi THIEU và bỏ qua). Xung đột: giữ cả hai ý, ưu tiên luật DE-BAI; không bỏ code của phiếu nào. Chạy test lab đủ + mọi test khoá nghiem-thu-* (phải xanh như nền) + test mới của các phiếu. Đỏ thì sửa tới xanh (không sửa test khoá). Xanh thì DEPLOY STAGING (được phép, cách deploy staging như thường lệ trên máy 2), kiểm /healthz đúng SHA. KHÔNG deploy prod. KET-QUA: SHA gộp, bảng test, staging SHA.
3. Duyệt bằng mắt trên pixel theo DE-BAI luật 7 cho mọi màn đụng tới; ảnh và ảnh ghép commit vào `bang-chung/yl09-gop/` (PNG ≤ 600 KB).
4. Chạy test lab đủ (`node --test --test-concurrency=2 --test-timeout=120000 test/*.test.js` trong apps/lab) và test khoá nghiem-thu-*; không thêm lỗi mới so với nền. Hết giờ thì commit + push phần dở, ghi CON_LAI.
5. Push `agy/yl09-gop`.
CẤM: như DE-BAI luật 5. Trạng thái cao nhất REVIEW.
Trả lời KET-QUA.md theo DE-BAI luật 9.
