may: may-3
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 1
theo_doi: D:\linhx\ifagent-wt\ev-gop-22

Phiếu ev-gop-22 (hoàn tất 2 test khoá còn đỏ trên nhánh gộp): COMMIT + PUSH SAU MỖI Ý.
0. `$env:GIT_TERMINAL_PROMPT=0`. `git clone https://github.com/fyzdfyzd/ifagent D:\linhx\ifagent-wt\ev-gop-22` (có thì fetch --all), `git checkout -b agy/ev-gop-22 origin/agy/ev-gop-21`. Trong apps/event: `npm ci`.
1. Chạy `node --test apps/event/test/unit/dau-tieng-viet.test.js` (ghi do.log). Sửa từng lỗi dấu/vỡ mã trong dữ liệu chữ cho tới xanh (không đổi nghĩa, không thêm chữ). Push.
2. Chạy `npm run test:lien-ket` (ghi do.log). Sửa liên kết hỏng, ảnh > 400 KB (sharp → webp, KHÔNG cắt, giữ tỉ lệ), thiếu width/height, title/description trùng (chỉ ghép từ chữ có sẵn trên trang) cho tới xanh. Push.
3. Ảnh chụp /de-xuat đang hiện trạng thái "Đề xuất này không còn mở được": trong script chụp tờ TONG, trang 13 phải mở /de-xuat với mã đề xuất mẫu Trà Việt có sẵn (để thấy slide thật). Chỉ sửa script chụp, không đổi trang.
4. Chạy tiền cảnh lần lượt: dau-tieng-viet, test:lien-ket, de-xuat-slide, khong-tran-ngang, giao-dien-sang, test:bo-cuc, test:lh, npm test. Chụp lại bang-chung/ev-gop-22/: TONG-1280, TONG-360, TONG-SANG-1280, TONG-SANG-360, TONG-SLIDE. Ghi bang-chung/ev-gop-22/KET-QUA-TEST.md: mỗi bộ test pass/fail, số ca. Push agy/ev-gop-22.

LUẬT CHUNG cụm event: chạy TIỀN CẢNH, không background task, không dùng lệnh `status` chờ tác vụ; máy chủ khởi động và tắt BÊN TRONG chính script test. Chỉ sửa apps/event/ và bang-chung/ev-gop-22/; không đụng apps/lab, packages/, bang-chung cụm khác, nhánh Yên Lam/brand; không deploy, không mail thật, không in khoá, không sửa/xoá test cũ, không sinh ảnh AI, không gọi AI thật, không viết chữ mới. Bộ quét bí mật runner báo nhầm dòng CŨ: không sửa các tệp đó. KET-QUA ngắn: SHA; bảng pass/fail từng bộ; số lỗi dấu và lỗi liên kết đã sửa.
