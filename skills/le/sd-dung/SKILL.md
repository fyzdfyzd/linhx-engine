---
name: sd-dung
description: Bước 7 Flow Pack. Ghép các bản giữ của một tập thành bản dựng nháp, chuẩn bị phụ đề và ghi chú hậu kỳ; tính credit trên mỗi giây và tỉ lệ giữ. Dùng khi mọi đoạn đã có bản giữ.
---

# sd-dung: bản dựng nháp

Chạy: `python LAB016-PHIM-NGAN-AI/src/tools/nhan_take.py LAB016-PHIM-NGAN-AI/data/<tap> --dung` (cần ffmpeg). Ra `output/<tap>-nhap.mp4`.

## Sau khi ghép
1. Viết `output/<tap>.srt` từ thoại trong JSON (mốc = tổng thời lượng các đoạn trước + mốc shot).
2. Ghi chú hậu kỳ cho CapCut: chỗ cần nhạc (Veo đã được dặn "No music"), chỗ cần lồng tiếng lại nếu Veo đọc tiếng Việt sai, chỗ cần cắt bớt đầu/cuối clip.
3. Tính và ghi vào `OVERVIEW.md` mục 4: tổng credit, credit/giây phim, tỉ lệ giữ, so với dự kiến trong pack.
4. Upscale 1080p trong Flow (0 credit) chỉ cho bản giữ, làm sau khi dựng xong.
