# Quy trình tạo brand mới (dùng cho mọi dự án)

Thư mục này chứa đủ để một dự án khác tự dựng Brand ID và Brand Guideline đạt chuẩn 2X.Lab (chuẩn chị Hương duyệt 10/11/2026).

## Có gì
- `QUY-TRINH-BRAND-ID.md`: quy trình 9 cổng G0–G8, tiêu chí đạt từng cổng, khung Guideline 8 phần (chuẩn OneHousing 2024), vai, khuôn thời gian, 10 bẫy đã gặp. **Đọc trước.**
- `bo-dung/guideline/`: mã dựng guideline 1920x1080 ra PDF, PNG từng trang, contact sheet; kiểm tràn chữ, quét chữ nội bộ; xuất PPTX sửa được chữ.
- `bo-dung/pattern-options/`: dựng bảng so sánh option pattern cho khách chọn.
- `bo-dung/tai-lieu-2-ban/`: dựng đầu bài, đề xuất hai bản (nội bộ và bản chào khách) có bìa nhận diện.
- `mau/`: trang mẫu đã đạt của 2X.Lab.
- `skill-brand-id-chuan/SKILL.md`: bản sao skill `brand-id-chuan` (cài bằng cách chép vào `C:\Users\ADMIN\.claude\skills\brand-id-chuan\`).

## Bắt đầu một brand mới, 6 bước
1. Tạo `D:\LINHX\BRAND\<TEN-BRAND>\` theo cấu trúc ở `D:\LINHX\BRAND\README.md` (00-goc … 08-phien-ban), viết `00-goc/CORE-VALUE.md` bằng lời nguyên văn của chủ thương hiệu.
2. Tạo thư mục việc (trong LAB hoặc PRJ của dự án), chép `bo-dung/guideline/` vào `<thu-muc-viec>/cong/`.
3. Sửa `nen.py`: màu (DEN, DO, NAU, KEM...), đường dẫn logo vector và font, hàm pattern `pat_X` theo pattern khách chốt.
4. Viết lại nội dung các trang trong `p_logo.py`, `p_luoi.py`, `p_con.py`, `p_cuoi.py` (giữ đủ 8 phần).
5. Chạy `python -I dung.py` trong `cong/`, soát 3 vòng (`kiem.py`, `quet_chu.py`, xem PNG từng trang), rồi `python -I xuat_pptx.py` khi khách xin bản sửa được.
6. Bản được duyệt: chép về `D:\LINHX\BRAND\<TEN-BRAND>\` đúng ngăn, ghi `08-phien-ban/`, commit git.

Mẫu đầy đủ một brand đã làm xong: `D:\LINHX\BRAND\2XLAB\`.
