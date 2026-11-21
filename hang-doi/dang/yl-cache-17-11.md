may: may-1
loai: code
tran_phut: 40
theo_doi: D:\linhx\wt-cache-17-11
nhan: may-1 2026-11-21T10:48:16+0700

Phiếu CHỐNG CHẠY BẢN CACHE (Linh 16:47: sau deploy không ai phải Ctrl+F5). Hiện trạng đo trên prod: trang HTML Cache-Control no-cache (ổn); JS/CSS /yen-lam/js/*.js trả "public, max-age=3600", nhiều tệp ?v= cố định tay (uik1, rc7p4...) hoặc không có ?v= (/js/audio.js, /js/gemini-live.js, /js/clip-plan.js, kiosk-lam.js...).
Làm:
1) HTML (kiosk, booth, dong-hanh, admin): Cache-Control: no-cache + ETag.
2) JS/CSS: tự gắn ?v=<BUILD_SHA ngắn> (hoặc hash nội dung) cho MỌI script/link khi phục vụ HTML (server thay chỗ ?v cũ / thêm nếu thiếu); immutable max-age dài chỉ khi URL có v= đúng; tệp không có v= -> no-cache.
3) Service worker nếu có: skipWaiting + clients.claim; bản mới thì tự tải lại khi rảnh.
4) Kiosk/booth mở lâu: mỗi 60s gọi GET /api/yl/v1/phien-ban (trả SHA build; tạo nếu chưa có); khác thì tải lại khi RẢNH (không giữa hội thoại/chụp ảnh). BUILD_SHA: compose prod chưa truyền -> ghi SHA vào image lúc build (vd tệp build-sha.txt tạo trong deploy, đọc lúc chạy; KHÔNG sửa compose/env prod). Healthz dùng luôn để hiện commit.
Test: unit cho rewrite ?v và chọn header; test tích hợp cục bộ: đổi BUILD_SHA -> trang trả ?v mới, kiosk mô phỏng nhận /phien-ban khác -> tải lại khi rảnh.
CÁCH LÀM: git clone https://github.com/fyzdfyzd/ifagent D:\linhx\wt-cache-17-11 ; cd D:\linhx\wt-cache-17-11 ; git checkout -b cache-17-11 origin/lam-gap-17-11 (bản 3fd424b1 = ứng viên prod). Cài phụ thuộc theo README/package.json của apps/lab. MỌI LỆNH TIỀN CẢNH, không background task. Commit + PUSH sau mỗi mục (hết giờ không mất việc). Không sửa test khoá nghiem-thu-*; test khoá 10/11 phải xanh. KHÔNG deploy staging/prod (máy 2 gộp và deploy). Không in/đổi khoá. KET-QUA ≤2000 ký tự: SHA nhánh, test, còn thiếu.

nhip: 10:52 4p đang chờ nền · log cuối 3 phút trước [log_cuoi=2026-11-21T10:49:01+0700] · root agent idle; waiting up to 40m0s for 1 ba
