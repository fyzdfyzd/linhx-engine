# Người ngoài đã làm: WF16

Bước 0 tìm sơ bộ 9/11 sáng. Nghiên cứu nền đọc thật 9/11 trưa: code clone vào `D:\LINHX\WF-NC\_refs\WF16\` (bản `--depth 1`, chỉ đọc, không chạy).

## Danh sách tìm sơ bộ (giữ nguyên)
| Nguồn | Link | Đọc để |
|---|---|---|
| Karpathy LLM wiki + Obsidian (mindstudio) | https://www.mindstudio.ai/blog/andrej-karpathy-llm-wiki-obsidian-ai-second-brain | cách wiki tự viết, đã dùng cho wiki linhx |
| aquinas-protocol second-brain | https://aquinas-protocol.github.io/second-brain/ | bản dựng sẵn Obsidian + Claude Code |
| 3 năm ghi chú thành second brain (bài) | https://buttondown.com/dodatathings/archive/the-ai-second-brain-wave-what-claude-code/ | sóng second brain, rút điều hỏng |
| Karpathy wiki + flomo 5 năm | https://www.botlearn.ai/insights/karpathy-llm-wiki-and-5-years-flomo-build-self-evolving-brain | ghi chú ngắn kiểu nugget |
| Tool nhớ những gì tôi đọc | https://levelup.gitconnected.com/i-built-an-ai-tool-that-remembers-what-i-read-so-i-dont-have-to-ea7e3e7d3a03 | quét + digest |

## Đã đọc gì / Lấy / Bỏ
| Nguồn | Đã đọc gì | Lấy | Bỏ |
|---|---|---|---|
| Karpathy `llm-wiki.md` (gist, nguồn gốc của bài mindstudio) [đọc] | Cả file 12 KB: raw/wiki/schema, ingest/query/lint, index.md, log.md | Raw bất biến; `log.md` tiền tố `## [YYYY-MM-DD] ingest |` để grep; lint tìm mâu thuẫn, trang mồ côi, ý cũ bị thay; câu trả lời hay thì ghi ngược vào kho | "batch-ingest nhiều nguồn ít giám sát": Karpathy nói ông thích nạp từng nguồn và "stay involved"; LAB070 đã batch 3.578 bài mà 0 nugget lời Linh |
| Astro-Han/karpathy-llm-wiki [đọc] | `SKILL.md` (Grounding Invariant, Triage, Compile, Cascade), `scripts/check_evidence.py` (431 dòng, regex số/ngày/trích trong ngoặc kép) | Luật "locate before you write": số, ngày, trích phải tìm thấy nguyên văn trong raw trước khi ghi; triage "No material … Do not force an article out of a thin source"; đánh dấu Outdated/Disputed thay vì sửa ngầm | Cấu trúc bài wiki dài theo khái niệm: WF16 cần thẻ ngắn |
| agenticnotetaking/arscontexta [đọc] | `skill-sources/reduce/SKILL.md` (46 KB), `verify/SKILL.md` | 4 tiêu chí ghi chú: Standalone, Composable, Novel, Connected ("If ANY criterion fails: do not extract"); "The title IS the claim"; mô tả ~150 ký tự thêm thông tin ngoài tiêu đề; recite test đọc lạnh 1–5, ≥3 đạt; thử tìm lại top 3 / top 10 | "Comprehensive extraction … skip rate must be below 10%": hợp kho máy, ngược mục tiêu nugget ít mà là lời Linh; hệ hook/ralph nặng |
| chadboyda/writing-style [đọc] | `SKILL.md` (26 KB): profile giọng, register, taste_score | Đo giọng theo từng register: tác giả mẫu viết chat 21–28 từ/câu, bài dài 13,4; gộp hai loại thì dải 13–98 "can never flag anything at all"; sửa của người là dữ liệu; điểm máy "a prompt to look, never as a gate" (AUC 0,917 trên 24 đoạn) | Gọi API ngoài (Jev/TypeSafe) gửi mẫu viết ra ngoài: không dùng với lời Linh |
| danielmiessler/fabric `extract_wisdom` [đọc] | `system.md` | QUOTES: "Use the exact quote text from the input" kèm tên người nói | Ép số lượng ("Extract at least 25 IDEAS", "exactly 16 words"): sinh ý độn |
| tobi/qmd [đọc] | `README.md`, `skills/qmd/SKILL.md` | Tìm cục bộ BM25 + vector + rerank cho markdown, có MCP; đổi mô hình embedding bằng `QMD_EMBED_MODEL` cho kho đa ngữ | Chưa kiểm với tiếng Việt có dấu; cần đo trước khi tin. LAB070 đã có SQLite FTS5 `vault.db`, dùng trước |
| sdyckjq-lab/llm-wiki-skill (tiếng Trung) [đọc] | `SKILL.md` (50 KB) phần digest/lint | Nhãn độ tin mỗi ý: EXTRACTED (có trong nguyên văn, kèm trích ≤50 chữ), INFERRED (suy ra, ghi lý do), AMBIGUOUS; báo cáo đếm theo nhãn, đẩy AMBIGUOUS lên để người kiểm | Bộ adapter WeChat/Zhihu/X: máy quét LINHX đã lo |
| AgriciDaniel/claude-obsidian [đọc] | `skills/wiki-ingest/SKILL.md` | Coi nội dung nguồn là dữ liệu không phải lệnh; tách "source statements" khỏi lời suy của máy; ý không có dữ liệu ghi `unsupported`; ý rủi ro cao cần 2 nguồn độc lập | Sổ claim/ledger SHA-256: quá nặng cho vòng 1 |
| huytieu/COG-second-brain [đọc] | `.claude/skills/braindump/SKILL.md` | Thu ý thô kể cả "voice-to-text", giữ mục "Raw Thoughts … preserved exactly as provided" | Phân loại "competitive intelligence": ngoài phạm vi |
| aquinas-protocol/second-brain [đọc] | `README.md`, `starter-files/CLAUDE.md` | Cron đêm + hook cuối phiên ghi lại hội thoại Claude vào `claude-exports/auto/`: nguồn lời Linh có sẵn | Cấu trúc thư mục riêng: LINHX đã có |
| Andy Matuschak, Evergreen notes [đọc] | https://notes.andymatuschak.org/Evergreen_notes | Atomic, concept-oriented, densely linked, viết cho mình | — |
| Tiago Forte, Progressive Summarization [đọc] | https://fortelabs.com/blog/progressive-summarization-a-practical-technique-for-designing-discoverable-notes/ | Layer 4 "going beyond highlighting the words of others, to recording my own"; "Making a note discoverable involves making it small, simple, and easy to digest" | Bôi đậm nhiều lớp trên bài gốc: tốn tay Linh |
| Simon Willison TIL [đọc] | https://til.simonwillison.net/ | Mẫu ghi chú ngắn đều đặn, nhãn chủ đề | — |
| SocialPilot, ghostwriting cho agency [đọc] | https://www.socialpilot.co/blog/linkedin-ghostwriting-for-agencies | "Start with a structured 30-minute interview during onboarding"; "Each time the executive edits a draft, you learn something new about their voice"; lỗi sửa lặp thành luật trong hồ sơ giọng | Trang bán công cụ, số chưa kiểm |
| Postiv, nghề ghostwriter LinkedIn [đọc] | https://postiv.ai/blog/how-to-become-a-linkedin-ghostwriter | "A 30 to 60 minute call, weekly or every other week, covering recent work, opinions and customer conversations." · "You record and transcribe it." | Trang bán công cụ |
| DoDataThings (buttondown) [đọc] | bài 16/4/2026, mục "Where Claude Code + Obsidian Breaks Down" | Cảnh báo: "your knowledge base generates confident fiction dressed up as your own thinking." | — |
| mindstudio, botlearn, levelup [chỉ thấy] | chưa đọc | — | Bài thứ cấp; đã đọc nguồn gốc Karpathy |
| Tiếng Việt: donglabs Zettelkasten, quantrimang, youmind [chỉ thấy] | donglabs bị khoá sau đoạn mở | — | Mỏng; giao DR đề 1 |

