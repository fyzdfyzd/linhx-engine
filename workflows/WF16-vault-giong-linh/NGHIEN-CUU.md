# Nghiên cứu nền WF16 · Vault giọng Linh

9/11/2026. Đọc thật 10 repo + 6 trang web; code ở `D:\LINHX\WF-NC\_refs\WF16\` (chỉ đọc, không chạy). Bảng chi tiết: `NGOAI.md`. Bản vàng: `vang/DANH-SACH-VANG.md`. Đề DR: `DR/DE-1.md`.

## Kết luận 5 dòng
1. Phần máy đã có và mạnh: LAB070 lấy 3.578 bài, ra 2.110 thẻ, 12.254 câu trích có máy kiểm khớp bài gốc. Nhưng nugget bằng lời Linh vẫn là 0 (`_DIGEST/nuggets/` chỉ có template).
2. Chỗ tắc là đầu vào lời Linh, không phải quét hay digest. Đơn vị top (ghostwriter cho CEO) lấy giọng bằng **phỏng vấn ghi âm 30–60 phút mỗi tuần**, rồi cắt ý từ bản chép. Họ không bắt khách tự viết.
3. Nugget "giọng Linh" phải có câu gốc Linh đã nói hoặc viết, kèm nhãn nguồn từng câu (kiểu EXTRACTED/INFERRED). AI viết thay rồi gọi là giọng Linh thì đúng cái bẫy "confident fiction dressed up as your own thinking".
4. Máy đo giọng hiện có (`moc-giong.json`) lấy từ 4 bài essay. Đem đo nugget 2–5 câu là sai register. Cần mốc riêng từ lời nói ngắn của Linh.
5. Ngưỡng "≥ 20 nugget/tuần/chủ đề" (80/tuần) chưa khả thi khi thực tế là 0. Đề xuất tách đôi: máy ≥ 20 thẻ có nguồn/tuần/chủ đề; nugget lời Linh ≥ 5/tuần/chủ đề, nâng dần khi 2 tuần liền đạt. Linh chốt ở D2.

## Quy trình đề xuất
| Bước | Việc | Ai | Đầu ra |
|---|---|---|---|
| 0 | Gộp 3 bản vault rời (LAB070, `IDEA/CONTENT_VAULT`, `D:\@WF\TOOL\CONTENT_VAULT`) về một nơi chính; raw bất biến | agy, Claude duyệt | một `INDEX.md`, một `LOG.md` |
| 1 | Quét theo 4 chủ đề, lấy toàn văn, chống trùng | máy quét (mayquet, 0 token) | bài sạch trong raw |
| 2 | Lọc + thẻ DG ngắn (3 dòng, không phải 12 mục), mỗi thẻ 1–2 câu trích nguyên văn ≤ 25 từ; chọn ⭐ 8–10 thẻ/chủ đề/tuần | agy | `daily/`, `queue` |
| 3 | Claude soạn 5–8 câu hỏi từ thẻ ⭐ ("anh đồng ý hay cãi câu này? ở DN Việt đã thấy chưa?") | Claude | phiếu phỏng vấn |
| 4 | Linh trả lời bằng ghi âm hoặc nhắn vội 15–20 phút/chủ đề/tuần; giữ bản chép nguyên văn | Linh | `raw/loi-linh/YYYY-MM-DD.md` |
| 5 | Cắt bản chép thành nugget: tiêu đề là một mệnh đề; 2–5 câu dùng chữ của Linh, chỉ cắt và sửa chính tả, chỗ thiếu ghi `[?]`; mỗi câu gắn nhãn `LINH` (có trong bản chép) hoặc `NGUON` (có trong bài, kèm link) | agy | `nuggets/NG-…md` |
| 6 | Máy đo M1–M4 dưới đây; trượt thì trả agy, tối đa 2 vòng | máy, rồi Claude | phiếu chấm |
| 7 | Linh duyệt (D4); 10 nugget đầu thành bản vàng; mỗi chỗ Linh sửa ghi một dòng vào hồ sơ giọng ngắn (luật có ≥ 2 bằng chứng mới vào skill) | Linh, Claude ghi | `vang/`, `BAI-HOC.md` |
| 8 | Lint tuần: trùng ý, mâu thuẫn (đánh dấu, không sửa ngầm), nugget mồ côi; dựng lại chỉ mục tìm | máy + agy | `weekly/` |

## Máy đo + ngưỡng (rẻ tới đắt)
| Mã | Đo gì | Cách | Ngưỡng đạt |
|---|---|---|---|
| M1 | Nguồn sống + trích nguyên văn | Script 0 token: link trả 200 hoặc có trong kho đã quét; mọi chuỗi trong ngoặc kép và mọi số ≥ 2 chữ số tìm thấy nguyên văn trong bài sạch (gộp logic `LAB070/src/kiem_the.py` và `check_evidence.py` của Astro-Han); đủ frontmatter | 100% nugget, 0 lỗi |
| M2 | Lời Linh thật | Script: mỗi câu nhãn `LINH` phải khớp mờ (≥ 0,8 theo tỉ lệ từ chung) một đoạn trong bản chép lời Linh có ngày | ≥ 1 câu `LINH`/nugget; 0 câu không nhãn |
| M3 | Tìm lại ≤ 1 phút | Trước mỗi tuần, Claude viết che 20 câu hỏi/chủ đề theo lời Linh; tìm trên `vault.db` FTS5 (sau thử qmd); thêm recite test của arscontexta: chỉ đọc tiêu đề + mô tả, đoán nội dung, chấm 1–5 | nugget đúng nằm top 3 ở ≥ 80% câu; recite ≥ 3 ở ≥ 90% nugget |
| M4 | Giọng Linh | Mốc mới từ ≥ 30 đoạn lời Linh ngắn (nhắn vội, ghi âm, chat Claude); chấm mù: trộn 5 nugget đã duyệt + 5 câu Linh gốc, agent khác đoán đâu là gốc | đoán đúng ≤ 60%; Linh sửa ≤ 20% chữ khi duyệt |
| M5 | Nhịp | Đếm trong `INDEX.md` | thẻ máy ≥ 20/tuần/chủ đề; nugget Linh duyệt ≥ 5/tuần/chủ đề (đề xuất, chờ D2) |
Điểm máy (M4) chỉ để nhìn lại, không thay Linh: writing-style tự ghi điểm của nó là "a prompt to look, never as a gate".

## Bản vàng
Năm mốc ở `vang/DANH-SACH-VANG.md`: Evergreen notes (Matuschak), TIL (Simon Willison, 583 mục), LLM Wiki (Karpathy), karpathy-llm-wiki (Grounding Invariant), arscontexta verify (recite). Bản vàng giọng Linh thật: 10 nugget đầu Linh duyệt ở vòng 1.

## Sửa vào skill nào, sửa gì
- **Thiếu skill trong engine**: `linhx-engine/skills/` không có skill digest/nugget. Đưa `IDEA/CONTENT_VAULT/_DIGEST/AGENTS_DIGEST.md` thành một skill `tieu-hoa-vault` (không tạo bản thứ hai nếu Linh muốn sửa thẳng file luật cũ). Thêm bước 3–5 (phỏng vấn, cắt bản chép, nhãn từng câu), M1–M5, triage "không có gì mới thì không ép ra nugget" (Astro-Han).
- **`soat-giong`**: thêm mục "register": không chấm nugget bằng `moc-giong.json` essay; thêm `moc-giong-ngan.json` từ lời nói ngắn. Bài học từ writing-style: gộp hai register thì máy "can never flag anything at all".
- **`giong-linh`**: kiểm mù hiện dùng đoạn essay; thêm biến thể cho nugget (M4).
- **LAB070 `kiem_the.py`**: tái dùng làm M1; bỏ thẻ 12 mục cho lớp nugget (quá dài, 47.463 từ cho 25 thẻ ở mẻ `ai-001`).
- **`vault-daily-scan` (CONTENT_VAULT)**: bỏ phần quét bằng Claude in Chrome, chuyển cho mayquet/agy.
- Hồ sơ giọng học từ bản sửa: nối `hoc-tu-ban-sua` (đã có trong `linhx-viet-bai`).

## Rủi ro
- Linh không có 15–20 phút/chủ đề/tuần: hạ còn 1 chủ đề/tuần xoay vòng; dùng lời Linh đã có (chat Claude, nhắn Zalo cho agent) làm nguồn trước.
- Nugget AI viết "na ná" Linh lọt qua: chặn bằng M2 (câu phải khớp bản chép), không bằng cảm giác.
- Ghi âm là dữ liệu riêng tư: lưu cục bộ, không gửi API chấm giọng bên ngoài (writing-style gửi mẫu cho TypeSafe).
- Tìm tiếng Việt có dấu: FTS5 và qmd chưa đo với tiếng Việt; M3 vòng 1 phải đo trước khi chọn công cụ.
- Ba vault rời gộp sai thì mất lịch sử: gộp bằng chép, không xoá (luật số 5 AGENTS.md).

## Nguồn
- Karpathy, llm-wiki.md: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f [đọc]
- Astro-Han/karpathy-llm-wiki: https://github.com/Astro-Han/karpathy-llm-wiki [đọc]
- agenticnotetaking/arscontexta: https://github.com/agenticnotetaking/arscontexta [đọc]
- chadboyda/writing-style: https://github.com/chadboyda/writing-style [đọc]
- danielmiessler/fabric (extract_wisdom): https://github.com/danielmiessler/fabric [đọc]
- tobi/qmd: https://github.com/tobi/qmd [đọc]
- sdyckjq-lab/llm-wiki-skill: https://github.com/sdyckjq-lab/llm-wiki-skill [đọc]
- AgriciDaniel/claude-obsidian: https://github.com/AgriciDaniel/claude-obsidian [đọc]
- huytieu/COG-second-brain: https://github.com/huytieu/COG-second-brain [đọc]
- aquinas-protocol/second-brain: https://github.com/aquinas-protocol/second-brain [đọc]
- coreyhaines31/makerskills: https://github.com/coreyhaines31/makerskills [chỉ thấy, đã clone, chưa đọc]
- Matuschak, Evergreen notes: https://notes.andymatuschak.org/Evergreen_notes [đọc]
- Forte, Progressive Summarization: https://fortelabs.com/blog/progressive-summarization-a-practical-technique-for-designing-discoverable-notes/ [đọc]
- Simon Willison TIL: https://til.simonwillison.net/ [đọc]
- SocialPilot: https://www.socialpilot.co/blog/linkedin-ghostwriting-for-agencies [đọc]
- Postiv: https://postiv.ai/blog/how-to-become-a-linkedin-ghostwriter [đọc]
- DoDataThings, 16/4/2026: https://buttondown.com/dodatathings/archive/the-ai-second-brain-wave-what-claude-code/ [đọc]
- Tiếng Việt: https://donglabs.substack.com/p/zettelkasten-phuong-phap-ghi-chep [chỉ thấy, bị khoá]
- Nội bộ: `D:\LINHX\LAB\LAB070-VAULT-MEDIUM\OVERVIEW.md`, `D:\LINHX\IDEA\CONTENT_VAULT\_DIGEST\` (AGENTS_DIGEST, weekly/2026-W41), `skills/bo/linhx-viet-bai/` (giong-linh, soat-giong, du-lieu/moc-giong.json), wiki `trang/he-thong-linhx-personal-brand.md` mục h18 (nhánh `claude/project-thread-1xveou`) [đọc]
- [DR] chưa có kết quả; đề ở `DR/DE-1.md`.
