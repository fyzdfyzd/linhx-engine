# LINHX: luật chung cho agent

Đây là "bộ não thứ 2" của Đinh Trần Tuấn Linh. Mọi agent (Claude, Antigravity…) đọc file này trước.
**Bản chính là `D:\LINHX` trên máy Linh.** Bản trên dự án Claude web chỉ là bản sao; khi khác nhau, bản trên máy thắng.
Trả lời và viết note bằng **tiếng Việt có dấu**, câu ngắn, rõ.

## Bản đồ
| Thư mục | Dùng cho | Luật riêng |
|---|---|---|
| `00-INBOX/` | Ghi vội của Linh | `00-INBOX/AGENTS.md` |
| `LAB/` | Ý tưởng + thử nhanh: "làm được không?" | `LAB/README.md`, `LAB/INDEX.md` |
| `PROTOTYPE/` | Bản mẫu cho người dùng thật: "có nên làm thật không?" | `PROTOTYPE/AGENTS.md` |
| `PRJ/` | Dự án cho các BU | `PRJ/.agents/` (Antigravity) |
| `EDU/` | Lớp học, bài giảng | — |
| `IDEA/` | **3 vault nạp tri thức**: SIGNAL_VAULT (vấn đề & tín hiệu), IDEA_VAULT (ý tưởng), CONTENT_VAULT (+ lớp `_DIGEST` đọc hằng ngày) | `IDEA/README_3_VAULT.md`, rồi `AGENTS.md` của từng vault |
| `LINHX-OPC/` | Công ty một người chạy bằng agent | `LINHX-OPC/README.md`, `QUY-CHUAN-OPC.md` |
| `PLAN/` | Hệ thống **LINHX plan daily** (xem dưới) | — |
| `KB/` | Kho kiến thức (raw → wiki) | `KB/AGENTS.md` |
| `ARCHIVE/` | Đã xong / bỏ | — |
| `_system/` | Template, skill, script | — |
| `SKILLS/` | Thư viện bản sao mọi skill/plugin của Linh (lab, claude.ai) để agy và Claude đọc, học | `SKILLS/INDEX.md` |

Luật riêng của một thư mục **thắng** luật gốc này khi khác nhau.

