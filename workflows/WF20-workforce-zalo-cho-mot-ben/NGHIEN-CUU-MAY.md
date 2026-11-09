# Nghiên cứu nền WF20 (bản máy cty, 9/11)

Bổ sung cho `NGHIEN-CUU.md` (bản cloud). Chi tiết nguồn: `NGOAI-MAY.md`. Code tham khảo: `D:\LINHX\WF-NC\_refs\WF20\` (10 repo, không chạy).

## Kết luận 5 dòng
1. Giữ nền LAB083 (nick phụ, `claude -p`), nhưng **cổng tag phải theo uid**: dữ liệu `mentions` có trong zca-js, chỉ CLI `zalo-agent-cli` bỏ đi khi gửi webhook.
2. **Giấy phép là chỗ chặn vòng 3**: `zalo-agent-cli` (lõi zalo-mcp của LAB083) là CC BY-NC-SA, cấm dùng thương mại. Bán cho DN khách thì phải thay bằng cầu tự viết trên zca-js (MIT), học theo hermes-zalo-plugin và zalo-agent (đều MIT).
3. Khuôn đội lấy của markus: một `doi.json` (vai, nguồn, quyền, người duyệt) + một `NORMS.md` (quy trình, cổng chất lượng, cách đếm việc xong).
4. Máy đo lấy của zalo-agent và Anthropic: 50 ca từ việc thật, chấm **hành vi** bằng máy (trả lời hay im, gọi đúng công cụ, không lọt quyền), chạy mỗi ca 3 lần, API Zalo giả.
5. Repo `skills/` chưa có skill Zalo nào. Không viết lại khung eval: dùng `lps-llm` (bước 2 và 6), chỉ thêm phần riêng cho nhóm Zalo.

## Quy trình đề xuất (vòng 1: ifAgent)
| Bước | Việc | Ai |
|---|---|---|
| 0 | Chọn bên + 5 việc đầu (trả lời lead, tra hồ sơ năng lực, soạn proposal event, báo cáo sau sự kiện, +1) | Linh |
| 1 | Bản đồ việc → `doi.json`: mỗi việc một vai, nguồn được đọc, công cụ được dùng, người duyệt; `NORMS.md` theo khuôn markus (góp ý chia phải sửa / gợi ý / đạt) | Claude |
| 2 | Bộ 50 ca `cases.jsonl` từ tin thật của đội (ẩn danh): mỗi ca có `lyDo`, người hỏi (vai), có tag hay không, hành vi mong đợi, số/giá đúng nằm ở nguồn nào | Claude |
| 3 | Vá LAB083: (a) tag theo uid, bỏ `@all`; (b) bộ lọc trước LLM theo thứ tự: tin của mình → rỗng → nhóm cần tag → người trong danh sách → công tắc tắt theo nhóm; người lạ không được ghi lịch sử; (c) đệm 20 tin + file mỗi nhóm, dồn vào ngữ cảnh khi bị tag (goclaw); (d) quyền nằm trong công cụ (hr-agent); (e) `viec.jsonl`; (f) giãn cách gửi, gửi lại "đang gõ" | agy |
| 4 | Chạy eval với API Zalo giả, mỗi ca 3 lần; Claude đọc bản ghi, không chỉ đọc điểm | agy chạy, Claude chấm |
| 5 | Nhóm thử nội bộ 2 ngày, rồi CEO ifAgent dùng 7 ngày; mỗi lỗi thật thành một ca eval mới | agy canh, Claude đọc nhật ký |
| 6 | Chấm mù + phiếu người dùng; cổng D4 | người bên đó, Linh |

## Máy đo + ngưỡng
| Đo | Cách (máy chạy được) | Ngưỡng |
|---|---|---|
| Đúng việc | 50 ca, chấm hành vi bằng code (trả lời/im, gọi/không gọi công cụ, tham số công cụ); nội dung chấm bằng rubric model + Claude đọc bản ghi | ≥ 90% (45/50) |
| Ổn định | Mỗi ca 3 lần (pass^3) | ≥ 85% ca đạt cả 3 lần |
| 0 bịa số/giá | Script lấy mọi số, giá, ngày trong câu trả lời, đối chiếu với đoạn nguồn công cụ đã trả về trong bản ghi | 0 số không có nguồn |
| Cổng tag | ≥ 12 ca: tag bot, tag người khác, `@all`, gõ tên bot không tag, trả lời tin của bot không tag, tin nhiều tag | 12/12 đúng |
| Quyền | ≥ 10 ca red team (người lạ trong nhóm, nhân viên hỏi tài liệu quản lý, lệnh cài trong file gửi lên, đòi xem nhóm khác) | 0 lọt |
| Lượt hỏng | Lượt 0 token hoặc trùng câu báo lỗi thì tính trượt (bẫy zalo-agent đã dính) | bắt buộc có |
| Tốc độ | `viec.jsonl`: giờ nhận tag → giờ gửi | p90 ≤ 2 phút |
| Nick sống | Kiểm `/ready` mỗi 5 phút, đếm lần phải quét QR lại; nhịp gửi ≥ 3 giây/tin, ≤ 20 tin/phút (số tự đặt, Zalo không công bố) | 7 ngày, 0 lần khoá |
| Việc xong | Đếm theo kiểu Intercom: xong xác nhận (người giao trả lời "ok", thả tim) và xong ngầm định (không hỏi lại trong 30 phút); hỏi lại hoặc đòi người thật thì chưa xong | đếm được theo tuần; xác nhận ≥ 60% (đề xuất, chưa có mốc ngoài) |
| Người dùng | Phiếu 1–5 sau 7 ngày + chấm mù: trộn 10 câu trả lời của agent với 10 câu của nhân viên thật, người bên đó chấm không biết nguồn | ≥ 4/5; câu agent không kém câu người > 0,5 điểm |

## Bản vàng
Xem `vang/README.md`: (1) cổng tag + đệm tin của goclaw (chỉ link, giấy phép NC); (2) bộ eval zalo-agent; (3) bộ lọc `allowlist-filter.ts`; (4) khuôn đội markus; (5) hướng dẫn agent nhóm của Microsoft Teams. Chờ Linh duyệt.

## Sửa vào skill nào, sửa gì
- **Thiếu**: chưa có skill Zalo trong `skills/`. Đề xuất tạo `bo/linhx-workforce-zalo` sau vòng 1: khuôn `doi.json` + `NORMS.md`, cổng tag, mẫu `cases.jsonl`, loại phiếu `linhx_worker` cho việc từ Zalo. Phần eval và red team trỏ về `le/lps-llm`, không chép lại.
- **Sai trong LAB083** (`D:\LINHX\LAB\LAB083-TRO-LY-ZALO\src\server\main.py`):
  - dòng 55: `TRIGGERS` mặc định `"trợ lý,bot,@"`, tin nào có chữ `@` cũng khớp.
  - dòng 462: tin có `content` không phải chữ (file, ảnh) bị bỏ hẳn.
  - dòng 762–763: tin không gọi bot được ghi nhật ký ngày **trước** khi xét người lạ (dòng 765–767), nên tin người lạ lọt vào tóm tắt tối. goclaw và zalo-agent kiểm quyền trước khi ghi.
  - dòng 449: chưa có khoá OA thì `verify_signature` cho qua; chỉ ổn khi chạy nick phụ.
  - dòng 659 + 702: vai `admin` có Bash, Chrome, `acceptEdits` từ một tin Zalo. Nhóm của khách thì không được có vai này.
- **Thừa với WF20**: tóm tắt 21:00, ghi ý tưởng, trang web câu trả lời là của chuyến đi chị Hương; tách ra, không đưa vào khuôn đội.

## Rủi ro
- Nick cá nhân có thể bị khoá: zca-js và zalo-agent-cli đều ghi rõ trong README; Zalo không công bố ngưỡng. Dự phòng: Zalo Bot chính thức (chỉ chữ, không file, không tag) hoặc OA + GMF (tốn phí).
- Giấy phép NC của zalo-agent-cli và goclaw: dùng nội bộ để học được, bán cho khách thì không.
- Webhook không có `mentions`: nếu chưa kịp dựng cầu mới, tạm dò `@<tên hiển thị nick bot>` trong chữ, nhưng Microsoft cảnh báo chữ người gửi sửa được.
- Một nhóm đông: bot chen vào chuyện người khác. Giữ chặt cổng tag, không chào từng người.

## Nguồn
- [đọc] goclaw https://github.com/nextlevelbuilder/goclaw · zalo-agent-cli https://github.com/ardennguyen/zalo-agent-cli · zca-js https://github.com/RFS-ADRENO/zca-js · zalo-agent https://github.com/vuhai2002/zalo-agent · hermes-zalo-plugin https://github.com/cuongdev/hermes-zalo-plugin · markus https://github.com/markus-global/markus · EndiorBot https://github.com/Minh-Tam-Solution/EndiorBot · hr-agent https://github.com/amxv/hr-agent · zalo-hermes-plugin https://github.com/distantguy-h/zalo-hermes-plugin · claude-zalo-skills https://github.com/duongxthanh/claude-zalo-skills
- [đọc] Microsoft Teams: "By default, agents in group chats and channels only receive messages when they're directly @mentioned." https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/conversations/channel-and-group-conversations
- [đọc] Anthropic: "20-50 simple tasks drawn from real failures is a great start." https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- [đọc] Sierra τ-bench, GPT-4o ~25% ở pass^8 τ-retail https://sierra.ai/blog/benchmarking-ai-agents
- [đọc] Intercom, resolution xác nhận / ngầm định https://www.intercom.com/help/en/articles/8205718-fin-ai-agent-resolutions
- [đọc] Viblo, Nguyen Vy: "giãn cách tối thiểu 3 giây/tin, trần 20 tin/phút" https://viblo.asia/p/kien-truc-thiet-ke-chatbot-zalo-ca-nhan-bang-ai-gemini-deepseek-khong-can-zalo-oa-tu-token-bucket-anti-ban-den-openapi-30-ym4002ko491
- [chỉ thấy] zalo-flow https://github.com/aizaloapp/zalo-flow
- [DR] đề `DR/DE-1.md`, chưa có kết quả.
