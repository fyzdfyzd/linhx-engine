---
name: BM1_05_cham_chon_huong
description: "Bước 5 của Big Module 1 (LÀM MỚI HOÀN TOÀN): Tự chấm 3 phương án Outline A/B/C theo phản ứng của 3 Persona Neo + tiêu chí 'đạt khi' + độ dày bằng chứng + chống AI slop. Có cờ duyet_outline: nguoi/may; dừng chờ khi là người, tự chốt kèm ràng buộc khi là máy."
metadata:
  version: "0.1.0"
---

# Module 5: Tự chấm & Chốt hướng Outline (`BM1_05_cham_chon_huong`)

> **Trạng thái trong Đề 01**: Chưa có ở bất kỳ LAB nào — **làm mới hoàn toàn** (`cham_chon_huong.py`).

## 1. Công thức chấm điểm 4 trụ cột (Thang 100)
Mỗi phương án Outline `A`, `B`, `C` từ Bước 4 được chấm tự động và minh bạch trên 4 trụ cột:
1. **Phản ứng của 3 Persona Neo (40 điểm)**: Quy đổi từ `diem_persona_tong_hop` ở Bước 4 (khớp nỗi đau trừ đi nguy cơ bỏ đọc).
2. **Độ khớp tiêu chí `dat_khi.md` của loại nội dung (30 điểm)**: Kiểm tra cấu trúc dàn ý có giải quyết trực diện đầu ra cam kết trong `loai/<loai>/dat_khi.md` không.
3. **Độ dày bằng chứng & chất liệu thật (20 điểm)**: Số lượng insights loại `fact`/`paradox` gắn mã nguồn `[Nxx]`/`[BCxx]` và tỷ lệ chuyện thật so với `[GIẢ LẬP]`.
4. **Độ sắc góc nhìn & Chống lối mòn AI Slop (10 điểm)**: Trừ điểm nặng nếu dàn ý đi theo khuôn giáo điều ("Khái niệm -> Thực trạng -> Giải pháp") hoặc sáo ngữ liệt kê trong `loai/<loai>/loi_slop.md`.

## 2. Cơ chế Cờ duyệt (`duyet_outline: "nguoi" | "may"`)
- **`duyet_outline: "nguoi"`**:
  - Ghi trạng thái `CHO_NGUOI_DUYET` vào `05_cham_chon_huong.json`.
  - Xuất bảng đối chiếu 1 trang kèm phương án khuyến nghị ★ và 3 câu hỏi phản biện của Persona để người duyệt chỉ mất 2 phút bấm chọn (`A` / `B` / `C`).
- **`duyet_outline: "may"`** (chế độ chạy tự động Mức 1 hôm nay):
  - Tự động chốt phương án có tổng điểm cao nhất (yêu cầu ≥ 80/100).
  - **Không vứt bỏ hoàn toàn 2 phương án còn lại**: Tự động rút các *câu phản biện đắt nhất của Persona* từ cả 3 phương án để lập thành **"Bản Giao Kèo Ràng Buộc cho Bước 6 (Draft 1)"** (`rang_buoc_trien_khai_buoc_6`).

## 3. Lệnh chạy
```bash
python skills/BM1_05_cham_chon_huong/cham_chon_huong.py --b4-json runs/<run_id>/04_outline_thu_persona.json --duyet-outline <may|nguoi> --out-json runs/<run_id>/05_cham_chon_huong.json --out-md runs/<run_id>/05_cham_chon_huong.md
```
