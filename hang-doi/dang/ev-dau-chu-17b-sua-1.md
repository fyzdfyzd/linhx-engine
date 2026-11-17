may: may-3
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 0
theo_doi: D:\linhx\ifagent-wt\ev-dau-chu-17b
nhan: may-3 2026-11-18T00:17:45+0700

Lượt trước bị dừng vì chạy tác vụ nền rồi chờ. Lượt này mọi lệnh phải chạy tiền cảnh, đợi xong trong cùng lệnh.

Phiếu ev-dau-chu-17b (song song): COMMIT + PUSH SAU MỖI Ý.
0. `$env:GIT_TERMINAL_PROMPT=0`. Nếu `git ls-remote https://github.com/fyzdfyzd/ifagent HEAD` lỗi xác thực: dừng ngay, KET-QUA ghi `CAN-LINH: dang nhap GitHub may-3`. Rồi `git clone https://github.com/fyzdfyzd/ifagent D:\linhx\ifagent-wt\ev-dau-chu-17b` (đã có thì fetch), `git checkout -b agy/ev-dau-chu-17b origin/agy/ev-de-xuat-13b`. Trong apps/event: `npm ci`. Ngay sau đó commit rỗng KHÔNG cần; push nhánh khi có commit đầu tiên.
1. Thêm test khoá `apps/event/test/unit/dau-tieng-viet.test.js` (chạy trong npm test): quét mọi chữ hiển thị trong apps/event/public/**/*.html, catalog/**/*.json, public/**/*.js (chuỗi tiếng Việt), bắt: (a) ký tự vỡ mã hoá (Ã, Æ, á», â€, �); (b) dấu tổ hợp rời (NFD) thay vì dựng sẵn NFC; (c) danh sách từ thiếu dấu hay gặp khi đứng một mình: "Lien he", "Su kien", "Trai nghiem", "Giai phap", "Dang ky", "Tai ve", "Bao cao", "khach", "anh" trong câu tiếng Việt có dấu. Thông báo: "<tệp>:<dòng>: <loại lỗi> \"<đoạn>\" — sửa thành chữ có dấu NFC". Bỏ qua slug/URL/khoá JSON/tên tệp.
2. Chạy test (đỏ, ghi bang-chung/ev-dau-chu-17b/do.log), sửa từng chỗ trong dữ liệu chữ cho đúng dấu (không đổi nghĩa, không thêm chữ), chạy lại (xanh.log).
3. npm test sau cùng. KET-QUA: số lỗi tìm thấy theo loại, 10 ví dụ trước→sau.

LUẬT CHUNG cụm event: chạy TIỀN CẢNH, không background task, không dùng lệnh `status` chờ tác vụ; máy chủ nếu cần thì khởi động và tắt BÊN TRONG chính script test. Chỉ sửa apps/event/ và bang-chung/ev-dau-chu-17b/; không đụng apps/lab, packages/, bang-chung cụm khác, nhánh Yên Lam/brand; không deploy, không mail thật, không in khoá, không sửa/xoá test cũ (chỉ thêm ca mới), không sinh ảnh AI, không gọi AI thật, không viết chữ mới (chỉ sửa dấu/lỗi gõ của chữ đang có). Bộ quét bí mật runner báo nhầm dòng CŨ: không sửa các tệp đó; chỉ xác nhận `git diff origin/agy/ev-de-xuat-13b..HEAD` không có bí mật mới. KET-QUA ngắn: dat co/khong; SHA; test đỏ→xanh; pass/fail.

## Lần trước trượt vì:
model: mac-dinh
phieu: ev-dau-chu-17b
may: may-3
trang_thai: dung
ly_do: cho-tac-vu-nen
tep_doi: (khong)
drive: (khong)
phut: 1.14
token: vao=0 ra=0

dừng agy (cho-tac-vu-nen): waiting up to ... background task
warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the default mode.
root agent idle; waiting up to 40m0s for 1 background task(s)

nhip: 00:29 12p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
