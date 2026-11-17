# Số đo so sánh giao diện Kiosk / Booth (`ui-kiosk-17-11`)

- **Môi trường đo**: Máy chủ cục bộ `apps/lab` (`YL_THU=1`, máy trạm kích hoạt mẫu, AI giả `GEMINI_API_KEY=''`, không gọi khoá thật), trình duyệt Chromium headless qua Playwright.
- **Cấu hình mạng 3G giả lập (Playwright CDP `Network.emulateNetworkConditions`)**: Băng thông tải xuống `1,5 Mbps`, tải lên `750 Kbps`, độ trễ `RTT = 150 ms`, tắt hoàn toàn bộ nhớ đệm (`Network.setCacheDisabled: true`).
- **Ba phiên bản đối chiếu trên 3 khổ (`360×800`, `1280×800`, và màn cảm ứng `1080×1920`)**:
  1. **Hiện tại (`stg-e2e-17-11`)**: Bản trước tối giản (tải nền KV `.jpg`, logo `.png`, ảnh/video Lam `.webp`/`.webm`, 7 ảnh chân dung diễn giả `.jpg`, toàn bộ bộ dựng tạp chí 8 trang).
  2. **Tối giản (mặc định mới trên `ui-kiosk-17-11`)**: Nhận diện VSMCamp/CSMO + kính mờ Yên Lam (glassmorphism, không khối màu đặc), một màu nhấn `#0066B3`, bộ icon nét SVG tự host đồng độ dày `stroke-width="2"`, nhãn tiếng Việt 1–2 chữ, `aria-label` đầy đủ, vùng bấm `≥ 48px` (`≥ 72px` trên `1080×1920`), mỗi màn 1 việc chính & 1 nút chính nổi bật.
  3. **Lite (`?ban=lite`, không đổi mặc định)**: Bản nhẹ chuyên cho mạng hội trường nghẽn — giữ tính năng cốt lõi, cắt ảnh nền/video/ảnh diễn giả/JS dựng tạp chí nặng & SSE nền, rút ngắn bước thao tác (K1 nhảy thẳng K3, nút `Chụp ngay` không chờ hết đếm ngược, ẩn QR phụ).

## 1. Bảng tổng hợp KB tải, thời gian tải 3G và số bước hoàn thành việc chính

