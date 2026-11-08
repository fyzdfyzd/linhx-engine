---
name: kiem-chu-anh
description: Kiểm chính tả chữ trong ảnh AI (ChatGPT, Nano Banana, Flow…) ngay sau khi tải về, nhất là tiếng Việt có dấu; sai thì sửa/gen lại. Dùng sau MỌI lượt tạo ảnh có chữ (mockup, key visual, bìa, standee, slide) trước khi lưu bản chính hay gửi Linh.
---
# Kiểm chữ trong ảnh AI

Model ảnh hay vẽ sai dấu tiếng Việt (ư/ơ mất móc, dấu lệch chữ, "ngưởi" thay "người"), cắt chữ, thêm chữ lạ. Ảnh nhỏ nhìn vẫn "đúng", phải soi phóng to.

## Các bước
1. **Lập bảng chữ đúng** trước khi gen: mọi dòng chữ sẽ có trong ảnh, viết chính xác (copy từ prompt). Ghi vào file prompt của việc đó.
2. **Tải ảnh về**, rồi **cắt và phóng to ×2 từng vùng chữ** (ffmpeg `crop=w:h:x:y,scale=iw*2:-1:flags=lanczos` hoặc tương đương). Không chấm trên ảnh thu nhỏ.
3. **Đọc từng chữ, so với bảng**:
   - Đúng mặt chữ + đủ dấu (sắc/huyền/hỏi/ngã/nặng, mũ â ê ô, móc ư ơ, trăng ă, gạch đ).
   - Không thiếu/thừa từ, không bị cắt mép, không có chữ rác (giả Latin, ký tự lạ).
   - Tên riêng, số, giờ đúng y bảng (VSMCamp, CSMOSummit 2026, 1.248, 09:00…).
4. **Sai thì sửa**, mỗi ảnh tối đa 3 lượt:
   - Ưu tiên **sửa trên ảnh đó** (đính ảnh, "keep everything identical, only fix the text '…' → '…'", đánh vần từng chữ cái có dấu, ví dụ n-g-ư-ờ-i).
   - Sửa không được thì gen lại cả ảnh với prompt cũ, chữ ngắn hơn.
   - Vẫn sai sau 3 lượt: ghi lại, báo Linh; đề xuất bỏ chữ khỏi ảnh và đặt chữ thật bằng công cụ dựng (Canva/Figma/HTML).
5. **Kiểm lại bản sửa** đúng như bước 2–3 (model hay sửa chữ này làm hỏng chữ khác).
6. **Ghi kết quả** vào file prompt/báo cáo của việc: ảnh nào, chữ sai gì, mấy lượt, đạt hay chưa. Bản lỗi giữ trong `_archive/` của thư mục, không xoá.

## Lỗi hay gặp
| Sai | Đúng |
|---|---|
| ngưởi / ngưòi / nguời | người |
| truyện / chuyen | chuyện |
| Uỷ / Ủy (lẫn kiểu) | giữ đúng kiểu trong bảng chữ |
| dấu nằm lệch sang chữ bên cạnh | dấu trên đúng nguyên âm chính |
