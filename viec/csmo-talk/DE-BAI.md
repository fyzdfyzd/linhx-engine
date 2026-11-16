# Đề: bài nói CSMO Topic 07 của Linh (nói 19/11 14:45)
Nội dung chốt: viec/csmo-talk/KICH-BAN-v5.md (chữ trên slide và tool lấy NGUYÊN VĂN từ đó, không tự viết thêm).
Thẻ phong cách: viec/csmo-talk/mau/GHI-CHU.md (phiếu csmo-mau-slide).
Luật chung: không nêu tên URAH, Sakedemy, TUVA, IF Agent, BTMH hay thương hiệu nào của Linh. Không sinh ảnh/slide bằng AI. Không gọi AI thật, không deploy. Tiếng Việt có dấu đầy đủ, kiểm 134 chữ có dấu hiển thị đúng.

## Phiếu csmo-tool: trang "Soi thương hiệu trong 10 phút"
Mục 3 của kịch bản. Một file viec/csmo-talk/tool/index.html tự chứa (CSS, JS inline), không máy chủ, không thư viện ngoài trừ phông Google Fonts.
- Bước 1 form: tên, ngành, khách mục tiêu, đối thủ, 3 sự thật. Lưu localStorage (bọc try/catch).
- Bước 2: 3 câu hỏi ghép sẵn đúng nguyên văn kịch bản, nút Chép, nút mở chatgpt.com và gemini.google.com.
- Bước 3: ô tích kết quả theo 4 chỉ số (2 AI × 3 lần cho Có mặt; mỗi sự thật đúng/sai/không nhắc; được khuyên có/không; 2 AI giống/khác).
- Bước 4: điểm từng chỉ số 0–100, câu "đang rơi ở bước X" theo bảng ở mục 2 phút 9:00 của kịch bản, 3 việc tuần này, kế hoạch 30 ngày, nút tải mẫu "Bảng sự thật 1 trang" (.md tạo trong trình duyệt).
- Đầu trang 2 câu đo cảm nhận (thang 1–5 và "một việc bạn sẽ làm trước thứ Hai"); lưu localStorage, có hàm guiKetQua() để trống chờ nối máy chủ sau.
- Điện thoại 360px là chính: chữ ≥ 16px, nút ≥ 44px, không cuộn ngang. Phong cách theo thẻ phong cách nếu đã có, không thì tối giản trắng ngà + 1 màu nhấn.
- Kiểm: test Playwright tests/tool.spec (điền form → thấy điểm và "bước X"; 360 không cuộn ngang). Ảnh PNG 360 và 1280 từng bước vào viec/csmo-talk/bang-chung/.

## Phiếu csmo-deck: deck 19 slide
- 1920×1080, PPTX dựng bằng code (python-pptx hoặc pptxgenjs) từ viec/csmo-talk/deck/slides.json (agy tự viết json từ bảng slide của kịch bản: mỗi slide 1 ý, ≤ 12 chữ tiêu đề, ≤ 25 chữ thân; số liệu kèm dòng nguồn nhỏ ở chân slide theo mục 5).
- Slide 2: câu hỏi 60 giây + đồng hồ đếm ngược (chữ to). Slide 5: công thức. Slide 13: bảng claim → bằng chứng, ghi "ví dụ minh hoạ". Slide 16: QR giả chỗ (ô vuông ghi "QR"), chiếm ≥ 45% chiều cao. Slide 19: câu chốt.
- Phông nhúng hoặc phông có sẵn trên máy chiếu: dùng phông trong thẻ phong cách, dự phòng Arial. Ghi chú diễn giả (notes) = lời nói tương ứng trong kịch bản.
- Render PNG từng slide (LibreOffice) + 1 tờ lưới tổng TONG.png; kiểm không tràn chữ, không lỗi dấu. Commit vào viec/csmo-talk/deck/.
