# Module 01: Nghiên cứu & Thiết kế Report (`01_nghien_cuu_thiet_ke_report`)

## 1. Mục tiêu & Vai trò trong OPC OS
Module 01 chịu trách nhiệm biến dữ liệu đầu vào của khách hàng (sau khi sự kiện `don.da_tra` phát ra từ Module 03) thành sản phẩm số cá nhân hoá đạt chuẩn chất lượng, xuất ra file PDF (hoặc gói công cụ) để giao trên trang đơn của khách.

- **Người nghiệm thu**: Chị Đóng Gói (CPO)
- **Tài sản kế thừa (chỉ đọc qua `vendor/`)**:
  - `LAB046` (`vendor/LAB046/report-core`): Lõi `FactSet`, `KnowledgeStore` SQLite, `Blueprint`, `QualityGate` 17 luật.
  - `OPC001` (`vendor/OPC001/astro-engine`): Lõi tính thiên văn bản đồ sao `NatalChart`, `astro_calc` (Kerykeion + Swiss Ephemeris), 2.098 đoạn diễn giải `natalData.json`.
  - `LAB062` (`vendor/LAB062/NGHIEN-CUU-HOP-NHAT.md`): Khung chọn ngách và thiết kế sản phẩm quà theo dịp.
  - `Đề 01` (`_DUNG_CHUNG/may_tao_noi_dung_adapter.py`): Chu trình chống AI slop (`taoNoiDung`, `kiemChatLuong`).

## 2. Năm Module con
1. **`1.1_nghien_cuu_ngach`**: Xác định chân dung người mua và cấu trúc giá trị theo `opc.json`.
2. **`1.2_khung_blueprint`**: Nạp cấu trúc chương mục, độ dài tối thiểu, đại từ xưng hô (`bạn`) và từ cấm theo ngành.
3. **`1.3_loi_tinh_tat_dinh`**: Tính toán tất định 100% bằng code (vị trí hành tinh, nhà, góc chiếu, cosmodyne cho Chiêm tinh; chỉ số Pythagoras cho Thần số học).
4. **`1.4_viet_report_chong_slop`**:
   - Ghép kho diễn giải chuẩn + gọi lớp viết lời dẫn cá nhân hoá theo giọng tác giả.
   - Chấm cổng chất lượng 17 luật (`LAB046`) kết hợp `kiemChatLuong` (`Đề 01`).
5. **`1.5_xuat_pdf_kiem_truoc_giao`**:
   - Xuất `bao-cao.html` và `bao-cao.pdf` chuẩn A4 bằng Playwright Chromium.
   - Thực thi **Khâu kiểm trước giao**: 20 report đầu tiên gắn cờ `pending_linh_review_top20` để anh Linh duyệt tay trước khi gửi kênh ngoài, đồng thời trả đường dẫn PDF để hiển thị trên trang đơn.

## 3. Giao kèo Sự kiện (Event Bus)
- **Lắng nghe**: `don.da_tra`
- **Phát ra**: `report.xong` (kèm `pdf_path`, `html_path`, `quality_score`, `slop_check`, `token_usage`, `elapsed_seconds`, `manual_review_required`)

## 4. Chạy độc lập (CLI)
```powershell
python modules/01_nghien_cuu_thiet_ke_report/module.py --demo
```
