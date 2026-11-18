may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\nhat-ky\yl10-dong-hanh; C:\linhx\ifagent-wt\yl10-dong-hanh
nhan: may-2 2026-11-18T07:28:24+0700

Phiếu Yên Lam sửa nhanh `yl10-dong-hanh`. ĐỌC TRƯỚC: `viec/yen-lam-v09/DE-BAI-SUA-NHANH.md` và `viec/yen-lam-v09/DE-BAI.md` (git pull hàng đợi trước).
Chạy mọi lệnh ở tiền cảnh. Tạo `C:\linhx\nhat-ky\yl10-dong-hanh\`, ghi 1 dòng vào `tien-do.log` sau mỗi bước.
0. `git -C C:\linhx\ifagent fetch --all` (chưa có clone thì clone https://github.com/fyzdfyzd/ifagent vào C:\linhx\ifagent). `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\yl10-dong-hanh -b agy/yl10-dong-hanh origin/agy/yl09-gop`. Cài phụ thuộc apps/lab (dùng lại node_modules sẵn có nếu được).
Đồng hành (`/yen-lam/`, 390×844) sửa nhanh:
1. Tab "Lam" đổi tên hiển thị thành "Yên Lam". Trong tab có công tắc rõ ràng Nói ↔ Chat (một chạm đổi), nhớ lựa chọn.
2. EMAIL XÁC NHẬN để tham gia trả lời (câu hỏi bình chọn, thảo luận, hỏi diễn giả): ô nhập email đưa lên TRÊN CÙNG khu vực tham gia; gửi mã/link xác nhận qua bộ gửi mail sẵn có trong repo (test dùng mock, KHÔNG gửi mail thật khi chạy phiếu); chưa xác nhận thì nút trả lời mờ + nhắc. Xác nhận xong thì nhớ trên máy.
3. TÌM KIẾM ở Lịch: tìm theo tên phiên/nội dung và tên diễn giả (bỏ dấu, không phân biệt hoa thường, khớp một phần), kết quả nhóm Phiên / Diễn giả, chạm mở trang tương ứng. Dữ liệu agenda.json + dien-gia.json.
4. Ô chat Yên Lam dùng chung nguồn tri thức với kiosk (nếu phiếu yl10-tri-thuc chưa xong thì để hàm đọc nguồn chung, ghi CON_LAI).
Test: unit cho tìm kiếm (10 truy vấn mẫu có dấu/không dấu, tên diễn giả, tên phiên), cho luồng xác nhận email (mock). Ảnh: tab Yên Lam (nói + chat), ô email, kết quả tìm kiếm.
Cuối: commit + push `agy/yl10-dong-hanh`. CẤM như DE-BAI-SUA-NHANH. Trạng thái cao nhất REVIEW. KET-QUA theo DE-BAI-SUA-NHANH.

nhip: 07:58 30p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
