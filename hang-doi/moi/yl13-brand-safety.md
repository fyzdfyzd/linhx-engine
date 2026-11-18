may: may-3
loai: code
tran_phut: 40
khong_tien_phut: 25
theo_doi: D:\linhx\nhat-ky\yl13-brand-safety; D:\linhx\ifagent-wt\yl13-brand-safety

Phiếu `yl13-brand-safety`: đưa bộ Brand Safety Linh gửi (đã chỉnh cho sự kiện) vào Yên Lam. ĐỌC TRƯỚC `viec/yen-lam-v09/BRAND-SAFETY-CSMO.md` (đặc tả, làm ĐÚNG mục A–E, đặc biệt các mục KHÔNG THÊM) và `viec/yen-lam-v09/DE-BAI-SUA-NHANH.md`.
0. `git -C D:\linhx\ifagent fetch --all`; `git -C D:\linhx\ifagent worktree add D:\linhx\ifagent-wt\yl13-brand-safety -b agy/yl13-brand-safety origin/agy/yl10-gop`. Nối node_modules như phiếu yl10.
Chạy mọi lệnh ở tiền cảnh. Mỗi mục xong thì COMMIT + PUSH ngay. Phút 30 dừng việc mới, push, ghi CON_LAI.
VIỆC: chỉ sửa trong `apps/lab/server/v1/brand-safety/` (tu-dien-goc.json, loc-ai.js PROMPT_CHU/PROMPT_ANH, loc-anh.js, tu-dien.js nếu cần thêm whitelist) và chỗ gọi lọc ảnh bìa (luật mặt người chỉ cho bìa). Không đổi API, không đổi admin.
Test 1 tệp mới `yl13-brand-safety.test.js` (mock Gemini, KHÔNG gọi mạng):
- CHẶN lớp 1: "địt mẹ", "dit con me", "cờ ba sọc", "bác hồ", "vay nặng lãi", "pháp luân công".
- KHÔNG CHẶN: "Tôi từ TP Hồ Chí Minh ra dự", "Phiên đánh giá chiến dịch tấn công thị trường mấy giờ?", "PNJ làm loyalty thế nào?", "cc email cho mình slide", "Chi phí vé bao nhiêu tiền?", "Hồ Tây 1 ở đâu?".
- NGHI (gọi AI mock): "biểu tình", "quốc kỳ", "tự tử". Riêng chat Lam với "tự tử": trả câu ân cần có gợi ý hỗ trợ, không trả thông điệp "chưa phù hợp".
- Ảnh (mock nhãn AI): slide nhiều chữ → qua; QR backdrop → qua; ảnh chụp Zalo → chặn; bìa không mặt người → chặn với lý do rõ; Bảng tin ảnh sân khấu không người → qua.
Chạy thêm các test brand-safety cũ có sẵn, TỪNG TỆP; đỏ do thay đổi thì sửa code, test khoá nghiem-thu-* không được sửa.
THÊM: làm đúng mục F (luật 3 mức: sạch tự duyệt, nghi vào hàng Duyệt admin, vi phạm loại thẳng; lỗi AI = nghi). Test thêm 3 ca: ảnh sạch hiện ngay trên Bảng tin; ảnh nghi vào hàng duyệt; ảnh vi phạm bị loại và không có trong hàng.
Cuối: push `agy/yl13-brand-safety`. KHÔNG deploy. KET-QUA theo DE-BAI-SUA-NHANH, kèm số từ đã thêm mỗi nhóm.
