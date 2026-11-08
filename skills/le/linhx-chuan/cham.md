# Thang chấm chung (high standard)

Rút từ bộ tư vấn trong `D:\@WF\PROJECT\DTTL_Personal_Brand\data_raw\HIGHSTANDARD` (EY, VML, OMC, C+P/dentsu, TCB) và `D:\@WF\DATA\BU\IFAGENT\01_STRATEGY\HIGHSTANDARD_PMF`, cộng hai luật LINHX. Mỗi tiêu chí chấm 1–5. Đạt khi trung vị mọi tiêu chí ≥4 và 2/3 phiếu đạt. Điểm 3 là "sạch nhưng làm vội", chưa đạt.

| # | Tiêu chí | 5 điểm trông thế nào |
|---|---|---|
| 1 | Tóm tắt điều hành ở đầu | Đọc 1 trang là biết kết luận và việc cần quyết |
| 2 | Mục tiêu có số | Số, đơn vị, mốc thời gian ngay trang đầu |
| 3 | Số có nguồn | Mỗi số có `[BC-xxx]`, cỡ mẫu, năm; 5 số mở ngẫu nhiên khớp 5/5 |
| 4 | Thị trường tách lớp | Có mốc hiện tại và dự báo, TAM/SAM/SOM nếu cần |
| 5 | Phân khúc trên ma trận 2 trục | Chọn phân khúc sau khi đặt lên ma trận, có lý do |
| 6 | Chân dung khách theo khung cố định | Có trích lời thật, có job (Khi… tôi muốn… để…) |
| 7 | Insight trước giải pháp | Nhu cầu chưa đáp ứng nêu rõ trước khi đề xuất |
| 8 | Thông điệp theo tầng | Ý lớn, trụ cột, bằng chứng |
| 9 | Đối thủ có tên, có số | Bảng so sánh ít nhất 4 đối thủ thật |
| 10 | Giải pháp khớp định vị | Nói rõ vì sao đúng chỗ trống, không chỉ "hay" |
| 11 | Phiên bản và điểm lại | Có số bản, ngày, khác gì bản trước |
| 12 | Cổng Go/No-Go | Thời điểm, chỉ số, việc làm khi trượt |
| 13 | **Khán giả xem trọn** | Đi hết hành trình người xem trên đúng thiết bị, không chỗ nào vấp |
| 14 | **Tối giản** | Không có khối, chữ, hình nào bỏ đi mà bài vẫn đủ ý |
| 15 | **Không kém bản vàng** | Đặt cạnh bản vàng gần nhất cùng khổ, không trống, phẳng, mỏng hơn ở chỗ nào |
| 16 | **Không phạm 5 kiểu hỏng** | Không quá nhiều, không như khung sườn, không đóng hộp, không phẳng, không nhạt |

Phiếu chấm ghi JSON: `{"nguoi_cham": "...", "diem": {"1": 4, ...}, "loi": [{"muc": "...", "muc_do": "chan|nang|nhe", "sua": "..."}], "dat": true}`.
