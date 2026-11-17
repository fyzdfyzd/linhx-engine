# Số đo so sánh giao diện Đồng hành cùng Yên Lam (`ui-dong-hanh-17-11`)

- **Môi trường đo**: Máy chủ cục bộ `apps/lab` (`SEED_MAU=1`, `YL_MOI_TRUONG=staging`, AI giả `GEMINI_API_KEY=''`, không gọi khoá thật), trình duyệt Chromium headless qua Playwright.
- **Cấu hình mạng 3G giả lập (Playwright CDP `Network.emulateNetworkConditions`)**: Tải xuống `1,5 Mbps`, tải lên `750 Kbps`, độ trễ `RTT = 150 ms`, tắt bộ nhớ đệm (`Network.setCacheDisabled: true`).
- **Ba phiên bản đối chiếu**:
  1. **Hiện tại (`stg-e2e-17-11` · `00a4d635`)**: Bản trước tối giản (nhiều chữ giải thích mở sẵn, hộp giấy kem đặc trên các màn con, chưa có menu `Thêm` gom tính năng phụ, chưa có màn Ngày sinh riêng, tải đầy đủ video MP4 + nền `kvbg.webp` + webfont `.woff2`).
  2. **Tối giản (mặc định mới trên `ui-dong-hanh-17-11`)**: Kính mờ Yên Lam (`alpha ≤ 0.75` + `backdrop-filter: blur`) + nhận diện VSMCamp/CSMO, đúng 1 màu nhấn cam `#B83A1A`, bộ icon nét SVG tự host thống nhất (`stroke-width=1.9`), nhãn 1–2 chữ + `aria-label`, vùng bấm `≥ 48px`, `CLS = 0`. Màn chính 4 nút lớn nửa dưới màn một tay bấm, ẩn chữ phụ (chỉ hiện khi bấm), tính năng phụ gom vào menu `Thêm`.
  3. **Lite (`?ban=lite`, không đổi mặc định)**: Bản nhẹ cho mạng hội trường nghẽn (giữ nền tối VSMCamp `#081428`, **không phải giao diện sáng**) — bỏ tải video MP4, webfont `.woff2`, ảnh nền `kvbg.webp`, `qr.js` và module phụ; hỏi Lam ngay 1 bước trên màn chính; xác thực OTP bằng 1 ô gọn nhẹ.

## 1. Bảng tổng hợp KB tải, thời gian tải 3G (CDP) và số bước hoàn thành việc chính