| Màn hình | Khổ | Bản | KB tải (CDP) | Số request | Tải trên 3G (ms) | Số bước xong việc chính | Việc chính |
|---|---:|---|---:|---:|---:|---:|---|
| Màn chờ / chào Kiosk Yên Lam | 360px | Hiện tại | **3463.5 KB** | 48 | **13388 ms** | **2 bước** | Bắt đầu hỏi Yên Lam hoặc chuyển sang chụp bìa |
| Màn chờ / chào Kiosk Yên Lam | 360px | Tối giản | **3552.2 KB** | 51 | **13694 ms** | **1 bước** | Bắt đầu hỏi Yên Lam hoặc chuyển sang chụp bìa |
| Màn chờ / chào Kiosk Yên Lam | 360px | Lite (`?ban=lite`) | **448.3 KB** | 16 | **3524 ms** | **1 bước** | Bắt đầu hỏi Yên Lam hoặc chuyển sang chụp bìa |
| Màn chờ / chào Kiosk Yên Lam | 1280px | Hiện tại | **3426.7 KB** | 48 | **13351 ms** | **2 bước** | Bắt đầu hỏi Yên Lam hoặc chuyển sang chụp bìa |
| Màn chờ / chào Kiosk Yên Lam | 1280px | Tối giản | **3562 KB** | 51 | **13664 ms** | **1 bước** | Bắt đầu hỏi Yên Lam hoặc chuyển sang chụp bìa |
| Màn chờ / chào Kiosk Yên Lam | 1280px | Lite (`?ban=lite`) | **441.8 KB** | 16 | **3501 ms** | **1 bước** | Bắt đầu hỏi Yên Lam hoặc chuyển sang chụp bìa |
| Màn chờ / chào Kiosk Yên Lam | 1080×1920 | Hiện tại | **3483.4 KB** | 48 | **13353 ms** | **2 bước** | Bắt đầu hỏi Yên Lam hoặc chuyển sang chụp bìa |
| Màn chờ / chào Kiosk Yên Lam | 1080×1920 | Tối giản | **3572.7 KB** | 51 | **12140 ms** | **1 bước** | Bắt đầu hỏi Yên Lam hoặc chuyển sang chụp bìa |
| Màn chờ / chào Kiosk Yên Lam | 1080×1920 | Lite (`?ban=lite`) | **443.9 KB** | 16 | **2096 ms** | **1 bước** | Bắt đầu hỏi Yên Lam hoặc chuyển sang chụp bìa |
| Màn nói / nhắn với Yên Lam | 360px | Hiện tại | **3499.7 KB** | 48 | **11886 ms** | **3 bước** | Đặt câu hỏi cho Yên Lam và nhận thông tin sự kiện |
| Màn nói / nhắn với Yên Lam | 360px | Tối giản | **3589.6 KB** | 51 | **12162 ms** | **2 bước** | Đặt câu hỏi cho Yên Lam và nhận thông tin sự kiện |
| Màn nói / nhắn với Yên Lam | 360px | Lite (`?ban=lite`) | **442.5 KB** | 16 | **2130 ms** | **2 bước** | Đặt câu hỏi cho Yên Lam và nhận thông tin sự kiện |
| Màn nói / nhắn với Yên Lam | 1280px | Hiện tại | **3483.6 KB** | 48 | **11826 ms** | **3 bước** | Đặt câu hỏi cho Yên Lam và nhận thông tin sự kiện |
| Màn nói / nhắn với Yên Lam | 1280px | Tối giản | **3574 KB** | 51 | **12149 ms** | **2 bước** | Đặt câu hỏi cho Yên Lam và nhận thông tin sự kiện |
| Màn nói / nhắn với Yên Lam | 1280px | Lite (`?ban=lite`) | **444 KB** | 16 | **2111 ms** | **2 bước** | Đặt câu hỏi cho Yên Lam và nhận thông tin sự kiện |
| Màn nói / nhắn với Yên Lam | 1080×1920 | Hiện tại | **3505.9 KB** | 48 | **11880 ms** | **3 bước** | Đặt câu hỏi cho Yên Lam và nhận thông tin sự kiện |
| Màn nói / nhắn với Yên Lam | 1080×1920 | Tối giản | **3581.6 KB** | 51 | **12100 ms** | **2 bước** | Đặt câu hỏi cho Yên Lam và nhận thông tin sự kiện |
| Màn nói / nhắn với Yên Lam | 1080×1920 | Lite (`?ban=lite`) | **442.4 KB** | 16 | **2119 ms** | **2 bước** | Đặt câu hỏi cho Yên Lam và nhận thông tin sự kiện |
| Màn chờ / chào Booth AGENTIC:ME (K1) | 360px | Hiện tại | **1231.9 KB** | 24 | **5069 ms** | **2 bước** | Chạm bắt đầu chụp bìa tạp chí cá nhân |
| Màn chờ / chào Booth AGENTIC:ME (K1) | 360px | Tối giản | **1254.5 KB** | 26 | **5331 ms** | **1 bước** | Chạm bắt đầu chụp bìa tạp chí cá nhân |
| Màn chờ / chào Booth AGENTIC:ME (K1) | 360px | Lite (`?ban=lite`) | **273.1 KB** | 7 | **1886 ms** | **1 bước** | Chạm bắt đầu chụp bìa tạp chí cá nhân |
| Màn chờ / chào Booth AGENTIC:ME (K1) | 1280px | Hiện tại | **1301.3 KB** | 24 | **5207 ms** | **2 bước** | Chạm bắt đầu chụp bìa tạp chí cá nhân |
| Màn chờ / chào Booth AGENTIC:ME (K1) | 1280px | Tối giản | **1289.5 KB** | 26 | **5426 ms** | **1 bước** | Chạm bắt đầu chụp bìa tạp chí cá nhân |
| Màn chờ / chào Booth AGENTIC:ME (K1) | 1280px | Lite (`?ban=lite`) | **273.1 KB** | 7 | **1888 ms** | **1 bước** | Chạm bắt đầu chụp bìa tạp chí cá nhân |
| Màn chờ / chào Booth AGENTIC:ME (K1) | 1080×1920 | Hiện tại | **1257.8 KB** | 24 | **5119 ms** | **2 bước** | Chạm bắt đầu chụp bìa tạp chí cá nhân |
| Màn chờ / chào Booth AGENTIC:ME (K1) | 1080×1920 | Tối giản | **1269.1 KB** | 26 | **5324 ms** | **1 bước** | Chạm bắt đầu chụp bìa tạp chí cá nhân |
| Màn chờ / chào Booth AGENTIC:ME (K1) | 1080×1920 | Lite (`?ban=lite`) | **275.1 KB** | 7 | **1909 ms** | **1 bước** | Chạm bắt đầu chụp bìa tạp chí cá nhân |
| Form chọn Track chủ đề (AM-02d) | 360px | Hiện tại | **1005.2 KB** | 19 | **3608 ms** | **3 bước** | Chọn tối đa 3 Track quan tâm và xác nhận |
| Form chọn Track chủ đề (AM-02d) | 360px | Tối giản | **1046.8 KB** | 21 | **4032 ms** | **2 bước** | Chọn tối đa 3 Track quan tâm và xác nhận |
| Form chọn Track chủ đề (AM-02d) | 360px | Lite (`?ban=lite`) | **282.8 KB** | 7 | **1953 ms** | **2 bước** | Chọn tối đa 3 Track quan tâm và xác nhận |
| Form chọn Track chủ đề (AM-02d) | 1280px | Hiện tại | **999 KB** | 19 | **3597 ms** | **3 bước** | Chọn tối đa 3 Track quan tâm và xác nhận |
| Form chọn Track chủ đề (AM-02d) | 1280px | Tối giản | **1045 KB** | 21 | **4008 ms** | **2 bước** | Chọn tối đa 3 Track quan tâm và xác nhận |
| Form chọn Track chủ đề (AM-02d) | 1280px | Lite (`?ban=lite`) | **282.5 KB** | 7 | **1873 ms** | **2 bước** | Chọn tối đa 3 Track quan tâm và xác nhận |
| Form chọn Track chủ đề (AM-02d) | 1080×1920 | Hiện tại | **998.9 KB** | 19 | **3587 ms** | **3 bước** | Chọn tối đa 3 Track quan tâm và xác nhận |
| Form chọn Track chủ đề (AM-02d) | 1080×1920 | Tối giản | **1042.7 KB** | 21 | **4031 ms** | **2 bước** | Chọn tối đa 3 Track quan tâm và xác nhận |
| Form chọn Track chủ đề (AM-02d) | 1080×1920 | Lite (`?ban=lite`) | **277.9 KB** | 7 | **1897 ms** | **2 bước** | Chọn tối đa 3 Track quan tâm và xác nhận |
| Form chọn Diễn giả (AM-02e) | 360px | Hiện tại | **1230 KB** | 26 | **5104 ms** | **3 bước** | Chọn diễn giả yêu thích cho ấn bản tạp chí |
| Form chọn Diễn giả (AM-02e) | 360px | Tối giản | **1235 KB** | 28 | **5321 ms** | **2 bước** | Chọn diễn giả yêu thích cho ấn bản tạp chí |
| Form chọn Diễn giả (AM-02e) | 360px | Lite (`?ban=lite`) | **272.3 KB** | 7 | **1901 ms** | **1 bước** | Chọn diễn giả yêu thích cho ấn bản tạp chí |
| Form chọn Diễn giả (AM-02e) | 1280px | Hiện tại | **1238.1 KB** | 26 | **5137 ms** | **3 bước** | Chọn diễn giả yêu thích cho ấn bản tạp chí |
| Form chọn Diễn giả (AM-02e) | 1280px | Tối giản | **1224.8 KB** | 28 | **5338 ms** | **2 bước** | Chọn diễn giả yêu thích cho ấn bản tạp chí |
| Form chọn Diễn giả (AM-02e) | 1280px | Lite (`?ban=lite`) | **273.9 KB** | 7 | **1910 ms** | **1 bước** | Chọn diễn giả yêu thích cho ấn bản tạp chí |
| Form chọn Diễn giả (AM-02e) | 1080×1920 | Hiện tại | **1238.4 KB** | 26 | **5137 ms** | **3 bước** | Chọn diễn giả yêu thích cho ấn bản tạp chí |
| Form chọn Diễn giả (AM-02e) | 1080×1920 | Tối giản | **1244.4 KB** | 28 | **5337 ms** | **2 bước** | Chọn diễn giả yêu thích cho ấn bản tạp chí |
| Form chọn Diễn giả (AM-02e) | 1080×1920 | Lite (`?ban=lite`) | **274.8 KB** | 7 | **1944 ms** | **1 bước** | Chọn diễn giả yêu thích cho ấn bản tạp chí |
| Màn chụp ảnh bìa (K3) | 360px | Hiện tại | **1175.7 KB** | 17 | **4844 ms** | **3 bước** | Canh khung camera và chụp ảnh lên bìa |
| Màn chụp ảnh bìa (K3) | 360px | Tối giản | **1497.3 KB** | 19 | **5170 ms** | **3 bước** | Canh khung camera và chụp ảnh lên bìa |
| Màn chụp ảnh bìa (K3) | 360px | Lite (`?ban=lite`) | **272.7 KB** | 7 | **1934 ms** | **2 bước** | Canh khung camera và chụp ảnh lên bìa |
| Màn chụp ảnh bìa (K3) | 1280px | Hiện tại | **1174.5 KB** | 17 | **4843 ms** | **3 bước** | Canh khung camera và chụp ảnh lên bìa |
| Màn chụp ảnh bìa (K3) | 1280px | Tối giản | **1488.1 KB** | 19 | **5132 ms** | **3 bước** | Canh khung camera và chụp ảnh lên bìa |
| Màn chụp ảnh bìa (K3) | 1280px | Lite (`?ban=lite`) | **269.6 KB** | 7 | **1911 ms** | **2 bước** | Canh khung camera và chụp ảnh lên bìa |
| Màn chụp ảnh bìa (K3) | 1080×1920 | Hiện tại | **1179.6 KB** | 17 | **4872 ms** | **3 bước** | Canh khung camera và chụp ảnh lên bìa |
| Màn chụp ảnh bìa (K3) | 1080×1920 | Tối giản | **1467.6 KB** | 19 | **5148 ms** | **3 bước** | Canh khung camera và chụp ảnh lên bìa |
| Màn chụp ảnh bìa (K3) | 1080×1920 | Lite (`?ban=lite`) | **277.7 KB** | 7 | **1907 ms** | **2 bước** | Canh khung camera và chụp ảnh lên bìa |
| Màn kết quả bìa + QR nhận tạp chí (K6) | 360px | Hiện tại | **1187.5 KB** | 22 | **5135 ms** | **2 bước** | Quét mã QR nhận ấn bản tạp chí về điện thoại |
| Màn kết quả bìa + QR nhận tạp chí (K6) | 360px | Tối giản | **1235.8 KB** | 24 | **5330 ms** | **1 bước** | Quét mã QR nhận ấn bản tạp chí về điện thoại |
| Màn kết quả bìa + QR nhận tạp chí (K6) | 360px | Lite (`?ban=lite`) | **285.8 KB** | 8 | **1909 ms** | **1 bước** | Quét mã QR nhận ấn bản tạp chí về điện thoại |
| Màn kết quả bìa + QR nhận tạp chí (K6) | 1280px | Hiện tại | **1191.6 KB** | 22 | **5086 ms** | **2 bước** | Quét mã QR nhận ấn bản tạp chí về điện thoại |
| Màn kết quả bìa + QR nhận tạp chí (K6) | 1280px | Tối giản | **1243.1 KB** | 24 | **5322 ms** | **1 bước** | Quét mã QR nhận ấn bản tạp chí về điện thoại |
| Màn kết quả bìa + QR nhận tạp chí (K6) | 1280px | Lite (`?ban=lite`) | **283.2 KB** | 8 | **1888 ms** | **1 bước** | Quét mã QR nhận ấn bản tạp chí về điện thoại |
| Màn kết quả bìa + QR nhận tạp chí (K6) | 1080×1920 | Hiện tại | **1218.8 KB** | 22 | **5091 ms** | **2 bước** | Quét mã QR nhận ấn bản tạp chí về điện thoại |
| Màn kết quả bìa + QR nhận tạp chí (K6) | 1080×1920 | Tối giản | **1257.1 KB** | 24 | **5325 ms** | **1 bước** | Quét mã QR nhận ấn bản tạp chí về điện thoại |
| Màn kết quả bìa + QR nhận tạp chí (K6) | 1080×1920 | Lite (`?ban=lite`) | **294.3 KB** | 8 | **1884 ms** | **1 bước** | Quét mã QR nhận ấn bản tạp chí về điện thoại |

