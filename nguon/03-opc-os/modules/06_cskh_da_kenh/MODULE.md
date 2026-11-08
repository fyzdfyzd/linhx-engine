# Module 06: CSKH Đa Kênh & Inbox 3 Tầng (`06_cskh_da_kenh`)

## 1. Mục tiêu & Vai trò
Gom tin nhắn khách hàng từ nhiều kênh (Web, Zalo OA, Messenger, Email) theo kiến trúc **Inbox 3 tầng của `AmbassadorOS` M8** và thẻ **CS Agent (`OPC001/mau/03-DOI-AGENT.md`)**:
- **Tầng 1 (Auto FAQ)**: Câu hỏi thông thường (cách nhận link, thời gian ra PDF).
- **Tầng 2 (Contextual Report Q&A & Sửa thông tin)**: Khách hỏi giải thích thêm về report đã mua hoặc báo nhập sai giờ sinh → Agent tra cứu dữ kiện đơn và hỗ trợ sinh lại bản cập nhật.
- **Tầng 3 (Escalate lên Founder / Anh Linh)**: Khi khách đòi hoàn tiền, khiếu nại gay gắt, hoặc hỏi câu nhạy cảm (bói bệnh tật, chia tay, giải hạn). **Luật 6.2**: Agent tuyệt đối không được tự hoàn tiền hay hứa hẹn ngoài chính sách.

## 2. Xử lý 3 Ca Lạ (`03_OPC_OS.md` bảng đối chiếu A/B)
1. **`ca_la_1_sai_gio_sinh`**: Khách báo nhập sai giờ sinh (hoặc gõ nhầm giờ sinh không hợp lệ) → Hệ thống/Agent chuẩn hoá lại giờ sinh (hoặc chuyển sang chế độ UBT không giờ sinh) và cấp lại bản PDF chuẩn.
2. **`ca_la_2_hoi_lai_report`**: Khách hỏi sâu về ý nghĩa một mục trong report vừa mua → Đối chiếu đúng dữ kiện (`FactSet`) trong hồ sơ đơn của khách để giải thích kèm miễn trừ trách nhiệm.
3. **`ca_la_3_doi_hoan_tien`**: Khách yêu cầu hoàn tiền → Ghi nhận lịch sự, **chặn tự động chi tiền**, chuyển ngay lên Tầng 3 (`escalated_to_founder = True`) kèm phiếu chờ anh Linh duyệt.

## 3. Giao kèo Sự kiện
- **Lắng nghe**: `khach.hoi`
- **Phát ra**: `cskh.da_tra_loi`, `cskh.chuyen_founder_cap_3`

## 4. Chạy độc lập
```powershell
python modules/06_cskh_da_kenh/module.py --demo
```
