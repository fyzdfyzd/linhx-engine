# Người ngoài đã làm: WF05

Cập nhật 9/11 (nghiên cứu nền). Mã đã chép về `D:\LINHX\WF-NC\_refs\WF05\` làm dữ liệu, không chạy. [đọc] = đọc nội dung thật; [chỉ thấy] = chỉ thấy tên hoặc tóm tắt.

| Nguồn | Đã đọc gì | Lấy | Bỏ |
|---|---|---|---|
| elegant-reports (jdrhyne) https://github.com/jdrhyne/agent-skills/tree/main/skills/elegant-reports [đọc SKILL.md, NORDIC_DESIGN_RESEARCH.md] | Mẫu HTML→PDF qua Nutrient DWS (dịch vụ trả phí bên ngoài), 3 mẫu `executive/report/presentation`, nhắc "Do not claim a report was generated successfully unless the output artifact exists" | Luật "không báo xong khi chưa có tệp ra"; tách token màu/khoảng cách; "một thay đổi một lần rồi dựng lại" | Gửi nội dung lên dịch vụ ngoài; không có chấm trang, không kiểm số, không nguồn |
| typst-author (apcamargo) https://github.com/apcamargo/typst-skills [đọc SKILL.md] | Tài liệu Typst 0.15 kèm theo, bắt "PRIORITY: Trust local documentation", chạy `typstyle` rồi `typst compile` sau mỗi lần sửa | Chép tài liệu Typst bản mới làm tham chiếu; bước kiểm cú pháp bằng `typstyle` sau mỗi lần sửa `.typ` | Không có gì về thiết kế trang |
| adobe/skills whitepaper https://skills.browseract.com/skills/adobe-skills-whitepaper [đọc trang tóm tắt, chưa đọc repo gốc] | Markdown→pandoc→Typst, A4, tự tạo bìa, mục lục, ngắt trang H1 | Khẳng định hướng Markdown+Typst của LINHX là đúng; cờ `TYPST_FONT_PATHS` để nhúng font | "Xóa tệp nguồn ngay sau khi có PDF" (nguy hiểm), "chạy không hỏi", không chấm chất lượng |
| pdf-design (jamditis) https://github.com/jamditis/claude-skills-journalism/tree/main/pdf-design [đọc SKILL.md] | HTML→Chromium headless→PDF, vòng xem trước từng trang (`preview page N`), "Sentence case, never Title Case; Left-aligned, never justified" | Vòng "xem trang → sửa → dựng lại"; chặn mã chủ động trong HTML nguồn (coi nguồn là dữ liệu) | Gắn cứng thương hiệu tác giả; khổ Letter; căn trái bắt buộc (LINHX tiếng Việt có thể justify nếu D-luật ổn) |
| market-report / market-report-pdf (kmshihab7878) https://github.com/kmshihab7878/claude-code-setup [đọc SKILL.md market-report] | Báo cáo marketing có thang điểm 6 nhóm, kế hoạch 30-60-90, "Label assumptions, estimates, missing data, and confidence levels" | Gắn nhãn giả định/ước tính/độ tin cậy cạnh số | Thang điểm cố định kiểu marketing; không dàn trang |
| Pew: How we check numbers and facts https://www.pewresearch.org/decoded/2019/10/14/how-we-check-numbers-and-facts-at-pew-research-center/ [đọc] | Quy trình "number check" | Xem mục Quy trình bên dưới | Kiểm trên giấy bằng bút chì (thay bằng script + người kiểm khác) |
| Pew: small multiples https://www.pewresearch.org/decoded/2018/12/20/how-pew-research-center-uses-small-multiple-charts/ [đọc] | Luật biểu đồ | ≤5 đường/biểu đồ, khuôn chung, chỉ đổi dữ liệu | — |
| Urban Institute Data Viz Style Guide https://urbaninstitute.github.io/graphics-styleguide (đã clone repo: `_refs/WF05/UrbanInstitute_graphics-styleguide`) [đọc trang] | Luật biểu đồ, nguồn, ghi chú | Bắt buộc "title, source line, and axis or other labels"; "Stop! Should it even be a chart?"; <7 hạng mục | Công cụ Excel |
| Umbrex: McKinsey quantitative charts https://umbrex.com/resources/the-busy-consultants-guide-to-quantitative-charts/design-principles-for-mckinsey-quantitative-charts/ [đọc; tài liệu độc lập, không phải của McKinsey] | Phép thử tiêu đề | "if you cover up the data and only read the title, do you still get the point?" | — |
| Slideworks action title https://slideworks.io/resources/how-to-write-action-titles-like-mckinsey [đọc] | Tiêu đề kết luận | "Write the titles first"; <15 từ; đọc riêng các tiêu đề để kiểm mạch | Giới hạn 15 từ cho báo cáo giấy (LINHX đang 8–30 tiếng, hợp lý hơn) |
| iamwrm/typst_skill https://github.com/iamwrm/typst_skill | Link trả 404 (9/11) | — | Bỏ khỏi danh sách |
| Perplexity cookbook agent skills | [chỉ thấy] | — | Chưa đọc, không ưu tiên |
| tessl elegant-reports/review | [chỉ thấy] | — | Chưa đọc |
| adobe/skills whitepaper, repo gốc https://github.com/adobe/skills (vòng 2, clone `_refs/WF05/adobe_skills`) [đọc SKILL.md] | Xác nhận pandoc→Typst, A4, Source Sans 3 (đo: đủ 146 ký tự Việt) | Cờ `TYPST_FONT_PATHS`, font đi kèm skill | Xoá nguồn sau khi dựng, chạy không hỏi, tự cài bằng curl rồi tar |
| ETS R&D Connections 2005 https://www.ets.org/Media/Research/pdf/RD_Connections2.pdf (vòng 2) [đọc] | Hai người chấm lệch >1 điểm thì người thứ ba | Ngưỡng chấm mù lệch ≤1, quá thì agent thứ ba | — |
| [DR] Pew number check (kiểm lại vòng 2) [đọc] | "Can this chart stand alone?"; n hiệu dụng khoảng 100 | Câu hỏi đứng riêng; ngưỡng n nhóm con | — |
| [DR] Reuters DNR 2025 phương pháp (kiểm trong PDF, vòng 2) [đọc] | "do not regard differences of +/- 2pp as meaningful" | Luật văn ±2 điểm % | — |
| [DR] SlideUpLift https://slideuplift.com/blog/mckinsey-style-presentation/ (vòng 2) [đọc] | Câu "Start with the insight…" có thật | — | Blog bán mẫu, không phải McKinsey |
| [DR] 36Kr https://36kr.com/p/2853458940627588 (vòng 2) | Bị màn kiểm tra an ninh chặn | — | Chưa đọc được |
| [DR] Pew AI and Human Enhancement 2022 (vòng 2) [đọc text PDF] | 164 trang Letter dọc, có Methodology, Topline | Bản vàng V4 | — |
| [DR] Cimigo Xu hướng tiêu dùng VN 2026 (vòng 2) [đọc trang] | Tải qua form email | Ứng viên bản vàng tiếng Việt → `DR/DE-2.md` | — |

Còn chưa làm: Reddit/X/LinkedIn, nguồn tiếng Trung, tiếng Việt → đề DR `DR/DE-1.md`.
