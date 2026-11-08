# Bộ tài liệu high standard: học gì từ từng bộ

Đây là thước chấm của Linh. Gốc nằm ở `D:\@WF\PROJECT\DTTL_Personal_Brand\data_raw\HIGHSTANDARD` và `D:\@WF\DATA\BU\IFAGENT\01_STRATEGY\HIGHSTANDARD_PMF` (máy Linh). Tài liệu gốc là của khách và công ty tư vấn, có đóng dấu mật, nên skill chỉ giữ **cấu trúc và cách làm**, không chép số liệu.

Mẹo đọc bản text: các file `_extracted*.txt`, `_vml.txt` bị lỗi mã. Sửa từng dòng bằng `line.encode("cp437", errors="ignore").decode("utf-8", errors="ignore")`.

## 1. Từng bộ

| Bộ | Của ai | Loại | Học gì |
|---|---|---|---|
| OMC Customer Segmentation 12/2021 (37 trang) | One Mount | Phân khúc khách hàng cho hệ sinh thái | Trang đầu là **mục tiêu năm có số** (người dùng, doanh thu, EBITDA). Dân số **tách lớp**: cả nước → 30 thành phố → 10 thành phố → Hà Nội + TP.HCM, cắt theo giới, thành thị/nông thôn, thế hệ. Chọn mục tiêu theo địa bàn × độ tuổi rồi mới vẽ chân dung |
| TCB–MH Customer & Offering (15 trang) | Techcombank × Masterise | Chân dung + định vị giá trị | Phân khúc theo tài sản (HNW, AFF, MAF) rồi tới **chân dung điển hình** theo nghề và vai (chủ DN lớn, lãnh đạo cấp trung, chính trị gia…). Mỗi chân dung có **"Mục tiêu: 'Tôi muốn …'"** bằng lời khách, quan điểm tài chính, quan điểm cuộc sống, cỡ giao dịch. Nối sản phẩm cụ thể vào từng chân dung |
| VML × CLI × MS · IMC Plan 2025 Inspire (85 trang, bản 4) | VML cho Techcombank | Kế hoạch truyền thông tích hợp | Mục lục 4 khối: định hướng chiến lược → ý tưởng sáng tạo → triển khai mạng xã hội → media. Mở bằng **thách thức → định hướng nhiệm vụ** (3 nhiệm vụ có tên). Tầm nhìn, sứ mệnh, định vị, **nhu cầu chưa được đáp ứng của thế hệ mục tiêu** trước ý tưởng. **Khung thông điệp nhiều tầng**, GTM, rồi nhìn lại năm trước + ngân sách + KPI. Ghi số phiên bản |
| Cốt lõi chiến lược định vị BTMH (90 trang) | C+P Consulting · dentsu Redder · Line Collective | Định vị thương hiệu cấp cao | Cỡ thị trường **2024 → 2030** tách tích trữ / trang sức; **mỗi slide có dòng nguồn** (BCTC PNJ, SJC, DOJI…); cơ hội phân chia lại cuộc chơi; số người tiêu dùng có khả năng chi theo tầng |
| EY-Parthenon · Chiến lược sản phẩm BTMH (69 trang, Draft V3) | EY-Parthenon | Chiến lược sản phẩm theo định vị | Làm theo **vòng workshop** (Round 3), trang 2 là thành phần dự và lịch họp, có trang **"điểm lại nội dung đã thảo luận"**. Chủ đề sản phẩm gắn với định vị (đẳng cấp, hiện đại, thách thức). Mỗi trang ghi "Source: EY-Parthenon analysis" |
| BTMH Chiến lược 2025–2030 (80 trang) | BTMH | Chiến lược công ty | Khung mục tiêu 5 năm, đặt sản phẩm vào chiến lược công ty |
| Nghiên cứu khách hàng (32 trang) | | Nghiên cứu định tính/định lượng | Cách trình bày kết quả nghiên cứu khách |
| 1MG RE Final Deliverable · Summary Strategy | | Bản giao cuối | Cách tóm một chiến lược dài thành bản giao |
| HIGHSTANDARD_PMF (IFAGENT) | LINHX tự làm theo chuẩn trên | PMF: phân khúc, GTM, kiểm tài chính, slide | Mẫu nội bộ đã đạt, dùng làm ví dụ đầu ra |

## 2. Mười hai tiêu chí rút ra (đã đưa vào `../cham.md`)

1. Tóm tắt điều hành ở đầu. 2. Mục tiêu có số trang đầu (OMC). 3. Mỗi số có nguồn và cỡ mẫu (C+P, EY ghi nguồn từng trang). 4. Thị trường tách lớp, có mốc hiện tại và dự báo (OMC, C+P). 5. Phân khúc trên ma trận 2 trục rồi mới chọn (OMC). 6. Chân dung theo khung cố định, kèm lời khách (TCB–MH). 7. Insight và nhu cầu chưa đáp ứng trước giải pháp (VML). 8. Thông điệp theo tầng (VML). 9. Đối thủ có tên, có số (C+P). 10. Giải pháp nói rõ vì sao khớp định vị (EY). 11. Ghi phiên bản, ngày, điểm lại đợt trước (EY, VML). 12. Cổng Go/No-Go.

## 3. Chỗ các bộ này yếu, LINHX phải hơn

- Không có người chịu trách nhiệm và kiểm thử ở khâu giao (Deliver). LINHX bù bằng tình huống thành test và duyệt như khán giả.
- Không có ngưỡng kiểm giả thuyết. LINHX bù bằng cổng Go/No-Go có số.
- Không có bảng chứng thực truy ngược. LINHX bù bằng `bang-chung/` và bảng chứng thực.
