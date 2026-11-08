---
name: instructor-avatar
description: Dùng khi cần tạo video giảng viên AI nói khớp môi với lời giảng tiếng Việt bằng mô hình tự chạy trên máy, hỗ trợ cả nhánh từ video gốc (MuseTalk 1.5) và nhánh từ 1 ảnh chân dung tĩnh (SoulX-FlashHead Lite, JoyVASA).
---
# Tạo hình giảng viên AI khớp môi (`instructor-avatar`)

Skill này sinh video hình ảnh giảng viên nói khớp môi (`avatar.mp4`) theo đúng độ dài của file âm thanh lời giảng (`build/narration.wav`), hỗ trợ hai nhánh: từ một đoạn video quay sẵn (MuseTalk 1.5) hoặc chỉ từ một tấm ảnh chân dung chính diện (FlashHead Lite / JoyVASA).

## 1. File đầu vào
- File âm thanh lời giảng đã nối và chuẩn hoá: `work/course/04-lessons/<L>/build/narration.wav` (hoặc đoạn âm thanh kiểm thử).
- File cấu hình `work/course/engine.json` chứa đường dẫn môi trường ảo của các engine (`musetalk_python`, `flashhead_python`, `joyvasa_python`).
- Tư liệu hình ảnh giảng viên:
  - **Nhánh 1 (Từ clip quay sẵn)**: `inputs/linh-face.mp4` (clip 5–10 giây, chính diện, trung cảnh, 25 fps, ánh sáng đều, đầu và cuối cùng tư thế).
  - **Nhánh 2 (Từ 1 ảnh tĩnh — không cần quay clip)**: `inputs/linh-photo.jpg` (ảnh chân dung chính diện từ vai trở lên, kích thước tối thiểu 512 px, ánh sáng đều, môi khép tự nhiên).

## 2. File đầu ra
- Nhánh 1 (MuseTalk cho bài học): `work/course/04-lessons/<L>/avatar.mp4` (độ dài lệch so với `build/narration.wav` không quá `0,5` giây).
- Nhánh 2 (1 ảnh với `avatar_photo.py`): file video đầu ra theo tham số `--out` (ví dụ `work/course/m8/<engine>/L01-30s.mp4`) và dữ liệu thống kê thời gian chạy, FPS, đỉnh VRAM trong `work/course/m8/so-sanh.json`.

## 3. Lệnh engine cần chạy
### Nhánh 1 — Giảng viên từ video ngắn (`avatar_musetalk.py`)
```text
python src/plugin/linhx-course/engine/avatar_musetalk.py work/course/04-lessons/<L> --clip inputs/linh-face.mp4
```
### Nhánh 2 — Giảng viên từ 1 ảnh tĩnh (`avatar_photo.py`)
Chạy thử nghiệm hoặc sản xuất bằng engine `flashhead` (SoulX-FlashHead Lite) hoặc `joyvasa` (JoyVASA + LivePortrait):
```text
python src/plugin/linhx-course/engine/avatar_photo.py work/course/04-lessons/<L> --engine joyvasa --photo inputs/linh-photo.jpg --audio work/course/m8/L01-30s.wav --out work/course/m8/joyvasa/L01-30s.mp4
```
```text
python src/plugin/linhx-course/engine/avatar_photo.py work/course/04-lessons/<L> --engine flashhead --photo inputs/linh-photo.jpg --audio work/course/m8/L01-30s.wav --out work/course/m8/flashhead/L01-30s.mp4
```

## 4. Cổng duyệt
- **Trước khi chạy GPU**: Xác nhận đã có sẵn file `narration.wav` và không có tiến trình GPU nào khác đang chạy song song.
- **Sau khi chạy xong**: Kiểm tra độ dài `avatar.mp4` khớp với `narration.wav` (sai lệch `<= 0,5` giây) và trích xuất ảnh chụp khung hình (ở giây 60 đối với bài đầy đủ, hoặc giây 5, 15, 25 đối với bài đo kiểm 30 giây) vào `agy/bao-cao/` để người dùng chấm độ khớp môi bằng mắt.

## 5. Lỗi hay gặp và cách xử lý (từ thực tế vận hành)
- **Lỗi tràn bộ nhớ GPU (OOM) trên card 8 GB**: MuseTalk 1.5 ở chế độ `fp16` dùng đỉnh 6,90 GiB allocated / 7,03 GiB reserved trên RTX 4060 8 GB. Tuyệt đối không chạy hai tiến trình GPU cùng lúc.
- **Lỗi tải trọng số HuggingFace bị treo ở 0 byte**: Trên mạng cục bộ, `huggingface_hub` (cả `hf_xet` lẫn HTTP) có thể bị treo khi tải file lớn. Cách xử lý: dùng `curl -fSL -C - --retry 5` để tải tiếp (resume) về thư mục weights.
- **Lỗi cài đặt `chumpy` / `mmpose` khi tạo môi trường**: Khi cài đặt dependencies cho MuseTalk, cần cài `pip wheel "setuptools<70"` trước rồi cài `chumpy` với cờ `--no-build-isolation`.
- **Lỗi `nvidia-smi` luôn báo 0 MiB trên laptop WDDM**: Luôn đo VRAM thực tế bằng `torch.cuda.max_memory_allocated()` bên trong tiến trình Python.
