# Nhánh C: dựng lại video mẫu thành code

Dùng khi Linh gửi video mẫu (file, hoặc link X/TikTok/Douyin đã tải về) và muốn "làm giống thế này" cho chủ đề của mình. Học từ motion2code, animation-reverse-engineering, motion-prompt, vvv (LAB095).

**Giới hạn**: học nhịp, cách chuyển động, bố cục; không chép logo, nhân vật, chữ, nhạc, cảnh quay của mẫu. Phim ra là của Linh, ghi "phong cách tham khảo từ …" trong `CREDITS` nếu đăng công khai. Không tải được link (YouTube bị chặn trên cloud và máy ảo) thì nhờ Linh tải file về.

## Bước
1. **Phân loại**: chuyển động theo thời gian (intro, chữ chạy, logo) hay theo thao tác (cuộn, kéo, bấm)? Một cảnh hay nhiều cảnh cắt?
2. **Mổ mẫu**: `sh $SKILL/scripts/hoc_mau.sh mau.mp4 hoc-mau` → thông số (fps, cỡ, độ dài), khung mỗi 0,25 giây có đánh giờ, contact sheet 6 giây/tấm, danh sách điểm cắt. Xem từng tấm sheet.
3. **Đo chỗ khó**: đoạn chuyển động nhanh thì cắt dải một vùng: `--vung x:y:w:h --tu 3.0 --den 4.5` → 24 khung liền xếp dọc, đo vị trí từng khung để suy ra đường cong (easing). Đo, không đoán.
4. **Bảng nhịp** (`NHIP-MAU.md`), mỗi dòng một nhịp: khoảng thời gian; vật gì làm gì; thuộc tính đổi (vị trí, mờ, cỡ, xoay, nhoè, giãn chữ); thứ tự so le (xuôi, ngược, từ giữa ra); bao nhiêu vật cùng đang chuyển; vào nhanh ra chậm hay ngược lại; vật nào **không** chuyển động; chuyển sang nhịp sau bằng gì. Gọi tên chuyển động theo thư viện motion-prompt (showheyohtaki.github.io/motion-prompt) nếu khớp, để lần sau ra lệnh bằng tên.
5. **Dựng bản trung thành trước**: cùng cỡ, cùng độ dài, hình khối đơn giản thay cho nội dung, theo `hop-dong-khung.md`. Mở `so-sanh.html` (hai bên: video mẫu và trang code, cùng một thanh tua) để so từng nhịp.
6. **So**: xuất contact sheet bản code cùng mốc với mẫu (`kiem_khung.mjs --buoc 0.25`), đặt cạnh sheet mẫu, sửa đến khi nhịp khớp trong 2 khung. Vòng lặp (loop) thì khung cuối phải trùng khung đầu.
7. **Thay nội dung của Linh**: chữ, màu, ảnh, logo, giọng. Giữ nhịp, đổi chất.
8. **Ghi lại**: `NHIP-MAU.md` + tên chuyển động thêm vào thư viện nhịp của Linh để lần sau dùng lại.

## so-sanh.html tối thiểu
```html
<div style="display:flex;gap:8px"><video id="v" src="mau.mp4" muted style="width:50%"></video><iframe id="f" src="index.html" style="width:50%;aspect-ratio:16/9;border:0"></iframe></div>
<input id="s" type="range" min="0" max="1000" style="width:100%">
<script>const v=document.getElementById('v'),f=document.getElementById('f'),s=document.getElementById('s');
s.oninput=()=>{const t=s.value/1000*v.duration;v.currentTime=t;const w=f.contentWindow;(w.render||w.renderAt||w.seek||(x=>w.anim.seek(x)))(t)};</script>
```
