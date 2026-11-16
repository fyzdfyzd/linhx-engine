# Số đo so sánh giao diện Admin / BTC (`ui-admin-17-11`)

- **Môi trường đo**: Máy chủ cục bộ `apps/lab` (`YL_THU=1`, dữ liệu mẫu chuẩn + 2 máy trạm, AI giả `GEMINI_API_KEY=''`), trình duyệt Chromium headless qua Playwright.
- **Cấu hình mạng 3G giả lập (Playwright CDP `Network.emulateNetworkConditions`)**: Băng thông tải xuống `1,5 Mbps`, tải lên `750 Kbps`, độ trễ `RTT = 150 ms`, tắt hoàn toàn bộ nhớ đệm (`Network.setCacheDisabled: true`).
- **Ba phiên bản đối chiếu**:
  1. **Hiện tại (`stg-e2e-17-11`)**: Bản trước khi tối giản (tải nền `kvbg.jpg`, `logo.png`, 9 tệp font `.woff2`, 8 tệp CSS, 17 tệp JS).
  2. **Tối giản (mặc định mới trên `ui-admin-17-11`)**: Kính mờ Yên Lam + nhận diện VSMCamp/CSMO, 1 màu nhấn `#B83A1A`, bộ icon nét SVG `1.8` tự host, nhãn 1–2 chữ, `aria-label`, vùng bấm `≥ 48px`, mỗi màn đúng 1 việc chính & 1 nút chính nổi bật.
  3. **Lite (`?ban=lite`, không đổi mặc định)**: Bản nhẹ chuyên cho mạng hội trường nghẽn — chỉ giữ tính năng cốt lõi, bỏ ảnh nền/font mạng/SSE/JS màn phụ, phẳng hoá thao tác để ít bước nhất.

## 1. Bảng tổng hợp KB tải, thời gian tải 3G và số bước hoàn thành việc chính

