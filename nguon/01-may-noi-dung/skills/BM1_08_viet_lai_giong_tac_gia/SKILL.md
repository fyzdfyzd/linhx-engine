---
name: BM1_08_viet_lai_giong_tac_gia
description: "Bước 8 của Big Module 1: Viết lại theo giọng tác giả, cân bằng giữa nhu cầu độc giả (Persona Neo) và hồ sơ giọng (Linh / Vân Anh / Giảng viên / Báo cáo). Gắn từ LAB049 linhx-viet-giong-viet, luong-hoa, và ho-so-bien-tap."
---

# Module 8: Viết lại theo giọng tác giả & Cân bằng với Độc giả (`BM1_08_viet_lai_giong_tac_gia`)

## 1. Nguồn kế thừa (Vendor)
- **LAB049 (`vendor/LAB049/linhx-viet-giong-viet/skills/viet-bai-giong-viet/SKILL.md`)**: Làm mượt theo nhịp câu chảy tự nhiên, khử 8 lỗi chị Vân Anh bắt (`ho-so-bien-tap/van-anh/LUAT.md`).
- **LAB049 (`vendor/LAB049/linhx-bien-tap/ho-so-bien-tap/linh/LUAT.md`)**: Hồ sơ giọng anh Linh (tỉnh táo, sắc lạnh, đi từ chi tiết đời thực sang nghịch lý hệ thống, không kết bài kiểu khuyên nhủ đạo lý).
- **LAB049 (`vendor/LAB049/linhx-bien-tap/skills/luong-hoa/SKILL.md` & `scripts/luong_hoa.py`)**: Đo kiểm lại phân bố độ dài câu và nhịp văn sau khi viết lại.

## 2. Xử lý theo từng loại nội dung
1. **Bài viết (`bai_viet`)**: Giọng tác giả **Linh**, kiểm soát theo hồ sơ biên tập **Vân Anh**.
2. **Report mẫu (`report_mau`)**: Giọng **báo cáo tư vấn chiến lược** (khách quan, câu mở đoạn là kết luận định lượng, dùng thuật ngữ nhất quán theo `LUAT-ONBRAND.md` của Sakedemy).
3. **Nội dung khoá học (`noi_dung_khoa_hoc`)**: Giọng **giảng viên Linh** (gần gũi, thực chiến, câu nói vừa hơi thở 15–22 chữ/câu, đan xen câu hỏi gợi mở học viên).

## 3. Đầu ra
- Ghi file riêng: `runs/<run_id>/08_viet_lai_giong_tac_gia.md` (bản viết lại đã khử sạch các lỗi phát hiện ở Bước 7).
