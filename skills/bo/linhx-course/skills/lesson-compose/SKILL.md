---
name: lesson-compose
description: Dùng khi cần ghép ảnh các khung slide, các đoạn âm thanh lời giảng và video giảng viên AI thành video bài giảng hoàn chỉnh chuẩn 1920x1080 kèm phụ đề WebVTT và âm lượng chuẩn -16 LUFS.
---
# Ghép video bài giảng và phụ đề (`lesson-compose`)

Skill này đóng vai trò bàn dựng hậu kỳ tự động: lấy thời lượng giọng đọc làm đồng hồ chủ (master clock), nối các đoạn âm thanh kèm khoảng nghỉ ngắn, chuẩn hoá âm lượng theo chuẩn phát sóng `-16 LUFS`, sinh phụ đề `lesson.vtt` và ghép các khung hình slide (kèm khung tròn avatar nếu có) thành video MP4 hoàn chỉnh.

## 1. File đầu vào
- `work/course/04-lessons/<L>/segments.json`: danh sách các đoạn lời giảng và tên file ảnh PNG tương ứng.
- `work/course/04-lessons/<L>/frames/<seg_id>.png`: bộ khung hình slide `1920x1080`.
- `work/course/04-lessons/<L>/audio/<seg_id>.wav`: bộ file âm thanh của từng phân đoạn.
- (Tuỳ chọn) `work/course/04-lessons/<L>/avatar.mp4`: video giảng viên AI khớp môi.

## 2. File đầu ra
- `work/course/04-lessons/<L>/build/narration.wav`: toàn bộ âm thanh bài giảng đã nối kèm khoảng nghỉ (`0,3` giây mỗi đoạn) và chuẩn hoá âm lượng `-16 LUFS`.
- `work/course/04-lessons/<L>/build/lesson.vtt`: file phụ đề chuẩn WebVTT khớp chính xác tới từng mili-giây với từng đoạn lời giảng.
- `work/course/04-lessons/<L>/build/lesson.mp4`: video bài giảng `1920x1080`, `25 fps`, mã hoá `H.264` (`yuv420p`) + `AAC 160k` (bản không avatar).
- `work/course/04-lessons/<L>/build/lesson-avatar.mp4`: video bài giảng có chèn giảng viên AI trong khung tròn đường kính `440 px` ở góc dưới bên phải, cách mép `60 px` (khi chạy kèm tham số `--avatar`).
- `work/course/04-lessons/<L>/timing.json`: bảng kê thời điểm bắt đầu, kết thúc và thời lượng của từng phân đoạn.

## 3. Lệnh engine cần chạy
Chế độ 1 — Dựng video bài giảng tiêu chuẩn (không có avatar):
```text
python src/plugin/linhx-course/engine/compose.py work/course/04-lessons/<L>
```
Chế độ 2 — Dựng video bài giảng có chèn giảng viên AI ở góc dưới phải:
```text
python src/plugin/linhx-course/engine/compose.py work/course/04-lessons/<L> --avatar work/course/04-lessons/<L>/avatar.mp4 --out-name lesson-avatar.mp4
```

## 4. Cổng duyệt
Sau khi ghép xong mỗi bài, kiểm tra các tiêu chuẩn kỹ thuật trước khi đóng gói SCORM:
- Độ phân giải đúng `1920x1080`, có cả luồng hình (`video`) và luồng tiếng (`audio`).
- Thời lượng video nằm trong khoảng `230–420` giây (cho bài 5 phút) và khớp với tổng thời lượng các đoạn audio cộng khoảng nghỉ.
- Độ lớn âm thanh tích hợp (Integrated Loudness đo bằng `ffmpeg ebur128`) nằm trong dải `-18` đến `-14 LUFS` (mục tiêu `-16 LUFS`).
- Không có khung hình đen kéo dài quá `1,0` giây (`blackdetect`).
- Số mốc thời gian (`-->`) trong `build/lesson.vtt` bằng đúng số phân đoạn trong `segments.json`.

## 5. Lỗi hay gặp và cách xử lý (từ thực tế vận hành)
- **Lỗi mất khung hình cuối khi dùng `ffmpeg concat demuxer`**: Bộ demuxer `concat` của `ffmpeg` yêu cầu dòng cuối trong `frames.txt` phải lặp lại đường dẫn ảnh của khung cuối cùng (không kèm dòng `duration`) để khung cuối hiển thị đủ thời gian.
- **Lỗi độ lớn âm thanh lệch ngoài khoảng `-18...-14 LUFS`**: Khi nối nhiều file `.wav` có khoảng lặng, cần chạy bộ lọc `loudnorm=I=-16:TP=-1.5:LRA=11` trên toàn bộ chuỗi âm thanh đã nối (`narration.wav`) thay vì chỉ chuẩn hoá từng đoạn rời rạc.
- **Lỗi không tương thích trình phát web do hệ màu**: Luôn chỉ định `-pix_fmt yuv420p` khi xuất `libx264` để mọi trình duyệt và LMS đều phát được video.
