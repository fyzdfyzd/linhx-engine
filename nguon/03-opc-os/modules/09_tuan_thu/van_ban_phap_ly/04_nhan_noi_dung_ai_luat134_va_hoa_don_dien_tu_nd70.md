# CHÍNH SÁCH NHÃN NỘI DUNG TRÍ TUỆ NHÂN TẠO (LUẬT 134/2025/QH15) & HOÁ ĐƠN ĐIỆN TỬ (NGHỊ ĐỊNH 70/2025/NĐ-CP)
> **Trạng thái**: `[BẢN NHÁP GỬI LUẬT SƯ & KẾ TOÁN RÀ SOÁT — TRƯỚC KHI MỞ NHẬN TIỀN THẬT]`
> **Áp dụng cho hệ sinh thái OPC**: Chiêm Tinh Số (`OPC001`), Bộ công cụ AI Ngân hàng (`OPC002`), Hồ sơ Hướng nghiệp Học sinh THPT (`OPC003`).

## 1. Quy định Gắn nhãn Nội dung do AI hỗ trợ tạo lập (Tuân thủ Luật Công nghiệp Công nghệ số 134/2025/QH15)
1. **Minh bạch nguồn gốc tạo lập**:
   - Mọi bản báo cáo PDF, trang kết quả trực tuyến và bộ câu lệnh do hệ thống `03_OPC_OS` xuất ra đều kết hợp giữa **Lõi tính toán tất định chuyên ngành** (`astro-engine` cho toạ độ thiên văn, khung nghiệp vụ ngân hàng, hoặc bảng điểm IPIP RIASEC công khai) và **Hệ thống diễn giải ngôn ngữ tự nhiên bằng Trí tuệ nhân tạo (AI)**.
   - Tại trang bìa và chân trang (footer) của mọi bản báo cáo PDF luôn hiển thị rõ dòng nhãn nhận diện không thể tẩy xoá:
     > *"[NHÃN MINH BẠCH AI — LUẬT 134/2025/QH15]: Văn bản phân tích này được tổng hợp từ thông số tính toán tất định và diễn giải ngôn ngữ bởi Trí tuệ nhân tạo dưới sự kiểm duyệt khung nội dung của chuyên gia. Nội dung chỉ phục vụ mục đích tham khảo, chiêm nghiệm và tự khám phá, không thay thế tư vấn y tế, tâm lý lâm sàng, tài chính hay pháp lý."*
2. **Cơ chế Kiểm duyệt Con người (Human-in-the-loop)**:
   - Hệ thống bắt buộc kích hoạt cổng duyệt tay của Chủ sở hữu chuyên môn đối với **20 bản báo cáo đầu tiên** của mỗi dòng sản phẩm trước khi cho phép xuất tự động.
   - Bộ lọc đạo đức & pháp lý (`Module 09`) tự động chặn tuyệt đối các cụm từ phán đoán vận mệnh tiêu cực, mê tín dị đoan hoặc phán xét năng lực học sinh.

## 2. Quy định Xuất Hoá đơn Điện tử & Kê khai Thuế (Tuân thủ Nghị định 70/2025/NĐ-CP sửa đổi NĐ 123/2020/NĐ-CP)
1. **Đơn vị xuất hoá đơn**:
   - Mọi giao dịch thương mại sau khi mở cổng thanh toán thật được ghi nhận doanh thu về **Hộ kinh doanh Vân Anh** (hoàn tất đăng ký kinh doanh và Mã số thuế trước ngày 15/11/2026).
2. **Kết nối Hoá đơn điện tử khởi tạo từ máy tính tiền / phần mềm bán hàng**:
   - Theo Nghị định 70/2025/NĐ-CP, ngay khi giao dịch VietQR/SePay được đối soát thành công ở chế độ vận hành thật, hệ thống kế toán (`Module 07`) ghi sổ doanh thu tức thời (`so-doanh-thu.csv`) kèm mã đơn hàng, thời điểm giao dịch và thông tin người mua (nếu khách hàng yêu cầu xuất hoá đơn điện tử).
   - Khách hàng có nhu cầu nhận Hoá đơn điện tử chỉ cần điền thông tin xuất hoá đơn (Họ tên/Đơn vị, Mã số thuế/CCCD, Email nhận hoá đơn) trên trang tra cứu đơn hàng `/o/<token>` trong vòng 24 giờ kể từ lúc thanh toán.
3. **Cảnh báo Ngưỡng Doanh thu & Nghĩa vụ Thuế Hộ kinh doanh**:
   - Hệ thống `03_OPC_OS` đặt ngưỡng **Cảnh báo Đỏ ở mức 400.000.000 VNĐ/năm** (tính gộp toàn bộ các OPC chạy trên cùng tài khoản Hộ kinh doanh Vân Anh) để chủ động chuẩn bị hồ sơ thuế trước khi chạm ngưỡng chịu thuế GTGT/TNCN theo quy định hiện hành.
