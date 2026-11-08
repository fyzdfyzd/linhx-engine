---
name: lesson-script
description: Dùng khi cần viết kịch bản lời giảng chi tiết và bố cục slide Slidev cho từng bài học theo cấu trúc Gagné rút gọn, bảo đảm độ dài mỗi đoạn và tổng số âm tiết khớp chuẩn đọc tiếng Việt.
---
# Viết kịch bản lời giảng và slide (`lesson-script`)

Skill này chuyển hoá mục tiêu học tập và đề cương của từng bài thành file trình chiếu Slidev (`slides.md`) chứa đồng thời nội dung hiển thị trên màn hình và lời giảng chi tiết trong phần chú thích (`<!-- ... -->`), kèm danh mục thuật ngữ tiếng Anh cần đọc chuẩn (`pronunciation.yaml`).

## 1. File đầu vào
- `work/course/00-brief.yaml` và `work/course/02-outline.yaml`.
- `work/course/01-objectives/<L>.yaml`: danh sách mục tiêu cần đạt của bài học `<L>`.
- `work/course/03-assessment/quiz-<L>.yaml` và `exercise-<L>.md`: để bảo đảm lời giảng cung cấp đủ kiến thức cho học viên trả lời được mọi câu hỏi và làm được bài tập.

## 2. File đầu ra
- `work/course/04-lessons/<L>/slides.md`: file Slidev định dạng Markdown, sử dụng font `Be Vietnam Pro`, kích thước canvas `1920`, tỉ lệ `16/9`. Lời giảng đặt trong khối注释 HTML `<!-- ... -->` ở cuối mỗi slide, chia đoạn theo đúng dấu `[click]`.
- `work/course/04-lessons/<L>/style.css`: bảng kiểu CSS định dạng màu sắc thương hiệu, cỡ chữ lớn dễ đọc trên điện thoại và chừa trống góc dưới bên phải cho khung hình giảng viên AI.
- `work/course/04-lessons/<L>/pronunciation.yaml`: khai báo danh sách `en_terms: [...]` liệt kê các từ tiếng Anh xuất hiện trong lời giảng để bộ đọc bọc thẻ `<en>...</en>`.

## 3. Quy tắc viết lời giảng và đồng bộ `[click]`
1. **Cấu trúc Gagné rút gọn**: Mỗi bài gồm 5 phần mạch lạc: Mở đầu thu hút chú ý (Hook, 5–10%), Bối cảnh & Mục tiêu (Context, 10–15%), Nội dung cốt lõi & Ví dụ minh hoạ (Core, 60–70%), Hướng dẫn thực hành (Practice, 10–15%), và Tóm tắt (Summary, 5–10%).
2. **Độ dài chuẩn tiếng Việt**: Tổng lời giảng của mỗi bài phải đạt từ **1.000 đến 1.500 âm tiết** (tương đương 4–6 phút với tốc độ đọc 4,3 âm tiết/giây của VieNeu-TTS). Mỗi đoạn văn cách nhau bởi `[click]` hoặc sang slide mới **không được vượt quá 60 âm tiết** (dưới 15 giây) để lip-sync và phụ đề hiển thị mượt mà.
3. **Văn phong tự nhiên**: Xưng "mình", gọi người học là "bạn", câu văn ngắn gọn, trò chuyện tự nhiên, không đọc vẹt nguyên văn dòng chữ trên slide. Các ký hiệu hoặc dấu câu đặc biệt phải viết thành chữ đọc được (ví dụ viết `chấm claude gạch chéo skills` thay vì `.claude/skills`, viết `SKILL chấm MD` thay vì `SKILL.md`).
4. **Quy tắc khớp số khung click**: Trên một slide, nếu có `N` hiệu ứng xuất hiện (`v-click`, các mục trong `<v-clicks>`, hoặc bước chuyển dòng code `{all|1|2}`), thì phần chú thích `<!-- ... -->` của slide đó phải có đúng `N` dấu `[click]`, tạo thành `N + 1` đoạn lời giảng.

## 4. Lệnh engine cần chạy
Sau khi viết xong `slides.md` và đã xuất khung hình PNG (qua skill `lesson-slides`), chạy lệnh dưới đây để tách lời giảng và kiểm tra độ khớp giữa số đoạn lời với số khung hình:
```text
python src/plugin/linhx-course/engine/make_segments.py work/course/04-lessons/<L>/slides.md work/course/04-lessons/<L>/frames work/course/04-lessons/<L>/segments.json
```

## 5. Cổng duyệt
- **Cổng duyệt 2 (Duyệt lời giảng)**: Ghi danh sách các file lời giảng đã hoàn thành vào báo cáo chờ duyệt (ví dụ `agy/bao-cao/M2-cho-duyet.md`) để giảng viên/người dùng đọc soát văn phong và thuật ngữ.

## 6. Lỗi hay gặp và cách xử lý (từ thực tế vận hành)
- **Lỗi chữ viết hoa bị đánh vần từng chữ cái**: Trong VieNeu-TTS (`sea-g2p`), từ viết hoa như `SKILL` nếu không có thẻ `<en>SKILL</en>` sẽ bị đọc thành "ét ca i lờ lờ", và `MD` bị đọc thành "mờ đê". Phải đưa đầy đủ các từ tiếng Anh (cả hoa lẫn thường) vào `pronunciation.yaml`.
- **Lỗi lệch số đoạn notes và số khung PNG**: Nếu dùng `<v-clicks>` cho danh sách có 4 dòng gạch đầu dòng thì Slidev sinh ra 1 khung gốc + 4 khung click = 5 khung PNG; do đó phần `<!-- ... -->` bắt buộc phải có 1 đoạn mở đầu + 4 đoạn bắt đầu bằng `[click]`.
- **Lỗi số và ký hiệu làm tăng sai số ASR**: Tránh viết số Ả Rập (`1, 2, 3`) hoặc đường dẫn có dấu gạch chéo trong lời giảng; hãy viết bằng chữ tiếng Việt (`một, hai, ba`, `thư mục chấm claude`) để TTS phát âm chính xác và ASR đối soát khớp.
