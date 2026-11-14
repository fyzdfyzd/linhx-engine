---
name: rea
description: Cửa vào họ skill phân tích ngược linhx-rea cho 5 loại đầu vào (video, sách, báo cáo, bài, ảnh). Dùng khi người dùng muốn mổ xẻ cấu trúc, thẩm mỹ, thủ pháp hoặc tái tạo một tác phẩm tham chiếu.
---

# rea — Cửa vào phân tích ngược (linhx-rea)

Họ `linhx-rea` mổ xẻ tác phẩm theo chuẩn 2 tầng: **code đo định lượng trước → agent đọc theo từ vựng đóng có mốc sau** (xem `../../references/khung-chung.md`).

## 1. Xác định loại đầu vào

Nếu người dùng chưa đưa tư liệu hoặc chưa rõ định dạng, hỏi ngắn gọn tác phẩm thuộc loại nào trong 5 loại:
1. **Ảnh** (`.jpg`, `.png`, `.webp`, keyframe, ảnh chụp, poster/KV)
2. **Video** (`.mp4`, `.mov`, `.mkv`, MV, TVC, clip ngắn)
3. **Sách** (chương sách, chuyên khảo)
4. **Báo cáo** (báo cáo nghiên cứu, deck phân tích)
5. **Bài** (bài viết, tiểu luận, bài đăng)

## 2. Điều hướng sang skill con

| Loại đầu vào | Trạng thái | Hành động của agent |
|---|---|---|
| **Ảnh** | Đã mở | Đọc và thực hiện đúng `../rea-anh/SKILL.md` |
| **Video** | Dùng bản sẵn | Chuyển sang skill `rea-video` (`src/rea-video/skills/rea-video/SKILL.md`) |
| **Sách / Báo cáo / Bài** | Chưa mở | Báo hiện chỉ mới mở `rea-anh` (và `rea-video` có sẵn); hỏi người dùng có muốn trích trang/bìa dạng ảnh để chạy `rea-anh` không |

## 3. Chuẩn dùng chung

- Khung 2 tầng, mốc toạ độ/thời gian, cấu trúc thư mục ra: `../../references/khung-chung.md`
- Schema thẻ thủ pháp rút trích: `../../references/the-thu-phap.md` và `../../references/the-thu-phap.schema.json`
