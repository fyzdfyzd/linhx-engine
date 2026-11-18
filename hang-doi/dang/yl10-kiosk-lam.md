may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\nhat-ky\yl10-kiosk-lam; C:\linhx\ifagent-wt\yl10-kiosk-lam
nhan: may-2 2026-11-18T07:28:26+0700

Phiếu Yên Lam sửa nhanh `yl10-kiosk-lam`. ĐỌC TRƯỚC: `viec/yen-lam-v09/DE-BAI-SUA-NHANH.md` và `viec/yen-lam-v09/DE-BAI.md` (git pull hàng đợi trước).
Chạy mọi lệnh ở tiền cảnh. Tạo `C:\linhx\nhat-ky\yl10-kiosk-lam\`, ghi 1 dòng vào `tien-do.log` sau mỗi bước.
0. `git -C C:\linhx\ifagent fetch --all` (chưa có clone thì clone https://github.com/fyzdfyzd/ifagent vào C:\linhx\ifagent). `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\yl10-kiosk-lam -b agy/yl10-kiosk-lam origin/agy/yl09-gop`. Cài phụ thuộc apps/lab (dùng lại node_modules sẵn có nếu được).
Kiosk Lam (`/yen-lam/csmo/kiosk-lam`, 1080×1920) sửa nhanh:
1. Lam TO RA: nhân vật chiếm phần lớn màn, giao diện bớt rối (ẩn bớt chữ, gom 5 nút tròn thành ít nút hơn hoặc thu nhỏ; widget tối đa 2 cùng lúc, nhỏ gọn). Không đổi CSS kính.
2. Nói CẢ ĐOẠN: hiện tại tách và phát theo từng câu (nghe ngắt quãng). Đổi thành gom cả lượt trả lời rồi nói liền một mạch (hoặc gom theo đoạn ≥ 2–3 câu), chữ hiện theo đoạn. Giữ độ trễ bắt đầu nói ≤ 1,5s so với hiện tại (đo và ghi).
3. NÚT REFRESH: nút nhỏ ở góc (≥ 44px) tải lại trang khi lag; giữ trạng thái kiosk (mã máy) sau khi tải lại.
4. WIDGET THEO LỜI NÓI: khi Lam nhắc tới phiên, diễn giả, giờ, địa điểm thì hiện widget tương ứng (thẻ phiên, thẻ diễn giả, bản đồ/phòng) lấy từ dữ liệu BTC (agenda.json, dien-gia.json), qua công cụ/hàm trả dữ liệu, không để model bịa. Tối đa 2 widget, tự ẩn sau 20s.
5. Sửa "SẮP DIỄN RA · 09:00" bị xuống dòng.
Test: unit cho gom đoạn nói, cho bộ chọn widget theo câu trả lời (5 câu mẫu → đúng widget). Ảnh trước/sau K1 và K1 đang nói có widget.
Cuối: commit + push `agy/yl10-kiosk-lam`. CẤM như DE-BAI-SUA-NHANH. Trạng thái cao nhất REVIEW. KET-QUA theo DE-BAI-SUA-NHANH.

nhip: 07:31 3p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