## 2. Phân tích rút gọn bước thao tác & hiệu năng theo màn

### Màn chờ / chào Kiosk Yên Lam (`man-cho-chao`)
- **Ảnh ghép tổng hợp (1280 + 1080×1920 + 360)**: `so-sanh-man-cho-chao.jpg` · Riêng từng khổ: `so-sanh-man-cho-chao-360.jpg`, `so-sanh-man-cho-chao-1280.jpg`, `so-sanh-man-cho-chao-1080x1920.jpg`
- **Hiệu năng 3G trên màn Kiosk 1080×1920**: Hiện tại `3483.4 KB / 13353 ms` → Tối giản `3572.7 KB / 12140 ms` → Lite `443.9 KB / 2096 ms` (**giảm 87.3% dung lượng, nhanh hơn 84.3% trên 3G**).
- **Số bước việc chính (Bắt đầu hỏi Yên Lam hoặc chuyển sang chụp bìa)**: Hiện tại `2 bước` → Tối giản `1 bước` → Lite `1 bước`. Hiện tại (2 bước): nhiều chữ và 5 nút/chip đồng cấp khiến khách phải đọc dò trước khi bấm; ảnh nền KV + ảnh/video Lam nặng. Tối giản (1 bước): kính mờ Yên Lam, đúng 1 nút chính Hỏi Lam màu nhấn #0066B3, nhãn 1–2 chữ. Lite (1 bước): bỏ ảnh nền/video bước vào, vào thẳng trạng thái sẵn sàng 1 chạm.

