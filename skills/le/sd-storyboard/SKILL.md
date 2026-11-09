---
name: sd-storyboard
description: Bước 4 Flow Pack. Chuyển kịch bản thành các đoạn Veo 4/6/8 giây có nhiều shot theo mốc thời gian, chọn chế độ Flow và model cho từng đoạn, rồi chạy kiem_nhip.py. Dùng sau sd-tai-san.
metadata:
  version: "0.1.0"
---

# sd-storyboard: đoạn Veo và shot

**Đầu ra:** mảng `doan` trong `data/<tap>/<tap>.json`. Chạy `python LAB016-PHIM-NGAN-AI/src/tools/kiem_nhip.py LAB016-PHIM-NGAN-AI/data/<tap>/<tap>.json` cho tới khi **ĐẠT**.

## Mỗi đoạn
`id` (`E01-D03`), `giay` (4/6/8), `che_do`, `model`, `vai_tro` (chinh/phu/hero), `nhan_vat` (≤ 3), `boi_canh`, `keyframe_dau` (bắt buộc với frames có nhân vật), `vao`, `shots`, `am_nen`, `ra`.

## Mỗi shot
`t` (`00:03-00:06`, phủ kín đoạn, ≥ 1,5 giây), `co_canh`, `may` (một chuyển động máy), `hanh_dong` (tiếng Anh, chỉ mô tả thay đổi theo thời gian), `thoai` {ai, cach_noi, cau tiếng Việt} nếu có, `sfx`, `nhip` (hook/suong/cliff).

## Chọn chế độ và model (gói Ultra)
| Trường hợp | Chế độ | Model |
|---|---|---|
| Có nhân vật, cần bố cục chính xác | `frames` | Fast (10) |
| 2–3 nhân vật tương tác, không cần bố cục cứng | `ingredients` | Fast (10) |
| Cảnh không nhân vật, chuyển cảnh | `text` | Lite (5) hoặc Lite Lower Priority (0) |
| 1 shot đẹp nhất tập (thường là cliffhanger) | `frames` | Quality (100), `luot_du_kien: 1` |

**Tiết kiệm:** gộp 2–3 shot vào một đoạn 8 giây thay vì mỗi shot một clip; giữ trạng thái `ra` của đoạn trước khớp `vao` của đoạn sau; không dùng Extend để kéo dài shot.
