# Luật viết V01–V11 và luật dàn trang D01–D17

Script report.py kiểm phần lớn các luật này; ngưỡng lấy từ số đo 24 báo cáo mẫu.


Mỗi luật có mã, mô tả, ngưỡng và cách kiểm. Ngưỡng lấy từ số đo ở mục 1. "Lỗi" chặn xuất bản, "Cảnh báo" chỉ báo cáo.

### 5.1 Luật viết

| Mã | Luật | Ngưỡng | Cách kiểm | Mức |
|---|---|---|---|---|
| V01 | Mỗi tiêu đề mục (H2) là câu kết luận | Có ít nhất một động từ hoặc từ so sánh; 8 đến 30 tiếng (âm tiết) tiếng Việt; không phải chỉ danh từ | Danh sách động từ, trợ từ ("tăng", "giảm", "đạt", "dẫn đầu", "vẫn", "đang", "sẽ", "cao hơn", "gấp"); đếm tiếng bằng khoảng trắng | Lỗi |
| V02 | Tiêu đề hình là câu có dấu chấm | Kết thúc bằng "."; 8 đến 30 tiếng; chứa số hoặc từ so sánh ở ít nhất 60% hình | Regex trên trường `title` của hình | Lỗi |
| V03 | Tóm tắt điều hành có 3 đến 7 phát hiện | Mỗi phát hiện: câu đầu ≤ 25 tiếng; có ít nhất một con số; tổng ≤ 80 tiếng | Đếm mục, regex số | Lỗi |
| V04 | Mỗi con số có mốc so sánh hoặc mẫu số | Trong 2 câu quanh con số phải có "so với", "từ ... lên", "gấp", "điểm phần trăm", "trung bình", "n =" | Cửa sổ câu quanh regex số | Cảnh báo |
| V05 | Quy kết số liệu khảo sát về người trả lời | Câu chứa % từ khảo sát phải có chủ ngữ là nhóm được hỏi hoặc động từ "cho biết", "cho rằng", "dự kiến" | Từ khóa | Cảnh báo |
| V06 | Định dạng số tiếng Việt | Phân cách nghìn bằng dấu chấm, thập phân bằng dấu phẩy, "%" liền số, đơn vị "tỷ USD", "nghìn tỷ đồng" | Regex `\d,\d{3}` trong văn bản tiếng Việt là lỗi | Lỗi |
| V07 | Khuyến nghị mở bằng động từ | Mỗi mục trong T20 bắt đầu bằng động từ mệnh lệnh | Danh sách động từ đầu câu | Cảnh báo |
| V08 | Câu thân bài không quá dài | Trung vị ≤ 28 tiếng, không câu nào > 55 tiếng | Tách câu | Cảnh báo |
| V09 | Không dùng gạch ngang dài | Không có ký tự gạch ngang dài U+2014 hoặc U+2013 trong văn bản | Tìm ký tự | Lỗi |
| V10 | Có trang phương pháp khi dùng dữ liệu khảo sát | Nếu bất kỳ nguồn nào có "khảo sát" hoặc "n =" thì phải có T21 với thời gian thực địa, n, phạm vi | Kiểm cấu trúc | Lỗi |
| V11 | Thuật ngữ nhất quán | Mỗi khái niệm phân khúc (vd. "doanh nghiệp dẫn đầu") được định nghĩa một lần và dùng một tên | Từ điển thuật ngữ của báo cáo | Cảnh báo |

### 5.2 Luật dàn trang

| Mã | Luật | Ngưỡng | Cách kiểm | Mức |
|---|---|---|---|---|
| D01 | Mỗi hình có số thứ tự liên tục | "Hình 1", "Hình 2"... không trùng, không nhảy; hình tiếp trang ghi "(tiếp)" | Đọc PDF xuất, regex `^Hình \d+` | Lỗi |
| D02 | Mỗi hình có dòng "Nguồn:" ngay dưới | 100% hình; nguồn khảo sát có tên, tháng năm, n | Khối chữ "Nguồn:" nằm trong 60 pt dưới khung hình | Lỗi |
| D03 | Mỗi hình có dòng đối tượng và đơn vị | Dòng thứ hai sau tiêu đề chứa "%", "tỷ", "đơn vị" hoặc "chỉ số" | Regex | Lỗi |
| D04 | Thân bài nằm trong dải cỡ chuẩn | Khổ dọc: thân 9,5 đến 11 pt; khổ 16:9 (960x540): 11 đến 14 pt; chú thích ≥ 6,5 pt | Mode cỡ chữ của PDF xuất | Lỗi |
| D05 | Giãn dòng thân | 1,3 đến 1,5 lần cỡ chữ (tiếng Việt có dấu cần tối thiểu 1,3) | Đo khoảng cách đường cơ sở | Lỗi |
| D06 | Trần chữ mỗi trang | Trung vị toàn báo cáo 1.500 đến 3.000 ký tự quy A4; không trang nào > 4.300 trừ T23 | Đếm ký tự mỗi trang | Lỗi khi vượt trần |
| D07 | Tỷ lệ phủ vùng chữ | Trung vị 0,20 đến 0,40; trang T12 và T14 ≤ 0,25 | Tổng diện tích khối chữ / diện tích trang | Cảnh báo |
| D08 | Tỷ lệ trang có hình | 40 đến 80% trang nội dung có hình, bảng hoặc số lớn; không quá 3 trang chữ thuần liên tiếp | Phát hiện ảnh hoặc vector | Cảnh báo |
| D09 | Lề tối thiểu | Lề ngoài ≥ 5% chiều rộng, lề trên và dưới ≥ 4% chiều cao; kiểu lề treo T10 có lề trái 15 đến 23% | bbox khối chữ | Lỗi |
| D10 | Số họ font | ≤ 2 họ font (một serif tiêu đề, một sans thân, hoặc ngược lại); ≤ 4 kiểu (weight) | Danh sách font nhúng | Lỗi |
| D11 | Font phủ đủ tiếng Việt | Mọi glyph có dấu hiển thị bằng font chính, không rơi về font dự phòng | So danh sách font nhúng với font khai báo; tìm ký tự .notdef | Lỗi |
| D12 | Bảng màu | 1 màu thương hiệu chính, 1 màu nhấn, thang 3 đến 5 sắc độ cho biểu đồ, xám; tổng màu không xám ≤ 6 | Lượng tử hóa màu chữ và vector | Cảnh báo |
| D13 | Chân trang nhất quán | Mọi trang nội dung có tên báo cáo và số trang ở cùng vị trí; trang bìa, mở chương được miễn | Khối lặp lại ở 7% dưới | Lỗi |
| D14 | Không mồ côi tiêu đề | Tiêu đề mục không nằm ở 15% cuối trang; không dòng đơn lẻ đầu hoặc cuối cột | bbox | Lỗi |
| D15 | Cấu trúc tối thiểu | Có T01, T04 (nếu > 12 trang), T06 hoặc T07, ít nhất một T09 nếu > 20 trang, T21 khi có khảo sát, T22 | Nhận diện kiểu trang qua thẻ trong mã nguồn | Lỗi |
| D16 | Nhãn số liệu trên biểu đồ | Biểu đồ cột và thanh có nhãn giá trị trực tiếp; không viền khung; lưới trục mảnh ≤ 0,5 pt | Kiểm cấu hình biểu đồ trước khi render | Cảnh báo |
| D17 | Số lớn có chú giải | Mọi chữ số ≥ 28 pt phải có câu giải thích và nguồn trong cùng khối | Ghép khối theo khoảng cách | Lỗi |

