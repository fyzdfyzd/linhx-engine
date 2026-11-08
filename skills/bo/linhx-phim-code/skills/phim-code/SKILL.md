---
name: phim-code
description: Dựng phim ngắn bằng code (canvas/WebGL, HTML/GSAP, React) với một quy trình chung và nhiều style để chọn, máy dựng là Lemo-Opuscar, HyperFrames hoặc Remotion, giọng Việt qua edge-tts. Dùng khi Linh muốn làm phim, clip bán hàng/ra mắt sản phẩm, video giải thích, e-learning, hoạt hình, MV theo bài hát, reel dọc, motion graphic, intro, phim dữ liệu, làm giống một video mẫu, hoặc hỏi có những style phim nào. Cũng dùng khi Linh đưa file record (mặt người nói + màn hình) để dựng video YouTube: cắt hư, ậm ờ, phụ đề sống, PiP, nhạc, SFX. Không dùng để tạo người giả hay nhân vật diễn xuất (việc của Veo/Flow, LAB016).
---

# phim-code: một quy trình, ba máy dựng, nhiều style

Claude không vẽ ra pixel. Claude viết chương trình vẽ từng khung, trình duyệt headless chụp từng khung, ffmpeg ghép. Ba máy dựng dùng chung một quy trình; khác nhau ở cách viết trang.

Thư mục skill này gọi là `$SKILL`. Thư viện style Lemo-Opuscar gọi là `$LIB` (mặc định `~/lemo-opuscar`).

## Luật cứng
- **Không tạo người giả, không nhân vật diễn xuất tự nhiên.** Cần thì báo Linh và chuyển sang Veo/Flow. Người thật chỉ được có khi là file record Linh đưa (nhánh B).
- **Giọng Việt chỉ qua edge-tts** (`vi-VN-HoaiMyNeural` nữ, `vi-VN-NamMinhNeural` nam), cần mạng. Không có mạng tới Microsoft (ví dụ trên cloud) thì dùng `--nhap` để có lưới thời gian, lồng giọng thật trên máy Linh.
- **Font phải có dấu tiếng Việt.** Font sẵn của Lemo (Fredoka, Lilita, IM Fell, ZCOOL) thiếu dấu. Chạy `sh $SKILL/scripts/font_viet.sh <thư-mục-phim>/fonts` rồi dùng font trong đó.
- **Thử nhỏ trước**: khung tĩnh rồi nháp 960×540, 12 fps trước khi render 1080p 24 fps.
- Không để `node_modules` trong thư mục chung `/mnt/project-files`. Cài vào thư viện hoặc thư mục tạm.
- Phim làm ra là của Linh: không ghi công LemoLab, không watermark. Ghi `CREDITS` cho font, nhạc, giọng.

## Bước 0: loại video và nhánh
Xác định loại video theo bảng đầu `references/loai-video.md` (bán hàng, giải thích, hoạt hình/ca nhạc, clip dọc, bắt chước mẫu, dựng từ cảnh quay) và đọc mục của loại đó: nó quyết định độ dài, cấu trúc, điểm dừng duyệt và kiểm thêm. Rồi đi một trong ba nhánh:
- **Nhánh A, phim 100% code**: 8 bước dưới đây.
- **Nhánh B, có file record hoặc cảnh quay** (Linh tự quay, muốn đăng YouTube, hoặc cắt clip dọc từ video dài): theo `references/record.md`, máy dựng HyperFrames, cắt bằng `scripts/cat_record.py`, đề mẫu `khuon/DE-BAI-RECORD.md`.
- **Nhánh C, làm giống video mẫu**: theo `references/bat-chuoc.md`, mổ mẫu bằng `scripts/hoc_mau.sh`, dựng bản trung thành rồi thay nội dung của Linh.

Ghi tiến độ vào `TRANG-THAI.md` trong thư mục phim sau mỗi bước (bước đã xong, đang làm, còn mở) để phiên sau làm tiếp được.

