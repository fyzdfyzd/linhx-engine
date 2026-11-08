# LUẬT RIÊNG KHU LAB (`D:\LINHX\LAB`)

> Kế thừa `D:\LINHX\AGENTS.md`. Quy ước chi tiết nằm tại `D:\LINHX\LAB\README.md`.
> Khi làm việc trong `D:\LINHX\LAB`, mọi agent (Claude, Antigravity…) **bắt buộc** tuân thủ luật này trước tiên.

---

## 1. CỔNG BẮT BUỘC ĐẦU MỖI CUỘC TRÒ CHUYỆN (SESSION GATE)

**Nguyên tắc bất khả xâm phạm:** Không có cuộc trò chuyện nào trong `LAB/` được phép chạy "trôi nổi" ngoài một thư mục `LABNNN-TEN-VIET-TAT/`.

Ngay ở lượt trả lời đầu tiên của cuộc trò chuyện (hoặc khi người dùng chuyển sang chủ đề mới), agent **PHẢI** thực hiện 1 trong 2 nhánh sau **trước khi** viết code, tạo file hay chạy lệnh thử nghiệm:

1. **Nhánh 1 — Sử dụng LAB đã có:**
   - Kiểm tra `LAB/INDEX.md` và các thư mục `LABNNN-*` trên đĩa. Nếu yêu cầu của Linh thuộc về một LAB đã tồn tại:
   - Đọc `LABNNN-TEN-VIET-TAT/OVERVIEW.md` và `LOG.md` (cùng `.handoff/` nếu có).
   - Nếu thư mục đó trước đây chưa có `OVERVIEW.md` hoặc `LOG.md`, tạo bổ sung ngay từ `_template/`.
   - Ghi ở dòng đầu tiên của câu trả lời: **`[Đang dùng: LABNNN-TEN-VIET-TAT]`**.
   - Chỉ đọc/ghi/chạy trong phạm vi `LABNNN-TEN-VIET-TAT/` (và cập nhật 1 dòng tương ứng ở `LAB/INDEX.md` khi đổi trạng thái).

2. **Nhánh 2 — Tạo LAB mới (kể cả khi Linh không gõ chữ `"LAB mới"`):**
   - Nếu yêu cầu là một ý tưởng, khảo sát, hoặc thử nghiệm mới chưa có thư mục `LABNNN-*`:
   - Tự động chạy quy trình **Tạo LAB mới** (skill `lab-moi`) ngay lập tức:
     1. Lấy số `NNN` tiếp theo = `max(số trong LAB/INDEX.md, các folder LAB* tại D:\LINHX\LAB, và LAB/_archive/) + 1` (3 chữ số, không trùng).
     2. Đặt mã `LABNNN-TEN-VIET-TAT` (`TEN-VIET-TAT`: 1–3 cụm, IN HOA, không dấu, nối bằng `-`, ≤ 16 ký tự).
     3. Nhân bản từ `LAB/_template/` thành `LAB/LABNNN-TEN-VIET-TAT/` (đủ `OVERVIEW.md`, `LOG.md`, `src/`, `data/`, `output/`, `refs/`).
     4. Điền ngay frontmatter, **Mục 1 (Ý tưởng)** và **Mục 2 (Giả thuyết & Tiêu chí "chạy được" đo được)** vào `OVERVIEW.md`. Nếu Linh chưa nêu tiêu chí đo được, đề xuất 1 tiêu chí cụ thể và hỏi xác nhận ngắn gọn 1 câu.
     5. Ghi mục đầu tiên (`## YYYY-MM-DD HH:MM`) vào `LOG.md`.
     6. Thêm 1 dòng (`IDEA` hoặc `TESTING`) vào cuối bảng `LAB/INDEX.md`.
   - Ghi ở dòng đầu tiên của câu trả lời: **`[Đã tạo mới: LABNNN-TEN-VIET-TAT]`**.

3. **Các hành vi bị cấm tuyệt đối:**
   - **CẤM** tạo file lẻ hoặc thư mục đặt tên tự do trực tiếp dưới `D:\LINHX\LAB\` (như `demo/`, `test/`, `TenDuAn/` không có tiền tố `LABNNN-`).
   - **CẤM** tạo thư mục `LABNNN-...` rỗng chỉ chứa file lẻ mà bỏ qua `OVERVIEW.md`, `LOG.md` và không ghi vào `LAB/INDEX.md`.
   - **CẤM** sửa hoặc xoá các dòng lịch sử cũ trong `LOG.md` (chỉ nối thêm ở cuối).
   - **CẤM** xoá thư mục thí nghiệm (nếu bỏ hẳn, chuyển vào `LAB/_archive/`).

---

## 2. QUY ƯỚC FILE TRONG MỖI LAB (`LABNNN-TEN-VIET-TAT/`)

| Thành phần | Quy tắc bắt buộc |
|---|---|
| `OVERVIEW.md` | Có YAML frontmatter (`type: exp`, `status`, `created`, `updated`, `alias`, `proto`, `tools`, `links`). Mục 1–2 viết ngay khi mở LAB; Mục 3–6 viết khi đóng LAB (`viết overview`). |
| `LOG.md` | Nhật ký theo mốc `## YYYY-MM-DD HH:MM` (`Thử`, `Kết quả`, `Ghi chú`). Chỉ thêm vào cuối file (`append-only`). |
| `src/` | Toàn bộ mã nguồn, script, prompt, file cấu hình của thí nghiệm. |
| `data/` | Dữ liệu đầu vào, mẫu thử. |
| `output/` | Kết quả chạy thử, ảnh chụp màn hình, video demo, báo cáo xuất ra (bằng chứng cho mục 4 của `OVERVIEW.md`). |
| `refs/` | Tài liệu tham khảo, danh sách repo khảo sát, bài viết, ghi chú nghiên cứu nền. |
| `.handoff/` | Thư mục lưu vết bắt buộc của Antigravity (`BANG.md`, `VAN-DE.md`, `logs/`, `BAO-CAO.md`) và file bàn giao từ Claude (`tasks/`, `HANDOFF-*.md`). |

---

## 3. ĐÓNG LAB & CỔNG LÊN PROTOTYPE

- Khi kết thúc thí nghiệm hoặc khi Linh nhắn `viết overview`, chạy skill `viet-overview`:
  1. Đọc `LOG.md` và `output/` để hoàn thiện mục 3–6 của `OVERVIEW.md`.
  2. Cập nhật `status` (`WORKS`, `PARTIAL`, `FAILED`, `PARKED`) trong `OVERVIEW.md` và dòng tương ứng ở `LAB/INDEX.md`.
- **Cổng lên PROTOTYPE:**
  - Khi LAB đạt `WORKS`, chấm **nháp** 3 tiêu chí (thang 1–5) ở mục 6 của `OVERVIEW.md`: **Giá trị**, **Phù hợp**, **Chi phí prototype** (5 = dựng được trong dưới 1 tuần).
  - Tổng ≥ 11: chủ động đề xuất lên PROTOTYPE (skill `proto-moi`). Thấp hơn: chỉ ghi điểm.
  - Linh có quyền đưa bất kỳ LAB nào lên PROTOTYPE. Khi đã chuyển sang `PROTOTYPE/PRTNNN-TEN-VIET-TAT`, đổi trạng thái LAB thành `PROMOTED` và điền `proto: PRTNNN-TEN-VIET-TAT` vào frontmatter.
