---
type: nghien-cuu
status: ban-may
created: 2026-11-09
updated: 2026-11-09
---
# WF01 · Nghiên cứu nền (bản máy, 9/11)

Bổ sung bản cloud. Chi tiết nguồn: `NGOAI-MAY.md`. Bản vàng: `vang/VANG.md`. Đề DR: `DR/DE-1.md`.

## Kết luận 5 dòng
1. Không viết skill mới. Xương sống là `thiet-ke` nhánh landing (đã gom LAB058); quy trình D1–D4 đã khớp cách người giỏi làm. Thiếu nằm ở **máy đo**, không ở quy trình.
2. Lỗ hổng lớn nhất: `landing.md` đòi Playwright ghi `kiem/do.json`, nhưng **repo không có script nào ghi file đó**; `kiem_thiet_ke.py` chỉ đọc 360/1280 và tràn ngang. Cần một script đo thật trước vòng 1.
3. Luật đo tốt nhất bên ngoài là Vercel web-interface-guidelines (MUST/NEVER, đo được) + ngưỡng CWV của Addy Osmani; luật chống mùi AI tốt nhất là frontend-design + impeccable (đã có trong NGOAI.md).
4. Người giỏi chấm theo hai lớp tách nhau: **mắt** (Awwwards: nhiều giám khảo, bỏ điểm lệch) và **lời** (Wynter: người đúng chân dung khách đọc mù, 4 trục rõ/hợp/giá trị/khác biệt). LINHX mới có lớp mắt.
5. Đối thủ event tech (Snapbar) thắng nhờ ảnh đầu ra thật + logo khách + form 4 ô; event.ifagent.net đang thiếu đúng 3 thứ này (`NOI-DUNG-BU.md` mục 4, 5, 6), nên chặn chất lượng là nội dung, không phải giao diện.

## Quy trình đề xuất (giữ D1–D4 của `thiet-ke`, thêm chỗ in đậm)
| Bước | Việc | Ai |
|---|---|---|
| D1 | Đề bài có **tên miền đích + ngày đã xác minh**; PRODUCT.md + bảng dữ kiện (`data-assumed`); 5 trang thắng đi trọn tới form, `MAU-HINH.md`; **chụp 4 bản vàng ở 390/1280** | Claude; Chrome máy cty chụp |
| D1b | **Lời trước**: viết toàn bộ chữ trang, chạy `kiem_van.py` | Claude viết, agy không sửa lời |
| D2 | 3 hướng (Stitch hoặc HTML), **soi kế hoạch với đề + 5 cụm mặc định AI**; che tên nhánh | Claude; **Linh chọn** |
| D3 | Dựng HTML từ `tokens.css`; form ghi CRM qua engine C2 | agy |
| D4a | **Máy đo tầng 1** (script, dưới); lỗi nào cũng chặn, miễn chỉ qua `waivers.json` có lý do | agy chạy, Claude đọc `do.json` |
| D4b | Rubric: onbrand-cham + kỹ thuật /20 | agy phiên mới |
| D4c | Chấm mù mắt (3 người, trộn với 2 bản vàng) + **chấm mù lời** (5 persona LAB048 theo 4 trục Wynter) | agy mới, Gemini, ChatGPT máy cty |
| D4d | Đặt cạnh bản vàng cùng khổ; **Linh duyệt** | Linh |
| Sau | Khoá giao diện (MASTER + trang ghi đè); lịch kênh 14 ngày có utm; đếm lead ngày 14 | Claude lịch, agy dựng bài, CEO BU duyệt giọng |

## Máy đo + ngưỡng (rẻ trước, đắt sau)
**Tầng 1, script (mới, chưa có): `do_trang` Playwright → `kiem/do.json`**, khổ 1280/1024/768/390/360/320:
- Tràn ngang: `scrollWidth ≤ innerWidth` mọi khổ. Chạm: nút/link ngoài đoạn văn ≥ 44px ở ≤ 390 (Vercel: "mobile ≥44px"), cách nhau ≥ 8px. Ô nhập ≥ 16px. Chữ thân ≥ 16px. Chữ cách mép khối ≥ 8px; hai khối chữ không chạm.
- Ảnh: không ảnh rỗng (`naturalWidth = 0`), mọi `<img>` có `width/height` và `alt`. Không `user-scalable=no`. Có `prefers-reduced-motion`. Nền tối có `color-scheme: dark`.
- Form: mọi ô có nhãn và `autocomplete`; gửi thử một bản ghi giả vào CRM thử, đọc lại được; gửi rỗng thì báo lỗi cạnh ô.
- axe: 0 lỗi serious/critical. Lighthouse mobile: hiệu năng ≥ 80, truy cập ≥ 90; lab LCP ≤ 2.5s, CLS ≤ 0.1.
- Đếm mùi AI: nhãn nhỏ IN HOA trên tiêu đề = 0; "→" trong nút = 0; chữ gradient chỉ khi brand cho; số `data-assumed` liệt kê hết trong báo cáo; ảnh AI trong hero = 0 khi đã có ảnh thật.

