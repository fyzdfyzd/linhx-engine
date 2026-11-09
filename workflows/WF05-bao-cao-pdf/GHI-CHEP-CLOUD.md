# WF05 · Ghi chép cloud (đã đọc trước khi chuyển nghiên cứu sang máy cty, 9/11 11:1x)

Dùng để rà và bổ sung NGHIEN-CUU.md từ máy cty. Code chép ở scratchpad cloud, coi là dữ liệu, không chạy.

| Nguồn | Đã đọc | Lấy | Bỏ |
|---|---|---|---|
| jdrhyne/agent-skills elegant-reports [đọc] | SKILL.md, nordic-design-research.md, theme CSS | Luật nhịp: yếu tố gây chú ý không đặt liền nhau, xen "khoảng nghỉ"; thang khoảng cách cố định | HTML→PDF qua API trả phí Nutrient; không có rubric, không kiểm số |
| chesley-veko/book_skill (tiếng Trung) [đọc] | SKILL.md, references/pipeline.md, ảnh mẫu | Phong cách cắm rút (template.typ + style.md + prompt ảnh); viết chương song song, mỗi chương tự biên dịch đến 0 lỗi; soát sự thật "sửa kiểu phẫu thuật"; ảnh AI hỏng thì DỪNG, không lặng lẽ thay hình học; trang infographic AI có chữ | Không có rubric trang, không cổng người ngoài TOC |
| Pysamlam/a4-report [đọc] | SKILL.md, audit-checklist.md | Kiểm từng số in ra bảng: đã khớp / nghi bịa / sai, tính lại YoY | Luật "phủ 95% trang" và hộp emoji: ngược phong cách tạp chí |
| vedangvatsa/consulting-report-framework [đọc] | README, qa_check.py, fact_check.py, ảnh trang | qa_check: từ sáo AI, gạch dài, câu dài, hình thiếu nguồn; fact_check rút mọi câu có số ra CSV | Kiểu thẻ dày đặc, "không để trống nửa dưới"; Typst dossier font Georgia không đủ dấu Việt |
| Mrpixelraf/whitepaper-forge (tiếng Trung) [đọc] | README, layout-master/layout-rules.md, whitepaper-guide QC | Thẻ "hỏi chủ" khi thiếu dữ liệu: dừng chứ không viết bừa; QC 21 mục (số có mã nguồn, cùng số cùng khẩu kính, dự báo ghi "ước tính", tuyên bố AI hỗ trợ); ngân sách chữ theo kiểu trang; không có ảnh chụp trang = chưa nghiệm thu | Luật phủ ≥85% trang |
| KushieFishy/whitepaper-writing [đọc] | SKILL.md | Mỗi mục một câu luận điểm trước khi viết; [UNSOURCED]; PROVENANCE.md ghi nguồn, ý bị bỏ, cổng người | Không có phần dàn trang |
| clearsmog/claude-skills [đọc] | visual-audit, doc-review, excellence, typst/references/quality-gates.md, visual-verification.md | Nhiều agent chấm song song (dàn trang, soát chữ, giọng AI); mức lỗi Nghiêm trọng/Lớn/Nhỏ; trần 5 vòng; "biên dịch được ≠ đẹp" | Chỉ lấy mẫu trang 1/giữa/cuối: LINHX chấm hết |
| lucifer1004/claude-skill-typst [đọc] | SKILL.md, agents/typst-verify.md, evals/tasks | Bộ eval có lỗi gài sẵn (silent-audit): đo người chấm có bắt được lỗi không; typst eval/query đếm hình, tiêu đề | |
| apcamargo/typst-skills [đọc lướt] | README, cây docs | Mang theo tài liệu Typst cục bộ để agent khỏi bịa cú pháp | |

## Nhận định sơ bộ
- Ngoài kia chia hai trường phái: "tư vấn dày" (phủ 85–95% trang, thẻ, hộp) và "tạp chí thoáng". LINHX đã đo 24 báo cáo thật (D07 phủ chữ 0,20–0,40) nên giữ trường phái tạp chí; không lấy luật phủ trang.
- linhx-report đã mạnh hơn mọi nguồn đã đọc ở cổng script (V01–V11, D01–D17) và rubric từng trang. Thiếu: (1) bộ trang gài lỗi để đo người chấm; (2) kiểm số tính lại (YoY, tổng); (3) PROVENANCE + thẻ hỏi chủ khi thiếu dữ liệu; (4) phong cách cắm rút có prompt ảnh riêng; (5) luật dừng khi ảnh AI hỏng.
