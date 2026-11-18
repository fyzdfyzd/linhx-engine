may: may-2
loai: code
model: gemini-4-argon-high
tran_phut: 25
khong_tien_phut: 15
theo_doi: C:\linhx\ifagent-wt\bhc-staging

Lưu ý máy: KHÔNG background task/subagent; KHÔNG chờ/ngủ; mỗi lệnh phải xong trong 3 phút (lệnh lâu hơn bị máy coi là chạy nền và dừng phiếu). Push mỗi bước.
Tiếp bhc-trien-staging-4 (đã merge agy/bhc-sua-4 vào agy/bhc-staging ef3616e, dừng ở bước chụp vì đọc ADMIN_CODE.txt thiếu sudo).
1. Qua gcloud ssh: `curl -s http://127.0.0.1:3920/healthz`. Nếu BUILD_SHA chưa phải ef3616e (7 ký tự đầu) thì chạy cổng `cong_phat_hanh.py --truoc` → `len-vm.sh ef3616e` → `--sha ef3616e`; trượt thì lùi :prev. Prod demo.ifagent.net/brand-health-check/ và event.ifagent.net phải 200.
2. Mã quản trị đọc bằng `sudo cat /opt/stg-brand/ADMIN_CODE.txt` vào biến, không in. Qua đường hầm chụp 1280 + 360: trang chủ, /bao-cao/2026-11-13-vinamilk-9b816db5/, /quan-tri/ tổng quan. Vào bang-chung/bhc-staging-4/, push agy/bhc-staging.
CẤM: deploy prod, sửa /opt/ifagent, stg-event, Caddy, rollback-app.sh, in khoá, quét AI thật. KET-QUA: dat, SHA, healthz, ảnh.