### Màn nói / nhắn với Yên Lam (`man-noi-voi-lam`)
- **Ảnh ghép tổng hợp (1280 + 1080×1920 + 360)**: `so-sanh-man-noi-voi-lam.jpg` · Riêng từng khổ: `so-sanh-man-noi-voi-lam-360.jpg`, `so-sanh-man-noi-voi-lam-1280.jpg`, `so-sanh-man-noi-voi-lam-1080x1920.jpg`
- **Hiệu năng 3G trên màn Kiosk 1080×1920**: Hiện tại `3505.9 KB / 11880 ms` → Tối giản `3581.6 KB / 12100 ms` → Lite `442.4 KB / 2119 ms` (**giảm 87.4% dung lượng, nhanh hơn 82.2% trên 3G**).
- **Số bước việc chính (Đặt câu hỏi cho Yên Lam và nhận thông tin sự kiện)**: Hiện tại `3 bước` → Tối giản `2 bước` → Lite `2 bước`. Hiện tại (3 bước): mở khung -> đọc câu dẫn dài -> gõ/chọn câu hỏi giữa nhiều chữ phụ. Tối giản (2 bước): chạm Nhắn Lam -> chạm chip gợi ý hoặc Gửi trên tấm kính mờ gọn. Lite (2 bước): mở tức thì không hiệu ứng, ẩn chân trang phụ, chạy mượt khi mạng sảnh nghẽn.

