---
name: soat-ngon-ngu
description: Lượt biên tập 3, soát câu chữ theo hai prompt gốc của Linh - Tổng biên tập CQS 6 trụ cột và máy dò văn AI APS - cộng luật học từ bản sửa của biên tập viên; ra điểm CQS, APS và danh sách sửa từng câu. Dùng trong bien-tap-bai hoặc khi cần soát ngôn ngữ.
---

# Soát ngôn ngữ (lượt 3)

Hai prompt gốc của Linh giữ nguyên văn ở `references/goc/editor-qa.txt` (CQS) và `references/goc/ai-detector.txt` (APS). Skill này chạy chúng như hai subagent tách nhau, rồi lọc kết quả qua luật giọng.

## Cách làm
1. **Subagent A, Tổng biên tập (CQS).** Đưa nguyên văn `editor-qa.txt` làm vai, kèm bài. Thêm ba dòng: ghi lỗi bằng mã ở `references/ma-loi.md`; trích câu gốc nguyên văn; câu đúng giọng tác giả trong `LUAT.md` thì không bắt.
2. **Subagent B, máy dò văn AI (APS).** Đưa nguyên văn `ai-detector.txt`, kèm bài và kết quả lượt 0 (`bt-0-may.md`) để khỏi bắt lại thứ máy đã bắt.
3. **Lọc qua luật giọng** (phiên điều phối làm): với mỗi lỗi A, B trả về
   - bỏ nếu trái `EDITORIAL_CHECKLIST.md` phần C hay `LUAT.md` (ví dụ: CQS chê câu dài, nhưng Linh viết câu dài nối chảy là đúng giọng);
   - gộp nếu hai bên bắt cùng một câu;
   - đổi mã về bảng chung.
4. **Áp luật của biên tập viên**: đọc `ho-so-bien-tap/<ten>/LUAT.md`, với mỗi luật có mẫu kiểm bằng máy (cột "Kiểm") thì grep; luật cần người đọc thì giao cho subagent A trong bước 1.

## Ngưỡng
- CQS ≥ 85 (mức XUẤT BẢN của prompt gốc), APS ≤ 30 (mức CHẤP NHẬN).
- Điểm chỉ để báo. Quyết định giao bài dựa trên lượt 4 (chấm từng câu), vì nghiên cứu nền cho thấy LLM chấm điểm tổng gần như tung đồng xu (Chakrabarty 2025).

## Trả về `bt-3-ngon-ngu.md`
Điểm CQS, APS; bảng `| Câu | Mã | Gốc (CQS/APS/luật VA-xx) | Câu sửa |` tối đa 15 dòng; các lỗi đã bỏ vì trái luật giọng (để tác giả thấy plugin đã nhường chỗ nào).
