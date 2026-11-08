---
name: lps-ui
description: Thiết kế và tự kiểm giao diện web theo LPS (design token, trạng thái, mobile-first, WCAG 2.2 AA, Core Web Vitals, heuristic Nielsen). Dùng khi làm hoặc sửa màn hình, component, landing page, Zalo Mini App.
---

# Giao diện theo LPS

## Trước khi vẽ
1. Đọc `docs/design/TOKENS.md` (hoặc `src/styles/tokens.css`). Chưa có thì tạo trước: màu (chính, nền, chữ, viền, trạng thái thành công/cảnh báo/lỗi), cỡ chữ (thang 12–14–16–20–24–32), khoảng cách (bội số 4px), bo góc, bóng. **Mọi màu, khoảng cách trong code lấy từ token**, không viết mã màu trực tiếp.
2. Chọn một hướng thị giác rõ ràng cho sản phẩm (ví dụ "ngân hàng tin cậy, nhiều khoảng trắng" hay "năng động, màu đậm") và ghi vào TOKENS.md. Tránh giao diện chung chung kiểu mặc định (gradient tím, bóng mờ khắp nơi, emoji làm icon).
3. Dùng thư viện component đã chọn trong ADR (mặc định shadcn/ui + Tailwind; Zalo Mini App dùng zmp-ui). Không trộn hai thư viện.

## Khi làm mỗi màn
- Thiết kế từ 360px lên. Vùng chạm ≥ 44×44px. Chữ thân ≥ 16px. Font hỗ trợ đủ dấu tiếng Việt (Be Vietnam Pro, Inter, hệ thống).
- Đủ 4 trạng thái: có dữ liệu, rỗng (kèm hướng dẫn bước tiếp), đang tải (skeleton), lỗi (nói rõ chuyện gì và cách thử lại).
- Form: nhãn luôn hiện (không chỉ placeholder), báo lỗi cạnh ô, giữ dữ liệu khi lỗi, nút gửi khoá khi đang gửi.
- Văn bản tiếng Việt tự nhiên, ngắn, động từ trên nút ("Lưu đơn", không "OK").

## Tự kiểm (bắt buộc trước khi báo xong)
1. Mở trình duyệt thật (Playwright, browser của Antigravity, hoặc preview) và **chụp màn hình** ở 360px và 1280px, sáng và tối nếu có. Tự nhìn ảnh, sửa chỗ vỡ bố cục, chữ tràn, căn lệch.
2. Chạy axe (`@axe-core/playwright`): 0 lỗi serious/critical. Tương phản chữ ≥ 4.5:1, chữ lớn ≥ 3:1. Dùng được bằng bàn phím, có focus nhìn thấy được.
3. Lighthouse trên bản build: LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1. Ảnh có kích thước cố định, font `display: swap`.
4. Rà nhanh 10 heuristic Nielsen, ghi vấn đề vào PR: trạng thái hệ thống hiển thị, ngôn ngữ người dùng, cho phép hoàn tác, nhất quán, phòng lỗi, nhận biết hơn nhớ, linh hoạt, tối giản, giúp sửa lỗi, trợ giúp.
5. Đính kèm ảnh chụp vào PR.
