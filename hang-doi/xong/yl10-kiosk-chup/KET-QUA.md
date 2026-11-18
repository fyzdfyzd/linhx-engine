model: mac-dinh
phieu: yl10-kiosk-chup
may: may-3
trang_thai: xong
tep_doi: (khong)
drive: (khong)
phut: 39.80
token: vao=726583 ra=91149

dat: co
trang_thai: REVIEW
nhanh: `agy/yl10-kiosk-chup`
sha_dinh: `ae3979d4`

### Các lỗi vỡ giao diện đã tìm và sửa (1080×1920, giữ nguyên CSS kính & logo Le Bros)
- **K1 & ngăn phụ** ([kiosk-v09-bo-cuc.css](file:///D:/linhx/ifagent-wt/yl10-kiosk-chup/apps/lab/demos/yen-lam/public/css/kiosk-v09-bo-cuc.css), [kiosk-v09.js](file:///D:/linhx/ifagent-wt/yl10-kiosk-chup/apps/lab/demos/yen-lam/public/js/kiosk-v09.js)): ẩn `visibility: hidden` các ngăn đóng, nâng chấm trang `.kl-wg-cham button` lên `≥44×44px` (trước rò 5 nút `14px` ở đáy `1906px`), tách `data-nut` nút chụp chính.
- **K3 đếm `3-2-1` & `"Lại gần chút nhé"`**: khung camera chuẩn `3:4` (`720×960`, tâm ngang `540px`), cắt canvas `3:4` khớp khung nhìn chống méo webcam 16:9/4:3; bỏ lộ ảnh mặt người lạ `chan-dung.jpg` khi mở `getUserMedia`; thêm dải tối đầu màn chống mờ logo/chữ trên nền camera sáng; số `3-2-1` đúng tâm khung; căn Lam gọn góc trái dưới (không cắt bàn tay trái, không đè viền khung, không thò chân đáy); gỡ ngõ cụt sau 3 lần không thấy mặt & nối mượt fake camera Playwright.
- **K3b chờ bìa chọn 1 trong 4 track** ([kiosk-v09-api.js](file:///D:/linhx/ifagent-wt/yl10-kiosk-chup/apps/lab/demos/yen-lam/modules/csmo/kiosk-v09-api.js)): đưa Lam xuống khoảng thoáng dưới lưới 4 track (trước bị hộp kính che mắt);
...[cat bot]...
hx/ifagent-wt/yl10-kiosk-chup/bang-chung/yl10-kiosk-chup/ghep-03-k3-lai-gan.png) (107 KB): **9/10**
- [ghep-04-k3b-chon-track.png](file:///D:/linhx/ifagent-wt/yl10-kiosk-chup/bang-chung/yl10-kiosk-chup/ghep-04-k3b-chon-track.png) (541 KB): **9.5/10**
- [ghep-05-k4-bia-qr.png](file:///D:/linhx/ifagent-wt/yl10-kiosk-chup/bang-chung/yl10-kiosk-chup/ghep-05-k4-bia-qr.png) (443 KB): **9.5/10**
- Nhật ký: [tien-do.log](file:///D:/linhx/nhat-ky/yl10-kiosk-chup/tien-do.log), [KET-QUA.md](file:///D:/linhx/nhat-ky/yl10-kiosk-chup/KET-QUA.md)

CON_LAI: khong