| Màn hình | Khổ | Bản | KB tải (CDP) | Số request | Tải trên 3G (ms) | Số bước xong việc chính | Việc chính |
|---|---:|---|---:|---:|---:|---:|---|
| Tổng quan Admin (#tong-quan) | 360px | Hiện tại | **389.4 KB** | 39 | **3774 ms** | **2 bước** | Kiểm tra sức khoẻ & mở Hàng chờ duyệt |
| Tổng quan Admin (#tong-quan) | 360px | Tối giản | **425.6 KB** | 38 | **4237 ms** | **1 bước** | Kiểm tra sức khoẻ & mở Hàng chờ duyệt |
| Tổng quan Admin (#tong-quan) | 360px | Lite (`?ban=lite`) | **30.1 KB** | 5 | **2610 ms** | **1 bước** | Kiểm tra sức khoẻ & mở Hàng chờ duyệt |
| Tổng quan Admin (#tong-quan) | 1280px | Hiện tại | **390.8 KB** | 40 | **2557 ms** | **2 bước** | Kiểm tra sức khoẻ & mở Hàng chờ duyệt |
| Tổng quan Admin (#tong-quan) | 1280px | Tối giản | **439.7 KB** | 39 | **2789 ms** | **1 bước** | Kiểm tra sức khoẻ & mở Hàng chờ duyệt |
| Tổng quan Admin (#tong-quan) | 1280px | Lite (`?ban=lite`) | **30.1 KB** | 5 | **883 ms** | **1 bước** | Kiểm tra sức khoẻ & mở Hàng chờ duyệt |
| Danh sách khách (#khach) | 360px | Hiện tại | **384.2 KB** | 38 | **2542 ms** | **2 bước** | Lọc tra cứu & Xuất danh sách lead CSV |
| Danh sách khách (#khach) | 360px | Tối giản | **440.7 KB** | 39 | **2765 ms** | **1 bước** | Lọc tra cứu & Xuất danh sách lead CSV |
| Danh sách khách (#khach) | 360px | Lite (`?ban=lite`) | **31.2 KB** | 5 | **881 ms** | **1 bước** | Lọc tra cứu & Xuất danh sách lead CSV |
| Danh sách khách (#khach) | 1280px | Hiện tại | **458.3 KB** | 41 | **3228 ms** | **2 bước** | Lọc tra cứu & Xuất danh sách lead CSV |
| Danh sách khách (#khach) | 1280px | Tối giản | **484.9 KB** | 41 | **3024 ms** | **1 bước** | Lọc tra cứu & Xuất danh sách lead CSV |
| Danh sách khách (#khach) | 1280px | Lite (`?ban=lite`) | **32.9 KB** | 6 | **863 ms** | **1 bước** | Lọc tra cứu & Xuất danh sách lead CSV |
| Chi tiết khách (#khach -> chọn khách) | 360px | Hiện tại | **387.2 KB** | 40 | **4219 ms** | **3 bước** | Xử lý yêu cầu Quên tôi / Mở khoá khách |
| Chi tiết khách (#khach -> chọn khách) | 360px | Tối giản | **442.2 KB** | 40 | **3101 ms** | **2 bước** | Xử lý yêu cầu Quên tôi / Mở khoá khách |
| Chi tiết khách (#khach -> chọn khách) | 360px | Lite (`?ban=lite`) | **32.7 KB** | 6 | **1138 ms** | **2 bước** | Xử lý yêu cầu Quên tôi / Mở khoá khách |
| Chi tiết khách (#khach -> chọn khách) | 1280px | Hiện tại | **459.9 KB** | 42 | **3457 ms** | **3 bước** | Xử lý yêu cầu Quên tôi / Mở khoá khách |
| Chi tiết khách (#khach -> chọn khách) | 1280px | Tối giản | **486.4 KB** | 42 | **3573 ms** | **2 bước** | Xử lý yêu cầu Quên tôi / Mở khoá khách |
| Chi tiết khách (#khach -> chọn khách) | 1280px | Lite (`?ban=lite`) | **34.5 KB** | 7 | **1080 ms** | **2 bước** | Xử lý yêu cầu Quên tôi / Mở khoá khách |
| Cấu hình (#cau-hinh) | 360px | Hiện tại | **391.1 KB** | 40 | **2494 ms** | **3 bước** | Đổi công tắc vận hành Kiosk/Booth & Lưu |
| Cấu hình (#cau-hinh) | 360px | Tối giản | **439.9 KB** | 39 | **2739 ms** | **2 bước** | Đổi công tắc vận hành Kiosk/Booth & Lưu |
| Cấu hình (#cau-hinh) | 360px | Lite (`?ban=lite`) | **30.4 KB** | 5 | **861 ms** | **2 bước** | Đổi công tắc vận hành Kiosk/Booth & Lưu |
| Cấu hình (#cau-hinh) | 1280px | Hiện tại | **389.6 KB** | 39 | **2493 ms** | **3 bước** | Đổi công tắc vận hành Kiosk/Booth & Lưu |
| Cấu hình (#cau-hinh) | 1280px | Tối giản | **439.9 KB** | 39 | **2725 ms** | **2 bước** | Đổi công tắc vận hành Kiosk/Booth & Lưu |
| Cấu hình (#cau-hinh) | 1280px | Lite (`?ban=lite`) | **30.4 KB** | 5 | **873 ms** | **2 bước** | Đổi công tắc vận hành Kiosk/Booth & Lưu |

## 2. Phân tích rút gọn bước thao tác & hiệu năng theo màn

### Tổng quan Admin (#tong-quan)
- **Ảnh ghép tổng hợp (1280 + 360)**: `so-sanh-tong-quan.jpg` · Riêng khổ: `so-sanh-tong-quan-360.jpg`, `so-sanh-tong-quan-1280.jpg`
- **Hiệu năng 3G (360px)**: Hiện tại `389.4 KB / 3774 ms` → Tối giản `425.6 KB / 4237 ms` → Lite `30.1 KB / 2610 ms` (**giảm 92.3% dung lượng, nhanh hơn 30.8% trên 3G**).
- **Số bước việc chính (Kiểm tra sức khoẻ & mở Hàng chờ duyệt)**: Hiện tại `2 bước` → Tối giản `1 bước` → Lite `1 bước`. Hiện tại trên máy tính không có nút mở thẳng Hàng chờ từ Tổng quan (phải tìm ở thanh bên, 2 bước; điện thoại bị chia thẻ nhỏ). Bản Tối giản & Lite đặt 1 nút chính `Duyệt (N)` ngay đầu màn (1 bước).

### Danh sách khách (#khach)
- **Ảnh ghép tổng hợp (1280 + 360)**: `so-sanh-danh-sach-khach.jpg` · Riêng khổ: `so-sanh-danh-sach-khach-360.jpg`, `so-sanh-danh-sach-khach-1280.jpg`
- **Hiệu năng 3G (360px)**: Hiện tại `384.2 KB / 2542 ms` → Tối giản `440.7 KB / 2765 ms` → Lite `31.2 KB / 881 ms` (**giảm 91.9% dung lượng, nhanh hơn 65.3% trên 3G**).
- **Số bước việc chính (Lọc tra cứu & Xuất danh sách lead CSV)**: Hiện tại `2 bước` → Tối giản `1 bước` → Lite `1 bước`. Hiện tại 2 nút phụ đồng cấp dễ nhầm, nhãn dài, cột trạng thái bị cắt chữ. Bản Tối giản & Lite nổi bật đúng 1 nút chính `Xuất CSV` (1 chạm tải ngay).

### Chi tiết khách (#khach -> chọn khách)
- **Ảnh ghép tổng hợp (1280 + 360)**: `so-sanh-chi-tiet-khach.jpg` · Riêng khổ: `so-sanh-chi-tiet-khach-360.jpg`, `so-sanh-chi-tiet-khach-1280.jpg`
- **Hiệu năng 3G (360px)**: Hiện tại `387.2 KB / 4219 ms` → Tối giản `442.2 KB / 3101 ms` → Lite `32.7 KB / 1138 ms` (**giảm 91.6% dung lượng, nhanh hơn 73.0% trên 3G**).
- **Số bước việc chính (Xử lý yêu cầu Quên tôi / Mở khoá khách)**: Hiện tại `3 bước` → Tối giản `2 bước` → Lite `2 bước`. Hiện tại từ danh sách phải cuộn qua nhiều dòng chữ và liên kết phụ mới tới nút Xử lý rồi xác nhận (3 bước). Bản Tối giản & Lite gom chỉ số 1 hàng và đặt 1 nút chính `Xoá dữ liệu` ngay trong tầm mắt -> bấm xác nhận (2 bước).

### Cấu hình (#cau-hinh)
- **Ảnh ghép tổng hợp (1280 + 360)**: `so-sanh-cau-hinh.jpg` · Riêng khổ: `so-sanh-cau-hinh-360.jpg`, `so-sanh-cau-hinh-1280.jpg`
- **Hiệu năng 3G (360px)**: Hiện tại `391.1 KB / 2494 ms` → Tối giản `439.9 KB / 2739 ms` → Lite `30.4 KB / 861 ms` (**giảm 92.2% dung lượng, nhanh hơn 65.5% trên 3G**).
- **Số bước việc chính (Đổi công tắc vận hành Kiosk/Booth & Lưu)**: Hiện tại `3 bước` → Tối giản `2 bước` → Lite `2 bước`. Hiện tại nút `Lưu` nằm cuối cột phải / đáy trang (ở 360px phải cuộn hết 5 thẻ + danh sách máy mới bấm được: 3 bước). Bản Tối giản & Lite ghim nút chính `Lưu` ngay đầu màn: gạt công tắc -> bấm `Lưu` (2 bước).
