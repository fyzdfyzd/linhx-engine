# Phiếu hỏi API khối lớn (agy, máy công ty DESKTOP-PVHR2CD), ≤ 40 phút

Cần: `OPENROUTER_API_KEY` riêng (không gắn tài khoản chat của Linh). Không có khoá thì bỏ phiếu này, chỉ chạy dán tay.

```
cd linhx-engine/skills/bo/linhx-brand-check/scripts
set W=..\..\..\..\workflows\WF18-cham-thuong-hieu-ca-nhan\vong-1\ws
python brandcheck.py hoi -w %W% --lan 2026-11-09 --mo-hinh openrouter:openai/gpt-5:online,openrouter:google/gemini-2.5-pro:online,openrouter:anthropic/claude-sonnet-4.5:online,openrouter:openai/gpt-5,openrouter:google/gemini-2.5-pro --luot 5
```
28 câu × 5 lượt × 5 = 700 lần gọi. Không dùng `claude-tim`, `claude-nho`, `agy` (chạy dưới tài khoản Linh, nhiễm ngữ cảnh, BAI-HOC L8).
Chạy lại y hệt với `--lan 2026-11-10` để đo ổn định (ngưỡng lệch có mặt gộp ≤ 10).
Xong: commit `WF18 hỏi API <ngày>`, push nhánh `claude/project-thread-l78gyp`.
