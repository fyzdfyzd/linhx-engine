may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 1
theo_doi: C:\linhx\wt\so-tai-khoan
nhan: may-2 2026-11-15T12:22:58+0700

Phiếu: SỔ TÀI KHOẢN cho đội máy (danh sách tài khoản đã đăng nhập sẵn trên từng máy, runner tự chọn). Việc PHỤ, ưu tiên thấp: không khởi động lại runner/bảng đang chạy. Chạy mọi lệnh tiền cảnh, KHÔNG background task, mỗi 5 phút có file mới hoặc commit trong theo_doi. TUYỆT ĐỐI không đọc/in/commit cookie, token, mật khẩu; chỉ đọc tên hồ sơ và địa chỉ email hiển thị.
1. `git clone -b claude/project-thread-jowxv1 https://github.com/fyzdfyzd/linhx-engine C:\linhx\wt\so-tai-khoan` (có rồi thì fetch), `git checkout -b agy/so-tai-khoan`.
2. Lệnh mới `runner/lenh/tai-khoan.ps1` (dùng như các lệnh suc-khoe, xem-viec): trên máy đang chạy, liệt kê
   (a) hồ sơ Chrome: đọc `%LOCALAPPDATA%\Google\Chrome\User Data\Local State` → `profile.info_cache`: thư mục hồ sơ, tên, email đăng nhập (`user_name`), có gói (nếu có trường), lần dùng cuối;
   (b) tài khoản agy: chỉ tên tài khoản/email agy đang dùng nếu agy có lệnh hiện (vd `agy whoami`/`agy auth status`); không có thì ghi "chua_ro".
   Ghi `hang-doi/may/<ma_may>-tai-khoan.json` (email che giữa: `zo***@gmail.com`), commit lên nhánh hang-doi như hồ sơ máy hiện có.
3. File sổ chung `hang-doi/tai-khoan.json` (Claude/Linh giữ, runner chỉ đọc): mỗi dòng {ma, email_che, may, ho_so_chrome, cong_cu: [agy|flow|deep-research|anh|chatgpt], trang_thai: dung|het_han_muc|can_dang_nhap, mo_lai_luc}. Viết hàm Python trong runner (file mới runner/so_tai_khoan.py, KHÔNG sửa logic cũ ngoài 1 chỗ gọi) `chon_tai_khoan(may, cong_cu)` → dòng còn dùng được, xoay vòng, bỏ dòng het_han_muc chưa tới giờ mở lại. Phiếu có header `cong_cu: <ten>` thì runner truyền biến môi trường LINHX_HO_SO_CHROME=<thư mục hồ sơ> cho agy (agy dùng `--profile-directory=` khi mở Chrome). Gặp 429/"quota" ở phiếu `cong_cu` thì đánh het_han_muc + mo_lai_luc (lấy giờ trong lỗi, không có thì +5 giờ) và giao lại phiếu cho tài khoản kế.
4. Bảng 8090: thêm thẻ nhỏ "Tài khoản" ở tab Máy: mỗi máy số tài khoản dùng được / hết hạn mức / cần đăng nhập (dữ liệu từ 2 file trên). Không hiện email đầy đủ.
5. Test mới runner/test_so_tai_khoan.py (dữ liệu giả): chọn xoay vòng, bỏ tài khoản hết hạn mức, 429 đánh dấu đúng, email luôn bị che, không có trường token/cookie nào được ghi. Chạy `python -m pytest runner -q` và `python -m pytest tests/nghiem-thu -q`.
6. Chạy thử tai-khoan.ps1 trên máy 2 thật, kiểm file json không chứa token/cookie, push `agy/so-tai-khoan` (KHÔNG push vào claude/project-thread-jowxv1).
CẤM: đăng xuất/đăng nhập tài khoản nào, đọc cookie/Login Data, in khoá. Trạng thái cao nhất REVIEW.
Trả lời KET-QUA.md (ngắn): dòng đầu `dat: co`/`dat: khong`; SHA; test pass/fail; bảng tài khoản máy 2 (email đã che) | hồ sơ Chrome | công cụ đoán được.

nhip: 12:26 3p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
