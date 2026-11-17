may: may-4
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 1
theo_doi: D:\LINHX\ifagent-wt\ev-lien-ket-18

Phiếu ev-lien-ket-18 (song song): COMMIT + PUSH SAU MỖI Ý.
0. `$env:GIT_TERMINAL_PROMPT=0`. Nếu `git ls-remote https://github.com/fyzdfyzd/ifagent HEAD` lỗi xác thực: dừng ngay, KET-QUA ghi `CAN-LINH: dang nhap GitHub may-4`. Rồi `git clone https://github.com/fyzdfyzd/ifagent D:\LINHX\ifagent-wt\ev-lien-ket-18` (đã có thì fetch), `git checkout -b agy/ev-lien-ket-18 origin/agy/ev-de-xuat-13b`. Trong apps/event: `npm ci`. Ngay sau đó commit rỗng KHÔNG cần; push nhánh khi có commit đầu tiên.
1. Thêm test khoá `apps/event/test/e2e/lien-ket-va-anh.test.js` (script npm `test:lien-ket`): khởi động máy chủ trong test, bò toàn bộ trang nội bộ từ / (giới hạn 200 trang), kiểm: mọi liên kết nội bộ trả 200 (trừ /404 cố ý), mọi ảnh/phông/script tải được, không ảnh nào > 400 KB, mọi ảnh có width/height hoặc aspect-ratio, mọi trang có <title> và meta description riêng, không id trùng trong trang. Thông báo: "<trang> → <tài nguyên>: <lỗi> — <cách sửa>".
2. Chạy (đỏ, bang-chung/ev-lien-ket-18/do.log), sửa trong apps/event: liên kết hỏng, ảnh quá nặng (nén webp bằng sharp, KHÔNG cắt, giữ tỉ lệ), thiếu kích thước, title/description trùng (chỉ ghép từ chữ đã có trên trang), chạy lại (xanh.log).
3. npm test sau cùng. KET-QUA: số lỗi theo loại trước/sau, tổng dung lượng ảnh trước/sau.

LUẬT CHUNG cụm event: chạy TIỀN CẢNH, không background task, không dùng lệnh `status` chờ tác vụ; máy chủ nếu cần thì khởi động và tắt BÊN TRONG chính script test. Chỉ sửa apps/event/ và bang-chung/ev-lien-ket-18/; không đụng apps/lab, packages/, bang-chung cụm khác, nhánh Yên Lam/brand; không deploy, không mail thật, không in khoá, không sửa/xoá test cũ (chỉ thêm ca mới), không sinh ảnh AI, không gọi AI thật, không viết chữ mới (chỉ sửa dấu/lỗi gõ của chữ đang có). Bộ quét bí mật runner báo nhầm dòng CŨ: không sửa các tệp đó; chỉ xác nhận `git diff origin/agy/ev-de-xuat-13b..HEAD` không có bí mật mới. KET-QUA ngắn: dat co/khong; SHA; test đỏ→xanh; pass/fail.
