may: may-3
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: D:\linhx\nhat-ky\yl13-brand-safety; D:\linhx\ifagent-wt\yl13-brand-safety
nhan: may-3 2026-11-18T16:12:16+0700

Phiếu `yl13-brand-safety`: hoàn thiện Brand Safety CSMO. ĐỌC TRƯỚC `viec/yen-lam-v09/BRAND-SAFETY-CSMO.md` (bộ đầy đủ, mục F thắng) và `viec/yen-lam-v09/DE-BAI-SUA-NHANH.md`.
Máy 2 ĐÃ làm phần từ điển, prompt và file luật chuẩn `apps/lab/server/v1/brand-safety/LUAT-BRAND-SAFETY-CSMO.md` (nhánh origin/agy/yl12-brand-safety, ≥ 2a969da7; file này thắng khi khác đặc tả viec/). Đọc diff nhánh đó trước, KHÔNG làm lại.
0. `git -C D:\linhx\ifagent fetch --all`; `git -C D:\linhx\ifagent worktree add D:\linhx\ifagent-wt\yl13-brand-safety -b agy/yl13-brand-safety origin/agy/yl12-brand-safety`. Nối node_modules như phiếu yl10 (cần cả jpeg-js, ws).
Chạy mọi lệnh ở tiền cảnh. Mỗi mục xong thì COMMIT + PUSH ngay. Phút 30 dừng việc mới, push, ghi CON_LAI.
VIỆC CÒN LẠI:
1. Mục F, LUẬT 3 MỨC cho nội dung công khai (ảnh Bảng tin, chữ kèm ảnh, câu hỏi diễn giả, bình luận, chữ và ảnh bìa):
   - sạch thì tự duyệt, hiện ngay;
   - nghi thì vào hàng Duyệt của admin;
   - vi phạm thì loại thẳng, không vào hàng, chỉ đếm;
   - lỗi hoặc timeout AI thì xếp là nghi.
   Ảnh trẻ em vẫn khoá như cũ.
2. Luật mặt người CHỈ cho ảnh bìa (loai anh_bia). Bảng tin không cần.
3. "tự tử", "tự sát" trong chat Lam: Lam trả câu ân cần, có gợi ý tìm người hỗ trợ, không trả thông điệp "chưa phù hợp". Ở chỗ công khai thì xếp là nghi.
4. Kiểm KHÔNG chặn: "Tôi từ TP Hồ Chí Minh ra", "Phiên đánh giá chiến dịch tấn công thị trường mấy giờ?", "PNJ làm loyalty thế nào?", "Chi phí vé bao nhiêu tiền?". Nếu bị chặn thì sửa bằng ngoại lệ (mục D).
5. Mục G: email hoặc SĐT của chính khách ở ô cổng email và trong chat riêng không bị chặn. Ở chỗ công khai vẫn chặn.
6. Kiosk Live (giọng nói, live-proxy.js): lọc cả LỜI LAM NÓI qua bản chữ phiên âm. Nếu vi phạm thì cắt lượt, ghi brand_safety_block. Không làm trễ câu sạch.
Test 1 tệp `yl13-brand-safety.test.js` (thêm 1 ca cho mục 6) (mock Gemini, không gọi mạng), phủ các mục 1–5:
- ảnh sạch hiện ngay;
- ảnh nghi vào hàng duyệt;
- ảnh vi phạm không có trong hàng;
- AI timeout thì xếp là nghi;
- bìa không mặt người bị chặn, Bảng tin ảnh sân khấu được qua.
Chạy các test brand-safety cũ TỪNG TỆP. Test khoá nghiem-thu-* không được sửa.
Cuối: push `agy/yl13-brand-safety`. KHÔNG deploy. KET-QUA theo DE-BAI-SUA-NHANH.

nhip: 16:15 3p warning: --mode auto is not available because the terminal sandbox is not available on this host; continuing in the defa
