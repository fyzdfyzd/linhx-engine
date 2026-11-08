---
name: ho-so-tai-tro
description: Khung kiến thức viết và tự phản biện hồ sơ xin tài trợ (concept note, full proposal, mục tiêu, khung logic, ngân sách, tác động), theo tiêu chí chấm của nhà tài trợ. Dùng khi viết hoặc soát hồ sơ cho TUVA và các tổ chức của Linh (EU, UNDP, GIZ, quỹ quốc tế, NAFOSTED), hoặc khi LAB013 và LAB018 cần mẫu, tiêu chí chấm, lỗi thường gặp.
---

# Hồ sơ tài trợ (bản LINHX)

Mượn từ skill `research-grants` của K-Dense Scientific Agent Skills (MIT, xem `goc/LICENSE-KDENSE.md`). Bản gốc viết cho NSF, NIH, DOE, DARPA và NSTC (`goc/SKILL-GOC.md`, `goc/references/`). Phần dùng được cho mọi nhà tài trợ là nguyên tắc viết, tiêu chí chấm, cách viết mục tiêu, tác động rộng, ngân sách và lỗi thường gặp.

**Quan hệ với các lab:** LAB018 là xưởng viết hồ sơ chính, LAB013 là radar chọn call. Skill này là **thư viện kiến thức** cho hai lab đó, không thay quy trình của LAB018. Hồ sơ tổ chức TUVA ở `LAB013-CALL-TRACKER/tuva/HO-SO-TUVA.md`.

## Quy trình

1. **Nắm call trước.** Đọc tài liệu chính thức của call (Guidelines, mẫu đơn, tiêu chí chấm, hạn), không dùng trang tổng hợp. Ghi ngày đọc. Bản gốc gọi bước này là "establish the governing opportunity first".
2. **Ma trận tuân thủ.** Lập bảng: yêu cầu của call (điều kiện, độ dài, mục bắt buộc, trần ngân sách, đồng tài trợ) → mục trong hồ sơ → trạng thái.
3. **Mục tiêu và logic.** Áp `goc/references/specific_aims_guide.md`, đổi "Specific Aims" thành mục tiêu tổng, mục tiêu cụ thể, kết quả và hoạt động. Với EU, dùng khung logic hoặc lý thuyết thay đổi theo đúng mẫu của call.
4. **Viết theo tiêu chí chấm.** Mỗi tiêu chí trong call phải có một đoạn trả lời rõ ràng. Nguyên tắc viết ở `goc/references/writing_principles.md`; tác động ở `goc/references/broader_impacts.md`.
5. **Ngân sách và thuyết minh:** dùng `goc/assets/budget_justification_template.md` làm khung, thay quy tắc NIH/NSF bằng quy tắc của nhà tài trợ (ví dụ PRAG của EU).
6. **Tự phản biện** theo `goc/references/review_criteria.md` và mục "Common Mistakes" trong `goc/SKILL-GOC.md`. Chấm từng tiêu chí bằng thang của call, ghi điểm yếu và cách sửa.
7. Trước khi giao, chạy `xac-minh-truoc-khi-bao-xong`: số liệu, hạn, điều kiện đều phải có link nguồn.

## Luật

- Không nộp, không đăng ký tài khoản và không gửi email thay Linh hoặc TUVA.
- Không bịa số liệu, đối tác, thư cam kết hay kết quả cũ. Chỗ còn thiếu ghi `[CẦN LINH/TUVA: …]`.
- Phần chỉ đúng cho NIH, NSF, DOE, DARPA hay NSTC (định dạng, biểu mẫu) thì bỏ qua, trừ khi call thật sự là của các cơ quan đó.
