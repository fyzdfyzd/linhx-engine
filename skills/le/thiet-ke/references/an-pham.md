# Nhánh ấn phẩm: logo, poster, pano, social, KV

## Tham chiếu người thật (tải về `tham-chieu/`, ghi tác giả)
- Poster: Poster House, typographicposters.com, Fonts In Use, AIGA Eye on Design, Behance "Featured" (lọc người làm), Pentagram, Experimental Jetset, Sagmeister & Walsh, Studio Dumbar.
- Việt Nam: tranh cổ động Việt (Bảo tàng Mỹ thuật, Dogma Collection), tranh Đông Hồ/Hàng Trống, thiết kế Kilala, Rice Creative, Hanoi Grapevine, triển lãm Hà Nội Design Week.
- Logo: logosystem.co, Brand New (underconsideration.com), Logo Archive (Richard Baird), sách "Logo Modernism".
- Riso/in: Risotto Studio, Hato Press, Colorcode Printing.
Mỗi tham chiếu ghi "học:" một điều cụ thể (vd "học: tiêu đề chiếm 1/3 khung trên, ảnh cắt sát mép").

## Hệ phong cách trước khi vẽ (học Appllama image-assets)
Ghi một lần: họ phong cách (một: riso, khắc gỗ, ảnh chụp, mực tay...), 3–5 mã màu, ánh sáng và chất bề mặt, ngữ pháp chủ thể. Mọi prompt = hệ phong cách + chủ thể. Mỗi thành phần vẽ 3–4 bản, chọn 1, vẽ lại phần còn lại cho khớp bản thắng. Bộ icon vẽ một tờ rồi cắt. Vẽ ≥2 lần cỡ hiển thị, không phóng ảnh nhỏ; soi viền 400%.

## Dựng
- Poster/pano: dựng SVG hoặc HTML khổ thật (pano A0 = 841×1189 mm; dựng ở 1/10 tỉ lệ rồi xuất PDF vector + PNG 150 dpi). Chữ font thật đủ 134 ký tự Việt (`vls.py phong` của LAB099).
- Logo: vector SVG từ đầu; thử ở 16 px, 32 px, đen trắng, nền tối, khắc 1 màu. Ảnh AI chỉ dùng để khám phá ý, không dùng nét.
- Thương hiệu đã có guideline: dùng `onbrand-thiet-ke` (LAB043) và chấm `onbrand-cham` ≥85.
- Tách lớp KV: `tach-kv` (LAB078) khi cần PSD.

## Kiểm khổ thật (`kiem/`)
- Poster/pano: xuất bản thu nhỏ còn 8% (mô phỏng xem cách 3 m) và bản mờ Gauss 4 px: thông điệp chính vẫn đọc được. Bản đen trắng: thứ tự nhìn không đổi.
- Social: khung điện thoại 360 px trong feed giả có 2 bài khác bên cạnh; xem 1 giây ghi nhớ được gì.
- Logo: bảng 16/32/64 px, 1 màu, nền sáng/tối.
- In: PDF có tràn lề 3 mm, ảnh ≥150 dpi ở khổ thật, màu CMYK hoặc màu pha ghi rõ.

## Vòng sửa
- Mỗi vòng sửa ≤3 lỗi nặng nhất từ phiếu chấm. Ghi lỗi → cách sửa → kết quả vào STATUS.
- Sửa bản cũ bị chê: viết `CHAN-DOAN.md` trước (lời chê nguyên văn, dấu hiệu theo `chong-mui-ai.md` A, phần nào giữ). Không vẽ lại từ đầu khi chỉ cần gỡ.
