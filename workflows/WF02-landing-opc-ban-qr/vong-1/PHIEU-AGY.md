# Phiếu cho agy · BrandAI hướng A (Linh chọn D2 9/11 12:23)

Sửa trang Q1 có sẵn trong `linhx-engine`, không dựng app mới. Đề xuất thành file `features-dot1c.json` (bản nháp `features-brandai.json` bên cạnh). Thread canh engine viết bộ nghiệm thu `tests/nghiem-thu/test_q2..q7.py` theo đúng tiêu chí dưới đây, Linh duyệt, rồi chạy `cong_kiem.py khoa`. Mỗi phiếu ≤ 40 phút; có `phu_thuoc` để chạy song song.

Đầu vào chung: `vong-1/d2/dung-A.html` và ảnh `d2/dung-A-{trang,mua,qr}-{360,390,1280}.png` (ảnh đích, **không** chép code; chữ nền vàng là giữ chỗ), `MOODBOARD.md`, `THAM-CHIEU.md`, `vong-1/prep/KHACH-SAN-PHAM.md` (rào cản và câu hỏi), skill `brand-ifagent` (chế độ sáng: nền `#F7F8FA`, chữ `#1A1D21`/`#656D76`, link `#0066CC`, nút `#0088FF` chữ `#0D1117`), luồng màn QR của Chiêm Tinh Số (`/mnt/project-files/01-man-qr-natal-360.png`).
Chưa thu tiền thật: giá thử 5.000đ trong catalog cho tới D4.

| id | Việc | Vùng | Tiêu chí (máy kiểm được) | Phụ thuộc |
|---|---|---|---|---|
| Q2 | Màn đầu hướng A: tiêu đề serif, giá lấy từ catalog hiện ngay dưới tiêu đề, nút "Xem báo cáo mẫu" cuộn tới khối mẫu, khối báo cáo mẫu là **ảnh trang thật** từ `front/mau/` (đường dẫn cấu hình, không viết cứng). Bỏ bộ ba thẻ. | `front/**` | 360 và 390: giá và nút nằm trong 800 px đầu; không có ba `.the` giống nhau liền nhau; không tràn ngang; front không viết cứng giá (giữ test Q1) | Q1 |
| Q3 | Biểu mẫu: email **bắt buộc**; 2 ô đồng ý không tích sẵn: (1) xử lý thông tin để làm báo cáo (bắt buộc), (2) nhận tin từ ifAgent (tuỳ chọn); gửi lên `tao_don` đúng giá trị khách tích; ghi LX Dong Y theo mục đích (A3). | `front/**`, `apps/linhx_core/linhx_core/pay/api_ban.py` | Không tích ô (1) thì không tạo đơn; mã nguồn front không có `dong_y...: true` viết cứng; tạo đơn ghi 1 hoặc 2 bản ghi LX Dong Y đúng mục đích; tối đa 2 ô nhập bắt buộc ngoài ô đồng ý | Q1, A3 |
| Q4 | Màn QR theo Chiêm Tinh Số: QR lớn, nút "Tải ảnh QR", dòng "Đang chờ chuyển khoản · Giữ đơn 30 phút", bảng số tiền / nội dung CK / người nhận (tên chủ TK từ cấu hình), mỗi dòng nút Sao chép; hỏi trạng thái đơn mỗi 3 giây (API mới `trang_thai_don(ma_don)`, khách chỉ xem đơn của mình qua mã khó đoán); khi `da_tra` tự chuyển sang trang báo cáo. | `front/**`, `apps/linhx_core/linhx_core/pay/api_ban.py` | `kiem_qr.py` trên ảnh QR: giải được, CRC đúng, số tiền = catalog, nội dung = mã đơn; đổi đơn sang `da_tra` thì trong ≤ 6 giây trang chuyển; có tên người nhận; từ vào trang tới QR ≤ 3 chạm | Q3, B3 |
| Q5 | Chân trang định danh + 2 trang chính sách: tên chủ, địa chỉ, MST, email, điện thoại đọc từ cấu hình bản cài; trang `#/bao-mat`, `#/hoan-tien` đọc nội dung Markdown từ cấu hình. Câu hoàn tiền mặc định: "Hoàn lại toàn bộ tiền nếu sau 24 giờ chưa nhận được báo cáo." (không viết "100%" vì Q6 quét từ cấm có "100%") | `front/**` | Chân trang có đủ 5 trường (thiếu trường nào thì test đỏ, không hiện chữ trống); hai link mở được; không viết cứng thông tin chủ trong front | Q1 |
| Q6 | Câu hỏi trước khi mua (6 câu trong KHACH-SAN-PHAM.md mục 2) + `<title>` và thẻ chia sẻ (og:title, og:description, og:image) riêng cho BrandAI. | `front/**` | Có ≥ 5 câu hỏi dạng `<details>`; `<title>` khác "LINHX Engine"; có og:image; quét từ cấm (giải pháp số 1, top ChatGPT, cam kết lên đầu, 100%) = 0 | Q2 |
| Q7 | Tên miền brandai.ifagent.net trỏ vào trang bán của bản cài ifagent (Caddy), HTTPS. | `deploy/**` | `curl -I https://brandai.ifagent.net` trả 200 và trang chứa `data-tra-qr`; trang quản trị không lộ ở tên miền này | Q2 (và Linh trỏ DNS) |

## Thứ tự chạy song song
Q2 và Q5 chạy ngay song song. Q3 sau A3 (đã đạt). Q4 sau Q3. Q6 sau Q2. Q7 cần Linh trỏ DNS (cổng người).

## Claude chấm sau khi đủ Q2–Q6 (vòng 1, D4)
1. Máy: `do/kiem_qr.py`, chụp 360/390/768/1280 + `do.json` (tràn ngang, sát mép, chạm), axe 0 lỗi nặng, Lighthouse mobile.
2. Đi 3 đường: suôn, hoài nghi (bỏ qua hết), phá (bỏ ô đồng ý, email sai, quay lại sau khi trả).
3. Chấm mù 3 người (agy phiên mới, Gemini, ChatGPT qua Chrome máy cty): đọc 5 giây "bán gì, giá bao nhiêu, bấm đâu"; đặt cạnh 3 bản vàng (`../DR/DE-2.md`); ≤ 1/3 đoán "AI làm".
4. Ghi lỗi quy trình vào `../BAI-HOC.md`, sửa skill `thiet-ke` nhánh landing.

## Ghi chú cho thread canh khi viết test
- Q6 quét từ cấm trên **chữ hiện ra** (innerText), không quét mã nguồn: CSS có `width:100%` sẽ làm test đỏ oan.
- Bản dựng `d2/dung-A.html` đã đo: không tràn ngang ở 360/390/1280; giá và hai nút nằm trong 590 px đầu ở 360 (tiêu chí Q2 là 800 px); `kiem_thiet_ke.py --pha d1` và `d2` đều DAT.
