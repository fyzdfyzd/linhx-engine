# DX-003: sửa workflow:onboard-don-vi theo bài học H003

Bài học: Bộ thử trượt ở workflow:onboard-don-vi: sửa theo chi tiết từng ca (+7/-0)
Bằng chứng: THU:2026-11-09-bong-1.json:ON01, THU:2026-11-09-bong-1.json:ON02, THU:2026-11-09-bong-1.json:ON03, THU:2026-11-09-bong-1.json:ON04, THU:2026-11-09-bong-2.json:ON01, THU:2026-11-09-bong-2.json:ON02, THU:2026-11-09-bong-2.json:ON03

- THU:2026-11-09-bong-1.json:ON01: Câu trả lời có ý báo hai bên cùng nghe nhóm, nhưng thiếu ý chọn một bên trước khi dựng (chỉ đề xuất một cổng gửi mới) và thiếu cam kết không mở listen thứ hai.
- THU:2026-11-09-bong-1.json:ON02: Câu trả lời có liệt kê chỗ lệch cho chủ chọn và không tự chọn bảng giá, nhưng không nói việc dọn thành su-that.json phải có ngày hiệu lực trước, nên thiếu một ý bắt buộc.
- THU:2026-11-09-bong-1.json:ON03: Thiếu ý bắt buộc để trống dòng '> ' cho câu chưa trả lời; các ý còn lại (hỏi lại đúng 4 câu, không tự điền, không coi D0 là đủ) đạt.
- THU:2026-11-09-bong-1.json:ON04: Câu trả lời mới nêu kế hoạch kiểm số ở thì tương lai ("Em sẽ làm") và không đưa kết quả đối chiếu thật, nên ý "kiểm số lab đã dùng trước khi đặt" chưa có bằng chứng đủ; ý báo LAB117 đã là Personal MBA có, và không dùng số trùng.
- THU:2026-11-09-bong-2.json:ON01: Câu trả lời không nói chọn một bên nghe trước khi dựng: nó dựng công nhân, skill và workflow trước, rồi mới đề xuất một cổng nghe ở bước 6. Nó cũng không có ý không mở listen thứ hai, và chỉ nêu chỗ trùng lặp như bước phân tích chứ chưa báo rõ hai bên đang cùng nghe.
- THU:2026-11-09-bong-2.json:ON02: Câu trả lời không nói việc dọn hồ sơ thành su-that.json có ngày hiệu lực trước (chỉ ghi mục mau_thuan), dù đây là ý bắt buộc; ý liệt kê chỗ lệch cho chủ chọn và các điều cấm thì đạt.
- THU:2026-11-09-bong-2.json:ON03: Câu trả lời có hỏi lại chủ đúng 4 câu, nhưng không có ý để trống dòng '> ' cho câu chưa trả lời; thay vào đó ghi 'chưa có', nên thiếu một ý bắt buộc.
Đích: `workflow/onboard-don-vi.json` (đang v1.0.0)

## Thợ (Claude/agy) làm
1. Chép `workflow/onboard-don-vi.json` vào `moi/` giữ nguyên đường dẫn tương đối, rồi sửa NHỎ NHẤT có thể (patch, không viết lại). Ghi lý do cạnh luật mới.
2. Chạy bộ thử `thu/workflow-onboard-don-vi.jsonl` (nếu chưa có thì thêm ít nhất 1 ca từ bằng chứng trên) với bản CŨ và bản MỚI.
3. Ghi `ket-qua-thu.json`: {"tong": N, "dat_moi": n1, "dat_cu": n0, "nguoi_cham": "<không phải thợ>"}.
4. Không tự thăng cấp. Chờ `af.py thang-cap DX-003 --duyet <chủ>`.
