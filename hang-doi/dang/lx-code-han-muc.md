may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 1
theo_doi: C:\linhx\wt\so-tai-khoan
phu_thuoc: lx-code-so-tai-khoan; lx-do-agy-tai-khoan
nhan: may-2 2026-11-15T12:48:17+0700

Phiếu nối tiếp sổ tài khoản: HẠN MỨC từng tài khoản + TAB "Công cụ" (sổ công cụ + crawler + Zalo). Việc phụ, cùng luật cấm phiếu lx-code-so-tai-khoan (không đọc/in cookie, token đăng nhập, mật khẩu; tiền cảnh, KHÔNG background task, mỗi 5 phút có file mới/commit).
1. Làm tiếp nhánh `agy/so-tai-khoan` (`git pull`). Đọc KET-QUA của lx-do-agy-tai-khoan (nhánh hang-doi, xong/lx-do-agy-tai-khoan/KET-QUA.md).
2. Token đã dùng: cộng dòng `token: vao=.. ra=..` của mọi KET-QUA theo tài khoản + máy (24h, 7 ngày).
3. Còn lại / giờ reset: nếu phiếu dò tìm được lệnh chỉ đọc của agy cho hạn mức thì gọi sau mỗi phiếu; không có thì lấy giờ reset từ lỗi 429 ("resets Nh", "quota reached"), ghi `reset_luc`; `con_lai` = "chua_ro" khi không có nguồn. Không bịa số.
4. Ghi vào hang-doi/tai-khoan.json: token_da_dung_24h, token_da_dung_7n, con_lai, reset_luc, nguon (lenh|loi-429|uoc).
5. Bảng 8090: TAB RIÊNG "Công cụ" (chuyển thẻ Tài khoản ở tab Máy sang đây). Sổ là sổ CÔNG CỤ, không chỉ agy: `cong_cu` là chuỗi tự do (agy, flow, deep-research, anh, chatgpt, heygen, elevenlabs, ...). Mỗi công cụ một khối: các tài khoản (email che) | máy | hồ sơ Chrome | đã dùng 24h | còn lại (token hoặc credit) | reset lúc | trạng thái. Công cụ web chưa đọc được hạn mức thì ghi "chua_ro", chỉ cập nhật khi phiếu dùng nó báo hết. Sắp xếp: công cụ có tài khoản cần đăng nhập/hết hạn mức lên đầu.
5b. Cùng tab "Công cụ", khối "Crawler": tìm crawler đang có trên máy (repo fyzdfyzd/mayquet, D:\LINHX\CRAWLER, D:\linhx\LUU-TRU, MCP linhx-crawler; máy 2 không có thì ghi đường dẫn đã thử). Viết lệnh runner/lenh/crawler.ps1 ghi hang-doi/may/<ma_may>-crawler.json: mỗi nguồn/adapter: lần chạy cuối, số trang/bài lấy được, lỗi/bị chặn gần nhất, thư mục dữ liệu (không chép dữ liệu đã quét, không cookie). Bảng hiện mỗi nguồn một dòng + chấm trạng thái.
5c. Cùng tab, khối "Zalo": tìm bộ nghe Zalo đang chạy trên máy (tiến trình/lịch có chữ zalo, Zalo PC CDP của LAB124 ai-goi-hop, WF20 đội agent nhóm Zalo, LAB083 trợ lý; thư mục D:\linhx, C:\linhx). Lệnh runner/lenh/zalo.ps1 ghi hang-doi/may/<ma_may>-zalo.json: mỗi bộ nghe: đang chạy hay không, nghe NHÓM nào (chỉ tên nhóm), tin cuối nhận lúc mấy giờ, lỗi gần nhất. KHÔNG chép nội dung tin, số điện thoại, tên thành viên. Không tìm thấy thì ghi đường dẫn đã thử.
6. Test runner/test_so_tai_khoan.py thêm ca: cộng token đúng, đọc giờ reset từ mẫu 429, "chua_ro" khi thiếu. Chạy `python -m pytest runner -q` + `python -m pytest tests/nghiem-thu -q`. Push `agy/so-tai-khoan`.
Trả lời KET-QUA.md (ngắn): dòng đầu `dat: co`/`dat: khong`; SHA; test; bảng tài khoản máy 2 (email che) | đã dùng 24h | còn lại | reset | nguồn.

nhip: 13:00 12p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
