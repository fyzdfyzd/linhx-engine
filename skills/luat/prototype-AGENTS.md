# PROTOTYPE

PROTOTYPE trả lời: **"người dùng có cần, có nên làm thật không?"**. Chỉ nhận ý tưởng đã `WORKS` ở LAB và qua cổng điểm.

- Mỗi prototype một thư mục `PRT<số>-<VIẾT-TẮT>/` (giữ viết tắt của LAB gốc) (tạo bằng skill `proto-moi`):
  - `OVERVIEW.md` (từ template `proto.md`): EXP gốc, người dùng thử, giả thuyết, tiêu chí đạt, kết quả, quyết định.
  - `LOG.md`: nhật ký dựng và thử, chỉ thêm.
  - `FEEDBACK.md` (từ template `feedback.md`): mỗi buổi thử một mục.
  - `src/`, `output/`, `.handoff/`.
- `INDEX.md`: Mã | Tên | EXP gốc | Trạng thái | Người dùng thử | Bước tiếp.

## Vòng đời
`BUILDING` → `USER-TEST` → `VALIDATED` / `KILLED` / `PARKED` → `HANDOFF`

- `BUILDING`: chỉ dựng đủ để người dùng thử được. Claude viết task, Antigravity làm.
- `USER-TEST`: ghi phản hồi **nguyên văn** vào FEEDBACK.md; không tóm tắt mất ý.
- Quyết định do Linh chốt. `VALIDATED` → tạo `PRJ<số>-…` hoặc `EDU/MODULE/…`, đổi thành `HANDOFF`, link hai chiều.
- Không xoá prototype bị loại; giữ lý do.
- Không ghi thông tin cá nhân của người dùng thử; chỉ ghi vai trò (ví dụ "cán bộ tín dụng VCB").