| Màn hình | Khổ | Bản | KB tải (CDP) | Số request | Tải trên 3G (ms) | Số bước xong việc chính | Việc chính |
|---|---:|---|---:|---:|---:|---:|---|
| Màn chính (/lam) | 360px | Hiện tại (`stg-e2e-17-11`) | **970.4 KB** | 54 | **5838 ms** | **2 bước** | Hỏi Lam hoặc mở ngay Tạp chí / Lịch phiên bằng 1 tay |
| Màn chính (/lam) | 360px | Tối giản (mặc định mới) | **746.1 KB** | 36 | **4914 ms** | **1 bước** | Hỏi Lam hoặc mở ngay Tạp chí / Lịch phiên bằng 1 tay |
| Màn chính (/lam) | 360px | Lite (`?ban=lite`) | **173.3 KB** | 17 | **3788 ms** | **1 bước** | Hỏi Lam hoặc mở ngay Tạp chí / Lịch phiên bằng 1 tay |
| Màn chính (/lam) | 1280px | Hiện tại (`stg-e2e-17-11`) | **937.3 KB** | 54 | **5808 ms** | **2 bước** | Hỏi Lam hoặc mở ngay Tạp chí / Lịch phiên bằng 1 tay |
| Màn chính (/lam) | 1280px | Tối giản (mặc định mới) | **754.7 KB** | 36 | **3435 ms** | **1 bước** | Hỏi Lam hoặc mở ngay Tạp chí / Lịch phiên bằng 1 tay |
| Màn chính (/lam) | 1280px | Lite (`?ban=lite`) | **174 KB** | 17 | **1960 ms** | **1 bước** | Hỏi Lam hoặc mở ngay Tạp chí / Lịch phiên bằng 1 tay |
| Màn Đồng ý NĐ13 (/lam — khách mới) | 360px | Hiện tại (`stg-e2e-17-11`) | **954.1 KB** | 57 | **4774 ms** | **2 bước** | Đọc tóm tắt trong 3 giây & bấm Đồng ý tiếp tục |
| Màn Đồng ý NĐ13 (/lam — khách mới) | 360px | Tối giản (mặc định mới) | **763 KB** | 37 | **3805 ms** | **1 bước** | Đọc tóm tắt trong 3 giây & bấm Đồng ý tiếp tục |
| Màn Đồng ý NĐ13 (/lam — khách mới) | 360px | Lite (`?ban=lite`) | **178.6 KB** | 21 | **2703 ms** | **1 bước** | Đọc tóm tắt trong 3 giây & bấm Đồng ý tiếp tục |
| Màn Đồng ý NĐ13 (/lam — khách mới) | 1280px | Hiện tại (`stg-e2e-17-11`) | **940.1 KB** | 57 | **4723 ms** | **2 bước** | Đọc tóm tắt trong 3 giây & bấm Đồng ý tiếp tục |
| Màn Đồng ý NĐ13 (/lam — khách mới) | 1280px | Tối giản (mặc định mới) | **760.8 KB** | 37 | **3797 ms** | **1 bước** | Đọc tóm tắt trong 3 giây & bấm Đồng ý tiếp tục |
| Màn Đồng ý NĐ13 (/lam — khách mới) | 1280px | Lite (`?ban=lite`) | **180.1 KB** | 21 | **2705 ms** | **1 bước** | Đọc tóm tắt trong 3 giây & bấm Đồng ý tiếp tục |
| Màn Ngày sinh (/cua-toi/ngay-sinh) | 360px | Hiện tại (`stg-e2e-17-11`) | **927.3 KB** | 53 | **4354 ms** | **3 bước** | Chọn ngày sinh cá nhân hoá & bấm Lưu |
| Màn Ngày sinh (/cua-toi/ngay-sinh) | 360px | Tối giản (mặc định mới) | **803.6 KB** | 39 | **3276 ms** | **2 bước** | Chọn ngày sinh cá nhân hoá & bấm Lưu |
| Màn Ngày sinh (/cua-toi/ngay-sinh) | 360px | Lite (`?ban=lite`) | **230.1 KB** | 22 | **2139 ms** | **2 bước** | Chọn ngày sinh cá nhân hoá & bấm Lưu |
| Màn Ngày sinh (/cua-toi/ngay-sinh) | 1280px | Hiện tại (`stg-e2e-17-11`) | **936.8 KB** | 53 | **4334 ms** | **3 bước** | Chọn ngày sinh cá nhân hoá & bấm Lưu |
| Màn Ngày sinh (/cua-toi/ngay-sinh) | 1280px | Tối giản (mặc định mới) | **775.7 KB** | 39 | **3285 ms** | **2 bước** | Chọn ngày sinh cá nhân hoá & bấm Lưu |
| Màn Ngày sinh (/cua-toi/ngay-sinh) | 1280px | Lite (`?ban=lite`) | **230.5 KB** | 22 | **2102 ms** | **2 bước** | Chọn ngày sinh cá nhân hoá & bấm Lưu |
| Màn Email lead (/cua-toi/email) | 360px | Hiện tại (`stg-e2e-17-11`) | **922.2 KB** | 53 | **3987 ms** | **3 bước** | Nhập email giữ trang & xác nhận mã OTP nhận tạp chí |
| Màn Email lead (/cua-toi/email) | 360px | Tối giản (mặc định mới) | **806.9 KB** | 37 | **3288 ms** | **2 bước** | Nhập email giữ trang & xác nhận mã OTP nhận tạp chí |
| Màn Email lead (/cua-toi/email) | 360px | Lite (`?ban=lite`) | **234 KB** | 22 | **2281 ms** | **2 bước** | Nhập email giữ trang & xác nhận mã OTP nhận tạp chí |
| Màn Email lead (/cua-toi/email) | 1280px | Hiện tại (`stg-e2e-17-11`) | **933.7 KB** | 53 | **3941 ms** | **3 bước** | Nhập email giữ trang & xác nhận mã OTP nhận tạp chí |
| Màn Email lead (/cua-toi/email) | 1280px | Tối giản (mặc định mới) | **811.6 KB** | 37 | **3278 ms** | **2 bước** | Nhập email giữ trang & xác nhận mã OTP nhận tạp chí |
| Màn Email lead (/cua-toi/email) | 1280px | Lite (`?ban=lite`) | **230.3 KB** | 22 | **2108 ms** | **2 bước** | Nhập email giữ trang & xác nhận mã OTP nhận tạp chí |
| Màn Diễn đàn (/dien-dan) | 360px | Hiện tại (`stg-e2e-17-11`) | **960.9 KB** | 58 | **4245 ms** | **3 bước** | Chọn phiên/diễn giả & gửi câu hỏi thảo luận |
| Màn Diễn đàn (/dien-dan) | 360px | Tối giản (mặc định mới) | **737 KB** | 35 | **3355 ms** | **2 bước** | Chọn phiên/diễn giả & gửi câu hỏi thảo luận |
| Màn Diễn đàn (/dien-dan) | 360px | Lite (`?ban=lite`) | **188.2 KB** | 18 | **2213 ms** | **2 bước** | Chọn phiên/diễn giả & gửi câu hỏi thảo luận |
| Màn Diễn đàn (/dien-dan) | 1280px | Hiện tại (`stg-e2e-17-11`) | **948.8 KB** | 58 | **4243 ms** | **3 bước** | Chọn phiên/diễn giả & gửi câu hỏi thảo luận |
| Màn Diễn đàn (/dien-dan) | 1280px | Tối giản (mặc định mới) | **751.5 KB** | 35 | **3307 ms** | **2 bước** | Chọn phiên/diễn giả & gửi câu hỏi thảo luận |
| Màn Diễn đàn (/dien-dan) | 1280px | Lite (`?ban=lite`) | **188.1 KB** | 18 | **2181 ms** | **2 bước** | Chọn phiên/diễn giả & gửi câu hỏi thảo luận |
| Màn Tường ảnh (/anh) | 360px | Hiện tại (`stg-e2e-17-11`) | **939.5 KB** | 53 | **4193 ms** | **3 bước** | Xem tường ảnh chung & bấm Đăng ảnh sự kiện |
| Màn Tường ảnh (/anh) | 360px | Tối giản (mặc định mới) | **752.6 KB** | 34 | **3213 ms** | **2 bước** | Xem tường ảnh chung & bấm Đăng ảnh sự kiện |
| Màn Tường ảnh (/anh) | 360px | Lite (`?ban=lite`) | **191.7 KB** | 19 | **2100 ms** | **1 bước** | Xem tường ảnh chung & bấm Đăng ảnh sự kiện |
| Màn Tường ảnh (/anh) | 1280px | Hiện tại (`stg-e2e-17-11`) | **946.4 KB** | 53 | **4227 ms** | **3 bước** | Xem tường ảnh chung & bấm Đăng ảnh sự kiện |
| Màn Tường ảnh (/anh) | 1280px | Tối giản (mặc định mới) | **746.7 KB** | 34 | **3260 ms** | **2 bước** | Xem tường ảnh chung & bấm Đăng ảnh sự kiện |
| Màn Tường ảnh (/anh) | 1280px | Lite (`?ban=lite`) | **195.3 KB** | 19 | **2060 ms** | **1 bước** | Xem tường ảnh chung & bấm Đăng ảnh sự kiện |
| Màn Của tôi (/cua-toi) | 360px | Hiện tại (`stg-e2e-17-11`) | **925.6 KB** | 53 | **4424 ms** | **2 bước** | Mở Mã QR / Tạp chí / Email hoặc Sửa hồ sơ |
| Màn Của tôi (/cua-toi) | 360px | Tối giản (mặc định mới) | **792.5 KB** | 38 | **3661 ms** | **1 bước** | Mở Mã QR / Tạp chí / Email hoặc Sửa hồ sơ |
| Màn Của tôi (/cua-toi) | 360px | Lite (`?ban=lite`) | **235.6 KB** | 23 | **2485 ms** | **1 bước** | Mở Mã QR / Tạp chí / Email hoặc Sửa hồ sơ |
| Màn Của tôi (/cua-toi) | 1280px | Hiện tại (`stg-e2e-17-11`) | **937 KB** | 53 | **4345 ms** | **2 bước** | Mở Mã QR / Tạp chí / Email hoặc Sửa hồ sơ |
| Màn Của tôi (/cua-toi) | 1280px | Tối giản (mặc định mới) | **791.4 KB** | 38 | **3677 ms** | **1 bước** | Mở Mã QR / Tạp chí / Email hoặc Sửa hồ sơ |
| Màn Của tôi (/cua-toi) | 1280px | Lite (`?ban=lite`) | **232.5 KB** | 23 | **2272 ms** | **1 bước** | Mở Mã QR / Tạp chí / Email hoặc Sửa hồ sơ |
| Màn Lịch & diễn giả (/phien) | 360px | Hiện tại (`stg-e2e-17-11`) | **936 KB** | 53 | **4284 ms** | **2 bước** | Xem lịch trình & chạm + Lưu phiên quan tâm |
| Màn Lịch & diễn giả (/phien) | 360px | Tối giản (mặc định mới) | **741.3 KB** | 34 | **3292 ms** | **1 bước** | Xem lịch trình & chạm + Lưu phiên quan tâm |
| Màn Lịch & diễn giả (/phien) | 360px | Lite (`?ban=lite`) | **175.3 KB** | 20 | **2137 ms** | **1 bước** | Xem lịch trình & chạm + Lưu phiên quan tâm |
| Màn Lịch & diễn giả (/phien) | 1280px | Hiện tại (`stg-e2e-17-11`) | **942.1 KB** | 53 | **4239 ms** | **2 bước** | Xem lịch trình & chạm + Lưu phiên quan tâm |
| Màn Lịch & diễn giả (/phien) | 1280px | Tối giản (mặc định mới) | **727.8 KB** | 34 | **3247 ms** | **1 bước** | Xem lịch trình & chạm + Lưu phiên quan tâm |
| Màn Lịch & diễn giả (/phien) | 1280px | Lite (`?ban=lite`) | **170.7 KB** | 20 | **2141 ms** | **1 bước** | Xem lịch trình & chạm + Lưu phiên quan tâm |
| Màn Bìa & Tạp chí (/cua-toi/bia) | 360px | Hiện tại (`stg-e2e-17-11`) | **930.8 KB** | 55 | **4331 ms** | **3 bước** | Đồng ý ảnh mặt & Tải ảnh lên tạo bìa AGENTIC:ME |
| Màn Bìa & Tạp chí (/cua-toi/bia) | 360px | Tối giản (mặc định mới) | **805.5 KB** | 40 | **3618 ms** | **2 bước** | Đồng ý ảnh mặt & Tải ảnh lên tạo bìa AGENTIC:ME |
| Màn Bìa & Tạp chí (/cua-toi/bia) | 360px | Lite (`?ban=lite`) | **230.4 KB** | 24 | **2458 ms** | **2 bước** | Đồng ý ảnh mặt & Tải ảnh lên tạo bìa AGENTIC:ME |
| Màn Bìa & Tạp chí (/cua-toi/bia) | 1280px | Hiện tại (`stg-e2e-17-11`) | **924 KB** | 55 | **4288 ms** | **3 bước** | Đồng ý ảnh mặt & Tải ảnh lên tạo bìa AGENTIC:ME |
| Màn Bìa & Tạp chí (/cua-toi/bia) | 1280px | Tối giản (mặc định mới) | **791.2 KB** | 40 | **3639 ms** | **2 bước** | Đồng ý ảnh mặt & Tải ảnh lên tạo bìa AGENTIC:ME |
| Màn Bìa & Tạp chí (/cua-toi/bia) | 1280px | Lite (`?ban=lite`) | **234.4 KB** | 24 | **2411 ms** | **2 bước** | Đồng ý ảnh mặt & Tải ảnh lên tạo bìa AGENTIC:ME |

