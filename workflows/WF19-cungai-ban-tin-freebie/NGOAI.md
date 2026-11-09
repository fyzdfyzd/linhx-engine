# Người ngoài đã làm: WF19

Bước 0, tìm sơ bộ 9/11 (GitHub, trang skill, blog, mạng). **Mới tìm thấy, chưa đọc code.** Vòng 1 phải đọc code/quy trình ít nhất 3 cái tốt nhất, ghi: lấy gì, bỏ gì, so với skill LINHX đang có.

| Nguồn | Link | Đọc để |
|---|---|---|
| AIPulse | https://github.com/raghavkv85/AIPulse | bản tin AI tự động |
| techPulse | https://github.com/c7ozkan/techPulse | bản tin tech tự động |
| aigc-weekly (miantiao-me) | https://www.sourcepulse.org/projects/22137201 | bản tin tuần AIGC tiếng Trung, mẫu chạy lâu |
| Pipeline newsletter AI 2026 (dev.to) | https://dev.to/paxrel/how-to-build-an-automated-ai-newsletter-in-2026-full-pipeline-24ic | các bước đầy đủ |
| Newsletter digest agent | https://21st.dev/community/agents/serafimcloud/newsletter-digest | agent mẫu |

## Còn phải tìm ở vòng 1
- GitHub tìm theo tên skill + 'SKILL.md'; skills.sh, claudemarketplaces, openskillindex.
- Mạng: X, LinkedIn, Reddit, nhóm Facebook VN; tiếng Trung (Zhihu) khi hợp.
- Ghi kết quả đọc vào bảng dưới:

| Nguồn | Đã đọc gì | Lấy | Bỏ |
|---|---|---|---|
| AIGC Weekly (miantiao-me/aigc-weekly) | Clone, đọc `agent/.opencode/commands/weekly.md`, `agents/{editor,writer,reviewer,researcher}.md`, `skills/batch-research`; xem số Y26W44 (7/11/2026) | Khung 6 pha; "sản phẩm là trạng thái" (có tệp thì bỏ qua pha); chấm 3 trục liên quan 40 / ảnh hưởng 30 / thực dụng 30, lấy ≥70; khử trùng với RSS số cũ; reviewer PASS hoặc góp ý, tối đa 3 vòng; link neo trong chữ, không dòng "đọc thêm" | Firecrawl, Payload CMS, R2, khâu ảnh; ngưỡng 100 sao GitHub (độc giả là dev, không hợp học viên corp) |
| AIPulse (raghavkv85/AIPulse) | Clone, đọc README, `src/curator/{deduplicator,ranker,contentFilter,treatmentGenerator}.ts` | Khử trùng: LLM gom theo sự kiện, dự phòng Jaccard tiêu đề >0,6; tầng "Why It Matters" + "What You Can Build" (gần với freebie "làm thử được") | Resend email, lịch 2 số/tuần, SQLite; chấm 0–1 không mốc |
| techPulse (c7ozkan/techPulse) | Clone, đọc README, `config/editor.yaml`, `process/agents/reviewer.py` | Checklist reviewer: link giả, chữ giữ chỗ, nhãn [1][2], link YouTube bịa → thành máy đo M4 | Reviewer tự sửa HTML rồi trả lại (người soát không nên tự sửa); quét LinkedIn qua Apify |
| glebis weekly-digest (glebis/claude-skills) | Lấy `weekly-digest/SKILL.md` qua git show (repo có tên tệp Windows không nhận) | Cờ đỏ/xanh "slopiness"; chỉ kiểm 8–10 ứng viên có tên, ngày, số phiên bản, số tiền; tin top không được rác >6; fetch hỏng thì cho 5 và ghi sổ lỗi; sổ lỗi riêng | Báo cáo HTML Tufte, 5 trục ngang nhau, xuất Obsidian |
| deer-flow newsletter-generation (bytedance) | Sparse clone, đọc `skills/public/newsletter-generation/SKILL.md` | Khuôn bản tin tuần (lời mở, tin chính 2–3, tin nhanh, công cụ, kết); checklist "mỗi khẳng định có link" | Chiến lược tìm kiếm chung chung; không có máy kiểm |
| fact-check-workflow (jamditis/claude-skills-journalism) | Clone, đọc `journalism-core/skills/fact-check-workflow/SKILL.md` | Thang nội bộ Verified/False/Unverifiable; ưu tiên khẳng định theo hậu quả; nguồn gốc trước; mẫu đính chính và sổ đính chính | Bước liên hệ nguồn xin phản hồi (không cần cho bản tin tóm) |
| Paxrel dev.to | Đọc bài | Chấm 0–30 có 4 dải, lấy ≥15, tối đa 10; script kiểm đã đăng sau 30 phút | Không khử trùng, không kiểm sự thật; số chi phí là tự khai |
| 21st.dev newsletter-digest | Mở link | — | Link nay là thư viện giao diện React, không có agent; bỏ |
| The Rundown AI (6/11/2026) | Đọc một số | Khuôn tin 3 tầng "The Rundown / The details / Why it matters"; 4 tin chính + tin nhanh | Quảng cáo chen giữa; 14 tin nhanh là quá dài cho Zalo |
| TLDR AI | Đọc trang; bài phỏng vấn Dan Ni chỉ thấy qua tìm kiếm | Tóm vài câu, người viết, "viết cho người trong nghề" | Gửi mỗi ngày (cungai chỉ tuần một) |
| Zalo OA (eSMS FAQ, Nhanh.vn) | Đọc hai trang bên thứ ba | Broadcast: OA xác thực 40 tin/30 ngày, mỗi người nhận tối đa 4 tin/tháng, tối đa 5 bài/lượt, duyệt khoảng 30 phút, không thu hồi | Chưa có tài liệu chính thức Zalo → DR-1 |
| MailerLite benchmark 2025 | Đọc | Mốc mở 43,46%, giáo dục đại học 43,98%; Apple làm số mở cao hơn thật | Số email, không phải Zalo |
| Nhịp AI (blog.uncledao.com) | Chỉ mở trang chủ | Mẫu bản tin AI tiếng Việt hằng tuần, >1.000 người đăng ký | Chưa đọc số nào; vòng 1 đọc |
