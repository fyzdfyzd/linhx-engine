# Gửi chị Vân Anh: cách sửa bài mẫu để dạy máy biên tập giống chị

Máy sẽ học cách chị biên tập bằng cách so bản trước và bản sau khi chị sửa. Chị không cần viết quy trình hay giải thích gì, chỉ cần sửa bài như chị vẫn sửa bài cho cộng tác viên.

## Bài để sửa
Thư mục `cho-van-anh/` có ba bài, đều do máy viết, chưa qua người biên tập:

| File | Thể loại | Ghi chú |
|---|---|---|
| `01-Trach-nhiem-huu-han-ban-nhap.docx` | Góc nhìn kinh tế, ~1.500 chữ | Bản nháp đầu, trước khi qua plugin biên tập. Máy sẽ so cách chị sửa với cách plugin đã sửa |
| `02-Cong-ty-mot-nguoi-sau-con-sot.docx` | Góc nhìn kinh tế, ~1.700 chữ | |
| `03-Nha-cung-cap-tot-nhat-nam-sau.docx` | Góc nhìn kinh tế, ~1.800 chữ | |

Chuyện các nhân vật trong ba bài là chuyện dựng, đánh dấu [GIẢ LẬP]; chị cứ sửa cách viết như thể chuyện thật.
Chị sửa bao nhiêu bài cũng được. Ba bài là đủ để máy bắt đầu rút luật; năm bài thì máy có bài để tự kiểm.

## Cách sửa
1. Mở file bằng Word, bật **Review → Track Changes** trước khi sửa.
2. Sửa như bình thường: cắt, nối câu, đổi chữ, đảo đoạn, viết lại câu. Không cần sạch, không cần chấp nhận thay đổi.
3. Chỗ nào chị muốn nói lý do thì thêm **Comment**, ngắn thôi ("câu dịch", "nói hai lần", "ai nói?"). Không bắt buộc, nhưng mỗi comment giúp máy hiểu đúng hơn rất nhiều.
4. Nếu chị thấy cả bài hỏng ở cấu trúc thì ghi một comment ở đầu bài, rồi sửa phần câu chữ như bình thường.
5. Lưu, giữ nguyên tên file và thêm đuôi `-VA`, ví dụ `01-Trach-nhiem-huu-han-ban-nhap-VA.docx`.

Chị dùng Google Docs thì bật chế độ **Suggesting**, sửa xong tải về bằng File → Download → Microsoft Word; các đề xuất vẫn giữ dạng Track Changes.
Chị muốn đưa bài cũ chị đã sửa cho cộng tác viên thật thì càng tốt: gửi file có Track Changes, hoặc hai file bản trước và bản sau.

## Sau khi chị gửi
Anh Linh đặt file vào thư mục `mau-sua/` (mỗi bài một thư mục, tên dạng `van-anh-<ngay>-<ten-bai>/`) và chạy skill `hoc-tu-ban-sua`. Máy sẽ:
- tách từng chỗ chị sửa (cắt, nối câu, thay chữ...) và comment của chị;
- gom những chỗ sửa giống nhau thành luật, mỗi luật phải có ít nhất hai lần chị sửa như vậy;
- ghi luật vào `ho-so-bien-tap/van-anh/LUAT.md`, kèm câu trước và sau làm bằng chứng;
- thử biên tập một bài chị đã sửa mà máy chưa thấy, rồi so với bản của chị để biết máy bắt được bao nhiêu phần chỗ chị sửa.

Chị đọc lại `LUAT.md` nếu muốn: luật nào máy rút sai, chị gạch đi là máy bỏ.
