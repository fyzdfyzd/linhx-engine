may: may-3
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 1
theo_doi: D:\linhx\ifagent-wt\ev-hieu-nang-14b
nhan: may-3 2026-11-17T21:53:15+0700
moc: 95b73a5fdecab580834068791c4efcf717c40a19

Phiếu ev-hieu-nang-14c: LÀM TIẾP trong worktree CÓ SẴN D:\linhx\ifagent-wt\ev-hieu-nang-14b (nhánh agy/ev-hieu-nang-14b). Hai lượt trước đo được Lighthouse (truoc-mobile.json, truoc-desktop.json, scripts/do-lighthouse.js) nhưng KHÔNG commit/push nên mất 40 phút.
BƯỚC 0 BẮT BUỘC (trong 3 phút đầu): `$env:GIT_TERMINAL_PROMPT=0`; cd worktree; `git add apps/event bang-chung/ev-hieu-nang-14b`; commit "ev-hieu-nang-14b: do Lighthouse truoc"; `git push -u origin agy/ev-hieu-nang-14b`. Sau đó mỗi lần sửa xong 1 nhóm (ảnh / phông / script / trợ năng / meta) là commit + push ngay.
CẤM tác vụ nền: mọi lệnh chạy tiền cảnh, tự kết thúc; không dùng lệnh `status` chờ tác vụ; Lighthouse chạy từng lô tối đa 6 trang/lệnh, máy chủ khởi động và tắt trong chính script node đó.
Phần việc giữ nguyên như dưới (bỏ bước clone):

Phiếu ev-hieu-nang-14b (song song, máy 3): đo và nâng điểm Lighthouse cho event.ifagent.net bản agy. COMMIT + PUSH SAU MỖI Ý.
0. Nếu `git ls-remote https://github.com/fyzdfyzd/ifagent` lỗi xác thực thì dừng ngay, KET-QUA ghi `CAN-LINH: dang nhap GitHub may-3`. Không mở hộp thoại, đặt `$env:GIT_TERMINAL_PROMPT=0` trước mọi lệnh git. Rồi `git clone https://github.com/fyzdfyzd/ifagent D:\linhx\ifagent-wt\ev-hieu-nang-14b` (nếu đã có thì fetch), `git checkout -b agy/ev-hieu-nang-14b origin/agy/ev-de-xuat-11`. Trong apps/event: `npm ci`, KHÔNG chạy máy chủ nền bằng lệnh riêng: máy chủ phải được khởi động và tắt BÊN TRONG chính tiến trình test/script node (start server → đo → close), mỗi lệnh tự kết thúc. Lần trước agy để một tác vụ nền nên phiếu bị dừng "cho-tac-vu-nen".
1. Chạy Lighthouse (devDependency `lighthouse` + chrome-launcher, headless) chế độ di động và máy bàn cho 18 trang đang có trong test chụp (/, /demo, /giai-phap, 1 trang /giai-phap/<slug>, 1 demo, /blog, 1 bài, /case, /lien-he, /goi, /mau, /thu, /de-xuat, /tao, /tao?agency, 2 trang play, 404). Ghi bảng điểm TRƯỚC vào bang-chung/ev-hieu-nang-14b/BANG-DIEM.md (4 cột: hiệu năng, trợ năng, thực hành tốt, SEO).
2. Sửa trong apps/event cho tới khi MỌI trang di động đạt: hiệu năng ≥ 85, trợ năng ≥ 95, thực hành tốt ≥ 95, SEO ≥ 95. Hướng sửa: ảnh đúng cỡ + srcset + loading=lazy ngoài màn đầu, width/height chống nhảy bố cục, preload phông chính, defer script, alt/label/aria, tương phản màu (cả giao diện Đêm và Sáng), meta description/canonical. Không đổi chữ hiển thị, không đổi bố cục thấy được ở 1280 và 360.
3. Thêm test khoá `apps/event/test/e2e/lighthouse-nguong.test.js` (script npm `test:lh`): chạy 18 trang di động, trượt ngưỡng thì báo "Trang <url>: <hạng mục> <điểm> < <ngưỡng> — xem mục <audit id> trong báo cáo". Ghi bảng SAU vào BANG-DIEM.md.
4. Chạy tiền cảnh: test:lh, khong-tran-ngang, giao-dien-sang, de-xuat-slide; npm test sau cùng. Push agy/ev-hieu-nang-14b.

LUẬT CHUNG cụm event: chạy TIỀN CẢNH, không background task; chỉ sửa apps/event/ và bang-chung/ev-hieu-nang-14b/; không đụng apps/lab, packages/, bang-chung cụm khác, nhánh Yên Lam/brand; không deploy, không mail thật, không in khoá, không sửa/xoá test cũ, không sinh ảnh AI, không gọi AI thật, không viết chữ mới. Bộ quét bí mật runner báo nhầm dòng CŨ: không sửa các tệp đó; chỉ xác nhận `git diff origin/agy/ev-de-xuat-11..HEAD` không có bí mật mới. KET-QUA ngắn: dat co/khong; SHA; bảng điểm trước/sau (trung bình + trang thấp nhất); pass/fail.

nhip: 22:08 15p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
