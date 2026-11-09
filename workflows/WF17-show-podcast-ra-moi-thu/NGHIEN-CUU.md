---
type: nghien-cuu
status: xong-nen-v1 (chờ DR/KQ-1 bổ sung)
created: 2026-11-09
wf: WF17-show-podcast-ra-moi-thu
---

# WF17 · Nghiên cứu nền: một buổi show ra mọi thứ

## Kết luận 5 dòng
1. Skill ngoài đã đọc (ericosiu, onewave, clawfu) đều là "đưa bản chép lời cho LLM rồi sinh thread/blog". Không cái nào có cắt video thật, kiểm chữ, hay đường về tập gốc. Điểm "viral" của ericosiu là giả: `base_score + bonus` rồi nhân 1,1/0,9/1,0 (podcast_pipeline.py dòng 539-547). Đừng mượn điểm này.
2. Phần dựng từ record của LINHX (`phim-code` nhánh B, `cat_record.py`) đã đi xa hơn các nguồn ngoài, nhưng chỉ lo **một** việc: tập dài sạch + phụ đề. Còn thiếu chọn 5 clip, mốc chương, show notes, nugget vào vault, tư liệu sách, cổng khách mời.
3. `cat_record.py` có 3 chỗ dễ làm hỏng buổi hai người: không tách người nói; `LAM_LAI` chứa "quay lại", "lại nhé" (lời bình thường cũng dính); `DEM` chứa "à", "ơ" (có thể là từ thật). Cắt nhầm lời khách là rủi ro lớn nhất.
4. Luật chọn clip dùng được, có chữ thật: 45-90 giây, mở bằng móc 3 giây, không cắt giữa câu, các clip không chồng nhau (SamurAIGPT/highlights.py); ngưỡng chương YouTube: ≥3 mốc, mốc đầu 00:00, mỗi chương ≥10 giây. Mọi thứ khác phải do Linh/Claude chấm, vì ngoài kia chưa có số liệu hiệu chuẩn.
5. Bản vàng tìm được còn ít (xem dưới). Nguồn tiếng Việt/tiếng Trung chỉ ra trang quảng cáo công cụ; đã gửi `DR/DE-1.md`.

## Quy trình đề xuất
| Bước | Việc | Ai |
|---|---|---|
| 0 | Cổng khách mời: có thoả thuận đồng ý đăng clip và trích dẫn (Typeface: "check whether your guest agreement requires their sign-off") | Linh |
| 1 | Ghi hình 45 phút, hai kênh âm riêng nếu được | Linh |
| 2 | Chép lời có giờ từng chữ (faster-whisper) + tách người nói | agy |
| 3 | Đánh dấu khoảnh khắc: 10-20 ứng viên, mỗi cái kèm giờ, câu móc, vì sao (học Podglomerate, SamurAIGPT) | Claude |
| 4 | Cắt hư/ậm ờ bằng `cat_record.py --chi-xem`, người xem `cat.json` trước khi cắt thật | agy, Linh liếc |
| 5 | Dựng tập dài + `chuong.txt` | agy |
| 6 | Chọn 5 trong 20 ứng viên (chấm mù, bảng dưới), dựng clip dọc có phụ đề | Claude chọn, agy dựng |
| 7 | Bài CafeBiz qua `viet-bai-giong-viet` (nháp của Linh, không máy viết từ đầu) + `chuyen-kenh` | Linh, Vân Anh |
| 8 | Nugget vào vault, tư liệu chương sách: mỗi mục ghi giờ + link về tập gốc | agy |
| 9 | D4: Linh duyệt ≤ 30 phút ngoài buổi ghi | Linh |

