may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 2
theo_doi: C:\linhx\ifagent-wt\yl20-template
nhan: may-2 2026-11-20T10:33:22+0700

LUẬT MỚI của Linh 20/11 10:28: tạp chí AGENTIC:ME tạo từ ảnh khách (bản web, bản in, PDF tải về) VÀ ảnh bìa hiển thị phải theo DUY NHẤT template InDesign: hang-doi/du-an/yl20-template/TEMPLATE-CHUAN-layout_AgenticMe_Quynh.pdf (5 trang PDF = bìa, cặp 2|3, 4|5, 6|7, trang 8; A5). Chữ trong template là chữ giả, chỉ lấy BỐ CỤC, font, cỡ, màu, vị trí ảnh. Ảnh đối chiếu template|prod hiện tại: doi-chieu-0..4.png cùng thư mục. Chạy tiền cảnh, mỗi bước commit + push ngay (bước 0 push nhánh trước).

0. `git -C C:\linhx\ifagent fetch origin`. Nền = origin/yl18-bia-dt-lam (da85e71a, đang chạy prod) hoặc nhánh yl18 mới nhất đang ở prod (so /healthz commit của https://demo.ifagent.net). `worktree add C:\linhx\ifagent-wt\yl20-template -b agy/yl20-template <nền>`. KHÔNG clone mới.
1. Đo template: `pdftoppm -r 150` từng trang, `pdffonts`, `pdftotext -bbox-layout` lấy toạ độ/cỡ chữ. Ghi bảng đo vào bang-chung/yl20-template/DO-TEMPLATE.md (mỗi khối: trang, x/y/w/h theo %, font, cỡ, màu).
2. Sửa theo bảng đo (mỗi trang một commit "yl20(Tn): ..."):
   - Font: tiêu đề UTM Hanzel, condensed HCP Tungsen, thân bài Barlow (Light/Regular/Bold, OFL, tải từ Google Fonts vào public/fonts, khai trong tap-chi.cau-hinh.json). Chỉnh cỡ chữ/khoảng cách khớp template.
   - Bìa (cả ảnh bìa có chữ bia-chu.jpg hiện trên ĐT/kiosk/QR và trang 1): masthead AGENTIC ME màu ĐEN trên dải nền TRẮNG phía trên, ảnh khách + Lam ở dưới, cover lines + "AGENTIC:ME / The <tên> Edition" như template.
   - Trang 2: "CÔNG TY" hiện khi có dữ liệu thật (không câu đệm), bố cục 2 cột như template.
   - Trang 3: tiêu đề 2 dòng cỡ lớn; cột trái 5 ảnh SỰ KIỆN (không ảnh khách).
   - Trang 4: ảnh sự kiện thật thay KV poster; tiêu đề 2 dòng lớn.
   - Trang 5: ảnh khách + Lam khung vuông như template; "YÊN LAM / GỢI Ý" 2 dòng lớn.
   - Trang 6: nền xanh + ảnh sự kiện tràn, chữ "NHỮNG / HÌNH ẢNH / NỔI BẬT" 3 dòng font đậm trắng như template.
   - Trang 7: 4 ảnh SỰ KIỆN (bỏ ảnh AI check-in/sảnh và ảnh khách), đoạn thân chữ đậm căn phải.
   - Trang 8: ảnh sự kiện trên cùng, hộp trắng 2 cột, tiêu đề đậm, chân trang logo như template (bỏ logo VSM thừa góc phải).
   - Ảnh sự kiện: tạo khoá cấu hình danh sách ảnh BTC (hinhAnh.suKien = mảng) dùng chung cho T3/T4/T6/T7/T8; hiện dùng assets/su-kien/toan-the-1.jpg, toan-the-2.jpg, phần còn thiếu để ô trống placeholder trung tính và ghi CHUA_DU_ANH_BTC (KHÔNG sinh ảnh AI, KHÔNG dùng ảnh AI cũ t131/t146).
   - Tường chung: tạp chí chỉ dùng ảnh la_cua_khach===true (cherry-pick ý từ origin/agy/yl19-tap-chi-pdf commit 981461ad).
   - PDF tải về: một nguồn dựng duy nhất từ HTML bằng Chromium (cherry-pick 5476bd31 Dockerfile + pdf.js từ agy/yl19-tap-chi-pdf, đã chạy đạt trên staging). Bộ vẽ thuần Node (trang-anh-node.js/ve-trang-node.js) chỉ còn là dự phòng khi không có Chromium.
3. Test khoá mới apps/lab/test/yl20-template.test.js: font Barlow được nạp; trang 7 không có ảnh khách/AI cũ; trang 2 không có "Cộng đồng CSMO Vietnam"; khách A không thấy ảnh Tường chung khách B.
4. Bằng chứng bang-chung/yl20-template/: render phiên mẫu mau-k1 tên "Trần Thị Quỳnh" bằng Chromium cục bộ, xuất PDF, ghép CẠNH template theo đúng cặp trang (so-0..so-4.png, cùng chiều cao, PNG ≤ 600 KB); ảnh bìa có chữ cạnh trang 1 template; ảnh web ĐT 360 và 1280. Tự chấm từng trang lệch gì còn lại.
5. Chạy test lab đủ (`npm i --no-save ws` trong packages/character), log thô, sửa lỗi mới. Push agy/yl20-template.
CẤM: deploy staging/prod, sửa env/khoá, sinh ảnh AI, xoá dữ liệu, sửa test cũ để xanh, push lên nhánh yl18-*/main.
KET-QUA.md ≤ 2000 ký tự: `dat: co|khong`; SHA; bảng 8 trang (khớp/lệch còn lại); số ảnh BTC còn thiếu; pass/fail test; đường dẫn so-*.png.

nhip: 10:34 1p đang chờ nền · log cuối 0 phút trước [log_cuoi=2026-11-20T10:34:18+0700] · root agent idle; waiting up to 40m0s for 1 ba
