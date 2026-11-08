---
name: quy-trinh-nghiep-vu
description: Soạn hoặc chuẩn hoá quy trình nghiệp vụ ngân hàng (SOP) từ mô tả thô, ghi chú họp hoặc văn bản cũ, theo khung 10 mục có RACI, lưu đồ, điểm kiểm soát, SLA, rồi tự kiểm bằng script. Dùng khi người dùng nói soạn quy trình, viết SOP, chuẩn hoá quy trình, quy trình giải ngân, mở tài khoản, đối soát.
---

# Soạn quy trình nghiệp vụ

Đầu vào: mô tả thô của một quy trình (lời kể, ghi chú họp, văn bản cũ, ảnh lưu đồ). Đầu ra: một file `QT-<ma>.md` theo khung `assets/khung-quy-trinh.md`, đã qua `scripts/kiem_sop.py`.

## Các bước

1. **Hỏi đủ 5 thứ trước khi viết** (gộp một lượt hỏi, bỏ câu nào đầu vào đã trả lời): tên và mã quy trình; đơn vị chủ trì; điểm bắt đầu, điểm kết thúc; các vai tham gia; hệ thống dùng (core banking, LOS, eKYC...).
2. **Chép khung** `assets/khung-quy-trinh.md`, điền từng mục. Giữ đúng tên 10 mục để script kiểm được.
3. **Bảng bước**: mỗi bước một dòng, đủ cột Người làm, Đầu vào, Đầu ra, Hệ thống, SLA, Kiểm soát. Bước nào có rủi ro (tiền ra, dữ liệu khách, phê duyệt) phải có kiểm soát cụ thể: maker-checker, đối chiếu, hạn mức, nhật ký.
4. **RACI**: mỗi bước đúng một A. Không để trống R.
5. **Lưu đồ** bằng khối `mermaid` (flowchart TD), nút trùng tên bước.
6. **Căn cứ pháp lý**: chỉ ghi văn bản người dùng đưa hoặc đã tra được nguồn. Văn bản chưa chắc thì ghi `[CẦN XÁC MINH]`, không tự bịa số hiệu thông tư.
7. **Tự kiểm**: chạy `python scripts/kiem_sop.py QT-<ma>.md`. Sửa đến khi `ĐẠT`. Tối đa 3 vòng, còn lỗi thì báo người dùng.
8. **Trả kết quả**: đường dẫn file, số bước, số điểm kiểm soát, danh sách `[CẦN XÁC MINH]` để người dùng rà.

## Luật

- Viết tiếng Việt hành chính ngân hàng, câu ngắn, động từ đầu câu ("Kiểm tra", "Phê duyệt").
- Không đưa dữ liệu khách hàng thật vào ví dụ.
- SLA ghi đơn vị rõ (phút, giờ làm việc, ngày làm việc).
