# `03_OPC_OS` — Hệ Điều Hành Vận Hành Công Ty Một Người (Plug-and-Play Multi-OPC OS)

> **Chuẩn thiết kế**: `D:\LINHX\PLAN\00_SYSTEM\PROTO_DE\00_CHUAN_PROTO.md`, `D:\LINHX\PLAN\00_SYSTEM\PROTO_DE\03_OPC_OS.md` (Bản 3) & `D:\LINHX\LINHX-OPC\QUY-CHUAN-OPC.md`  
> **Trạng thái**: **HOÀN TẤT KIỂM CHỨNG (10 Module + Đối chiếu A/B + 3 OPC chạy trên cùng OS)** · `verify.py` đạt `100% PASS (Exit Code 0)`

---

## 1. Bài Toán & Kiến Trúc Cắm – Rút

`03_OPC_OS` là hệ điều hành cắm-rút cho phép **1 người (Founder) vận hành nhiều sản phẩm số (OPC)** trên cùng một lõi hạ tầng với thời gian can thiệp **≤ 1,5 giờ/ngày**:
- **Thay sản phẩm = Thay cấu hình `opcs/<tên_opc>/opc.json` (+ `plugin.py` nếu có lõi tính riêng)**, không viết lại hệ thống thanh toán, quản lý khách, sổ kế toán hay bảng điều khiển.
- **Luật an toàn sắt**: Phần tiền (tạo đơn, kiểm khoá SePay, chống trùng giao dịch, ghi sổ doanh thu S1a-HKD, cảnh báo đỏ 400 triệu VNĐ) **luôn là code tất định cố định 100%** ở cả Phương án A và Phương án B. Khoá SePay đọc từ `.env` do anh Linh tự tạo, tuyệt đối không lưu trong mã nguồn hay log.

