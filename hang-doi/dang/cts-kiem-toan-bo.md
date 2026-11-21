may: may-3
loai: khac
tran_phut: 40
theo_doi: C:\linhx\wt-cts-kiem
nhan: may-3 2026-11-21T22:12:17+0700

Khảo sát sức khoẻ repo Chiêm Tinh Số trước launch 1/12.
1. Clone mới https://github.com/fyzdfyzd/chiemtinhso vào C:\linhx\wt-cts-kiem (có rồi thì git fetch + checkout origin/main).
2. Đọc AGENTS.md, docs/KE-HOACH-NGUOC.md, docs/TAM-NHIN-SAU-LAUNCH.md, .canh/TRANG-THAI.md, dieu-khien.json, docs/HANG-DOI.json.
3. Chạy được gì thì chạy tiền cảnh: python -m pytest -q -x --co (đếm test), rồi pytest cho thư mục không cần Postgres; nếu cần Postgres/Redis mà máy không có thì ghi rõ, không cài.
4. Tìm gắn cứng 'unikon' trong code (grep), liệt kê file:dòng.
5. Liệt kê module trong modules/ và cờ bật/tắt ở config/, đánh dấu module nào cần cho luồng: chọn sản phẩm → nhập ngày sinh → QR SePay → webhook → sinh báo cáo → email.
KET-QUA: test đếm/đạt/đỏ, 10 lỗi chặn launch lớn nhất có file:dòng, đề xuất phạm vi launch hẹp (2–3 sản phẩm).
Luật chung: CHỈ ĐỌC. Không xoá, không sửa, không cài, không deploy, không gửi tin/email/Zalo, không trả tiền, không in bí mật (.env, token, cookie) vào kết quả. Kết quả chính ghi KET-QUA.md ≤ 2000 ký tự, tiếng Việt, gạch đầu dòng; bảng dài ghi file CSV/MD cạnh KET-QUA và chỉ tóm tắt.
