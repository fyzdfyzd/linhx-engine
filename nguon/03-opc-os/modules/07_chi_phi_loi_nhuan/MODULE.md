# Module 07: Chi phí, Lợi nhuận & Báo đỏ 400 Triệu (`07_chi_phi_loi_nhuan`)

## 1. Mục tiêu & Luật An toàn Tài chính
Module 07 là sổ cái kế toán tự động (chuẩn S1a-HKD từ `LAB060`) và bộ kiểm soát tài chính (Finance Agent kiểu "Seymour Cash" theo `QUY-CHUAN-OPC.md` 6.3, 10.1–10.6).

- **Người nghiệm thu**: Chị Giữ Két (CFO)
- **LUẬT AN TOÀN SẮT**:
  1. **Luôn chạy bằng code cố định tất định 100%** ở cả Phương án A lẫn Phương án B.
  2. **Ngưỡng Báo Đỏ 400.000.000 VNĐ tính gộp cả 3 OPC** (vì cả 3 OPC cùng nhận tiền vào tài khoản Vân Anh — chỉ đạo của Chị Giữ Két CFO tại `03_OPC_OS.md` dòng 106). Ngay khi doanh thu luỹ kế gộp chạm hoặc vượt `400.000.000 VNĐ`, sổ cái ghi cờ `BAO_DO_400TR_CHAM_NGUONG` và phát sự kiện khẩn `canh_bao.doanh_thu_400tr`.
  3. **Luật Quảng cáo 40% & Cửa CAC 3 tầng**:
     - Ngân sách quảng cáo 7 ngày ≤ 40% doanh thu 7 ngày.
     - `CAC ≤ 80.000đ`: `BAT_SCALE`
     - `80.000đ < CAC ≤ 150.000đ`: `CHI_RETARGET`
     - `CAC > 150.000đ`: `DUNG_QUANG_CAO`

## 2. Năm Module con
1. **`7.1_so_thu_s1a_hkd`**: Tự động ghi `so-doanh-thu.csv` ngay khi nhận sự kiện `don.da_tra` (chống ghi trùng `ma_don`).
2. **`7.2_so_chi_token_va_ads`**: Ghi `so-chi-phi.csv` (chi phí token AI từ sự kiện `report.xong`, chi phí quảng cáo).
3. **`7.3_pnl_ngay_thang_gop_3_opc`**: Tính Doanh thu, Chi phí AI, Chi phí Ads, Lãi ròng và tỷ lệ `AI Cost / Revenue` (mục tiêu < 10%) cho từng OPC và gộp cả 3 OPC.
4. **`7.4_cua_cac_va_luat_ads_40pct`**: Kiểm tra tự động trần quảng cáo và cửa CAC.
5. **`7.5_canh_bao_do_400_trieu`**: Giám sát luỹ kế gộp trên tài khoản Vân Anh, bật cờ báo đỏ ở mốc `400.000.000 VNĐ`.

## 3. Giao kèo Sự kiện
- **Lắng nghe**: `don.da_tra`, `report.xong`
- **Phát ra**: `so_cai.da_ghi`, `canh_bao.doanh_thu_400tr`

## 4. Chạy độc lập
```powershell
python modules/07_chi_phi_loi_nhuan/module.py --demo
```