## Máy đo + ngưỡng (chạy được trước)
| # | Đo | Cách | Ngưỡng |
|---|---|---|---|
| M1 | Độ dài clip | ffprobe | 45-90 s (ngoại lệ 20-44 s phải ghi lý do) |
| M2 | Clip bắt đầu và kết thúc đúng ranh câu | so giờ clip với `words.json` | 100% |
| M3 | Phụ đề đúng | phụ đề lệch bản chép ≤ 2% từ; Linh nghe ngẫu nhiên 10 câu/clip | ≤ 1 lỗi/clip *(ngưỡng đề xuất, chưa có nguồn)* |
| M4 | Mốc chương | script: ≥3 mốc, mốc đầu 00:00, mỗi chương ≥10 s | đạt hết |
| M5 | Đường về tập gốc | mỗi clip/bài/nugget có `nguon: tập X, hh:mm:ss` | 100% |
| M6 | Lời cắt không đổi nghĩa | `cat.json`: mọi đoạn bỏ có lý do; đoạn bỏ của **khách** phải Linh xem | 0 đoạn khách bỏ mà chưa xem |
| M7 | Trích dẫn đúng người nói | đối chiếu tách người nói | 100% |
| M8 | Bài | máy đo WF06 | theo WF06 |
| M9 | Chọn clip mù | 2 giám khảo khác model chấm 20 ứng viên trên: móc 3 s, trọn ý, đứng riêng được (0-2 mỗi ô); trộn thêm 3 clip bản vàng | 5 clip chọn đều ≥5/6 và không thua bản vàng quá 1 điểm *(đề xuất)* |
| M10 | Giờ của Linh | Linh tự ghi | ≤ 30 phút ngoài buổi ghi |

## Bản vàng (còn thiếu)
- Lex Fridman: mục lục chương có giờ + bản chép bấm về đúng giây https://lexfridman.com/sam-altman-2-transcript [đọc]. Làm mốc cho chương + nugget có link ngược.
- Acquired: trang bản chép làm sản phẩm chính, không có mục lục chương (đã đọc) https://www.acquired.fm/episodes/costco. Chỉ làm mốc cho bản chép, không phải cho clip.
- **Chưa có** mốc cho clip dọc và bài. Chờ DR; Linh có thể chỉ 2-3 clip mình thấy hay.
Chưa tải được tệp mẫu vào `vang/`.

## Sửa vào skill nào, sửa gì
- `phim-code` (`scripts/cat_record.py`, `references/record.md`): thêm tách người nói; bỏ "quay lại", "lại nhé" khỏi `LAM_LAI` (hoặc chỉ tính khi đứng một mình); `DEM` bỏ "à", "ơ"; thêm cờ "đoạn bỏ của người khác Linh"; thêm bước ra `chuong.txt` kiểm M4.
- Skill mới (đề xuất tên `chon-clip` hoặc nhánh B2 trong `phim-code`): bước 3 và 6 với bảng chấm M9, luật 45-90 s, ranh câu. Mượn prompt SamurAIGPT, bỏ điểm LLM tự cho.
- `chuyen-kenh`: thêm khuôn "bài từ buổi show" có trích nguyên văn + giờ; không sửa phần còn lại.
- Phiếu `linhx_worker`: thêm loại phiếu "ghi nugget từ tập" có trường `nguon`.
- Không mượn: pipeline sinh Twitter thread/LinkedIn hàng loạt (Linh không viết kiểu đó, dễ ra văn máy).

## Rủi ro
- Cắt làm đổi nghĩa lời khách → M6.
- Whisper tiếng Việt chưa có số WER của riêng mình; cần đo trên 5 phút thật *(chưa đo)*.
- Chưa chạy với buổi ghi thật (đề nói rõ); các ngưỡng trên là đề xuất, vòng 1 hiệu chuẩn.
- Chọn clip bằng LLM dễ thiên về câu "nghe kêu"; cần Linh duyệt 5 clip.

## Nguồn
[đọc] https://github.com/ericosiu/ai-marketing-skills · https://github.com/onewave-ai/claude-skills · https://github.com/guia-matthieu/clawfu-skills · https://github.com/ClipsAI/clipsai · https://github.com/SamurAIGPT/AI-Youtube-Shorts-Generator · https://github.com/WyattBlue/auto-editor · https://podglomerate.com/one-episode-ten-assets-your-podcast-repurposing-playbook/ · https://podcaststudiolondon.com/pod-edit/repurposing-one-episode · https://www.typeface.ai/blog/how-to-repurpose-podcasts-with-ai-a-step-by-step-workflow · https://support.google.com/youtube/answer/9884579 · https://lexfridman.com/sam-altman-2-transcript · https://www.acquired.fm/episodes/costco
[chỉ thấy] castmagic, vizard, capcut, vidio.ai (trang quảng cáo)
Trong repo: `skills/bo/linhx-phim-code/skills/phim-code/{SKILL.md,references/record.md,scripts/cat_record.py}`, `chuyen-kenh`, `viet-bai-giong-viet`.
