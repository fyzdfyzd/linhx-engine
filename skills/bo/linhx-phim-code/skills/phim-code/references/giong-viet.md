# Giọng Việt, font, phụ đề

## Giọng: edge-tts
- Cài: `pip install edge-tts` (cần mạng tới Microsoft khi chạy; cloud Claude Code bị chặn, máy Linh chạy được).
- Giọng: `vi-VN-HoaiMyNeural` (nữ, mặc định), `vi-VN-NamMinhNeural` (nam). Chỉ có hai giọng.
- Lệnh: `python3 $SKILL/scripts/giong_viet.py loi.json am-thanh/ [--giong nam] [--toc +0%] [--nghi 0.35] [--nhap]`
  - Ra: `<id>.wav` từng câu, `giong.wav` nối sẵn (có khoảng nghỉ), `dur.json`, `cues.json` (`[{id,t0,t1,text}]`), `phu-de.srt`.
  - `--nhap`: không gọi mạng, ước thời lượng (khoảng 4,2 âm tiết/giây) và tạo tiếng im; để dựng hình trước khi có giọng thật. Chạy lại không `--nhap` trên máy có mạng, cảnh sẽ khớp nếu dựng theo `cues.json`.
  - Bộ đệm theo nội dung câu: sửa một câu chỉ đọc lại câu đó.
- Lemo có sẵn `core/tts/tts_zh.py` cũng gọi edge-tts; đưa `"voice": "vi-VN-HoaiMyNeural"` vào từng dòng là dùng được, nhưng script của skill này ra thêm `giong.wav`, `cues.json`, `srt` cho cả ba máy.

## Viết lời cho máy đọc
- Câu ngắn, 8–18 âm tiết. Một ý một câu.
- Số, ký hiệu, viết tắt: điền trường `say` cách đọc ("2026" → "hai nghìn không trăm hai mươi sáu", "AI" → "ây ai", "%" → "phần trăm"); `text` giữ cách viết cho phụ đề.
- Tên riêng nước ngoài: phiên âm trong `say`.
- Nghe lại những câu có tên riêng và số. Muốn kiểm tự động: `faster-whisper` model `small` (tiếng Việt) rồi so với `text`, chấp nhận sai lệch nhỏ.

## Font có dấu
- `sh $SKILL/scripts/font_viet.sh <phim>/fonts` tải Be Vietnam Pro (600), Noto Serif (nghiêng), Lora, Dancing Script từ Google Fonts (OFL) bản TTF đầy đủ.
- Thử dấu chồng ở cỡ lớn: "Nhà cổ trăm năm, ặ ỗ ữ ỹ".
- Ghi font vào `CREDITS` (OFL, Google Fonts).

## Phụ đề
- Mặc định có, đốt vào hình theo luật chữ của STYLE.md, đồng thời giao `.srt`.
- Tối đa 2 dòng, khoảng 42 ký tự/dòng, giữ trên màn hình ≥ max(1,5 giây, thời lượng câu + 0,4 giây).
- Không đè lên hành động chính; đặt trong khoảng trống của khung.
