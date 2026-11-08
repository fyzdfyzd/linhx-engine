# LUẬT TỔNG ANTIGRAVITY: LƯU VẾT & BÁO CÁO XUỐNG Ổ CỨNG CHO CLAUDE GIÁM SÁT

> **Phạm vi**: Áp dụng bắt buộc cho MỌI dự án trong `D:\LINHX` (`PRJ/`, `PROTOTYPE/`, `LAB/`, `LINHX-OPC/`).
> **Bản đồng bộ toàn máy**: `C:\Users\Admin\.gemini\config\plugins\linhx-tracking\rules\AGENTS.md` và `C:\Users\Admin\.gemini\GEMINI.md`.
> **Nguyên tắc cốt lõi**: Claude luôn là Kiến trúc sư ra đề và Giám sát chất lượng sau các bước của Antigravity. Mọi hành động, kết quả kiểm thử và vấn đề phát sinh của Antigravity **PHẢI được ghi xuống ổ cứng trong thư mục `.handoff/`**, tuyệt đối không chỉ trả lời trong khung chat.

## 1. Bốn điểm chạm bắt buộc trong `.handoff/` của mọi dự án
| File trên ổ cứng | Vai trò để Claude bám | Quy tắc ghi của Antigravity |
|---|---|---|
| `.handoff/BANG.md` | Bảng điều phối task (`T-NNN`) và phiên làm nhanh (`S-YYYYMMDD-HHMM`) | Cập nhật khi bắt đầu (`DOING`) và khi kết thúc (`REVIEW` / `ACCEPTED` / `BLOCKED`) |
| `.handoff/VAN-DE.md` | **Sổ vấn đề, rủi ro, lệch spec, lỗi lặp lại, điểm chờ duyệt** | Ghi ngay khi gặp lỗi bất thường, sửa lỗi lần 2 chưa xong, lệch kiến trúc, hoặc cần giả định |
| `.handoff/logs/<MA>-YYYYMMDD-HHMM.md` | **Tracklog thời gian thực** (chỉ nối thêm, có giờ `HH:MM`) | Tạo **trước khi sửa code**; ghi từng bước đọc, test, sửa, commit |
| `.handoff/<MA>/BAO-CAO.md` | Báo cáo nghiệm thu từng đề (hoặc mục Kết luận cuối Tracklog với việc nhỏ `S-...`) | Dán nguyên văn đầu ra `verify`/`test`, `git diff --stat`, và mục Tự phản biện cho Claude |

## 2. Quy trình cho việc không có đề `T-NNN` (Giao trực tiếp trên chat)
Khi anh Linh giao việc trực tiếp mà chưa có mã `T-NNN`:
1. Antigravity tự đặt mã phiên `S-YYYYMMDD-HHMM-<slug-ngan>`.
2. Tạo ngay `.handoff/logs/S-YYYYMMDD-HHMM-<slug-ngan>.md` để ghi từng bước.
3. Nếu phát hiện lỗi, xung đột hoặc vấn đề chưa giải quyết dứt điểm, ghi mã `[VD-NNN]` vào `.handoff/VAN-DE.md`.
4. Cuối phiên ghi đầy đủ kết quả test, `git diff --stat` và tự phản biện vào cuối file log để Claude kiểm tra bất kỳ lúc nào.

## 3. Mẫu mục trong `.handoff/VAN-DE.md`
```markdown
### [VD-NNN] <Tiêu đề ngắn gọn> — Trạng thái: OPEN | BLOCKED | RESOLVED
- **Thời gian & Phiên**: YYYY-MM-DD HH:MM · `<MA>` · Nhánh: `<branch>`
- **Hiện tượng / Vấn đề**: Mô tả rõ triệu chứng, thông báo lỗi hoặc mâu thuẫn kiến trúc.
- **File / Lệnh liên quan**: `path/to/file.js:L10-L30`, lệnh tái hiện `npm test ...`
- **Đã thử / Cách xử lý tạm**: Đã thử cách A, B (kết quả...).
- **Cần Claude / Anh Linh**: (Ví dụ: Claude chốt hướng xử lý / Anh Linh cấp biến env X).
```
