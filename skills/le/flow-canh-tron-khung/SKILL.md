---
name: flow-canh-tron-khung
description: Dựng cảnh hoạt hình nét vẽ bằng Flow/Veo trọn khung (nhân vật cùng object, chữ trong một ảnh), code chỉ chọn khung, đẩy máy, phụ đề, nhạc. Dùng khi Linh nói "phương án Flow", hoặc cảnh có object nhỏ, ít chuyển động. Cần object bật ra theo nhịp thì dùng skill hybrid-canh-nhan-vat.
---

# Cảnh Flow trọn khung

Mẫu: N2 trailer VSMCamp, `PRJ\IFAGENT\showreel\vsmcamp-trailer\hybrid\N2-flow-nhac.mp4`. Đọc thêm `CHUAN-ANIMATION.md`.

**Lê Bích:** skill `le-bich-hoat-hinh` cấm dùng mô hình sinh video vẽ nhân vật. Chỉ chạy khi Linh yêu cầu rõ, và nhắc Linh khi giao.

## Flow
- Tài khoản zomplaza, `flow.google.com/u/3/...`. Veo 3.1 Lite (5 tín dụng), Frames to Video, 9:16, 8 giây, x1. Cùng một ảnh làm khung đầu và khung cuối. Tối đa 3 lần sinh.
- Ô tìm ảnh: gõ đúng tên, đợi 3 giây, xem ảnh xem trước rồi bấm "Thêm vào câu lệnh".
- Khung trình duyệt có thể đổi cỡ giữa chừng: chụp màn hình lại trước khi bấm gửi.

## Prompt (đạt ngay lần 1 ở N2, 02/11/2026)
Điểm khác prompt hybrid: khoá cả object, liệt kê thứ không được thêm, chỉ xin chuyển động nhỏ, không xin nhảy.

```
Keep the exact black-and-white hand-drawn line art, same character design, same white paper background and same layout; do not add new objects, text or colours; static camera; simple 2D cartoon motion. The round-headed man keeps the same head, hair, ears, stubble, big belly, navel and thin stick arms and legs, no clothes, no nose, no eyebrows, no fingers, same size, same position. The three cats, their logos and the handwritten words stay fixed in exact shape, position and colour for the whole clip; only the cats' tails sway slightly. Follow the 12 principles of animation with small moves only. Acting: bored, sarcastic, tired; half-closed eyes, flat mouth, no smile, no anger. Timing: 0-2s still, one slow breath, belly rises. 2-3s head tilts slightly up towards the cats. 3-5s long deadpan hold. 5-5.5s small slow nod. 5.5-8s hold, returning to the starting pose.
```

Thay phần object, diễn xuất và mốc giây theo cảnh. Một lần đạt chưa đủ để kết luận: khung có poster ảnh thật từng hỏng ở lượt trước.

Clip vẫn lệch mốc giây và có vài khung há miệng, có lông mày. Không dùng cả clip: chọn đoạn sạch.

## Duyệt
Dải khung 0,5 giây cả clip. Kiểm nhân vật theo `CHUAN-ANIMATION.md`, cộng: object có đứng yên, logo có giữ màu, chữ có biến mất không.

## Code (`mau\dung_nhac.py`, nhánh `flow`)
- Bảng `NHIP`: giây cảnh sang giây clip, trên 2 khung. Bỏ đoạn lỗi. Đổi dáng đúng phách.
- Máy: zoom nhẹ, tối đa khoảng 1,1 nếu object chạm hai mép khung. Giật đúng chữ chốt.
- Phụ đề dựng bằng code ở vùng trắng dưới. Nhạc như mục 6 của skill `hybrid-canh-nhan-vat` (`mau\nhac.py`).

## Chọn phương án
Flow trọn khung: nhanh, mặt diễn tốt hơn, nhưng object không tự diễn được. Hybrid: có trò đùa bật object theo nhịp, nhưng diễn của clip riêng kém hơn ở N2.
