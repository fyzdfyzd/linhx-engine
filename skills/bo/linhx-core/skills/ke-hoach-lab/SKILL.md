---
name: ke-hoach-lab
description: Lập và giữ kế hoạch bằng file cho một lab LINHX (PLAN.md, LOG.md, refs/) để không lạc mục tiêu qua nhiều phiên. Dùng khi mở lab mới, khi việc có từ 3 bước trở lên, khi quay lại lab cũ, hoặc khi Linh nói "lên kế hoạch", "làm tiếp lab".
---

# Kế hoạch lab bằng file

Ngữ cảnh là RAM: dễ mất, có hạn. File là ổ cứng: bền, không giới hạn. Cái gì quan trọng phải ghi ra file.

Mỗi lab có 3 chỗ ghi, không thêm file mới:

| File | Ghi gì | Khi nào |
|---|---|---|
| `PLAN.md` | Mục tiêu, tiêu chí "chạy được", các pha, **bước kế tiếp**, sổ quyết định, bảng lỗi | Tạo trước khi làm; sửa mỗi khi xong một pha hoặc có quyết định |
| `LOG.md` | Nhật ký theo ngày: đã làm gì, kết quả, lệnh đã chạy | Sau mỗi bước có kết quả |
| `refs/` hoặc `01-NGHIEN-CUU-NEN.md` | Phát hiện: repo đã đọc, nguồn, số liệu, trích dẫn | Ngay khi phát hiện (luật 2 thao tác) |

## Quy trình

1. **Đứng trong folder lab.** Nếu chưa có `PLAN.md`, chép `templates/PLAN.md` của skill này vào lab và điền. Mục tiêu và tiêu chí lấy từ `OVERVIEW.md` mục 1–2 nếu đã có.
2. **Đọc trước khi làm.** Mỗi lần quay lại lab, đọc `PLAN.md`, sau đó đọc khoảng 30 dòng cuối `LOG.md`. Hook `nhac-plan` sẽ nhắc phần đầu PLAN.md, nhưng nhắc không thay cho việc đọc.
3. **Làm theo pha.** Mỗi pha có trạng thái `[ ]`, `[~]` hoặc `[x]`. Chỉ một pha ở trạng thái `[~]` tại một thời điểm. Dòng `Bước kế tiếp` luôn là **một hành động cụ thể**.
4. **Xong pha:** đánh `[x]`, ghi một dòng vào `LOG.md`, sửa `Bước kế tiếp`.
5. **Đóng lab:** khi Linh nói "viết overview", tổng hợp từ PLAN.md, LOG.md và refs/ vào `OVERVIEW.md` theo `_template`, rồi cập nhật `INDEX.md`.

## Luật

- **Luật 2 thao tác:** cứ sau 2 lần xem, tìm, duyệt web hoặc đọc repo, ghi ngay phát hiện vào `refs/` hoặc `01-NGHIEN-CUU-NEN.md`. Nhất là kết quả nhìn bằng mắt (ảnh, trang web), vì loại này mất đầu tiên khi ngữ cảnh bị nén.
- **Luật 3 lần hỏng:** lần 1 chẩn đoán và sửa đúng chỗ. Lần 2 đổi cách khác, không lặp lại đúng hành động vừa hỏng. Lần 3 nghĩ lại từ gốc, có thể sửa kế hoạch. Sau 3 lần, ghi vào bảng lỗi và báo Linh. Mọi lỗi đều ghi vào bảng lỗi trong PLAN.md để không lặp lại.
- **Quyết định ghi vào sổ** theo mẫu của skill `de-xuat-phuong-an`: `Ruling: <quyết định> — <vì sao> — <sai thì tốn gì>`.
- **Kiểm tra khởi động lại.** Nếu không trả lời được 5 câu sau từ file, kế hoạch đang thiếu, cần bổ sung:

| Câu hỏi | Trả lời ở đâu |
|---|---|
| Đang ở đâu? | Pha `[~]` trong PLAN.md |
| Đi tới đâu? | Các pha còn lại |
| Mục tiêu là gì? | Đầu PLAN.md |
| Đã học được gì? | refs/, 01-NGHIEN-CUU-NEN.md |
| Đã làm gì? | LOG.md |

- Việc chỉ 1–2 bước hoặc câu hỏi nhanh: không cần PLAN.md.