### 10 Module Độc Lập (`modules/01..10`)
Mỗi module đều có `MODULE.md`, `giao_keo.json` (JSON Schema đầu vào/đầu ra/sự kiện), `module.py` chạy độc lập bằng `--demo`, và cặp `demo/input/demo_in.json` → `demo/output/demo_out.json`:
1. [`01_nghien_cuu_thiet_ke_report`](file:///D:/LINHX/PROTO/03_OPC_OS/modules/01_nghien_cuu_thiet_ke_report/MODULE.md): Lõi tính toán + viết báo cáo + cổng chất lượng 17-luật & chống văn mẫu `01_MAY_TAO_NOI_DUNG` + xuất PDF/ZIP.
2. [`02_thiet_ke_goi_gia`](file:///D:/LINHX/PROTO/03_OPC_OS/modules/02_thiet_ke_goi_gia/MODULE.md): Quản lý bảng giá, gói combo, mã giảm giá có hạn dùng & kiểm cửa kinh tế đơn vị (biên gộp ≥ 85%).
3. [`03_flow_thanh_toan_sinh_report`](file:///D:/LINHX/PROTO/03_OPC_OS/modules/03_flow_thanh_toan_sinh_report/MODULE.md): Tạo đơn, sinh VietQR, xác thực Webhook SePay, chống trùng `tx_id`, nhúng PDF hiển thị trực tiếp trên trang đơn `/o/<token>`.
4. [`04_quan_ly_user`](file:///D:/LINHX/PROTO/03_OPC_OS/modules/04_quan_ly_user/MODULE.md): Hồ sơ khách hàng, lịch sử đơn, bảo vệ dữ liệu cá nhân NĐ 13/2023 & tự xoá bài làm thô của trẻ vị thành niên sau 30 ngày.
5. [`05_quan_ly_content`](file:///D:/LINHX/PROTO/03_OPC_OS/modules/05_quan_ly_content/MODULE.md): Sinh bài nội dung kéo khách theo cấu hình từng OPC, chấm điểm chống văn mẫu (`kiemChatLuong >= 75`) và xếp lịch chờ duyệt.
6. [`06_cskh_da_kenh`](file:///D:/LINHX/PROTO/03_OPC_OS/modules/06_cskh_da_kenh/MODULE.md): Tiếp nhận câu hỏi khách hàng đa kênh, phân tầng Escalation Tier 1/2/3 và chặn hoàn tiền tự động (QUY-CHUAN 6.2).
7. [`07_chi_phi_loi_nhuan`](file:///D:/LINHX/PROTO/03_OPC_OS/modules/07_chi_phi_loi_nhuan/MODULE.md): Ghi sổ doanh thu S1a-HKD (`so-doanh-thu.csv`), tính chi phí AI, kiểm cửa CAC (`80k`/`150k`) và **Báo đỏ 400.000.000 VNĐ gộp cả 3 OPC trên tài khoản Vân Anh**.
8. [`08_keo_khach`](file:///D:/LINHX/PROTO/03_OPC_OS/modules/08_keo_khach/MODULE.md): Gắn UTM, đo phễu 5 bước, khóa trần ngân sách thử khói `≤ 1.000.000 VNĐ / 7 ngày`.
9. [`09_tuan_thu`](file:///D:/LINHX/PROTO/03_OPC_OS/modules/09_tuan_thu/MODULE.md): Cổng chặn pháp lý trước khi nhận tiền thật + bộ 3 văn bản pháp lý nháp (`van_ban_phap_ly/`) chờ luật sư rà.
10. [`10_giam_sat_kpi`](file:///D:/LINHX/PROTO/03_OPC_OS/modules/10_giam_sat_kpi/MODULE.md): Bảng chỉ số 06:00 sáng, cảnh báo đơn kẹt > 5 phút, sao lưu hằng ngày và sinh Báo cáo tuần 6 mục chuẩn `QUY-CHUAN-OPC.md`.

### 3 OPC Đang Chạy Chung Trên Cùng Hệ Điều Hành (`opcs/`)
1. **OPC 1 — Chiêm Tinh Số (`opcs/opc001_chiemtinh`)**: Bản đồ sao cá nhân phương Tây (`astro-engine` + `report-core` 17-luật), giá `199.000đ – 299.000đ`.
2. **OPC 2 — Bộ Prompt + Template AI Cá Nhân Hoá Cho Dân Ngân Hàng (`opcs/opc002_bank_prompt_kit`)**: Điền form 2 phút → sinh gói `.zip` + `.pdf` riêng gồm **18 prompt** khớp 100% vị trí & việc tốn giờ đã khai, **3 template hành chính ngân hàng** và **lịch tập 7 ngày** (`249.000đ`).
3. **OPC 3 — Hồ Sơ Hướng Nghiệp Cho Học Sinh Lớp 9–12 (`opcs/opc003_huong_nghiep_hs`)**: Phụ huynh mua & đồng ý, con làm trắc nghiệm sở thích nghề 6 nhóm bản công khai **IPIP RIASEC** trên link riêng, tự xoá bài làm thô sau 30 ngày, xuất báo cáo PDF **13 trang A4** kèm cẩm nang trò chuyện dành cho phụ huynh (`249.000đ`).

---

## 2. Cách Chạy Kiểm Thử 1 Dòng Lệnh

Sử dụng môi trường Python đã cài sẵn `astro-engine`, `report-core` và `playwright`:

```powershell
$py = "D:\LINHX\LINHX-OPC\OPC001-CHIEMTINH-VN\src\astro-engine\.venv\Scripts\python.exe"

# 1. Chạy kiểm tra nghiệm thu tự động toàn bộ dự án (AC-01 -> AC-07)
& $py "D:\LINHX\PROTO\03_OPC_OS\verify.py"

# 2. Chạy đối chiếu Phương án A (Code thuần) và Phương án B (Agent điều phối)
& $py "D:\LINHX\PROTO\03_OPC_OS\A_CODE\chay_a.py"
& $py "D:\LINHX\PROTO\03_OPC_OS\B_AGENT\chay_b.py"

# 3. Chạy gộp cả 3 OPC trên cùng OS và xuất Dashboard động (dashboard/index.html)
& $py "D:\LINHX\PROTO\03_OPC_OS\scripts\chay_3_opc_va_dashboard.py"

# 4. Chạy độc lập bất kỳ module nào (01 -> 10) ở chế độ --demo
& $py "D:\LINHX\PROTO\03_OPC_OS\modules\01_nghien_cuu_thiet_ke_report\module.py" --demo
```
