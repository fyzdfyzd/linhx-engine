# LỆNH · Gom bộ skill viết theo giọng Linh (10/11)

Người ra lệnh: Linh. Quản trị: Claude (cloud). Thợ + người chấm: agy trên máy cty DESKTOP-PVHR2CD, repo `D:\linhx\linhx-engine`, nhánh `claude/project-thread-tw74mw`.

## Việc
Hiện có 4 bộ skill viết chồng nhau: `new-article` (LinhX Write 9 bước), `viet-bai` (7 trạm), `viet-bai-giong-viet` (luồng Vân Anh), `le/bm1_01..09`. Gom thành **một cửa vào**: skill `viet-giong-linh` trong `skills/bo/linhx-viet-bai/skills/`. Không xoá bộ cũ; bộ cũ thành bước con được cửa vào gọi tới.

## Cửa vào phải làm gì
1. **Hỏi loại việc, định tuyến** (bảng 4 dòng):
   - Bài báo/op-ed có ý của Linh → luồng Vân Anh (`viet-bai-giong-viet`) là luồng CHÍNH: máy tìm ý + dữ liệu → Linh viết nháp gạch đầu dòng → máy chỉ làm mượt.
   - Chưa có tứ → chỉ mượn bước 1–5 của `new-article`/BM1 (gieo ý, 11 câu hỏi, nguồn ≥15, 30 tứ, 3 phương án) rồi DỪNG chờ Linh chọn và viết nháp. Không viết bài tự động từ đầu.
   - Bài có sẵn cần sửa → `soat-giong` + `linhx-bien-tap/bien-tap-bai`.
   - Đoạn ngắn/nugget → register ngắn, không chấm bằng mốc essay.
2. **Hồ sơ giọng chính** = `giong-linh` (sổ tay 11 nước đi) + vault giọng Linh (nugget lời Linh, nhãn từng câu LINH/NGUON; WF16) + mốc 7 bài đã đăng (`references/bai-mau`). Giọng tác giả đè luật chung.
3. **Cổng cấu trúc trước làm mượt**: luận đề một câu, tối đa 3 ý. Chưa qua thì không làm mượt.
4. **Sổ quy ước mỗi bài** (`SO-QUY-UOC.md`: tên riêng, thuật ngữ, cách viết số, ai nói gì).
5. **Kiểm giữ nghĩa sau làm mượt** (`kiem_giu_nghia.py`): số thêm/mất; câu khẳng định đổi mức (rào đón, quy kết, nhân quả, phủ định, điều kiện); bản sau dài > 1,25 lần bản trước; câu đều quá (hệ số biến thiên độ dài câu < 0,35). Sửa 1 lần, trượt lần 2 thì dừng báo người.
6. **Ngưỡng đặt bằng dương tính giả**: chạy máy dò lên 7 bài đã đăng; ngưỡng sao cho 7 bài đó không bị gắn cờ.
7. Bỏ khi sang tiếng Việt: luật gạch ngang dài, ngoặc cong, viết tắt, từ ghép gạch nối.

## Luồng Linh 10/11 (thay bước 1–5 của new-article cho dòng "chưa có tứ")
- B1 Linh nạp ý loé lên + kênh đăng + MỘT câu "tôi nghĩ gì mà người khác chưa nói" (tạm, được đổi).
- B2 Ba độc giả theo kênh, neo vào độc giả thật (bình luận, bài cũ cùng kênh, phân tầng LAB048); chọn MỘT độc giả chính; thêm "họ đã đọc gì về chủ đề này". Không dùng độc giả ảo làm giám khảo giọng.
- B3 Kho ý, nguồn kho = VAULT CỦA LINH (bài cũ + bài tâm đắc; LAB070, D:\LINHX\IDEA\CONTENT_VAULT, D:\@WF\TOOL\CONTENT_VAULT), tìm vault trước rồi mới ra ngoài: chuyện thật đa ngôn ngữ (có Trung, châu Á) → quote → ngạn ngữ, ca dao, tục ngữ, thành ngữ cổ (Việt + nước khác, ghi xuất xứ) → chuyện xuyên ngành làm nền (văn học, sinh học, động vật học, vật lý, hoá học, tôn giáo..., mỗi chuyện có nguồn khoa học/văn bản gốc) → khung lý thuyết (≤ 2) → meme, phim, nhạc, tranh, sách. Hạn mức mỗi loại ≤ 5 mục, chuyện thật ≤ 10; lọc theo độc giả chính.
- Mỗi mục: link gốc + trích nguyên văn ngôn ngữ gốc + nhãn LINH/NGUON/GIẢ LẬP. Quote phải truy được người nói. Nhạc chỉ ghi tên + vì sao hợp, không chép lời.
- DỪNG: ra KHO-Y.md (bảng: mục, loại, nguồn, nhãn, độ hợp 1–3) cho Linh gạch, thêm, phản biện. Chưa duyệt thì không sang dàn ý.
- B4 Từ KHO-Y đã duyệt, đề xuất 3 hướng khác nhau ở LUẬN ĐỀ (không chỉ khác mở bài). Mục tiêu lớn: đổi nhận thức độc giả chính, đưa tới điều mới. Chấm bằng khuon/MA-TRAN-CHAM.md (P04 viết theo bảng dưới), giám khảo phiên mới, không phải phiên tạo hướng. Linh chọn.

