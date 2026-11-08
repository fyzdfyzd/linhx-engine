---
name: loi-the-offer
description: Bước 5, 6, 7, 9 của quy trình deck proposal - lợi thế của Linh lấy từ hồ sơ năng lực LINHX, tìm khoảng trống và thiết kế offer giải nỗi đau khách có mapping năng lực, ba giải pháp, mô tả dịch vụ. Dùng trong deck-proposal hoặc khi Linh hỏi "mình có lợi thế gì", "offer nào cho khách này", "đưa 3 phương án".
---

# Lợi thế, offer, ba giải pháp, mô tả dịch vụ

Script: `python "${CLAUDE_PLUGIN_ROOT}/scripts/deck.py"`. Hồ sơ năng lực: `${CLAUDE_PLUGIN_ROOT}/du-lieu/nang-luc.json` (33 năng lực, mỗi năng lực có `muc_do`: `da-chung-minh` | `dang-thu` | `y-tuong`). Bản đọc cho người: `LAB027-DECK-PROPOSAL/data/NANG-LUC-LINHX.md`.

## Bước 5. Lợi thế → `05-loi-the.md`

- Lọc năng lực theo BU trình bày và theo pain ở bước 4. Mỗi lợi thế một dòng bảng: lợi thế, mã NL-xx, bằng chứng nói được với khách, mức.
- Năng lực `dang-thu` / `y-tuong`: ghi rõ "đang thử" hoặc "thí điểm". Không biến dự án thử thành case thành công.
- Bằng chứng có tên khách khác: chỉ dùng khi đã công khai hoặc Linh cho phép; không chắc thì ghi "một ngân hàng TMCP" và đánh dấu `[CẦN LINH: được nêu tên?]`.
- Viết điểm yếu thật với đề bài này và cách bù (đối tác, thí điểm nhỏ, cam kết đo).

## Bước 6. Khoảng trống và offer → `06-offer.json`

1. **Khoảng trống**: điều khách cần mà đối thủ/phương án hiện tại làm chưa tốt (K1…), mỗi cái có BCxx.
2. **Offer**: giao điểm của pain điểm cao × khoảng trống × năng lực đã chứng minh. Mỗi offer có `loi_hua` một câu đo được ("giảm thời gian lập báo cáo tuần từ 2 ngày xuống nửa ngày"), `giai_pain`, `tao_gain`, `lap_khoang_trong`, `nang_luc`, `gia` (`[Linh chốt]` nếu chưa có), `nhan` (`chinh` | `thi-diem`).
3. Chạy `deck.py doi-chieu <dir>`: bảng offer ↔ pain ↔ năng lực, và danh sách pain ≥7 chưa offer nào giải. Script chặn offer không giải pain ≥7 và offer không có năng lực đã chứng minh mà không gắn `thi-diem`.
4. Giá tham chiếu chỉ lấy từ `NANG-LUC-LINHX.md` mục 6 hoặc lời Linh. Không tự đặt giá.
5. Xin Linh duyệt offer (cổng 6).

## Bước 7. Ba giải pháp → `07-ba-giai-phap.md`

- Đúng 3, khác nhau thật: thường là **gọn** (thí điểm nhỏ, rủi ro thấp), **khuyến nghị**, **mở rộng**. Không được là ba mức giá của cùng một gói.
- Mỗi giải pháp trỏ pain (P1…) và offer (O1…). Bảng so sánh GP1/GP2/GP3. Dòng `Khuyến nghị: Giải pháp n, vì …`.
- Xin Linh duyệt (cổng 7).

## Bước 9. Mô tả dịch vụ → `09-mo-ta-dich-vu.md`

Mỗi gói trong giải pháp khuyến nghị (và gói của 2 giải pháp kia nếu deck cần): Làm gì · Đầu ra · Mốc · Điều kiện (khách phải chuẩn bị gì) · Giá · Bằng chứng (NL-xx, BCxx). Viết để khách đọc một mình vẫn hiểu.
