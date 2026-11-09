# WF13 · Nền nghiên cứu: khoá lớp corp (Course OS)

9/11/2026. Đọc thật 5 bộ skill ngoài + 2 phương pháp của người làm nghề top + 3 mẫu khoá AI cho doanh nghiệp. Chi tiết bảng đọc ở `NGOAI.md`.

## Kết luận 5 dòng
1. Giữ Course OS bản 2 làm xương sống, vì nó đã ngang bộ ngoài tốt nhất (idstack). Không viết lại.
2. Thiếu lớn nhất nằm ở đầu khâu: LINHX chưa hỏi "việc gì phải làm khác đi, đo bằng số nào, có phải do thiếu kỹ năng không". Cathy Moore và idstack đều đặt câu này trước mọi slide.
3. Thiếu thứ hai là thời lượng thực hành. Bộ TBR 4Cs đòi thực hành chiếm 40–50% thời gian, không đoạn giảng nào dài quá 15 phút. Máy kiểm được hai điều này.
4. Thiếu thứ ba là bản giảng viên đủ để trợ giảng dạy một mình: kịch bản theo phút, câu nói chốt, câu hỏi học viên hay hỏi, phương án khi chậm giờ hay mất mạng.
5. Đo hiệu quả nên theo 8 tầng LTEM: lớp corp của LINHX hiện mới đo tới tầng 3 (cảm nhận). Mục tiêu v1 là đo tới tầng 6–7 (làm được việc, dùng lại sau 30 ngày).

## Quy trình đề xuất (một bài, một lớp)
| # | Bước | Ra gì | Ai |
|---|---|---|---|
| 1 | Nhận đề, hỏi theo khuôn 7 dòng + **đích đo** ("số X đổi Y% trước ngày Z vì nhóm A làm được B") | `de.json` | Linh 10 phút, agy |
| 2 | **Việc thật**: liệt kê việc học viên phải làm, chấm tần suất × hệ trọng; mỗi việc ghi khó vì đâu (kỹ năng, quy trình, công cụ, động lực). Việc không do kỹ năng → danh sách cho Agent Force | `viec.yaml` | agy |
| 3 | Khung theo 4C: Kết nối 10–15% · Khái niệm 30–40% (khúc ≤ 15 phút, mỗi khúc có 1–2 phút xử lý) · Thực hành 40–50% (có hướng dẫn → theo nhóm → tự làm) · Chốt 5–10% (học viên tự tóm, cam kết). Gắn nhãn xương sống / tự chọn | `khung.yaml` | agy |
| **D2** | Linh chọn 1 trong 2–3 hướng khung (che tên nhánh) | | Linh |
| 4 | Sinh từ một lõi: đề cương, slide (LAB099), workbook, quiz trước/sau, prompt pack, bản giảng viên | thư mục khoá | agy |
| 5 | Máy đo rẻ → đắt (dưới) | `PHIEU-CHAM.md` | máy, Claude máy cty, 1 trợ giảng |
| **D4** | Linh duyệt cuối | | Linh |
| 6 | Sau lớp: điểm, quiz sau, hỏi lại D+30 | báo cáo HR 1 trang | agy, Linh duyệt |

## Máy đo + ngưỡng
| Tầng | Kiểm gì | Ngưỡng qua |
|---|---|---|
| Tự động | (a) mỗi mục tiêu có hoạt động **và** đánh giá; mục tiêu không dùng "hiểu, nắm được"; (b) thực hành ≥ 40% tổng phút; không khúc giảng > 15 phút; mỗi khúc có xử lý; (c) slide qua `vls.py` (phông đủ 134 chữ Việt, chữ/slide); (d) bản giảng viên đủ 6 mục: theo phút, câu chốt, câu hỏi hay gặp, chuyển ý, dự phòng, checklist D-1 | 100% |
| Red team mắt sạch | Claude máy cty, không thấy lịch sử thợ, 5 chiều idstack + giả lập 4 học viên Việt (nhân viên lớn tuổi ngại máy, quản lý bận, người đã dùng AI nhiều, người sợ AI thay việc). Trừ Critical −15, Warning −5 | ≥ 80/100 |
| Trợ giảng | 1 trong 6 trợ giảng đọc bản giảng viên, dạy thử 15 phút, ghi mọi câu phải hỏi Linh | 0 câu |
| Linh D4 | Sửa lớn hay không | không sửa lớn |
| Sau lớp | Điểm học viên; quiz sau so với trước; D+30 còn dùng ≥ 1 workflow | ≥ 4,5/5; +40%; ≥ 60% |

