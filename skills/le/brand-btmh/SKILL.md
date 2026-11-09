---
name: brand-btmh
description: "Áp dụng thương hiệu Bảo Tín Mạnh Hải (BTMH, vàng và trang sức 24K) cho mọi thứ tạo ra: web, giao diện, slide, bài đăng, ảnh, bao bì, văn bản Word/Excel, nội dung chữ. Dùng khi người dùng nhắc BTMH, Bảo Tín Mạnh Hải, Kim Gia Bảo, MHJ, Trân Bảo, hoặc làm việc trong D:\\@WF\\PROJECT\\BTMH."
metadata:
  version: "0.1.0"
---

# Thương hiệu Bảo Tín Mạnh Hải

Nhà bán lẻ vàng và trang sức 24K Hà Nội từ 1992; "Thương hiệu Vàng Quốc dân": chuẩn hoá, minh bạch, ấm áp.

## Trước khi làm
1. Đọc `BRAND.md` (luật có mã) và `brand.json`. Màu, chữ, khoảng cách lấy từ `tokens.json` (tầng ngữ nghĩa `color.*`).
2. Theo kênh, mở `prompt-kit/` (web, deck, social, image, product).

## Luật quan trọng nhất
- Màu: Đỏ sơn mài `#7C0410` (`color.primary`) + Vàng Timeless `#EDD0A7` (`color.accent`) + trắng/trắng ngà `#F7F3ED`. Không dùng đỏ/vàng tự chế (`#B71C1C`, `#8B0000`, `#D4A843`, `#FFD700`).
- Vàng không bao giờ làm chữ/logo trên nền trắng (1.5:1). Chữ phụ dùng `#3A2E2A`, không dùng xám `#8C857C` cho chữ nhỏ.
- Tỉ lệ web: 50% nền sáng · 20% đỏ (CTA, logo) · 10% vàng (đường kẻ, hover) · 20% màu phụ.
- Chữ: Artifex CF cho tiêu đề và tên thương hiệu; Google Sans cho nội dung quảng bá; Arial cho văn phòng. Không Times New Roman.
- Logo: dùng `assets/logos/btmh-logo-horizontal-{red,gold,black,white}.svg` theo nền; vùng an toàn 2X; web ≥ 24px cao. Nền vàng → logo đỏ, nền đỏ → logo vàng, nền trắng → logo đỏ. Cấm dùng `logo_btmh.svg` (con dấu tự sinh).
- Giọng: đáng tin, ấm áp, sang trọng Á Đông, điềm tĩnh về giá. Gọi khách "Quý khách" (trang trọng) hoặc "bạn" (social).
- Cấm: hứa lợi nhuận, "đầu tư chắc thắng", "giá sốc", "mua ngay kẻo lỡ"; số liệu tài chính, IPO khi chưa được phép.
- Ảnh AI: không chữ, không logo; vàng 24K trên nền đỏ sơn mài, ánh sáng ấm, tối giản.

## Khi xong
Tự chấm `qa/checklist.md` (bản chung ở `src/lbs-template/qa/`), ghi mục lệch. Nội dung đánh dấu *(suy đoán)* trong BRAND.md thì nói rõ chưa được BTMH duyệt.
