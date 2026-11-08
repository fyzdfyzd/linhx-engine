---
name: lps-user-test
description: Chuẩn bị, chạy và tổng hợp một vòng thử nghiệm người dùng (usability test) 5 người. Dùng khi tính năng lớn sắp phát hành, khi Linh nói "thử với người dùng", "test người dùng", "UAT".
---

# Thử nghiệm người dùng

Claude chuẩn bị và tổng hợp; **Linh hoặc người trong đội trực tiếp ngồi với người dùng** (AI không thay được người thật). Có thể chạy thử kịch bản trước bằng agent duyệt web để bắt lỗi rõ ràng, nhưng kết quả đó không tính là thử nghiệm người dùng.

## Chuẩn bị
1. Tạo `docs/user-tests/UT-YYYYMMDD-<ten>.md` từ `docs/templates/USER-TEST.md`.
2. Viết 3–5 nhiệm vụ từ AC trong SPEC, giao bằng mục tiêu đời thường, không nhắc tên nút.
3. Đề xuất hồ sơ 5 người tham gia giống người dùng thật (vai trò, mức quen công nghệ, thiết bị). Không ghi tên thật, số điện thoại vào file.
4. Chuẩn bị môi trường: bản staging, tài khoản thử, dữ liệu mẫu; chạy thử toàn bộ kịch bản một lần bằng e2e để chắc không vỡ.
5. Câu hỏi SUS 10 câu (bản tiếng Việt) dùng sau buổi.

## Tổng hợp (sau khi Linh dán ghi chép)
1. Điền bảng kết quả: hoàn thành/thất bại/có trợ giúp, thời gian, SUS.
2. Gom vấn đề, đếm số người gặp, chấm mức 1–4, gắn heuristic Nielsen.
3. Đề xuất sửa, ưu tiên mức 3–4 và vấn đề ≥ 2 người gặp. Mỗi sửa đổi đáng kể thành một SPEC hoặc một mục trong SPEC hiện có.
4. Ngưỡng phát hành T3: mọi nhiệm vụ chính ≥ 4/5 người hoàn thành không trợ giúp, SUS trung bình ≥ 68, không còn vấn đề mức 4.
