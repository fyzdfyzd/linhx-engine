---
name: BM1_01_phan_tich_de_bai
description: "Bước 1 của Big Module 1: Đọc kỹ, phân tích đề bài, xác định hạt giống ý tưởng (Seed Input) và mở rộng bối cảnh bằng 11 câu hỏi sâu (3 câu ưu tiên). Gắn từ LAB025 idea-seeder, LAB028 bước 1 (report) và LAB017 course-architect (khoá học)."
metadata:
  version: "0.1.0"
---

# Module 1: Đọc kỹ, phân tích đề bài (`BM1_01_phan_tich_de_bai`)

## 1. Nguồn kế thừa (Vendor)
- **LAB025 (`vendor/LAB025/linhx-viet-bai/skills/idea-seeder/SKILL.md`)**: Hạt giống (`01_Seed_Input`) + Mở rộng bối cảnh bằng 11 câu hỏi sâu (`02_Context_Expansion`).
- **LAB028 (`vendor/LAB028/linhx-report/skills/khung-nghien-cuu/SKILL.md`)**: Bước 1 làm rõ đề bài báo cáo (`01-de-bai.md`) + Cây vấn đề MECE.
- **LAB017 (`vendor/LAB017/linhx-course/skills/course-architect/SKILL.md`)**: `00-brief.yaml` + Mục tiêu học tập theo thang Bloom (`01-objectives`).

## 2. Đầu vào
- `de_bai`: Chủ đề, yêu cầu cốt lõi, bối cảnh sử dụng.
- `loai`: `bai_viet` | `report_mau` | `noi_dung_khoa_hoc`.
- Cấu hình loại nội dung tại `loai/<loai>/cau_hinh.json`, `dau_ra.md`, `dat_khi.md`, `loi_slop.md`.

## 3. Xử lý bắt buộc
1. **Phân rã hạt giống (Seed Input)**:
   - Luận điểm hạt nhân (Core Thesis / Câu hỏi trung tâm).
   - Nghịch lý hoặc mâu thuẫn thực tế cần giải quyết (tránh viết xuôi chiều kiểu AI).
   - Ràng buộc cứng: Độ dài, kênh xuất bản, giọng tác giả, nhận diện thương hiệu (`Nhận diện tạm: Sakedemy (LAB043)`).
2. **Trả lời 11 câu hỏi mở rộng bối cảnh (chọn 3 câu mũi nhọn)**:
   - Câu hỏi về *Ai thực sự trả giá nếu vấn đề này không giải quyết?*
   - Câu hỏi về *Ngộ nhận phổ biến nhất trên thị trường Việt Nam hiện nay là gì?*
   - Câu hỏi về *Bằng chứng thực địa / hệ thống nào phản bác cách làm phong trào?*
3. **Đặc thù theo loại**:
   - Nếu `report_mau`: Lập thêm Cây vấn đề MECE 3 nhánh (theo `LAB028`).
   - Nếu `noi_dung_khoa_hoc`: Xác định thêm 3 Mục tiêu học tập đo lường được theo động từ Bloom (theo `LAB017`).

## 4. Đầu ra
- Ghi file riêng: `runs/<run_id>/01_phan_tich_de_bai.md` (kèm header truy vết Skill, LAB nguồn, Nhận diện tạm Sakedemy, Trạng thái mẫu).
