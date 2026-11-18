may: may-2
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: C:\linhx\nhat-ky\yl11-chat-noi-dung; C:\linhx\ifagent-wt\yl11-chat-noi-dung
nhan: may-2 2026-11-18T12:53:22+0700

Phiếu Yên Lam `yl11-chat-noi-dung`: sửa tab chat Yên Lam (điện thoại) sau đánh giá UX Linh duyệt 12:50 18/11. ĐỌC TRƯỚC `viec/yen-lam-v09/DE-BAI-SUA-NHANH.md` (luật chung, chống chuyển nền, cấm) và XEM ẢNH `viec/yen-lam-v09/anh/chat-linh-18-11.png` (màn Linh chụp trên staging 84ba9304).
Chạy mọi lệnh tiền cảnh. Ghi tiến độ `C:\linhx\nhat-ky\yl11-chat-noi-dung\tien-do.log`. Mỗi mục xong COMMIT + PUSH ngay. Phút 30 dừng việc mới, chụp ảnh, push, ghi CON_LAI.
0. `git -C C:\linhx\ifagent fetch --all`; `git -C C:\linhx\ifagent worktree add C:\linhx\ifagent-wt\yl11-chat-noi-dung -b agy/yl11-chat-noi-dung origin/agy/yl10-gop` (đỉnh 3b7dd30f). Nối node_modules như phiếu yl10.
VIỆC (nội dung trả lời, server/prompt/tri thức, KHÔNG đụng CSS):
1. Hỏi "Khai mạc lúc mấy giờ?" Lam trả giờ tea break/nghỉ trưa/networking, hỏi lại trả y hệt. Tìm gốc: truy xuất tri thức/agenda (lọc theo từ khoá?), FAQ cache (cache câu sai?), prompt. Sửa để trả đúng giờ khai mạc từ agenda.json (phiên khai mạc mỗi ngày, có phòng). Câu sai đã cache thì xoá khỏi cache và chặn cache câu trả lời không chứa dữ kiện được hỏi.
2. Câu đầu "Chủ đề 06 xác định những năng lực…" lạc đề: tìm nguồn (lời chào/tin đầu, mẩu tri thức bị chèn), bỏ. Tin đầu chỉ là lời chào chuẩn PROMPT-CHUAN.
3. Chip gợi ý: không lặp câu khách đã hỏi trong phiên; sinh 3 chip mới theo ngữ cảnh (phiên kế tiếp, diễn giả liên quan, chỗ ăn/nghỉ), lấy từ dữ liệu BTC.
4. Hỏi lại cùng câu: không trả nguyên văn câu cũ; nếu đã trả lời thì trả ngắn + thêm chi tiết.
Test mới (mock Gemini): 10 câu hỏi giờ/địa điểm mẫu (khai mạc ngày 19 và 20, bế mạc, nghỉ trưa, phòng Hồ Tây 1…) → ngữ cảnh gửi đi có đúng dòng agenda; chip không trùng câu đã hỏi; tin đầu không chứa "Chủ đề".
Cuối: push `agy/yl11-chat-noi-dung`. KHÔNG deploy. KET-QUA theo DE-BAI-SUA-NHANH (dat, SHA, test, ảnh ghép trước/sau + điểm).

nhip: 13:02 9p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