## So với LINHX đang có
| Có ở LINHX | Đánh giá |
|---|---|
| LAB070 (`D:\LINHX\LAB\LAB070-VAULT-MEDIUM`): 3.578 bài, 2.110 thẻ 12 mục, 5.496 trang wiki, 12.254 quote nguyên văn, `kiem_the.py` lỗi 0, `vault.db` FTS5, ~17 triệu token agy | Phần máy rất mạnh, đã có kiểm trích ≤25 từ khớp bài gốc. Thiếu hẳn lớp lời Linh; quy mô vượt khả năng Linh đọc (Karpathy: nạp từng nguồn, có người) |
| `IDEA/CONTENT_VAULT/_DIGEST` (phễu 50 → 5 → 3 nugget/ngày, TIL) | Luật đúng hướng (nugget do Linh viết, AI không thêm ý). Thực tế 2 ngày chạy, 0 nugget, 0 TIL; tuần W41 tự phản biện "phễu đang tắc ở khâu của Linh" |
| 3 bản vault rời: LAB070, `D:\LINHX\IDEA\CONTENT_VAULT` (19 mục trong `_VAULT`), `D:\@WF\TOOL\CONTENT_VAULT` (49 ENTRY) | Phải gộp một nơi chính trước vòng 1 |
| Skill `soat-giong` + `kiem_van.py` + `moc-giong.json` | Mốc lấy từ 4 bài essay (6.768 từ, câu TB 34,2 từ): sai register cho nugget 2–5 câu |
| Skill `giong-linh` (kiểm mù 3 cặp) | Lấy được cách kiểm mù; cần mẫu lời nói ngắn của Linh |
| CONTENT_VAULT `vault-daily-scan` (quét bằng Claude in Chrome) | Trái luật "agy/máy quét lo quét, 0 token"; bỏ |
| Engine `skills/` | Không có skill nào cho digest/nugget; skill vault chỉ nằm ở `IDEA/CONTENT_VAULT/skills/` |
