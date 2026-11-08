# Module 02: Thiết kế Gói giá (`02_thiet_ke_goi_gia`)

## 1. Mục tiêu & Vai trò
Quản lý bậc giá (199k/299k/349k), gói combo, mã giảm giá theo mùa vụ (Tết 06/02/2027, Valentine 14/02/2027, mùa chọn ngành T1–T3/2027), thử nghiệm giá A/B và kiểm tra **Luật 3 Cửa Giá** (bảo đảm biên lợi nhuận gộp ≥ 85% và chịu được chi phí quảng cáo tối đa 40%).

- **Tài sản kế thừa**: `LAB062`, `OPC001/mau/04-MVP.md`, `QUY-CHUAN-OPC.md` mục 6.2.
- **Luật an toàn sắt**: Agent **không được** tự đổi giá bán hoặc tự phát hành mã giảm giá công khai khi chưa có chữ ký duyệt của Founder (`founder_approved = True`).

## 2. Năm Module con
1. **`2.1_bac_gia_tiers`**: Tính giá theo gói sản phẩm khai trong `opc.json`.
2. **`2.2_combo_bundle`**: Gói cặp đôi, gói phòng ban ngân hàng (5 người), gói học sinh + cẩm nang phụ huynh.
3. **`2.3_ma_giam_theo_dip`**: Kiểm tra hạn dùng và mức giảm của mã ưu đãi theo dịp (Tết, Valentine), chặn giảm quá 20% nếu chưa có Founder duyệt.
4. **`2.4_kiem_cua_kinh_te_don_vi`**: Kiểm tra giá sau giảm có giữ biên gộp ≥ 85% và ngân sách CAC cho phép (≤ 40% giá bán) hay không.
5. **`2.5_thu_gia_ab`**: Đề xuất phương án thử giá A/B cho báo cáo tuần của Founder.

## 3. Giao kèo Sự kiện
- **Lắng nghe**: `gia.yeu_cau_tinh`
- **Phát ra**: `gia.da_tinh`, `gia.de_xuat_ab_cho_duyet`

## 4. Chạy độc lập
```powershell
python modules/02_thiet_ke_goi_gia/module.py --demo
```
