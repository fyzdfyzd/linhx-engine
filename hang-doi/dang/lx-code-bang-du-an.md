may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
tu_sua: 1
theo_doi: C:\linhx\wt\bang-du-an
nhan: may-2 2026-11-15T12:12:38+0700

Phiếu: thêm 2 tab "Dự án" và "Chất lượng" cho bảng theo dõi (runner/bang/bang.py, cổng 8090). Việc PHỤ, ưu tiên thấp: KHÔNG khởi động lại bảng đang chạy, KHÔNG đụng runner/linhx_runner.py, hang_doi_git.py, không chạy Playwright song song quá 1 trình duyệt (máy đang chạy phiếu Yên Lam). Chạy mọi lệnh ở tiền cảnh, KHÔNG dùng background task, mỗi 5 phút phải có file mới hoặc commit trong thư mục theo_doi.
1. `git clone -b claude/project-thread-jowxv1 https://github.com/fyzdfyzd/linhx-engine C:\linhx\wt\bang-du-an` (có rồi thì fetch + checkout lại), `git checkout -b agy/bang-du-an`.
2. Đọc runner/bang/bang.py, test_bang.py, ảnh viec/bang-giao-dien/anh/ (giữ đúng phong cách hiện có: tối giản kiểu Apple, sáng/tối, 390px không tràn ngang). Đọc file mẫu dữ liệu hang-doi/du-an/yen-lam.json ở nhánh hang-doi.
3. Tab "Dự án" (đặt ĐẦU, mặc định): mỗi file hang-doi/du-an/*.json là một dự án. Trên cùng: tên, còn bao lâu tới hạn, 1 câu "đang ở bước X, việc tiếp theo Y". Dưới: dòng thời gian các bước. Mỗi bước một chấm trạng thái: chờ / đang chạy (phút/trần + dòng nhịp cuối) / xong đạt / xong KHÔNG đạt (đọc dòng `dat:` hoặc chữ "KHÔNG" ở mục tiêu chí của KET-QUA) / chờ Claude (có `cong` mà xong/<cong> chưa có) / chờ Linh (`nguoi`). Bấm một bước: hiện các phiếu, 30 dòng cuối log/nhịp, KET-QUA, và ảnh thu nhỏ.
4. Ảnh và log: route mới `/tep?p=<đường dẫn>` chỉ phục vụ file .png .jpg .webp .webm .mp4 .txt .log .json nằm DƯỚI `goc_anh` của dự án (resolve rồi kiểm tiền tố, chặn `..`, symlink, ổ khác), tối đa 20 MB, chỉ GET. Ảnh trong phiếu: quét `<goc_anh>\<id phiếu>\bang-chung\**` lấy tối đa 6 ảnh mới nhất, ưu tiên `ghep-*.png`.
5. Tab "Chất lượng": mỗi dự án một khối. (a) Bảng mức 9: đọc file do-muc-9.json mới nhất theo mẫu `chat_luong.do_muc_9` (nếu chưa có thì ghi "chưa đo"), hiện 7 chỉ số: tên | ngưỡng | số đo tệ nhất | đạt/đỏ. (b) Lưới ảnh ghép khung|bản dựng (`chat_luong.anh_ghep`), mỗi ảnh ghi tên phiếu + giờ. (c) Bảng chấm: `chat_luong.cham` (mảng {rc, nguoi, diem, ghi_chu, tep}) — Claude ghi vào, bảng chỉ đọc. Không có dữ liệu thì để trống gọn, không bịa số.
6. Test mới trong runner/bang/test_bang.py (thư mục tạm, dữ liệu giả): tab Dự án đủ 6 trạng thái; /tep chặn `..`, chặn ngoài gốc, chặn đuôi lạ, phục vụ đúng ảnh trong gốc; tab Chất lượng hiện "chưa đo" khi thiếu file. Chạy `python -m pytest runner -q` và `python -m pytest tests/nghiem-thu -q`, log thô vào theo_doi.
7. Chụp 4 ảnh (390×844 và 1440×900, sáng/tối) tab Dự án + 2 ảnh tab Chất lượng bằng dữ liệu giả, lưu viec/bang-giao-dien/anh/du-an-*.png, commit. Push `agy/bang-du-an`. KHÔNG push vào claude/project-thread-jowxv1.
CẤM: in khoá/mật khẩu, mở cổng ra ngoài, sửa phiếu khác, sửa nhánh hang-doi. Trạng thái cao nhất REVIEW.
Trả lời KET-QUA.md (ngắn): dòng đầu `dat: co`/`dat: khong`; SHA; số test pass/fail; đường dẫn 6 ảnh.