## 2. Phân tích rút gọn bước thao tác & hiệu năng theo từng màn

### Màn chính (/lam)
- **Ảnh ghép so sánh**: `so-sanh-man-chinh.jpg` · Riêng khổ: `so-sanh-man-chinh-360.jpg`, `so-sanh-man-chinh-1280.jpg`
- **Hiệu năng 3G (360px)**: Hiện tại `970.4 KB / 5838 ms` → Tối giản `746.1 KB / 4914 ms` → Lite `173.3 KB / 3788 ms` (**giảm 82.1% dung lượng tải, nhanh hơn 35.1% trên 3G**).
- **Số bước xong việc chính (Hỏi Lam hoặc mở ngay Tạp chí / Lịch phiên bằng 1 tay)**: Hiện tại `2 bước` → Tối giản `1 bước` → Lite `1 bước`. Hiện tại phải bấm biểu tượng bàn phím nhỏ hoặc đọc qua đoạn giới thiệu dài mới gõ hỏi (2 bước), không có nút Tạp chí/Lịch ngay nửa dưới; Tối giản đặt 4 nút lớn ở nửa dưới màn (1 chạm) và Lite đặt sẵn ô gõ hỏi Lam ngay đầu màn (1 bước).

### Màn Đồng ý NĐ13 (/lam — khách mới)
- **Ảnh ghép so sánh**: `so-sanh-dong-y.jpg` · Riêng khổ: `so-sanh-dong-y-360.jpg`, `so-sanh-dong-y-1280.jpg`
- **Hiệu năng 3G (360px)**: Hiện tại `954.1 KB / 4774 ms` → Tối giản `763 KB / 3805 ms` → Lite `178.6 KB / 2703 ms` (**giảm 81.3% dung lượng tải, nhanh hơn 43.4% trên 3G**).
- **Số bước xong việc chính (Đọc tóm tắt trong 3 giây & bấm Đồng ý tiếp tục)**: Hiện tại `2 bước` → Tối giản `1 bước` → Lite `1 bước`. Hiện tại thẻ giấy kem đặc và nhiều chữ pháp lý mở sẵn khiến khách phải đọc/cuộn trước khi bấm (2 bước); Tối giản & Lite gập chi tiết vào "Xem chi tiết", giữ câu chính ≤10 từ + 1 nút cam nổi bật (1 bước).

