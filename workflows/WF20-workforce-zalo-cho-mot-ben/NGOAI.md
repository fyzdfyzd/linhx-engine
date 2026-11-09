# Người ngoài đã làm: WF20

Bước 0 xong 9/11. Tìm GitHub (search repositories "zalo agent group", "zalo claude skill") và danh sách sơ bộ cũ; đã clone và đọc code 8 repo (bản sao ở scratchpad cloud, không để trong thư mục chung). Ba nguồn tốt nhất: **goclaw**, **zalo-agent-cli** (lõi của zalo-mcp mà LAB083 dùng), **markus**.

## Đã đọc code

| Nguồn | Đã đọc gì | Lấy | Bỏ |
|---|---|---|---|
| **goclaw** (nextlevelbuilder, CC BY-NC 4.0, Go) | `internal/channels/zalo/personal/{handlers,policy}.go`, `channels/quota.go`, `docs/11-agent-teams.md` | (1) Chỉ coi là gọi bot khi `mentions` có uid nick bot, bỏ `@all`. (2) Tin không tag vẫn ghi vào lịch sử nhóm; khi bị tag thì dồn N tin gần nhất cùng ảnh/file gửi trước đó làm ngữ cảnh rồi xoá. (3) Người/nhóm lạ nhận mã ghép cặp, chủ duyệt bằng lệnh, chống spam 60 giây. (4) Hạn mức theo người/nhóm theo giờ, ngày, tuần. (5) Đội agent: một trưởng nhận tin, mọi lần giao phải gắn mã việc trên bảng việc, xong tự đánh dấu, trưởng gộp kết quả. | Postgres, đa thuê bao, 20 nhà cung cấp mô hình: quá nặng cho một đơn vị trên máy cty. Giấy phép không thương mại: chỉ học cách làm, không chép code. |
| **zalo-agent-cli 2.5.9** (ardennguyen, CC BY-NC-SA) | `src/commands/listen.js` hàm `messageEvent`, `src/mcp/thread-filter.js` | Sự kiện webhook có `dName` (tên hiển thị). Tin đính kèm có `content` là object (`href`, `title`) cùng `msgType`. Có `fleet` nhiều tài khoản, `/ready`, `/metrics`, webhook bền (hàng đợi gửi lại). | **Webhook không gửi trường `mentions`**, nên không biết chắc ai bị tag theo uid. Phải dò `@<tên nick bot>` trong chữ. Bộ lọc trigger của nó cũng chỉ tìm từ khoá. |
| **markus** (markus-global, Apache-2.0, TS) | `templates/teams/content-team/{team.json,NORMS.md}` | Khuôn đội là một file JSON (thành viên, vai, việc khởi đầu) cộng một file NORMS.md (quy trình, cổng chất lượng mỗi chặng giao, cách nhắn nhau). Mỗi việc có người làm và người duyệt; góp ý chia "phải sửa / gợi ý / đạt"; sản phẩm đăng ký thành mục giao nộp để đếm. | Bảng điều khiển web, tự lập đội từ mục tiêu: nhân viên ifAgent chỉ ở Zalo. |
| EndiorBot (Minh Tâm Solution, MIT, TS) | `src/channels/zalo/agent-handler.ts`, `zalo-config.ts` | Gọi đích danh `@vai: việc`, sổ đội để một tag gọi nhiều vai. Trên Zalo chỉ cho đọc; việc ghi phải xác nhận hai bước ở kênh khác. | Bản Zalo của họ là OA 1-1 gửi CEO, không có nhóm; quy trình SDLC nặng. |
| hr-agent (amxv, TS) | `lib/ai/tools/team-availability.ts`, `people-search.ts`, schema | Quyền kiểm ở trong công cụ, không ở lời dặn: công cụ tự trả `permissionDenied` khi vai không đủ. Mọi bảng có cột kiểm vết. | Web Next.js + đăng nhập. |
| zalo-hermes-plugin (MIT, Python + zca-js) | `adapter.py`, `zalo-api-bridge.js` | Gửi tin có tag người (`mention_uids`) để agent nhắc đúng người giao việc. | Nối Hermes, không có vai/quyền. |
| claude-zalo-skills (SKILL.md) | `skills/creating-zalo-oa-chatbot/SKILL.md` | Mẹo token OA: refresh_token xoay vòng, sai là chết sau ~25 giờ; cửa sổ CS 48 giờ. Dùng nếu sau này chuyển sang OA. | Chỉ là gửi tin OA, không có nhóm. |
| openzosma (TS) | README, ARCHITECTURE.md | Agent phân cấp, giao việc qua WhatsApp/Slack, chạy trong sandbox. | Chưa có Zalo, cần Docker + Postgres. |

Không đọc được code: Chative (sản phẩm đóng), plugin OpenClaw Zalo OA (trùng ý goclaw), bài Moltbot (blog). Chưa thấy ai làm sẵn skill "đội agent theo vai trong nhóm Zalo thường cho một đơn vị": chỗ này còn trống.

## So với LAB083 (nền của WF20)

| Việc | LAB083 hiện có | Người ngoài làm | Vá ở vòng 1 |
|---|---|---|---|
| Biết mình được tag | `should_reply` tìm từ khoá `trợ lý, bot, @` (`src/server/main.py:524`) | goclaw so uid | Chữ `@` khớp cả khi ai tag ai, nên bot chen vào việc người khác. Chỉ nhận khi có `@<tên nick bot>` |
| Nhận file trong nhóm | `parse_event` bỏ tin có `content` không phải chữ (`main.py:461`) | goclaw tải file, gắn vào ngữ cảnh | Ghi file vào lịch sử nhóm, dùng khi bị tag |
| Ngữ cảnh nhóm | Chỉ lưu tin có tag | goclaw dồn tin không tag | Đệm 20 tin gần nhất mỗi nhóm |
| Quyền | uid trong `.env`, kiểm bằng `--tools` của `claude -p` | hr-agent kiểm trong công cụ; goclaw ghép cặp | Thêm vai `nhan_vien`; nguồn nội bộ chỉ đọc được khi người hỏi là nhân viên; người lạ trong nhóm thì im |
| Đội nhiều vai | Một persona "Nụ" | goclaw trưởng + bảng việc; markus làm + duyệt | Một nick, nhiều vai, mỗi vai một file lời dặn và nguồn riêng (cổng D2) |
| Đếm việc xong | Không | markus giao nộp; LAB116 sổ đếm | `viec.jsonl`: ai giao, vai nào, xong hay chưa, mấy phút |
| Hạn mức | Không | goclaw giờ/ngày/tuần | Trần lượt mỗi người mỗi ngày |

**Kết luận bước 0:** giữ nền LAB083 (nick phụ qua zalo-mcp, `claude -p`), vá 3 lỗ (tag, file, ngữ cảnh) theo goclaw, lấy khuôn đội JSON + NORMS + người duyệt của markus, lấy luật "quyền nằm trong công cụ" của hr-agent.
