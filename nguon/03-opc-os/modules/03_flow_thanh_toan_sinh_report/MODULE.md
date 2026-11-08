# Module 03: Flow Thanh toán → Sinh Report (`03_flow_thanh_toan_sinh_report`)

## 1. Mục tiêu & Luật An toàn Cố định
Module 03 là cổng thu tiền và điều phối đơn hàng của toàn bộ OPC OS, kế thừa trực tiếp từ `LAB060` (`vendor/LAB060/src/server.py`).

- **Người nghiệm thu**: Chị Giữ Két (CFO) & Chị Đóng Gói (CPO)
- **LUẬT AN TOÀN SẮT (`03_OPC_OS.md` & `QUY-CHUAN-OPC.md` 6.2, 7.2)**:
  - Phần tiền (tạo đơn, kiểm tra chữ ký `Authorization: Apikey`, đối soát số tiền, chống trùng `tx_id`, kiểm tra hết hạn, phát sự kiện `don.da_tra`) **LUÔN CHẠY BẰNG CODE CỐ ĐỊNH TẤT ĐỊNH 100%** ở cả Phương án A (`A_CODE`) lẫn Phương án B (`B_AGENT`).
  - Phương án B tuyệt đối không để Agent tự quyết phần tiền; Agent chỉ được đọc sự kiện `don.da_tra` sau khi Module 03 đã xác thực.
  - Khoá SePay và số tài khoản Vân Anh đọc từ `D:\LINHX\PROTO\03_OPC_OS\.env` qua `core/env_loader.py`, không ghi vào code hay log.

## 2. Sáu Module con
1. **`3.1_tao_don`**: Nhận thông tin khách (đã kiểm đồng ý dữ liệu), cấp mã đơn theo tiền tố của từng OPC (`CT00001`, `BK00001`, `HN00001`) để đối soát chung trên tài khoản Vân Anh.
2. **`3.2_vietqr_generator`**: Sinh URL ảnh QR VietQR tự điền sẵn số tiền và nội dung chuyển khoản chứa mã đơn.
3. **`3.3_webhook_sepay_verify`**: Xác thực header `Authorization: Apikey <key>` (trả `401` nếu sai khoá), kiểm tra `transferType == "in"`.
4. **`3.4_doi_soat_chong_trung`**:
   - Chống trùng giao dịch (`tx_id` đã xử lý → bỏ qua idempotent, trả `200`, không thu lặp).
   - Chặn đơn hết hạn (`status == "expired"` hoặc quá `order_expiry_seconds` → từ chối kích hoạt, báo ca cần xử lý).
   - Chặn chuyển thiếu tiền (`transferAmount < amount` → giữ trạng thái `underpaid`, báo lỗi thanh toán).
5. **`3.5_phat_su_kien_va_giao_pdf`**:
   - Khi khớp lệnh: cập nhật `status = "paid"`, phát sự kiện `don.da_tra`.
   - Lắng nghe `report.xong` từ Module 01, gắn `pdf_path` và dựng HTML trang đơn `/o/<token>` có **khung xem PDF trực tiếp trên trang** (`<embed type="application/pdf">` + nút tải PDF).
6. **`3.6_hoan_tien_pending_founder`**: Tiếp nhận yêu cầu hoàn tiền, tạo phiếu `pending_founder_approval` (Agent không được tự hoàn tiền).

## 3. Giao kèo Sự kiện
- **Phát ra**: `don.tao_moi`, `don.da_tra`, `don.loi_thanh_toan`, `don.het_han`, `don.yeu_cau_hoan_tien`
- **Lắng nghe**: `report.xong`

## 4. Chạy độc lập
```powershell
python modules/03_flow_thanh_toan_sinh_report/module.py --demo
```
