---
name: phan-bien
description: Hội đồng phản biện cho deck proposal - hai agent đọc ghost deck và deck như khách hàng khó tính và như partner tư vấn chiến lược, chấm theo rubric Nội dung, Mạch, Phong cách, Đúng pain, Khả thi, trả danh sách lỗi có mức độ. Dùng khi Linh nói "phản biện deck", "soi deck", hoặc deck giá trị lớn trước khi gửi.
---

# Phản biện deck

1. Chuẩn bị gói đọc: `03-nguoi-nghe.md`, `04-pain-gain.json`, `07-ba-giai-phap.md`, `10-ghost-deck.md`, `10-deck.json`, `02-bang-chung.csv`, tờ ghép `13-claude-deck/xem/to-slide.png` (chạy `deck.py xem` trước) và chuẩn `${CLAUDE_PLUGIN_ROOT}/skills/dung-deck/references/chuan-slide.md`.
2. Chạy **song song** hai agent của plugin: `khach-kho-tinh` và `partner-tu-van`. Đưa cho mỗi agent đường dẫn gói đọc, không đưa cách Claude đã làm (để đọc bằng mắt mới).
3. Mỗi agent ghi `phan-bien/<ten-agent>.json`:
```json
{"diem": {"noi_dung": 1-5, "mach": 1-5, "phong_cach": 1-5, "dung_pain": 1-5, "kha_thi": 1-5, "chuan_slide": 1-5},
 "ket_luan": "dat|sua",
 "loi": [{"slide": "id", "muc_do": "nang|nhe", "mo_ta": "...", "sua": "..."}],
 "cau_hoi_kho": ["..."]}
```
   Mỗi mức điểm phải thoả đủ tiêu chí của mức đó; còn lỗi nặng thì không được `dat`. `chuan_slide` chấm theo thang trong `chuan-slide.md`, lỗi ghi mã chuẩn (C1–C12) ở `mo_ta`. Điểm `chuan_slide` ≤ 2 nghĩa là cổng máy đã để lọt: ghi thành việc sửa plugin.
4. Claude gộp: sửa lỗi nặng, liệt kê lỗi nhẹ cho Linh chọn, đưa `cau_hoi_kho` vào bàn giao bước 15.
5. Phản biện chạy lại tối đa 2 vòng. Lỗi lặp ở nhiều deck thì ghi vào `du-lieu/local/<brand>.md` dạng `- cấm: …` hoặc thành luật mới.
