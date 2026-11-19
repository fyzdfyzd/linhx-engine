may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 0
theo_doi: C:\linhx\ifagent-wt\yl19-tap-chi-pdf
nhan: may-2 2026-11-20T04:49:52+0700
moc: 42df5e6df6db38dfe7620461538460cfa7ce7b7c

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

## Lần trước trượt vì:
thuc-hat-giong.json:1232, apps/lab/server/v1/lam/tri-thuc-hat-giong.json:1257, apps/lab/server/v1/lam/tri-thuc-hat-giong.json:1297, apps/lab/server/v1/lam/tri-thuc-hat-giong.json:1333, apps/lab/server/v1/lam/tri-thuc-hat-giong.json:1371, apps/lab/server/v1/lam/tri-thuc-hat-giong.json:1409, apps/lab/server/v1/lam/tri-thuc-hat-giong.json:1443, apps/lab/server/v1/lam/tri-thuc-hat-giong.json:1515, apps/lab/server/v1/lam/tri-thuc-hat-giong.json:1539, apps/lab/server/v1/lam/tri-thuc-hat-giong.json:1563, apps/lab/server/v1/lam/tri-thuc-hat-giong.json:1590, apps/lab/test/agentic-me-luot.test.js:134, apps/lab/test/agentic-me-noi-dung.test.js:71, apps/lab/test/agentic-me-su-kien.test.js:35, apps/lab/test/nghiem-thu-rc7/05-chi-phi.test.js:27, apps/lab/test/nghiem-thu-rc7/09-van-hanh.test.js:153, apps/lab/test/rc7-chi-phi-live.test.js:24, apps/lab/test/sua-401-dong-y.test.js:39, apps/lab/test/t148-quan-tri-chung.test.js:18, apps/lab/test/t161-nen-v1.test.js:546, apps/lab/test/tri-thuc-03-api-qt.test.js:112, apps/lab/test/tri-thuc-04-giao-dien-e2e.test.js:74, apps/lab/test/tri-thuc-04-giao-dien-e2e.test.js:179, apps/lab/test/yen-lam-full-suite.test.js:27, apps/lab/test/yen-lam-t101.test.js:13, apps/lab/test/yl13-brand-safety.test.js:32, apps/lab/test/yl14-hai-khoa.test.js:21, apps/lab/test/yl16-hop.test.js:36, apps/lab/test/yl16-ma-loi.test.js:22, apps/lab/test/yl16-ma-loi.test.js:23, apps/lab/test/yl16-ma-loi.test.js:24, apps/veew-booth/server/setup-kiosks.js:7, docs/T-160-GHI-CHU.md:33

nhip: 04:52 3p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
