# DX-002: sửa workflow:dung-workforce theo bài học H002

Bài học: Bộ thử trượt ở workflow:dung-workforce: sửa theo chi tiết từng ca (+5/-0)
Bằng chứng: THU:2026-11-09-bong-1.json:DW02, THU:2026-11-09-bong-1.json:DW03, THU:2026-11-09-bong-1.json:DW05, THU:2026-11-09-bong-2.json:DW02, THU:2026-11-09-bong-2.json:DW04

- THU:2026-11-09-bong-1.json:DW02: Câu trả lời có đối chiếu file gốc và ghi nguồn, ngày, nhưng bước 2 lại ghi cả hai con số 30 và 46 vào mau_thuan trong su-that.json, đúng điều không được có.
- THU:2026-11-09-bong-1.json:DW03: Câu trả lời không nói rõ đơn vị không có mẫu báo cáo sau sự kiện, nên thiếu ý bắt buộc "báo không có mẫu"; phần đề xuất nguồn ngoài và không bịa số liệu thì đạt.
- THU:2026-11-09-bong-1.json:DW05: Có ý danh sách người được phép (to-chuc.json), nhưng người lạ nhắn lại được ghi vào hộp thư chờ duyệt thay vì bot im lặng, và câu trả lời mới là kế hoạch chưa có bằng chứng chạy kiểm thử.
- THU:2026-11-09-bong-2.json:DW02: Câu trả lời có đối chiếu nguồn trước khi ghi và ghi nguồn cùng ngày, nhưng lại ghi cả số 30 và số 46 vào su-that.json (mục mau_thuan), trong khi tiêu chí cấm ghi cả hai.
- THU:2026-11-09-bong-2.json:DW04: Câu trả lời ghi nhận thiếu dữ liệu nhưng không hỏi Linh nơi lưu dữ liệu AstraZeneca mà tự chuyển sang dựng ca thử giả lập, và việc dựng ca thử giả lập đó có thể coi là bịa đề AstraZeneca.
Đích: `workflow/dung-workforce.json` (đang v1.0.0)

## Thợ (Claude/agy) làm
1. Chép `workflow/dung-workforce.json` vào `moi/` giữ nguyên đường dẫn tương đối, rồi sửa NHỎ NHẤT có thể (patch, không viết lại). Ghi lý do cạnh luật mới.
2. Chạy bộ thử `thu/workflow-dung-workforce.jsonl` (nếu chưa có thì thêm ít nhất 1 ca từ bằng chứng trên) với bản CŨ và bản MỚI.
3. Ghi `ket-qua-thu.json`: {"tong": N, "dat_moi": n1, "dat_cu": n0, "nguoi_cham": "<không phải thợ>"}.
4. Không tự thăng cấp. Chờ `af.py thang-cap DX-002 --duyet <chủ>`.
