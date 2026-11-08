---
name: sd-flow-pack
description: Bước 5 Flow Pack. Xuất phiếu render cho Google Flow từ JSON tập đã ĐẠT kiem_nhip, kèm bảng duyệt credit; Linh dán tay vào Flow. Dùng khi tập sẵn sàng render.
---

# sd-flow-pack: xuất phiếu render

Chạy: `python LAB016-PHIM-NGAN-AI/src/tools/flow_pack.py LAB016-PHIM-NGAN-AI/data/<tap>/<tap>.json --goi ultra`
Ra `FLOW-PACK-<tap>.md` và `<tap>.pack.json` cạnh file JSON.

## Trước khi đưa cho Linh
1. Đọc lại bảng chi phí; so với `ngan_sach` của tập. Nếu > 100%, quay lại `sd-storyboard` hạ model hoặc gộp đoạn.
2. Nhắc Linh kiểm bảng giá trong Settings của Flow nếu đã lâu chưa kiểm; sửa `src/tools/credit.json` khi Google đổi giá.
3. Trình bảng chi phí cho Linh duyệt. **Không** coi pack là đã duyệt khi Linh chưa trả lời.

## Thứ tự Linh làm trong Flow
- **Bước A:** tạo ảnh neo, bối cảnh, keyframe; lưu đúng tên vào `data/<tap>/anh/`.
- **Bước B0 (Ultra):** chạy nháp mỗi phiếu bằng Lite Lower Priority (0 credit), lưu `<đoạn>-n1.mp4`. Claude xem nháp, sửa prompt nếu Veo bỏ shot hoặc sai hướng.
- **Bước B:** render theo phiếu, số output = 1, lưu `<đoạn>-t<số>.mp4` vào `data/<tap>/takes/`.

Không tự động hoá Flow qua API ẩn hay extension lách kiểm tra (xem `01-NGHIEN-CUU-NEN.md` mục 5).
