---
name: anh-sang-slide
description: Chế độ "ảnh trọn slide" của linhx-deck - viết prompt từng slide theo ảnh tham chiếu, tạo ảnh slide hoàn chỉnh (có chữ, sơ đồ) trên ChatGPT Plus, rồi chuyển bộ ảnh thành PPTX và Claude slide chỉnh được, có bước duyệt chữ tiếng Việt trước khi xuất. Dùng khi Linh muốn slide nhìn như ảnh GPT, đổi ảnh slide sang PPTX, convert ảnh thành slide sửa được.
---

# Ảnh slide → PPTX / Claude slide chỉnh được (bản nháp, KHÔNG dùng)

> 14/10/2026: Linh chốt giữ cách cũ của linhx-deck (ảnh nền không chữ, Claude dựng chữ). Skill này không gắn vào plugin, chỉ giữ làm tham khảo.

Script: `python "${CLAUDE_PLUGIN_ROOT}/scripts/anh2slide.py"` (cần `pip install rapidocr-onnxruntime opencv-python-headless python-pptx pillow`; lệnh `xem` cần thêm LibreOffice và pdftoppm).

Chế độ này thay bước 11–13 của quy trình deck khi chọn **B: ảnh trọn slide**. Chế độ A (mặc định của linhx-deck) vẫn là: GPT chỉ vẽ ảnh nền không chữ, Claude dựng chữ bằng Design System.

## Khi nào chọn chế độ B
- Slide nặng hình: sơ đồ quy trình, infographic, trang bìa, trang chương, poster.
- Cần nhìn "đẹp như GPT" nhanh, chấp nhận icon và khung nằm trong ảnh nền (không sửa được từng icon).
- Không dùng cho: slide số liệu cần sửa biểu đồ, bảng giá, slide có logo khách (GPT vẽ sai logo).

## Bước B1. Prompt từng slide → `11-goi-anh/PROMPT-SLIDE.md`
1. Từ `10-deck.json` (ghost deck đã duyệt), mỗi slide một prompt: khổ 16:9, bố cục (lấy từ thư viện 7 bố cục bước 8b), **toàn bộ chữ tiếng Việt chép nguyên văn trong ngoặc kép**, màu brand (hex), font gợi ý, phong cách ảnh neo.
2. Mỗi slide đính kèm ảnh neo + 1–2 ảnh moodboard (luật ref của skill `hinh-anh` giữ nguyên).
3. Ghi thêm `kich-ban.txt`: mỗi dòng một câu chữ của deck, đúng dấu. Đây là "đáp án" để tự sửa dấu ở B3.
4. Câu mở đầu chat: "Tạo lần lượt N ảnh slide 16:9, giữ nhất quán phong cách với ảnh neo. Chữ tiếng Việt phải viết đúng từng dấu như trong ngoặc kép, không thêm chữ khác."

## Bước B2. Tạo ảnh trên ChatGPT Plus → `11-goi-anh/slide-NN.png`
Như bước 11 của skill `hinh-anh` (Claude in Chrome qua phiên trên máy Linh; Linh làm tay là dự phòng). Mỗi slide một lượt, tải về, `deck.py nhan-anh --ten slide-NN.png --ref ...`. Ảnh chữ sai dấu không cần tạo lại: B3 sửa chữ. Chỉ tạo lại khi sai bố cục hoặc thiếu khối chữ.

## Bước B3. Đọc ảnh và duyệt chữ → `13-anh-sang-slide/duyet.json`
1. `anh2slide.py doc 11-goi-anh/slide-*.png --ra 13-anh-sang-slide --kich-ban 11-goi-anh/kich-ban.txt`
   OCR tìm vị trí dòng chữ, gom khối, đo cỡ và màu; khớp với kịch bản để tự điền dấu (thử: 27/29 khối tự khớp).
2. Claude mở từng `ban-duyet-NN.png` (ảnh gốc có khung đánh số) và `duyet.json`:
   - Khối `tu_khop: false`: sửa `chu` đúng dấu theo ảnh.
   - Khối `tu_khop: true`: kiểm chỗ ngắt dòng khớp ảnh.
   - Đặt `dam: true` cho chữ đậm, `can: "giua"` cho chữ căn giữa; gộp khối bị tách (sửa `hop`, đặt `bo: true` cho khối thừa); tách khối hai cỡ chữ; đặt `bo: true` cho chữ nằm trong hình minh hoạ hoặc logo.
3. Đưa Linh xem bảng chữ đã duyệt (luật 10 phút áp dụng). Xong đặt `"da_duyet": true`. `xuat` từ chối khi chưa duyệt.

## Bước B4. Xuất → `deck.pptx` + `claude-slide/`
1. `anh2slide.py xuat 13-anh-sang-slide/duyet.json`: xoá chữ khỏi ảnh (nền phẳng tô màu viền, nền hoạ tiết inpaint), đặt hộp chữ thật lên trên. Ra `deck.pptx` (13.33×7.5 in) và `claude-slide/slide-NN.html` 1920×1080 cho Claude deck.
2. `anh2slide.py xem 13-anh-sang-slide/duyet.json`: dựng PPTX thành ảnh, ghép cạnh ảnh gốc `so-sanh-NN.png`. Claude mở từng ảnh, sửa `co_pt`, `hop` cho khối lệch, xuất lại.
3. Font mặc định Inter (trường `font` trong duyet.json; đổi sang font brand nếu máy trình chiếu có cài).

## Giới hạn đã biết
- Icon, khung, mũi tên nằm trong ảnh nền: đổi màu hay di chuyển phải sửa ảnh. Bản sau (PA3) dựng shape thật.
- Nền phức tạp sau chữ to có thể còn vệt mờ; khi đó thêm LaMa (IOPaint) hoặc nhờ ChatGPT xoá chữ khỏi ảnh đó.
- Ô tô màu đặc có thể lấn viền khung khi khối chữ sát viền: kiểm ở `so-sanh`.
