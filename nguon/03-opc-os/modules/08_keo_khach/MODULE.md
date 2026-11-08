# Module 08: Kéo Khách & Đo Phễu Chuyển Đổi (`08_keo_khach`)

## 1. Mục tiêu & Vai trò
7 module đầu chỉ xử lý sau khi khách đã vào trang. Module 08 phụ trách kéo khách vào phễu, gắn UTM/pixel, đo tỷ lệ chuyển đổi 5 bước (`vào trang → điền form → hiện QR → trả tiền → nhận PDF`), và kiểm soát thử khói quảng cáo ngân sách ≤ 1.000.000 VNĐ / 7 ngày.

- **Người nghiệm thu**: Chị Kể Chuyện (CMO) & Chị Giữ Két (CFO)
- **Tài sản kế thừa**: Kế hoạch `OPC001/mau/05-KPI-NHIP-VAN-HANH.md`, thẻ Ads Agent (`_launchpad`), Luật 3 cửa CAC.

## 2. Bốn Module con
1. **`8.1_landing_page_config`**: Sinh cấu hình landing page (tiêu đề, mồi tóm tắt miễn phí 1 trang, CTA, khối uy tín tác giả sách).
2. **`8.2_utm_pixel_tracker`**: Chuẩn hoá tham số `utm_source`, `utm_medium`, `utm_campaign`, `utm_content` và sự kiện pixel.
3. **`8.3_do_pheu_5_buoc`**: Tính tỷ lệ chuyển đổi qua 5 bước (`landing_view`, `form_submit`, `qr_shown`, `paid`, `pdf_delivered`) và CAC thực tế.
4. **`8.4_thu_khoi_1tr_7ngay`**: Kiểm tra chiến dịch thử khói (ngân sách tối đa 1.000.000đ/7 ngày) và đối chiếu cửa CAC (`≤ 80k` bật, `80–150k` retarget, `> 150k` dừng).

## 3. Giao kèo Sự kiện
- **Lắng nghe**: `don.tao_moi`, `don.da_tra`, `report.xong`
- **Phát ra**: `pheu.cap_nhat_cac`

## 4. Chạy độc lập
```powershell
python modules/08_keo_khach/module.py --demo
```