## Bản vàng (mốc chấm, chưa Linh duyệt)
1. **Anthropic AI Fluency** (khung 4D: Giao việc, Mô tả, Phân định, Cẩn trọng). Tốt vì: học viên làm một dự án thật của mình xuyên khoá, kết thúc bằng bản cam kết dùng AI có trách nhiệm. Đúng chất "agentic working" cho CBCNV. [đọc qua bài giới thiệu + trang Skilljar]
2. **Microsoft Copilot Success Kit**: bộ triển khai cho doanh nghiệp (hướng dẫn cho lãnh đạo, thư viện tình huống theo việc, prompt-a-thon, "10 việc thử đầu tiên"). Tốt vì: có phần cho người quản lý và phần sau lớp, không dừng ở buổi học. [đọc trang tổng]
3. **Cathy Moore, sơ đồ action mapping 15 bước**: mẫu cho bước 1–3. Tốt vì: bắt đầu từ số đo kinh doanh, chỉ dạy khi phân tích thấy cần luyện quyết định. [đọc]
4. Giáo trình Vinhomes/MSB cũ của Linh: mốc "trước khi chuẩn hoá" để so. [chờ lấy từ máy]

## Sửa vào skill nào, sửa gì
- `linhx-engine/skills/bo/linhx-course/skills/course-architect`: thêm bước "đích đo + việc thật" trước mục tiêu; thêm luật 4C và ngưỡng phút; thêm nhãn xương sống / tự chọn. Skill này hiện viết cho e-learning video 5 phút, cần thêm nhánh lớp trực tiếp.
- Course OS bản 2, module 02 (người học): thêm `viec.yaml` + cổng có nên đào tạo. Module 08: bản giảng viên 6 mục bắt buộc. `verify.py`: thêm kiểm tự động (a)(b)(d).
- Thêm skill mới `khoa-red-team` (hoặc vào `linhx-chuan`): đề chấm mắt sạch + điểm 0–100.
- Đã viết `kiem_khoa.py` (thư mục WF13) kiểm `khung.yaml`: phút 4C, khớp mục tiêu, nhãn, bản giảng viên 6 mục; thử với `mau-kiem/tot.yaml` (DAT) và `xau.yaml` (CHUA_DAT, 14 lỗi). Vòng 1 đưa vào verify.py của Course OS.

## Rủi ro
- master-instructional-design cấm dùng thương mại: chỉ lấy ý, không chép chữ hay mẫu vào repo.
- Tài liệu nội bộ khách (Vinhomes, ngân hàng) không đưa lên kho chung khi chưa ẩn danh, không để red team gửi ra ngoài.
- Tỉ lệ 4C là kinh nghiệm của một trường phái (Training from the Back of the Room), không phải nghiên cứu; coi là ngưỡng khởi điểm, chỉnh sau 2 lớp.
- Đo D+30 cần HR khách hợp tác; phải ghi vào bản chào từ đầu.

## Nguồn
- idstack: https://github.com/savvides/idstack [đọc: README, needs-analysis, red-team, assessment-design, course-builder]
- master-instructional-design: https://github.com/narosemena/master-instructional-design [đọc: README, SKILL.md, document-templates, facilitation-and-ilt]
- educates-course-design: https://github.com/educates/educates-course-design-skill [đọc: README, SKILL.md]
- course-material-creator: https://github.com/travisjneuman/.claude/tree/master/skills/course-material-creator [đọc]
- bailejl AI-Enablement training-designer, workshop-facilitator-prep, training-reviewer (bản chép ở https://github.com/mattnigh/skills_collection/tree/main/collection) [đọc 3 SKILL.md]
- learning-workshop-builder: https://skills.sh/pauljbernard/content/learning-workshop-builder [chỉ thấy]
- Cathy Moore: https://blog.cathy-moore.com/action-mapping-workflow-at-a-glance/ [đọc]. Nguyên văn: "Focus on what people need to do, not what they might need to know."
- LTEM (Thalheimer), bản tóm: https://thinkdev.org/blog/learning-transfer-evaluation-model [đọc, nguồn thứ cấp]
- Anthropic AI Fluency: https://www.theneuron.ai/explainer-articles/inside-anthropics-ai-fluency-masterclass-on-human-ai-collaboration , https://anthropic.skilljar.com/ai-fluency-for-small-businesses [đọc]
- Microsoft Copilot Success Kit: https://adoption.microsoft.com/copilot/success-kit [đọc trang tổng, chưa đọc bộ tải về]
- Chưa vào được (cloud chặn): openskillindex, skills.lc (WeMakeGood LeadersPath, OpenClaw training-course-designer).
