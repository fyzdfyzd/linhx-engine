may: may-2
loai: code
tran_phut: 30
khong_tien_phut: 25
tu_sua: 1
theo_doi: C:\linhx\wt\so-tai-khoan
phu_thuoc: lx-code-so-tai-khoan; lx-do-agy-tai-khoan

Phiếu nối tiếp sổ tài khoản: HẠN MỨC từng tài khoản. Việc phụ, cùng luật cấm phiếu lx-code-so-tai-khoan (không đọc/in cookie, token đăng nhập, mật khẩu; tiền cảnh, KHÔNG background task, mỗi 5 phút có file mới/commit).
1. Làm tiếp nhánh `agy/so-tai-khoan` (`git pull`). Đọc KET-QUA của lx-do-agy-tai-khoan (nhánh hang-doi, xong/lx-do-agy-tai-khoan/KET-QUA.md).
2. Token đã dùng: cộng dòng `token: vao=.. ra=..` của mọi KET-QUA theo tài khoản + máy (24h, 7 ngày).
3. Còn lại / giờ reset: nếu phiếu dò tìm được lệnh chỉ đọc của agy cho hạn mức thì gọi sau mỗi phiếu; không có thì lấy giờ reset từ lỗi 429 ("resets Nh", "quota reached"), ghi `reset_luc`; `con_lai` = "chua_ro" khi không có nguồn. Không bịa số.
4. Ghi vào hang-doi/tai-khoan.json: token_da_dung_24h, token_da_dung_7n, con_lai, reset_luc, nguon (lenh|loi-429|uoc).
5. Bảng 8090 tab Máy: mỗi tài khoản (email che) một dòng: đã dùng 24h, còn lại, reset lúc, trạng thái.
6. Test runner/test_so_tai_khoan.py thêm ca: cộng token đúng, đọc giờ reset từ mẫu 429, "chua_ro" khi thiếu. Chạy `python -m pytest runner -q` + `python -m pytest tests/nghiem-thu -q`. Push `agy/so-tai-khoan`.
Trả lời KET-QUA.md (ngắn): dòng đầu `dat: co`/`dat: khong`; SHA; test; bảng tài khoản máy 2 (email che) | đã dùng 24h | còn lại | reset | nguồn.
