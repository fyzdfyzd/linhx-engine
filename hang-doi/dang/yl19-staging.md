may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 1
theo_doi: C:\linhx\ifagent-wt\yl19-tap-chi-pdf
nhan: may-2 2026-11-20T07:54:21+0700
moc: 036ea544ec27f09e963712e865c33f1a7a4540ba

Phiếu Yên Lam: đưa nhánh agy/yl19-tap-chi-pdf (036ea544) lên STAGING stg-lab. Linh đã duyệt "lên staging" 20/11 07:51. KHÔNG đụng prod (đang ngày 2 sự kiện). Chạy tiền cảnh, không background, mỗi bước ghi log vào theo_doi.

0. `git -C C:\linhx\ifagent fetch origin agy/yl19-tap-chi-pdf`. Worktree C:\linhx\ifagent-wt\yl19-tap-chi-pdf đã có thì `git -C ... merge --ff-only origin/agy/yl19-tap-chi-pdf`, chưa có thì `worktree add` từ origin/agy/yl19-tap-chi-pdf. HEAD phải là 036ea544 (hoặc con cháu của nó trên nhánh này).
1. Kiểm VM trước (gcloud compute ssh như deploy.bat, lệnh chỉ đọc + dọn cache): `df -h /`, `free -m`, `docker system df`. Nếu ổ trống < 5 GB: `docker builder prune -af` (CHỈ build cache; KHÔNG image prune -a, KHÔNG xoá image/volume/container prod). Ghi số trước/sau. RAM dùng > 80% thì DỪNG, ghi VM_DAY.
2. `cmd.exe /c "cd /d C:\linhx\ifagent-wt\yl19-tap-chi-pdf && infra\deploy.bat lab --staging"` (giống phiếu yl09-deploy). Image mới có thêm Chromium (apk) nên build lâu hơn. Lỗi apk/build thì ghi nguyên log, không tự sửa Dockerfile quá 1 lần (sửa thì commit+push nhánh, ghi rõ).
3. Kiểm trên staging (https://staging-demo.ifagent.net):
   - `/healthz` 200, BUILD_SHA khớp.
   - Trong container: `docker exec ifagent-staging-lab sh -c 'ls -la /usr/bin/chromium*; chromium-browser --version || chromium --version'`.
   - `GET /yen-lam/csmo/api/agentic-me-v5/tap-chi/mau-k1` → coPdf phải true.
   - `POST /yen-lam/csmo/api/agentic-me-v5/pdf/mau-k1` body {"ten":"Tran Thi Quynh"} → 200 application/pdf, đếm số trang = 8, đo thời gian. Lưu stg-mau-k1.pdf, `pdftoppm -png -r 100` (cài Poppler qua winget nếu thiếu) ghép 1 tấm `stg-pdf-8-trang.png`.
   - Chụp Playwright màn tạp chí điện thoại (/yen-lam/#tap-chi hoặc /yen-lam/csmo/agentic-me-v5/mau-k1) ở 360 và 1280, bấm "TẢI PDF A5" thật, lưu file tải về và xác nhận là PDF 8 trang có chữ (không trống).
   - `free -m` VM sau khi xuất PDF 3 lần liên tiếp; prod `https://demo.ifagent.net/healthz` vẫn 200 và uptime không reset.
4. Bằng chứng vào bang-chung/yl19-staging/ (PNG ≤ 600 KB), commit + push lên agy/yl19-tap-chi-pdf.
CẤM: deploy prod (`deploy.bat lab` không có --staging), sửa env/khoá, in khoá, xoá dữ liệu/volume, image prune -a, đổi Caddyfile, gửi tin ra ngoài.
Trả lời KET-QUA.md ≤ 2000 ký tự: dòng đầu `dat: co|khong`; SHA staging; ổ/RAM VM trước/sau; phiên bản Chromium trong container; HTTP + số trang + thời gian PDF; prod healthz; đường dẫn stg-pdf-8-trang.png.

nhip: 07:56 2p đang chờ nền · log cuối 0 phút trước [log_cuoi=2026-11-20T07:56:35+0700] · root agent idle; waiting up to 40m0s for 2 ba
