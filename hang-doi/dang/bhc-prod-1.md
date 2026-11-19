May: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 30
khong_tien_phut: 10
theo_doi: C:\linhx\ifagent-wt\bhc-prod
nhan: may-2 2026-11-19T08:16:53+0700

Lưu ý máy: KHÔNG background task/subagent; KHÔNG chờ/ngủ dài; MỖI LỆNH PHẢI XONG TRONG 3 PHÚT. Push KET-QUA sau mỗi bước.
LINH DUYỆT (08:14 VN 19/11, nguyên văn "deploy lên production"): deploy Brand Health Check lên PRODUCTION demo.ifagent.net/brand-health-check/ (service brand-health, /opt/ifagent, cổng 3020). Đây là lệnh của Linh, đúng 1 app này.
Bản deploy: ifagent commit ead66ac5 (nhánh agy/bhc-sua-6; staging 999ed2e chạy đúng code này, 121/121 test, đã quét thật CSMO).
0. gcloud compute ssh ifagent-event --zone=asia-southeast1-b --project=ifagent-event-2026. Ghi trước: `df -h /` (cần ≥ 3 GB trống; thiếu thì `sudo docker builder prune -af` rồi `sudo docker image prune -f`), image + trạng thái container ifagent-brand-health-1, curl healthz prod, HTTP code https://demo.ifagent.net/brand-health-check/ và https://event.ifagent.net/.
1. Sao lưu dữ liệu: `sudo tar -czf /opt/ifagent/backup-brand-health-data-19-11.tgz -C /opt/ifagent/infra/data brand-health` (trước khi đổi gì).
2. Tên biến env (CHỈ TÊN, không in giá trị): `sudo grep -o '^[A-Z_]*=' /opt/ifagent/infra/brand-health.env` và ifagent.env. So với /opt/stg-brand/stg-brand.env (chỉ tên). Ghi vào KET-QUA những tên staging có mà prod thiếu. KHÔNG sửa env prod trong phiếu này, trừ: nếu prod thiếu BH_TRAN_CHI_PHI_NGAY thì thêm BH_TRAN_CHI_PHI_NGAY=50000; nếu thiếu BH_QUICK thì thêm BH_QUICK=1 (trần chi phí cho QR công khai).
3. Deploy bằng đúng công cụ có sẵn: trên máy, `git archive ead66ac5:apps/brand-health | gzip > brand-health-app.tgz` (và core.tgz từ packages/core nếu deploy-app.sh cần, đọc script trước), scp lên VM /tmp/brand-health-app.tgz, chạy `sudo sh /opt/ifagent/infra/deploy-app.sh brand-health`. Script tự tag :prev, kiểm healthz 60 s và tự rollback nếu lỗi. Nếu deploy-app.sh trên VM khác bản trong repo thì dùng bản trên VM, ghi khác biệt.
4. Kiểm sau: healthz prod 200 kèm BUILD_SHA/version; https://demo.ifagent.net/brand-health-check/ 200; https://event.ifagent.net/ 200; lab.ifagent.net và bd.ifagent.net giữ nguyên code HTTP như bước 0. Chụp trang chủ prod 1280 và 360 (sáng) vào bang-chung/bhc-prod-1/ trên nhánh agy/bhc-prod-1. Mở 1 báo cáo cũ đã có trên prod (nếu có) xem còn 200.
5. Nếu bất kỳ bước 4 nào hỏng: chạy `sudo sh /opt/ifagent/infra/blue-green/rollback-fast.sh brand-health` hoặc rollback theo hướng dẫn trong deploy-app.sh về :prev, kiểm lại 200, ghi rõ.
CẤM: đụng service khác (event, caddy, concept-note, idea-lab, lab), sửa Caddyfile/DNS, đụng stg-event/stg-brand, in khoá/mã, quét thật trên prod. KET-QUA: dat, SHA đang chạy, df trước/sau, tên env thiếu, HTTP các trang trước/sau, ảnh.

nhip: 08:19 3p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
