may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 0
theo_doi: C:\linhx\ifagent-wt\ev-de-xuat-9
phu_thuoc: ev-sang-8
nhan: may-2 2026-11-17T08:20:51+0700
moc: 2396c241922c6c3c637641b2f6571b14fe491b43

Phiếu cụm event.ifagent.net (ev-de-xuat-9): làm bản ĐỀ XUẤT của xưởng ý tưởng thành bộ SLIDE đẹp, chỉn chu như TẠP CHÍ (anh Linh 17/11). Claude chấm bản hiện tại 6.5/10: trông như tài liệu, ảnh chung chung không thể hiện ý tưởng, chữ nhỏ, lịch triển khai chữ bị gãy dòng, phần đo lường không có điểm nhấn.
0. `git -C C:\linhx\ifagent fetch --all`. `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\ev-de-xuat-9 -b agy/ev-de-xuat-9 origin/agy/ev-sang-8` (nếu ev-sang-8 chưa push thì dùng origin/agy/ev-tran-7). Trong apps/event: `npm ci`.
1. Bằng chứng TRƯỚC: xuất PDF đề xuất hiện tại với dữ liệu mẫu (Trà Việt, như test xuong-pdf-mail) rồi chuyển từng trang thành PNG 1600 px rộng vào bang-chung/ev-de-xuat-9/truoc/.
2. Dựng bộ slide 16:9 (1920×1080) dùng chung cho trang web /de-xuat/<mã> (chế độ xem slide, phím ← →, vuốt trên điện thoại) và cho PDF tải về/gửi mail (mỗi slide một trang ngang). 8 slide:
   1 Bìa: ảnh hình thử tràn khung, tên khách cỡ lớn, dòng "Đề xuất sự kiện · <ngày>", logo IF Agent nhỏ góc.
   2 Một câu: tên ý tưởng làm câu trích lớn (pull quote) + mô tả một dòng.
   3 Ý tưởng: ảnh lớn ≥ 55% khung + tiêu đề + tối đa 30 chữ.
   4 Khách trải nghiệm: 4 bước, số thứ tự lớn, mỗi bước ≤ 8 chữ.
   5 Giải pháp dùng: thẻ cho từng giải pháp (tên + một dòng).
   6 Lịch triển khai: dòng thời gian ngang, chữ không gãy dòng giữa từ.
   7 Đo bằng gì: 3 chỉ số chữ lớn.
   8 Bước tiếp: nút/link "Để team IF Agent làm thật", lienhe@ifagent.net, mã QR về trang đề xuất.
   Chỉ dùng chữ đang có trong dữ liệu đề xuất và câu đang có trên trang, không tự viết chữ mới. Font Be Vietnam Pro / Montserrat (nhúng vào PDF, đủ dấu tiếng Việt), bảng màu sẵn có trong public/web/css/web.css (nền Đêm #0B1220, Giấy #F4F6F8, xanh #0088FF, gradient #2E9FF8→#02DCAF, nhát cắt 34°). Lề an toàn 96 px, lưới 12 cột, khoảng trắng rộng, mỗi slide một ý.
3. TEST KHOÁ mới test/e2e/de-xuat-slide.test.js (đỏ trước, xanh sau), thông báo lỗi nêu slide + phần tử: đúng 8 slide 16:9; không phần tử nào tràn khỏi khung slide; cỡ chữ nhỏ nhất ≥ 22 px ở 1920; mỗi slide ≤ 40 chữ; ảnh bìa phủ ≥ 60% diện tích slide 1; PDF có 8 trang khổ ngang và chứa font nhúng; không chữ nào bị gãy giữa từ ở slide 6. Đề xuất có ít trường (thiếu ảnh, thiếu đo lường) vẫn ra đủ slide, không ô trống.
4. Bằng chứng SAU: PNG từng slide 1920×1080 từ trang web và PNG từng trang PDF vào bang-chung/ev-de-xuat-9/sau/, ghép TONG-SLIDE.png (lưới 2×4); chụp trang /de-xuat ở 360 (vuốt) 3 slide đầu.
5. npm test + test mới + e2e xưởng (xuong-ev4) + khong-tran-ngang. Push agy/ev-de-xuat-9.

LUẬT CHUNG cụm event: chạy mọi lệnh TIỀN CẢNH, không background task; chỉ sửa apps/event/ và bang-chung/ev-de-xuat-9/; không đụng apps/lab, packages/, nhánh Yên Lam/brand; không deploy, không mail thật, không in khoá, không sửa/xoá test cũ, không sinh ảnh bằng AI (dùng ảnh mẫu đang có), không gọi AI thật. Bộ quét bí mật runner báo nhầm dòng CŨ (apps/lab/..., platform.test.js:38, apps/veew-booth/..., infra/staging/stg-event/...): không sửa các tệp đó; phiếu sửa chỉ cần xác nhận `git diff <base>..HEAD` không có bí mật mới. KET-QUA ngắn: dat co/khong; SHA đỉnh; test mới đỏ→xanh; pass/fail npm test; đường dẫn TONG-SLIDE.png.

## Lần trước trượt vì:
model: mac-dinh
phieu: ev-de-xuat-9
may: may-2
trang_thai: loi
ly_do: qua_gio
tep_doi: KET-QUA.md, bang-chung/bhc-code-khung-quan-tri/a-dang-nhap-1280-dem.png, bang-chung/bhc-code-khung-quan-tri/a-dang-nhap-1280-sang.png, bang-chung/bhc-code-khung-quan-tri/b-tong-quan-1280-sang.png, bang-chung/bhc-code-khung-quan-tri/b-tong-quan-360-sang.png, bang-chung/bhc-code-khung-quan-tri/c-lu...
drive: (khong)
phut: 40.31
token: vao=0 ra=0

phát hiện bí mật: apps/event/test/e2e/platform.test.js:38, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:73, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:86, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:111, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:212, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:265, apps/lab/demos/yen-lam/modules/san-khau/san-khau.html:275, apps/lab/test/agentic-me-luot.test.js:126, apps/lab/test/agentic-me-noi-dung.test.js:71, apps/lab/test/agentic-me-su-kien.test.js:35, apps/lab/test/t148-quan-tri-chung.test.js:18, apps/lab/test/yen-lam-t101.test.js:13, apps/veew-booth/server/setup-kiosks.js:7, infra/staging/stg-event/GOI-LENH-DEPLOY-16-11.md:53, infra/staging/stg-event/chay-cloud.sh:23
