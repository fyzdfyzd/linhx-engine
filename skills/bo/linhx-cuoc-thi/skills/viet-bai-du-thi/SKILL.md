---
name: viet-bai-du-thi
description: Cùng Linh viết bài dự thi (tiểu luận, tản văn, bài báo, hồ sơ đề cử, kịch bản video) đúng thể lệ, giọng Linh, rồi tự phản biện theo tiêu chí chấm. Dùng sau khi cuộc thi đã qua thẩm định và Linh muốn viết.
---

# Viết bài dự thi

Đầu vào: `output/tham-dinh/<id>.md` (chủ đề, giới hạn, tiêu chí, chính sách AI). Nếu chưa có, chạy skill `tham-dinh-cuoc-thi` trước.

1. **Kiểm chính sách AI.** Thể lệ cấm AI hoặc yêu cầu "tự sáng tác": chỉ làm dàn ý, câu hỏi gợi ý, góp ý bản Linh viết. Không viết hộ.
2. **Gom chất liệu thật** của Linh: hỏi hoặc đọc kho (bài đã đăng, case dự án, số liệu đã kiểm). Mỗi số liệu, tên người, sự kiện phải có nguồn; không bịa trải nghiệm cá nhân.
3. **Ba góc tiếp cận**, mỗi góc 3 dòng (ý chính, cảnh/câu mở, vì sao ăn điểm theo tiêu chí). Linh chọn; quá 10 phút không trả lời thì đi theo góc đề xuất.
4. **Bản nháp** đúng giới hạn chữ, đúng thể loại, giọng Linh (câu ngắn, cụ thể, ít khẩu hiệu). Ghi vào `output/bai/<id>-v1.md`.
5. **Hội đồng phản biện**: đọc lại như từng giám khảo theo `criteria`, cho điểm, chỉ 3 sửa đáng nhất; kiểm độ dài bằng `wc -w`, kiểm tác phẩm chưa đăng ở đâu nếu thể lệ yêu cầu.
6. Bản cuối `-final.md` + checklist nộp (định dạng file, tên file, thông tin tác giả, ảnh, cam kết). `mark <id> "đang viết"` khi bắt đầu.

Linh tự nộp. Sau khi Linh báo đã nộp: `mark <id> "đã nộp" --entry "<tên bài>"` để radar dò kết quả theo tên bài.
