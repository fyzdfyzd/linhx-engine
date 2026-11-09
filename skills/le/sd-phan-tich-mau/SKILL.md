---
name: sd-phan-tich-mau
description: Phân tích một video mẫu (short drama, quảng cáo, trailer) theo 5 khía cạnh để lấy nhịp, khung hình, chuyển động máy cho tập của mình mà không sao chép. Dùng khi Linh đưa link hoặc file video tham khảo.
metadata:
  version: "0.1.0"
---

# sd-phan-tich-mau: học từ video mẫu

Học từ `video-reference-analyst` của OpenMontage. Mục đích là lấy **cấu trúc** (nhịp, cỡ cảnh, chuyển động máy), không chép nhân vật, thoại hay bố cục từng khung.

**Đầu vào:** file video ở `data/mau/` hoặc link. Nếu chỉ có link, nhờ Linh tải về hoặc chụp 6–10 khung.
**Đầu ra:** `data/mau/<ten>-phan-tich.md`, dùng cho `sd-de-xuat`, `sd-kich-ban`, `sd-storyboard`.

## Lấy khung (cần ffmpeg)
```
ffmpeg -i data/mau/<ten>.mp4 -vf "select='gt(scene,0.3)',scale=360:-1,tile=4x3" -frames:v 1 data/mau/<ten>-cat.jpg
ffmpeg -i data/mau/<ten>.mp4 -vf "fps=1,scale=240:-1,tile=6x5" -frames:v 1 data/mau/<ten>-1s.jpg
```
Ảnh thứ nhất là các điểm cắt cảnh; ảnh thứ hai là 1 khung/giây để đo nhịp. Claude đọc trực tiếp hai ảnh này.

Muốn máy khác xem cả video có tiếng: dùng **Gemini** (nhận MP4). ChatGPT Plus hiện không nhận file video (tháng 10/2026); nếu dùng ChatGPT thì tải hai ảnh trên và file âm thanh tách bằng `ffmpeg -i <ten>.mp4 -vn -c:a aac <ten>.m4a`.

## Bảng 5 khía cạnh (mỗi shot một dòng)
| Mốc | Chủ thể | Chuyển động chủ thể | Bối cảnh | Khung hình (cỡ cảnh, vị trí) | Máy quay |
|---|---|---|---|---|---|

## Rút ra
- Độ dài shot trung bình; hook làm gì trong 3 giây đầu; điểm sướng nằm ở giây nào; cliffhanger kết bằng gì.
- 3–5 "luật" mang sang tập của mình, viết thành câu dùng được ngay trong `sd-storyboard` (ví dụ: "mở bằng ECU vật thể rồi kéo ra WS trong 2 giây").
- Những gì **không** mang sang: nhân vật, câu thoại, logo, nhạc, bố cục đặc trưng nhận ra được.

Không gửi video mẫu lên công cụ tạo video làm tham chiếu trực tiếp (rủi ro bản quyền và giống bản gốc).
