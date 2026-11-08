---
name: proto-moi
description: Đưa một EXP đã chạy được ở LAB lên PROTOTYPE khi Linh nói "lên prototype: LAB…" hoặc đồng ý sau khi chấm cổng.
---
# Lên prototype

1. Đọc `OVERVIEW.md` của EXP gốc. Nếu chưa `WORKS` hoặc chưa có điểm/điểm < 11, **vẫn làm tiếp** (Linh được đi thẳng): ghi frontmatter `promoted: truc-tiep` ở PRT và một dòng lý do (nếu Linh nói) vào LOG. Ngược lại ghi `promoted: theo-diem`.
2. Đọc `PROTOTYPE/INDEX.md` để lấy số tiếp theo.
3. Tạo `PROTOTYPE/PRT<số>-<VIẾT-TẮT>/` (giữ viết tắt của LAB gốc) với `OVERVIEW.md` (từ `_system/templates/proto.md`), `LOG.md` (từ `exp-log.md`), `FEEDBACK.md` (từ `feedback.md`), thư mục `src/ output/`. Chép code cần dùng từ `src/` của EXP, không di chuyển.
4. Điền mục 1–4: EXP gốc, đề xuất người dùng thử, giả thuyết rủi ro nhất, tiêu chí đạt đo được, phạm vi tối thiểu. Hỏi Linh chốt người dùng thử và tiêu chí.
5. Link hai chiều: frontmatter `exp:` ở PROTO; ở EXP đổi `status: PROMOTED`, thêm `proto: PRT…`, sửa dòng trong `LAB/INDEX.md`.
6. Thêm dòng `BUILDING` lên đầu `PROTOTYPE/INDEX.md`.
7. Nếu cần code: viết `.handoff/tasks/TASK-001.md` cho Antigravity.
