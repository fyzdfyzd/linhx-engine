---
name: viet-bai-giong-viet
description: Viết bài tiếng Việt cùng Linh theo luồng của biên tập viên Vân Anh - máy tìm ý và dữ liệu, Linh viết nháp gạch đầu dòng, máy chỉ làm mượt từng ý của Linh rồi gửi biên tập. Dùng khi Linh đưa một đến ba ý gốc cho một bài.
---

# Viết bài cùng Linh (v0.3, luồng Vân Anh)

Từ 19/10/2026 máy **không viết bài từ đầu**. Chị Vân Anh đọc bản PA1 chạy tự động và kết luận "chỉ dùng được ý, không dùng được một sự diễn đạt nào"; bài chạy tự động càng nhiều càng nát, sửa không cứu được. Bài tốt khi nháp của tác giả đã đủ ý, máy chỉ làm mượt. Luồng dưới đây theo đúng cách chị làm.

## Các bước
1. **Tìm ý** từ 1–3 ý gốc Linh đưa. Máy đề xuất góc nhìn, câu hỏi độc giả sẽ hỏi, chỗ ý gốc còn yếu, dưới dạng gạch đầu dòng ngắn. Không viết văn xuôi. Ý quá nhiều thì bài rời rạc: chốt tối đa 3 ý chính, ghi `01-y.md`.
2. **Tìm dữ liệu bổ trợ** cho đúng 3 ý ấy. Mỗi dữ liệu ghi nguồn, ngày, và nó đỡ ý nào. Dữ liệu không đỡ ý nào thì bỏ (luật VA-04: không thả số liệu lung tung). Chủ thể phải gọi được tên: bộ nào, ai, hội thảo nào (VA-06). Ghi `02-du-lieu.md`.
3. **Dừng, chờ Linh viết nháp gạch đầu dòng.** Chỉ cần gạch đầu dòng, đủ ý và hàm ý (Linh 19/10: không đòi số chữ). Linh viết bằng ý và chuyện của mình; máy không viết nháp thay, không bịa chuyện bạn bè. Kiểm: `python scripts/kiem_nhap.py nhap 03-nhap.md`; mục nào mỏng (dưới hai gạch) thì hỏi Linh đúng mục ấy, một câu, rồi làm tiếp với những gì có.
3b. **Kiểm ý** (Linh 19/10: ý nào cũng có thể sai với thực tế). Theo tinh thần bước "11 câu hỏi sâu" trong LinhX Write.
   - Mỗi gạch của Linh viết lại thành một khẳng định, rồi thành 1–3 câu hỏi kiểm được: ai, bao nhiêu, ở đâu, và "nếu ý này sai thì sẽ thấy gì".
   - Subagent riêng (không phải người làm mượt) tìm câu trả lời, ưu tiên số liệu Việt Nam và người làm thật, ghi nguồn và ngày.
   - Mỗi ý một nhãn: **đúng** / **sai** / **đúng một phần** (ghi cách nói hẹp lại) / **chưa ai biết**.
   - Ghi `03b-kiem-y.md`, bảng `| Gạch | Khẳng định | Câu hỏi | Tìm được (nguồn) | Nhãn | Đề xuất |`, gửi Linh duyệt: giữ, sửa, bỏ.
   - Ý "chưa ai biết" giữ được nhưng vào bài dưới dạng câu hỏi hoặc ghi rõ là ý kiến của tác giả, không viết thành khẳng định. Ý "sai" không vào bài nếu Linh chưa lật lại.
   - Chỉ làm mượt những ý Linh đã duyệt.
4. **Làm mượt.** Đi theo thứ tự nháp, mỗi gạch thành câu hoặc đoạn văn xuôi, giữ nguyên ý, chuyện, chữ đắt của Linh. Được nối câu, thêm chữ chuyển ý, sắp lại trong một đoạn. Không được thêm chuyện, số, ẩn dụ, tên người ngoài nháp và `02-du-lieu.md`. Ghi `04-ban-muot.md`, rồi kiểm:
   - `python scripts/kiem_nhap.py bai 03-nhap.md 04-ban-muot.md --kho 02-du-lieu.md`: không rơi gạch nào, không số lạ, đoạn máy tự thêm tối đa một phần mười.
   - `python scripts/cham_cau.py 04-ban-muot.md`: giọng nằm trong dải 7 bài Linh đã đăng, câu so sánh hai vế không quá 5%.

Sau đó gửi biên tập bằng skill `bien-tap` (plugin `linhx-bien-tap`, hồ sơ `van-anh`) và sửa theo phiếu.

## Khi làm mượt, tránh tám lỗi chị Vân Anh bắt
Chi tiết và bằng chứng ở `linhx-bien-tap/ho-so-bien-tap/van-anh/LUAT.md`.
1. So sánh hai vế ("X thì…, còn Y thì…", "chưa có… nhưng… thì đã").
2. "Không còn là… mà là", "càng… càng…" (bài đăng của Linh không có lần nào; "không chỉ… mà còn" thì Linh vẫn dùng).
3. Láy lại cụm của câu trước để nối câu sau.
4. Thả số liệu không gánh luận điểm, nhắc lại số ở đoạn xa.
5. Ẩn dụ kéo xuyên đoạn; chồng danh từ, định nghĩa cho cùng một người.
6. Chủ thể mơ hồ.
7. Chuyện nghe không thật (lỗi chặn). Chuyện chỉ lấy từ nháp của Linh.
8. Câu cụt mang ý lớn mà không triển khai.

Thêm: thuật ngữ (OPC...) giải nghĩa ở lần đầu; tiêu đề không theo khuôn "X không biến mất, nó…"; kết không có hậu gọn gàng.

## Giọng
Đọc toàn văn 2 bài trong `references/bai-mau/` trước khi làm mượt (chỉ bài Linh đã đăng báo). Giữ câu dài nối chảy như bài mẫu, không chặt câu cụt.

## Không làm
Viết nháp thay Linh; bịa số, trích dẫn, người thật; chạy cả bài tự động từ đề đến bản cuối.
