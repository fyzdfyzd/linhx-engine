---
name: soat-cau-truc
description: Lượt biên tập 2, soát bài ở mức đoạn - mạch, lặp ý, đoạn thừa, mở và kết, nhịp, độ dài theo đơn đặt hàng - và chấm từng đoạn GIỮ, SỬA, CẮT, VIẾT LẠI. Dùng trong bien-tap-bai hoặc khi cần biên tập cấu trúc.
---

# Soát cấu trúc (lượt 2)

Chạy trong subagent mới. Đọc: bài, đơn đặt hàng, `references/goc/EDITORIAL_CHECKLIST.md` phần C, `LUAT.md` của hồ sơ biên tập viên đang dùng.

## Cách làm
1. Đọc một lượt như người đọc báo, không dừng. Ghi lại một câu: "bài này nói gì". Nếu không viết được câu ấy thì lỗi nặng nhất của bài là luận điểm, ghi đầu phiếu.
2. Lập **bản đồ đoạn**: mỗi đoạn một dòng, ghi đoạn ấy làm việc gì (mở cảnh, đưa số, lật, phản đề, đề xuất, kết...). Đây là "khung nhịp" người viết lẽ ra đã có; so với khung nếu người dùng đưa kèm.
3. Soát trên bản đồ:
   - `MD` mạch đứt: đoạn nhắc điều chưa giới thiệu, hoặc không có cầu nối với đoạn trước.
   - `LA` lặp ý: hai đoạn làm cùng một việc. Chỉ rõ giữ đoạn nào.
   - `TH` thừa: đoạn bỏ đi bài vẫn trọn ý (phép thử xoá).
   - `MO`, `KE`: mở bằng bối cảnh hay lý thuyết; kết khuyên nhủ, tóm tắt, tích cực gượng, câu chốt để trích.
   - `NH` nhịp: đoạn dài đều nhau, mỗi đoạn kết bằng một câu chốt ngắn, cảm xúc leo đều không có cú rẽ.
   - `BU`: gạch đầu dòng, hộp tóm tắt, tiêu đề mục rời trong văn xuôi (checklist Linh mục 10).
   - Checklist Linh: chuyện trước lý thuyết sau (mục 2), có chuyện thật cụ thể (3), có chơi chữ (4), chuyện bên lề (5), tự giễu (6), dark observation thả nhẹ (11), mỗi đoạn cho thấy trước khi giải thích (12). Thiếu mục nào thì ghi, kèm gợi ý đặt ở đoạn nào.
   - `DO` độ dài: đếm chữ, so đơn đặt hàng.
4. Chấm từng đoạn: GIỮ / SỬA (kèm mã và cách sửa) / CẮT / VIẾT LẠI (kèm nhiệm vụ mới của đoạn, không viết hộ).

## Trả về `bt-2-cau-truc.md`
Câu "bài này nói gì"; bản đồ đoạn kèm nhãn; danh sách sửa (tối đa 10, nặng trước); các mục checklist còn thiếu; số chữ so với đơn.
