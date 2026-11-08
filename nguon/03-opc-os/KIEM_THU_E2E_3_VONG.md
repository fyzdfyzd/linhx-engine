# Hồ Sơ Tổng Hợp Kiểm Thử End-to-End 3 Vòng (`KIEM_THU_E2E_3_VONG.md`)

> **Dự án**: `D:\LINHX\PROTO\03_OPC_OS` · **Quy chuẩn áp dụng**: `00_CHUAN_PROTO.md` (Mục *Tự kiểm 3 vòng*) & Skill `e2e-3-rounds-harsh-reviewer`  
> **Kịch bản thực thi**: [`scripts/run_e2e_round.py`](file:///D:/LINHX/PROTO/03_OPC_OS/scripts/run_e2e_round.py) + [`scripts/chay_3_opc_va_dashboard.py`](file:///D:/LINHX/PROTO/03_OPC_OS/scripts/chay_3_opc_va_dashboard.py) + [`verify.py`](file:///D:/LINHX/PROTO/03_OPC_OS/verify.py)  
> **Checkpoint lưu trên ổ cứng**: [`.handoff/e2e-checkpoint.json`](file:///D:/LINHX/PROTO/03_OPC_OS/.handoff/e2e-checkpoint.json)

---

## 1. Bảng Tiến Độ Điểm Số & Sửa Lỗi Qua 3 Vòng E2E Liên Tiếp

| Vòng E2E | Thời gian chạy | Điểm Reviewer (`/10.0`) | Số lỗi phát hiện (`Findings`) | Lỗi Console / Network | Tóm tắt những gì đã phát hiện (qua soi ảnh chụp `.png`) và đã sửa | Biên bản & Ảnh chụp |
|---|---|---:|---:|---:|---|---|
| **Vòng 1 (`Round 1`)** | `14:23:59` | **`5.00 / 10.0`** | `22` (4 nhóm gốc) | `0 Console` / `4 HTTP 404` | 1) Khung `<embed>` PDF trên trang đơn hiện hộp đen `"Couldn't load plugin."` trên Chromium headless;<br>2) Thanh điều hướng bị bó trong `body { max-width: 860px }` trên trang đơn làm gãy menu thành 3 dòng;<br>3) Form đặt mua trên `/store/*` hiện placeholder thô `[Dữ liệu mẫu ...]` và chưa có API `/api/create-demo-order`;<br>4) Chưa đồng bộ thư mục `reports/` sang `runtime/multi_opc/reports/` và thiếu thẻ `<main>`. | [`E2E-ROUND-1.md`](file:///D:/LINHX/PROTO/03_OPC_OS/reports/E2E-ROUND-1.md) · [`round1-audit.json`](file:///D:/LINHX/PROTO/03_OPC_OS/reports/round1-audit.json) · [`screens/round1/`](file:///D:/LINHX/PROTO/03_OPC_OS/reports/screens/round1/) |
| **Vòng 2 (`Round 2`)** | `14:29:50` | **`9.10 / 10.0`** | `3` (tinh chỉnh sâu) | `1 Console` / `1 Request` | Đã sửa sạch 4 nhóm lỗi lớn của Vòng 1 (nội dung báo cáo của cả 3 OPC đã hiển thị trực tiếp sắc nét ngay trong trang đơn, có hộp `.product-highlights`). Phát hiện thêm 3 điểm tinh chỉnh:<br>1) Trình duyệt gọi `/favicon.ico` và hủy tải `<embed>` ẩn gây `1 Console Error`, link `/privacy` chưa mở 3 văn bản pháp lý;<br>2) 5 nút trên thanh điều hướng hơi dài làm rớt dòng ở `1440px`;<br>3) Nội dung `bao-cao.html` của OPC 3 trong `iframe` sát mép viền trái/phải. | [`E2E-ROUND-2.md`](file:///D:/LINHX/PROTO/03_OPC_OS/reports/E2E-ROUND-2.md) · [`round2-audit.json`](file:///D:/LINHX/PROTO/03_OPC_OS/reports/round2-audit.json) · [`screens/round2/`](file:///D:/LINHX/PROTO/03_OPC_OS/reports/screens/round2/) |
| **Vòng 3 (`Round 3`)** | `14:33:28` | **`9.65 / 10.0`** | **`0`** | **`0 Console` / `0 Failed`** | Đã sửa dứt điểm cả 3 điểm của Vòng 2: phục vụ `/favicon.ico` + trang `/privacy` hiển thị 3 văn bản pháp lý nháp của Module 09; gom thanh điều hướng gọn trên 1 hàng ngang duy nhất; thêm `@media screen { body { padding: 18px 24px; } }` giúp khung báo cáo thoáng đẹp mà vẫn giữ chuẩn **13 trang PDF A4** cho OPC 3. | [`E2E-ROUND-3.md`](file:///D:/LINHX/PROTO/03_OPC_OS/reports/E2E-ROUND-3.md) · [`round3-audit.json`](file:///D:/LINHX/PROTO/03_OPC_OS/reports/round3-audit.json) · [`screens/round3/`](file:///D:/LINHX/PROTO/03_OPC_OS/reports/screens/round3/) |

---

## 2. Kết Quả Kiểm Thử Luồng Backend & Nghiệp Vụ Qua Cả 3 Vòng

1. **10 Module cắm-rút (`modules/01..10`)**: `10/10 PASS` ở cả 3 vòng (`MODULE.md`, `giao_keo.json`, `module.py --demo`, `demo_out.json`, 3 văn bản pháp lý nháp).
2. **Đối chiếu Phương án A (`A_CODE`) vs Phương án B (`B_AGENT`)**:
   - Cả hai khớp **10/10 đơn giả** (0 lỗi), phần tiền chạy bằng code cố định 100%.
   - Phương án A tốn **43 VNĐ/đơn** (`~3,8s – 4,0s/đơn` sau khi làm nóng trình duyệt, xử lý 1/3 ca lạ).
   - Phương án B tốn **173 VNĐ/đơn** (`~4,4s/đơn`, tự xử lý **2/3 ca lạ**, chặn tự hoàn tiền ở ca thứ 3).
3. **3 OPC chạy chung 1 OS (`30/30` kịch bản đơn giả khớp 100%)**:
   - **OPC 1 (`opc001_chiemtinh`)**: `10/10 PASS`, xuất PDF 34 trang (`515 KB`) + hiển thị trực tiếp trên trang đơn `order_CT00001.html`.
   - **OPC 2 (`opc002_bank_prompt_kit`)**: `10/10 PASS`, qua **Cổng CPO** (`3/3` bộ `.zip` + `.pdf` khác nhau cho RM SME, Giao dịch viên Teller, Thẩm định Tín dụng; **100% (18/18) prompt** khớp việc đã khai `>= 70%`).
   - **OPC 3 (`opc003_huong_nghiep_hs`)**: `10/10 PASS`, qua **Cổng Pháp lý Vị thành niên** (IPIP RIASEC 6 nhóm công khai, phụ huynh đồng ý, tự xoá bài làm thô sau **30 ngày**, xuất PDF dài đúng **13 trang A4** nằm trong chuẩn `12–15 trang`, không phán *"con không hợp ngành X"*).
   - **Sổ doanh thu S1a-HKD dùng chung (`so-doanh-thu.csv`)**: Doanh thu luỹ kế gộp cả 3 OPC trên tài khoản Vân Anh đạt **`401.332.000 VNĐ`** → bật **BÁO ĐỎ 400 TRIỆU (`red_alert_400m = True`)** ngay tại đơn `HN00002`.
