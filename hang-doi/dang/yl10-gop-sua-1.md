may: may-3
loai: code
tran_phut: 30
khong_tien_phut: 20
theo_doi: D:\linhx\nhat-ky\yl10-gop-sua-1; D:\linhx\ifagent-wt\yl10-gop
nhan: may-3 2026-11-18T08:12:53+0700

Phiếu `yl10-gop-sua-1`: GỘP để Linh test sớm. ĐỌC `viec/yen-lam-v09/DE-BAI-SUA-NHANH.md`.
1. `git -C D:\linhx\ifagent fetch --all`. Worktree `D:\linhx\ifagent-wt\yl10-gop` nhánh `agy/yl10-gop`: chưa có thì tạo `-b agy/yl10-gop origin/agy/yl09-gop`.
2. Merge lần lượt các nhánh origin đang có: agy/yl10-dong-hanh, agy/yl10-kiosk-chup, agy/yl10-trang-test, agy/yl10-kiosk-lam, agy/yl10-cam-an. Nhánh nào không có trên origin thì ghi THIEU, KHÔNG chờ. Xung đột: giữ ý cả hai.
3. Chạy test mới của các nhánh vừa gộp (tệp test yl10-*.test.js), TỪNG TỆP, không chạy cả bộ. Đỏ do gộp thì sửa. LUẬT CHỐNG CHUYỂN NỀN như DE-BAI-SUA-NHANH.
4. Push `agy/yl10-gop`. KHÔNG deploy (phiếu deploy làm). Phút 20 phải push dù chưa chạy hết test, ghi CON_LAI.
KET-QUA: dat, SHA đỉnh, nhánh đã gộp/THIEU, test.
