---
name: soat-giong
description: Soát bài nháp tiếng Việt theo giọng Linh: chạy script kiem_van.py (dấu hiệu AP-01..AP-20, so mốc giọng, điểm 0-100) rồi đọc 3 lượt độc lập và sửa tối đa 2 vòng. Dùng khi Linh nhờ "soát bài", "bỏ giọng AI", "biên tập lại", "xem bài này có giống tôi không", hoặc ở trạm 6 của viet-bai.
---

# Soát giọng

## Bước 1. Chạy script

```
python ${CLAUDE_PLUGIN_ROOT}/scripts/kiem_van.py kiem <bai.md> --moc ${CLAUDE_PLUGIN_ROOT}/du-lieu/moc-giong.json
```

Thêm `--json` nếu cần đọc bằng máy. Trên Windows dùng `python` hoặc `py`. Script chỉ dùng thư viện chuẩn.

Script báo: các dấu hiệu theo dòng (mã AP từ `_PATTERNS/ANTI_PATTERNS.md` trong vault của Linh), chỉ số lệch mốc, điểm. Bài thuần của Linh đạt 90–99, bài pha 79–91. Dưới 88 thì phải sửa; 88 trở lên vẫn phải đọc. Chữ nằm trong ngoặc kép không bị bắt lỗi, vì thường là trích hoặc nhại.

Điểm không phải mục tiêu. Đừng sửa câu hay chỉ để tăng điểm.

## Bước 2. Ba lượt đọc độc lập

Mỗi lượt là một lần đọc riêng (dùng subagent nếu có), không đọc kết luận của lượt khác:

**Lượt A, giọng.** So với `skills/giong-linh/references/SO-TAY-GIONG.md` và EDITORIAL_CHECKLIST 12 điểm của Linh:
1. Câu dài nối chảy, không cụt lủn kiểu "Đúng vậy."
2. Humor hoặc chuyện trước, lý thuyết sau.
3. Ít nhất một chuyện thật cụ thể (tên giả, năm, chi tiết vật lý).
4. Ít nhất một cú chơi chữ tiếng Việt.
5. Một "chuyện bên lề".
6. Tự giễu, giọng hèn mọn, không đứng trên cao dạy đời.
7. Số theo kênh (essay viết bằng chữ).
8. Không mở bằng lý thuyết hay câu hỏi tu từ.
9. Không kết sáo rỗng.
10. Văn xuôi liền, không gạch đầu dòng, không tiêu đề rời.
11. Quan sát đen tối thả nhẹ, không nhấn.
12. Cho thấy trước, giải thích sau.

**Lượt B, nội dung và tư liệu.** Mỗi con số, mỗi chuyện có trong `nguyen-lieu.md` hoặc `KHO-CHUYEN-THAT.md` không? Mức chắc chắn có bị đẩy lên không? Có câu nào khái quát hoá quá chứng cứ không? Có lập luận nào bỏ qua phản chứng mạnh nhất không?

**Lượt C, người đọc báo.** Đọc như một người lướt Dân trí trên điện thoại lúc 7 giờ sáng: đoạn nào muốn bỏ qua, câu nào muốn chụp màn hình, tít có hứa đúng cái bài cho không.

## Bước 3. Gộp và sửa

Gộp ba lượt thành `bao-cao-soat.md`:
- **Giữ**: những câu, hình ảnh hay nhất, cấm động vào.
- **Sửa**: mỗi mục có dòng, lý do, cách sửa.
- **Bỏ qua**: lỗi script bắt nhưng là giọng Linh.

Sửa một lần. Chạy lại script. Tối đa 2 vòng; sau 2 vòng mà vẫn dở thì giao cho Linh kèm ghi chú, đừng sửa tiếp đến mức nhạt.

## Những thứ không phải lỗi

Mượn từ lieflat-less-ai-tone (đo trên 329 bài người so với 300 bài AI): câu dài ngắn không đều, câu bị động, danh từ hoá, có câu hỏi đều không phải dấu hiệu AI. Đừng sửa những thứ này chỉ vì "nghe như AI".
