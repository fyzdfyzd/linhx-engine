---
name: BM1_07_danh_gia_draft1
description: "Bước 7 của Big Module 1: Đánh giá Draft 1 bằng bộ công cụ định lượng và phản biện tách ngữ cảnh. Gắn từ LAB049 lượt 0 (cham_cau.py, kiem_van_dich.py, kiem_van.py) + soat-cau-truc, LAB025 bước 8 (APS/CQS), và LAB046 (cổng 17 luật quality.py cho report)."
metadata:
  version: "0.1.0"
---

# Module 7: Đánh giá Draft 1 (`BM1_07_danh_gia_draft1`)

## 1. Nguồn kế thừa (Vendor)
- **LAB049 Lượt 0 (Máy)**:
  - `vendor/LAB049/linhx-bien-tap/scripts/cham_cau.py`: Đo độ dài câu trung bình, tỷ lệ câu dài >35 chữ, tỷ lệ câu ngắn ≤10 chữ, phát hiện cấu trúc so sánh 2 vế và từ máy.
  - `vendor/LAB049/linhx-bien-tap/scripts/kiem_van_dich.py`: Bắt các cụm văn dịch Tây, danh từ hoá, bị động giả.
  - `vendor/LAB049/linhx-bien-tap/scripts/kiem_van.py`: Đối chiếu số đo nhịp văn với mốc 7 bài đã đăng của anh Linh (`moc-giong.json`).
- **LAB049 `soat-cau-truc`**: Kiểm tra mạch lập luận, phát hiện đoạn sáo hoặc lệch trọng tâm.
- **LAB025 Bước 8 (`gemini-reviewer` / `ai_detector_system.md` & `critic_system.md`)**: Chấm điểm **APS** (AI Pattern Score — càng thấp càng tốt, ngưỡng ≤ 25) và **CQS** (Content Quality Score — thang 100, ngưỡng ≥ 85).
- **LAB046 (`report-core/quality.py`)**: Chạy thêm cổng kiểm 17 luật chất lượng báo cáo đối với loại `report_mau`.

## 2. Nguyên tắc bắt buộc
- Chạy thật các script Python trên file `06_trien_khai_draft_1.md` và ghi nguyên văn bảng số đo + danh sách câu bị bắt lỗi vào `07_danh_gia_draft_1.md` để Bước 8 sửa trúng đích.
