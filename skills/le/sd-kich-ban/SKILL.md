---
name: sd-kich-ban
description: Bước 2 Flow Pack. Viết kịch bản một tập short drama 60–90 giây theo nhịp hook, điểm sướng mỗi 15 giây, cliffhanger, với thoại vừa clip Veo 8 giây. Dùng sau khi series bible đã duyệt.
---

# sd-kich-ban: kịch bản một tập

**Đầu vào:** `data/series/SERIES-BIBLE.md`, số tập.
**Đầu ra:** `data/<tap>/<tap>-kich-ban.md` (người đọc), làm nền cho `sd-storyboard`.

## Khuôn nhịp (bắt buộc, `kiem_nhip.py` sẽ kiểm lại)
| Mốc | Việc |
|---|---|
| 0–3 giây | **Hook**: hình gây sốc, câu hỏi, nguy hiểm. Không mở bằng giới thiệu |
| Mỗi 15 giây | Ít nhất 1 **điểm sướng**: thắng nhỏ, lật mặt, bị bắt quả tang, được công nhận |
| 8 giây cuối | **Cliffhanger** đúng kiểu hook cuối tập trong bible |

## Viết
- Chia tập thành **khối 8 giây** (mỗi khối sẽ là một lần tạo Veo). 60 giây ≈ 8 khối. Mỗi khối 1–3 shot.
- Mỗi khối: bối cảnh, tối đa 3 nhân vật, trạng thái mở, hành động, trạng thái kết.
- Thoại: **1 người nói mỗi shot**, câu ngắn, tối đa ~3 âm tiết mỗi giây của shot. Hội thoại hai người thì cắt shot/phản shot.
- Diễn xuất viết bằng cử động cơ thể ("tai giật, mắt mở bừng"), không bằng tính từ cảm xúc.
- Bảng trong file: `Khối | Thời gian | Bối cảnh | Nhân vật | Hình | Thoại | Nhịp (hook/sướng/cliff)`.

Dừng cho Linh đọc kịch bản trước khi sang `sd-tai-san`.
