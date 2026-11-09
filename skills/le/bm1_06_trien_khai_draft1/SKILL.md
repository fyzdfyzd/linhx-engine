---
name: BM1_06_trien_khai_draft1
description: "Bước 6 của Big Module 1: Triển khai từng phần theo Outline đã chốt ở Bước 5, thiếu thì nghiên cứu thêm, lưu Draft 1. Tự động điều phối theo loại nội dung: Bài viết (LAB049 + LAB025), Report mẫu (LAB028 + LAB046), Nội dung khoá học (LAB017 linhx-course)."
metadata:
  version: "0.1.0"
---

# Module 6: Triển khai từng phần & Lưu Draft 1 (`BM1_06_trien_khai_draft1`)

## 1. Điều phối theo cấu hình 3 loại nội dung
| Loại nội dung | Skill / Engine gọi từ `vendor/` | Quy tắc thực thi ở Bước 6 |
|---|---|---|
| **Bài viết** (`bai_viet`) | `vendor/LAB049/linhx-viet-giong-viet/skills/viet-bai-giong-viet` + `vendor/LAB025/linhx-viet-bai/skills/critic-loop-writer` | - Nếu có nháp gạch đầu dòng của tác giả (`che_do: co_nhap_tac_gia`): chạy `kiem_nhap.py` → kiểm ý `03b` → làm mượt.<br>- Khi chạy thử tự động Mức 1 (`che_do: chay_thu_khong_mau`): dựng khung gạch đầu dòng từ Outline Bước 5 + `KHO-CHUYEN-THAT.md` (`LAB025`), kiểm ý `03b`, triển khai thành `06_draft_1.md`. Giai thoại giả định bắt buộc gắn `[GIẢ LẬP]`. |
| **Report mẫu** (`report_mau`) | `vendor/LAB028/linhx-report/skills/viet-bao-cao` + `vendor/LAB046/report-core/src/report_core/compose.py` | - Lập Ghost Report (`05-ghost` mỗi trang 1 thông điệp kết luận Action Title) + triển khai từng chương có trỏ mã bằng chứng `[BC01]..[BC15]`. |
| **Nội dung khoá học (1 buổi)** (`noi_dung_khoa_hoc`) | `vendor/LAB017/linhx-course/skills/lesson-script` | - Triển khai kịch bản lời giảng chi tiết + bố cục slide theo 5 sự kiện Gagné rút gọn, đảm bảo độ dài mỗi phân đoạn 90–120 giây (khoảng 180–250 âm tiết tiếng Việt), kèm danh mục từ tiếng Anh trong `pronunciation.yaml`. |

## 2. Đầu ra
- Ghi file riêng: `runs/<run_id>/06_trien_khai_draft_1.md` (bản nháp toàn văn đầu tiên trước khi đưa vào vòng phản biện độc lập).
