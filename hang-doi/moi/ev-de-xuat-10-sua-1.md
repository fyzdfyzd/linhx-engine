may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 0
theo_doi: C:\linhx\ifagent-wt\ev-de-xuat-10

Phiếu ev-de-xuat-10: nâng bộ 8 slide đề xuất từ 8 lên 9 điểm chuẩn tạp chí (Claude soi bang-chung/ev-de-xuat-9/sau/). COMMIT + PUSH SAU MỖI Ý.
0. `git -C C:\linhx\ifagent fetch --all`. `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\ev-de-xuat-10 -b agy/ev-de-xuat-10 origin/agy/ev-de-xuat-9`. Trong apps/event: `npm ci`.
1. Slide 7 "Đo bằng gì": BỎ các thanh tiến độ trang trí (trông như số liệu giả) và bỏ số 01/02/03. Tên chỉ số thành chữ lớn nhất slide (≥ 64 px ở 1920), dòng phụ bên dưới; 3 cột cách nhau bằng đường kẻ mảnh, không hộp.
2. Slide 4 "Khách trải nghiệm": bỏ khoảng trống giữa số và chữ trong thẻ; số lớn và chữ bước đứng sát nhau, chữ bước ≥ 32 px; thẻ cao theo nội dung, cả khối căn giữa theo chiều dọc slide.
3. Slide 5 "Giải pháp dùng": bỏ biểu tượng nhỏ và khoảng trống trên thẻ; mỗi thẻ có ảnh/thumbnail của giải pháp (lấy ảnh sẵn có trong public/web cho AI Ambassador, AI Photobooth...; không sinh ảnh mới) chiếm nửa trên, tên + một dòng nửa dưới.
4. Slide 6 "Lịch triển khai": hộp gọn theo chữ (không cao thừa), khối dòng thời gian căn giữa dọc slide, không để 1/4 dưới trống.
5. Slide 2: bỏ đường kẻ ngang lẻ phía dưới; câu trích ≥ 88 px.
6. Test khoá thêm vào de-xuat-slide.test.js (đỏ trước, xanh sau): không phần tử trang trí dạng thanh tiến độ ở slide 7; khoảng trống dọc lớn nhất trong mỗi slide ≤ 30% chiều cao khung; slide 5 mỗi thẻ có <img> đã tải được.
7. Chạy từng tệp test tiền cảnh: de-xuat-slide, xuong-ev4, xuong-pdf-mail, khong-tran-ngang; npm test sau cùng. Bằng chứng bang-chung/ev-de-xuat-10/: slide-1..8 (1920×1080), pdf-1..8, TONG-SLIDE.png. Push agy/ev-de-xuat-10.

LUẬT CHUNG cụm event: chạy TIỀN CẢNH, không background task; chỉ sửa apps/event/ và bang-chung/ev-de-xuat-10/; không đụng apps/lab, packages/, bang-chung cụm khác, nhánh Yên Lam/brand; không deploy, không mail thật, không in khoá, không sửa/xoá test cũ (trừ thêm ca vào de-xuat-slide.test.js), không sinh ảnh AI, không gọi AI thật, không viết chữ mới trên slide. Bộ quét bí mật runner báo nhầm dòng CŨ: không sửa các tệp đó; chỉ xác nhận `git diff origin/agy/ev-de-xuat-9..HEAD` không có bí mật mới. KET-QUA ngắn: dat co/khong; SHA; test mới đỏ→xanh; pass/fail; đường dẫn TONG-SLIDE.png.

## Lần trước trượt vì:
model: mac-dinh
phieu: ev-de-xuat-10
may: may-2
trang_thai: loi
ly_do: qua_gio
tep_doi: bang-chung/bhc-on-dinh/test-lap.log
drive: (khong)
phut: 40.30
token: vao=0 ra=0

phát hiện bí mật: apps/event/test/e2e/platform.test.js:38, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:73, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:86, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:111, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:212, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:265, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:275, apps/lab/test/agentic-me-luot.test.js:126, apps/lab/test/agentic-me-noi-dung.test.js:71, apps/lab/test/agentic-me-su-kien.test.js:35, apps/lab/test/t148-quan-tri-chung.test.js:18, apps/lab/test/yen-lam-t101.test.js:13, apps/veew-booth/server/setup-kiosks.js:7, infra/staging/stg-event/GOI-LENH-DEPLOY-16-11.md:53, infra/staging/stg-event/chay-cloud.sh:23
