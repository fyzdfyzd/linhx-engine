---
name: BM1_09_bien_tap_3_vong
description: "Bước 9 của Big Module 1: Duyệt, biên tập qua 6 lượt tách ngữ cảnh (máy, sự thật, cấu trúc, ngôn ngữ, chấm từng câu, độc giả ảo), sửa tối đa 3 vòng và lưu kinh nghiệm. Gắn từ LAB049 bien-tap-bai, hoc-tu-ban-sua và LAB025 bước 9."
---

# Module 9: Duyệt, biên tập 6 lượt (tối đa 3 vòng) & Lưu kinh nghiệm (`BM1_09_bien_tap_3_vong`)

## 1. Nguồn kế thừa (Vendor)
- **LAB049 (`vendor/LAB049/linhx-bien-tap/skills/bien-tap-bai/SKILL.md`)**:
  - **Lượt 0 (Máy)**: Chạy lại `cham_cau.py`, `kiem_van_dich.py`, `kiem_van.py` để đối chiếu cải thiện số đo từ Bước 7 → Bước 8 → Bước 9.
  - **Lượt 1 (Sự thật - `soat-su-that`)**: Đối chiếu mọi con số/trích dẫn với sổ nguồn Bước 3, liệt kê mọi nhãn `[GIẢ LẬP]` / `[CẦN LINH]`.
  - **Lượt 2 (Cấu trúc - `soat-cau-truc`)**: Kiểm tra độ chặt chẽ của các đoạn và tỷ lệ độ dài.
  - **Lượt 3 (Ngôn ngữ - `soat-ngon-ngu`)**: Chấm lại CQS (≥ 85) và APS (≤ 25).
  - **Lượt 4 (Chấm từng câu - `cham-tung-cau`)**: Rà từng câu theo quy tắc GIỮ / SỬA / CẮT.
  - **Lượt 5 (Độc giả ảo - `doc-gia-ao`)**: Cho 3 Persona Neo (từ Bước 2) đọc lại bản hoàn chỉnh và xác nhận đã trả lời được câu cãi của họ.
- **LAB049 (`hoc-tu-ban-sua`) & LAB025 (Bước 9)**: Sửa tối đa 3 vòng, trích xuất quy tắc mới vào `loai/<loai>/kinh_nghiem.md` và sổ lỗi hồi quy.

## 2. Luật sắt số 3 của Đề 01
- **Không tự tuyên bố "đạt" thay người duyệt cuối**: Cuối file `09_bien_tap_va_kinh_nghiem.md` ghi rõ bảng số đo kỹ thuật qua các vòng, danh sách nhãn `[GIẢ LẬP]` (nếu có), và đặt trạng thái `CHO_NGUOI_HOAC_GIAM_KHAO_DOC_LAP_NGHIEM_THU`.
