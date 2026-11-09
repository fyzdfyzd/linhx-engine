---
name: brand-ifagent
description: "Áp dụng thương hiệu IF Agent (ifagent.net, AI Event Technology) cho mọi thứ tạo ra: web, giao diện, slide, credential, proposal, bài đăng, ảnh, booth sự kiện, email, nội dung chữ. Dùng khi người dùng nhắc IF Agent, IFAGENT, IFA, ifagent.net, AI activation cho sự kiện, hoặc làm việc trong thư mục IFAGENT/IFAgent/IFA PROPOSAL."
metadata:
  version: "0.1.0"
---

# Thương hiệu IF Agent

Đối tác AI Event Tech giúp agency và nhãn hàng biến brief thành trải nghiệm sự kiện tương tác, cá nhân hoá, đo lường được. Tagline: "AI That Activates".

## Trước khi làm
1. Đọc `BRAND.md` (luật có mã) và `brand.json`. Màu, chữ, khoảng cách lấy từ `tokens.json` (tầng `color.*` = light; bộ dark ở `$extensions.lbs.dark`). Web dùng `build/tokens.css`.
2. Theo kênh, mở `prompt-kit/` (web, deck, social, image, product).

## Luật quan trọng nhất
- Tên: "IF Agent" trong câu; "IFAGENT" chỉ khi IN HOA. Domain ifagent.net (không .vn).
- Chế độ: **dark mặc định** (web, hero, bìa deck, booth): nền `#0D1117`, card `#161B22`, chữ `#FFFFFF`/`#8B949E`. Light cho credential ruột, proposal, giá: nền `#F7F8FA`, chữ `#1A1D21`/`#656D76`.
- Màu: gradient `#0088FF → #00D4AA` (135°) không đổi giữa hai chế độ; cam `#FF6B35` ≤ 5%; tím `#7C3AED` chỉ sub-brand. Cấm palette cũ `#1A237E`, `#00BCD4`, `#E91E63`, `#A78BFA`, `#D4AF37`.
- Tương phản: nút `#0088FF` dùng chữ tối `#0D1117` (chữ trắng chỉ 3.5:1); chữ xanh trên nền sáng dùng `#0066CC`; teal/cam không làm chữ trên nền sáng.
- Chữ: Be Vietnam Pro (tiêu đề), Inter (nội dung), JetBrains Mono (số liệu). Không Outfit cho tiếng Việt, không Georgia/Times.
- Logo: chỉ file trong `assets/` (màu gradient trên nền tối, trắng trên nền tối, đen trên nền sáng); tối thiểu 100px; không vẽ lại.
- Giọng: chuyên nghiệp không khô, tự tin không kiêu, số liệu có nguồn. Gọi khách "bạn". Cấm: "đột phá", "cách mạng hoá", "số 1 Việt Nam", "hành trình", "Vibe Marketing Tool".
- Ảnh AI: không chữ, không logo; sự kiện thật, LED xanh-teal, nền tối, khán giả Việt.
- Không tự viết quan hệ với URAH/Unikon, không ghi CEO/pháp nhân (chưa chốt).

## Khi xong
Tự chấm `qa/checklist.md`, ghi mục lệch. Nội dung đánh dấu *(đề xuất)*/*(suy đoán)* trong BRAND.md thì nói rõ chưa được duyệt.

## Dùng với ChatGPT
Dán phần trên vào Instructions của Project hoặc Custom GPT, upload `BRAND.md`, `brand.json`, `tokens.json`, logo vào mục Files.
