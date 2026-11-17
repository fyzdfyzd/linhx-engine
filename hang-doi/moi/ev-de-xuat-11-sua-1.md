may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 0
theo_doi: C:\linhx\ifagent-wt\ev-de-xuat-11

Phiếu ev-de-xuat-11 (vòng 3, cuối): bộ slide đang 8.5, cần 9. COMMIT + PUSH SAU MỖI Ý.
0. `git -C C:\linhx\ifagent fetch --all`. `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\ev-de-xuat-11 -b agy/ev-de-xuat-11 origin/agy/ev-de-xuat-10`. Trong apps/event: `npm ci`.
1. Khối nội dung chính của slide 4, 6, 7 phải căn giữa theo chiều dọc phần dưới tiêu đề và to lên cho đầy khung: slide 4 thẻ cao ≥ 360 px với số ≥ 120 px và chữ bước ≥ 36 px; slide 6 hộp mốc chữ ≥ 30 px, dòng thời gian ở giữa dọc; slide 7 tên chỉ số ≥ 80 px, cả hàng ở giữa dọc. Không còn khoảng trống dọc liền mạch > 22% chiều cao khung (sửa ngưỡng trong ca test khoảng trống của de-xuat-slide.test.js từ 30% xuống 22% — đây là ca do chính chuỗi phiếu ev-de-xuat thêm, được phép siết).
2. Slide 5: ảnh thẻ giải pháp KHÔNG được trùng ảnh bìa (slide 1) hay ảnh ý tưởng (slide 3). Lấy ảnh riêng của từng giải pháp đang có trong public/web (ảnh trang /giai-phap/<slug>), thêm ca test: src ảnh slide 5 khác src ảnh slide 1 và 3.
3. Slide 4: thêm mũi tên mảnh hoặc đường nối giữa 4 thẻ để đọc thành hành trình (không chữ mới).
4. Chạy từng tệp test tiền cảnh: de-xuat-slide, xuong-ev4, xuong-pdf-mail, khong-tran-ngang; npm test sau cùng. Bằng chứng bang-chung/ev-de-xuat-11/: slide-1..8, pdf-1..8 (1920×1080), TONG-SLIDE.png. Push agy/ev-de-xuat-11.

LUẬT CHUNG cụm event: chạy TIỀN CẢNH, không background task; chỉ sửa apps/event/ và bang-chung/ev-de-xuat-11/; không đụng apps/lab, packages/, bang-chung cụm khác, nhánh Yên Lam/brand; không deploy, không mail thật, không in khoá, không sửa/xoá test cũ ngoài ý 1, không sinh ảnh AI, không gọi AI thật, không viết chữ mới. Bộ quét bí mật runner báo nhầm dòng CŨ: không sửa các tệp đó; chỉ xác nhận `git diff origin/agy/ev-de-xuat-10..HEAD` không có bí mật mới. KET-QUA ngắn: dat co/khong; SHA; test đỏ→xanh; pass/fail; TONG-SLIDE.png.

## Lần trước trượt vì:
model: mac-dinh
phieu: ev-de-xuat-11
may: may-2
trang_thai: loi
ly_do: qua_gio
tep_doi: KET-QUA.md, bang-chung/bhc-quan-tri/a1-dang-nhap-1280.png, bang-chung/bhc-quan-tri/a1-dang-nhap-360.png, bang-chung/bhc-quan-tri/a2-tong-quan-1280.png, bang-chung/bhc-quan-tri/a2-tong-quan-360.png, bang-chung/bhc-quan-tri/a3-luot-quet-1280.png, bang-chung/bhc-quan-tri/a3-luot-quet-360.png, bang-c...
drive: (khong)
phut: 40.30
token: vao=0 ra=0

phát hiện bí mật: apps/event/test/e2e/platform.test.js:38, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:73, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:86, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:111, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:212, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:265, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:275, apps/lab/test/agentic-me-luot.test.js:126, apps/lab/test/agentic-me-noi-dung.test.js:71, apps/lab/test/agentic-me-su-kien.test.js:35, apps/lab/test/t148-quan-tri-chung.test.js:18, apps/lab/test/yen-lam-t101.test.js:13, apps/veew-booth/server/setup-kiosks.js:7, infra/staging/stg-event/GOI-LENH-DEPLOY-16-11.md:53, infra/staging/stg-event/chay-cloud.sh:23
