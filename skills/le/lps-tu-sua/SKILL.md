---
name: lps-tu-sua
description: Vòng tự kiểm và tự sửa sau mỗi thay đổi code. Dùng sau khi sửa file, trước khi báo "xong", khi CI đỏ, hoặc khi Linh nói "kiểm lại", "chạy cho xanh", "fix CI".
---

# Tự kiểm, tự sửa

Agent **không được nói "xong" nếu chưa có bằng chứng chạy**. Bằng chứng = đầu ra lệnh, ảnh chụp trình duyệt, hoặc link CI xanh.

## Vòng lặp (tối đa 3 lần cho cùng một lỗi)
1. Chạy `pnpm verify` (format → lint → typecheck → test → build). Với giao diện: chạy thêm e2e liên quan và chụp màn hình 360px và 1280px.
2. Đỏ → đọc **lỗi đầu tiên** đầy đủ, xác định nguyên nhân gốc (không đoán). Ghi một dòng: "Lỗi X do Y".
3. Sửa đúng chỗ gây lỗi. Không sửa test, không tắt luật lint, không thêm `@ts-ignore`/`any`/`as unknown as` để vượt qua.
4. Chạy lại từ bước 1.
5. Sau 3 lần vẫn đỏ cùng một lỗi: **dừng**, hoàn tác thay đổi dở nếu nó làm hỏng thêm, báo Linh: lỗi, 3 giả thuyết đã thử, đề xuất bước tiếp.

## Sau khi xanh
- So lại với SPEC: mọi AC của bước này đã có test và đã qua?
- Xem `git diff` một lượt: còn `console.log`, code chết, TODO không có mã việc, bí mật?
- Kiểm thay đổi ngoài phạm vi: file nào bị sửa mà SPEC không nhắc? Có lý do thì ghi, không thì hoàn tác.

## CI đỏ
Lấy log bước lỗi (`gh run view --log-failed`), tái hiện trên máy bằng đúng lệnh đó, rồi vào vòng lặp ở trên. Không bấm chạy lại CI khi chưa hiểu lỗi; test "chập chờn" (flaky) phải được ghi vào `docs/FLAKY.md` và sửa, không bỏ qua.
