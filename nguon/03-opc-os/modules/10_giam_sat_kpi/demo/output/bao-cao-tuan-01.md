# Báo cáo tuần 01: Hệ điều hành OPC OS (3 OPC chạy chung)

**Tuần:** 01 (2026-10-19 → 2026-10-25) · **Giai đoạn:** SETUP / POC Mức 1–3 · **Cổng kế tiếp:** Đã kiểm chứng & Pháp lý nhận tiền thật (15/11/2026)

## 1. Tiến độ (10 Module & 3 OPC)
| Hạng mục | Hoàn thành | Tổng | % Done | Ghi chú |
|---|---|---|---|---|
| 10 Module cắm rút (`modules/01..10`) | 10 | 10 | 100% | Đầy đủ `MODULE.md`, `giao_keo.json`, CLI & Demo |
| Phương án A (`A_CODE`) vs B (`B_AGENT`) | 2 | 2 | 100% | Đã chạy 10 đơn giả + 3 ca lạ và đo số thật |
| 3 OPC cắm trên cùng OS (`opcs/opc001..003`) | 3 | 3 | 100% | Chiêm tinh, Prompt Ngân hàng, Hướng nghiệp HS |

## 2. Ba điều tốt
1. Luồng tiền-ra-report tất định 100% ở phần tiền (Module 03 & 07): chặn sạch đơn sai khoá `401`, chống ghi trùng `tx_id`, chặn đơn thiếu tiền và hết hạn.
2. Cắm thêm OPC 2 (Bộ công cụ ZIP+PDF Ngân hàng) và OPC 3 (Hồ sơ hướng nghiệp học sinh RIASEC 12–15 trang) trên cùng một lõi mà không phải viết lại luồng thanh toán hay sổ cái.
3. Cảnh báo đỏ `400.000.000 VNĐ` tính gộp cả 3 OPC trên tài khoản Vân Anh tự động kích hoạt chính xác.

## 3. Ba điều chưa tốt (và vì sao)
1. Chưa bật nhận tiền thật vì đang chờ hoàn tất đăng ký Hộ kinh doanh Vân Anh + MST (hạn 15/11/2026) và tạo file `.env`.
2. Phương án B (`B_AGENT`) tốn thời gian và chi phí token cao hơn Phương án A (`A_CODE`) ở luồng sinh report tiêu chuẩn, nên cần kiến trúc lai (A cho luồng chính, B cho CSKH/ca lạ).
3. 3 trang pháp lý ở Module 09 đang ở trạng thái bản nháp, cần luật sư rà trước khi mở cổng thanh toán thật.

## 4. Số đo tuần (đo thật từ chạy 3 OPC)
| Chỉ số | Giá trị đo được | Mục tiêu / Ngưỡng |
|---|---|---|
| Tổng đơn `paid` (3 OPC giả lập) | 18 đơn | 18 đơn hợp lệ / 30 đơn thử |
| Doanh thu luỹ kế gộp (TK Vân Anh) | 401,290,000 VNĐ | Báo đỏ tại 400.000.000 VNĐ (**ĐÃ BÁO ĐỎ**) |
| Tổng chi phí token AI | 940 VNĐ (0.0002% doanh thu) | < 10% doanh thu |
| Đơn kẹt > 5 phút chưa giao PDF | 0 đơn | 0 đơn |
| Giờ Founder / ngày (ước tính vận hành) | 0.75 giờ | ≤ 1,5 giờ |

## 5. Quyết định cần anh Linh (👤)
- [ ] Tạo file `D:\LINHX\PROTO\03_OPC_OS\.env` khi sẵn sàng nối SePay thật ở Mức 2.
- [ ] Duyệt 20 bản report đầu tiên trong hàng đợi `pending_linh_review_top20`.
- [ ] Chốt phương án kiến trúc **Lai (Hybrid A+B)**: dùng A (`A_CODE`) cho luồng thanh toán & sinh report chuẩn, dùng B (`B_AGENT`) cho CSKH đa kênh (Module 06) và xử lý ca lạ.

## 6. Thử nghiệm tuần tới
- Chạy thử khói (Smoke Test) ngân sách ≤ 1.000.000 VNĐ / 7 ngày cho OPC 1 (Chiêm Tinh Số) và OPC 2 (Bộ Prompt Ngân hàng) sau khi có MST Hộ kinh doanh.
