may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\nhat-ky\yl09-gop; C:\linhx\ifagent-wt\yl09-gop
phu_thuoc: yl09-admin
nhan: may-2 2026-11-18T05:19:40+0700

Phiếu Yên Lam v0.9 `yl09-gop`. ĐỌC TRƯỚC: `viec/yen-lam-v09/DE-BAI.md` (luật chung 1–9, bắt buộc) trong thư mục hàng đợi của máy này (`git pull` trước).
Lượt 3. Lượt trước quá 40 phút vì chờ bộ test đầy đủ: KHÔNG chạy cả bộ test lab, chỉ chạy test mới của phiếu + `apps/lab/test/nghiem-thu-*` liên quan, mỗi lệnh test có timeout ≤ 8 phút. Chạy mọi lệnh ở tiền cảnh, KHÔNG background task. Tạo `C:\linhx\nhat-ky\yl09-gop\` và ghi 1 dòng tiến độ vào `tien-do.log` ở đó sau mỗi bước (ít nhất 5 phút một lần). COMMIT + PUSH sau mỗi ý nhỏ, phút 35 phải push dù chưa xong.
1. `git -C C:\linhx\ifagent fetch --all`; `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\yl09-gop -b agy/yl09-gop origin/yl-full-17-11`.
2. Việc: Gộp v0.9 (lượt 3). Nhánh tap-chi và clip-t147 có thể còn đang được phiếu khác đẩy tiếp: gộp bản mới nhất trên origin lúc chạy, thiếu thì ghi THIEU, KHÔNG chờ. Tạo `agy/yl09-gop` từ nền `yl-full-17-11` (6291514e), merge lần lượt: dh-khung, dh-lam, dh-lich, dh-bang-tin-cua-toi, tap-chi, kiosk, clip-t147, widget, admin, chia-se-don (nhánh agy/yl09-*; nhánh nào thiếu thì ghi THIEU và bỏ qua). Xung đột: giữ cả hai ý, ưu tiên luật DE-BAI; không bỏ code của phiếu nào. Chạy mọi test khoá nghiem-thu-* (phải xanh như nền) + test mới yl09-* (KHÔNG cả bộ lab; mỗi lệnh ≤ 8 phút). Đỏ thì sửa tới xanh (không sửa test khoá). Xanh thì DEPLOY STAGING (được phép, cách deploy staging như thường lệ trên máy 2), kiểm /healthz đúng SHA. KHÔNG deploy prod. KET-QUA: SHA gộp, bảng test, staging SHA.
3. Duyệt bằng mắt trên pixel theo DE-BAI luật 7 cho mọi màn đụng tới; ảnh và ảnh ghép commit vào `bang-chung/yl09-gop/` (PNG ≤ 600 KB).
4. Chạy test mới của phiếu + test khoá liên quan (KHÔNG cả bộ, mỗi lệnh ≤ 8 phút, tiền cảnh). Hết giờ thì commit + push phần dở, ghi CON_LAI.
5. Push `agy/yl09-gop`.
CẤM: như DE-BAI luật 5. Trạng thái cao nhất REVIEW.
Trả lời KET-QUA.md theo DE-BAI luật 9.

nhip: 05:28 9p đang chờ nền · log cuối 0 phút trước [log_cuoi=2026-11-18T05:27:57+0700] · root agent idle; waiting up to 40m0s for 1 ba
