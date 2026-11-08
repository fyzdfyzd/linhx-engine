---
name: y-tuong-bai
description: Tìm tứ cho bài của Linh bằng vòng lặp ý tưởng tự tối ưu LAB024 (gieo 30 ý, khán giả ảo và giám khảo nghề chấm, giữ bản thắng, rút bài học), rồi đưa hướng thắng về trạm dàn ý của viet-bai. Dùng khi chủ đề còn mở, Linh chưa có góc nhìn, hoặc Linh nói "nghĩ giúp tôi vài hướng", "bài này nên viết góc nào".
---

# Ý tưởng bài (cầu nối LAB024)

Vòng lặp nằm ở `D:\LINHX\LAB\LAB024-Y-TUONG-TU-TOI-UU\src\` (bản trong project: `/mnt/project-files/LAB024-Y-TUONG-TU-TOI-UU/src/`). Skill này không chép lại vòng lặp; nó chuẩn bị đầu vào và nhận đầu ra.

## 1. Tạo thư mục lượt chạy

`LAB024-Y-TUONG-TU-TOI-UU\chay\<yyyy-mm-dd>-bai-<ten-ngan>\`, với 2 file:

**`brief.md`** theo mẫu lượt chạy OPC Bloomberg (`chay/2026-10-12-bai-opc-bloomberg/brief.md`):
- Loại: bài viết (bình luận / góc nhìn / tản văn)
- Chủ đề, kênh, tên ký, độ dài (lấy từ `don-hang.md` của viet-bai)
- Tư liệu của Linh: liệt kê chuyện trong `du-lieu/KHO-CHUYEN-THAT.md` hợp chủ đề
- Đầu ra mỗi ý: tít, sapo 2 câu, tứ một câu (nghịch lý), tên khái niệm, cú chơi chữ, dàn ý 5–6 đoạn mỗi đoạn một câu, chuyện thật sẽ dùng, câu mở viết hoàn chỉnh. Tối đa 350 chữ.

**`nen.md`**: tóm tắt giọng Linh cho người gieo ý, gồm 11 nước đi trong `skills/giong-linh/references/SO-TAY-GIONG.md` (mỗi nước một dòng) và danh sách "những thứ Linh không làm". Thêm luật: ý nào cần chuyện riêng không có trong kho thì đánh dấu `[CẦN LINH]`, không bịa.

## 2. Chạy vòng lặp

Trên máy Linh (PowerShell):

```
cd D:\LINHX\LAB\LAB024-Y-TUONG-TU-TOI-UU\src
.\chay-dem.ps1 -Luot ..\chay\<thu-muc-luot> -SoVong 3
```

`chay-dem.ps1` dùng Antigravity (`agy`) viết và Claude chấm. Không có `agy` thì chạy tay trong phiên Claude theo các file `prompt-gieo.md`, `prompt-persona.md`, `prompt-hoi-dong.md`, `prompt-hoc-bai.md`, `prompt-viet-lai.md`, ghi sổ bằng `so-cai.js`.

Thêm vào hội đồng chấm một giám khảo "giọng Linh": chấm 0–2 cho mỗi tiêu chí cảnh mở cụ thể, có lật chữ, có chuyện thật trong kho, kết quay về hình ảnh mở.

## 3. Đưa kết quả về viet-bai

Đọc `KET-QUA.md` và `bai-hoc.md` của lượt chạy. Ghi vào `tu.md` của bài:
- Hướng thắng, kèm tỉ lệ phiếu và lý do.
- Hướng về nhì, phòng khi Linh không thích hướng thắng.
- Các bài học dùng được cho dàn ý.

Rồi quay lại trạm 3 của `viet-bai`.
