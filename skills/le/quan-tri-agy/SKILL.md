---
name: quan-tri-agy
description: Claude làm quản trị dự án tổng cho agy với ít token nhất - nhận lệnh của Linh, viết LENH.md, khởi tạo kế hoạch, giao agy chạy trên máy công ty, rồi chỉ đọc BAO-CAO-QUAN-TRI.md theo lịch. Dùng khi Linh giao việc lớn cho agy, hoặc khi Claude sắp hết quota.
metadata:
  version: "0.1.0"
---

# quan-tri-agy

Linh ra lệnh cho Claude. Claude giao cho agy rồi **chỉ kiểm định kỳ**. Claude không làm thợ, không đọc lại bài dài, không chấm từng phiếu.

## Lúc nhận lệnh (một lần)

1. Viết `LENH.md` trong thư mục việc, tối đa 15 dòng:
   ```
   Việc: ...            Loại: chien-luoc | bao-cao | slide | ...
   Người xem: ai, xem ở đâu, xem xong làm gì
   Hạn: ...             Ràng buộc: ... (ANCHOR khách nếu có)
   Tài liệu đầu vào: đường dẫn
   Ai duyệt cổng: Linh (D2, D4)
   ```
2. Khởi tạo: `python <skills>/agy-tu-chay/scripts/ke_hoach.py moi <thu-muc> --loai <loai> --ten "<tên>"`. Loại chưa có mẫu thì bỏ qua, phiếu đầu của agy là lập kế hoạch.
3. Nhờ Linh bấm duyệt trên **máy công ty** một lần: `dang-ky-lich.ps1 -Viec <thu-muc>` (mỗi 20 phút). Nói rõ máy nào.
4. Đặt lịch tự kiểm cho mình (giãn dần: 1 giờ, 2 giờ, 4 giờ, rồi mỗi sáng).
5. Báo Linh một tin: đã giao gì, bao giờ kiểm lại, khi nào cần Linh.

## Mỗi lần kiểm định kỳ

Chỉ đọc **một file**: `BAO-CAO-QUAN-TRI.md` (≤1 trang). Không mở bài, không mở log, trừ khi báo cáo nói kẹt.

| Báo cáo nói | Claude làm |
|---|---|
| Đang chạy, không có "Cần quyết" | Không nhắn Linh. Hẹn lần kiểm sau. |
| Cổng D2 hoặc D4 chờ | Mở đúng 1 file đầu ra của phiếu cổng, đọc tóm tắt điều hành, rồi gửi Linh 3 dòng + link. Linh đồng ý thì `ke_hoach.py duyet <thu-muc> D2 --nguoi Linh`. |
| Phiếu dừng sau 3 vòng | Đọc 3 dòng nhật ký của phiếu đó. Quyết một trong ba: chia nhỏ phiếu, đổi người chấm, hoặc báo Linh. Ghi quyết định vào `LENH.md`. |
| Không đổi qua 3 lần kiểm | Báo Linh agy có thể đã dừng (máy tắt, hết quota agy). |

## Khi Claude sắp hết quota

1. Sửa `che_do` trong `ke-hoach.json` thành `agy-doc-lap`.
2. Ghi cuối `LENH.md`: "Từ <ngày giờ> Claude vắng; cổng gửi thẳng Linh."
3. Báo Linh: agy vẫn chạy, Linh tự đọc `BAO-CAO-QUAN-TRI.md` khi có tin cổng.

## Ngân sách token

- Mỗi lần kiểm: đọc ≤1 trang, trả lời ≤5 dòng.
- Không tải ảnh, không đọc bài đầy đủ, không chấm lại phiếu agy đã chấm. Chấm chất lượng là việc của người chấm agy và của Linh ở cổng.
- Muốn xem sâu thì giao một phiếu chấm mới cho agy, không tự đọc.
