# WF02 vòng 1 · Đề bài: trang bán báo cáo "AI nói gì về thương hiệu" (QR SePay)

Linh chốt đề 9/11. Theo skill `thiet-ke` nhánh landing, kèm khung `web-thiet-ke` (11 mục) và 4 mục thêm của NGHIEN-CUU. Chỗ có dấu ? là chờ Linh.

## Phát hiện trước khi viết đề
Trang này **đã có bản chạy được** trong LINHX ENGINE: feature Q1 (đạt 8/11), file `linhx-engine/front/index.html` hàm `trangChu()`, API `linhx_core.pay.api_ban` (đạt B2: VietQR, B3: webhook SePay). Feature B4 (tự giao báo cáo) và T2 (Playwright đơn trả QR) chưa đạt, thợ engine đang làm.
**Vì vậy vòng 1 không dựng lại từ đầu.** Vòng 1 là "sửa trang có sẵn" theo đúng luật của nhánh landing: gọi tên 3 lỗi nặng nhất (`CHAN-DOAN.md`), tìm tham chiếu nhắm vào 3 lỗi đó, rồi giao agy sửa qua một feature mới của engine. Claude không sửa code của agy.

## 11 mục
1. **Loại**: landing một trang có biểu mẫu và màn QR, chạy trên engine (front tĩnh + API Frappe).
2. **Brand**: ? Mặc định đề xuất **ifAgent** (brand-check là dịch vụ cho khách IF Agent; T1 Khám đã làm mồi trên Trang BU). Phương án khác: LinhX (Personal Brand).
3. **Mục tiêu**: chủ thương hiệu nhỏ quét QR trả tiền để nhận báo cáo "AI nói gì về thương hiệu của tôi".
4. **Người xem**: chủ doanh nghiệp nhỏ, marketer; đến từ T1 Khám (freebie), bài LinkedIn/Facebook của Linh, Zalo. Mặc định xem trên điện thoại 360–390 px.
5. **Thông điệp chính**: "AI nói gì về thương hiệu của bạn?". Ba lý do tin: hỏi thật 3–4 trợ lý AI và lưu nguyên văn; code tính điểm, AI chỉ gán nhãn (chuẩn ABC); có người kiểm nhãn trước khi gửi.
6. **Bằng chứng thật**: một báo cáo mẫu đã ẩn danh (lấy từ lượt chạy brand-check có sẵn, không dùng thương hiệu của Linh theo luật CSMO), ảnh chụp trang báo cáo thật. ? cần Linh chọn báo cáo mẫu.
7. **Khối**: hero (lời hứa, giá, nút) · báo cáo mẫu (ảnh thật) · cách làm 3 bước · giá và gói · câu hỏi trước khi mua (bao lâu nhận, AI nào, nếu AI không nhắc tên thì sao, hoàn tiền) · biểu mẫu + QR · chân trang định danh.
8. **Cảm giác**: rõ ràng, có số đo, đáng tin (không hào nhoáng). Mẫu: xem `../DR/DE-2.md`.
9. **Cấm**: bộ ba thẻ giống nhau, tím–xanh gradient, eyebrow in hoa, hứa "lên top ChatGPT", số không đếm được (luật brand-check: không hiện con số nào không đếm được).
10. **Đầu ra**: sửa `front/` của engine qua feature mới (đề sẵn ở `PHIEU-AGY.md` khi qua D2); HTML một file để Linh xem.
11. **Hạn và người duyệt**: Linh duyệt D2 (hướng) và D4 (bản cuối).

## Bốn mục thêm
- **Giá**: **499.000đ** (Linh chọn 9/11 12:17). Giá nằm trong catalog `LX Goi` của bản cài, không viết cứng trong front (test Q1 đã chặn việc viết cứng).
- **Thông tin phải thu**: tên thương hiệu (bắt buộc), email (**bắt buộc**, vì đây là kênh giao báo cáo; hiện đang để tuỳ chọn), 2 ô đồng ý tách riêng (xử lý dữ liệu để làm báo cáo: bắt buộc; nhận tin: tuỳ chọn), không tích sẵn.
- **Cách giao**: sau khi trả, trang tự chuyển sang trạng thái "đã nhận tiền" và hiện link báo cáo; gửi email link (B4).
- **Hoàn trả**: ? đề xuất: hoàn 100% nếu sau 24 giờ chưa giao được báo cáo; không hoàn khi báo cáo đã giao (sản phẩm số giao ngay). Cần Linh duyệt câu chữ.
- **Tài khoản nhận**: ? Cấu hình trong `site_config` của bản cài (`vietqr_bin`, `vietqr_so_tk`, `vietqr_ten_tk`), không nằm trong code.

## Máy đo vòng 1 (đạt mới qua D4)
1. Chạm từ vào trang tới thấy QR ≤ 3. Hiện tại: 2 (đạt).
2. `kiem_qr.py` trên ảnh QR thật của bản cài: giải được, CRC đúng, số tiền = giá catalog, tài khoản = cấu hình, nội dung CK = mã đơn.
3. Webhook: khoá sai → 401; gửi trùng → giao 1 lần; trả thiếu → không giao; trả 200 kèm `{"success": true}`.
4. Pháp chế: 0 đỏ (ô đồng ý không tích sẵn và không gửi cứng; chân trang có tên chủ, địa chỉ, mã số thuế, liên hệ; có link Bảo mật, Hoàn tiền).
5. Chụp 360/390/1280, không tràn ngang, axe 0 lỗi nặng.
6. Đọc 5 giây: người chấm mù trả lời được "bán gì, giá bao nhiêu, bấm đâu".
7. Chấm mù 3 người: ≤ 1/3 đoán "AI làm"; đặt cạnh 3 bản vàng không khối nào kém hơn.
Chưa thu tiền thật trước D4: giá thử 5.000đ và webhook giả.
