# Nghiên cứu nền WF15 · Brand guideline (9/11/2026, máy Linh)

## Kết luận
1. Skill `brand-guideline-chuan` trong repo **cũ hơn** thứ Linh đã làm: nó dừng ở chuẩn 19/10 (khung 5 phần, PHẦN 4 nằm trong guideline), còn LAB043 đã có thang chấm v3 (cổng đo D1–D10, 4 persona, giám khảo lỗi, casting hệ hình, mục tiêu ≥ 7,0) và danh sách cải tiến IL-01…IL-14 (Hà chấm URAH 1/5 hôm 22/10). Việc số một là **chép v3 vào skill**, không phải đi tìm thứ mới.
2. Trong 6 nguồn ngoài đọc code, không nguồn nào có máy đo cho mỹ thuật; họ chỉ có khung nội dung. Chỗ đáng lấy là **đường máy đọc**: DESIGN.md + `lint` (tham chiếu gãy, tương phản WCAG, thiếu mục) và "seed → token dẫn xuất" của open-design. Hợp với máy đo "theme web + slide đọc được từ brand.json".
3. Khung 8 mục của rampstackco và 7 kiểu hỏng của họ nên làm **danh sách chặn nội dung** (đủ khung); khung BTMH vẫn dày hơn ở logo/màu nên giữ BTMH làm gốc.
4. Bản vàng chỉ nên là BTMH 2026 (Linh gọi "quy chuẩn cao") + NASA 1975 + NYCTA 1970; 5 bộ v3 (7,2–7,5) là mốc "đạt", chưa phải "vàng".
5. Chưa chạy `design.md lint` trên brand.json thật; đó là việc đầu của vòng 1 (nguồn chỉ là dữ liệu, tôi không chạy code lạ).

## Quy trình đề xuất
| Bước | Việc | Ai |
|---|---|---|
| 0 | Gom nguồn BU thật, lập `brand.json` | Claude |
| 1 | Cổng nội dung: đủ 5 phần khung BTMH + 8 mục rampstack (có "chúng tôi không phải") | Claude, máy |
| 2 | Casting hệ hình từ logo: 6 ứng viên, 4 khung giống nhau, giữ bản tốt nhất (thang v3 §4) | agy dựng, Claude chấm |
| 3 | Dựng cả cuốn, mockup ChatGPT (luật 7 điều ảnh của Linh) | agy, ChatGPT |
| 4 | Cổng đo D1–D10 + lint token + tương phản; trượt thì không đưa hội đồng | máy |
| 5 | Hội đồng 4 persona mù, agent mới mỗi lượt, giám khảo lỗi riêng; so cặp với BTMH hai chiều | Claude |
| 6 | PHẦN 4 tách ra `PHUONG-AN-CHON.pdf` (IL-14); guideline chính chỉ có luật đã chốt, luật tạm ghi "chốt tạm" | Claude |
| 7 | Linh chọn, rồi xuất DESIGN.md + css-vars/Tailwind từ brand.json, dựng thử 1 trang web + 1 slide | Claude, máy |

## Máy đo + ngưỡng
| Đo | Ngưỡng | Có sẵn? |
|---|---|---|
| Đủ khung (5 phần BTMH, 8 mục rampstack) | 100% mục bắt buộc | cần viết script nhỏ |
| D1–D10 (chữ ≤ 60/trang luật, trống ≥ 55%, ≤ 3 cỡ chữ, chữ ≥ 20 px, lề 1 giá trị ≥ 120 px, ≤ 1 hoạ tiết…) | không trang nào trượt D1–D4 | `do_mat_do.py` (LAB043) |
| brand.json → DESIGN.md → `lint` | 0 lỗi; mọi cặp chữ/nền ≥ 4,5:1 (ngưỡng WCAG AA của lint) | công cụ ngoài, chưa chạy |
| Theme đọc được: dựng 1 trang web + 1 slide chỉ từ token | màu dựng ra khớp token | cần viết |
| Hội đồng 4 persona (.35/.25/.20/.20), giám khảo lỗi có trần | ≥ 7,0 sau quy đổi chấm cả cuốn; lệch giữa các lượt ±0,2 nên chấm lại bằng agent mới | thang v3 (LAB043) |
| So cặp với BTMH, đảo thứ tự | không thua ≥ 2/3 lượt | quy trình casting |
| Mỗi quy tắc có số đo (x, mm, px, %) | 100% trang luật | rà bằng script |

