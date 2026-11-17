may: may-3
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 1
theo_doi: D:\linhx\ifagent-wt\ev-gop-21
nhan: may-3 2026-11-18T00:58:08+0700

Phiếu ev-gop-21 (gộp đợt 1): COMMIT + PUSH SAU MỖI Ý.
0. `$env:GIT_TERMINAL_PROMPT=0`. `git clone https://github.com/fyzdfyzd/ifagent D:\linhx\ifagent-wt\ev-gop-21` (có thì fetch --all), `git checkout -b agy/ev-gop-21 origin/agy/ev-de-xuat-16`. Trong apps/event: `npm ci`.
1. Lần lượt `git merge --no-ff` các nhánh: origin/agy/ev-hieu-nang-14b, origin/agy/ev-bo-cuc-19, và nếu đã có commit sau ev-de-xuat-13b thì thêm origin/agy/ev-lien-ket-18, origin/agy/ev-video-luong-20, origin/agy/ev-dau-chu-17b. Xung đột: giữ cả hai phía (CSS: giữ luật mới của cả hai; package.json: gộp đủ script và devDependency). Push sau mỗi lần merge. Ghi nhánh đã gộp/chưa gộp vào KET-QUA.
2. Slide đề xuất (apps/event/public/xuong): slide 3 chữ mô tả ý tưởng ≥ 28 px và tiêu đề ≥ 56 px, khối chữ không đè ảnh; slide 7 khoảng cách tên chỉ số → dòng phụ ≤ 48 px, cả khối căn giữa dọc. Thêm ca test vào de-xuat-slide.test.js cho 2 ngưỡng này.
3. Chạy tiền cảnh lần lượt: de-xuat-slide, khong-tran-ngang, giao-dien-sang, test:bo-cuc, test:lh, (test:lien-ket nếu đã gộp), npm test. Chụp bang-chung/ev-gop-21/: TONG-1280.png, TONG-360.png (Đêm), TONG-SANG-1280.png, TONG-SANG-360.png (18 trang mỗi tờ, như ev-chup-6), TONG-SLIDE.png. Push agy/ev-gop-21.

LUẬT CHUNG cụm event: chạy TIỀN CẢNH, không background task, không dùng lệnh `status` chờ tác vụ; máy chủ khởi động và tắt BÊN TRONG chính script test. Chỉ sửa apps/event/ và bang-chung/ev-gop-21/; không đụng apps/lab, packages/, bang-chung cụm khác, nhánh Yên Lam/brand; không deploy, không mail thật, không in khoá, không sửa/xoá test cũ (chỉ thêm ca mới), không sinh ảnh AI, không gọi AI thật, không viết chữ mới. Bộ quét bí mật runner báo nhầm dòng CŨ: không sửa các tệp đó. KET-QUA ngắn: nhánh đã gộp; SHA; test pass/fail từng bộ; 5 tờ ảnh.