### Màn Ngày sinh (/cua-toi/ngay-sinh)
- **Ảnh ghép so sánh**: `so-sanh-ngay-sinh.jpg` · Riêng khổ: `so-sanh-ngay-sinh-360.jpg`, `so-sanh-ngay-sinh-1280.jpg`
- **Hiệu năng 3G (360px)**: Hiện tại `927.3 KB / 4354 ms` → Tối giản `803.6 KB / 3276 ms` → Lite `230.1 KB / 2139 ms` (**giảm 75.2% dung lượng tải, nhanh hơn 50.9% trên 3G**).
- **Số bước xong việc chính (Chọn ngày sinh cá nhân hoá & bấm Lưu)**: Hiện tại `3 bước` → Tối giản `2 bước` → Lite `2 bước`. Hiện tại trên stg-e2e-17-11 chưa có màn ngày sinh riêng (rơi về Của tôi); Tối giản & Lite bổ sung màn kính mờ /cua-toi/ngay-sinh với 1 ô chọn ngày + 1 nút Lưu (2 bước).

### Màn Email lead (/cua-toi/email)
- **Ảnh ghép so sánh**: `so-sanh-email-lead.jpg` · Riêng khổ: `so-sanh-email-lead-360.jpg`, `so-sanh-email-lead-1280.jpg`
- **Hiệu năng 3G (360px)**: Hiện tại `922.2 KB / 3987 ms` → Tối giản `806.9 KB / 3288 ms` → Lite `234 KB / 2281 ms` (**giảm 74.6% dung lượng tải, nhanh hơn 42.8% trên 3G**).
- **Số bước xong việc chính (Nhập email giữ trang & xác nhận mã OTP nhận tạp chí)**: Hiện tại `3 bước` → Tối giản `2 bước` → Lite `2 bước`. Hiện tại nhiều chữ giải thích + 6 ô OTP rời trên hộp giấy đặc (3 bước); Tối giản gập chữ phụ vào "Xem chi tiết" và Lite dùng 1 ô mã 6 số gọn nhẹ tự gửi khi đủ 6 số (2 bước).

