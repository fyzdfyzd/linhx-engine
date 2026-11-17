may: may-2
loai: code
tran_phut: 20
khong_tien_phut: 10
theo_doi: C:\linhx\nhat-ky\yl09-deploy; C:\linhx\ifagent-wt\yl09-gop
phu_thuoc: yl09-gop

Phiếu Yên Lam v0.9 `yl09-deploy`: chỉ DEPLOY STAGING bản gộp. ĐỌC TRƯỚC: `viec/yen-lam-v09/DE-BAI.md` (luật 5: chỉ staging, KHÔNG prod, không in khoá).
Chạy mọi lệnh ở tiền cảnh. Ghi tiến độ vào `C:\linhx\nhat-ky\yl09-deploy\tien-do.log`.
1. Đọc `xong/yl09-gop-sua-5/KET-QUA.md` trong hàng đợi. Nếu `dat: khong` vì có test khoá đỏ MỚI (không phải DO_SAN) thì dừng, ghi KHONG_DEPLOY + lý do.
2. `git -C C:\linhx\ifagent fetch --all`. SHA cần deploy = đỉnh `origin/agy/yl09-gop`.
3. Gọi `/healthz` staging. Commit đã đúng SHA đó thì ghi DA_CO, sang bước 5.
4. Deploy staging `origin/agy/yl09-gop` theo cách deploy staging thường lệ trên máy 2 (như các lần deploy staging trước). KHÔNG đụng prod, compose prod, `infra/` prod. Kiểm `/healthz` đúng SHA.
5. Chụp 2 màn: điện thoại `/yen-lam/` 390×844 (deviceScaleFactor 2) và kiosk 1080×1920 trên staging. Commit vào `bang-chung/yl09-deploy/` của nhánh `agy/yl09-gop`, push.
KET-QUA: dòng đầu `dat: co|khong`, SHA staging, link staging đã kiểm, 2 ảnh.
