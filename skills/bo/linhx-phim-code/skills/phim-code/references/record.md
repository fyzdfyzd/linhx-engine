# Nhánh B: dựng video YouTube từ file record (HyperFrames)

Học từ video "Hướng dẫn làm video Youtube với Opus 5.5" (kênh Zuey, 25/10/2026, https://youtu.be/P7M1ObSV6Xo). Cách làm của video: quay một file record (mặt người nói + màn hình), đưa cho Claude một đề duy nhất, Claude dựng bằng HyperFrames ra bản đăng YouTube. Đề gốc ở `khuon/DE-BAI-RECORD.md`.

Khác nhánh A (phim 100% code): ở đây **người thật là chính Linh trong file record**, nên được dùng. Vẫn không tạo người giả.

## Các bước

1. **Nhận record + đề.** Chép `khuon/DE-BAI-RECORD.md` vào thư mục phim, điền đường dẫn record. Hỏi một lần: khổ (16:9 YouTube hay 9:16 Shorts), có file màn hình riêng không, logo/màu kênh.
2. **Cắt hư, làm lại, ậm ờ.** `python3 $SKILL/scripts/cat_record.py record.mp4 cat/ --chi-xem` → đọc `cat/cat.json` (đoạn bỏ kèm lý do và lời). Sai thì sửa `words.json` hoặc hằng số `NGAT`, `TRUNG` rồi chạy lại không có `--chi-xem` → `sach.mp4`, `phu-de.json`, `phu-de.srt`. Chép lời bằng faster-whisper `large-v3` (chạy trên máy Linh, `pip install faster-whisper`), máy yếu thì `WHISPER_MODEL=medium`.
   - Luật cắt: câu nào bắt đầu bằng 3 chữ giống câu sau là bản hỏng, bỏ; câu có "làm lại / nói lại / sai rồi" bỏ cùng câu trước; tiếng đệm (ờ, ừm, à...) và im lặng dài bị cắt, chừa 0,25 giây cho tự nhiên.
3. **Bảng cảnh theo lời.** Đọc `phu-de.json`, chia nhịp. Mỗi nhịp chọn một trong bốn khung: **talking head** (mặt toàn khung, chữ nhấn), **PiP** (màn hình/đồ hoạ toàn khung, mặt góc dưới, bo tròn), **motion graphic** (khái niệm, không mặt, giọng vẫn chạy), **infographic động** (số liệu, so sánh, các bước). Đổi khung ít nhất mỗi 8–12 giây.
4. **Không dùng ảnh chụp màn hình nguyên tấm.** Tách thành phần giao diện (nút, ô nhập, thẻ, biểu tượng) dựng lại bằng HTML/CSS, mỗi phần có chuyển động riêng (stagger, scale từ 0.9, trượt 20–40px, ease `power3.out` / `back.out(1.4)`). Cần đúng giao diện thì chụp website bằng HyperFrames rồi cắt từng vùng.
5. **Phụ đề sống tiếng Việt.** Từ `phu-de.json`: hiện 4–7 chữ một dòng, chữ đang nói tô màu nhấn hoặc nảy nhẹ. Font có dấu (`font_viet.sh`), viền/đổ bóng cho dễ đọc trên mặt người, đặt tránh vùng mặt và vùng PiP.
6. **Nhạc nền + SFX.** Nhạc chill không lời, −28 đến −24 LUFS dưới giọng (ducking), cắt theo nhịp cảnh. SFX ngắn (whoosh khi chuyển khung, pop khi hiện thẻ, click khi hiện nút), không quá 1 SFX mỗi 2 giây. Ghi nguồn vào `CREDITS` (Pixabay, YouTube Audio Library).
7. **Dựng HyperFrames.** `sach.mp4` là `<video id="cam" data-start="0">` chạy suốt; khung PiP chỉ đổi vị trí/kích thước của chính video đó (tween `width/height/left/top`, không cắt video ra nhiều file). Mỗi khung là một sub-composition. Kiểm như nhánh A: `npx hyperframes check` 0 lỗi, contact sheet, −14 LUFS tổng.
8. **Giao.** Như nhánh A, thêm `cat.json` (để Linh xem đã bỏ gì) và `chuong.txt` (mốc chương YouTube lấy từ bảng cảnh).

## Chất lượng chuyển động (yêu cầu của đề)
Làm như bản sản xuất thật, không phải demo: mọi thứ hiện ra đều có chuyển động vào/ra; có lực nhưng tinh tế (overshoot nhỏ, không lắc lư); một nhịp nhấn mạnh mỗi cảnh, còn lại tĩnh để đọc; giữ một bảng màu và một kiểu ease cho cả video.