### Màn chờ / chào Booth AGENTIC:ME (K1) (`booth-cho-chao`)
- **Ảnh ghép tổng hợp (1280 + 1080×1920 + 360)**: `so-sanh-booth-cho-chao.jpg` · Riêng từng khổ: `so-sanh-booth-cho-chao-360.jpg`, `so-sanh-booth-cho-chao-1280.jpg`, `so-sanh-booth-cho-chao-1080x1920.jpg`
- **Hiệu năng 3G trên màn Kiosk 1080×1920**: Hiện tại `1257.8 KB / 5119 ms` → Tối giản `1269.1 KB / 5324 ms` → Lite `275.1 KB / 1909 ms` (**giảm 78.1% dung lượng, nhanh hơn 62.7% trên 3G**).
- **Số bước việc chính (Chạm bắt đầu chụp bìa tạp chí cá nhân)**: Hiện tại `2 bước` → Tối giản `1 bước` → Lite `1 bước`. Hiện tại (2 bước): 3 bìa mẫu chồng dày trên màn nhỏ/ngang, nút cam đụng nhận diện sự kiện. Tối giản (1 bước): quạt bìa cân đối theo khung 360/1280/1080, đúng 1 nút chính Bắt đầu màu nhấn #0066B3. Lite (1 bước): thẻ bìa CSS siêu nhẹ (0 ảnh mẫu nặng), bấm Bắt đầu nhảy thẳng vào màn chụp K3.

