# Hộp thư LAB ↔ BOD

Hai project (LINHX LAB và Board of Director) không nhắn thẳng cho nhau được. Repo này là cầu nối vì cả hai đều đọc được.

| File | Ai ghi | Ai đọc |
|---|---|---|
| `lab-gui-bod.md` | LAB | BOD |
| `bod-gui-lab.md` | BOD | LAB |

## Mỗi sáng (khoảng 7:00 giờ VN)
1. Đọc hộp vào của mình. Mục nào đã xử lý thì đổi `[ ]` thành `[x]` và ghi kết quả ngắn.
2. Ghi thư mới vào hộp ra, trên cùng, dưới tiêu đề ngày `## YYYY-MM-DD`.
3. Commit thẳng lên nhánh của thread rồi mở PR, hoặc ghi qua trạm máy 2 nếu đã đồng bộ.

## Mỗi thư
```
- [ ] [LOẠI] Tiêu đề ngắn | cần gì | hạn | link
```
LOẠI: `BAO-CAO` (tin, không cần làm), `QUYET-DINH` (cần Linh chốt), `GIAO-VIEC` (bên kia làm), `CHUYEN-GIAO` (lab đã thành dự án, chuyển sang BOD).

## Ranh giới
- BOD: business, khách hàng, tiền.
- LAB: thử nghiệm, skill, đội máy agy.
- Lab thành dự án thật thì gửi `CHUYEN-GIAO`, rồi chuyển sang BOD hoặc project riêng (như ifAgent).

## Luật
- Không ghi bí mật, token, số tài khoản, dữ liệu khách.
- Mỗi thư tối đa 1 dòng, chi tiết để link.
- Thư quá 30 ngày đã `[x]` thì chuyển xuống mục `## Lưu` cuối file.
