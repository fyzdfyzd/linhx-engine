---
name: kiem-tin-hieu
description: Kiểm 5 lớp truth signal và mức sẵn sàng giao dịch với agent của một thương hiệu (robots cho bot AI, schema, llms.txt, nhất quán đa kênh, bên thứ ba, người đứng tên, review, feed/API/MCP/Zalo mini app). Dùng ở bước 5 của brand-check.
---

# Kiểm tín hiệu (vế Verifiable Data và Reputation)

1. Tự động: `brandcheck.py tin-hieu -w <ws>`
   - B1: robots.txt với 19 bot AI (bot tra web/tìm kiếm tính gấp đôi bot huấn luyện), trang chủ đọc được không cần JavaScript, JSON-LD Organization/Product/Offer/FAQ/Person, sitemap, llms.txt (điểm nhỏ), meta + ngày cập nhật.
   - B2: tải các kênh trong `channels`, dò tên và các dòng `kiem_kenh`. Kênh cần đăng nhập/JS (Facebook, Shopee) sẽ nằm trong `can_kiem_tay`.
2. Tra web để điền `<ws>/tin-hieu-tay.json` (mẫu: `tin-hieu-tay.mau.json`). Mỗi mục phải có link; không có link thì không ghi.
   - B2 tay: với kênh máy không đọc được, mở bằng trình duyệt nếu có, ghi trường khớp/lệch.
   - B3: nguồn độc lập nói về thương hiệu (báo, hiệp hội, giải thưởng, case khách) — đếm domain khác nhau; Wikipedia.
   - B4: người đứng tên có hồ sơ công khai (trang giới thiệu, LinkedIn, báo phỏng vấn).
   - B5: điểm và số review (Google Maps, sàn), có phản hồi khiếu nại, chính sách đổi trả công khai.
   - B6 (thương hiệu bán hàng): feed sản phẩm, API/MCP, Zalo mini app, thanh toán online, giá/tồn kho trên web.
3. Chạy lại `tin-hieu` để code tính điểm. Ghi chú: điểm B1 là điều kiện cần (máy đọc được), không phải lời hứa tăng hạng; bằng chứng về llms.txt và schema còn mâu thuẫn.
