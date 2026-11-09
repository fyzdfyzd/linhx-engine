# Người ngoài đã làm: WF18

Bước 0, tìm sơ bộ 9/11 (GitHub, trang skill, blog, mạng). Cập nhật nghiên cứu nền 9/11: đã clone và đọc 8 repo ở `_refs/WF18/` (dữ liệu, không chạy).

| Nguồn | Link | Đọc để |
|---|---|---|
| CLI mã nguồn mở xem ChatGPT có trích brand không | https://dev.to/alex-isa/i-built-an-open-source-cli-that-tells-you-if-chatgpt-cites-your-brand-and-what-to-do-about-it-31gg | so với bts.py LAB015 [chỉ thấy] |
| AEO tracker mã nguồn mở | https://dev.to/alexisa/free-open-source-aeo-tracker-our-real-score-was-33100-258i | cách chấm điểm [chỉ thấy] |
| xanlens brand visibility | https://aiproductivity.ai/news/xanlens-open-source-brand-visibility-ai-engines/ | mã nguồn mở [chỉ thấy] |
| GEO optimizer audit (GitHub Action) | https://github.com/marketplace/actions/geo-optimizer-audit | chạy định kỳ trong CI [chỉ thấy] |
| Model memory check | https://www.datadab.com/tools/model-memory-check | model nhớ gì về một tên [chỉ thấy] |
| Danh mục AI visibility tracking | https://openalternative.co/categories/business-software/marketing-customer-engagement/ai-visibility-tracking | quét thêm đối thủ [chỉ thấy] |

## Bảng đã đọc (9/11)

| Nguồn | Đã đọc gì | Lấy | Bỏ |
|---|---|---|---|
| danishashko/geo-aeo-tracker (322★, MIT) | README, `lib/scoring.ts` | Khớp tên theo từ nguyên, Unicode, tên dài thắng khi chồng; ý "ghi vị trí nhắc" | Điểm 30/+20/+15/+20/+15 tự đặt; cảm xúc bằng danh sách từ tiếng Anh, không hợp tiếng Việt, không đối chiếu sự thật |
| aichatwatch/aicw-ai-mentions | README, mẫu câu hỏi, `extract-entities.md`, `system-prompt.md` | Mẫu câu hỏi một dòng một câu có `{{SUBJECT}}`; bắt buộc mô hình kèm link nguồn và "không bịa link"; trích thực thể loại 1–4 gồm người | Không đối chiếu sự thật, không số lượt |
| nikhonit/llm-mentions-skills (MentionsAPI) | `mentions-check/SKILL.md` | Tham số `runs` 1–7 để đo biến động; trả `mentioned/rank/context/citations` mỗi mô hình | Phải trả tiền qua dịch vụ ngoài, cần khoá |
| zubair-trabzada/geo-seo-claude | `geo-brand-mentions/SKILL.md` | Điểm "uy tín thương hiệu" theo nền tảng (YouTube, Reddit, Wikipedia, LinkedIn…) với bậc điểm rõ | Số tương quan 0,737 trích từ nghiên cứu Ahrefs, tôi chưa kiểm gốc [chỉ thấy]; hướng doanh nghiệp |
| Auriti-Labs/geo-optimizer-skill | README, `SCORING_RUBRIC.md` | Chấm **trang web** có crawl/trích được không (nên dùng cho phần JSON-LD, llms.txt) | `SCORING_RUBRIC.md` là rubric chấm chính phần mềm, không liên quan |
| limelit-co/open, hellowalt/aeo-radar, elmohq/elmo | cấu trúc thư mục, README | Chỉ xác nhận cùng mô hình "hỏi nhiều AI, đếm nhắc" | Cả ba, không có gì mới hơn |
| SEJ về SparkToro/Gumshoe | bài | Dưới 1/100 lần ra cùng danh sách; cần nhiều lượt | Không có số lượt tối thiểu rõ |
| Firon (kiểm 5 bước) | bài | Trình tự hỏi tên → theo ngành → so sánh → cảm xúc → kiểm chính xác; nhãn hallucination vs outdated | Khuyến nghị schema chung chung |
| Tiếng Việt / tiếng Trung | chưa tìm được nguồn đáng đọc | | Đề DR `DR/DE-1.md` |
| Ahrefs 75k thương hiệu (12/12/2025) | https://ahrefs.com/blog/ai-brand-visibility-correlations/ | kiểm gốc số 0,737 [đọc]; chỉ cho thương hiệu, tương quan |
| SparkToro Office Hours (8/5/2026) | https://sparktoro.com/blog/office-hours-can-you-actually-track-ai-visibility/ | số lượt: 490 kết quả/lượt ≈ ±5 điểm; link nghiên cứu gốc [đọc] |
| Nguyễn Phi Vân, đính chính Go Global Holdings | https://en.nguyenphivan.com/post/setting-the-record-straight-the-facts-about-go-global-holdings | mẫu trang đính chính lỗi AI, về tổ chức [đọc] |
| LAB036 `CHUAN-ABC-v1.md`, `tu_kiem` | D:\LINHX\LAB\LAB036-BRAND-CHECK-AGENT | nhãn Nhầm đã phủ trùng tên; tự kiểm XANH [chạy] |
