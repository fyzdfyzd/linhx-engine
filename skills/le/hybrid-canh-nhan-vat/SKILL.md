---
name: hybrid-canh-nhan-vat
description: Dựng cảnh hoạt hình kiểu hybrid: Flow/Veo chỉ làm chuyển động riêng của nhân vật nét vẽ trên nền trắng, code lo object, chữ, máy, âm thanh và canh nhịp theo thoại. Dùng khi Linh nói "hybrid", "làm chuyển động riêng", hoặc khi cảnh có nhân vật cạnh poster, logo, chữ mà Veo làm hỏng.
---

# Cảnh hybrid: nhân vật từ Flow, mọi thứ khác từ code

Mẫu đầu tiên: cảnh N2 trailer VSMCamp, `PRJ\IFAGENT\showreel\vsmcamp-trailer\hybrid\` (`N2-hybrid.mp4`, `LOG.md`). Bản script chạy được: `mau\dung_canh.py`, `mau\kiem_4khung.py`.

Luôn đọc thêm `PRJ\IFAGENT\showreel\CHUAN-ANIMATION.md`.

## Trước khi làm
- Hỏi tính cách nhân vật, đo thời lượng thoại, tìm chữ chốt bằng `ffmpeg -af silencedetect=noise=-35dB:d=0.12`.
- **Lê Bích:** skill `le-bich-hoat-hinh` cấm dùng mô hình sinh video vẽ nhân vật vì tác giả đã từ chối bản vẽ lại. Chỉ chạy hybrid với Lê Bích khi Linh đã yêu cầu rõ, và nhắc Linh việc này khi giao.

## 1. Ảnh nhân vật riêng
- Chỉ ghép từ bộ phận gốc. Nền trắng tinh 1080×1920, không sàn, không bóng, không gì khác.
- Căn giữa, chân cách đáy 220 px. Nhân vật dang tay thì đo bề rộng trước: phải lọt khung, lề ít nhất 40 px.

## 2. Flow
- Tài khoản zomplaza: `flow.google.com/u/3/...` (Chrome hay mở sẵn tài khoản công việc, xem tên ở góc phải trước khi gửi).
- Veo 3.1 Lite (5 tín dụng), Frames to Video, 9:16, 8 giây, x1. Cùng một ảnh làm khung đầu và khung cuối.
- Ô tải lên không có sẵn trong trang. Vá `HTMLInputElement.prototype.click` để giữ input file lại, bấm nút tải, rồi dùng `file_upload` vào input đó.
- Mỗi lần gửi xem ảnh xem trước rồi mới bấm "Thêm vào câu lệnh". Tối đa 3 lần sinh.

Prompt đã dùng, thay phần diễn và mốc giây theo cảnh:

```
Keep the exact black-and-white hand-drawn line art of this round cartoon man, identical design in every frame, pure white background, no floor, no shadow, no new objects, no text, no colour, locked static camera, character stays the same size and position. Deadpan, sarcastic, bored acting: heavy half-closed eyelids, flat mouth, slumped, small economical moves, long deadpan holds; follow the 12 principles of animation (anticipation, arcs, slow-in slow-out, squash and stretch, follow-through, holds). Timing: 0.0s squinting, still, breathing. 0.6s leans forward along an arc. 1.6s slow nod. 1.9s second nod. 2.2s hold. 3.4s small crouch (anticipation). 3.8s eyebrows-up small realisation, tiny jump with stretch. 4.0s lands with squash. 4.2s belly jiggles (follow-through). 4.4s holds a bored stare until 8.0s, returning to the starting pose.
```

Kết quả đo được với prompt này (N2, 02/11/2026): 1/3 lần giữ được thiết kế. Veo **không theo mốc giây**, tự đổi dáng và diễn cau có dù đã cấm. Vì vậy đừng mong clip đúng nhịp: chỉ cần clip có đủ các dáng sạch, nhịp do code quyết.

## 3. Duyệt clip
- `kiem_4khung.py`: so 4 khung 0 / 2,5 / 5 / 7,5 giây với ảnh đầu vào, thêm dải 0,5 giây để thấy dáng và lỗi.
- Loại nếu đổi đầu, tóc, tai, râu, bụng, rốn, nét que; bụng lật bên; thêm mũi, ngón tay. Clip loại vào `_loai\`. Bỏ tiếng bằng `-an`.
- Đo độ nhoè từng khung (tỉ lệ điểm xám trên điểm đen). Khung nhoè phải né.

## 4. Dựng bằng code (`mau\dung_canh.py`)
- **Nhịp nhân vật:** bảng `NHIP` ánh xạ giây cảnh sang giây clip. Giãn đoạn đứng yên, nhảy qua khung nhoè, đặt cú lớn đúng chữ chốt. Vẽ trên 2 khung (`BAC = 2`) cho ra chất tay.
- **Lọc nét:** kéo mức xám (95→205) để nền trắng tuyền, nét đen tuyền, hết bóng mờ của Veo.
- **Ghép:** nhân (multiply) lên sân khấu, nên nền trắng của clip tự trong suốt. Vì vậy không để đường kẻ hay object đi ngang thân nhân vật.
- **Code thêm squash** lúc tiếp đất, neo ở chân. Cú nhảy cao quá thì hạ bằng lệch y.
- **Object:** tách từ storyboard, bỏ đường xám, tách mảng trong bằng floodFill. Bật lò xo, lệch nhau 2 khung.
- **Máy:** đẩy chậm theo câu thoại, đọng trước chữ chốt, giật ra đúng chữ chốt. Zoom không dưới 1 kẻo lộ viền đen. Khi zoom vẫn phải thấy mặt.
- **Chữ:** dựng sau máy nên không rung. Hiện theo mốc thoại, chữ chốt hiện đúng lúc nói.
- **Giấu trò đùa đến chữ chốt:** ở N2, logo hiện trước, mèo chỉ bật ra ở "mông mèo".
- **Âm thanh:** giọng + pốp + bật + tiếp đất tổng hợp bằng numpy.

## 5. Tự duyệt trước khi gửi
Xuất dải khung cả cảnh, cộng dải 12 khung/giây quanh chữ chốt. Kiểm: viền đen, nhoè, đầu đè object, mặt bị cắt, chữ tiếng Việt, tiếng có khớp không. Ghi prompt, số lần sinh, tín dụng, lỗi còn lại vào `LOG.md`.

## 6. Canh theo nhịp nhạc (`mau\nhac.py`, `mau\dung_nhac.py`)
- Nhạc tổng hợp 96 BPM, 1 phách 0,625 s. Tự sinh nên không vướng bản quyền, là nhạc tạm.
- Tính `LECH`: đẩy giọng trễ để chữ chốt rơi đúng phách. N2: 5,84 + 0,41 = 6,25 s, phách 10.
- Nhạc im hẳn 1 phách trước chữ chốt, vào lại đúng chữ chốt. Nhạc nhường giọng bằng ducking.
- Logo hiện và nhún trên phách. Mèo lắc xen kẽ theo phách. Chốt độ dài cảnh theo số phách.
