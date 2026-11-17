may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 30
khong_tien_phut: 20
theo_doi: C:\linhx\ifagent-wt\bhc-staging
nhan: may-2 2026-11-17T19:45:52+0700
moc: 7b2d0545fd87e0382e6c7b66cc8df816b0bffd40

Lưu ý máy: KHÔNG background task/subagent; tiền cảnh; `npm.cmd`. Commit + push mỗi 10 phút.
Đưa bản chi phí thật (origin/agy/bhc-chi-phi 0421fe6) lên staging stg-brand. Giờ VN 07:00–22:00, ngoài giờ DỪNG.
1. Worktree C:\linhx\ifagent-wt\bhc-staging: fetch, merge origin/agy/bhc-chi-phi vào agy/bhc-staging; verify + test:lap xanh; push.
2. Thêm vào /opt/stg-brand/stg-brand.env trên VM (giữ root 600, KHÔNG in giá trị khác): `BH_GIA_OPENROUTER=800`, `BH_TY_GIA=26500`, `BH_TIMEOUT_MS_OPENAI_TIM=90000` (thay nếu đã có). Xoá file /opt/stg-brand/stg-brand.env.bak-* (chứa khoá cũ).
3. Cổng `cong_phat_hanh.py --truoc` → `len-vm.sh` (STG_SHA=<sha mới>) → `--sha <sha>`; trượt thì lùi :prev. Prod demo.ifagent.net/brand-health-check/ và event.ifagent.net phải 200.
4. KHÔNG quét AI thật. Chụp qua đường hầm 1280: /quan-tri/ màn chi tiết lượt quét 2026-11-17-vinamilk-9fc765e8 (đăng nhập bằng mã trong /opt/stg-brand/ADMIN_CODE.txt, đọc vào biến, không in). Vào bang-chung/bhc-staging-3/, push.
CẤM: deploy prod, sửa /opt/ifagent, stg-event, Caddy, rollback-app.sh, in khoá. KET-QUA: dat co|khong, SHA, healthz, ảnh.

nhip: 20:06 21p đang chờ nền · log cuối 0 phút trước [log_cuoi=2026-11-17T20:06:26+0700] · root agent idle; waiting up to 40m0s for 1 ba
