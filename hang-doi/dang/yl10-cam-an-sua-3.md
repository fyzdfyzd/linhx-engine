may: may-3
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: D:\linhx\nhat-ky\yl10-cam-an; D:\linhx\ifagent-wt\yl10-cam-an
nhan: may-3 2026-11-18T11:37:15+0700

Phiếu `yl10-cam-an` LƯỢT 4 (lượt 3 lỗi hạn mức, chưa làm gì), CHẠY TIẾP. Đề gốc: `git show ba1a2e50:hang-doi/moi/yl10-cam-an.md` trong thư mục hàng đợi, và `viec/yen-lam-v09/DE-BAI-SUA-NHANH.md`.
Lượt trước đã push phần dở lên origin/agy/yl10-cam-an. Việc đầu tiên: `git -C D:\linhx\ifagent fetch --all`, `git -C D:\linhx\ifagent worktree add D:\linhx\ifagent-wt\yl10-cam-an agy/yl10-cam-an` (theo dõi origin), nối node_modules như các phiếu yl10 khác trên máy 3. Đọc git log nhánh để biết đã làm gì.
Sau đó làm tiếp phần còn lại. Ưu tiên theo thứ tự trong đề gốc, mỗi mục xong là COMMIT + PUSH ngay (không để dồn). Phút 30 dừng việc mới, chụp ảnh ghép các màn đã sửa, push, ghi CON_LAI.
LUẬT CHỐNG CHUYỂN NỀN như DE-BAI-SUA-NHANH. Chỉ chạy test của phiếu, từng tệp. CẤM như DE-BAI-SUA-NHANH. KET-QUA theo DE-BAI-SUA-NHANH.
Trước khi làm: `git merge origin/agy/yl10-gop` (đỉnh 23bac445, đã có kiosk Lam mới: Lam to hơn, dock 3 nút, nói cả đoạn) vào nhánh, giải xung đột giữ cả hai, push. Biểu tượng "Lam đang nhìn" đặt sao cho không đè nút làm mới góc phải trên.
Cuối: sau khi push agy/yl10-cam-an, merge nó vào agy/yl10-gop (worktree riêng D:\linhx\ifagent-wt\yl10-gop, pull trước), chạy test yl10-cam-an + yl10-kiosk-lam từng tệp, push agy/yl10-gop. KHÔNG deploy. KET-QUA ghi SHA agy/yl10-gop mới.