### Form chọn Track chủ đề (AM-02d) (`form-track`)
- **Ảnh ghép tổng hợp (1280 + 1080×1920 + 360)**: `so-sanh-form-track.jpg` · Riêng từng khổ: `so-sanh-form-track-360.jpg`, `so-sanh-form-track-1280.jpg`, `so-sanh-form-track-1080x1920.jpg`
- **Hiệu năng 3G trên màn Kiosk 1080×1920**: Hiện tại `998.9 KB / 3587 ms` → Tối giản `1042.7 KB / 4031 ms` → Lite `277.9 KB / 1897 ms` (**giảm 72.2% dung lượng, nhanh hơn 47.1% trên 3G**).
- **Số bước việc chính (Chọn tối đa 3 Track quan tâm và xác nhận)**: Hiện tại `3 bước` → Tối giản `2 bước` → Lite `2 bước`. Hiện tại (3 bước): tải video Lam nền, 2 nút Bỏ qua / Xong thiếu phân cấp rõ ở màn ngang & di động. Tối giản (2 bước): lưới kính mờ Yên Lam vừa tầm mắt, đúng 1 nút chính Xong nổi bật + nút phụ Bỏ qua nhẹ. Lite (2 bước): bỏ video Lam nền, thẻ phẳng nhẹ phản hồi tức thì.

