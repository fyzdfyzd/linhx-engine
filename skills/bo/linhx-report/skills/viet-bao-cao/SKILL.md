---
name: viet-bao-cao
description: Bước 5–8 của linhx-report. Ghost report (mỗi trang một thông điệp, kiểu trang, ảnh mẫu), viết từng chương bằng cú pháp chương có khối hình/số lớn/trích dẫn/sidebar/khuyến nghị, kiểm số và trích dẫn, phản biện bằng agent và viết tóm tắt điều hành sau cùng. Dùng trong quy trình bao-cao.
---

# Bước 5–8: ghost report, viết, kiểm số, phản biện

Tài liệu: `references/kieu-trang.md` (23 kiểu trang), `references/luat.md` (V01–V11, D01–D17), `references/cu-phap-chuong.md`.

## Bước 5: ghost report (`05-ghost.md`), cổng chính Linh duyệt

1. Mỗi dòng là MỘT trang: `- [Txx] Thông điệp là câu kết luận | hinh: H01, H02 | mau: 00-mau/<ten>/p-012.png | chu: 1800`.
2. Thông điệp 8–30 tiếng, có động từ hoặc số. Đọc liền các thông điệp phải ra một lập luận: câu trả lời trước, lý do sau (kim tự tháp).
3. Mỗi trang T09–T20 có `mau:` trỏ một trang mẫu cụ thể (từ bước 0) để dựng giống tinh thần trang đó.
4. Nhịp: không quá 2 trang chữ thuần liền nhau (T10, T11); mỗi chương có ít nhất 1 trang hình (T12/T13) và 1 điểm nhấn (T14 số lớn, T15 bình luận, T16 sidebar hoặc trích dẫn).
5. Tóm tắt (T06/T07) để trống thông điệp chi tiết: viết sau cùng.
`report.py cong <dir> 5`, gửi Linh danh sách thông điệp (không kèm chi tiết), Linh duyệt.

## Bước 6: viết chương (`06-chuong/NN-ten.md`)

- Một chương một lượt, ≤2.000 chữ. Trước khi viết chương N, đọc lại tiêu đề và ý chính các chương đã viết để không lặp.
- Theo cú pháp `references/cu-phap-chuong.md`. Mỗi trang trong ghost report thành một đoạn khối tương ứng (hình, số lớn, trích dẫn, sidebar).
- Mỗi câu có số mang `[BCxx]` ngay trong câu. Số do mình suy ra ghi `[SUY LUẬN]`.
- Tiêu đề chương và mục (`##`) là câu kết luận.
- Số kiểu Việt: 1.200; 2,5%; 39 tỷ USD. Không gạch ngang dài.
- Giọng: thẳng, cụ thể, câu trung vị ≤28 tiếng; tránh mẫu giọng AI (script đếm). Có `linhx-viet-bai` thì soát thêm giọng Linh.
- Chương phương pháp đặt tên `NN-phuong-phap.md` (nội dung: thời gian, phạm vi, nguồn, định nghĩa, giới hạn).
`report.py cong <dir> 6`.

## Bước 7: kiểm số và trích dẫn

`report.py cong <dir> 7` ghi `07-kiem-so.json`. Số "mồ côi" (lệch >10% hoặc không có trong bằng chứng): sửa theo bằng chứng hoặc bỏ. Số "cần duyệt" (lệch 1–10%, thường do làm tròn): ghi đúng như nguồn.

## Bước 8: phản biện và tóm tắt

1. Dựng bản nháp PDF (`report.py dung`) để agent đọc được.
2. Gọi agent `nguoi-doc-moi` (không cho ngữ cảnh, chỉ PDF) và `partner-tu-van` (cho đề bài + PDF). Ghi kết quả vào `08-phan-bien.md`, mỗi điểm cần sửa là `- [ ] …`; sửa xong đánh `[x]`, không sửa thì ghi `Lý do: …`.
3. Viết `06-chuong/00-tom-tat.md` SAU CÙNG: 3–7 phát hiện, mỗi phát hiện mở bằng câu kết luận in đậm ≤25 tiếng, rồi 1–2 câu số có mốc so sánh và `[BCxx]`; có khối `::: so-lon` 2–3 con số lớn.
`report.py cong <dir> 8`.
