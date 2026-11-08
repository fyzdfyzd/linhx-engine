---
name: bang-su-that
description: Lập bảng sự thật (brand-facts.json) cho brand check chuẩn ABC, bằng phỏng vấn chủ thương hiệu hoặc chuyển từ brand.json chuẩn LBS. Dùng ở bước 1 của brand-check hoặc khi người dùng muốn khai/sửa sự thật về thương hiệu.
---

# Bảng sự thật

1. `brandcheck.py khoi-tao -w <ws> --brand ... --website ... --category ...` tạo `brand-facts.json` từ mẫu.
2. Nếu có brand.json chuẩn LBS (LAB012/LAB015, ví dụ `LAB015-BRAND-TRUTH/data/*.brand.json`): đọc và chép sang. Chỉ đưa vào `facts` các dòng `status: confirmed`; dòng `proposed`/`inferred` ghi vào `_chua_chot` để báo cáo nói "thương hiệu chưa tự chốt thì không bắt AI nói đúng được".
3. Nếu không có: phỏng vấn ngắn, mỗi lần một nhóm:
   - Nhận diện: tên, tên khác/viết tắt/không dấu, công ty, năm, trụ sở, hotline, người sáng lập.
   - Sản phẩm: 1–3 sản phẩm chủ lực + giá + link.
   - Khách: persona (2–3), nhu cầu điển hình, ngân sách, "không dành cho ai".
   - Định vị: 3–5 thuộc tính muốn AI nói về mình (dùng cho chỉ số Khớp định vị).
   - Bằng chứng có link; claim tự cấm (ví dụ "số 1").
   - Đối thủ (tên + domain); nếu không biết, chạy thử gói Nhanh rồi lấy `doi_thu_chua_khai` trong báo cáo.
   - Kênh chính thức: website, fanpage, gian hàng sàn, Google Business, masothue.
   - Dữ kiện đã đổi: điền `previous` + `valid_from` (để chấm nhãn Cũ).
4. Đánh `kiem_kenh: true` cho dòng cần thống nhất giữa các kênh (công ty, trụ sở, hotline).
5. Mỗi dòng có `source`. Không tự điền giá trị bằng hiểu biết của mình; chỗ không biết để trống.
