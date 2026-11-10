# LỆNH · Gom bộ skill viết theo giọng Linh (10/11)

Người ra lệnh: Linh. Quản trị: Claude (cloud). Thợ + người chấm: agy trên máy cty DESKTOP-PVHR2CD, repo `D:\linhx\linhx-engine`, nhánh `claude/project-thread-tw74mw`.

## Việc
Hiện có 4 bộ skill viết chồng nhau: `new-article` (LinhX Write 9 bước), `viet-bai` (7 trạm), `viet-bai-giong-viet` (luồng Vân Anh), `le/bm1_01..09`. Gom thành **một cửa vào**: skill `viet-giong-linh` trong `skills/bo/linhx-viet-bai/skills/`. Không xoá bộ cũ, nhưng cửa vào KHÔNG gọi new-article, viet-bai 7 trạm, BM1 (Linh 10/11: bỏ quy trình cũ, chỉ giữ phản biện Vân Anh: `linhx-bien-tap/ho-so-bien-tap/van-anh/LUAT.md` VA-01..08 + quy tắc BTV longform).

## Cửa vào phải làm gì
1. **Hỏi loại việc, định tuyến** (bảng 4 dòng):
   - Bài báo/op-ed có ý của Linh → luồng Vân Anh (`viet-bai-giong-viet`) là luồng CHÍNH: máy tìm ý + dữ liệu → Linh viết nháp gạch đầu dòng → máy chỉ làm mượt.
   - Chưa có tứ → Giai đoạn 1 + 2 bên dưới, rồi DỪNG chờ Linh viết nháp. Không viết bài tự động từ đầu.
   - Bài có sẵn cần sửa → `soat-giong` + `linhx-bien-tap/bien-tap-bai`.
   - Đoạn ngắn/nugget → register ngắn, không chấm bằng mốc essay.
2. **Hồ sơ giọng chính** = `giong-linh` (sổ tay 11 nước đi) + vault giọng Linh (nugget lời Linh, nhãn từng câu LINH/NGUON; WF16) + mốc 7 bài đã đăng (`references/bai-mau`). Giọng tác giả đè luật chung.
3. **Cổng cấu trúc trước làm mượt**: luận đề một câu, tối đa 3 ý. Chưa qua thì không làm mượt.
4. **Sổ quy ước mỗi bài** (`SO-QUY-UOC.md`: tên riêng, thuật ngữ, cách viết số, ai nói gì).
5. **Kiểm giữ nghĩa sau làm mượt** (`kiem_giu_nghia.py`): số thêm/mất; câu khẳng định đổi mức (rào đón, quy kết, nhân quả, phủ định, điều kiện); bản sau dài > 1,25 lần bản trước; câu đều quá (hệ số biến thiên độ dài câu < 0,35). Sửa 1 lần, trượt lần 2 thì dừng báo người.
6. **Ngưỡng đặt bằng dương tính giả**: chạy máy dò lên 7 bài đã đăng; ngưỡng sao cho 7 bài đó không bị gắn cờ.
7. Bỏ khi sang tiếng Việt: luật gạch ngang dài, ngoặc cong, viết tắt, từ ghép gạch nối.

## Luồng Linh 10/11
Giai đoạn 1 = phát triển ý, tìm nguyên liệu (B1–B3, đích KHO-Y.md). Giai đoạn 2 = ấn định ý và nguyên liệu viết (B4, đích PHIEU-NGUYEN-LIEU.md). Ý ở GĐ2 được phép khác GĐ1, nhưng:
- ghi 1 dòng "đổi từ … sang … vì nguyên liệu …";
- ý đổi thì chấm lại toàn bộ nguyên liệu theo ý mới; thiếu thì quay GĐ1 một vòng hẹp chỉ cho chỗ thiếu, tối đa 1 lần;
- ý mới do Linh chốt, máy chỉ đề xuất.
GĐ3 = Linh viết nháp gạch đầu dòng (luồng Vân Anh), máy chỉ làm mượt.
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

### Đích của B4: PHIEU-NGUYEN-LIEU.md (nguyên liệu đã sơ chế, Linh 10/11)
Đạt khi đủ cả:
1. 1 ý lớn viết thành câu X→Y, ma trận ý lớn ≥ 40/55, qua cổng loại.
2. 2–3 ý phụ, mỗi ý ≥ 15/25, mỗi ý một dòng "vậy thì sao" cho độc giả chính.
3. Mỗi ý phụ 1–2 chất liệu, trong đó ≥ 1 chuyện thật; cả phiếu ≥ 1 chất liệu xuyên ngành hoặc ngạn ngữ, ≤ 2 khung lý thuyết.
4. 100% chất liệu có link gốc + trích nguyên văn + nhãn LINH/NGUON/GIẢ LẬP; 0 mục không nguồn.
5. 1 phản bác mạnh nhất + câu trả lời.
6. 1 gợi ý mở (chuyện hoặc cảnh) + 1 điều độc giả mang về ở kết.
7. Mật độ ý nằm trong dải mat_do_y của 7 bài, theo độ dài kênh.
8. Phiếu ≤ 800 từ, đọc trong 5 phút; mục bị loại để ở phụ lục, không xoá.
Phép thử cuối: Linh viết được nháp gạch đầu dòng từ phiếu mà không phải tìm thêm gì. Phải tìm thêm thì ghi lại thiếu gì để sửa B3.

### Sau D1: lưu kho (Linh 10/11)
Mọi mục tốt của KHO-Y (cả mục bị loại, kèm lý do) ghi vào vault của Linh, không lập kho thứ tư: thẻ chủ đề + loại + nhãn nguồn + cờ "đã kiểm nguồn" để lần sau không kiểm lại. Khuôn và giọng tìm ở D2 cũng lưu như vậy (thư mục khuon/, giong/ trong vault).

### Kim cương 2 (Linh 10/11)
- K1 Tìm khuôn: kho bài mẫu hay → bài kinh điển → sách dạy viết (kim tự tháp ngược, bánh kẹp, khuôn WSJ...). Mỗi khuôn ghi: hợp loại bài nào, độ dài nào, 1 bài thật làm ví dụ. Lọc theo mục tiêu đổi nhận thức (kim tự tháp ngược hợp tin, ít hợp bài đổi nhận thức).
- K2 Tìm giọng: bắt đầu từ 7 bài của Linh; bài giọng kinh điển chỉ được mượn NƯỚC ĐI cụ thể (nhịp, cách mở, cách chuyển), không nhại cả giọng. Mốc đo vẫn là 7 bài của Linh.
- K3 Chấm khuôn và giọng riêng theo độc giả chính, lấy top 2 × top 2 = tối đa 4 phương án (không ghép hết a×b).
- K4 Mỗi phương án AI chỉ viết mẫu ngắn: đoạn mở + dàn ý theo khuôn + 1 đoạn thân (≤ 300 từ). Chấm kỹ: ma trận + kiểm nhắc lại + chấm cặp đảo trái/phải + nhóm giữ riêng. Linh chọn 1 (cổng D3).
- K5 Linh viết nháp gạch đầu dòng theo phương án thắng (luật Vân Anh: AI chỉ dùng được ý, không dùng được diễn đạt); AI làm mượt.
- K6 Tráng giọng + biên tập: luật VA-01..08, kiem_giu_nghia (không đổi ý, mức khẳng định, số), ≤ 3 vòng. Đọc lại cuối là người thật (Linh/Vân Anh) = cổng D4.

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
