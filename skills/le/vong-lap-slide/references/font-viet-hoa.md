# Phông tiếng Việt cho vòng lặp slide

## Vì sao cần
Phông thiếu chữ Việt dựng sẵn (ấ, ữ, ệ…) thì trình duyệt lấy riêng chữ đó từ phông khác: dấu và nét lệch kiểu giữa một từ. Mắt người chấm khó bắt (vòng 1–3 deck BTMH đều cho đạt với Gilda Display thiếu 92/134 chữ). Máy bắt được ngay.

## Ba tầng
1. **Kiểm (tự động, đã có):** `vls.py phong <deck>` đếm 134 chữ trong cmap từng phông, in `bang-dau.png`. `khoa-mau` từ chối khi thiếu.
2. **Chọn phông đủ chữ trước:** đã đo trên Google Fonts 30/10/2026. Đủ 134: Noto Serif Display, Playfair Display, Prata, EB Garamond, Cormorant (dấu mũ nhọn, tránh cho tiêu đề), Lora, Fraunces, Literata, Newsreader. Thiếu: Gilda Display, Bodoni Moda, Marcellus, Forum, Bellefair, Italiana.
3. **Việt hoá khi brand bắt buộc dùng phông không có tiếng Việt:** Font Tàu Nhanh (https://github.com/ivyiron/Fonttaunhanh, web https://fonttaunhanh.vercel.app). Xử lý trong trình duyệt, không tải phông lên máy chủ; có Việt hoá (ghép dấu, chỉnh vị trí/độ cao dấu, dấu chồng), sửa glyph, kerning; xuất TTF. Chạy trên máy Linh (`npm install && npm run dev`, cổng 3000) hoặc dùng bản web.
   - Quy trình: mở phông gốc → Việt hoá → xuất TTF vào `LAB043-DESIGN-ONBRAND/brands/<id>/03-chu/viet-hoa/<Ten>-VN.ttf` → khai báo trong slide bằng `@font-face` → `vls.py phong <deck> --tep <ttf>` phải ra 134/134 → soi `bang-dau.png`.
   - Chỉ Việt hoá phông có giấy phép cho sửa (OFL hoặc mua quyền sửa). Artifex CF, Product Sans là phông bản quyền: hỏi chủ phông trước.
   - Repo chưa có tệp LICENSE: dùng như công cụ, không chép mã vào skill. Cần Việt hoá hàng loạt không người thì viết riêng bằng fontTools (ghép glyph gốc + dấu theo anchor), là việc khác.
