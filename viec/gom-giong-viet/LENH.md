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

## Ràng buộc
- Nguồn luật: `/mnt/project-files/BAN-GIAO-0911/WF06-bai-viet-hay.md` (bản chép sẵn ở `viec/gom-giong-viet/nguon/WF06.md`), WF06 + WF16 `NGHIEN-CUU.md` (chép ở `nguon/`).
- Không đổi văn bộ cũ ngoài dòng `description` + một dòng "Đã gộp" đầu SKILL.md.
- Sau khi sửa skill: `python scripts/skill_kiem.py --index`, commit cả `INDEX.md`.
- Không bí mật, không key. Mỗi phiếu một phiên, ≤ 40 phút.
- Cổng D4 (Linh duyệt cửa vào) không tự mở.
