# 20 payload mẫu Chiêm Tinh Số (đã ẩn danh) cho R1, R2

Dựng theo code CTS ở commit 73a10ddb (repo chiemtinhso): `POST /v1/checkout` (modules/order/api/router.py, create_checkout_order,
serialize_public_order, core/vietqr.build_qr_payload) và `POST /v1/pay/sepay/webhook` (handle_sepay_webhook,
apply_webhook_payment_to_order). Tên, email, ngày sinh, mã đơn, số tài khoản đều giả. Thợ không sửa thư mục này.

- `checkout-XX.json`: `vao` là thân request; `ra.http`, `ra.body` là CTS trả. Đơn mới: so dạng (khoá, kiểu), giá lấy từ danh mục.
- `webhook-XX.json`: `truoc.don` là đơn đang có, `truoc.tx_da_co` là tx_id đã ghi; `vao` là thân webhook SePay;
  `ra` là CTS trả; `sau` là trạng thái đơn sau xử lý.
- `danh-muc.json`: danh mục giá dùng chung (lấy từ config/products/chiem-tinh.yaml của CTS).
