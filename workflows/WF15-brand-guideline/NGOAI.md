# Người ngoài đã làm: WF15

Bước 0, tìm sơ bộ 9/11 (GitHub, trang skill, blog, mạng). **Mới tìm thấy, chưa đọc code.** Vòng 1 phải đọc code/quy trình ít nhất 3 cái tốt nhất, ghi: lấy gì, bỏ gì, so với skill LINHX đang có.

| Nguồn | Link | Đọc để |
|---|---|---|
| brand-guidelines (Anthropic) | https://open-design.ai/skills/anthropics-brand-guidelines/ | skill gốc |
| brand-style-guide (rampstackco) | https://skills.cat/skills/rampstackco/claude-skills/brand-style-guide | có evals |
| brand-guidelines-generator (claude-office-skills) | https://skills.sh/claude-office-skills/skills/brand-guidelines-generator | sinh guideline |
| brand-guidelines (alirezarezvani) | https://open-design.ai/skills/alirezarezvani-brand-guidelines/ | so với chuẩn BTMH |

## Còn phải tìm ở vòng 1
- GitHub theo tên skill + 'SKILL.md'; skills.sh, claudemarketplaces, openskillindex.
- Mạng: X, LinkedIn, Reddit, nhóm Facebook VN; tiếng Trung khi hợp.

| Nguồn | Đã đọc gì | Lấy | Bỏ |
|---|---|---|---|
| brand-style-guide (rampstackco) | đọc SKILL.md đủ 202 dòng (clone `_refs/WF15/rampstackco_claude-skills`) | khung 8 mục, 7 kiểu hỏng, "nguồn là md, bản trình bày chỉ là view"; không thấy evals riêng (sửa ghi chú cũ "có evals") | không có số đo mỹ thuật; khung logo/màu mỏng hơn BTMH |
| design.md (google-labs-code) | spec.md, README, danh sách luật lint (broken-ref, contrast-ratio 4,5, missing-primary, section-order, orphaned-tokens…) | token YAML + lint + diff + export css-vars/Tailwind/DTCG | chưa chạy; alpha |
| open-design (nexu-io) | README engine thương hiệu, skills brandkit, brand-extract (sparse clone `od2`) | seed ~20 trường → token dẫn xuất, đo từ trang thật chứ không đoán; bố cục bảng ảnh brandkit tối giản | engine TypeScript nặng; brandkit sinh ảnh bảng, trùng việc ChatGPT mockup |
| brand-guidelines (anthropics) | SKILL.md 73 dòng | không gì: chỉ màu/font Anthropic | cả skill |
| brand-guidelines (alirezarezvani) | SKILL.md + references | checklist audit nhanh, ngưỡng WCAG, ví dụ "contractor chưa từng biết brand vẫn làm đúng" | phần Anthropic; không có máy đo |
| brand-guidelines (claude-office-skills) | SKILL.md 331 dòng | không gì: mẫu mục lục chung | cả skill |
| LAB043 v3 (nội bộ) | THANG-CHAM-V3, KET-QUA-V3, GOP-Y-HA | cổng D1–D10, persona, giám khảo lỗi, casting | cần chép vào skill |
