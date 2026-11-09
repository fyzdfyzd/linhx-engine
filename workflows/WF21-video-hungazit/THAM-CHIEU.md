# Tham chiếu WF21 (agy, ngày 09/11/2026)

## 5 điều đáng học nhất
1. Kết hợp biểu thức tín hiệu đa phương thức (`audio:threshold`, `motion`, `subtitle`) để cắt nháp (rough cut) tự động từ file raw và xuất timeline XML không phá hủy sang Premiere/DaVinci Resolve (học từ `WyattBlue/auto-editor`).
2. Kiến trúc Local-First ghép `whisper.cpp` (word-level timestamp) + LLM cục bộ (nhận diện take hỏng, từ đệm "ậm ờ") và phơi bày mặt phẳng công cụ MCP để Claude Code điều khiển trực tiếp trình dựng (học từ `PaulBratslavsky/roughcut-ai-local-first-editor`).
3. Quy trình 2 pha của `appariciojunior/video-editor-skills`: tách riêng kỹ năng đánh giá nhịp độ vlog (pacing), cắt theo transcript, tự động chèn B-roll và xuất timeline trong DaVinci Resolve bằng bộ rule `SKILL.md` cho Claude Code.
4. Luồng Trung Quốc `modelscope/FunClip` + `linyqh/NarratoAI`: dùng ASR nhận diện người nói (diarization) kết hợp LLM chọn đoạn highlight để cắt nhanh (fast cut) và khớp kịch bản phân cảnh (storyboard) với khung hình thực tế.
5. Thiết kế bài giảng e-learning và video lập trình hóa bằng Markdown/React thông qua `slidevjs/slidev` và bộ skill router `remotion-dev/skills` (`/remotion-best-practices`), cho phép khóa thời lượng từng phân cảnh với phụ đề và xuất PNG/MP4 tự động.

## Bảng nguồn

| Tên | Link | Loại (repo/skill/workflow/sản phẩm/bài) | Giấy phép | Sao hoặc độ tin | Cập nhật lần cuối | Lấy gì cho WF | Đã đọc code/README hay mới thấy |
|---|---|---|---|---|---|---|---|
| WyattBlue/auto-editor | https://github.com/WyattBlue/auto-editor | repo | Unlicense (mã lõi) | ~5.800 sao | 2026 | Nhánh (1) edit từ file raw & (4) edit nhanh: cú pháp lọc khoảng lặng kết hợp chuyển động (`--edit audio/motion`) và xuất XML timeline sang NLE | Đã đọc README |
| PaulBratslavsky/roughcut-ai-local-first-editor | https://github.com/PaulBratslavsky/roughcut-ai-local-first-editor | repo | GPL-3.0 | Đang lên (LobeHub MCP / GitHub) | 2026 | Nhánh (1) edit từ file raw: kiến trúc `whisper.cpp` + LLM lọc bỏ bad takes/từ đệm và giao diện MCP cho agent | Đã đọc README |
| appariciojunior/video-editor-skills | https://github.com/appariciojunior/video-editor-skills | skill | CC BY-NC 4.0 | ~429 sao | 10/2026 | Nhánh (1) & (4): cấu trúc `SKILL.md` dạy Claude Code làm first-pass editor (transcript cut, pacing, B-roll) trên DaVinci Resolve | Đã đọc README |
| remotion-dev/skills (`remotion-best-practices`) | https://github.com/remotion-dev/skills | skill | Remotion License / MIT | ~4.500+ sao | 2026 | Nhánh (2) storyboard & (3) e-learning: bộ skill chuẩn trên skills.sh/tessl.io điều phối dựng scene, caption, timeline bằng code React | Đã đọc README |
| modelscope/FunClip | https://github.com/modelscope/FunClip | repo | MIT | ~6.400 sao | 2026 | Nhánh (4) edit nhanh (nguồn tiếng Trung): dùng FunASR/Paraformer trích xuất timestamp chính xác và gọi LLM chọn clip highlight tự động | Đã đọc README |
| linyqh/NarratoAI | https://github.com/linyqh/NarratoAI | workflow | MIT | ~11.000+ sao | 2026 | Nhánh (2) storyboard & (4) edit nhanh (nguồn tiếng Trung): pipeline tự động hóa viết kịch bản phân cảnh, khớp footage, lồng tiếng và phụ đề | Đã đọc README |
| chatfire-AI/huobao-drama | https://github.com/chatfire-AI/huobao-drama | workflow | Tuỳ chỉnh / Phi thương mại | ~17.000+ sao | 2026 | Nhánh (2) storyboard (nguồn tiếng Trung): luồng bóc tách kịch bản thành bảng phân cảnh (shot list), quản lý nhân vật đồng nhất và ghép video | Đã đọc README |
| slidevjs/slidev | https://github.com/slidevjs/slidev | repo | MIT | ~49.000+ sao | 2026 | Nhánh (3) video e-learning: biên tập slide từ Markdown, điều khiển bước click, ghi hình presenter và xuất PNG/PDF bằng Playwright | Đã đọc README |
| TimeBolt (Umcheck & FastForward) | https://www.timebolt.io | sản phẩm | Thương mại | Độ tin cậy cao (chuẩn ngành) | 2026 | Nhánh (1) & (4): cơ chế kết hợp cắt theo biên độ sóng âm (waveform) trước khi dùng transcript để bắt từ thừa ("ậm ờ") chính xác tới từng frame | Mới thấy (đọc tài liệu sản phẩm) |
| Chân dung & kênh nội dung Hungazit (Nguyễn Mạnh Hùng) | https://vietcetera.com/vn/podcast/have-a-sip/ep-147-hungazit-dau-bep-tu-do-trong-can-bep-cua-minh | bài | Bản quyền báo chí | Vietcetera / YouTube | Chưa rõ | Bước 0 xác định "Hungazit": trên internet công khai, Hungazit là đầu bếp/tác giả Nguyễn Mạnh Hùng (chuyên vlog nấu ăn, kỹ năng bếp); chưa có repo AI công khai mang tên này nên cần đối chiếu lại với nguồn nội bộ của anh Linh | Đã đọc bài tóm tắt |
