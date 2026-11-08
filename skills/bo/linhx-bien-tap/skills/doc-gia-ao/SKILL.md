---
name: doc-gia-ao
description: Lượt biên tập 5, hai hoặc ba độc giả Việt cụ thể đọc mù bài như người đọc thật và chỉ ra chỗ bỏ đọc, chỗ không hiểu, chỗ muốn cãi, chỗ nghe như Tây dịch, điều mang về. Dùng trong bien-tap-bai hoặc khi muốn thử bài trên người đọc.
---

# Độc giả ảo (lượt 5)

## Chọn độc giả
- Lấy 2–3 độc giả từ bảng độc giả của bài (người viết đã lập ở bước đề). Thiếu thì dựng theo kênh: mỗi người có tuổi, nghề, nơi sống, lúc nào đọc bài, đọc trên gì, nỗi sợ ẩn, một câu họ hay cãi.
- Nếu cần độc giả đa dạng hơn, lấy persona từ LAB048 (Nemotron-Personas-Vietnam), nhưng lọc đúng tầng độc giả của kênh: bộ persona dân số chung không hợp với độc giả báo kinh tế.

## Cách làm
Mỗi độc giả một subagent mới, chỉ được mở đúng file bài (bỏ qua mã [N..], [GIẢ LẬP]). Đề cho từng người, viết bằng giọng của họ, ngắn:
1. Chỗ suýt bỏ đọc (trích câu) và vì sao.
2. Chỗ không hiểu hoặc phải đọc lại (trích câu).
3. Chỗ muốn cãi (trích câu và câu sẽ cãi); với độc giả trong nghề: chỗ "đúng là mình" và chỗ bài nói quá.
4. Câu nghe "như Tây dịch sang" hoặc "như sách giáo khoa".
5. Đọc xong mang về được gì, trong một câu; mai có làm gì khác không.
6. Câu nhớ nhất.

## Đọc kết quả
- Mục 5 khác luận điểm của bài: lỗi nặng, báo đầu phiếu.
- Hai độc giả cùng chỉ một chỗ ở mục 1, 2, 4: đưa vào phiếu như lỗi nặng (`BO`, `KH-DG`, `TAY`).
- Mục 3 là nguồn sửa quý nhất: câu cãi chưa được trả lời là `CAI`. Lần chạy thử 19/10, câu cãi "danh bạ là của công ty" và chi tiết "tắt được nhưng không dám tắt" đều đến từ độc giả, không từ biên tập.
- Mục 6 cho biết câu nào không được đụng khi sửa.

## Trả về
`bt-5-doc-gia-<ten>.md` cho từng người, và năm dòng tổng hợp trong phiếu biên tập.
