# DANH SÁCH ĐỀ XUẤT TÍNH NĂNG NGOÀI ĐỀ GỐC (`DE_XUAT.md` — `03_OPC_OS`)

> Theo Mục 13 (`11_LO_TRINH_VAN_HANH_THAT.md`): *"Không có tính năng ngoài đề gốc. Đếm số nút, tab, mục menu và ô nhập, rồi so với đề. Mỗi thứ thừa là một lỗi... Nếu muốn thêm tính năng thì ghi vào `DE_XUAT.md`, không làm."*

Các phần tử/tính năng dưới đây đã được **cắt bỏ khỏi màn hình chính** trong quá trình tự sửa 3 vòng Cổng A và lưu lại tại đây để chờ anh Linh xem xét ở các giai đoạn sau:

1. **Hộp 3 nút "Xem nhanh 3 bộ hồ sơ mẫu của 3 vị trí Ngân hàng khác nhau" trên trang bán hàng `/store/opc002_bank_prompt_kit`**:
   - *Lý do cắt khỏi trang bán hàng*: Trang bán hàng chỉ phục vụ 1 việc chính duy nhất là khách điền biểu mẫu 2 phút và bấm Đặt mua. Việc để thêm 3 nút xem mẫu (`BK00001`, `BK00002`, `BK00003`) làm tăng số phần tử bấm được từ `17` lên `20` và gây xao nhãng luồng mua hàng.
2. **Hiển thị mở sẵn toàn bộ 61 dòng lịch sử đơn hàng kịch bản trên mặt chính Bảng Điều Khiển (`/`)**:
   - *Lý do thu gọn*: Làm phát sinh `141` phần tử bấm được cùng lúc trên màn chính. Đã chuyển sang hiển thị thẻ tóm tắt 3 dịch vụ kèm đơn mới nhất và thu gọn bảng lịch sử chi tiết vào trong `<details><summary>Xem thêm danh sách đơn hàng chi tiết...</summary></details>`.
3. **Bộ lọc nâng cao theo ngày/kênh thanh toán và biểu đồ xu hướng doanh thu theo tuần**:
   - *Trạng thái*: Chỉ ghi nhận đề xuất, không đưa lên giao diện MVP để giữ màn hình chính tối giản tuyệt đối.