### Màn Diễn đàn (/dien-dan)
- **Ảnh ghép so sánh**: `so-sanh-dien-dan.jpg` · Riêng khổ: `so-sanh-dien-dan-360.jpg`, `so-sanh-dien-dan-1280.jpg`
- **Hiệu năng 3G (360px)**: Hiện tại `960.9 KB / 4245 ms` → Tối giản `737 KB / 3355 ms` → Lite `188.2 KB / 2213 ms` (**giảm 80.4% dung lượng tải, nhanh hơn 47.9% trên 3G**).
- **Số bước xong việc chính (Chọn phiên/diễn giả & gửi câu hỏi thảo luận)**: Hiện tại `3 bước` → Tối giản `2 bước` → Lite `2 bước`. Hiện tại bộ lọc dài và tiêu đề dày; Tối giản & Lite dùng thanh phân đoạn gọn 1–2 chữ + 1 danh sách kính mờ rõ nút chính (2 bước).

### Màn Tường ảnh (/anh)
- **Ảnh ghép so sánh**: `so-sanh-tuong-anh.jpg` · Riêng khổ: `so-sanh-tuong-anh-360.jpg`, `so-sanh-tuong-anh-1280.jpg`
- **Hiệu năng 3G (360px)**: Hiện tại `939.5 KB / 4193 ms` → Tối giản `752.6 KB / 3213 ms` → Lite `191.7 KB / 2100 ms` (**giảm 79.6% dung lượng tải, nhanh hơn 49.9% trên 3G**).
- **Số bước xong việc chính (Xem tường ảnh chung & bấm Đăng ảnh sự kiện)**: Hiện tại `3 bước` → Tối giản `2 bước` → Lite `1 bước`. Hiện tại tab Ảnh chiếm thanh đáy và nhiều câu dẫn dài; Tối giản gom Tường ảnh vào menu "Thêm", giữ 1 nút chính "Đăng ảnh" (2 bước); Lite hiển thị gọn nhẹ kèm nút chính tải nhanh (1–2 bước).

