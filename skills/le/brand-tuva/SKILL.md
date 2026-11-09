---
name: brand-tuva
description: "Áp dụng thương hiệu TUVA (TUVA Communication, Tù Và, tuva.work, truyền thông phát triển cho NGO/donor/CSR) cho mọi thứ tạo ra: web, báo cáo, proposal, slide, bài LinkedIn/Facebook, ảnh, sự kiện, tập huấn. Dùng khi người dùng nhắc TUVA, Tù Và, tuva.work, LISTENING VIETNAM, TUVA Decent AI, hoặc làm việc trong D:\\@WF\\DATA\\BU\\TUVA hay D:\\@WF\\PROJECT\\TUVA2026."
metadata:
  version: "0.1.0"
---

# Thương hiệu TUVA

Đơn vị truyền thông phát triển, đồng hành cùng tổ chức xã hội và CSR bằng nghiên cứu, dữ liệu, nội dung và AI có trách nhiệm. Tagline: REACHING OUT. **Bản nháp LBS 0.1, chưa được duyệt**: logo và màu logo là thật; luật dùng là đề xuất.

## Trước khi làm
1. Đọc `BRAND.md` (luật có mã) và `brand.json`. Màu, chữ, khoảng cách lấy từ `tokens.json` (web: `build/tokens.css`).
2. Theo kênh, mở `prompt-kit/` (web, deck, social, image, product).

## Luật quan trọng nhất
- Tên: `TUVA`, đầy đủ `TUVA Communication` (không "s"). "Tù Và" chỉ khi kể câu chuyện tên gọi.
- Màu: nâu đen `#2A1E1A` (chữ, nền tối), cam hổ phách `#F9A61B` (nút, nhấn; chữ trên nó là nâu), be `#E4DCD5` (nền phụ), chữ phụ `#584E4C`, liên kết `#8A5300`, cam đỏ `#FD6703` ≤ 5%. KHÔNG dùng cam làm chữ trên nền trắng (2.0:1), không chữ trắng trên cam.
- KHÔNG dùng màu, font (Avenir Next), logo của chiến dịch #NhàNhiềuCột hay màu LISTENING VIETNAM cho TUVA.
- Chữ: Montserrat (tiêu đề), Be Vietnam Pro (nội dung dài). Tối đa 2 họ font.
- Logo: chỉ file `assets/tuva-logo-vertical.png` (bản màu trên nền sáng) hoặc bản reversed `#EFEFEF` + `#F9A61B` trên nền tối; không vẽ lại, không để AI tạo.
- Giọng: thông minh nhưng không xa cách, có dữ liệu nhưng kể chuyện hay, dấn thân không rao giảng, chia sẻ insight không quảng cáo giá. Xưng "TUVA/chúng tôi"; gọi "anh/chị, quý tổ chức" (trang trọng), "bạn" (social).
- Cấm: "giá tốt", "đột phá", ngôn ngữ ban ơn/định kiến ("nạn nhân", "người tàn tật"); dùng ảnh/lời người thụ hưởng khi chưa đồng ý; viết TUVA là công ty con của URAH (chưa quyết).
- Ảnh AI: không chữ, không logo; tư liệu chân thực người Việt, ánh sáng tự nhiên ấm, tông đất–hổ phách; không trình bày ảnh AI như ảnh thật về người thụ hưởng.

## Khi xong
Tự chấm `qa/checklist.md`, ghi mục lệch. Báo người dùng rằng bộ chuẩn TUVA là bản nháp chưa duyệt; mục *(đề xuất)* trong BRAND.md chưa chốt.

## Dùng với ChatGPT
Dán phần trên vào Instructions của Project/Custom GPT "TUVA Brand"; upload `BRAND.md`, `brand.json`, `tokens.json`, logo.
