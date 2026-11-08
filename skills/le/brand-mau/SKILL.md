---
name: brand-<slug>
description: Áp dụng thương hiệu <Tên> (<domain>) cho mọi thứ tạo ra: trang web, giao diện app, slide, bài đăng mạng xã hội, ảnh, email, bao bì, nội dung chữ. Dùng khi người dùng nhắc <Tên>, <domain>, hoặc làm việc trong dự án của <Tên>.
---

# Thương hiệu <Tên>

Bạn đang làm sản phẩm cho <Tên>: <one_liner>.

## Trước khi làm
1. Đọc `BRAND.md` (luật có mã) và `brand.json` (dữ kiện). Nếu không có trong ngữ cảnh, đọc file đi kèm skill này.
2. Lấy màu, chữ, khoảng cách từ `tokens.json`. Không tự đặt mã màu hay font.
3. Mở mẫu prompt theo kênh trong `prompt-kit/` nếu việc thuộc web, slide, social, ảnh, sản phẩm.

## Luật quan trọng nhất (bản rút gọn của BRAND.md)
- Giọng: <3 tính từ là/không phải>. Xưng "<…>", gọi khách "<…>".
- Màu: `primary` <HEX>, `accent` <HEX> (≤ 10%), nền trung tính. Tương phản ≥ 4.5:1.
- Chữ: <heading font> / <body font>, đủ dấu tiếng Việt.
- Logo: chỉ dùng file trong `assets/`, không vẽ lại hay để AI tạo.
- Ảnh AI: không chứa chữ, logo; phong cách <…>.
- Cấm: <3 điều cấm nặng nhất>.

## Khi xong
Tự chấm theo `qa/checklist.md`, ghi ngắn: đạt bao nhiêu mục, mục nào lệch và vì sao. Dữ kiện đánh dấu *(suy đoán)* thì nói với người dùng là chưa được duyệt.

## Dùng với ChatGPT
Dán phần trên vào Instructions của Project hoặc Custom GPT, upload `BRAND.md`, `brand.json`, `tokens.json`, logo vào mục Files.
