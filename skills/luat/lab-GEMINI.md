@AGENTS.md

## Riêng cho Antigravity tại `D:\LINHX\LAB`
1. **Cổng bắt buộc đầu mỗi cuộc trò chuyện (Session Gate)**:
   - Trước khi thực hiện bất kỳ yêu cầu nào trong `D:\LINHX\LAB`, bắt buộc xác định đang làm trên `LABNNN-TEN-VIET-TAT` nào (dùng LAB hiện có) hoặc khởi tạo ngay một `LABNNN-TEN-VIET-TAT` mới từ `_template/` (theo `AGENTS.md` và `README.md`).
   - Mở đầu phản hồi bằng `[Đang dùng: LABNNN-TEN-VIET-TAT]` hoặc `[Đã tạo mới: LABNNN-TEN-VIET-TAT]`.
2. **Kỷ luật lưu vết `.handoff/` (`D:\LINHX\GEMINI.md` & `linhx-tracking`)**:
   - Khi làm việc trong một `LABNNN-TEN-VIET-TAT`, ghi vết vào `LABNNN-TEN-VIET-TAT/.handoff/` (`BANG.md`, `VAN-DE.md`, `logs/<MA>-YYYYMMDD-HHMM.md`, `BAO-CAO.md`), đồng thời cập nhật `LABNNN-TEN-VIET-TAT/LOG.md`.
   - Khi làm việc cấp toàn khu `D:\LINHX\LAB` (như rà soát kho, sửa quy ước chung), ghi vết vào `D:\LINHX\LAB\.handoff/`.
