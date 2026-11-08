# Bài Học Rút Ra Từ Prototype `03_OPC_OS` (`BAI_HOC.md`)

> **Dự án**: `03_OPC_OS` · **Ngày đúc kết**: 2026-10-25

---

## Bài học 1: Tách "Luồng Chính Tất Định (A_CODE)" khỏi "Luồng Ngoại Lệ Linh Hoạt (B_AGENT)" giúp giảm 4 lần chi phí AI mà vẫn giải phóng sức người

- **Số đo thực tế**:
  - Trên cùng 10 đơn giả của `OPC001`, Phương án A (`A_CODE` — code cố định, chỉ gọi AI ở bước viết lời dẫn) tốn **43 VNĐ/đơn** (`939 input + 328 output tokens`), chạy lại lần 2 giống hệt **100%**, và tìm lỗi trong log chỉ mất **15 giây**.
  - Ngược lại, Phương án B (`B_AGENT` — Agent điều phối chọn tool) tốn **173 VNĐ/đơn** (đắt gấp **4,0 lần**) ở luồng chuẩn, nhưng lại **tự giải quyết được 2/3 ca lạ** (khách nhắn tin sửa giờ sinh `25:99 -> 08:15` cần tính lại lá số & dựng lại PDF trên cùng link; khách hỏi giải thích sâu về sự kết hợp *Mặt Trời Sư Tử + Cung Mọc Xử Nữ* trong báo cáo đã mua) mà rule `if/else` của A phải đẩy về cho người.
- **Quy tắc áp dụng**: Luồng thanh toán, xuất báo cáo chuẩn và sổ kế toán **bắt buộc dùng A (`A_CODE`)**; luồng CSKH đa kênh (Module 06) và xử lý ca lạ sau bán hàng **dùng B (`B_AGENT`)** kèm rào chắn `FORBIDDEN_AGENT_ACTIONS` (cấm tự hoàn tiền/đổi giá).

---

## Bài học 2: Cổng cắm-rút `plugin.py` (8 dòng code) biến Module 01 thành máy sản xuất đa định dạng (`.pdf`, `.zip`) với 0 dòng sửa cho các OPC tiếp theo

- **Hiện tượng**: Ở Mức 1 (chỉ có OPC 1 Chiêm tinh), Module 01 chỉ biết gọi `astro-engine` và `report-core` để xuất 1 file `.pdf`. Khi cắm **OPC 2 (Bộ Prompt + Template AI Ngân hàng)** cần đóng gói cả `.zip` (18 prompt + 3 template + lịch tập 7 ngày) lẫn `.pdf`, nếu viết nhánh `if opc_id == "opc002..."` trực tiếp trong Module 01 thì mỗi lần thêm OPC mới lại phải sửa code hệ điều hành.
- **Giải pháp đã kiểm chứng**: Chỉ cần thêm **8 dòng nạp động `opcs/<opc_id>/plugin.py`** trong [`modules/01_nghien_cuu_thiet_ke_report/module.py#L145-L152`](file:///D:/LINHX/PROTO/03_OPC_OS/modules/01_nghien_cuu_thiet_ke_report/module.py#L145-L152) và cho phép Module 03 hiển thị nút tải `.zip` tự động nếu payload có `zip_path`. Kết quả: khi cắm tiếp **OPC 3 (Hồ sơ hướng nghiệp học sinh lớp 9–12, PDF 13 trang)**, số dòng code phải sửa ở cả 10 module dùng chung là **0 dòng (`= 0`)**.

---

## Bài học 3: Nhiều OPC dùng chung 1 tài khoản cá nhân/HKD bắt buộc phải dùng chung 1 Sổ Cái Sự Kiện (`FinanceLedgerModule`) để không lọt lưới ngưỡng thuế 400 triệu

- **Hiện tượng**: Nếu mỗi OPC tự ghi một file `so-doanh-thu.csv` riêng, từng OPC nhìn riêng lẻ đều dưới 400 triệu (`OPC 1 = 398,34tr`, `OPC 2 = 399,83tr`), dẫn đến không OPC nào phát cảnh báo thuế dù tổng tiền về tài khoản Vân Anh đã vượt ngưỡng.
- **Giải pháp đã kiểm chứng**: Trong [`scripts/chay_3_opc_va_dashboard.py`](file:///D:/LINHX/PROTO/03_OPC_OS/scripts/chay_3_opc_va_dashboard.py), cả 3 OPC đều phát sự kiện `don.da_tra` vào cùng một `FinanceLedgerModule` gắn với `shared_account_pool = "VAN_ANH_HKD"`. Nhờ đó, ngay tại đơn `HN00002` của OPC 3, tổng doanh thu luỹ kế gộp đạt **`401.332.000 VNĐ`** và hệ thống lập tức bật cờ **`BAO_DO_VUOT_400TR`** trên cả sổ CSV lẫn Dashboard tổng.

---

## Bài học 4: Giữ ấm phiên trình duyệt Chromium (`_get_browser()`) giảm 65% thời gian xuất PDF

- **Số đo thực tế**: Nếu mỗi đơn hàng gọi `sync_playwright().start()` rồi đóng trình duyệt ngay, mỗi file PDF mất `~6,5 – 9,0 giây`. Khi giữ ấm 1 phiên Chromium dùng chung trong tiến trình worker (`vendor/LAB046/report-core/src/report_core/render.py` và `vendor/OPC001/astro-engine/astro_engine/render.py`), thời gian kết xuất mỗi báo cáo PDF 13–30 trang giảm xuống chỉ còn **`~1,2 – 1,8 giây`** (tổng thời gian toàn luồng từ webhook đến xong PDF chỉ **`3,8 – 4,2 giây/đơn`**).
