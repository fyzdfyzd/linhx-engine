# Module 10: Giám Sát, KPI Ngày & Báo Cáo Tuần (`10_giam_sat_kpi`)

## 1. Mục tiêu & Vai trò
Thực thi `QUY-CHUAN-OPC.md` mục 6.3, 7.3, 8, 9 và `03_OPC_OS.md` dòng 74:
1. **KPI Ngày lúc 06:00**: Tổng hợp Top 20 KPI (trong đó 5 KPI chính: Doanh thu, Số đơn `paid`, Tỷ lệ mua/xem thử, Sean Ellis PMF, Tỷ lệ mua lại 60 ngày + Chi phí AI/Doanh thu < 10% + Giờ Founder/ngày).
2. **Cảnh báo vận hành tự động**:
   - Cảnh báo lỗi webhook SePay (`401 Unauthorized` / `underpaid` / `expired`).
   - Cảnh báo đơn đã trả tiền mà quá 5 phút chưa sinh xong PDF.
   - Cảnh báo sụt giảm doanh thu (> 50% theo ngày, > 30% theo tuần).
   - Cảnh báo **Báo đỏ 400 triệu VNĐ** tính gộp cả 3 OPC trên tài khoản Vân Anh.
3. **Sao lưu DB hằng ngày (`daily_backup`)**: Sao lưu `orders.json`, `so-doanh-thu.csv`, `users.json` kèm checksum.
4. **Báo cáo tuần tự động (`bao-cao-tuan.md`)**: Sinh đúng mẫu `QUY-CHUAN-OPC.md` mục 9 & `OPC001/mau/07-BAO-CAO-TUAN.md` (% tiến độ, 3 điểm tốt, 3 điểm chưa tốt, bảng số đo, cổng, quyết định cần Founder, 1 thử nghiệm tuần sau).

## 2. Chạy độc lập
```powershell
python modules/10_giam_sat_kpi/module.py --demo
```
