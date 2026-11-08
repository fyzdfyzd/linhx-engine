---
name: mm-chon
description: Chọn 0–3 mental model (thẻ Naval, Munger, Farnam Street hoặc thẻ riêng của Linh) cho một tình huống hay câu hỏi cụ thể rồi chạy câu hỏi kích hoạt của từng thẻ. Dùng khi Linh gõ /mm-chon, hỏi "nên nghĩ việc này thế nào", "dùng mental model nào", hoặc đang cân nhắc một lựa chọn.
---

# Chọn mental model cho tình huống

Lệnh: `node "${CLAUDE_PLUGIN_ROOT}/scripts/tu-duy.js" <lệnh>`

1. Chạy `index` để xem bảng thẻ (mã, tên, nhóm, câu kích hoạt, số lần Linh đã dùng). Không nạp hết nội dung thẻ.
2. Gọi tên loại vấn đề trong một dòng: quyết định, chẩn đoán lỗi, hiểu một hiện tượng, chọn hướng dài hạn, giao việc, hay đọc số liệu.
3. Chọn **0 đến 3 thẻ** theo các luật sau:
   - Các thẻ phải thuộc nhóm khác nhau (lưới đa ngành, M1).
   - Nếu là quyết định, phải có ít nhất 1 thẻ kiểu đảo ngược (B5, M8 hoặc C6).
   - Khi chọn ngang nhau, ưu tiên thẻ Linh đã có ví dụ, rồi tới thẻ lâu chưa dùng.
   - Nếu không thẻ nào thật sự khớp, nói thẳng là "không cần thẻ" và trả lời bình thường. Không gượng ép.
4. Với mỗi thẻ đã chọn, chạy `show <mã>` để đọc phần "Khi KHÔNG dùng"/"Bẫy" và ví dụ cũ của Linh. Sau đó áp **câu hỏi kích hoạt** vào đúng tình huống của Linh, mỗi thẻ 2–4 dòng, dùng số liệu và tên thật.
5. Viết thêm một mục **"Phản biện"**: thẻ nào kéo theo hướng ngược với các thẻ còn lại, và điều gì sẽ làm kết luận đổi.
6. Kết bằng thẻ kết quả gồm 4 dòng:
   - Nên làm
   - Độ chắc ~X%
   - Đổi ý nếu…
   - Bước tiếp theo
7. Nếu quyết định khó đảo ngược hoặc tốn hơn 1 ngày công, đề nghị ghi nhật ký bằng `/mm-quyet`. Nếu Linh thấy ví dụ này đáng nhớ, ghi bằng `vi-du <mã> "<tình huống → cách dùng → kết quả>"`.

Không đóng vai Naval hay Munger. Không bịa câu trích: chỉ trích câu đã có trong thẻ, và giữ nhãn `[V]`/`[R]`.