**Tầng 2, rubric**: `onbrand-cham` ≥ 85/100; kỹ thuật /20 (impeccable) ≥ 14; ≤ 3 lỗi sửa mỗi vòng, ≤ 3 vòng.
**Tầng 3, chấm mù**: mắt ≤ 1/3 đoán AI (đã có); lời: 5 persona đọc màn đầu, trả lời "trang bán gì, cho ai, bấm đâu", đúng ≥ 4/5, mỗi trục Wynter trung bình ≥ 4/5.
**Own media**: mỗi bài có link utm (`utm_source`, `utm_medium`, `utm_campaign` bắt buộc); ≤ 3 bài/ngày, cùng kênh cùng loại cách ≥ 2 ngày; `kiem_van` dấu hiệu ≤ 2/1000 chữ; lead đếm theo `utm_campaign` ở ngày 14.

## Bản vàng
Snapbar AI Photo Booth (cấu trúc lead), Groove Jones (khối case), Stripe Sessions (trang sự kiện), Sakédemy v1.0 nội bộ (mức hoàn thiện). Chi tiết, điểm yếu: `vang/VANG.md`. Chưa có mẫu VN, chưa có ảnh chụp; chờ Linh duyệt.

## Sửa vào skill nào, sửa gì
1. `skills/le/thiet-ke/scripts/`: **thêm `do_trang` (Playwright + axe)** ghi `do.json` theo tầng 1; `kiem_thiet_ke.py --pha d4` đọc đủ 6 khổ và mọi mục, không chỉ tràn ngang.
2. `skills/le/thiet-ke/references/landing.md`: thêm luật form (nhãn, autocomplete, lỗi cạnh ô), `waivers.json`, chấm mù lời 4 trục, đặt cạnh bản vàng; khổ thêm 1024 và 320.
3. `skills/le/web-thiet-ke/SKILL.md` bước 6: đang ghi "Chụp 360 và 1280", lệch `landing.md`. Đổi thành "chạy máy đo của `thiet-ke` landing", để một chỗ giữ luật.
4. `skills/le/lps-ui/SKILL.md`: thêm vài luật Vercel đo được (ô nhập ≥ 16px, không chặn zoom, `color-scheme`).
5. `kiem_van.py` (linhx-viet-bai): thêm dấu hiệu MXH: câu mồi cuối bài, tự hỏi tự đáp, mỗi câu một dòng. (Gạch ngang dài, "không phải… mà là", emoji đã có.)
6. Lịch kênh BU: thêm vào `chuyen-kenh` hoặc skill nhỏ mới, cột Ngày, Giờ, Kênh, Loại bài, File, Link utm, Người duyệt, Trạng thái; dùng `utm_*` thay `?kenh=` (sửa `vong-1/LICH-14-NGAY.md`).
7. Khoá giao diện: dùng mẫu MASTER.md + `pages/<trang>.md` (ui-ux-pro-max), ghi băm như `.khoa` của engine. Cần Linh duyệt.

## Rủi ro
- Nội dung thật (case có số, ảnh sự kiện, logo khách được phép) chưa có: giao diện đẹp vẫn trượt chấm mù. Phải hỏi BU trước D3.
- Máy đo tầng 1 chưa tồn tại; nếu vòng 1 chạy trước khi có script, "đạt" chỉ là lời agy (memory: agy sai ~25% vẫn báo OK).
- Persona ảo chấm lời không thay được người thật; Wynter cần 12–13 người mới bão hoà. Dùng persona làm sàn, khách thật ở ngày 14.
- Snapbar, Groove Jones: số liệu đều tự khai.
- Chữ gradient của brand ifAgent nằm sát cụm mặc định AI: phải có lý do brand ghi trong `waivers.json`.

## Nguồn
- [đọc code] leonxlnx/taste-skill f6b7657 · pbakaus/impeccable 613fbf8 · anthropics/skills 2c5958e · coreyhaines31/marketingskills 96798cf · agricidaniel/claude-repurpose 669187e · vercel-labs/web-interface-guidelines 434b7f9 · vercel-labs/agent-skills 1a2c79d · addyosmani/web-quality-skills afa8da9 · nextlevelbuilder/ui-ux-pro-max-skill 4f2dbb6 (đều github.com/<tên>, bản clone ở `D:\LINHX\WF-NC\_refs\WF01\`).
- [đọc] https://www.awwwards.com/about-evaluation/ · https://www.gov.uk/service-manual/helping-people-to-use-your-service/testing-for-accessibility · https://wynter.com/post/message-testing · https://smashingmagazine.com/2023/12/five-second-testing-case-study · https://support.google.com/analytics/answer/10917952 · https://snapbar.com/ai-photo-booth · https://groovejones.com/ai-powered-photo-booth · https://stripesessions.com/ · https://laphotoparty.com/ai-brand-activation-what-generative-ai-does-at-a-live-event/ · https://www.vu.studio/blog/ai-photobooth
- [chỉ thấy] Unbounce Conversion Benchmark 2024 (trung vị 6,6% mọi ngành, theo kết quả tìm kiếm; chưa đọc báo cáo, không dùng làm ngưỡng) · advertisingvietnam.com, brandsvietnam.com (bài xu hướng photobooth).
- [nội bộ] `skills/le/thiet-ke` (SKILL, landing.md, chong-mui-ai.md, kiem_thiet_ke.py) · `skills/le/web-thiet-ke` · `skills/le/lps-ui` · `skills/bo/linhx-viet-bai/scripts/kiem_van.py` · `D:\LINHX\LAB\LAB058-WEB-DESIGN-FLOW\KHAO-SAT.md` · wiki nhánh 1xveou `trang/he-thong-nen-dung-chung.md` (h23 "Hệ kênh lấy lead", trạng thái Ý tưởng).
