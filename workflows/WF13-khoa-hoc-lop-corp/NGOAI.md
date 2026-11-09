# Người ngoài đã làm: WF13

Bước 0 làm xong 9/11/2026. Đã đọc code (SKILL.md, mẫu, agent) của 4 nguồn trên GitHub qua raw.githubusercontent. Các trang chỉ mục (openskillindex, skills.sh, skills.lc…) bị chặn ở cloud; WeMakeGood LeadersPath, OpenClaw training-course-designer, Corporate Training Designer chưa tìm được đường dẫn code, để vòng 2 mở bằng Chrome máy cty (DESKTOP-PVHR2CD).

## Bảng đọc

| Nguồn | Đã đọc gì | Lấy | Bỏ |
|---|---|---|---|
| **idstack** (savvides/idstack, MIT, beta v3.10, 12 skill), tốt nhất | README, `skills/needs-analysis`, `red-team`, `assessment-design`, `course-builder` (.tmpl) | (1) **Cổng "đào tạo có phải cách chữa không"** ở bước nhu cầu: khoảng cách hiện tại → mong muốn, nguyên nhân là thiếu kỹ năng hay do quy trình, khuyến khích; ghi cả phương án không đào tạo. Với lớp ngân hàng đây là chỗ nối sang Agent Force (việc nào nên làm agent thay vì dạy). (2) **Phân tích việc**: mỗi việc học viên phải làm có tần suất × mức hệ trọng → ưu tiên; "hiểu AI" không phải việc. (3) **Red team mắt sạch**: chạy ở subagent không thấy lịch sử soạn, 5 chiều (khớp mục tiêu, bằng chứng, tải nhận thức, giả lập học viên, chuỗi tiên quyết), ra điểm tin cậy 0–100 (Critical −15…), ngưỡng 80/60/40. (4) **Duyệt từng mục**: chat chỉ một dòng + một câu hỏi, bảng để trong file báo cáo. (5) Khuyến nghị gắn mức bằng chứng T1–T5. (6) Một manifest chung cho cả khoá. | Xuất IMSCC/Canvas API, extension Chrome, chuẩn đại học (QM, CoI). Persona "ESL" đổi thành persona VN (giao dịch viên lớn tuổi, quản lý chi nhánh bận). Không cài nguyên bộ: tiếng Anh, giả định giảng viên đại học. |
| **master-instructional-design** (narosemena, **giấy phép riêng, cấm dùng thương mại**) | README, `SKILL.md` (15 chế độ, khung rà 9 chiều), `references/document-templates.md`, `facilitation-and-ilt.md` | Chỉ lấy ý, không chép chữ: (1) **Bản giảng viên** có cột "học viên hay trả lời gì" và bảng "tình huống → xử lý": đúng thứ trợ giảng cần để dạy không phải hỏi Linh. (2) Khung rà có **an toàn tâm lý** và **chuyển giao về việc**: hợp lớp ngân hàng, nơi nhân viên sợ AI thay việc. (3) Kirkpatrick mức 3 cần **quản lý quan sát** sau lớp → nối đo 30 ngày. (4) Hook chặn ghi đè SKILL.md, router chọn file tham chiếu theo từ khoá (0 token). | Không chép nội dung, không đưa vào repo (giấy phép). Bỏ phần Storyline, Captivate, Adobe. |
| **educates-course-design** (educates) | README, `SKILL.md` 6 bước | (1) **Phạm vi co giãn**: workshop lẻ thì rút bước, khoá nhiều phần mới đủ bước. (2) Bài chia **xương sống / tự chọn**: hợp "bản theo khách" (giữ xương sống, đổi tự chọn theo ngành). (3) Bước **rà nhất quán** giữa các file, lỗi ghi thành việc. (4) Mỗi khoá có file chỉ dẫn cho AI (AGENTS.md) trỏ tới brief, nguồn, quy ước. | Toàn bộ phần nền tảng Educates (Kubernetes, YAML workshop). |
| **bailejl AI-Enablement** training-designer, workshop-facilitator-prep, training-reviewer (bản chép mattnigh/skills_collection) | 3 SKILL.md | Luật TBR 4Cs: kết nối 10–15%, khái niệm 30–40% (khúc ≤ 15 phút), thực hành 40–50%, chốt 5–10%; luật 10-1; danh sách lỗi Critical (thực hành < 40%, giảng > 15 phút liền, thực hành giả thay việc thật, không có hỗ trợ sau lớp); bản giảng viên theo phút có câu chốt nguyên văn, Q&A, dự phòng. **Máy kiểm tự động được.** | Script `checklist_scorer.py` không có trong bản chép; mô hình 70-20-10 để sau. |
| **Cathy Moore action mapping** (blog) | trang quy trình 15 bước | Bắt đầu từ số đo kinh doanh; liệt kê việc phải làm; khó vì đâu; "đào tạo có phải là một phần lời giải"; mẫu thử 1 hoạt động trước khi soạn cả bộ. | Phần bán khoá, sách. |
| **course-material-creator** (travisjneuman/.claude) | `skills/course-material-creator/SKILL.md` | Mẫu workshop, bảng động từ Bloom (đã có ở course-architect). | Mẫu chung, không kiểm, không cổng. Không lấy thêm. |

## So với cái LINHX đang có

| LINHX có | Ngoài có | Kết luận |
|---|---|---|
| Course OS bản 2 (PROTO 06, 9 module, 12/12 tiêu chí): một lõi nội dung → nhiều đầu ra; cổng 08 dừng ở CHO_GIANG_VIEN_DUYET; persona neo + chẩn đoán 12 câu | idstack manifest chung, pipeline tự bỏ bước đã xong | Xương sống LINHX đã ngang idstack. **Giữ Course OS bản 2, không thay.** |
| `linhx-course/course-architect`: Backward Design, Bloom, quiz ↔ mục tiêu | idstack learning-objectives + assessment-design | Ngang nhau. Thêm: kiểm hai chiều (mỗi mục tiêu có hoạt động **và** đánh giá). |
| Module 02 người học | needs-analysis 3 tầng + **cổng có nên đào tạo** + việc tần suất × hệ trọng | **LINHX thiếu.** Thêm vào module 02. |
| Chấm mù LAB106, vòng slide LAB099 | red-team mắt sạch 5 chiều + điểm tin cậy + giả lập học viên | **Thêm red team mắt sạch** làm máy đo rẻ trước khi trợ giảng dạy thử. |
| Module 08 bản giảng viên, D-7/D-3/D-1 | bản giảng viên có câu trả lời dự kiến + xử lý tình huống | **Thêm 2 cột** → đo được "trợ giảng dạy không cần hỏi Linh". |
| Chưa có bản theo khách có cấu trúc | xương sống / tự chọn | Gắn nhãn `xuong_song` / `tu_chon` cho từng bài; bản theo khách chỉ đổi tự chọn + ví dụ ngành. |

## Đưa vào vòng 1
1. Module 02 thêm **việc thật** (tần suất × hệ trọng) và **cổng có nên đào tạo** → danh sách việc chuyển Agent Force.
2. Khung gắn nhãn xương sống / tự chọn.
3. Bản giảng viên có cột "học viên hay trả lời" và bảng "tình huống → xử lý".
4. Red team mắt sạch (Claude máy cty, không thấy lịch sử thợ) ra điểm 0–100, ≥ 80 mới đưa trợ giảng dạy thử.
