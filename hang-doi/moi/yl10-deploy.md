may: may-2
loai: code
tran_phut: 20
khong_tien_phut: 10
theo_doi: C:\linhx\nhat-ky\yl10-deploy; C:\linhx\ifagent-wt\yl09-gop
phu_thuoc: yl10-gop

Phiếu `yl10-deploy`: chỉ DEPLOY STAGING `origin/agy/yl10-gop`. Như phiếu `yl09-deploy` (xem xong/yl09-deploy/KET-QUA.md để làm lại đúng cách): fetch, deploy staging theo cách thường lệ trên máy 2, KHÔNG prod, không dừng ngang deploy, kiểm /healthz đúng SHA. Sau deploy chụp: điện thoại /yen-lam/ 390×844, kiosk /yen-lam/csmo/kiosk-lam 1080×1920, trang kỹ thuật (nếu có, dùng mã từ cấu hình staging, KHÔNG in mã). Commit ảnh vào bang-chung/yl10-deploy/ nhánh agy/yl10-gop, push.
Trang kỹ thuật cần mã trên staging: nếu phiếu yl10-trang-test ghi tên biến/tệp cấu hình, tạo giá trị ngẫu nhiên 32 ký tự trên VM staging (KHÔNG prod), KHÔNG in ra log/KET-QUA; ghi đường dẫn đầy đủ trang vào tệp C:\linhx\_ENV\yl-ky-thuat-link.txt trên máy 2 để Linh mở.
KET-QUA: dat, SHA staging, healthz, ảnh.
