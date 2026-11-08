# Hướng dẫn sử dụng (Vietnamese)

Bộ tài liệu hướng dẫn nhanh về hệ sinh thái Kỹ năng Antigravity và các mẫu triển khai.

## 1. Cài đặt Kỹ năng
- Tổ chức các kỹ năng vào thư mục `skills/`.
- Đảm bảo mỗi kỹ năng có tệp `SKILL.md` để Agent có thể nhận diện.

## 2. Cách sử dụng
- Gọi trực tiếp: "Sử dụng kỹ năng **@brainstorming** để lập kế hoạch..."
- Kiểm tra mã nguồn: "Chạy **@lint-and-validate** cho file này."

## 3. Xây dựng Marketplace & Thiết kế (Landing Page)
Để thương mại hóa hoặc trình diễn các kỹ năng:
- Sử dụng mẫu **Marketplace Landing Page** (xem file `marketplace_ui/implementation_guide.md`).
- Tuân thủ tiêu chuẩn **Design Intelligence** (xem file `marketplace_ui/design_intelligence.md`).
- Stack đề xuất: **Vite + React + Tailwind CSS**.

## 4. Kiểm tra & Xác thực (Verification)
Trong môi trường bị hạn chế không thể mở trình duyệt (lỗi Playwright/Chrome):
- Sử dụng tool `read_url_content` để kiểm tra phản hồi từ `localhost:5173`.
- Xác thực HTML thô để đảm bảo Server đang hoạt động đúng.
