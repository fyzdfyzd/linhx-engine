---
name: hoi-ai
description: Hỏi nhiều mô hình AI bộ câu hỏi ABC như khách thật và lưu nguyên văn câu trả lời (claude -p, agy -p, codex, Gemini API, OpenRouter, hoặc dán tay từ ChatGPT/Gemini/Cốc Cốc/AI Hay). Dùng ở bước 3 của brand-check.
---

# Hỏi AI

`brandcheck.py hoi -w <ws> --mo-hinh <danh sách> --luot <n>`

| Mô hình | Ý nghĩa | Chi phí |
|---|---|---|
| `claude-tim` / `claude-nho` | Claude Code CLI, có / không tra web | gói Claude của người dùng |
| `agy` | Antigravity CLI (Gemini) | gói của người dùng |
| `codex` | Codex CLI | gói của người dùng |
| `gemini-tim` / `gemini-nho` | Gemini API, có Google Search / trí nhớ | cần GEMINI_API_KEY, tốn tiền |
| `openrouter:<model>[:online]` | mọi mô hình qua OpenRouter (GPT, Perplexity, DeepSeek) | cần OPENROUTER_API_KEY, tốn tiền |
| `dan-tay:<ten>` | tạo file trống để người dán câu trả lời thật | không tốn, đáng tin nhất |

Quy tắc:
- Số lượt: Nhanh 1 (ghi rõ "ảnh chụp một lần"), Chuẩn 3, Sâu 10. Ít hơn 3 lượt thì không nói về độ ổn định.
- Báo số lần gọi trước khi chạy đường tốn tiền.
- Ít nhất 3 họ mô hình khác nhau; có cả Tìm và Nhớ.
- Đường dán tay: hướng dẫn người dùng mở đúng ứng dụng khách dùng (ChatGPT, Gemini, Cốc Cốc AI, AI Hay, Zalo AI), cửa sổ mới, đăng xuất hoặc chế độ ẩn danh nếu được, dán cả link nguồn. File chưa dán bị bỏ qua, không tính là không nhắc.
- Không tự trả lời thay mô hình khác. Nếu chính Claude trong phiên phải trả lời (không có CLI), làm trước khi đọc brand-facts.json và đặt tên mô hình `claude-phien`.
- Chạy lại chỉ lấp file thiếu; muốn hỏi lại từ đầu thì dùng `--lan` mới.
