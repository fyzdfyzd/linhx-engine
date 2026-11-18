may: may-3
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: D:\linhx\nhat-ky\yl10-gop; D:\linhx\ifagent-wt\yl10-gop
phu_thuoc: yl10-tri-thuc; yl10-kiosk-lam; yl10-kiosk-chup; yl10-cam-an; yl10-trang-test; yl10-dong-hanh

Phiếu Yên Lam sửa nhanh `yl10-gop`. ĐỌC TRƯỚC: `viec/yen-lam-v09/DE-BAI-SUA-NHANH.md` và `viec/yen-lam-v09/DE-BAI.md` (git pull hàng đợi trước).
Chạy mọi lệnh ở tiền cảnh. Tạo `D:\linhx\nhat-ky\yl10-gop\`, ghi 1 dòng vào `tien-do.log` sau mỗi bước.
0. `git -C D:\linhx\ifagent fetch --all` (chưa có clone thì clone https://github.com/fyzdfyzd/ifagent vào D:\linhx\ifagent). `git -C D:\linhx\ifagent worktree add D:\linhx\ifagent-wt\yl10-gop -b agy/yl10-gop origin/agy/yl09-gop`. Cài phụ thuộc apps/lab (dùng lại node_modules sẵn có nếu được).
Gộp sửa nhanh. Tạo `agy/yl10-gop` từ `origin/agy/yl09-gop`, merge lần lượt các nhánh `origin/agy/yl10-*` (tri-thuc, kiosk-lam, kiosk-chup, cam-an, trang-test, dong-hanh); nhánh nào thiếu thì ghi THIEU, không chờ. Xung đột: giữ ý cả hai, không bỏ code phiếu nào. Chạy test mới yl10-* + yl09-* từng tệp. Đỏ thì sửa (không sửa test khoá). Push. KHÔNG deploy (phiếu yl10-deploy làm).
Cuối: commit + push `agy/yl10-gop`. CẤM như DE-BAI-SUA-NHANH. Trạng thái cao nhất REVIEW. KET-QUA theo DE-BAI-SUA-NHANH.
