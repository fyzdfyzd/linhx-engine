---
name: de-xuat-phuong-an
description: Viết đề xuất 3–4 phương án tách module, có khuyến nghị, rồi đi tiếp bằng sổ quyết định thay vì đứng chờ. Dùng khi Linh hỏi "cho tôi phương án", "đề xuất hướng đi", "nên làm thế nào", sau bước nghiên cứu nền của một lab, hoặc khi gặp ngã rẽ cần Linh chọn.
---

# Đề xuất phương án

## Điều kiện vào

Chỉ đề xuất khi đã có nghiên cứu nền thật: đã đọc code repo cùng loại và ghi vào `01-NGHIEN-CUU-NEN.md`. Nếu chưa có, làm bước đó trước. Đề xuất dựa trên README hay bài tổng hợp là không đạt.

## Viết đề xuất

File `02-PHUONG-AN.md` (hoặc `02-DE-XUAT-HUONG-DI.md` nếu lab đã đặt tên như vậy) trong folder lab, theo `templates/PHUONG-AN.md`.

1. **Kết luận trước:** 2–3 câu nói nên làm gì và vì sao.
2. **3–4 phương án**, khác nhau thật về cách làm, không phải 3 mức độ của cùng một ý. Mỗi phương án có:
   - làm gì, dạng sản phẩm là gì (ưu tiên skill hoặc plugin cho Claude/Antigravity, không phải app);
   - **bảng module**, mỗi module có tên, việc làm và nguồn mượn (repo nào, file nào);
   - ưu, nhược và rủi ro (license, Windows, chi phí token hay credit);
   - hợp khi nào.
3. **Không khuyến nghị:** những gì đã xem và loại, kèm lý do một dòng.
4. **Khuyến nghị:** một phương án, hoặc một phương án chính kèm phần làm song song, cùng lộ trình v0.1 → v0.2.

## Hỏi Linh

- Câu hỏi trả lời được bằng một từ, mỗi lựa chọn một dòng, đánh dấu khuyến nghị. Nếu môi trường có thẻ quyết định (`ask_decision`) thì dùng thẻ, không lặp câu hỏi trong tin nhắn.
- Ghi vào `PLAN.md` dòng `Đang chờ Linh: <câu hỏi> (gửi <giờ>)`.

## Không đứng chờ: sổ quyết định

Khi đang chờ hoặc gặp ngã rẽ nhỏ, quyết định rồi đi tiếp. Mỗi quyết định ghi một dòng vào `Sổ quyết định` trong `PLAN.md`:

```
Ruling: <đã quyết gì> — <vì sao> — <nếu sai thì tốn gì để sửa>
```

- **Luật 10 phút:** chờ Linh duyệt mà 10 phút không có tương tác thì coi như duyệt theo khuyến nghị. Ghi `tự duyệt sau 10 phút` vào cột "Ai duyệt", rồi làm tiếp. Nếu có công cụ hẹn giờ (`send_later`, routine), đặt hẹn 10 phút để tự quay lại.
- **Ngoại lệ phải chờ Linh:** việc không hoàn tác được, như xoá dữ liệu, gửi email hoặc tin nhắn ra ngoài, nộp hoặc đăng ký, đăng bài, thanh toán, hoặc đẩy lên nhánh chính hay production.
- Khi Linh trả lời khác khuyến nghị, đổi hướng ngay và ghi thêm một Ruling mới. Không giữ việc đã làm theo hướng cũ nếu nó cản hướng mới.

## Dấu hiệu đang làm sai

| Ý nghĩ | Thực tế |
|---|---|
| "Chỉ có một cách hợp lý, đưa 1 phương án thôi" | Linh muốn so sánh. Tìm cách khác thật sự, ví dụ mua sẵn, tự viết, hoặc ghép. |
| "Phải hỏi Linh trước đã" với việc hoàn tác được | Quyết, ghi Ruling, đi tiếp. |
| "Đề xuất trước, đọc code sau" | Sai thứ tự. Đọc code trước. |
| Mỗi phương án là một khối lớn không tách được | Tách module để Linh chọn ghép. |
