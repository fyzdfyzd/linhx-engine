# Người ngoài đã làm: WF01 · bản máy (9/11 trưa)

Bản này **bổ sung** `NGOAI.md` (bản cloud, 5 nguồn), không thay. Code clone nông vào `D:\LINHX\WF-NC\_refs\WF01\` (coi là dữ liệu, không chạy). Đọc lại 5 nguồn cũ ở bản mới nhất để trích nguyên văn, đọc thêm 4 nguồn code và 9 trang người làm nghề.

## A. Nguồn code đã đọc (9)

| # | Nguồn | Bản đọc | Lấy | Bỏ |
|---|---|---|---|---|
| 1 | leonxlnx/taste-skill (`skills/taste-skill/SKILL.md`) | f6b7657, 7/11 | Như NGOAI.md. Nguyên văn luật bịa: "Nothing is invented but a coined brand name … each marked `data-assumed`". Cổng miễn lỗi: "A FAIL you judge false is waived in `.taste-skill/waivers.json` with its reason, never fixed by gaming the check". Khổ đo: 1440/1024/820/768/390, đi bộ ở 320; nút "44px tall [tap-size] (a FAIL when another target is under 8px away)". | Như NGOAI.md. |
| 2 | pbakaus/impeccable (`.claude/skills/impeccable`) | **613fbf8, 9/11** (bản 4.8.1; NGOAI.md đọc 4b6b80f) | Rubric audit vẫn 5 mục × 0–4 = /20, dải: "18-20 Excellent … 14-17 Good … 10-13 Acceptable". Danh sách cấm trong `reference/craft-floor.md`: nhãn nhỏ trên tiêu đề ("This one is a ban, not a default"), chữ gradient, kính mờ trang trí, viền trái màu > 1px. | Lệnh launcher tải binary ngoài. Cấm chữ gradient: brand thắng. |
| 3 | anthropics/skills `frontend-design` | 2c5958e, 6/11 | Năm cụm mặc định AI (dòng 39–43). Nguyên văn bước soi: "review that plan against the brief before building … work through a similar prompt to see if you arrive somewhere similar". Hero: "a big number with a small label, supporting stats, and a gradient accent is the default treatment". | Không. |
| 4 | coreyhaines31/marketingskills `social` | 96798cf, 6/11 | Dấu hiệu văn AI (dòng 117–128): "It's not X, it's Y", chuỗi phủ định, gạch ngang dài, emoji làm gạch đầu dòng. | Tần suất theo Mỹ. |
| 5 | agricidaniel/claude-repurpose `repurpose-calendar` | 669187e, 10/4 | Cột lịch "Day, Date, Time, Platform, Content Type, File Reference, Image Needed, Notes"; "No more than 3 posts on any single day"; cùng loại bài "at least 2 days apart". | Ngày chủ đề cố định, kênh không dùng ở VN. |
| 6 | **vercel-labs/web-interface-guidelines** (`AGENTS.md`, 156 dòng) | 434b7f9, 5/10 | Bộ luật MUST/NEVER **kiểm được bằng máy**: "Hit target ≥24px (mobile ≥44px)"; "Mobile `<input>` font-size ≥16px to prevent iOS zoom"; "NEVER: Disable browser zoom"; form: "Errors inline next to fields; on submit, focus first error", "`autocomplete` + meaningful `name`"; "Honor `prefers-reduced-motion`"; "Prevent CLS (explicit image dimensions)"; "`color-scheme: dark` on `<html>` for dark themes" (ifAgent nền tối). | Phần React/hydration, virtual list (trang BU tĩnh không cần). Luật APCA thay WCAG 2: giữ WCAG 4.5:1 như lps-ui cho dễ đo. |
| 7 | vercel-labs/agent-skills `web-design-guidelines` | 1a2c79d, 27/10 | Cách chấm: tải luật mới nhất mỗi lần, ra lỗi dạng `file:line`. Áp được cho người chấm kỹ thuật của D4. | Tải luật từ mạng lúc chạy: máy cty nên chép cố định một bản. |
| 8 | **addyosmani/web-quality-skills** (`web-quality-audit`, `core-web-vitals`) | afa8da9, 24/8 | Ngưỡng CWV: LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1, đo ở "75th percentile". Luật bằng chứng: "do not claim that LCP, INP, or CLS is failing without runtime evidence"; "Keep measured findings separate from hypotheses found only in code". Lighthouse 13 đã đổi sang Performance Insights. | Phần CrUX (trang mới chưa có dữ liệu thật). SEO sâu: để WF khác. |
| 9 | **nextlevelbuilder/ui-ux-pro-max-skill** (`ui-ux-pro-max`) | 4f2dbb6, 8/11 | Mẫu "Master + Overrides": `design-system/<du-an>/MASTER.md` + `pages/<trang>.md` ghi đè, **không ghi đè Master khi chưa được phép** (`--force`). Khớp ý "khoá giao diện" của DE-XUAT-QUY-TRINH. Bảng `landing.csv`: thứ tự khối theo mẫu (vd "Hero > Problem statement > Solution overview > Testimonials carousel > CTA"). | Kho phong cách/màu gợi ý tự động (ta có brand.json). Thanh trượt variance/motion: thừa. |

Chưa đọc code, lý do: như NGOAI.md; thêm GoogleChrome/lighthouse-ci và dequelabs/axe-core là công cụ đo, dùng thẳng, không cần đọc mã.

## B. Người làm nghề: quy trình và tiêu chí chấm (đã đọc trang)

| Nguồn | Lấy |
|---|---|
| Awwwards, cách chấm ([link](https://www.awwwards.com/about-evaluation/)) | Trọng số: Design 40%, Usability 30%, Creativity 20%, Content 10%; ban giám khảo ≥ 18 người, "the 3 jury scores furthest from the average are automatically eliminated". Lấy: **nhiều người chấm, bỏ điểm lệch**, trọng số cho rubric mắt. |
| GOV.UK Service Manual, kiểm truy cập ([link](https://www.gov.uk/service-manual/helping-people-to-use-your-service/testing-for-accessibility)) | "you'll miss some issues if you only do automated testing." Lấy: axe chỉ là sàn; thêm kiểm tay bàn phím, nhãn form, alt. |
| Wynter, kiểm thông điệp B2B ([link](https://wynter.com/post/message-testing)) | Bốn trục: rõ, hợp, giá trị, khác biệt; câu hỏi mở "What do you think this message is trying to say?"; "it takes 12-13 responses to reach saturation". Lấy: **chấm mù lời trên trang** bằng người đúng chân dung khách, tách khỏi chấm mắt. |
| Smashing Magazine, thử 5 giây ([link](https://smashingmagazine.com/2023/12/five-second-testing-case-study)) | Thời gian xem tuỳ độ phức tạp (khoảng 2–10 giây); 5 giây là quy ước ít bằng chứng; trang nhiều mục đích phải thử dùng đầy đủ. Lấy: giữ "đọc 5 giây" nhưng hỏi 3 câu cố định, không dùng làm cổng duy nhất. |
| Google Analytics, tham số UTM ([link](https://support.google.com/analytics/answer/10917952)) | "you should always use utm_source, utm_medium, and utm_campaign." Lấy: link đo dùng **utm_*** chuẩn thay `?kenh=` tự đặt. |
| Snapbar, trang AI photo booth ([link](https://snapbar.com/ai-photo-booth)) | Đối thủ gần nhất của event.ifagent.net. Xem `vang/VANG.md`. |
| Groove Jones ([link](https://groovejones.com/ai-powered-photo-booth)) | Case gắn tên nhãn hàng (SC Johnson, Keebler, PepsiCo) nhưng không có số. |
| LA Photo Party ([link](https://laphotoparty.com/ai-brand-activation-what-generative-ai-does-at-a-live-event/)) | Một con số cụ thể: tạo ảnh "in under four seconds"; còn lại là lời tự khen không số. Làm mốc "đừng làm thế". |
| Stripe Sessions ([link](https://stripesessions.com/)) | Trang sự kiện: một nút "Register" lặp, chương trình, giá, diễn giả, FAQ hoàn tiền rõ. |
| vu.studio blog ([link](https://www.vu.studio/blog/ai-photobooth)) | Chỉ là bài blog, không số. Bỏ. |
| Tìm nguồn VN (Advertising Vietnam, Brands Vietnam, Trang Vàng) | Chưa thấy bên VN nào làm trang AI activation đáng làm mốc; chỉ có cho thuê photobooth thường. Đưa vào DR/DE-1. |

## C. Sửa lại nhận định của NGOAI.md
1. NGOAI.md ghi "soat-giong thiếu bản tiếng Việt của danh sách dấu hiệu văn AI": **chưa đúng**. `skills/bo/linhx-viet-bai/scripts/kiem_van.py` đã có AP-03 "không phải… mà là", gạch ngang dài, AP-20 emoji. Còn thiếu cho bài MXH: câu mồi cuối bài ("Bạn nghĩ sao?"), tự hỏi tự đáp, mỗi câu một dòng.
2. `thiet-ke/references/landing.md` đã có 360/390/768/1280, Lighthouse ≥ 80/≥ 90, axe, đọc 5 giây, đi trọn tới form. **Nhưng trong repo không có script nào ghi `kiem/do.json`**: `kiem_thiet_ke.py` chỉ đọc file đó và chỉ xét 360, 1280, tràn ngang. Đây là lỗ hổng máy đo lớn nhất.
3. `cro/references/form.md` (marketingskills) ghi số "4-6 fields: 10-25% reduction" là "Rule of thumb", không có nguồn: không dùng làm ngưỡng.
