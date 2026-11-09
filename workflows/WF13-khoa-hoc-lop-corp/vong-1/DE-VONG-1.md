# WF13 vòng 1 · ~~Lớp AI cho chi nhánh ngân hàng~~ → Một bài agentic working cho CBCNV Vinhomes (Linh đổi 9/11 10:55 VN)

Đề mới: chọn 1 bài về agentic working trong giáo trình Vinhomes đã có, làm lại theo chuẩn Course OS. Khuôn 7 dòng dưới vẫn dùng, điền từ giáo trình cũ.

Claude điều phối, agy làm thợ (máy cty DESKTOP-PVHR2CD). Mục đích: tìm lỗi quy trình Course OS bản 2, ghi BAI-HOC.md, sửa skill.

## Đề (khuôn, Linh điền 7 dòng là chạy)
| Trường | Giá trị |
|---|---|
| Ngân hàng, chi nhánh | ? |
| Người học (vai, số người, tuổi, đã dùng AI chưa) | ? |
| Thời lượng, hình thức | ? (giả định: 1 ngày 7 giờ, trực tiếp, 30 người) |
| Ngày dạy | ? |
| Đầu bài HR nói (nguyên văn) | ? |
| Công cụ được phép trong ngân hàng (ChatGPT, Copilot, Gemini, cấm gì) | ? |
| Tài liệu khách gửi, cờ bảo mật | ? (mặc định: không đưa vào kho chung khi chưa ẩn danh) |

## Đầu ra (bộ đủ)
1. Đề cương 1 trang + bảng mục tiêu ↔ hoạt động ↔ đánh giá (Bloom).
2. Slide (vòng lặp LAB099, vls.py, phông đủ 134 chữ Việt, chuẩn BTMH + mẫu top tier).
3. Workbook bài tập theo việc thật chi nhánh, phiếu quiz trước/sau 10 câu, rubric.
4. Prompt pack mang về (J4: sáng thứ Hai làm được 1 việc).
5. Bản giảng viên: kịch bản theo phút, cột "học viên hay trả lời", bảng "tình huống → xử lý", D-7/D-3/D-1, dự phòng không mạng.
6. Bản theo khách: bài gắn nhãn xương sống / tự chọn.
7. Danh sách việc nên làm agent thay vì dạy (cửa Agent Force).

## Các bước
| # | Bước | Ai | Máy |
|---|---|---|---|
| 1 | Nạp đề → module 01, 02 (+ việc thật tần suất × hệ trọng, cổng có nên đào tạo) | agy | máy cty |
| 2 | Module 03 khung: 2–3 hướng | agy | máy cty |
| **D2** | Linh chọn hướng (che tên nhánh) | Linh | điện thoại |
| 3 | Module 04, 05, 07, 08 sinh bộ | agy | máy cty |
| 4 | Máy đo: tự động (vls.py, kiểm Bloom) → red team mắt sạch ≥ 80 → 1 trợ giảng đọc bản giảng viên, ghi câu phải hỏi | Claude máy cty, trợ giảng | máy cty |
| **D4** | Linh duyệt cuối | Linh | |
| 5 | Ghi BAI-HOC.md, NHAT-KY.tsv, sửa skill | Claude cloud | |

## Máy đo vòng 1
Giờ Linh ≤ 4; slide qua vls.py; red team ≥ 80; trợ giảng hỏi Linh 0 câu; (sau lớp) điểm học viên ≥ 4,5/5.
