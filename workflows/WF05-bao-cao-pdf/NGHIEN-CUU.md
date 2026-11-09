# Nghiên cứu nền WF05: Báo cáo PDF thiết kế đẹp

9/11. Đọc: 5 skill/mã ngoài đã chép vào `_refs/WF05/` (không chạy), 4 bài của đơn vị làm nghề, 2 PDF mẫu, 6 skill con của `linhx-report`. Chi tiết `NGOAI.md`.

## Kết luận
1. Skill `linhx-report` (13 bước, Typst, 17 luật dàn trang D01–D17, cổng do script kiểm) **đã vượt xa** mọi skill ngoài tìm được: các skill đó chỉ là Markdown/HTML→PDF, không có kiểm số, không chấm trang. Không nên viết lại, chỉ vá.
2. Chỗ người giỏi làm mà LINHX chưa có: **người kiểm số khác với tác giả** (Pew) và **kiểm số được vẽ trên hình**, không chỉ số trong văn.
3. Luật tiêu đề kết luận LINHX đã có (hình 8–30 tiếng, ghost report); thiếu **phép thử che dữ liệu**: chỉ đọc tiêu đề phải hiểu ý.
4. Thiếu máy đo "chấm mù": rubric 5 tiêu chí hiện do chính thợ dựng chấm (ca thử 4,08 chưa tách người).
5. Chưa có bản vàng tiếng Việt A4 dọc; bản vàng hiện tìm được là tiếng Anh (V1 Reuters DNR, V2 e-Conomy SEA). Đã gửi đề DR/DE-1.

## Quy trình đề xuất (ai làm)
1. Chọn bản vàng + ghost report (tiêu đề đọc riêng ra lập luận, Slideworks: "Write the titles first") · Claude, Linh duyệt D2.
2. Nghiên cứu, sổ bằng chứng BCxx · Claude.
3. Hình trước, chữ sau; mỗi hình qua câu hỏi "có nên là hình không?" (Urban: "Stop! Should it even be a chart?") · agy.
4. Viết chương, dựng Typst · agy.
5. **Kiểm số kiểu Pew**: script + một agent không dự phần viết, đối chiếu từng số trong văn và số vẽ trên hình với BCxx · Claude kiểm (tách khỏi agy).
6. Chấm mù từng trang (agent mới, chỉ thấy ảnh trang + bản vàng, không đọc lý do thợ) → sửa ≤3 vòng · Claude máy cty.
7. Linh duyệt D4.

## Máy đo + ngưỡng (rẻ → đắt)
| Tầng | Đo gì | Ngưỡng |
|---|---|---|
| Tự động | D01–D17 hiện có (`report.py cong 11`) | 0 lỗi, cảnh báo ≤3 |
| Tự động | Mọi hình có tiêu đề kết luận, đối tượng + đơn vị, nguồn có n (đã có D01–D03). **Thêm:** hình ≤7 hạng mục, đường ≤5, cột bắt đầu từ 0, không 3D, không trục kép (Pew, Urban) | 0 lỗi |
| Tự động | Số trong văn/hình lệch BCxx: ≤1% đạt, 1–10% duyệt, >10% lỗi (đã có) | 0 số mồ côi |
| Rubric | 5 tiêu chí/trang | TB ≥3,5, không tiêu chí <3 (đề gốc) |
| Chấm mù | Agent mới, ảnh trang cạnh bản vàng V1; mỗi trang chấm 2 lần độc lập | Hai lần lệch ≤1 điểm; lấy điểm thấp |
| Phép thử tiêu đề | Che hình, chỉ đọc tiêu đề: có hiểu thông điệp không (Umbrex) | ≥90% hình đạt |
| Người | Linh D4 | Không sửa lớn |

Ngưỡng phép thử 90% và "2 lần lệch ≤1" là **đề xuất của máy này, chưa có nguồn ngoài**; cần thử ở vòng 1.

## Bản vàng
Xem `vang/README.md`: V1 Reuters DNR 2025 (biểu đồ, khuôn chung), V2 e-Conomy SEA 2025 (mở chương, số lớn), V3 McKinsey Superagency, V4 Pew (chưa tải). Chưa mẫu nào qua Linh.

## Sửa vào skill nào, sửa gì
- `viet-bao-cao` bước 7: thêm "người kiểm số khác tác giả", kiểm số **vẽ trên hình** (so toạ độ/độ dài thanh với giá trị), theo Pew. Bằng chứng ngoài đã có; vẫn theo luật của LINHX là ≥2 bằng chứng từ vòng chạy mới sửa chắc.
- `hinh-du-lieu`: thêm luật ≤7 hạng mục, ≤5 đường, cột từ 0, nhãn trực tiếp, nhóm cùng màu mọi hình trong báo cáo; câu hỏi "có nên là bảng/số lớn không".
- `dan-trang` bước 11: tách người chấm khỏi người dựng; thêm phép thử che dữ liệu.
- `dan-trang` bước 10: kiểm cú pháp Typst bằng `typstyle` nếu có (typst-author); bàn giao **không xoá** tệp nguồn (trái với adobe whitepaper).
- Thừa/sai: không thấy gì cần bỏ. Chưa thể chứng minh phần D01–D17 đúng với báo cáo tiếng Việt thật, cần vòng 1.

## Rủi ro
- Bản vàng đều tiếng Anh; phông/ngắt dòng tiếng Việt khác. Cần mẫu A4 dọc tiếng Việt.
- Số liệu "chấm 4,08" tự thợ chấm, có thể thổi phồng.
- Kết quả tìm web chỉ đọc qua trang tóm tắt cho adobe whitepaper (chưa đọc repo gốc `adobe/skills`).
- Umbrex không phải tài liệu chính thức của McKinsey.
- Reddit/X/LinkedIn, tiếng Trung, Perplexity cookbook, tessl chưa đọc.

## Nguồn
- [đọc] elegant-reports https://github.com/jdrhyne/agent-skills/tree/main/skills/elegant-reports
- [đọc] typst-skills https://github.com/apcamargo/typst-skills
- [đọc] pdf-design https://github.com/jamditis/claude-skills-journalism/tree/main/pdf-design
- [đọc] market-report https://github.com/kmshihab7878/claude-code-setup
- [đọc tóm tắt] adobe whitepaper https://skills.browseract.com/skills/adobe-skills-whitepaper
- [đọc] Pew number check https://www.pewresearch.org/decoded/2019/10/14/how-we-check-numbers-and-facts-at-pew-research-center/
- [đọc] Pew small multiples https://www.pewresearch.org/decoded/2018/12/20/how-pew-research-center-uses-small-multiple-charts/
- [đọc] Urban Institute https://urbaninstitute.github.io/graphics-styleguide
- [đọc] Umbrex https://umbrex.com/resources/the-busy-consultants-guide-to-quantitative-charts/design-principles-for-mckinsey-quantitative-charts/
- [đọc] Slideworks https://slideworks.io/resources/how-to-write-action-titles-like-mckinsey
- [đọc] Reuters DNR 2025, e-Conomy SEA 2025 (link ở `vang/README.md`)
- [chỉ thấy] McKinsey Superagency; iamwrm/typst_skill (404)

Trích nguyên văn chính: Pew "number check", người kiểm "didn’t contribute to the writing or graphics at all"; Pew "Is the underlying number that was plotted in the chart correct?"; Urban "The axis in bar charts (whether vertical or horizontal) should always start at zero."; Umbrex "if you cover up the data and only read the title, do you still get the point?"; Slideworks "Write the titles first."
