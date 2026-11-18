may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\nhat-ky\yl10-cam-an; C:\linhx\ifagent-wt\yl10-cam-an
nhan: may-2 2026-11-18T07:28:22+0700

Phiếu Yên Lam sửa nhanh `yl10-cam-an`. ĐỌC TRƯỚC: `viec/yen-lam-v09/DE-BAI-SUA-NHANH.md` và `viec/yen-lam-v09/DE-BAI.md` (git pull hàng đợi trước).
Chạy mọi lệnh ở tiền cảnh. Tạo `C:\linhx\nhat-ky\yl10-cam-an\`, ghi 1 dòng vào `tien-do.log` sau mỗi bước.
0. `git -C C:\linhx\ifagent fetch --all` (chưa có clone thì clone https://github.com/fyzdfyzd/ifagent vào C:\linhx\ifagent). `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\yl10-cam-an -b agy/yl10-cam-an origin/agy/yl09-gop`. Cài phụ thuộc apps/lab (dùng lại node_modules sẵn có nếu được).
Kiosk: Lam THẤY người đối diện qua camera, khung hình ẨN.
1. Khi có người tới (đã có phát hiện người), bật camera, KHÔNG hiện khung hình lên màn. Hiện một biểu tượng camera nhỏ ở góc + dòng "Lam đang nhìn" (bắt buộc, để khách biết camera đang bật).
2. Gửi khung hình thưa (≤ 1 hình/2s, cỡ nhỏ ≤ 512px) vào phiên Gemini Live đang dùng (luồng video/ảnh) để Lam nhận ra người đối diện: số người, áo màu gì, đeo kính… và chào/khen tự nhiên. Không lưu ảnh xuống đĩa/DB, không nhận dạng danh tính ở bước này (nhận mặt khách đã đồng ý là luồng K2 riêng, giữ nguyên).
3. BIỂU CẢM: kiểm xem đã có tracking biểu cảm chưa (grep YuNet, face, expression, bieu-cam). Chưa có thì thêm nhẹ trên máy khách (MediaPipe Face Landmarker hoặc thư viện sẵn có trong repo) ra 4 trạng thái vui/bình thường/bối rối/không nhìn, chỉ dùng để Lam điều chỉnh giọng, không gửi lên server, không lưu. Có rồi thì nối vào Lam.
4. Có công tắc bật/tắt cả hai ở cấu hình kiosk (mặc định bật trên staging).
Test: unit cho bộ lấy mẫu khung hình (tần suất, kích thước, không ghi đĩa), cho công tắc. Ảnh K1 có biểu tượng camera.
Cuối: commit + push `agy/yl10-cam-an`. CẤM như DE-BAI-SUA-NHANH. Trạng thái cao nhất REVIEW. KET-QUA theo DE-BAI-SUA-NHANH.
