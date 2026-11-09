# Người ngoài đã làm: WF17

Cập nhật 9/11 (nghiên cứu nền). Code clone ở `_refs/WF17/` (dữ liệu, không chạy). [đọc] = đọc code/SKILL.md thật; [chỉ thấy] = chỉ thấy trang giới thiệu.

| Nguồn | Đã đọc gì | Lấy | Bỏ |
|---|---|---|---|
| ericosiu/ai-marketing-skills `podcast-ops` [đọc] https://github.com/ericosiu/ai-marketing-skills | SKILL.md + `podcast_pipeline.py` (1069 dòng) | Chia "nguyên tử nội dung" (câu trích, chuyện, số, khung, dự đoán) rồi mới sinh sản phẩm; lọc trùng giữa các tập (Jaccard 0,70 trong 30 ngày) | Điểm "viral" là giả: `final_score = base_score + bonus` rồi nhân 1,1/0,9/1,0 cho "novelty/controversy/utility" (dòng 539-547), không đo gì. Không dùng điểm này làm máy đo |
| onewave-ai/claude-skills `podcast-content-suite` [đọc] https://github.com/onewave-ai/claude-skills | SKILL.md + `component-specs.md` | Danh mục đầu ra (show notes có mốc giờ, 3-5 clip 30-60s kèm chữ trên hình, trích dẫn) | Không có bước kiểm; "Preserve the conversational tone" chỉ là lời dặn. `podcast-studio` cùng repo là khuôn rỗng |
| guia-matthieu/clawfu-skills `content-repurposer` [đọc] https://github.com/guia-matthieu/clawfu-skills | SKILL.md + `main.py` | Không lấy gì | Chỉ gọi LLM một phát sinh thread/LinkedIn/trích dẫn; không có mốc giờ, không kiểm nguồn |
| clipsai/clipsai [đọc] https://github.com/ClipsAI/clipsai | `clipfinder.py` | Cắt clip theo đổi chủ đề (TextTiling), mặc định `min_clip_duration=15`, `max=900`; cắt dọc 9:16 theo người đang nói (pyannote) | Nó chỉ tìm ranh giới chủ đề, không xếp hạng hay chấm móc câu; khoảng 15-900s quá rộng cho clip |
| SamurAIGPT/AI-Youtube-Shorts-Generator `highlights.py` [đọc] https://github.com/SamurAIGPT/AI-Youtube-Shorts-Generator | Prompt chọn highlight | Luật: "Duration sweet spot: 45-90 seconds", mở bằng móc 3 giây, "Never cut mid-sentence", clip không chồng nhau, ghi `hook_sentence` + lý do; chia khúc 20 phút gối 60s cho video dài | Điểm 0-100 do LLM tự cho, không hiệu chuẩn; phụ thuộc MuAPI |
| WyattBlue/auto-editor + `skills/` [đọc] https://github.com/WyattBlue/auto-editor | README + `skills/auto-editor/SKILL.md` | `--preview` xem trước chỗ cắt; `--margin 0.2s` chừa nhịp; cắt theo từ (`word`, `regex` trên phụ đề) | Cắt theo biên độ âm thanh không hiểu "làm lại"; `cat_record.py` của LINHX đã bù chỗ này |
| RayVentura/ShortGPT [đọc nhanh] | README | — | Là máy sinh video từ chủ đề, không phải từ buổi ghi thật |
| Podglomerate "One Episode, Ten Assets" [đọc] https://podglomerate.com/one-episode-ten-assets-your-podcast-repurposing-playbook/ | Bài blog | 2-4 clip dọc + 1-2 clip ngang/vuông; chọn 10-20 khoảnh khắc nổi bật. Trích: "A common mistake in repurposing podcast content is thinking that the same text can be copied and pasted into different formats with no changes." | — |
| The POD Edit (Podcast Studio London) [đọc] https://podcaststudiolondon.com/pod-edit/repurposing-one-episode | Bài blog | Đánh dấu khoảnh khắc đáng cắt ngay lúc dựng; làm song song chứ không tuần tự; clip 60-90s | — |
| Typeface "repurpose podcasts with AI" [đọc] https://www.typeface.ai/blog/how-to-repurpose-podcasts-with-ai-a-step-by-step-workflow | Bài blog | Trích: "Confirm every quote is attributed to the right speaker and, for guest episodes, check whether your guest agreement requires their sign-off…" → cổng khách mời | Quảng cáo công cụ |
| YouTube Help: chapters [đọc] https://support.google.com/youtube/answer/9884579 | Trang trợ giúp | Trích: "at least three timestamps listed in ascending order", "starts with 00:00", "minimum length for video chapters is 10 seconds" → máy đo chương | — |
| Lex Fridman transcript page [đọc] https://lexfridman.com/sam-altman-2-transcript | Cấu trúc trang | Mục lục chương có giờ + bản chép có giờ bấm được về đúng giây trên YouTube | — |
| tessl / skillselion / skills.cat / mcpmarket (4 link trong bản cũ) | Chỉ thấy trang bọc | Bản gốc đã thay bằng GitHub ở trên | — |
| Nguồn tiếng Việt, tiếng Trung | Tìm sơ bộ chỉ ra trang quảng cáo công cụ (Vizard, CapCut, vidio.ai); chưa có bài người làm nghề | — | Đã gửi `DR/DE-1.md` |

Chưa tìm được: bài của producer Việt Nam; quy trình Xiaoyuzhou/Bilibili. Chờ kết quả DR.
