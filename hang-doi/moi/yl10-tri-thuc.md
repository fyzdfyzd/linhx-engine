may: may-3
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: D:\linhx\nhat-ky\yl10-tri-thuc; D:\linhx\ifagent-wt\yl10-tri-thuc

Phiếu Yên Lam sửa nhanh `yl10-tri-thuc`. ĐỌC TRƯỚC: `viec/yen-lam-v09/DE-BAI-SUA-NHANH.md` và `viec/yen-lam-v09/DE-BAI.md` (git pull hàng đợi trước).
Chạy mọi lệnh ở tiền cảnh. Tạo `D:\linhx\nhat-ky\yl10-tri-thuc\`, ghi 1 dòng vào `tien-do.log` sau mỗi bước.
0. `git -C D:\linhx\ifagent fetch --all` (chưa có clone thì clone https://github.com/fyzdfyzd/ifagent vào D:\linhx\ifagent). `git -C D:\linhx\ifagent worktree add D:\linhx\ifagent-wt\yl10-tri-thuc -b agy/yl10-tri-thuc origin/agy/yl09-gop`. Cài phụ thuộc apps/lab (dùng lại node_modules sẵn có nếu được).
Nạp tri thức mới từ tài liệu Lark của BTC cho cả kiosk Lam và đồng hành.
1. Mở https://lebrothers.sg.larksuite.com/docx/YpPOdpE8JoQe3PxINjmlcBdXgLd bằng Browsentic (trình duyệt đã đăng nhập). Không mở được hoặc cần đăng nhập Lark thì dừng, ghi CAN-LINH: cần quyền xem tài liệu, KET_LUAN CHUA_DANG_NHAP.
2. Lấy toàn văn (giữ tiêu đề, bảng, danh sách), lưu `apps/lab/demos/yen-lam/tri-thuc/nguon/lark-btc-18-11.md` (UTF-8, không BOM). Không lấy ảnh có mặt người.
3. Tìm chỗ tri thức đang nạp cho Lam (grep `tri-thuc`, `/yen-lam/csmo/api/tri-thuc-cuc-bo`, prompt Lam, FAQ cache) và cho đồng hành. Gộp nội dung mới vào cùng một nguồn dùng chung cho cả kiosk và đồng hành (đồng hành hiện chưa có thì nối vào).
4. NÉN VỪA PHẢI: bản nạp vào prompt ≤ 12.000 ký tự (giữ giờ, phòng, track, diễn giả, địa điểm, vé, check-in, nhà tài trợ; bỏ văn chào hỏi, lặp lại). Bản đầy đủ để tra cứu khi cần (công cụ tìm), không nhồi hết vào prompt. Không bịa thông tin ngoài tài liệu và agenda.json.
5. Test: tệp test mới kiểm (a) tri thức nạp ≤ 12.000 ký tự, (b) 5 câu hỏi mẫu lấy từ tài liệu có câu trả lời chứa đúng dữ kiện (dùng mock Gemini, kiểm ngữ cảnh gửi đi chứa dữ kiện), (c) đồng hành và kiosk cùng đọc một nguồn.
Cuối: commit + push `agy/yl10-tri-thuc`. CẤM như DE-BAI-SUA-NHANH. Trạng thái cao nhất REVIEW. KET-QUA theo DE-BAI-SUA-NHANH.
