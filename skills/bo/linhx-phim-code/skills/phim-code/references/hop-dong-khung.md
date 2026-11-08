# Hợp đồng khung: mỗi khung là hàm của t

Áp dụng cho Lemo và HTML một file; HyperFrames và Remotion đã tự theo hợp đồng này nếu không phá luật dưới đây. Nguồn: shipvideo, brag-slim, opus-visual-motion-engine, motion2code, huashu-motion (LAB060, LAB095).

## Luật
1. Trang có **một** hàm vẽ: `window.render(t)` (Lemo), `window.renderAt(t)`, `window.seek(t)` hoặc `window.anim = {duration, seek(t)}`. `t` tính bằng giây, kẹp trong `[0, DUR]` (không kẹp về `[0,1]`, phim sẽ đứng).
2. Khai độ dài: `window.DUR` (hoặc `anim.duration`).
3. Gọi hàm vẽ ở bất kỳ `t` nào, theo bất kỳ thứ tự nào, ra cùng một hình. Không giữ trạng thái giữa các khung (`x += 5` là sai).
4. **Cấm trong hàm vẽ**: `Math.random()` (dùng `mulberry32(seed)` tạo sẵn lúc dựng, hoặc băm theo khung `hash(Math.floor(t*24)*13+i)`), `Date.now()`, `performance.now()`, `setTimeout`/`setInterval`, CSS `animation`/`transition`, tải từ mạng. `requestAnimationFrame` chỉ được dùng để xem thử trong trình duyệt, khi `window.__QA` có thì không chạy.
5. Font, thư viện, ảnh nằm trong thư mục phim. Chờ font xong mới đặt `window.READY = true`.
6. Chữ trong DOM, hoặc khai `window.TEXTS(t)` trả `[{id,text,x0,y0,x1,y1}]` nếu vẽ chữ trên canvas, để bộ kiểm đo được chữ tràn.
7. Chữ trong khung 1080p không nhỏ hơn 20 px (H/54).
8. Số hiện trên màn hình đi qua `Math.round`/`toFixed`/`Intl.NumberFormat`; đếm số phải dừng đúng số cuối.
9. Kết phim bằng 1 giây dừng (khung cuối đã ổn định).

Đánh dấu cho bộ kiểm: `data-qa-cho-phep` (cố ý đè/tràn, ví dụ chữ bay qua máy quay), `data-qa-bo-qua` (chữ trang trí, không phải nội dung).

## Kiểm
```bash
node $SKILL/scripts/kiem_khung.mjs <phim>/index.html --size 960x540 --buoc 0.5 --out <phim>/kiem
# Lemo: trang dùng /core/lib.js nên phục vụ từ thư viện:  --goc "$LIB"
```
Nó soát mã nguồn, mở trang trong Chromium headless, khoá đồng hồ của trang, rồi:
- đếm `Math.random`/`Date`/`setTimeout` bị gọi **trong lúc vẽ** (LỖI với random);
- tua ngược và nhảy cóc 8 mốc, so điểm ảnh với lần đầu (LỖI nếu khác: trạng thái phụ thuộc khung trước);
- chữ ra ngoài khung (LỖI), chữ quá nhỏ, chữ đè chữ (CẢNH BÁO);
- font chưa tải hoặc thiếu dấu tiếng Việt (LỖI), đo bằng cách so độ rộng chữ có dấu với font dự phòng;
- khung đầu trống, khung trống giữa phim, đứng hình quá 3 giây, khung cuối còn chuyển động (CẢNH BÁO);
- lỗi JS và tài nguyên tải hỏng (LỖI).
Ra `kiem/bao-cao.md`, `bao-cao.json` (độ phủ và độ đổi từng mốc), `sheet.jpg`. Thoát 1 nếu có LỖI. Mỗi CẢNH BÁO: sửa, hoặc ghi một dòng lý do vào `TREATMENT.md`.

Sau render chạy `python3 $SKILL/scripts/kiem_video.py <phim>.mp4 --kho 16:9 --giay 30-45 --srt <phim>.srt`: khổ, cỡ, độ dài, LUFS (−14, chấp nhận −18…−12), đỉnh thật (≤ −1 dBTP), im lặng đầu phim, khung đen, đứng hình, khung đầu trơn, phụ đề dài hơn phim.

## Sửa nhanh như sửa tin nhắn
Học từ huashu-motion (chỉ vào khung để sửa) và vvv (khuôn điền chữ/ảnh):
- Mọi thứ Linh có thể muốn sửa có `data-id` ổn định (canvas thì có tên trong `TEXTS`/vùng). Không đổi tên id khi sửa chữ.
- Chữ, màu, thời gian dừng, tên sản phẩm đưa vào `bien.json`; trang đọc biến từ đó. Sửa một câu = sửa một biến rồi render lại, không đụng code.
- Cảnh đặt nhãn `canh:mo`, `canh:tinh-nang-1`... để Linh nói "cảnh tính năng 1, giây 12, chữ to hơn".
- Khi sửa: làm đúng chỗ và đúng giây Linh chỉ, giữ nguyên phần khác. Kéo dài một nhịp thì các mốc sau dời theo, neo vào cùng sự kiện. Mơ hồ thì chọn cách hiểu hợp lý nhất, làm, và ghi một dòng đã hiểu thế nào. Giữ bản cũ trong `lich-su/` để quay lại.