## PLAN và LINHX plan daily: không đụng
- Quản trị bản thân, kế hoạch ngày/tuần/tháng chạy theo **LINHX plan daily**: nền là `PLAN/00_BASELINE_LINHX_MASTER_PLAN.md` (lớp A → B → C → D), nhịp và file ngày theo `D:\@WF\WIKI\LINHX_OPERATING_SYSTEM.md` (`WIKI/daily/YYYY-MM-DD.md`, `NOW.md`, `CLUSTER_DASHBOARD.md`).
- Bộ não thứ 2 này **không tạo** file kế hoạch ngày/tuần/tháng, không tạo mục tiêu riêng, không sửa gì trong `PLAN/` hay `D:\@WF\WIKI\`.
- Chỉ **đọc** PLAN khi cần biết ưu tiên. Ghi vào PLAN chỉ khi đang chạy đúng quy trình plan daily hoặc Linh yêu cầu rõ.
- Kết quả "rà soát kho" (skill `ra-soat-kho`) là **đầu vào** cho buổi Weekly Planning thứ 2 của plan daily, không phải một kế hoạch thay thế.

## Luật ghi (quan trọng nhất)
1. **Đọc INDEX trước**, không quét cả cây thư mục.
2. Chỉ ghi trong thư mục của mục đang làm, cộng **một dòng** trong `INDEX.md` của khu vực.
3. **Không sửa** nội dung trong `00-INBOX/` và `KB/raw/`. Chỉ thêm dấu "đã xử lý" ở cuối file INBOX.
4. `LOG.md` chỉ **thêm ở cuối**, ghi giờ, không sửa dòng cũ.
5. **Không xoá**. Chuyển vào `ARCHIVE/` (hoặc `_archive/` của khu đó).
6. **Không ghi bí mật** (mật khẩu, API key, token, số tài khoản, danh sách học viên chi tiết). Chỉ ghi "nằm ở đâu".
7. Tạo note mới **từ template** trong `_system/templates/`, giữ đủ frontmatter.
8. Khi không chắc đặt file ở đâu: ghi vào `00-INBOX/` và hỏi Linh.

## Quy ước tên
- Tên thư mục = **mã khu + số 3 chữ số + VIẾT-TẮT**: `LAB004-CLAUDE-AGY`, `PRT001-ZALO-BOT`, `PRJ001-VCB-AI`, `EDU001-VCB-BGL`, `OPC001-CHIEMTINH-VN`.
  - Số tiếp theo lấy từ `INDEX.md` của khu (tính cả `_archive/`), không dùng lại số cũ.
  - Viết tắt 1–3 cụm, IN HOA, không dấu, gạch ngang, ≤ 16 ký tự. Ưu tiên đơn vị/BU + chủ đề.
  - Chuyển khu thì nhận mã mới, **giữ nguyên viết tắt** (`LAB005-ZALO-BOT` → `PRT001-ZALO-BOT`).
  - Ngày không nằm trong tên; ghi ở frontmatter `created` và trong INDEX.
- Liên kết bằng wikilink theo mã: `[[LAB006-GAME-3D]]`. Liên kết **hai chiều**: khi PRT nhắc LAB gốc thì LAB cũng nhắc PRT.
- Frontmatter: `type`, `status`, `created`, `updated`. Ngày dạng `YYYY-MM-DD`.

## Trạng thái
- LAB: theo `LAB/README.md` (`IDEA` `TESTING` `WORKS` `PARTIAL` `FAILED` `PARKED` `PROMOTED`). `PROMOTED` = đã lên PROTOTYPE.
- PROTOTYPE: `BUILDING` `USER-TEST` `VALIDATED` `KILLED` `PARKED` `HANDOFF`

## Lệnh ngắn Linh hay dùng
| Linh nói | Làm |
|---|---|
| `ghi inbox: …` | Thêm một dòng có giờ vào `00-INBOX/INBOX-YYYY-MM-DD.md` |
| `LAB mới: …` | Skill `lab-moi` |
| `viết overview` | Skill `viet-overview` |
| `lên prototype: LAB…` | Skill `proto-moi` |
| `rà soát kho` | Skill `ra-soat-kho` (đầu vào cho Weekly Planning của plan daily) |
| `tín hiệu: …` · `vấn đề: …` · `ai đã giải: V-…` | `IDEA/SIGNAL_VAULT/AGENTS.md` |
| `ý tưởng: …` | `IDEA/IDEA_VAULT/AGENTS.md` |
| `đọc: <link>` · `tiêu hóa: …` | `IDEA/CONTENT_VAULT/_DIGEST/AGENTS_DIGEST.md` |
| `rà vault` | Lint 3 vault (`IDEA/README_3_VAULT.md`) |

## Vai trò & Lưu vết bắt buộc (`.handoff/`)
- **Claude** là **quản lý & giám sát chất lượng**: lập kế hoạch thí nghiệm, viết đề (`DE-BAI.md` / `tasks/T-NNN.md`), giám sát và review sau mỗi bước của Antigravity, viết overview.
- **Antigravity** là **worker thực thi**: tuân thủ `D:\LINHX\GEMINI.md` (và plugin toàn cục `linhx-tracking`), **luôn lưu vết xuống ổ cứng trong `.handoff/` ở mọi dự án** để Claude đọc:
  1. `.handoff/BANG.md`: trạng thái các đề `T-NNN` và các phiên làm việc trực tiếp `S-YYYYMMDD-HHMM-<slug>`.
  2. `.handoff/VAN-DE.md`: sổ vấn đề, lỗi lặp lại, lệch spec/kiến trúc, giả định tạm, hoặc điểm `BLOCKED` chờ Claude/Linh.
  3. `.handoff/logs/<MA>-YYYYMMDD-HHMM.md`: tracklog thời gian thực (append-only, ghi từng bước đọc/sửa/test/commit).
  4. `.handoff/<MA>/BAO-CAO.md` (hoặc cuối tracklog với phiên `S-...`): đầu ra lệnh `verify`/`test`, `git diff --stat`, và mục tự phản biện cho Claude review.
- **Linh** **quyết định**: lên prototype, chốt dự án, duyệt việc không đảo ngược được, nghiệm thu.

## Tạo ảnh AI (ChatGPT, Gemini, Flow…): luật tối giản và tự duyệt
- Tối giản, có khoảng thở; một chủ thể chính, chi tiết phụ ít và nhỏ; tương phản rõ; bố cục chuẩn (một phần ba, đối xứng, đường dẫn mắt), chừa vùng trống cho chữ; mỗi ảnh một ý; nhìn 3 giây thấy chủ thể (ảnh sản phẩm: 5 giây hiểu sản phẩm).
- Luôn tìm và đính ảnh tham chiếu thật (ưu tiên nguồn có giấy phép như Wikimedia Commons), nói rõ học gì (bố cục, màu, nét); ghi nguồn vào thư mục dự án.
- Prompt luôn có câu: "nhiều khoảng trống, tối giản, một chủ thể, không chi tiết thừa". Không để AI vẽ chữ, số, logo; chữ dựng sau bằng code hoặc công cụ thiết kế.
- Tự duyệt trước khi dùng: xem toàn khung và ở 100%; kiểm tay, ngón, mặt méo; vật thể vô lý; chữ giả, watermark; vỡ hạt sau upscale; lệch tham chiếu; sai văn hoá, địa lý Việt Nam; 7 luật trên. Có lỗi thì vẽ lại hoặc sửa rồi kiểm lại; ghi bảng Đạt/Lỗi (ví dụ `TU-DUYET.md`). Không đưa Linh bản còn lỗi.
