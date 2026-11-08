# Module 04: Quản lý User & Quyền Dữ liệu Cá nhân (`04_quan_ly_user`)

## 1. Mục tiêu & Vai trò
Quản lý hồ sơ khách hàng, lưu vết đồng ý dữ liệu cá nhân (NĐ 13/2023 & Luật BVDLCN 2026), lịch sử đơn hàng, phân nhóm khách (RFM/Cohort), mô hình **2 hồ sơ Phụ huynh – Học sinh** (cho OPC 3) và **Quyền yêu cầu xoá dữ liệu ngay từ Mức 1** (theo yêu cầu của Anh Vận Hành COO).

## 2. Năm Module con
1. **`4.1_form_va_dong_y_du_lieu`**: Kiểm tra và lưu bằng chứng khách tích chọn ô đồng ý xử lý dữ liệu cá nhân (họ tên, ngày giờ nơi sinh, liên hệ).
2. **`4.2_ho_so_khach_va_2_ho_so_phu_huynh_con`**:
   - Với OPC 1 & 2: Hồ sơ người mua đơn lẻ.
   - Với OPC 3 (Hướng nghiệp học sinh lớp 9–12): Tách **Hồ sơ Phụ huynh** (người mua & ký đồng ý trước) và **Phiên làm bài của Con** (link riêng `/quiz/<token>`, tự động đặt lịch xoá câu trả lời thô sau 30 ngày).
3. **`4.3_lich_su_don`**: Liên kết các mã đơn đã mua theo khách hàng.
4. **`4.4_phan_nhom_crm`**: Phân nhóm `khach_moi`, `khach_mua_lai`, `phu_huynh_chon_nganh`, `bank_ops_pro`.
5. **`4.5_quyen_xoa_du_lieu`**: Thực thi lệnh xoá/ẩn danh hoá toàn bộ dữ liệu cá nhân của khách theo yêu cầu (chỉ giữ dòng doanh thu kế toán bắt buộc theo luật thuế).

## 3. Giao kèo Sự kiện
- **Lắng nghe**: `don.tao_moi`, `user.yeu_cau_xoa`
- **Phát ra**: `user.da_luu_ho_so`, `user.da_xoa_du_lieu`

## 4. Chạy độc lập
```powershell
python modules/04_quan_ly_user/module.py --demo
```
