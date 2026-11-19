may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 1
theo_doi: C:\linhx\ifagent-wt\yl19-tap-chi-pdf
nhan: may-2 2026-11-20T04:09:22+0700

Phiếu Yên Lam, tạp chí AGENTIC:ME (góp ý BTC 19/11). Linh đã duyệt: cài Chromium lên máy chủ để PDF giống hệt bản xem online. Chạy mọi lệnh ở tiền cảnh, KHÔNG background task, mỗi bước commit + push ngay (BƯỚC 0 push nhánh rỗng trước).

0. `git -C C:\linhx\ifagent fetch origin yl17-tron` ; `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\yl19-tap-chi-pdf -b agy/yl19-tap-chi-pdf origin/yl17-tron` (nền = bản đang chạy prod 391678ca). Push nhánh ngay. KHÔNG clone mới; node_modules dùng `mklink /J` từ clone sẵn có nếu cần.

VIỆC (mỗi ý một commit "yl19(N): ..."):
(4) PDF trống trên prod. Nguyên nhân: image apps/lab/Dockerfile (node:22-alpine) không có Chromium nên POST /yen-lam/csmo/api/agentic-me-v5/pdf/:sid trả 503 khongCoChromium, điện thoại rơi về chụp trang trong trình duyệt → chỉ còn ảnh nền.
  - Dockerfile: `apk add --no-cache chromium nss freetype harfbuzz ttf-freefont font-noto font-noto-cjk` (giữ alpine), thêm dependency `playwright-core` (cùng bản với repo) vào apps/lab/package.json + lock, ENV `PLAYWRIGHT_CHROMIUM_EXECUTABLE=/usr/bin/chromium-browser`.
  - apps/lab/demos/yen-lam/modules/agentic-me-v5/pdf.js: timPlaywright nhận cả `playwright-core`; launch dùng executablePath từ env khi có; args thêm `--no-sandbox --disable-dev-shm-usage`.
  - Build image thật trên máy (`docker build -f apps/lab/Dockerfile apps/lab` hoặc lệnh build đang dùng trong infra/deploy-app.sh), chạy container cục bộ, gọi POST pdf cho phiên mẫu `mau-k1` (coPdf phải true khi có Chromium) → nhận application/pdf 8 trang A5. Ghi cỡ image trước/sau vào KET-QUA. Xoá build cache sau khi xong (`docker builder prune -f`).
(2) Trang 3 và trang 7 lấy nhầm ảnh Tường chung của khách KHÁC: server apps/lab/server/v1/dien-dan/tuong-chung.js duLieuChoTapChi trả cả ảnh la_cua_khach=false, client public/js/agentic-me-tap-chi-ruot.js chon4AnhT7 và agentic-me-tap-chi-t2-t4.js chon5AnhT3 dùng tcAnh[0] không lọc. Sửa: tạp chí CHỈ dùng ảnh la_cua_khach===true (lọc ở server duLieuChoTapChi khi có khachId, không có khachId thì trả rỗng; client cũng lọc). Test mới: khách A không thấy ảnh khách B.
(3) Trang 2 công ty/chức danh: khi trống đang in câu đệm chuChung.congTyMacDinh "Cộng đồng CSMO Vietnam". Sửa: KHÔNG in câu đệm; trống cả hai thì ẩn hẳn dòng CÔNG TY (cả web, bản in, PDF). Điện thoại agentic-me-v5-dien-thoai.js lấy thêm cong_ty/nghe từ hồ sơ Đồng hành (localStorage dh_cache_toi_v1) như nhánh origin/yl18-tap-chi đã làm (được tham khảo/cherry-pick riêng phần này, KHÔNG lấy bộ vẽ PDF thuần Node trang-anh-node.js/ve-trang-node.js). Test mới: không công ty → không có chữ "Cộng đồng CSMO Vietnam" và không có dòng cong-ty.

KIỂM + BẰNG CHỨNG (C:\linhx\ifagent-wt\yl19-tap-chi-pdf\bang-chung\yl19-tap-chi-pdf\, commit):
  - PDF mẫu từ container: `mau-k1.pdf` + ảnh PNG từng trang (pdftoppm 100dpi) ghép 1 tấm `pdf-8-trang.png`; và ảnh chụp bản web cùng trang ghép cạnh `so-pdf-web.png` (phải khớp chữ + ảnh, không trang trống).
  - Ảnh trang 2 và trang 7 bản web ở 1280 và 360 (PNG ≤ 600 KB).
  - Chạy test lab đủ (`npm i --no-save ws` trong packages/character trước), log thô; lỗi mới ngoài 9 lỗi môi trường đã biết thì sửa.
CẤM: deploy staging/prod, sửa env/khoá, in khoá, xoá dữ liệu, sửa test cũ, sinh ảnh AI, đổi bố cục tạp chí, push lên yl17-tron/yl18-tap-chi/main.
Trả lời KET-QUA.md (ngắn ≤ 2000 ký tự): dòng đầu `dat: co|khong`; SHA đỉnh; cỡ image trước/sau; HTTP + số trang PDF; đường dẫn ảnh so-pdf-web.png; pass/fail test.

nhip: 04:49 40p đang chờ nền · log cuối 0 phút trước [log_cuoi=2026-11-20T04:49:22+0700] · {"conversation_id":"88b8f740-c06c-4754-b4f8-b
