---
name: BM2_M1_chu_trinh_template
description: "Big Module 2 - Chu trình Template dạng chung (LÀM MỚI theo mẫu LAB043 v2): Phân tích yêu cầu -> Tham chiếu & nạp luật Onbrand -> Dựng 2-3 phương án thiết kế -> Chấm độc lập theo rubric -> Biên tập tối đa 3 vòng và đánh phiên bản."
metadata:
  version: "0.1.0"
---

# Big Module 2 · Chu trình Template dạng chung (`BM2_M1_chu_trinh_template`)

> **Trạng thái trong Đề 01**: **Làm mới dạng chung** theo cách làm PDCA của `LAB043` v2 (chấm bằng người chấm tách ngữ cảnh, sửa ≤ 3 vòng, có quản lý phiên bản). Dùng tạm bộ nhận diện **Sakedemy (`vendor/LAB043/brands/sakedemy/`)**.

## 1. Năm bước chuẩn của Chu trình Template (`M1` → `M5`)
| Bước | Tên bước | Công việc cụ thể | File ghi ra trong `runs/<run_id>/` |
|---|---|---|---|
| **M1** | Phân tích yêu cầu ấn phẩm & Nạp nhận diện | Xác định khổ ấn phẩm, mục đích sử dụng theo từng loại (`bai_viet`: 2 ảnh minh hoạ + DOCX; `report_mau`: mẫu trang báo cáo A4 PDF + biểu đồ; `noi_dung_khoa_hoc`: bộ khung Slide 16:9). Nạp `brand.json` & `LUAT-ONBRAND.md` của **Sakedemy**. | `M1_phan_tich_yeu_cau_template.md` |
| **M2** | Nghiên cứu tham chiếu bố cục | Đối chiếu `KHUNG-GUIDELINE-CHUAN.md` (`LAB043`), thư viện bố cục slide (`LAB027`), mẫu tạp chí (`LAB028`) và kho minh hoạ (`LAB031`) để rút thông số lưới, tỷ lệ màu (60% trắng / 25% xanh lá `#6EB264` / 10% xanh rêu đậm `#02403B` / 5% nhấn), tỷ lệ chữ `Be Vietnam Pro` (3.2 : 1.6 : 1). | `M2_tham_chieu_va_luat_onbrand.md` |
| **M3** | Dựng 3 phương án Template (`T-A`, `T-B`, `T-C`) | Thiết kế 3 phương án bố cục khác nhau hẳn nhau (khác cấu trúc lưới, tỷ lệ mảng màu chủ đạo và cách đặt hình/biểu đồ), mỗi phương án có thông số kỹ thuật và bản dựng thật. | `M3_ba_phuong_an_template.md` |
| **M4** | Chấm độc lập theo Rubric Onbrand (`LAB043` + `LAB036`) | Chấm 3 phương án theo 5 trọng số của `brand.json` Sakedemy: **Màu (30đ) + Chữ (20đ) + Logo (25đ) + Hình & Bố cục (15đ) + Nội dung không từ cấm (10đ)**. Bắt lỗi tương phản (cấm chữ trắng trên nền `#6EB264` vì chỉ đạt 2,56:1). | `M4_cham_chon_template_onbrand.md` |
| **M5** | Biên tập tối đa 3 vòng (PDCA), Đóng gói phiên bản & Xuất Media thật | Sửa các lỗi bố cục/tương phản qua tối đa 3 vòng (`v1.0` → `v1.1` → `v1.2-chot`), đóng dấu `"Nhận diện tạm: Sakedemy (LAB043)"`, và xuất các file Media hoàn chỉnh của ấn phẩm. | `M5_bien_tap_template_va_xuat_media.md` + các file ảnh/PDF/Slide/DOCX thật |