### Màn Của tôi (/cua-toi)
- **Ảnh ghép so sánh**: `so-sanh-cua-toi.jpg` · Riêng khổ: `so-sanh-cua-toi-360.jpg`, `so-sanh-cua-toi-1280.jpg`
- **Hiệu năng 3G (360px)**: Hiện tại `925.6 KB / 4424 ms` → Tối giản `792.5 KB / 3661 ms` → Lite `235.6 KB / 2485 ms` (**giảm 74.5% dung lượng tải, nhanh hơn 43.8% trên 3G**).
- **Số bước xong việc chính (Mở Mã QR / Tạp chí / Email hoặc Sửa hồ sơ)**: Hiện tại `2 bước` → Tối giản `1 bước` → Lite `1 bước`. Hiện tại hộp giấy kem đặc liệt kê 6 hàng ngang đồng cấp chữ dài khó quét mắt (2 bước); Tối giản chỉ giữ 3 mục cốt lõi có icon nét + công tắc tên (mục phụ gập vào "Mục khác") + 1 nút chính "Sửa hồ sơ" (1 bước); Lite bỏ tải da-luu phụ (1 bước).

### Màn Lịch & diễn giả (/phien)
- **Ảnh ghép so sánh**: `so-sanh-lich-phien.jpg` · Riêng khổ: `so-sanh-lich-phien-360.jpg`, `so-sanh-lich-phien-1280.jpg`
- **Hiệu năng 3G (360px)**: Hiện tại `936 KB / 4284 ms` → Tối giản `741.3 KB / 3292 ms` → Lite `175.3 KB / 2137 ms` (**giảm 81.3% dung lượng tải, nhanh hơn 50.1% trên 3G**).
- **Số bước xong việc chính (Xem lịch trình & chạm + Lưu phiên quan tâm)**: Hiện tại `2 bước` → Tối giản `1 bước` → Lite `1 bước`. Hiện tại thẻ giấy trắng đặc tách rời nền tối; Tối giản & Lite dùng thẻ kính mờ Yên Lam đồng nhất với nút "+ Lưu" ≥48px ngay trên từng dòng và 1 nút chính "Hỏi Lam" (1 bước).

### Màn Bìa & Tạp chí (/cua-toi/bia)
- **Ảnh ghép so sánh**: `so-sanh-tap-chi.jpg` · Riêng khổ: `so-sanh-tap-chi-360.jpg`, `so-sanh-tap-chi-1280.jpg`
- **Hiệu năng 3G (360px)**: Hiện tại `930.8 KB / 4331 ms` → Tối giản `805.5 KB / 3618 ms` → Lite `230.4 KB / 2458 ms` (**giảm 75.2% dung lượng tải, nhanh hơn 43.2% trên 3G**).
- **Số bước xong việc chính (Đồng ý ảnh mặt & Tải ảnh lên tạo bìa AGENTIC:ME)**: Hiện tại `3 bước` → Tối giản `2 bước` → Lite `2 bước`. Hiện tại câu dẫn và nhãn đồng ý dài nhiều dòng; Tối giản & Lite rút gọn câu dẫn ≤8 từ, nhãn nút ngắn gọn ("Mã QR", "Nhận qua email") và 1 nút cam nổi bật tải ảnh làm bìa (2 bước).

