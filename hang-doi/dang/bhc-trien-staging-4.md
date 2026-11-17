may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 30
khong_tien_phut: 20
theo_doi: C:\linhx\ifagent-wt\bhc-staging
nhan: may-2 2026-11-18T06:47:22+0700
moc: c52875cec5121b351634c5490f454edb530609c5

Lưu ý máy: KHÔNG background task/subagent; tiền cảnh; KHÔNG chờ/ngủ; `npm.cmd`. Push mỗi bước.
Đưa bản đã sửa 4 đợt (origin/agy/bhc-sua-4 7b853da, 115 test xanh) lên staging stg-brand. Giờ VN 07:00–22:00.
1. Worktree C:\linhx\ifagent-wt\bhc-staging: fetch, merge origin/agy/bhc-sua-4 vào agy/bhc-staging (giữ infra/staging/stg-brand); verify + test:lap xanh; push.
2. Cổng `cong_phat_hanh.py --truoc` qua đường hầm 127.0.0.1:3920 → `len-vm.sh <sha>` → `--sha <sha>`; trượt thì lùi :prev. Prod demo.ifagent.net/brand-health-check/ và event.ifagent.net phải 200. Kiểm `df -h /` VM trước, < 5 GB thì chỉ `docker builder prune -af` + `image prune -f`.
3. KHÔNG quét AI thật. Qua đường hầm chụp 1280 + 360: trang chủ, /bao-cao/2026-11-13-vinamilk-9b816db5/, /quan-tri/ tổng quan (mã trong /opt/stg-brand/ADMIN_CODE.txt, đọc vào biến, không in). Vào bang-chung/bhc-staging-4/, push.
CẤM: deploy prod, sửa /opt/ifagent, stg-event, Caddy, rollback-app.sh, in khoá. KET-QUA: dat, SHA, healthz, ảnh.

nhip: 06:50 3p đang chờ nền · log cuối 0 phút trước [log_cuoi=2026-11-18T06:50:30+0700] · root agent idle; waiting up to 40m0s for 1 ba
