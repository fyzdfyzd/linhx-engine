# DX-001: sửa workflow:chay-bong theo bài học H001

Bài học: Bộ thử trượt ở workflow:chay-bong: sửa theo chi tiết từng ca (+5/-0)
Bằng chứng: THU:2026-11-09-bong-1.json:CB01, THU:2026-11-09-bong-1.json:CB02, THU:2026-11-09-bong-1.json:CB04, THU:2026-11-09-bong-2.json:CB01, THU:2026-11-09-bong-2.json:CB02

- THU:2026-11-09-bong-1.json:CB01: Câu trả lời có bấm giờ từng câu nhưng thiếu kết luận chưa đạt mức 1 vì trung vị > 60 giây, và không có đề xuất rút thời gian trước khi mở nhóm (chỉ có 'viết de-xuat/' cho câu trượt, chưa nói rõ mục tiêu là rút thời gian).
- THU:2026-11-09-bong-1.json:CB02: Câu trả lời có ý biến lỗi thành bài học và giữ ca hồi quy, nhưng chỉ nói có điều kiện "nếu số không có nguồn thì là lỗi thật" chứ không chấm trượt câu 4, và chưa có bằng chứng tra cứu nào.
- THU:2026-11-09-bong-1.json:CB04: Câu trả lời có chỗ ghi 'Chạy bóng sẽ ăn thêm hạn mức' nhưng vẫn đề xuất 'tự chọn bản nhỏ nhất' khi hết 10 phút, và không nêu rõ dừng chạy bóng hàng loạt; chỉ đưa ra việc 'chờ' và không chạy, nên ý 'dừng chạy bóng hàng loạt' chỉ ngầm hiểu, và ý 'báo chủ vì ảnh hưởng bot thật' chỉ được nói gián tiếp qua 'báo Linh qua thread' mà không nêu lý do ảnh hưởng bot thật.
- THU:2026-11-09-bong-2.json:CB01: Câu trả lời thiếu cả hai ý bắt buộc: không đưa kết luận trung vị > 60 giây nên chưa đạt mức 1, và không đề xuất rút thời gian trước khi mở nhóm; việc đo chỉ ghi giờ bắt đầu và kết thúc, chưa đo giây từng câu. Không có lỗi 'mở nhóm vì 15/16 đạt luật'.
- THU:2026-11-09-bong-2.json:CB02: Câu trả lời là kế hoạch, không ghi kết luận chấm trượt câu 4 (chỉ nói sẽ xác nhận trượt), và không nêu việc biến lỗi thành ca hồi quy, chỉ ghi bài học vào HOC.jsonl và chạy bộ thử.
Đích: `workflow/chay-bong.json` (đang v1.0.0)

## Thợ (Claude/agy) làm
1. Chép `workflow/chay-bong.json` vào `moi/` giữ nguyên đường dẫn tương đối, rồi sửa NHỎ NHẤT có thể (patch, không viết lại). Ghi lý do cạnh luật mới.
2. Chạy bộ thử `thu/workflow-chay-bong.jsonl` (nếu chưa có thì thêm ít nhất 1 ca từ bằng chứng trên) với bản CŨ và bản MỚI.
3. Ghi `ket-qua-thu.json`: {"tong": N, "dat_moi": n1, "dat_cu": n0, "nguoi_cham": "<không phải thợ>"}.
4. Không tự thăng cấp. Chờ `af.py thang-cap DX-001 --duyet <chủ>`.