### Ma trận chấm (thang 1–5, mỗi mức có mô tả neo)
Ý lớn (luận đề), tổng 55:
| Tiêu chí | Hệ số | 5 điểm khi |
|---|---|---|
| Đổi nhận thức | ×3 | viết được rõ "trước khi đọc độc giả chính nghĩ X, sau khi đọc nghĩ Y", X là niềm tin phổ biến có dẫn chứng |
| Mới với độc giả chính | ×3 | không có trong những gì họ đã đọc (B2); không phải ngược đời cho lạ |
| Đứng vững | ×2 | ≥ 3 mục NGUON trong kho đỡ; đã trả lời phản bác mạnh nhất |
| Của Linh | ×2 | có trong vault/kinh nghiệm Linh; Linh có quyền nói |
| Hợp kênh | ×1 | đúng độ dài, giọng kênh |
Cổng loại: "Đổi nhận thức" < 4 hoặc không viết được X→Y thì loại, bất kể tổng.

Ý phụ (≤ 3 mỗi hướng), mỗi ý tổng 25: đỡ ý lớn (bỏ đi thì ý lớn yếu hẳn) · bằng chứng có nguồn · chất liệu bất ngờ (chuyện thật, xuyên ngành, ngạn ngữ) · chạm pain/gain độc giả chính · không trùng ý phụ khác. Ý phụ < 15 thì thay.

Phong cách tác giả, tổng 15: hướng dùng được bao nhiêu nước đi trong giong-linh · có chuyện người thật + tầm vóc + điều mang về · mức không bị làm phẳng (tránh luật VA-01..08).

Hiệu chuẩn: chấm thử ma trận lên 7 bài đã đăng; bài Linh không vào top thì sửa ma trận trước khi dùng.

### Lượng ý vừa sức đọc (Linh 10/11)
- Ngân sách ý theo độ dài: đo từ 7 bài đã đăng (số ý phụ / 1000 từ, số khái niệm mới mỗi đoạn, số liệu mỗi đoạn), đặt dải theo 7 bài, không tự bịa số.
- Mỗi ý phụ phải có chỗ thở: một chất liệu (chuyện, ví dụ) + một câu "vậy thì sao" cho độc giả. Ý không có chỗ thở thì bỏ hoặc gộp.
- Đoạn mang > 1 khái niệm mới hoặc > 2 con số thì cờ (luật VA "thả số liệu").
- Kiểm nhắc lại: phiên mới đọc mù bài, tóm tắt ý lớn + các ý phụ; so với KHO-Y/luận đề. Nhắc thiếu hay lẫn ý thì bài đang quá tải. Người thật (Linh, Vân Anh) kiểm lần cuối.
- Thứ tự cắt khi thừa: ý phụ điểm thấp nhất → khung lý thuyết → chất liệu trùng chức năng.

## Ràng buộc
- Nguồn luật: `/mnt/project-files/BAN-GIAO-0911/WF06-bai-viet-hay.md` (bản chép sẵn ở `viec/gom-giong-viet/nguon/WF06.md`), WF06 + WF16 `NGHIEN-CUU.md` (chép ở `nguon/`).
- Không đổi văn bộ cũ ngoài dòng `description` + một dòng "Đã gộp" đầu SKILL.md.
- Sau khi sửa skill: `python scripts/skill_kiem.py --index`, commit cả `INDEX.md`.
- Không bí mật, không key. Mỗi phiếu một phiên, ≤ 40 phút.
- Cổng D4 (Linh duyệt cửa vào) không tự mở.
