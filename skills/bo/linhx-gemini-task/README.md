# linhx-gemini-task v0.1 (LAB047)

Giao việc cho **Gemini Task** (gói Ultra, tài khoản Art Urah ở `gemini.google.com/u/1`, chế độ Nhiệm vụ, model Argon) mỗi khi có thể, để việc nặng chạy bằng hạn mức Gemini thay vì token Claude.

## Cài
```
/plugin marketplace add D:/LINHX/LAB/LAB047-GEMINI-TASK/src
/plugin install linhx-gemini-task@linhx-lab-047
```
Một lần trong Gemini: mở `gemini.google.com/u/1/customize/skills` → Create → Upload → chọn **thư mục** `gemini-skills/linhx-nhiem-vu` (Gemini không nhận zip). Đề nào bắt đầu bằng `@linhx-nhiem-vu` thì Argon tự theo chuẩn LINHX.

## Skill
| Skill | Làm gì |
|---|---|
| `gemini-task` | Cổng chính: việc nào giao Gemini, tách song song, vòng 6 bước, luật viết đề |
| `gemini-gui` | Mở tab mới, kiểm đúng tài khoản Ultra, chọn Nhiệm vụ + Argon, dán đề qua clipboard, đối chiếu, gửi, ghi link |
| `gemini-lay-cham` | Tải kết quả, bỏ trùng hash, giải nén, chấm máy, chấm tay, điểm Argon 1–5 |
| `gemini-skill` | Đóng gói Skill cho Gemini (SKILL.md ở gốc, chỉ file chữ, ≤100 MB, không mạng) |

## Script `scripts/gt.py` (Python chuẩn, không cần cài gì)
`moi` tạo đề từ khuôn · `gui` ghi link · `trang-thai` · `so` xem sổ · `lay` gom kết quả · `kiem` chấm máy · `skill` đóng gói Skill Gemini · `chieu-dai` đối chiếu khi dán.
Sổ chung: `D:/LINHX/LAB/GEMINI-TASK/so-nhiem-vu.jsonl` (đổi bằng biến `GT_SO`). Sổ ghi cả các lần chạm giới hạn để biết hạn mức thật của gói.

## Thư mục mỗi nhiệm vụ
`<LAB>/argon/<MÃ>/`: `DE.txt`, `yeu-cau.json`, `CHAY.md`, `files/`, `TRA-LOI.md`, `giai-nen/`, `KIEM-MAY.md`, `CHAM.md`. Giống cách LAB046 đã chạy ngày 17/10.

Antigravity (agy) không dùng plugin: gọi thẳng `python scripts/gt.py <lệnh>` và đọc `skills/*/SKILL.md`.
