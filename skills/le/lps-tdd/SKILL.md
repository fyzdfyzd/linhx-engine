---
name: lps-tdd
description: Thực hiện một bước trong SPEC theo vòng test trước (đỏ → xanh → dọn). Dùng khi code logic nghiệp vụ, API, hoặc sửa bug ("sửa lỗi", "implement", "làm bước N của SPEC").
metadata:
  version: "0.1.0"
---

# Vòng TDD

## Với tính năng
1. Chọn **một** AC hoặc một hành vi nhỏ từ SPEC.
2. **Đỏ:** viết test mô tả hành vi qua giao diện công khai của module (`index.ts`), không qua chi tiết bên trong. Chạy, xác nhận test **thất bại vì đúng lý do** (không phải lỗi import/cú pháp).
3. **Xanh:** viết code tối thiểu để test qua. Không thêm tính năng chưa có test.
4. **Dọn:** đổi tên, tách hàm, bỏ trùng lặp; test vẫn xanh.
5. Chạy `pnpm verify`. Xanh thì commit theo Conventional Commits (`feat(module): ...`), đánh dấu AC trong SPEC.
6. Lặp lại với hành vi tiếp theo.

## Với bug
1. Viết test tái hiện bug, xác nhận nó đỏ.
2. Tìm nguyên nhân gốc (đọc code, log, chạy thử), ghi một câu nguyên nhân vào commit.
3. Sửa, test xanh, `pnpm verify` xanh. Commit `fix(module): ...`.

## Luật cứng (vi phạm là dừng lại báo Linh)
- Không sửa, xoá, `skip`, `only` một test đang có để làm nó qua. Nếu test sai, nói rõ vì sao và xin duyệt.
- Không mock chính module đang test. Chỉ mock ranh giới ngoài (HTTP bên thứ ba, đồng hồ, ngẫu nhiên).
- Test integration chạy trên DB thật (container/schema riêng), không mock ORM.
- Không hạ ngưỡng coverage trong cấu hình.
