---
name: le-bich-hoat-hinh
description: Vẽ nhân vật Lê Bích bụng phệ bằng code từ bộ rời gốc (PSD của tác giả) để làm trang truyện, sticker động, clip hoạt hình. Dùng khi được nhờ vẽ, làm truyện, sticker hay animation Lê Bích.
---

# Lê Bích bụng phệ: vẽ bằng code từ bộ rời gốc

Lê Bích bụng phệ là nhân vật truyện tranh của tác giả Lê Bích. Skill này mang theo **bộ rời gốc** của nhân vật (tách từ file PSD của tác giả): đầu, tóc, râu, thân, tay trái, tay phải, hai chân, 6 kiểu mắt, 6 kiểu miệng. Mọi hình nhân vật phải ghép từ các mảnh này.

## Luật cứng
1. **Không tự vẽ lại Lê Bích**, không dùng mô hình sinh ảnh hay video để vẽ nhân vật. Chỉ ghép, xoay, co giãn nhẹ các mảnh gốc. Tác giả đã từ chối bản vẽ lại vì "xấu, sai nhân vật".
2. Đạo cụ, bối cảnh, bóng thoại thì được vẽ bằng code (Pillow hoặc SVG), nét đen dày `#111` khoảng 4–5px, tô trắng, nền xám `#c9c9c9`, cho hợp nét gốc.
3. Chữ tiếng Việt phải đủ dấu: dùng font đi kèm (`font()` trong `scripts/lebich.py`, hoặc Patrick Hand). Không dùng font mặc định của máy.
4. Không cần mạng: mọi thứ cần đều có trong skill.

## Bước 0: xem máy có gì
Chạy `bash scripts/kiem-tra.sh`, rồi chọn đường:
- **Đường A (mặc định, chắc chạy):** Python + Pillow, dùng `scripts/lebich.py`. Ra PNG, GIF, WebP động; MP4 nếu có ffmpeg.
- **Đường B (chỉ khi có Chrome + playwright):** HTML + GSAP với `assets/lebich-rig.js`, `assets/rig-data.js`, `assets/gsap.min.js`; tua timeline tới từng khung, chụp, rồi ghép bằng ffmpeg.

Thử nhanh: `python3 scripts/lebich.py thu bang.png` (bảng 7 biểu cảm) và `python3 examples/vay-tay.py ra/` (vẫy tay 1 giây, lặp liền). Nhìn kết quả trước khi làm bài thật.

## Đường A: API Python
```python
import sys; sys.path.insert(0, "scripts")
from lebich import nhan_vat, chu, bong_thoai, font, MAT, MIENG
nv = nhan_vat(mat="cuoi", mieng="ha", tay_trai=60, tay_phai=-100, dau=5, bung=1.04, rong=400, le=0)
# nv là ảnh RGBA nền trong; dán lên khung: khung.paste(nv, (x, y), nv)
```
- `mat`: `cham` (bình thường, hai chấm), `hoang` (hoảng, quầng thâm), `tron` (mắt tròn trợn), `ngan` (lim dim, đắc ý), `cuoi` (mắt cười), `buon` (buồn).
- `mieng`: `cuoi`, `ngai` (ngại), `chu` (chu môi), `thang` (mím thẳng, sốc), `ha` (há cười to), `le` (lè lưỡi).
- `tay_trai` xoay quanh vai trái, `tay_phai` xoay quanh vai phải, đơn vị độ, dương là chiều kim đồng hồ. Giơ tay phải lên cao: `tay_phai` khoảng -150; dang ngang: khoảng -100. Tay trái nằm sau thân, giơ cao dễ che mặt, nên ưu tiên tay phải.
- `dau`: nghiêng đầu quanh cổ (độ, nên trong khoảng -8 đến 8).
- `bung`: nhún bụng, 1.0 là thường, 1.03–1.06 là phình. Dùng cho vỗ bụng, bụng nảy.
- `le`: nới khung cắt mỗi phía (0–200) khi tay giơ ra ngoài; `dx`, `dy` dời nhân vật trong khung.
- `chu(ve, xy, noi_dung, co, vien=6)` viết chữ, `vien` cho chữ sticker viền trắng. `bong_thoai(ve, hop, noi_dung, duoi=(x, y))` vẽ bóng thoại có đuôi chỉ vào miệng.
- Ảnh ra cao bằng `rong * (620 + 2*le) / (400 + 2*le)`. Miệng nhân vật nằm khoảng 38% chiều rộng tính từ trái, 47% chiều cao tính từ trên (khi `le=0`).

## Diễn hoạt kiểu cut-out
- Mỗi khung gọi `nhan_vat(...)` với tham số nội suy theo thời gian (sin, ease), không vẽ lại.
- Nháy mắt: đổi `mat` sang `cuoi` hoặc `ngan` trong 2–3 khung. Nói: đổi `mieng` giữa `ha` và `cuoi` mỗi 3–4 khung.
- Đi lạch bạch: không có chân rời từng khớp, nên làm bằng nhún `bung`, lắc `dau`, dời `dx` và nảy `dy` theo nhịp.
- Lặp liền: dùng pha `p = i / n` (khung cuối không trùng khung đầu) và hàm tuần hoàn của `p`.
- Xuất: GIF bằng `Image.save(save_all=True, loop=0, disposal=2)`; WebP động nếu Pillow hỗ trợ; MP4 bằng `ffmpeg -framerate 30 -i f%04d.png -c:v libx264 -pix_fmt yuv420p`.

## Tự kiểm trước khi gửi
Mở ảnh ra xem lại (ít nhất khung đầu, giữa, cuối) và kiểm:
- Đầu hạt đậu cằm đưa trái, tai to, chỏm tóc đen dựng, râu cằm, bụng phệ rốn chữ "c", tay chân que.
- Không mảnh nào bị cắt cụt (tay giơ thì tăng `le`).
- Chữ đủ dấu, không tràn khỏi bóng thoại.
- Clip đúng kích thước và độ dài; sticker lặp không giật.

Gửi kèm: mã nguồn, file đầu ra, và 3 dòng tự nhận xét chỗ chưa được.

## Tệp trong skill
- `scripts/lebich.py`: ghép nhân vật, font, chữ, bóng thoại.
- `scripts/kiem-tra.sh`: xem máy có Pillow, ffmpeg, Chrome không.
- `examples/vay-tay.py`: mẫu sticker vẫy tay lặp.
- `assets/rig-data.js`: bộ rời gốc (PNG dạng base64) và toạ độ trong khung PSD 462×1348; dùng chung cho cả hai đường.
- `assets/lebich-rig.js`, `assets/gsap.min.js`: cho đường B (HTML). `LB.makeLeBich({eyes, mouth, armL, armR, head, w})` trả HTML, cùng tên mắt/miệng như trên.
- `assets/font-patrick-hand-vn.b64.txt`: font Patrick Hand đủ dấu tiếng Việt (giấy phép SIL OFL), dạng base64.
