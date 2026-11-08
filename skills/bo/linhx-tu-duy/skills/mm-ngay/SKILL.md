---
name: mm-ngay
description: Bốc thẻ mental model của ngày cho Linh (ưu tiên thẻ có quyết định tới hạn, rồi thẻ lâu chưa dùng), và tối ghi một câu thẻ đó xuất hiện ở đâu; cũng dùng để thêm ví dụ thật vào một thẻ. Dùng khi Linh gõ /mm-ngay, "thẻ hôm nay", "ghi ví dụ cho thẻ", hoặc khi lịch sáng chạy.
---

# Thẻ của ngày

Lệnh: `node "${CLAUDE_PLUGIN_ROOT}/scripts/tu-duy.js" <lệnh>`

**Buổi sáng:** chạy `ngay`.
- Gọi nhiều lần trong ngày vẫn ra cùng một thẻ. Thêm `--lai` để bốc thẻ khác.
- Trình bày gọn cho Linh, tối đa 8 dòng: tên thẻ, câu gốc, câu kích hoạt, một gợi ý **việc cụ thể hôm nay** có thể dùng thẻ.
- Gợi ý lấy từ dự án Linh đang làm. Đọc OVERVIEW hoặc LOG gần nhất nếu đang ở thư mục LINHX.

**Buổi tối:** chạy `ghi-ngay <mã> "<một câu>"`.
- Câu cần trả lời: hôm nay thẻ xuất hiện ở đâu, kể cả "không thấy chỗ dùng".
- Nếu Linh kể dài, rút thành một câu.

**Thêm ví dụ thật:** chạy `vi-du <mã> "<tình huống → cách dùng → kết quả>"`.
- Ví dụ của chính Linh quý hơn mọi định nghĩa, vì mental model là cái móc để gọi lại kinh nghiệm của mình.

Không biến buổi sáng thành bài giảng. Mục tiêu là luyện **nhận ra lúc dùng**, không luyện nhớ định nghĩa.
