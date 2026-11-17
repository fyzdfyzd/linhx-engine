may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\ifagent-wt\bhc-staging
nhan: may-2 2026-11-17T12:53:23+0700

Lưu ý máy: KHÔNG dùng background task, subagent hay thợ con; mọi lệnh chạy tiền cảnh. Gọi `npm.cmd`/`npx.cmd`. Commit + push mỗi 10 phút.
Brand health check: dựng STAGING RIÊNG trên VM chung (Linh duyệt 17/11 12:51). TUYỆT ĐỐI KHÔNG chạm prod, không chạm stg-event, staging Yên Lam (ifagent-staging-*, lab), Caddy, DNS.
0. Điều kiện: giờ VN 07:00–22:00. `git -C C:\linhx\ifagent fetch origin agy/bhc-quan-tri`; đỉnh phải chứa commit thư (log có "thư" hoặc "email"/"Resend" sau 19584c7). Chưa có thì DỪNG, ghi CHUA_CO_NEN.
1. Worktree C:\linhx\ifagent-wt\bhc-staging, nhánh agy/bhc-staging từ origin/agy/bhc-quan-tri. `npm.cmd run verify` và `npm.cmd run test:lap` trong apps/brand-health phải xanh, cây git sạch.
2. Viết infra/staging/stg-brand/ theo đúng mẫu infra/staging/stg-event/ trên origin/claude/project-thread-es2prv (đọc README + compose.yaml ở đó): compose project `stg-brand`, container `stg-brand-app`, image `stg-brand-app:<sha>`, chỉ mở 127.0.0.1:3920 trên VM, KHÔNG nối mạng Caddy, mem_limit 512m, cpus 0.5, dữ liệu /opt/stg-brand/data, env /opt/stg-brand/stg-brand.env (chỉ ghi file .example với TÊN biến: ADMIN_CODE, GEMINI_API_KEY, OPENROUTER_API_KEY, RESEND_API_KEY, BH_*; trần AI thấp). Healthz trả BUILD_SHA. README ghi lệnh đường hầm: gcloud compute ssh ifagent-event --zone=asia-southeast1-b --project=ifagent-event-2026 -- -N -L 3920:127.0.0.1:3920. Script len-vm.sh: build image từ git archive apps/brand-health (+ packages/core nếu cần), docker save | gcloud compute ssh ... docker load, giữ tag :prev, `docker compose -p stg-brand up -d`. Lệnh lùi: đổi STG_SHA về :prev.
3. Trước khi lên VM: kiểm ổ VM `df -h /` qua gcloud ssh, cần ≥ 5 GB trống, thiếu thì DỪNG, ghi CAN-LINH. Nếu máy không có gcloud đã đăng nhập hoặc thiếu quyền: DỪNG, trả `CAN-LINH: đăng nhập gcloud trên máy 2; LENH: gcloud auth login`.
4. Nếu /opt/stg-brand/stg-brand.env chưa có trên VM: KHÔNG tự tạo khoá; trả `CAN-LINH: tạo /opt/stg-brand/stg-brand.env từ stg-brand.env.example (ADMIN_CODE mới, GEMINI_API_KEY khoá staging); LENH: <lệnh scp/ssh cụ thể>` rồi dừng sau khi đã đẩy image.
5. Có env: chạy cổng `python C:\linhx\hang-doi\runner\cong_phat_hanh.py --base http://127.0.0.1:3920 --truoc --prod demo.ifagent.net,event.ifagent.net` (qua đường hầm), deploy, rồi `--sha <sha-moi>`. Trượt thì lùi ngay về :prev.
6. Qua đường hầm chụp 1280 + 360: trang chủ, /bao-cao/2026-11-13-vinamilk-9b816db5/, /quan-tri/ màn đăng nhập. Vào bang-chung/bhc-staging/. Commit infra + bằng chứng, push agy/bhc-staging.
CẤM: deploy prod, sửa Caddy/DNS/compose prod, đụng stg-event/ifagent-staging-*/lab, chạy rollback-app.sh, in khoá/ADMIN_CODE, gọi AI thật quá 1 lượt quét thử. Trạng thái cao nhất REVIEW.
KET-QUA.md: `dat: co|khong`; SHA trên staging; healthz; lệnh đường hầm; lệnh lùi; CAN-LINH nếu có.

nhip: 13:08 15p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
