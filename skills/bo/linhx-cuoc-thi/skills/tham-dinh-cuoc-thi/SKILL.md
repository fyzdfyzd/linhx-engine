---
name: tham-dinh-cuoc-thi
description: Đọc thể lệ một cuộc thi hoặc giải thưởng, kiểm điều kiện, chấm giá trị branding và công sức, quyết định nên làm hay bỏ, lập lịch ngược. Dùng khi Linh gửi link thể lệ hoặc hỏi "cuộc thi này có nên làm không".
---

# Thẩm định cuộc thi

Đầu vào: link thể lệ hoặc `id` trong `data/contests.json`.

1. Mở thể lệ gốc. Trích đúng các trường trong `../radar-cuoc-thi/references/schema.md`, cộng thêm:
   `theme` (chủ đề), `length` (giới hạn chữ/phút), `criteria` (tiêu chí chấm, nguyên văn), `rights` (bản quyền tác phẩm sau khi nộp), `submission` (cách nộp: email/form/bưu điện), `ai_policy` (có cấm/cho phép dùng AI không), `jury` (giám khảo).
2. **Cổng điều kiện** (luật cứng, không đoán): tuổi, quốc tịch, nghề, hội viên, tác phẩm chưa đăng, số bài tối đa, phí. Đánh dấu `Nộp được` / `Kiểm điều kiện` / `Không đủ điều kiện` kèm câu trích từ thể lệ.
3. **Chấm 4 trục, 1–5, mỗi trục một câu lý do**:
   - Branding: tên đơn vị tổ chức, báo chí đưa tin, giám khảo, danh xưng dùng được trong bio ("Giải A cuộc thi …").
   - Hợp chất liệu: Linh đã có sẵn bài, case, dữ liệu, góc nhìn AI/truyền thông dùng lại được không.
   - Công sức: số giờ ước tính.
   - Rủi ro: chuyển nhượng bản quyền, cấm AI, bình chọn kiểu like (giá trị thấp), phí.
4. **Quyết định**: Làm / Làm nếu rảnh / Bỏ, một câu. Nếu Làm: lịch ngược từ hạn (chốt ý → bản nháp → sửa → nộp sớm 2 ngày) và `python ".../contestscan.py" mark <id> "đang xem"`.
5. Ghi kết quả thẩm định vào `output/tham-dinh/<id>.md`.

Không bao giờ nộp hay đăng ký thay Linh. Nếu thể lệ cấm dùng AI, nói rõ và chỉ hỗ trợ ý tưởng, dàn ý, kiểm lỗi, không viết hộ.