## Bản vàng (đã lưu `vang/`)
- BTMH Guideline 2026, trang 2, 13, 21 (`vang/btmh-2026-tr*.jpg`): đầu trang PHẦN / mục / tiểu mục, cột trái ô quy tắc đánh số, cột phải hình có đường kích thước và nhãn, nhiều khoảng trống. Nguồn nội bộ Linh duyệt.
- NASA Graphics Standards Manual 1975 (Danne & Blackburn): 220 trang, 129 tấm ảnh theo [standardsmanual.com](https://standardsmanual.com/products/nasa-graphics-standards-manual) [chỉ thấy]. Học: mỗi quy tắc một trang, lưới nhất quán.
- NYCTA Graphics Standards Manual 1970 (Vignelli, Noorda, Unimark) [chỉ thấy](https://standardsmanual.com/products/nyctacompactedition). Học: hệ thống đủ chặt để cả tổ chức dùng.
- Mốc "đạt" (chưa vàng): `vang/ifagent-v3-contact-sheet.png` (7,52), `vang/sakedemy-v3-contact-sheet.png` (7,19).
- Mailchimp (giọng văn), Asana (PDF một tệp), Helsinki (khu vực công) là ví dụ [chỉ thấy] qua bài tổng hợp; chưa mở nguồn gốc, chưa dùng làm mốc.

## Sửa vào skill nào
`skills/le/brand-guideline-chuan/SKILL.md`:
- Thêm bước **cổng đo D1–D10** trước khi cho ai chấm; dẫn tới `do_mat_do.py` và `THANG-CHAM-V3.md`.
- Thay "kiểm bằng mắt ≥ 2 vòng" bằng hội đồng 4 persona mù + giám khảo lỗi, ngưỡng ≥ 7,0.
- Thêm bước casting hệ hình (6 ứng viên) và luật "vòng cuối chỉ được bỏ".
- Sửa PHẦN 4: tách khỏi guideline chính (IL-14); thêm IL-07/08 (bảng cặp màu cho/cấm kèm tỉ lệ tương phản), lịch sử phiên bản, thang cỡ chữ dạng token.
- Thêm xuất DESIGN.md + lint làm máy đo "theme đọc được".
- Cập nhật mục 6 "kiểm bằng mắt": số trang 30–45 giữ, nhưng ngân sách chữ theo D2.
Các skill `brand-ifagent`, `brand-unikon`… trỏ tới `BRAND.md`, `tokens.json`, `assets/` mà repo chỉ có SKILL.md: cần nạp tệp thật hoặc sửa đường dẫn.

## Rủi ro
- Người chấm lệch ±0,2 và hay tự khen: bắt buộc agent mới, không đọc lý giải của người dựng.
- Công cụ DESIGN.md ở phiên bản alpha, có thể đổi lược đồ.
- Ảnh hậu trường thật, ảnh sản phẩm độ phân giải cao: dựng không gỡ được (KET-QUA-V3), cần nguồn thật từ khách.
- Mockup AI hay có chữ nhoè (bài học v3); phải kiểm chữ giả theo luật ảnh của Linh.
- Nguồn quy trình agency top mới chỉ ở mức [chỉ thấy]; đã viết `DR/DE-1.md` xin Deep Research, chưa có kết quả.

## Nguồn
- [đọc] rampstackco `brand-style-guide`: https://github.com/rampstackco/claude-skills/blob/main/skills/brand-style-guide/SKILL.md . Trích: "A 200-page PDF that lives on a shared drive is dead weight."
- [đọc] google-labs-code/design.md: https://github.com/google-labs-code/design.md . Trích: "The tokens are the normative values; the prose provides context for how to apply them."
- [đọc] nexu-io/open-design (engine, brandkit, brand-extract): https://github.com/nexu-io/open-design . Trích: "Every downstream value traces back to the Seed via algorithm — nothing is hand-typed."; "Every value you emit must trace to something you **measured** on the page."
- [đọc] alirezarezvani `brand-guidelines`: https://github.com/alirezarezvani/claude-skills/tree/main/marketing-skill/skills/brand-guidelines . Trích: "brand outputs should be specific enough that a contractor who has never worked with the brand could produce on-brand work from the artifact alone."
- [đọc] anthropics/skills `brand-guidelines`: https://github.com/anthropics/skills/tree/main/skills/brand-guidelines (chỉ màu và font)
- [đọc] claude-office-skills `brand-guidelines`: https://github.com/claude-office-skills/skills/tree/main/brand-guidelines (mẫu chung, mỏng)
- [đọc] LAB043: `chuan-guideline/THANG-CHAM-V3.md`, `KET-QUA-V3-2026-10-26.md`, `GOP-Y-HA-2026-10-22.md`, `KHUNG-GUIDELINE-CHUAN.md`
- [chỉ thấy] https://standardsmanual.com/products/nasa-graphics-standards-manual ; https://standardsmanual.com/products/nyctacompactedition
