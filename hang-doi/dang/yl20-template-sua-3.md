may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 1
theo_doi: C:\linhx\ifagent-wt\yl20-template
nhan: may-2 2026-11-20T12:10:22+0700
moc: e1a836adb842234f1a53316d22d628afe8f4f35d

Vòng sửa 3 nhánh agy/yl20-template (e1a836ad), rồi đưa lên STAGING. Claude chấm ảnh so-*.png: đạt bố cục. Claude chạy test tạp chí trên cloud: yl20 làm ĐỎ MỚI 2 test (nền da85e71a xanh 2 test này). Chạy tiền cảnh, KHÔNG để agy chạy tác vụ nền (lần trước kẹt 'root agent idle waiting background task' tới quá giờ). Mỗi bước commit + push.

0. Worktree C:\linhx\ifagent-wt\yl20-template, `git pull --ff-only origin agy/yl20-template`.
1. Sửa (mỗi ý một commit "yl20(sua3): ..."):
   a) test/tap-chi-chan-02-ro-du-lieu.test.js "2b-dung-trang": lỗi 'Chữ Lam viết lại sạch được dùng ở T3' — T3 không còn hiện câu Lam viết lại (lam_viet_lai) từ ảnh/bài Tường chung CỦA CHÍNH KHÁCH ở mốc "LÊN BÌA AGENTIC:ME". Khôi phục: ảnh cột trái vẫn là ảnh sự kiện, nhưng chữ Lam viết lại sạch của chính khách vẫn vào dòng mốc như trước.
   b) cùng file "2c-api-server": `jTc.tuongChung.anh.length` mong 1, ra 0. Xem test: nếu ảnh do CHÍNH khách của phiên đăng thì server phải tìm ra khachId (viec_bia/khách gắn với phiên) và trả ảnh đó → sửa code. Nếu test đọc ảnh của khách KHÁC thì đây là đổi luật riêng tư (Linh 19/11: tạp chí chỉ dùng ảnh của chính khách): KHÔNG sửa test cũ, ghi rõ trong KET-QUA dòng `DOI_LUAT_TEST: 2c` kèm giải thích để Claude quyết.
   Kiểm: `node --test --test-concurrency=4 --test-timeout=120000 test/yl20-template.test.js test/*tap-chi*.test.js test/yl19*.test.js` — chỉ được đỏ đúng các test đã đỏ trên nền da85e71a: E2E-08, E2E Admin BTC, yl09-tap-chi (2), "không còn mã màu cứng" (nếu có). Ghi log thô vào bang-chung/yl20-template/test-tap-chi.log.
2. Kiểm VM: df/free/docker system df; ổ trống < 5 GB thì `docker builder prune -af` (chỉ build cache). RAM > 80% thì DỪNG, ghi VM_DAY.
3. `cmd.exe /c "cd /d C:\linhx\ifagent-wt\yl20-template && infra\deploy.bat lab --staging"`.
4. Kiểm staging https://staging-demo.ifagent.net: /healthz commit khớp; `docker exec ifagent-staging-lab sh -c 'ls /usr/bin/chromium*'`; POST /yen-lam/csmo/api/agentic-me-v5/pdf/mau-k1 {"ten":"Trần Thị Quỳnh"} → 200 PDF 8 trang (thời gian); GET /yen-lam/csmo/api/agentic-me-v5/bia/mau-k1 → ảnh bìa có chữ; Playwright ĐT 360 + 1280: tab tạp chí, bấm TẢI PDF A5 thật → file PDF có chữ. Ghép stg-pdf vs template (so-stg-0..4.png) + stg-bia-chu.png vào bang-chung/yl20-staging/. Prod healthz vẫn 200, uptime không reset.
CẤM: deploy prod, sửa env/khoá, xoá dữ liệu/volume, image prune -a, sửa test cũ để xanh, sinh ảnh AI, push yl18-*/main.
KET-QUA.md ≤ 2000 ký tự: `dat: co|khong`; SHA; test tạp chí pass/fail + tên test đỏ; DOI_LUAT_TEST nếu có; staging commit + PDF (HTTP, số trang, giây); ổ/RAM VM; prod healthz; đường dẫn so-stg-*.png.

nhip: 12:15 5p đang chờ nền · log cuối 0 phút trước [log_cuoi=2026-11-20T12:15:45+0700] · root agent idle; waiting up to 40m0s for 1 ba
