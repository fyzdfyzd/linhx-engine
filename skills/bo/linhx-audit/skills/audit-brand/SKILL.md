---
name: audit-brand
description: "Brand audit toàn diện cho một brand có brand.json (khuôn LAB043): nhận diện hình ảnh, nhất quán đa kênh, giọng và thông điệp, hiện diện trên AI, social. Gọi lại plugin đã có (linhx-onbrand, linhx-brand-check) thay vì làm lại."
argument-hint: "<brand_id> [thư mục ra]"
---

# Audit brand

Gốc dữ liệu một brand: `LAB043-DESIGN-ONBRAND/brands/<id>/` (brand.json, LUAT-ONBRAND.md, ấn phẩm trong 07-bai-thi/).

| Nhóm | Ai đo | Cách |
|---|---|---|
| Nhận diện hình ảnh 25% | agent `brand-nhan-dien` | chạy `linhx-onbrand` onbrand.py trên 5-10 ấn phẩm thật gần nhất (ảnh bài đăng, banner web), lấy điểm trung bình, chuyển lỗi màu/chữ/logo thành phát hiện |
| Nhất quán đa kênh 20% | script | `audit.py nhat-quan kenh.json --brand brand.json -o <id>-audit/` (tên, bio, tagline, link, SĐT) |
| Giọng và thông điệp 20% | agent `brand-giong` | đọc web, bio, 10 bài; đối chiếu định vị, tagline, từ nên dùng, từ cấm; ghi nhóm "Giọng và thông điệp" |
| Hiện diện trên AI 20% | agent `brand-ai` | chạy `linhx-brand-check` (LAB036, chuẩn ABC), quy AVI về 0-100, phát hiện từ chỉ số rơi |
| Social 15% | skill `audit-social` | gộp tự động nếu có `findings/social.json` |

Quy trình: thu kenh.json (Claude tự điền từ trang công khai nếu Linh cho link, ghi nguồn từng ô) → chạy script và agent song song → `audit.py tong-hop <id>-audit/ --loai brand` → khung 4 pha → `moc`.

Plugin nền chưa cài trên máy thì ghi nhóm đó vào chưa chấm, không ước lượng.
