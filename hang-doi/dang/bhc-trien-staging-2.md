may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\ifagent-wt\bhc-staging
nhan: may-2 2026-11-17T14:24:22+0700
moc: bece4901296fb2bc61490262ccc9e003c6f2716a

Lưu ý máy: KHÔNG dùng background task, subagent hay thợ con; mọi lệnh chạy tiền cảnh. Gọi `npm.cmd`/`npx.cmd`. Commit + push mỗi 10 phút.
Tiếp bhc-trien-staging-1 (dừng vì ổ VM 4.4 GB và thiếu stg-brand.env). Linh duyệt 17/11 14:22 VN: máy 2 dọn cache docker VM và tạo file khoá staging.
VM: gcloud compute ssh ifagent-event --zone=asia-southeast1-b --project=ifagent-event-2026. TUYỆT ĐỐI KHÔNG chạm container/compose prod (/opt/ifagent), stg-event, ifagent-staging-*, lab, Caddy, DNS.
0. Giờ VN 07:00–22:00, ngoài giờ thì DỪNG. Worktree C:\linhx\ifagent-wt\bhc-staging: `git fetch origin agy/bhc-quan-tri agy/bhc-staging`, merge origin/agy/bhc-quan-tri (đỉnh phải có 9312b33, link thư tuyệt đối) vào agy/bhc-staging; verify + test:lap xanh.
1. Dọn ổ: ghi `df -h /` trước; CHỈ chạy `sudo docker builder prune -af` và `sudo docker image prune -f` (chỉ ảnh treo). CẤM `docker system prune`, `image prune -a`, `volume prune`, xoá container. Ghi `df -h /` sau; vẫn < 5 GB trống thì DỪNG, CAN-LINH kèm `docker system df`.
2. File khoá /opt/stg-brand/stg-brand.env (quyền 600, chủ root), tạo HOÀN TOÀN trên VM bằng một lệnh ssh, KHÔNG để giá trị đi qua máy 2 hay log:
   - ADMIN_CODE: `openssl rand -hex 12` sinh trên VM; đồng thời ghi riêng vào /opt/stg-brand/ADMIN_CODE.txt (600, root) để Linh xem bằng ssh.
   - GEMINI_API_KEY: tìm file env prod của brand-health trong /opt/ifagent bằng `sudo grep -l '^GEMINI_API_KEY=' -r /opt/ifagent --include='*.env' --include='.env*'` (chỉ in TÊN file); chép đúng dòng đó bằng `grep '^GEMINI_API_KEY=' <file> >> stg-brand.env`, không cat/echo giá trị.
   - OPENROUTER_API_KEY, RESEND_API_KEY: để trống (Claude chép sau). Các BH_* lấy từ stg-brand.env.example, BH_URL_GOC=http://127.0.0.1:3920, trần AI thấp, thư thật TẮT.
   - Kiểm: in số dòng và TÊN biến (`cut -d= -f1`), không in giá trị.
3. Làm tiếp bước 5–6 của bhc-trien-staging-1: cổng `cong_phat_hanh.py --truoc` qua đường hầm 127.0.0.1:3920, len-vm.sh deploy SHA đỉnh agy/bhc-staging, `--sha <sha>`; trượt thì lùi :prev. Healthz phải trả đúng SHA. Prod demo.ifagent.net/brand-health-check/ và event.ifagent.net vẫn 200 sau deploy.
4. Chụp 1280 + 360 qua đường hầm: trang chủ, /bao-cao/2026-11-13-vinamilk-9b816db5/, /quan-tri/ đăng nhập. Vào bang-chung/bhc-staging/. Commit + push agy/bhc-staging.
CẤM: deploy prod, sửa /opt/ifagent, rollback-app.sh, in khoá/ADMIN_CODE, gọi AI thật. Trạng thái cao nhất REVIEW.
KET-QUA.md: `dat: co|khong`; df trước/sau; tên biến trong env; SHA staging; healthz; lệnh đường hầm; lệnh lùi; CAN-LINH nếu có.

nhip: 14:30 6p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
