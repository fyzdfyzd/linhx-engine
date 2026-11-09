# WF15 · ghi chú cloud trước khi dừng (9/11 11:15 VN)

Nghiên cứu nền chuyển sang máy Linh (nhánh linhx-engine `claude/project-thread-jmaq7q`). Đây chỉ là mấy điều đã thấy trên cloud, để rà bản từ máy về, không phải NGHIEN-CUU.md.

## Đã đọc thật
- **google-labs-code/design.md** (Apache-2.0, `@google/design.md` 0.4.1): DESIGN.md = YAML token (colors, typography, rounded, spacing, components) + văn giải thích theo 8 mục cố định. CLI `lint` (tham chiếu gãy, tương phản WCAG, thiếu primary, thiếu mục, trả JSON), `diff` (phát hiện hồi quy token), `export` ra css-vars / Tailwind v3-v4 / DTCG. → Ứng viên số 1 cho máy đo "theme web + slide đọc được từ brand.json": sinh DESIGN.md từ brand.json rồi lint + export.
- **rampstackco/claude-skills `brand-style-guide`**: khung 8 mục (Story, Logo, Color, Type, Imagery, Voice, Applications, Dos/Don'ts), 7 kiểu hỏng (thiếu "chúng tôi không phải", quy tắc không ví dụ, ví dụ không quy tắc, PDF không ai mở, không lịch sử bản, quy tắc ước ao). Nguồn là file md, bản trình bày chỉ là "view". Không thấy evals riêng cho skill này (NGOAI.md ghi "có evals" cần kiểm lại).

## So nhanh với LINHX
- Khung BTMH (LAB043) đã dày hơn cả 2 nguồn trên ở phần logo/màu (số đo x, mm, đường chéo/8, thang 20–180%, 60/30/10, PHẦN 4 phương án).
- Thiếu: màu ngữ nghĩa + bảng cặp màu cho phép/cấm có tỉ lệ tương phản; thang cỡ chữ + line-height dạng token; lịch sử phiên bản; bản web của guideline.
- Hở: skill `brand-ifagent` v.v. trỏ tới `BRAND.md`, `tokens.json`, `assets/` nhưng repo linhx-engine chỉ có SKILL.md. brand.json LAB043 là lược đồ riêng, không phải DTCG/DESIGN.md.

## Đã clone (scratchpad cloud, sẽ mất): anthropics/skills, alirezarezvani, rampstackco, claude-office-skills, nexu-io/open-design (brandkit, brand-extract, design-md), jubscodes/get-shit-pretty, b1rdmania/claude-brand-skills, nextlevelbuilder/ui-ux-pro-max-skill, wesleysmits, kenneth-liao, peterhdd. Chưa đọc kỹ ngoài 2 cái trên.