### Form chọn Diễn giả (AM-02e) (`form-dien-gia`)
- **Ảnh ghép tổng hợp (1280 + 1080×1920 + 360)**: `so-sanh-form-dien-gia.jpg` · Riêng từng khổ: `so-sanh-form-dien-gia-360.jpg`, `so-sanh-form-dien-gia-1280.jpg`, `so-sanh-form-dien-gia-1080x1920.jpg`
- **Hiệu năng 3G trên màn Kiosk 1080×1920**: Hiện tại `1238.4 KB / 5137 ms` → Tối giản `1244.4 KB / 5337 ms` → Lite `274.8 KB / 1944 ms` (**giảm 77.8% dung lượng, nhanh hơn 62.2% trên 3G**).
- **Số bước việc chính (Chọn diễn giả yêu thích cho ấn bản tạp chí)**: Hiện tại `3 bước` → Tối giản `2 bước` → Lite `1 bước`. Hiện tại (3 bước): tải 7 ảnh chân dung diễn giả + video Lam nền, dễ nghẽn trên 3G. Tối giản (2 bước): thẻ kính mờ đồng bộ, vùng chạm >=48px (>=72px ở 1080), 1 nút chính Xong. Lite (1 bước / tự gộp trong luồng nhanh; khi mở trực tiếp dùng huy hiệu chữ cái viết tắt thay 7 ảnh JPG).

### Màn chụp ảnh bìa (K3) (`man-chup`)
- **Ảnh ghép tổng hợp (1280 + 1080×1920 + 360)**: `so-sanh-man-chup.jpg` · Riêng từng khổ: `so-sanh-man-chup-360.jpg`, `so-sanh-man-chup-1280.jpg`, `so-sanh-man-chup-1080x1920.jpg`
- **Hiệu năng 3G trên màn Kiosk 1080×1920**: Hiện tại `1179.6 KB / 4872 ms` → Tối giản `1467.6 KB / 5148 ms` → Lite `277.7 KB / 1907 ms` (**giảm 76.5% dung lượng, nhanh hơn 60.9% trên 3G**).
- **Số bước việc chính (Canh khung camera và chụp ảnh lên bìa)**: Hiện tại `3 bước` → Tối giản `3 bước` → Lite `2 bước`. Hiện tại (3 bước): đi qua K1 -> AM-01/K2 -> đợi đếm ngược 3×1,3s cố định. Tối giản (3 bước): khung chụp bo kính gọn cho cả 360/1280/1080, chữ tối giản dễ hiểu trong 3 giây. Lite (2 bước): từ K1 nhảy thẳng sang K3, nhịp đếm nhanh 0,7s kèm 1 nút chính Chụp ngay để chốt tức thì.

### Màn kết quả bìa + QR nhận tạp chí (K6) (`man-ket-qua-qr`)
- **Ảnh ghép tổng hợp (1280 + 1080×1920 + 360)**: `so-sanh-man-ket-qua-qr.jpg` · Riêng từng khổ: `so-sanh-man-ket-qua-qr-360.jpg`, `so-sanh-man-ket-qua-qr-1280.jpg`, `so-sanh-man-ket-qua-qr-1080x1920.jpg`
- **Hiệu năng 3G trên màn Kiosk 1080×1920**: Hiện tại `1218.8 KB / 5091 ms` → Tối giản `1257.1 KB / 5325 ms` → Lite `294.3 KB / 1884 ms` (**giảm 75.9% dung lượng, nhanh hơn 63.0% trên 3G**).
- **Số bước việc chính (Quét mã QR nhận ấn bản tạp chí về điện thoại)**: Hiện tại `2 bước` → Tối giản `1 bước` → Lite `1 bước`. Hiện tại (2 bước): bìa, QR khách, QR IF Agent và 2 nút bố trí rời rạc ở khổ ngang/nhỏ. Tối giản (1 bước): gom thẻ kính mờ QR khách nổi bật cạnh bìa, đúng 1 nút chính Chụp tiếp, QR phụ tách xa. Lite (1 bước): ẩn QR phụ IF Agent, bỏ bộ dựng tạp chí nặng, tải mã QR tức thì.
