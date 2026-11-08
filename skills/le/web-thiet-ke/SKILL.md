---
name: web-thiet-ke
description: Quy trình 7 bước thiết kế landing page hoặc màn hình app đẹp, đúng brand bằng Claude: đề bài, moodboard ảnh tham chiếu, hướng thị giác, ảnh ChatGPT làm đích nhìn và thành phần, dựng HTML từ token brand, tự kiểm, đóng khuôn. Dùng khi Linh bảo làm landing, web, giao diện app.
---

# web-thiet-ke

Luật gốc: **ảnh AI là đích để nhìn và là thành phần, không phải giao diện.** ChatGPT không vẽ màn hình có chữ để cắt ra dùng; Claude dựng HTML thật từ token brand (cùng tinh thần linhx-deck).

Thư mục làm việc: `du-an/<ten>/` gồm `DE-BAI.md`, `moodboard/`, `HUONG.md`, `anh/`, `tokens.css`, `index.html`, `kiem/`.

## 1. Đề bài (Claude, cổng Linh duyệt)
Chép `khuon/DE-BAI.md`. Linh nói ý hoặc dán đề bài khách thì Claude viết lại đủ 11 mục, chỗ thiếu hỏi gộp một lần. Đề bài khách mơ hồ: viết lại thành mục tiêu đo được + khối cần có.

## 2. Moodboard tham chiếu (Claude in Chrome của Linh, 0 token ảnh)
Nguồn: land-book.com, lapa.ninja, godly.website, onepagelove.com (landing); mobbin.com, screenlane (app); Dribbble/Behance/Pinterest (hình ảnh). Lấy 6–12 ảnh chụp trang + link gốc vào `moodboard/` (dùng `deck.py tai-anh` của linhx-deck). Chỉ xem và tải để tham chiếu nội bộ.

## 3. Hướng thị giác (Claude, cổng Linh chọn)
Giao subagent Sonnet nhìn moodboard, viết `HUONG.md` với 2–3 hướng; mỗi hướng: bố cục, nhịp khoảng trắng, kiểu ảnh, góc bo, kiểu nút, 3 trang mẫu tiêu biểu. **Bắt buộc mở trang ứng dụng web/social của guideline brand (LAB043 `guideline/trang/`, `guideline/img/mockup/web.png`) và mockup đã duyệt trước khi dựng**; brand.json chỉ cho màu và chữ, không cho tinh thần. Đối chiếu luật cứng brand (`LUAT-ONBRAND.md`). Bài học 20/10: bản Sakédemy chỉ dựng từ token bị Linh trả về vì "chưa đúng tinh thần brand". Chạy `scripts/token.py <brand.json> tokens.css`.

## 4. Ảnh ChatGPT Plus (qua Chrome của Linh, có ref)
Hai loại, mọi prompt đều tải kèm ảnh moodboard + logo + bảng màu:
- **Ảnh đích**: 1–2 mockup cả trang theo hướng đã chọn, chỉ để Claude nhìn bố cục và cảm giác. Không cắt, không OCR.
- **Ảnh thành phần**: ảnh hero, minh hoạ, nền hoạ tiết, icon đặc biệt; không chữ, không logo, không số. Ưu tiên ảnh thật của brand (`04-hinh-anh/`) trước ảnh gen.

## 5. Dựng HTML (Claude, skill frontend-design + lps-ui)
Bắt đầu từ `khuon/landing.html` (6 khối) hoặc khuôn app. Mọi màu, cỡ, khoảng cách lấy từ `tokens.css`. Mobile-first 360px, chữ thân ≥ 16px, font đủ dấu.

## 6. Tự kiểm (bắt buộc)
Chụp 360 và 1280 (Playwright), không tràn ngang; đặt cạnh ảnh đích để so; `onbrand-cham` ≥ 85; axe 0 lỗi nặng. Sửa tối đa 3 vòng rồi đưa Linh.

## 7. Đóng khuôn và bàn giao
Khối đạt thì tách vào `khuon/` để dùng lại. **Gửi Linh luôn kèm bản một file** (`*-1file.html`: CSS, font, SVG, ảnh WebP 1400px nhúng base64) vì HTML gửi rời sẽ mất ảnh (lỗi 20/10). Cần designer sửa tay: nhập HTML vào Figma bằng plugin html.to.design (hoặc Figma MCP nếu đã cài) — Figma là nơi sửa, không phải bước bóc CSS. Cần trình diễn nhanh: dựng thẳng trong Claude Design với design system brand rồi handoff về Claude Code.
