may: may-3
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: D:\linhx\nhat-ky\yl12-email-bao-mat-sua-1; D:\linhx\ifagent-wt\yl12-email-vao

Phiếu `yl12-email-bao-mat-sua-1`: tiếp nối yl12-email-vao (đã push ff2ddd29, mục 1–4 xong, phiếu dừng vì quá giờ). Sửa các lỗ hổng email/phiên trước production. ĐỌC `viec/yen-lam-v09/DE-BAI-SUA-NHANH.md` và `viec/yen-lam-v09/EMAIL-BO-SUNG.md` (mục 2–6).
Làm trên worktree `D:\linhx\ifagent-wt\yl12-email-vao` nhánh `agy/yl12-email-vao`. Chạy `git pull` từ origin trước. Nếu worktree mất thì tạo lại từ origin/agy/yl12-email-vao. Bỏ qua mục nào đã có trong commit của nhánh.
Mỗi mục cần test mới chứng minh:
- gỡ header phía client vẫn bị chặn;
- email chưa xác minh không chiếm hay gộp được hồ sơ khác;
- không có đồng ý ngầm;
- lịch sử chat đọc từ server.
Mỗi mục xong thì COMMIT + PUSH ngay. Phút 30 dừng việc mới và push. Chống chuyển nền như DE-BAI-SUA-NHANH. Chụp 390×844 màn nhập email có ô đồng ý.
Push `agy/yl12-email-vao`. KHÔNG deploy. KET-QUA theo DE-BAI-SUA-NHANH.
