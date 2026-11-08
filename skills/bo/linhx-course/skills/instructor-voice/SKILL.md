---
name: instructor-voice
description: Dùng khi cần tổng hợp lời giảng tiếng Việt cho từng phân đoạn bài học bằng VieNeu-TTS (giọng preset hoặc giọng clone của giảng viên) và kiểm tra chất lượng phát âm tự động bằng ASR.
---
# Tổng hợp giọng giảng viên và kiểm lời (`instructor-voice`)

Skill này sử dụng mô hình VieNeu-TTS v3 Turbo tự chạy trên máy để đọc từng đoạn lời giảng trong `segments.json` thành file âm thanh `.wav`, ghi mốc thời lượng `timing.json`, và dùng mô hình nhận dạng tiếng nói (ASR) đối chiếu lại để phát hiện sớm từ đọc sai.

## 1. File đầu vào
- `work/course/04-lessons/<L>/segments.json`: danh sách các đoạn lời giảng của bài học.
- `work/course/04-lessons/<L>/pronunciation.yaml`: danh mục các thuật ngữ tiếng Anh cần bọc thẻ `<en>...</en>`.
- Cấu hình giọng trong `work/course/course.json`: dùng giọng có sẵn (`preset:Hải Đăng`) hoặc giọng nhân bản (`clone:linh` kèm file mẫu `inputs/linh-voice.wav` / hồ sơ `work/course/voices/linh/`).
- File cấu hình `work/course/engine.json` chỉ định đường dẫn `vieneu_python` và `hf_home`.

## 2. File đầu ra
- `work/course/04-lessons/<L>/audio/<seg_id>.wav`: các file âm thanh tần số 48 kHz tương ứng với từng đoạn trong `segments.json`.
- `work/course/04-lessons/<L>/timing.json`: thông tin thời lượng chi tiết của từng đoạn âm thanh và tổng thời lượng bài học.
- `work/course/04-lessons/<L>/asr.json`: kết quả nhận dạng lại từng đoạn âm thanh kèm điểm sai số ký tự (CER) để kiểm tra chất lượng phát âm.

## 3. Lệnh engine cần chạy
Bước 1 — Tổng hợp giọng đọc bằng VieNeu-TTS (chú ý bắt buộc dùng cờ `-I -X utf8` khi gọi Python của VieNeu):
```text
python src/plugin/linhx-course/engine/tts_vieneu.py work/course/04-lessons/<L> --voice "Hải Đăng"
```
Hoặc khi đã có mẫu giọng thật của giảng viên (5–8 giây):
```text
python src/plugin/linhx-course/engine/tts_vieneu.py work/course/04-lessons/<L> --ref-audio inputs/linh-voice.wav
```
Bước 2 — Chạy kiểm lời tự động bằng ASR (không chạy đồng thời với MuseTalk):
```text
python src/plugin/linhx-course/engine/asr_check.py work/course/04-lessons/<L>
```

## 4. Cổng duyệt
- Kiểm tra kết quả `asr.json`: sai số ký tự trung bình (CER) của cả bài phải `<= 0,15`.
- Nếu có đoạn nào có `CER > 0,30`, **tuyệt đối không sửa file âm thanh bằng tay** và không sửa chữ trong `asr.json`. Phải sửa lại cách viết trong `slides.md` hoặc bổ sung từ vào `pronunciation.yaml`, xoá file `.wav` của đoạn bị lỗi rồi chạy lại `tts_vieneu.py` và `asr_check.py`.

## 5. Lỗi hay gặp và cách xử lý (từ thực tế vận hành)
- **Lỗi `UnicodeEncodeError` trên cửa sổ dòng lệnh Windows (`cp1252`)**: Khi chạy Python với cờ `-I` (isolated mode), biến `PYTHONIOENCODING` bị bỏ qua khiến việc in tên giọng tiếng Việt ("Hải Đăng") bị lỗi. Cách xử lý: luôn truyền `-X utf8` (`python.exe -I -X utf8 ...`).
- **Lỗi đánh vần từ tiếng Anh viết hoa**: Từ `SKILL` không có thẻ `<en>` sẽ bị đọc thành "ét ca i lờ lờ", từ `MD` đọc thành "mờ đê". Luôn kiểm tra `pronunciation.yaml` trước khi chạy TTS.
- **Lưu ý độ dài mẫu giọng clone**: VieNeu-TTS tự động cắt mẫu âm thanh tham chiếu ở mức tối đa 8 giây; do đó chỉ cần chọn đoạn thu âm sạch, tự nhiên dài 5–8 giây trong phòng yên tĩnh.
