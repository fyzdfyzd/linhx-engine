# LUẬT TỔNG ANTIGRAVITY: LƯU VẾT & BÁO CÁO XUỐNG Ổ CỨNG CHO CLAUDE GIÁM SÁT

> **Phạm vi**: Áp dụng bắt buộc cho MỌI dự án (`PRJ/`, `PROTOTYPE/`, `LAB/`, `LINHX-OPC/` và mọi workspace trên máy).
> **Nguyên tắc cốt lõi**: Claude luôn là Kiến trúc sư ra đề và Giám sát chất lượng sau các bước của Antigravity. Mọi hành động, kết quả kiểm thử và vấn đề phát sinh của Antigravity **PHẢI được ghi xuống ổ cứng trong thư mục `.handoff/`**, tuyệt đối không chỉ trả lời trong khung chat.
> Luật riêng của từng repo (`AGENTS.md`, `GEMINI.md` tại repo) thắng luật này ở phần kỹ thuật/deploy, nhưng **không bao giờ được bỏ bước lưu vết dưới đây**.

## 1. Khởi tạo bắt buộc đầu mỗi phiên (Trước khi sửa bất kỳ file nào)
1. Đọc `AGENTS.md`, `GEMINI.md` của dự án (nếu có) và `.handoff/BANG.md`, `.handoff/VAN-DE.md`.
2. Nếu dự án chưa có thư mục `.handoff/`, tự tạo `.handoff/`, `.handoff/logs/`, `.handoff/BANG.md`, `.handoff/VAN-DE.md`.
3. Xác định **Mã công việc (`<MA>`)**:
   - **Có đề bài từ Claude**: dùng mã đề `T-NNN` (đọc `.handoff/T-NNN/DE-BAI.md` hoặc `.handoff/tasks/T-NNN.md`).
   - **Anh Linh giao trực tiếp trong chat (chưa có đề `T-NNN`)**: tự sinh mã phiên `S-YYYYMMDD-HHMM-<slug-ngan>` (ví dụ `S-20261017-1235-fix-ui`).
4. Mở ngay file tracklog `.handoff/logs/<MA>-YYYYMMDD-HHMM.md` trên ổ cứng **trước khi chạm vào code**.

## 2. Ghi Tracklog thời gian thực (`.handoff/logs/<MA>-YYYYMMDD-HHMM.md`)
- Chỉ thêm vào cuối file (`append-only`), có giờ `HH:MM`, không sửa hoặc xoá dòng cũ.
- Ghi ngay sau mỗi bước: đọc/phân tích, viết test đỏ, sửa code, chạy `verify`/`test`, kết quả và mã commit.
- Kể cả khi phiên làm việc chỉ là rà soát/chẩn đoán lỗi mà chưa sửa code, vẫn phải ghi tóm tắt phát hiện vào tracklog hoặc `.handoff/VAN-DE.md`.

```yaml
---
task: <T-NNN hoặc S-YYYYMMDD-HHMM-slug>
repo: <tên hoặc đường dẫn repo>
worker: antigravity
model: <tên model>
bat_dau: YYYY-MM-DD HH:MM
ket_thuc: YYYY-MM-DD HH:MM
nhanh: <branch hiện tại>
---
# Tracklog <MA> (chỉ thêm, không sửa dòng cũ)

| Giờ | Bước | Lệnh / hành động | File đọc hoặc sửa | Kết quả / Vấn đề |
|---|---|---|---|---|
| HH:MM | 1 | Đọc đề & mở tracklog | .handoff/... | ok |
```

## 3. Ghi Sổ Vấn Đề xuống ổ cứng (`.handoff/VAN-DE.md`)
Bất cứ khi nào gặp một trong các tình huống sau, Antigravity **phải ghi ngay** một mục vào `.handoff/VAN-DE.md` để Claude vào đọc thấy liền:
1. **Lỗi lặp lại / Kẹt**: Cùng một lỗi sửa lần 2 chưa xong (tối đa 3 lần phải dừng và chuyển `BLOCKED`).
2. **Lệch Spec / Lệch Kiến trúc**: Code thực tế khác với đề bài của Claude hoặc phát hiện xung đột giữa các tài liệu/test.
3. **Giả định bắt buộc**: Điểm đề bài chưa nói rõ mà Antigravity phải tự chọn hướng xử lý tạm.
4. **Rủi ro / Nợ kỹ thuật (Tech Debt)**: Vấn đề hiệu năng, bảo mật, test đang đỏ sẵn, hoặc giới hạn môi trường phát hiện trong lúc làm.
5. **Chờ quyết định (`BLOCKED`)**: Việc cần Claude thiết kế lại hoặc cần anh Linh duyệt.

Mẫu ghi trong `.handoff/VAN-DE.md` (mục mới đặt lên đầu phần `OPEN`):
```markdown
### [VD-NNN] <Tiêu đề ngắn gọn> — Trạng thái: OPEN | BLOCKED | RESOLVED
- **Thời gian & Phiên**: YYYY-MM-DD HH:MM · `<MA>` · Nhánh: `<branch>`
- **Hiện tượng / Vấn đề**: Mô tả rõ triệu chứng, thông báo lỗi hoặc mâu thuẫn kiến trúc.
- **File / Lệnh liên quan**: `path/to/file.js:L10-L30`, lệnh tái hiện `npm test ...`
- **Đã thử / Cách xử lý tạm**: Đã thử cách A, B (kết quả...).
- **Cần Claude / Anh Linh**: (Ví dụ: Claude chốt hướng xử lý / Anh Linh cấp biến env X).
```

## 4. Nghiệm thu & Bàn giao cuối mỗi bước (`.handoff/<MA>/BAO-CAO.md`)
Trước khi báo hoàn tất cho người dùng trên khung chat:
1. Chạy lệnh kiểm tra chất lượng của repo (`npm run verify`, `npm test`...) và **dán nguyên văn đầu ra cuối** vào `.handoff/<MA>/BAO-CAO.md` (hoặc mục Kết luận cuối Tracklog nếu là phiên sửa nhỏ `S-...`).
2. Dán `git status -sb` và `git diff --stat`.
3. Ghi rõ mục **Tự phản biện cho Claude review**:
   - Đã thoả mãn từng AC nào?
   - Điểm nào còn yếu, chưa có test tự động, hoặc cần Claude kiểm tra kỹ?
   - Danh sách mã `[VD-NNN]` đã mở hoặc cập nhật trong `.handoff/VAN-DE.md`.
4. Cập nhật trạng thái trong `.handoff/BANG.md` và dòng `ket_thuc` trong Tracklog.

## 5. Kỷ luật sắt
- **Không lưu vết = Chưa làm**: Mọi thay đổi hoặc kiểm tra của Antigravity không có dấu vết trong `.handoff/` trên ổ cứng đều coi là vi phạm quy trình.
- **Không giấu lỗi**: Test đỏ, cảnh báo SAST, hoặc workaround tạm thời đều phải ghi rõ vào `.handoff/VAN-DE.md`.
- **Không ghi bí mật**: Tuyệt đối không đọc/in/ghi nội dung `.env`, `cau-hinh.env`, API key, token vào log hay báo cáo (chỉ ghi tên biến).
