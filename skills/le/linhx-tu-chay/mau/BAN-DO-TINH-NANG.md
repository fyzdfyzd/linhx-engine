# Bản đồ tính năng: <tên sản phẩm>

Gọi mọi thứ theo cách người dùng gọi. Đề, góp ý, báo lỗi đều dùng mã TN. Phiếu đổi giao diện thì sửa dòng tương ứng.

| Mã | Tên người dùng gọi | Ở đâu (URL, màn) | File chính | Test e2e | Ảnh mới nhất |
|---|---|---|---|---|---|
| TN-01 | Trang chủ | `/` | `<đường dẫn>` | `tests/e2e/test_trang_chu.py` | `bang-chung/<ID>/360.png` |
| TN-02 | Nút "Mua" ở thẻ gói | `/san-pham`, thẻ gói | `<đường dẫn>` | `<test>` | `<ảnh>` |

## Luồng chính
| Mã | Luồng | Các bước (theo mã TN) |
|---|---|---|
| LU-01 | Mua báo cáo | TN-01 → TN-02 → TN-03 nhập ngày sinh → TN-04 QR → TN-05 nhận báo cáo |
