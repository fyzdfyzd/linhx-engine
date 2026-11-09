# LINHX Agent Force · lõi workforce trao tay

Một workforce là **một thư mục** của một đơn vị. Trong đó có: dữ liệu nền thành wiki, công nhân số có người chịu trách nhiệm, skill và workflow có phiên bản, bảng việc với mỗi việc một thư mục, danh sách điều cần nhớ và điều cần học. Công cụ duy nhất là `af.py`, chỉ dùng Python stdlib. Zip thư mục này lại thì Claude, agy hay ChatGPT đều chạy được: agent đọc `AGENTS.md` (Claude đọc qua `CLAUDE.md`, Gemini qua `GEMINI.md`).

```
          SETUP (một lần, bổ sung khi cần)
  D0 7 câu → 01-nguon → 02-wiki (su-that.json) → to-chuc.json → skill từ kho LINHX → workflow → kiem DAT
                                   │
                                   ▼
  ┌──────────── RUNNING ────────────┐      Zalo / Telegram / email
  │ /giao → viec/LX-0001/ (TASK.md,  │◀──── af.py lenh (quyền kiểm trong code)
  │ dau-vao, dau-ra, nhat-ky)        │────▶ hop-thu/ra.jsonl → bộ chuyển gửi
  │ cho → dang_lam → cho_duyet ──┐   │      server mỏng: af.py may-chu (token)
  │   cổng chống slop ┘  xong / tra_lai
  └──────────────┬──────────────────┘
                 │ mọi phản hồi (trả lại, /gopy, duyệt có lời khen)
                 ▼
  LEARNING: HOC.jsonl, mỗi bài học một dòng gắn đích (skill / workflow / công nhân / hệ thống),
            đếm ủng hộ và phản đối; ý trùng thì cộng dồn; việc mới tự chép bài học đang áp vào TASK.md
                 │ af.py hoc (cuối ngày): ≥ 2 bằng chứng từ ≥ 2 việc → đề xuất; bị phản đối nhiều → tỉa
                 ▼
  UPDATE:   de-xuat/DX-001/moi/ (bản sửa nhỏ nhất) + ket-qua-thu.json (bản mới so với bản cũ, người chấm khác thợ)
            → af.py thang-cap --duyet <chủ|quản lý> → v1.0.0 → v1.1.0, bản cũ lưu ở phat-hanh/ban/
            → af.py lui nếu bản mới kém → quay lại RUNNING
```

## Lấy từ đâu (đã đọc code; chi tiết ở WF-CHUAN/WF20/loi-agent-force/)
| Mảnh | Nguồn |
|---|---|
| Gói markdown làm gốc, mỗi vai `ROLE/POLICIES/HEARTBEAT.md`, `reportsTo` | Paperclip companies-spec (MIT), markus templates (Apache-2.0) |
| FSM việc có người duyệt bắt buộc, `vong` tăng mỗi lần trả lại, mỗi việc một thư mục | markus task, Paperclip execution workspace |
| Bài học dạng bullet có đếm, chỉ thêm hoặc vá, tỉa bài học hại | ACE (Generator/Reflector/Curator) |
| Điều kiện chưng cất, skill nháp chờ duyệt, thống kê đạt lần đầu | markus learning-loop |
| Phiên bản bất biến + con trỏ `production`, lùi bằng trỏ về | Langfuse prompt/skill versioning |
| Thăng cấp chỉ khi so với snapshot bản cũ, người chấm tách thợ | anthropics/skills skill-creator |
| Trần 2.200 ký tự cho điều cần nhớ | Hermes memory |
| `.agents/skills/<ten>/SKILL.md`, `AGENTS.md` | chuẩn Agent Skills + agents.md (Codex, Antigravity, Gemini CLI, Hermes đọc chung) |
| Router theo câu ví dụ, onboard 7 câu, untrusted-content, absent-is-not-zero, tenant-scope | anthropics/knowledge-work-plugins |
| Một nick một listen, hub nhóm → thư mục | LAB116 hub trên máy cty (đang chạy) |

## Lệnh
```
python workforce/af.py moi <W> --ten "Nụ Event" --don-vi "ifAgent Event" --kho skills --skills brand-ifagent,linhx-chuan
python workforce/af.py nap-skill workforce/mau/ifagent-event --kho skills   # mẫu trong repo không kèm skill
python workforce/af.py kiem <W>
python workforce/af.py lenh <W> --tu sales "/giao tra-loi-lead Agency hỏi booth 300 khách"
python workforce/af.py chuyen <W> LX-0001 cho_duyet
python workforce/af.py lenh <W> --tu hang "/tra LX-0001 thiếu timeline"
python workforce/af.py hoc <W>
python workforce/af.py thang-cap <W> DX-001 --duyet linh
python workforce/af.py dong-goi <W> goi.zip --mot-file GOI.md
AF_TOKEN=... python workforce/af.py may-chu <W> --cong 8120
```
Lệnh chat: `/giao <workflow> <việc>`, `/gopy <LX-…|đích> <góp ý>`, `/duyet LX-… [lời khen]`, `/tra LX-… <lý do>`, `/bang`, `/nho`, `/help`. Người lạ thì im; nhân viên không duyệt được.

## Nối kênh (mỏng)
Lõi không gọi mạng. Bên trả lời nhóm của hub LAB116 (`tra-loi-nhom.mjs`) gọi `af.py lenh` khi tin bắt đầu bằng `/`, và đọc `hop-thu/ra.jsonl` để gửi vào `gui-di.jsonl`. Email: bộ chuyển đọc cùng file đó. Khuôn dạng `gui-di.jsonl` của hub phải đối chiếu trên máy cty trước khi nối.

## Chạy ở đâu
- **Claude Code / agy / Codex**: giải nén, mở thư mục, agent tự đọc `AGENTS.md`.
- **ChatGPT project, Gemini Gem**: chưa nhận zip đầy đủ. Dùng `--mot-file GOI.md` (hiến chương, tổ chức, workflow, skill, nhớ, học trong một file), còn bảng việc giữ ở máy.
- **Gemini Task / sandbox code**: theo tài liệu thì không có mạng, không cài thư viện được, mỗi lần chạy tối đa 30 giây. `af.py` hợp với các giới hạn đó (chỉ stdlib, mỗi lệnh chạy dưới 1 giây). Việc giải nén zip trong sandbox **chưa thử thật**.

## Thử
`python -m pytest tests/workforce -q`: 18 ca, phủ trọn vòng setup → giao → cổng chống slop → trả lại thành bài học → đề xuất → chặn thăng cấp khi thiếu thử/quyền/người chấm → thăng cấp → lùi → quyền lệnh chat → kiểm bí mật và vòng báo cáo → đóng gói, giải nén ở chỗ khác vẫn chạy → mẫu ifAgent Event DAT.
