---
name: lps-spec
description: Viết SPEC có tiêu chí chấp nhận kiểm được trước khi code một tính năng. Dùng khi bắt đầu tính năng mới, khi yêu cầu còn mơ hồ, hoặc khi Linh nói "lên spec", "thiết kế tính năng", "plan".
metadata:
  version: "0.1.0"
---

# Viết SPEC trước khi code

Nguyên tắc: **không viết code sản phẩm khi chưa có SPEC được Linh duyệt** (trừ T1 và sửa lỗi nhỏ ≤ 20 dòng).

## Bước
1. **Khám phá, không sửa:** đọc `AGENTS.md`, `docs/adr/`, module liên quan trong `src/modules/`. Ghi lại 3–5 điều đã biết và các điều chưa rõ.
2. **Hỏi Linh tối đa 5 câu**, mỗi câu kèm phương án đề xuất. Điều gì có mặc định hợp lý thì tự chọn và ghi vào SPEC mục "Giả định".
3. **Viết** `docs/specs/SPEC-NNN-<ten>.md` từ `docs/templates/SPEC.md`:
   - Tiêu chí chấp nhận dạng "Khi … nếu … thì …", mỗi tiêu chí kiểm được bằng test. Có ít nhất một tiêu chí cho trường hợp lỗi.
   - Chỉ rõ module chịu trách nhiệm. Tính năng chạm ≥ 2 module hoặc thêm phụ thuộc mới → kèm ADR.
   - Chạm dữ liệu cá nhân, tiền, phân quyền hoặc LLM → điền mục 5 và mở `lps-bao-mat` bước 1.
   - Kế hoạch thực hiện chia thành các bước nhỏ, mỗi bước kết thúc bằng `pnpm verify` xanh.
4. **Tự phản biện:** đọc lại SPEC dưới vai người review khó tính. Có AC nào không đo được? Có bước nào quá 1 giờ làm? Có cách nào đơn giản hơn? Sửa rồi mới gửi.
5. Đặt `status: DRAFT`, báo Linh duyệt. Linh duyệt thì đổi `APPROVED`.
