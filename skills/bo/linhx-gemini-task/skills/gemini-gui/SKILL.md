---
name: gemini-gui
description: Gửi một đề có sẵn vào Gemini Task trên tài khoản Ultra Art Urah (gemini.google.com/u/1, Nhiệm vụ, Argon) bằng Chrome của Linh, rồi ghi link vào sổ. Dùng khi Linh nói "thả đề vào Gemini", "gửi đề Argon", hoặc bước gửi của skill gemini-task.
---

# Gửi đề vào Gemini Task

## Chạy ở đâu
- **Claude Code trên máy Linh** (plugin cài ở đây) có công cụ Claude in Chrome (`mcp__claude-in-chrome__*`): làm thẳng các bước dưới.
- **Thread trên cloud** (LINHX LAB) không với tới Chrome của Linh: mở phiên Remote Control ở `D:\LINHX\LAB` (`start_rc_session`), giao các bước dưới trong `instructions`, kèm đường dẫn file đề trên máy. Cách này đã chạy ngày 17/10.
- Không có cả hai: đưa Linh đường dẫn file đề và ba bước "mở `/u/1`, chọn Nhiệm vụ + Argon, dán". Linh dán mất khoảng 1 phút.

## Các bước (Claude in Chrome)
1. Luôn mở **tab mới** trong Chrome chính của Linh, không đụng tab đang dùng. Vào `https://gemini.google.com/u/1/app`.
2. Kiểm tài khoản ở góc phải là **Art Urah** (art.urah.vn@gmail.com). Sai tài khoản hoặc chưa đăng nhập thì dừng và báo Linh. Không nhập mật khẩu, không đổi cài đặt.
3. Chọn chế độ **Nhiệm vụ** (Task) và model **Argon** trong ô chọn công cụ/model. Không thấy thì chụp màn hình, báo Linh: giao diện đã đổi.
4. Dán đề. Đề dài nên dán qua clipboard thay vì gõ:
   `powershell -NoProfile -Command "Get-Content -Raw -Encoding UTF8 '<đường dẫn DE.txt>' | Set-Clipboard"`
   rồi bấm vào ô nhập, nhấn Ctrl+V.
5. Đối chiếu: `python "${CLAUDE_PLUGIN_ROOT}/scripts/gt.py" chieu-dai <DE.txt>` in 120 ký tự đầu và cuối; so với đầu và cuối ô nhập. Lệch thì xoá ô, dán lại.
6. Đề cần file đính kèm (zip lượt trước, ảnh): dùng nút "+" → tải tệp lên nếu công cụ làm được; không thì để tab mở và nhờ Linh kéo file vào, nêu rõ đường dẫn file.
7. Gửi. Chờ tới khi thấy kế hoạch hoặc trạng thái "đang làm", rồi lấy URL của cuộc trò chuyện (`https://gemini.google.com/u/1/app/<id>`).
8. Ghi: `python "${CLAUDE_PLUGIN_ROOT}/scripts/gt.py" gui <thư mục nhiệm vụ> --link <URL>`. Để tab mở.

Nhiều đề: mỗi đề một tab mới, lặp bước 1–8. Đã chạy 8 nhiệm vụ song song không vướng giới hạn.

## Khi bị chặn
- Bộ lọc quyền trên máy chặn một bước: không tìm cách vượt. Dừng, báo bước nào bị chặn và lý do; Linh xác nhận trên thẻ hoặc tự dán.
- Gemini báo hết hạn mức hoặc giới hạn: `gt.py trang-thai <thư mục> gioi-han --ghi-chu "<nguyên văn thông báo>"`, báo Linh giờ có thể gửi lại. Sổ giữ các lần chạm giới hạn để biết hạn mức thật của gói.
- CAPTCHA hay xác minh: dừng, để Linh làm.
