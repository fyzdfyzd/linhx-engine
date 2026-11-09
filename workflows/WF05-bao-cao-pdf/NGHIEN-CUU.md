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

## Bổ sung vòng 2

9/11. Lấp các chỗ vòng 1 tự khai mỏng (`_refs/WF05/chay.log`), đọc kết quả Deep Research `DR/KQ-1.md` [DR], thử máy đo trên một báo cáo có sẵn.

### 1. Lấp chỗ mỏng
- **Adobe whitepaper, đã đọc repo gốc.** Clone `adobe/skills` vào `_refs/WF05/adobe_skills` (không chạy). Tệp `plugins/aem/project-management/skills/whitepaper/SKILL.md` xác nhận đúng như vòng 1 đọc qua tóm tắt: pandoc → Typst, A4, 10pt, font Source Sans 3. Nguyên văn: "Delete ALL source files immediately after PDF is created" và "THIS SKILL RUNS COMPLETELY UNATTENDED". Vẫn bỏ hai luật này. Mới thấy thêm: skill tự cài pandoc/typst bằng curl rồi tar ở Linux (không hợp luật LINHX). https://github.com/adobe/skills/tree/main/plugins/aem/project-management/skills/whitepaper
- **Ngưỡng "chấm mù hai lần lệch ≤1 điểm" nay có nguồn ngoài.** Cách chấm bài luận GRE của ETS: "If the two assigned scores differ by more than 1 point on the scale, the discrepancy is adjudicated by a third GRE reader." (ETS R&D Connections, 4/2005, Monaghan và Bridgeman, https://www.ets.org/Media/Research/pdf/RD_Connections2.pdf, đã đọc PDF). Lấy luật đi kèm: lệch >1 thì **người chấm thứ ba**, không lấy trung bình. Đề xuất sửa máy đo: chấm mù 2 lần, lệch >1 thì gọi agent thứ ba, lấy điểm thấp trong hai điểm gần nhau.
- **Ngưỡng "phép thử tiêu đề ≥90%" vẫn chưa có nguồn ngoài.** Giữ là đề xuất, đo ở vòng 1.
- **Kiểm các trích dẫn trong DR [DR]:**
  - Pew, đúng nguyên văn, link sống: "Can this chart stand alone?" và "Our usual rule of thumb is to require an effective sample size of about 100 or more." (https://www.pewresearch.org/decoded/2019/10/14/how-we-check-numbers-and-facts-at-pew-research-center/). Lấy: mỗi hình qua câu "đứng riêng được không" (đăng lên mạng tách khỏi bài vẫn hiểu); nhóm con có n dưới khoảng 100 thì không vẽ riêng.
  - Reuters DNR 2025, đúng nguyên văn (tìm trong PDF đã tải, `pdftotext`): "We typically do not regard differences of +/- 2pp as meaningful, and as a general rule we do not refer to them in the text." Lấy: luật văn "không gọi là tăng/giảm khi chênh ≤2 điểm %" cho số khảo sát. Thêm được vào `kiem-so`.
  - "Start with the insight, then choose the chart." có thật, nhưng là blog bán mẫu SlideUpLift, **không phải McKinsey** (https://slideuplift.com/blog/mckinsey-style-presentation/). DR gắn nhầm là "hướng dẫn chuẩn McKinsey".
  - Bảng lề McKinsey "21/15/14/17 mm" và cỡ chữ 20/17/12–14 pt trong DR: **chưa kiểm được** (tải PDF MGI quá thời gian chờ). Không dùng.
  - 36Kr (https://36kr.com/p/2853458940627588): trang chặn bằng màn kiểm tra an ninh, không đọc được. Khung 4 bước của 36Kr và "三审" trong DR **chưa kiểm**, không dùng.
  - Bốn lỗi phông tiếng Việt trong DR (thiếu glyph, rơi font dự phòng, bảng mã VNI/TCVN3, không nhúng font) chỉ có nguồn blog thợ (ví dụ https://onepidesign.com/cach-sua-loi-font-tieng-viet-trong-thiet-ke/, chưa mở). Hai lỗi đầu và lỗi nhúng font đo được bằng máy, xem mục 2.
- **Bản vàng V1 đo lại:** Reuters DNR 2025 là **A4 dọc** (595 × 842 pt, 171 trang, đo bằng PyMuPDF). Vậy V1 dùng được làm khuôn A4 dọc, chỉ thiếu tiếng Việt.
- **Bản vàng V4 đã chọn:** Pew "AI and Human Enhancement" (3/2022), https://www.pewresearch.org/wp-content/uploads/sites/20/2022/03/PS_2022.03.17_AI-HE_REPORT.pdf, link sống, 164 trang khổ Letter dọc (612 × 792 pt), có mục "How we did this", chữ "Methodology" xuất hiện 12 lần, "Topline" 2 lần (đếm trong text PDF). Chưa xem trang bằng mắt.
- **Ứng viên tiếng Việt:** Cimigo "Xu hướng tiêu dùng Việt Nam 2026" (12/2/2026) có thật, tiếng Việt, nhưng tải qua form gửi email (https://www.cimigo.com/vi/trends/xu-huong-tieu-dung-viet-nam-2026/). EuroCham Whitebook 2024 vượt 10 MB, WebFetch không đọc được. Hai mẫu này đưa vào `DR/DE-2.md` cho máy công ty.

### 2. Thử máy đo trên mẫu có sẵn
Mẫu: `D:\LINHX\LAB\LAB028-REPORT-FLOW\output\bao-cao-dao-tao-ai-vn` (17 trang). Chép sang scratchpad trước vì `cong` ghi vào `trang-thai.json`.

| Lệnh | Kết quả thật |
|---|---|
| `python skills\bo\linhx-report\scripts\report.py kiem-so <bản chép>` | ĐẠT, `{'dat': 116, 'can-duyet': 0, 'mo-coi': 0}` |
| `report.py kiem-ban-in <bản chép>` (lần 1) | Hỏng: `FileNotFoundError` vì `trang-thai.json` ghi đường dẫn style tuyệt đối của máy khác (`\mnt\attach\project-files\...\style.json`). **Lỗi khả chuyển của skill**: nên lưu đường dẫn tương đối |
| `report.py cong <bản chép> 11` (sau khi sửa đường dẫn trong bản chép) | CHƯA ĐẠT: "LỖI [11] PDF mới hơn bảng chấm" (bản gốc cũng vậy: PDF 18:17:21, bảng chấm 18:17:17 ngày 13/10). Cảnh báo D07 phủ chữ 0,38 (mục tiêu 0,18–0,32). Cỡ chữ phổ biến 9,8 pt, 2 họ font |
| Máy đo mới (nháp, `may-do-nhap/do_thu_wf05.py`, chỉ đọc; chạy `python -I -X utf8 may-do-nhap/do_thu_wf05.py <thư mục báo cáo>`) trên bản gốc | 0 lỗi, 6 cảnh báo. 12 hình đều ≤7 hạng mục, 1 chuỗi, tiêu đề 13–25 tiếng. 7 font đều nhúng (ttf). Mọi giá trị vẽ trên hình đều có mặt thành chữ trong PDF. Cảnh báo: số giá trị khác số mã BC (H01: 5 giá trị, 4 mã BC; H02: 3/2…). `kiem-so` vẫn đạt nên chưa chắc là lỗi; cần người xem |
| Máy đo glyph tiếng Việt (nháp, `may-do-nhap/do_glyph_viet.py <tệp font>…`, 146 ký tự) | Be Vietnam Pro, Source Serif 4, Source Sans 3, Arial: 146/146. Đối chứng âm: Impact 54/146, Algerian 44/146 (thiếu ơ, ư, ạ…). Máy phân biệt được |

Kết luận đo thử: skill hiện **đã có** kiểm rơi font (D11, "có font ngoài khai báo"), **chưa có** kiểm nhúng font và kiểm phủ glyph tiếng Việt của tệp font trước khi dựng; hai kiểm này rẻ, nên thêm vào bước 10. Phép kiểm "số vẽ trên hình có thành chữ" còn yếu: chỉ tìm chuỗi số trong toàn văn, chưa so độ dài thanh với giá trị.

### 3. Sửa thêm vào skill (đề xuất, chưa sửa)
- `dan-trang` bước 10: kiểm nhúng font (PyMuPDF `get_fonts`) và phủ 146 ký tự Việt cho mọi font khai báo.
- `dan-trang` bước 11: chấm mù 2 lần, lệch >1 điểm thì agent thứ ba (theo ETS).
- `hinh-du-lieu`: câu hỏi Pew "Can this chart stand alone?"; nhóm con n dưới khoảng 100 không vẽ riêng.
- `kiem-so`: chênh ≤2 điểm % giữa hai số khảo sát thì văn không được viết "tăng/giảm" (theo Reuters).
- `report.py`: lưu `style` tương đối; cổng 11 lỗi khi PDF mới hơn bảng chấm là đúng, giữ.

### Còn thiếu sau vòng 2
Reddit/X/LinkedIn, tessl, Perplexity cookbook chưa đọc. Nguồn tiếng Trung chưa đọc được (36Kr chặn). Chưa có bản vàng tiếng Việt A4 dọc đã xem tận mắt. Ngưỡng phép thử tiêu đề 90% chưa có nguồn. Số liệu dàn trang McKinsey trong DR chưa kiểm.