## Quy trình 8 bước (nhánh A)

1. **Đề bài, hỏi một lần.** Chép `$SKILL/khuon/DE-BAI.md` vào thư mục phim, điền những gì Linh đã nói, hỏi một tin duy nhất những gì còn thiếu (sự thật về chủ đề, tư liệu có sẵn, độ dài, khổ dọc hay ngang, giọng nam/nữ, có muốn duyệt storyboard không). Phần còn lại tự điền mặc định: 30–45 giây, 1920×1080, 24 fps, giọng nữ, phụ đề có. Hỏi xong không hỏi thêm.
2. **Chọn style.** Đọc `references/style.md`. Linh đã nêu style thì tra ra thư mục; chưa nêu thì gợi ý 2–3 style hợp chủ đề và đưa link gallery. Đọc `STYLE.md` của style đó (bất biến về hình, màu, chữ, chuyển động, âm thanh). STYLE.md là luật hình, dùng được cho cả ba máy.
3. **Chọn máy dựng.** Theo bảng trong `references/may-dung.md`. Nhanh: tranh vẽ, chất liệu, 3D → **Lemo**; chữ, bố cục, bài giảng, slide thành video, ra mắt sản phẩm → **HyperFrames**; một khuôn ra nhiều bản từ dữ liệu → **Remotion**. Lemo và trang HTML một file phải theo `references/hop-dong-khung.md` (mỗi khung là hàm của t). Phim theo nhạc: chạy `python3 $SKILL/scripts/nhip_nhac.py nhac.mp3 --js` để có phách, cú đánh, độ to từng khung, cắt cảnh trên phách.
4. **Kịch bản + giọng trước.** Viết `loi.json` (`[{id, text, say?}]`, mỗi câu một cảnh hoặc một nhịp). Chạy `python3 $SKILL/scripts/giong_viet.py loi.json am-thanh/` → `giong.wav`, `cues.json`, `phu-de.srt`, `dur.json`. Giọng là lưới thời gian: cảnh khớp theo `cues.json`, không đoán.
5. **Treatment + bảng cảnh.** Viết `TREATMENT.md` theo `$LIB/DIRECTOR.md` §3–4: ba cấu trúc, chọn một, logline, móc 3 giây đầu, một "nước đi riêng" của chất liệu ở cao trào, bảng cảnh (khung, góc, chuyển động máy, giây, vì sao). Viết **trước** khi mở demo của style. Linh muốn duyệt storyboard thì dừng ở đây chờ.
6. **Khung mẫu.** Dựng 2–3 khung tĩnh bằng code thật (không phải ảnh AI), xem bằng mắt, so với STYLE.md, sửa đến khi đúng chất. Loại bán hàng và hoạt hình: đưa Linh ba hướng + khung mẫu, chờ chọn (xem `loai-video.md`).
7. **Dựng + nháp.** Dựng đủ cảnh, chạy `kiem_khung.mjs` tới khi 0 LỖI, render nháp nhỏ, giao agent duyệt độc lập (`references/duyet.md`), sửa tối đa 2 vòng, rồi mới render bản đủ, ghép tiếng và chạy `kiem_video.py`.
8. **Giao.** Trong thư mục phim: `<ten>.mp4`, `poster.jpg`, `<ten>.srt`, `TREATMENT.md`, `CREDITS`, mã nguồn + `build.sh` một lệnh. Báo Linh đường dẫn, độ dài, chỗ còn yếu.

