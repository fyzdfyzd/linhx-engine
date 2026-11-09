---
name: BM1_02_persona_neo
description: "Bước 2 của Big Module 1 (GỘP MỚI): Nghiên cứu người nhận, xác định khoảng trống độc giả (LAB029), lọc nhân khẩu học phân tầng Việt Nam (LAB048) và đắp khung tâm lý/nỗi sợ ẩn/câu hay cãi (LAB049 doc-gia-ao) để dựng 3 Persona Neo."
metadata:
  version: "0.1.0"
---

# Module 2: Nghiên cứu người nhận, dựng Persona làm neo (`BM1_02_persona_neo`)

> **Trạng thái trong Đề 01**: Có rời rạc ở 3 LAB (`LAB029`, `LAB048`, `LAB049`), **gộp thành 1 skill thống nhất** kèm script thực thi `persona_neo.py`.

## 1. Nguồn gộp từ 3 LAB
1. **LAB029 (`vendor/LAB029/linhx-khoang-trong/skills/nhu-cau-doc-gia/SKILL.md` & `cham-khoang-trong`)**: Tìm khoảng trống thông tin — điều người nhận đang bức xúc hoặc hiểu lầm mà các bài/báo cáo hiện có trên thị trường chưa giải đáp thỏa đáng.
2. **LAB048 (`vendor/LAB048/src/lay_mau_1000.py` & `data/persona-sample-60.json`)**: Nguồn hồ sơ nhân khẩu học Việt Nam (Nemotron-Personas-Vietnam: tuổi, giới tính, vùng miền, nghề nghiệp, trình độ học vấn, bối cảnh sống). **Quy tắc lọc**: Không bốc ngẫu nhiên dân số chung; lọc đúng tầng nghề nghiệp/độ tuổi khớp với kênh.
3. **LAB049 (`vendor/LAB049/linhx-bien-tap/skills/doc-gia-ao/SKILL.md`)**: Bổ sung chiều sâu tâm lý thực chiến cho từng Persona:
   - Đọc/xem vào lúc nào, trên thiết bị gì?
   - **Nỗi sợ ẩn** (điều không nói ra trong cuộc họp nhưng đêm về lo).
   - **Câu cửa miệng hay cãi** (phản xạ phòng vệ khi đọc thấy lý thuyết suông).
   - **Điểm kích hoạt bỏ đọc (`trigger_bo_doc`)**.

## 2. Lệnh chạy
```bash
python skills/BM1_02_persona_neo/persona_neo.py --loai <bai_viet|report_mau|noi_dung_khoa_hoc> --de-bai "<chuỗi đề bài>" --out runs/<run_id>/02_persona_neo.json --md runs/<run_id>/02_persona_neo.md
```

## 3. Đầu ra
- `runs/<run_id>/02_persona_neo.json`: Dữ liệu cấu trúc của Khoảng trống độc giả + 3 Persona Neo (`P1`, `P2`, `P3`) để Module 4 (`thu_outline_persona.py`) và Module 9 (`doc-gia-ao`) đọc trực tiếp.
- `runs/<run_id>/02_persona_neo.md`: Báo cáo phân tích người nhận & bảng hồ sơ 3 Persona Neo.
