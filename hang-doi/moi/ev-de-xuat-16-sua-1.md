may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 0
phu_thuoc: ev-anh-ly-12f
theo_doi: C:\linhx\ifagent-wt\ev-de-xuat-16

Lượt trước chạy tác vụ nền không ghi log rồi chờ. Tác vụ nền phải có timeout, ghi log vào thư mục theo_doi; dev server/watch phải tắt khi xong.

Phiếu ev-de-xuat-16 (vòng 5): gắn ảnh ly cà phê vào slide đề xuất mẫu + cân slide 7. COMMIT + PUSH SAU MỖI Ý.
0. `git -C C:\linhx\ifagent fetch --all`. `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\ev-de-xuat-16 -b agy/ev-de-xuat-16 origin/agy/ev-de-xuat-13b`. Trong apps/event: `npm ci`. Lấy ảnh từ nhánh hang-doi linhx-engine: `xong/ev-anh-ly-12f/ly-ngang.*`, `ly-vuong.*`.
1. Chép thành `apps/event/public/web/anh/ds/ly-ca-phe-ngang.webp` và `ly-ca-phe-vuong.webp` (sharp, chất lượng 82, KHÔNG cắt, giữ tỉ lệ; ≤ 400 KB). Slide 3 (ý tưởng): thay ảnh rạp chiếu bằng ảnh ly cà phê; nếu chỉ có ảnh ngang thì dùng ảnh ngang cho slide 3, khung ảnh slide 3 đổi theo đúng tỉ lệ ảnh (không méo, không cắt mất ly). Slide 1 (bìa) GIỮ ảnh hiện tại. Thêm ca test: src ảnh slide 3 chứa `ly-ca-phe`, naturalWidth > 0, tỉ lệ khung chứa lệch tỉ lệ ảnh ≤ 5%.
2. Slide 7: 3 cột chỉ số rộng bằng nhau, tên chỉ số mỗi cột 1 dòng ("Lượt trò chuyện" không gãy dòng — giảm cỡ chữ đồng đều cả 3 cột nếu cần, vẫn ≥ 64 px), dòng phụ cùng một hàng chân. Thêm ca test: 3 cột chênh rộng ≤ 2%, mỗi tên chỉ số đúng 1 dòng.
3. Chạy tiền cảnh: de-xuat-slide, xuong-ev4, xuong-pdf-mail, khong-tran-ngang, giao-dien-sang; npm test sau cùng. Bằng chứng bang-chung/ev-de-xuat-16/: slide-1..8, pdf-1..8 (1920×1080), TONG-SLIDE.png. Push agy/ev-de-xuat-16.

LUẬT CHUNG cụm event: chạy TIỀN CẢNH, không background task; chỉ sửa apps/event/ và bang-chung/ev-de-xuat-16/; không đụng apps/lab, packages/, bang-chung cụm khác, nhánh Yên Lam/brand; không deploy, không mail thật, không in khoá, không sửa/xoá test cũ (chỉ thêm ca mới), không sinh ảnh AI, không gọi AI thật, không viết chữ mới. Bộ quét bí mật runner báo nhầm dòng CŨ: không sửa các tệp đó; chỉ xác nhận `git diff origin/agy/ev-de-xuat-13b..HEAD` không có bí mật mới. KET-QUA ngắn: dat co/khong; SHA; test đỏ→xanh; pass/fail; TONG-SLIDE.png.

## Lần trước trượt vì:
model: mac-dinh
phieu: ev-de-xuat-16
may: may-2
trang_thai: loi
ly_do: cho-nen-im-lang
tep_doi: (khong)
drive: (khong)
phut: 7.05
token: vao=0 ra=0

phát hiện bí mật: apps/event/test/e2e/platform.test.js:38, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:73, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:86, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:111, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:212, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:265, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:275, apps/lab/test/agentic-me-luot.test.js:126, apps/lab/test/agentic-me-noi-dung.test.js:71, apps/lab/test/agentic-me-su-kien.test.js:35, apps/lab/test/t148-quan-tri-chung.test.js:18, apps/lab/test/yen-lam-t101.test.js:13, apps/veew-booth/server/setup-kiosks.js:7, infra/staging/stg-event/GOI-LENH-DEPLOY-16-11.md:53, infra/staging/stg-event/chay-cloud.sh:23
