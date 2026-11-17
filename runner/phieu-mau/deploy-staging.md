may: may-2
loai: code
tran_phut: 25
theo_doi: C:\linhx\wt-<du-an>
phu_thuoc: <id-phieu-kiem-thu>

Phiếu khuôn phát hành STAGING cho `<app>` (TUYỆT ĐỐI KHÔNG chạm production; mọi lệnh chạy tiền cảnh, tuần tự):
1. Kiểm điều kiện trước khi đẩy: cây git sạch, cổng `verify` + `e2e` local của `<app>` xanh, không nằm trong lịch khoá / giờ sự kiện.
2. Chạy cổng phát hành TRƯỚC deploy (chặn tên miền `--prod`, chặn ngoài 07:00–22:00 giờ VN, chỉ GET, lấy `BUILD_SHA` cũ làm mốc lùi):
   `python C:\linhx\hang-doi\runner\cong_phat_hanh.py --base <url-staging> --truoc --prod <ds-ten-mien-prod>`
3. Đẩy riêng `<app>` lên staging (giữ nguyên `data/` và lưu tag/thư mục `:prev`).
4. Chạy cổng phát hành SAU deploy để xác nhận `GET /healthz` trả đúng `<sha-moi>`:
   `python C:\linhx\hang-doi\runner\cong_phat_hanh.py --base <url-staging> --sha <sha-moi> --prod <ds-ten-mien-prod>`
   Nếu trượt: chạy ngay lệnh rollback staging về `:prev` và báo lỗi.
5. Trả lời ngắn gọn: SHA cũ → SHA mới trên staging, lệnh rollback đã kiểm, và dừng chờ Linh mở prod theo khối:
   `CAN-LINH: Duyệt và chạy deploy prod <app> (<sha-moi>); LENH: <lenh-deploy-prod> # Rollback: <lenh-rollback-prod>`
