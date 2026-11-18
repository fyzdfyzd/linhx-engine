model: gemini-4-hydrogen-low
phieu: kn-kiem-crawler-fb-m1
may: may-1
trang_thai: xong
tep_doi: (khong)
drive: (khong)
phut: 1.33
token: vao=44313 ra=3288

**Trạng thái:** `CHUA_DANG_NHAP` (không thể chạy quét Facebook qua `LINHX_CRAWLER` ở thời điểm hiện tại)

- **Endpoint:** `POST /api/tasks` và `GET /api/items` (trong [social_routes.py](file:///D:/LINHX_CRAWLER/server/api/social_routes.py), phối hợp worker Chrome Extension [facebook.js](file:///D:/LINHX_CRAWLER/extension/modules/facebook.js) trên cổng mặc định `8000`).
- **Số bài:** `0`
- **Thời gian:** Không có (chưa thực hiện được lượt quét).
- **Lỗi:** Cổng `8000` hiện đang bị dịch vụ khác (Frappe, PID `7608`/`6336`) chiếm dụng, nên server `LINHX_CRAWLER` không chạy trên `http://localhost:8000` và Chrome Extension worker không thể kết nối để nhận task quét `https://www.facebook.com/VnExpress`.
- **Thư mục đích đã tạo:** [xong/kn-kiem-crawler-fb-m1](file:///D:/linhx/hang-doi/runner/viec/lam-viec/xong/kn-kiem-crawler-fb-m1)

`CAN-LINH: Giải phóng cổng 8000 (tắt Frappe đang chiếm cổng 8000), khởi chạy LINHX_CRAWLER server và mở Chrome Extension đã đăng nhập tài khoản Facebook để worker nhận task quét.`
`LENH: cd D:\LINHX_CRAWLER\server && python main.py`
