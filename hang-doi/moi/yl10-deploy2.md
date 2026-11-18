may: may-2
loai: code
tran_phut: 20
khong_tien_phut: 10
theo_doi: C:\linhx\nhat-ky\yl10-deploy2; C:\linhx\ifagent-wt\yl09-gop
phu_thuoc: yl10-gop2

Phiếu `yl10-deploy2`: chỉ DEPLOY STAGING đỉnh `origin/agy/yl10-gop`, làm đúng như `xong/yl09-deploy` (đọc KET-QUA của nó). Không dừng ngang deploy. KHÔNG prod. Kiểm /healthz đúng SHA. Chụp điện thoại `/yen-lam/` 390×844 và kiosk `/yen-lam/csmo/kiosk-lam` 1080×1920 vào `bang-chung/yl10-deploy2/` nhánh agy/yl10-gop, push.
Trang kỹ thuật (yl10-trang-test): đọc KET-QUA của nó lấy TÊN biến/tệp cấu hình chứa mã. Trên VM STAGING (không prod) đặt giá trị ngẫu nhiên 32 ký tự nếu chưa có, KHÔNG in ra log/KET-QUA/màn hình; ghi đường dẫn đầy đủ trang vào `C:\linhx\_ENV\yl-ky-thuat-link.txt` trên máy 2.
KET-QUA: dat, SHA staging, healthz, ảnh.
