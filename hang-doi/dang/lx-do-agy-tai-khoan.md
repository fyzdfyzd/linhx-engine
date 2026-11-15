may: may-2
loai: kiem
tran_phut: 25
khong_tien_phut: 20
theo_doi: C:\linhx\wt\do-agy-tai-khoan
nhan: may-2 2026-11-15T12:22:28+0700

Phiếu DÒ (chỉ đọc, không đổi đăng nhập, không đăng xuất, không in token/khoá). Chạy mọi lệnh tiền cảnh, KHÔNG background task, mỗi 5 phút ghi file mới vào thư mục theo_doi.
Mục tiêu: biết runner có tự đổi tài khoản agy khi hết hạn mức được không.
1. Tìm agy lưu đăng nhập ở đâu: liệt kê (chỉ TÊN file/thư mục, không nội dung) trong %USERPROFILE%\.gemini, %APPDATA%, %LOCALAPPDATA% có chữ antigravity/gemini/agy. Ghi đường dẫn + cỡ.
2. `agy --help` và help lệnh con: có cờ/biến môi trường chọn thư mục cấu hình hay hồ sơ không (vd --profile, --config-dir, GEMINI_HOME, HOME, USERPROFILE). Ghi nguyên văn dòng liên quan.
3. Thử an toàn: tạo C:\linhx\wt\do-agy-tai-khoan\home-thu, chạy `agy --version` (hoặc lệnh không cần mạng) với USERPROFILE/HOME trỏ vào đó: agy có đòi đăng nhập lại không, có tạo cấu trúc thư mục mới không. KHÔNG đăng nhập.
4. Xem log runner 24h qua (thư mục log runner) có dòng 429 / "quota" không, ghi nguyên văn 1 dòng mẫu (che email).
Trả lời KET-QUA.md (ngắn): dòng đầu `dat: co` nếu tìm được cách tách đăng nhập theo thư mục, `dat: khong` nếu không; đường dẫn lưu đăng nhập; cờ/biến dùng được; mẫu dòng lỗi hạn mức.
