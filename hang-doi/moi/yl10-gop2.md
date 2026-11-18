may: may-3
loai: code
tran_phut: 30
khong_tien_phut: 20
theo_doi: D:\linhx\nhat-ky\yl10-gop2; D:\linhx\ifagent-wt\yl10-gop
phu_thuoc: yl10-gop; yl10-kiosk-lam; yl10-cam-an

Phiếu `yl10-gop2`: GỘP để Linh test sớm. ĐỌC `viec/yen-lam-v09/DE-BAI-SUA-NHANH.md`.
1. `git -C D:\linhx\ifagent fetch --all`. Worktree `D:\linhx\ifagent-wt\yl10-gop` nhánh `agy/yl10-gop`: checkout `agy/yl10-gop`, pull origin.
2. Merge lần lượt các nhánh origin đang có: agy/yl10-kiosk-lam, agy/yl10-cam-an (bản mới nhất). Nhánh nào không có trên origin thì ghi THIEU, KHÔNG chờ. Xung đột: giữ ý cả hai.
3. Chạy test mới của các nhánh vừa gộp (tệp test yl10-*.test.js), TỪNG TỆP, không chạy cả bộ. Đỏ do gộp thì sửa. LUẬT CHỐNG CHUYỂN NỀN như DE-BAI-SUA-NHANH.
4. Push `agy/yl10-gop`. KHÔNG deploy (phiếu deploy làm). Phút 20 phải push dù chưa chạy hết test, ghi CON_LAI.
KET-QUA: dat, SHA đỉnh, nhánh đã gộp/THIEU, test.
