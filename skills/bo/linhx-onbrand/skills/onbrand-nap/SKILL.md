---
name: onbrand-nap
description: Nạp một brand guideline (PDF, AI, PPTX, thư mục logo) thành cây thư mục chuẩn và brand.json để chấm onbrand. Dùng khi có guideline mới hoặc guideline đổi.
---

# Nạp brand guideline

Đầu vào: file guideline hoặc thư mục tài sản của một brand. Đầu ra: `brands/<brand-id>/` theo cây chuẩn và `brand.json` đã điền.

## Bước
1. Tạo cây: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/onbrand.py tao-cay <thu-muc-brands> <brand-id>` (brand-id viết thường, gạch nối, ví dụ `listening-vietnam`).
2. Chép file gốc vào `00-goc/`, giữ nguyên tên.
3. Đọc guideline:
   - PDF: `pdfinfo`, `pdftotext -layout`, `pdffonts` (font thật sự nhúng), `pdftoppm -r 150 -png` để xem từng trang, `pdfimages -j` lấy ảnh gốc (ảnh CMYK của Adobe thường bị âm bản, đảo màu lại).
   - Xem bản ghép nhỏ các trang trước để biết trang nào là logo, màu, font, ảnh, ứng dụng.
4. Xếp file: cắt từng biến thể logo vào `01-logo/` (đặt tên theo nền: `logo-ngang-tren-nen-xanh-dam.png`), trang màu vào `02-mau/`, trang font vào `03-chu/`, ảnh vào `04-hinh-anh/`, icon vào `05-icon/`, ấn phẩm mẫu vào `06-ung-dung/`.
5. Điền `brand.json`:
   - Mã màu lấy đúng chữ trong guideline (HEX, CMYK). Guideline làm hệ CMYK thì đo thêm màu render thật trên trang (đếm pixel nhiều nhất) và ghi vào `mau_khi_in_ra_man_hinh`, để thiết kế xuất từ chính file đó không bị chấm oan.
   - `chu.font_cho_phep` theo guideline; font logo nếu guideline không ghi thì đoán, ghi rõ là đoán.
   - `noi_dung.tu_cam`: lorem ipsum, tên template cũ còn sót, từ thương hiệu không được dùng.
6. Viết `LOI-TRONG-GUIDELINE.md`: những chỗ guideline thiếu, mâu thuẫn hoặc còn sót template. Chạy luôn `onbrand.py cham` trên chính PDF guideline: guideline phải tự đạt chuẩn của nó.
7. Viết `LUAT-ONBRAND.md`: checklist một trang cho designer, mỗi dòng một luật kiểm được.
8. Ngôn ngữ thiết kế (để skill onbrand-thiet-ke dùng): điền `brand.json > ngon_ngu_thiet_ke` (tinh thần, luật bố cục, tỉ lệ cỡ chữ, điều không làm); tách logo thành SVG từng màu cho phép (ưu tiên file vector có sẵn trên máy, đổi `fill`); tách hoạ tiết thành tile SVG lặp được (`pdftocairo -svg` từ PDF Illustrator, giữ một chu kỳ); chép font vào `03-chu/`; chạy `thiet_ke.py token`; viết 3–4 khuôn trong `09-khuon/` bắt chước trang ứng dụng của guideline.

## Lưu ý
- Không bịa số: thiếu vùng an toàn, cỡ tối thiểu, tỉ lệ màu thì ghi "guideline không nói" và đề xuất số tạm, đánh dấu chờ duyệt.
- Mỗi brand một thư mục; không trộn tài sản hai brand.
