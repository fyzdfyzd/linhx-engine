---
name: brand-unikon
description: Áp dụng thương hiệu Unikon (unikon.vn, sub-agency chiến dịch Generative AI) cho mọi thứ tạo ra: web, slide, credential, proposal, bài đăng, ảnh, nhân vật AI, email, nội dung chữ. Dùng khi người dùng nhắc Unikon, UNIKON, unikon.vn, AI Persona Factory, BESPOKE AI, aicontent.vn, hoặc làm việc trong thư mục BU\UNIKON hoặc PROJECT\Unikon.
---

# Thương hiệu Unikon

Sub-agency chiến dịch AI cho các agency lớn và nhãn hàng tại Việt Nam: Analyse → Generate → Deliver. MMA Smarties Global Silver 2020.

**Lưu ý:** Unikon chưa có guideline chính thức. Màu, chữ, giọng, tagline trong gói là *(đề xuất)* chờ Linh duyệt; với ấn phẩm gửi khách, nói rõ điều này.

## Trước khi làm
1. Đọc `BRAND.md` (luật có mã) và `brand.json`. Màu, chữ, khoảng cách lấy từ `tokens.json` (`color.*` = light, mặc định cho tài liệu; dark ở `$extensions.lbs.dark` cho web hero, showreel). Web dùng `build/tokens.css`.
2. Theo kênh, mở `prompt-kit/` (web, deck, social, image, product).

## Luật quan trọng nhất
- Tên: "Unikon" trong câu, "UNIKON" khi IN HOA; logo "unikon" chỉ qua file.
- Màu: nút/nhấn `#CC1150` (hover `#A30D40`, chữ trắng); magenta logo `#ED145B` chỉ cho mảng lớn/gradient; tím `#5216A6`; cam `#F7941D` ≤ 10%; chữ `#1C1720`, chữ phụ `#58595B`; nền `#FFFFFF`/`#F7F4F8`; nền tối `#120D17`, link tối `#FF85AB`. Gradient chữ ký `#F7941D → #ED145B → #5216A6`.
- Cấm màu cũ rời rạc: `#E93E72`, `#F60863`, `#FC4293`, `#0074FF`, `#FF00DF`, `#020101`.
- Chữ: Montserrat (tiêu đề), Be Vietnam Pro (nội dung). Không Avenir/Raleway/Abel cho tài liệu mới; không Georgia/Times.
- Logo: `assets/unikon-logo-color.png` trên nền sáng; bản chữ trắng chỉ cỡ nhỏ trên nền tối; không vẽ lại, không phóng to bản nhỏ.
- Giọng: tự tin có thành tích, sáng tạo có cá tính, rõ ràng với agency. "anh/chị" trong email, "bạn" trên social. Cấm: "đột phá", "số 1", "giỏi nhất", "đảm bảo viral", "hành trình".
- Ảnh AI: không chữ, không logo, không người nổi tiếng thật; rim light magenta/tím, người Việt trẻ.
- Không tự viết quan hệ với URAH/IF Agent; không ghi năm thành lập, địa chỉ (đang mâu thuẫn).

## Khi xong
Tự chấm `qa/checklist.md`, ghi mục lệch. Nội dung đánh dấu *(đề xuất)*/*(suy đoán)* trong BRAND.md thì nói rõ chưa được duyệt.

## Dùng với ChatGPT
Dán phần trên vào Instructions của Project hoặc Custom GPT, upload `BRAND.md`, `brand.json`, `tokens.json`, logo vào mục Files.
