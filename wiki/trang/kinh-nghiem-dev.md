---
tieu_de: Kinh nghiệm dev với AI
loai: loi
trang_thai: dang-chay
cap_nhat: 2026-11-20
nguon: [nguon/2026-11-20-BAI-PURACAM.md]
---
# Kinh nghiệm dev với AI

**Một câu:** luật làm sản phẩm khi Claude ra đề, chấm, kiểm còn agy làm việc nặng. Rút từ bài Puracam (app quét 3D, có khách trả tiền sau ~1 tháng lên store). Phần chia việc, phiếu 4 mục, soát chéo đã có ở skill `hang-doi-may`; trang này chỉ thêm cái chưa có.

## 1. Không tin "xong rồi"
- Báo xong phải kèm ít nhất một bằng chứng: **test** (đỏ trước, xanh sau), **A/B** (cùng đầu vào thật, so trước/sau), **mắt người** (ảnh màn hình Claude xem, hoặc Linh thử máy thật).
- Có hình, giao diện, âm thanh, chữ cho khách đọc: bắt buộc mắt người. Test xanh chưa đủ.
- "Sửa xong" mà A/B tệ hơn bản cũ thì trượt, hoàn phiếu. AI hay sửa một chỗ làm hỏng chỗ khác.

## 2. Tiêu chí kiểm được trước khi giao
- Mỗi feature có câu "đạt khi …" đo được: số, lệnh chạy, ảnh mẫu. Không viết được thì chưa giao, chia nhỏ tiếp.
- Đây là nội dung mục "Test bằng chứng" của phiếu, không phải văn xuôi.

## 3. Hiểu domain trước khi ra đề
- Lĩnh vực mới: Claude viết 5–10 dòng "chỗ khó" (ca biên, lỗi hay gặp) trước khi viết features. Puracam liệt kê: trôi vị trí, kính và gương làm thủng, nối ảnh lệch màu.
- Mỗi chỗ khó thành ít nhất một test hoặc một ca A/B.
- Không viết nổi danh sách chỗ khó: đọc code repo cùng loại trước, đừng để AI dắt đi.

## 4. Bộ test chỉ lớn lên
- Mỗi lỗi bắt được (bởi Linh, khách, soát chéo) thêm một test khoá nó lại. Bộ nghiệm thu chỉ thêm, không bớt.
- Giữ bộ dữ liệu thật nhỏ (ảnh, file, đơn mẫu) làm đầu vào A/B cố định.

## 5. Ra sớm, đo từ ngày đầu
- Sản phẩm có người dùng thật lên khi chạy được luồng chính, không đợi đẹp.
- Gắn đo ngay bản đầu: vào trang, từng bước phễu, nút hành động chính, bỏ ở bước nào. Chưa có đo thì chưa tính là "đã ra".
- Đặt sớm cổng "khách trả tiền đầu tiên". Có một người trả là có câu trả lời "có giá trị thật không".

## 6. Dữ liệu quyết việc tiếp
- Đợt features mới mở đầu bằng 3 số: bước rơi nhiều nhất, tính năng ít dùng nhất, chỗ dùng lâu mà không ra hành động (Puracam: xem mô hình lâu nhưng không bấm chia sẻ).
- Tính năng gần như không ai dùng sau 2 tuần thì bỏ khỏi lộ trình, không đánh bóng tiếp.

## 7. Đề khó hơn sức model
- Mỗi lĩnh vực giữ một "bài thử khó" cố định. Có model mới thì chạy lại, ghi kết quả. Không dựa demo hay benchmark.
- Trước khi kết luận "AI chưa làm được", thử bằng model mới nhất đang có.

## Liên quan
[[he-du-an-tu-chay]], [[loi-engine]], skill `skills/le/hang-doi-may` (ngưỡng 20 dòng, phiếu 4 mục, soát chéo).
