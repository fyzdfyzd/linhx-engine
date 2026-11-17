may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 1
theo_doi: C:\linhx\ifagent-wt\ev-de-xuat-10
nhan: may-2 2026-11-17T09:18:22+0700

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

nhip: 09:24 6p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
