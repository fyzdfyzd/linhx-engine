model: mac-dinh
phieu: yl-tong-duyet-kiosk-17-11
may: may-3
trang_thai: xong
tep_doi: (khong)
drive: (khong)
phut: 38.22
token: vao=409617 ra=85363

Đã hoàn tất tổng duyệt Luồng 2 (chỉ chụp và ghi, commit + push sau từng mục 1→6 lên `linhx-engine` nhánh `soi-rc8-17-11`, commit cuối `41e83f1f`, chi tiết tại [BANG.md](file:///D:/linhx/wt-tong-duyet-dt/soi/tong-duyet/kiosk/BANG.md)):

- **Số ảnh**: **43 ảnh** (`01`→`43`, PNG viewport `1080×1920` DPR 1 cho kiosk/booth và `390×844` DPR 3 iPhone 13 cho trang khách quét QR) + `BANG.md` trong `soi/tong-duyet/kiosk/`.
- **Chuyển màn & bước không đi được**:
  - Kiosk đang mở tự do (`mo-tu-do`), không bị khoá. Từ `kiosk-lam` **có nút `Lên bìa` chuyển thẳng** mở SPA Booth ngay trên cùng trang/máy (kèm nút `Yên Lam` quay lại); Booth độc lập chạy ở `/yen-lam/csmo/agentic-me-v5/kiosk` (`/yen-lam/agentic-me-v5/kiosk` trả `404`; trang chủ `/yen-lam/` không còn chân `"Dành cho BTC"`).
  - **Nhập tên/nghề trên kiosk**: không có ô nhập trên màn Booth (thiết kế `LB-04` bỏ bàn phím trên kiosk; khách tự sửa `Tên trên bìa` ở màn `P1` điện thoại sau khi quét QR).
  - **Chia sẻ & lên tạp chí (màn khách)**: `P3` **có** `Tải tạp chí (PDF)`, `Tải ảnh bìa`, `Chia sẻ` (`navigator.share`/chép link), **không** có nút Facebook/Zalo riêng; nhánh lên tạp chí dẫn qua `/yen-lam/dong-hanh/cua-toi/bia?nhan_bia=<sid>` (Của tôi → Tạp chí).
  - **Để yên 60s**: `kiosk-lam` **tự về màn chờ `CHO`** trong ≤60s; Booth ở mốc 60s **vẫn ở `K2`** do cấu hình `ranhGiay=110s` + `k9DemGiay=10s` = **120s** mới tự về `K1` (đã xác nhận về `K1` ở 121s).
- **Thời gian tạo bìa**: Kiểm ảnh `3450 ms`; tổng chờ tạo bìa tới màn `K6` (bìa + QR): **`≤ 72352 ms`**.
- **Lỗi ghi nhận**: `HTTP 400 POST /yen-lam/csmo/api/event/lemedia` ở Booth; `HTTP 401 GET /api/yl/v1/may/toi` (chưa gắn cookie máy trạm); `HTTP 409 POST .../gan-dong-hanh/<sid>`; chữ mặc định *"The Khách mời CSMO Editio"* trên bìa bị cắt mất chữ *"n"* ở mép phải; trên `kiosk-lam` câu 3 Lam xưng *"Mình"* thay vì *"Lam"*.
