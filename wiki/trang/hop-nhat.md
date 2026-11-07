---
tieu_de: Lộ trình gộp các dự án vào LINHX ENGINE
loai: tong-quan
trang_thai: dang-chay
cap_nhat: 2026-11-08
nguon: [nguon/2026-11-08-BAN-DO-CTS-K6.md, nguon/2026-11-08-BANG-HE-THONG.json, features-dot1.json, features-dot1b.json]
---
# Lộ trình gộp các dự án vào LINHX ENGINE

**Một câu:** các dự án cứ chạy song song như hiện nay, không chuyển vội (chuyển vội là mất đơn); nhưng từ hôm nay mỗi dự án làm theo 5 luật "sẵn sàng gộp" dưới đây, để khi engine ổn định thì gộp từng lớp, chạy bóng trước, tắt bản cũ sau.

## Engine "ổn định" nghĩa là gì (cổng mở gộp)
1. Đợt 1 đạt: N1–N6, A1–A5, B1–B5 DAT theo `cong_kiem`, T1 và T2 xanh (một lead đi trọn, một đơn QR tự giao).
2. Hai bản cài `linhx` và `ifagent` chạy ≥ 7 ngày không lỗi chặn, sao lưu hằng ngày (N6).
3. Module tương ứng với phần định gộp đã có nghiệm thu riêng và đã DAT.
Chưa qua cổng thì chỉ được nối API hoặc chạy bóng, không chuyển dữ liệu thật.

## Năm luật cho dự án đang chạy song song
1. **Đặt tên theo engine.** Mỗi module ghi trong `module.yaml` (hoặc README) dòng `gop_vao: linhx_<module>` theo [[kien-truc]] (vd `linhx_pay`, `linhx_crm`, `linhx_consent`, `linhx_catalog`).
2. **Khách theo một khuôn.** Người, Tổ chức, Đồng ý theo mục đích; khoá gộp trùng là điện thoại, email, Zalo. Không thêm trường nghiệp vụ chỉ dự án mình hiểu mà không ghi vào wiki.
3. **Tiền theo một đường.** VietQR + webhook SePay, chống trùng `tx_id`, đơn có trạng thái `cho_tra → da_tra → da_giao`. Không viết cổng thanh toán thứ ba.
4. **Giữ API ở mép.** Nghiệp vụ nằm sau một API rõ (tạo đơn, webhook, giao hàng) để engine thay được bằng adapter (kiểu R1 của CTS).
5. **Ghi vào wiki.** Đổi module, schema, tên miền, trạng thái thì sửa trang dự án ở đây trong cùng lượt.

## Bản đồ gộp từng dự án
| Dự án / nguồn | Chạy ở đâu nay | Gộp vào | Cách và điều kiện | Feature |
|---|---|---|---|---|
| ENGINE 0.1 `linhx_worker` | repo này, VM linhx-engine-1 | lõi (đã là lõi) | giữ, mở rộng | N1, E2, W1 |
| PROTO 03 OPC OS | `D:\LINHX\PROTO` trên MSI | `linhx_crm`, `linhx_consent`, `linhx_catalog`, `linhx_pay`, sổ S1a-HKD | chép vào `nguon/` rồi chuyển, không viết mới | N2 → A1, B1–B5 |
| PROTO 01 Máy tạo nội dung | `D:\LINHX\PROTO` trên MSI | máy nền Write + module qc | gọi qua hàng việc, sau Chặng 0 | N2 |
| Chiêm Tinh Số lớp 1 (pay, order, subscription) | repo chiemtinhso, FastAPI, có khách | `linhx_pay`, `linhx_catalog` | adapter R1 → chạy bóng R2 → so lệch 0 trong 7 ngày → chuyển | R1, R2 |
| Chiêm Tinh Số lớp 2 (user, sản phẩm, gift, points, affiliate) | như trên | `linhx_id`, `linhx_crm`, shop, partner | sau khi A1–A5 DAT | đợt sau |
| Chiêm Tinh Số lớp 3 (động cơ chiêm tinh, calc-service AGPL) | máy riêng | **không gộp**, engine gọi API | mở mã calc-service trước 20/11 | - |
| Máy quét `mayquet` | máy cty `D:\LINHX\CRAWLER` | máy nền Crawler | không chuyển code; nối qua hàng việc LX Job, kết quả đẩy về engine | đợt sau |
| OPC Live | máy cty `OPC-LIVE-SRC`, nhánh main chiemtinhso | Bàn điều hành `/#/engine` | lấy dữ liệu thợ/token; tắt OPC Live khi E1, E2, W1 DAT | E1, E2, W1 |
| ifAgent demo + T1 Khám (LAB113) | demo.ifagent.net | template Trang BU + freebie | dựng lại trên khuôn C1, chạy IP trước, đổi DNS sau | C1–C3, D1–D2 |
| Báo cáo QR (LAB060, LAB062) | lab | template Báo cáo | trang bán báo cáo CSMO | Q1, B4 |
| PROTO 06 Course OS, 05 Agent Force OS, 07 Channel OS, 04 Ambassador OS | `D:\LINHX\PROTO` | dọc course, dọc agent, content + Own Media, dọc avatar | sau Chặng 0, theo [[kien-truc]] mục Tái dùng | đợt sau |

## Ai làm gì khi gộp
- Claude viết features + nghiệm thu cho từng lớp gộp, Linh duyệt, agy làm phiếu.
- Mỗi lần gộp xong: sửa trang dự án, thêm dòng [[quyet-dinh]], ghi LOG.

## Liên quan
[[dich-cuoi]] [[kien-truc]] [[lo-trinh]] [[du-an-chiem-tinh-so]] [[du-an-may-quet]] [[du-an-opc-live]] [[loi-engine]]