## Kiểm trước khi giao
Kiểm bằng số trước, bằng mắt sau. Script thoát 1 khi có LỖI; LỖI thì phải sửa, CẢNH BÁO thì sửa hoặc ghi một dòng lý do.
- **Trang** (Lemo, HTML một file, HyperFrames dạng `__timelines`): `node $SKILL/scripts/kiem_khung.mjs <phim>/index.html --out <phim>/kiem` (Lemo thêm `--goc "$LIB"`). Bắt: random/đồng hồ trong lúc vẽ, tua lại ra hình khác, chữ tràn khung, chữ quá nhỏ hoặc đè nhau, font chưa tải hoặc thiếu dấu Việt, khung đầu trống, đứng hình quá 3 giây, lỗi JS. Ra `sheet.jpg` + `bao-cao.md`.
- **Video**: `python3 $SKILL/scripts/kiem_video.py <ten>.mp4 --kho 16:9 --giay 30-45 --srt <ten>.srt`. Bắt: sai khổ, sai độ dài, LUFS ngoài −18…−12, đỉnh thật trên −1 dBTP, im lặng đầu, khung đen, đứng hình, khung đầu trơn (ảnh bìa trống), phụ đề dài hơn phim.
- **Mắt**: `sh $SKILL/scripts/to_sheet.sh <video.mp4>` → contact sheet 12 khung, xem một lượt: chữ tràn, dấu vỡ, khung đen, chữ đè hình chính.
- **Duyệt độc lập**: agent ngữ cảnh sạch chấm theo `references/duyet.md`, mọi điểm ≥ 8.
- Chữ trên màn hình đủ lâu để đọc: Lemo có `node core/render/readcheck.mjs`; máy khác tự tính, tối thiểu số ký tự ÷ 15 + 1,5 giây.
- HyperFrames: `npx hyperframes check` phải 0 lỗi. Remotion: `npx remotion still` vài khung trước khi render.
- Tiếng khoảng −14 LUFS (`$LIB/core/render/mux.sh` làm sẵn), phụ đề khớp giọng.
- Không giống demo của style: so cấu trúc, mở, cảnh đinh, đường máy, nhạc, kết; ít nhất 4/6 phải khác.

## Chia việc Claude và agy
Phim dài hoặc làm loạt (nhiều tập, nhiều biến thể) thì Claude làm bước 1–6 và một cảnh mẫu chuẩn, rồi viết đề chạy đêm cho agy theo `references/dem-agy.md`. Sáng ra Claude chỉ xem contact sheet và `SANG-NAY.md`.

## Tài liệu kèm
- `references/style.md`: danh mục style, gợi ý theo chủ đề Việt.
- `references/may-dung.md`: chọn máy, cài đặt, hợp đồng trang và lệnh render của từng máy, bẫy đã gặp.
- `references/giong-viet.md`: edge-tts, viết lời cho dễ đọc, font, phụ đề.
- `references/dem-agy.md`: khuôn đề cho agy chạy đêm.
- `references/record.md`: nhánh B, dựng video YouTube từ file record.
- `references/loai-video.md`: khuôn cho 6 loại video (bán hàng, giải thích, hoạt hình/ca nhạc, clip dọc, bắt chước, cảnh quay).
- `references/hop-dong-khung.md`: luật "mỗi khung là hàm của t", cách kiểm, cách sửa nhanh bằng `bien.json` + `data-id`.
- `references/bat-chuoc.md`: nhánh C, dựng lại video mẫu thành code.
- `references/duyet.md`: agent duyệt độc lập, rubric, dấu hiệu rập khuôn.
- `scripts/kiem_khung.mjs`, `scripts/kiem_video.py`: kiểm tự động trang và MP4.
- `scripts/nhip_nhac.py`: nhạc → BPM, phách, cú đánh, độ to từng khung (ffmpeg + numpy).
- `scripts/hoc_mau.sh`: video mẫu → khung 0,25 giây, contact sheet, điểm cắt, dải vùng.
- `scripts/cat_record.py`: chép lời (faster-whisper), cắt hư/làm lại/ậm ờ, ra `sach.mp4` + phụ đề từng chữ.
- `khuon/DE-BAI.md`, `khuon/loi.json`: khuôn đề bài và lời.
