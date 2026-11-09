---
name: lab-moi
description: "Mở một thí nghiệm LAB mới hoặc gắn cuộc trò chuyện vào LAB hiện có. Tự động kích hoạt ở đầu mỗi cuộc trò chuyện trong D:\\LINHX\\LAB (Session Gate) hoặc khi Linh nói \"LAB mới: <ý tưởng>\", muốn ghi lại một ý tưởng, hay muốn thử nhanh một ý tưởng trên Claude/Antigravity."
metadata:
  version: "0.1.0"
---
# LAB mới & Cổng đầu cuộc trò chuyện (Session Gate)

Làm đúng quy trình trong `LAB/README.md` và `LAB/AGENTS.md` (nguồn quy tắc của LAB):

## Bước 0: Cổng kiểm tra đầu cuộc trò chuyện (Sử dụng LAB đã có hay Tạo LAB mới?)
1. Đọc `LAB/INDEX.md` và danh sách thư mục `LAB*` trong `D:\LINHX\LAB\`.
2. **Nếu cuộc trò chuyện tiếp nối một LAB đã có**:
   - Chọn đúng `LAB/LAB<số>-<VIẾT-TẮT>/` đó, đọc `OVERVIEW.md` và `LOG.md`.
   - Nếu thư mục đó thiếu `OVERVIEW.md` hoặc `LOG.md`, bổ sung ngay từ `LAB/_template/`.
   - Mở đầu phản hồi bằng: **`[Đang dùng: LAB<số>-<VIẾT-TẮT>]`** và làm việc hoàn toàn bên trong thư mục đó.
3. **Nếu là ý tưởng / chủ đề thử nghiệm mới** (kể cả khi Linh không nói từ khoá `"LAB mới"`):
   - Chạy ngay các bước 1–6 bên dưới để tạo LAB mới trước khi viết code hay tạo file.

## Quy trình tạo 1 LAB mới (Bước 1–6)
1. **Lấy số thứ tự `NNN` (3 chữ số)**:
   - Kiểm tra cả 3 nơi: `LAB/INDEX.md`, toàn bộ thư mục `LAB*` trên đĩa (`D:\LINHX\LAB\`), và `LAB/_archive/`.
   - Lấy `NNN = số lớn nhất đang có + 1` (không bao giờ dùng lại số đã tồn tại).
2. **Đặt tên & Tạo thư mục**:
   - Đề xuất viết tắt `TEN-VIET-TAT` (1–3 cụm, IN HOA, không dấu, nối bằng `-`, ≤ 16 ký tự).
   - Nhân bản `LAB/_template/` thành `LAB/LAB<NNN>-<TEN-VIET-TAT>/` (gồm `OVERVIEW.md`, `LOG.md`, `src/`, `data/`, `output/`, `refs/`).
3. **Điền `OVERVIEW.md`**:
   - Cập nhật YAML frontmatter (`type: exp`, `status: IDEA` hoặc `TESTING`, `created`, `updated`).
   - Điền **Mục 1 (Ý tưởng)** và **Mục 2 (Giả thuyết & Tiêu chí "chạy được" đo được)**. Nếu Linh chưa nói tiêu chí đo được, tự đề xuất 1 tiêu chí cụ thể và hỏi lại trong 1 câu.
4. **Xác định trạng thái**:
   - `IDEA` nếu Linh chỉ muốn ghi lại ý tưởng chưa thử; `TESTING` nếu bắt tay vào thử ngay.
5. **Cập nhật `LAB/INDEX.md` và `LOG.md`**:
   - Thêm 1 dòng vào cuối bảng trong `LAB/INDEX.md`.
   - Ghi mục đầu tiên (`## YYYY-MM-DD HH:MM`) vào `LAB/LAB<NNN>-<TEN-VIET-TAT>/LOG.md`.
6. **Báo lại ở dòng đầu câu trả lời**:
   - Ghi rõ: **`[Đã tạo mới: LAB<NNN>-<TEN-VIET-TAT>]`**, đường dẫn thư mục và tiêu chí "chạy được".
