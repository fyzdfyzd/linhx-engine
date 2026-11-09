---
name: BM1_04_outline_thu_persona
description: "Bước 4 của Big Module 1 (LÀM MỚI PHẦN THỬ PERSONA): Rút 30 insights và dựng 3 phương án Outline A/B/C khác biệt (gắn LAB025 content-synthesizer), sau đó đưa cả 3 Outline cho 3 Persona Neo (từ Bước 2) đọc thử và chấm phản ứng theo 5 tiêu chí."
metadata:
  version: "0.1.0"
---

# Module 4: Dựng 2–3 hướng Outline & Thử trên Persona (`BM1_04_outline_thu_persona`)

> **Trạng thái trong Đề 01**: Có phần dựng outline từ `LAB025` bước 5–6 (30 insights → 3 phương án A/B/C). **Làm mới phần thử outline trên persona** (`thu_outline_persona.py`).

## 1. Quy trình 2 nửa trong Module 4
### Nửa A — Kế thừa `LAB025/content-synthesizer`
1. Nén tư liệu từ Bước 3 thành **30 Insights** (phân loại: `fact`, `paradox`, `metaphor`, `provocation`).
2. Tạo **3 phương án Outline (A, B, C)** khác nhau ở ít nhất 2/3 trục (*Góc nhìn*, *Tone giọng*, *Cấu trúc mạch bài*):
   - Mỗi phương án chọn 10–12 insights (độ trùng lặp giữa các phương án ≤ 3 insights).
   - Mỗi phương án đề xuất 2–3 giai thoại/tình huống minh hoạ (nếu là giai thoại giả định để thử mạch, bắt buộc gắn nhãn `[GIẢ LẬP]`).

### Nửa B — Làm mới: Thử từng Outline trên 3 Persona Neo (`P1`, `P2`, `P3` từ Bước 2)
Cho từng Persona đọc mù từng phương án Outline A, B, C và phản hồi độc lập theo **5 tiêu chí**:
1. `diem_khop_noi_dau` (Thang 10): Dàn ý này có chạm đúng nỗi sợ ẩn và bài toán thực tế của tôi không?
2. `diem_nguy_co_bo_doc` (Thang 10, càng thấp càng tốt): Nhìn dàn ý có chỗ nào chạm `trigger_bo_doc` không?
3. `muc_chan_nhat`: Chỉ đích danh mục nào trong Outline nhìn vào đã thấy sáo rỗng hoặc thừa.
4. `cau_phan_bien_ngay_tu_dan_y`: Câu cãi cụ thể của Persona đối với luận điểm trong Outline.
5. `gia_tri_ky_vong_mang_ve`: Đọc xong Outline này Persona kỳ vọng nhận được gì.

## 2. Lệnh chạy
```bash
python skills/BM1_04_outline_thu_persona/thu_outline_persona.py --loai <loai> --persona-json runs/<run_id>/02_persona_neo.json --out-json runs/<run_id>/04_outline_thu_persona.json --out-md runs/<run_id>/04_outline_thu_persona.md
```

## 3. Đầu ra
- `runs/<run_id>/04_outline_thu_persona.json`: Toàn bộ 30 insights, 3 phương án Outline A/B/C, và ma trận phản ứng của 3 Persona Neo (9 lượt đánh giá: 3 Persona × 3 Outline).
- `runs/<run_id>/04_outline_thu_persona.md`: File báo cáo chi tiết Bước 4.
