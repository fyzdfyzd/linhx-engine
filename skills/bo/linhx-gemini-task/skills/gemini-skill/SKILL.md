---
name: gemini-skill
description: Đóng gói một Skill cho Gemini (Gemini không có plugin; Skill là SKILL.md ở gốc + script, chỉ file chữ, ≤100 MB, script không gọi mạng, gọi bằng @tên) và cài Skill chuẩn linhx-nhiem-vu. Dùng khi cần cho Gemini Task dùng lại công cụ, dữ liệu, luật nhiều lần, hoặc khi Linh nói "làm skill cho Gemini".
---

# Skill cho Gemini

Đưa vào Skill những gì đề nào cũng lặp lại: luật, script tự kiểm, dữ liệu nền, font, thư viện JS. Đề khi đó ngắn lại, chỉ còn `@tên-skill` + việc riêng.

## Luật của Gemini (17/10/2026)
- `SKILL.md` ở **gốc** thư mục/zip, có frontmatter `name` (trùng tên thư mục) và `description`.
- **Chỉ các đuôi Gemini nhận**: .md .py .txt .csv .pdf (đo 17/10 trên hộp "Upload a skill"). Script .sh/.js/.json thì đổi đuôi thành .txt hoặc viết lại bằng Python. Ảnh, font, PSD thì đổi sang base64 trong `.b64.txt` và kèm hàm giải mã (xem LAB045 `le-bich-hoat-hinh`).
- Tổng ≤ 100 MB. Script **không gọi mạng** (máy Gemini chặn), chỉ dùng thư viện có sẵn: Python 3.11, pandas, Pillow, sqlite3, Jinja2, WeasyPrint, python-pptx; Node 18.
- Kèm `scripts/kiem-tra.sh` hoặc một lệnh thử nhanh để lượt đầu biết máy thiếu gì.

## Đóng gói
`python "${CLAUDE_PLUGIN_ROOT}/scripts/gt.py" skill <thư mục skill>`: kiểm các luật trên, cảnh báo script có dấu hiệu gọi mạng, rồi nén `<tên>.zip` cạnh thư mục (zip chỉ để lưu trữ hay gửi đi; Gemini cần thư mục).

## Cài vào Gemini
1. Mở `https://gemini.google.com/u/1/customize/skills` (Art Urah; hoặc bánh răng góc dưới trái → Skills) → **Create → Upload** (không phải "Create with Gemini") → chọn **folder** là thư mục skill. Gemini **không nhận zip**; chọn thư mục để giữ thư mục con `scripts/`.
   Bộ lọc quyền trên máy chặn Claude chọn file trong hộp thoại hệ thống (17/10), nên bước chọn thư mục do Linh bấm (khoảng 30 giây). Claude mở sẵn tab tới đúng hộp Upload và đưa đường dẫn thư mục.
2. Sửa skill: sửa thư mục, chạy lại `gt.py skill`, tải lên lại cả thư mục.
3. Gọi trong đề: dòng đầu `@tên-skill`.

## Skill chuẩn có sẵn: `linhx-nhiem-vu`
Ở `${CLAUDE_PLUGIN_ROOT}/gemini-skills/linhx-nhiem-vu/`: luật nguồn, máy, thư mục chuẩn, checkpoint, nối lượt, `tu_kiem.py` (đếm CSV/SQLite, đoạn cắt cứng, URL bọc google, file trùng tên thư viện) và `dong_goi.py`. Cài một lần; khuôn đề (`templates/khuon-de.txt`) đã gọi `@linhx-nhiem-vu` ở dòng đầu.
