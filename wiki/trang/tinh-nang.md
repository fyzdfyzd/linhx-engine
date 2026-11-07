---
tieu_de: Tính năng engine theo đợt
loai: danh-muc
trang_thai: dang-chay
cap_nhat: (theo git)
nguon: [features-dot1.json, features-dot1b.json]
sinh_tu_dong: scripts/wiki_tu_features.py (sửa features rồi chạy lại, đừng sửa tay)
---
# Tính năng engine theo đợt

Mỗi đợt một file `features-dotN.json` ở gốc repo. Có file `.khoa` là đã khoá, ý mới sang đợt sau. Cách viết đề: [[danh-muc-de-bai]], [[he-du-an-tu-chay]].

## features-dot1.json · đã khoá · đạt 0/26

**Đích:** Một lead đi trọn đường và một đơn báo cáo trả QR tự giao, trên hai bản cài linhx và ifagent

Trạng thái: Linh CHỐT 8/11 05:35 VN; chưa khoá, chờ tests/nghiem-thu

| Mã | Cần trước | Mô tả | Đạt |
|---|---|---|---|
| N1 | - | Repo linhx-engine có code ENGINE 0.1 (apps/linhx_worker, front, runner, deploy); CI chạy tests/nghiem-thu | - |
| N2 | N1 | Chép PROTO 03 OPC OS và 01 Máy nội dung từ D:\LINHX\PROTO vào nguon/ (chỉ đọc, không chạy) | - |
| N3 | N1 | Khung app Frappe linhx_core: cài được trên bench, mỗi module bật/tắt bằng cờ trong LX Cau Hinh | - |
| N4 | N3 | Lệnh `linhx tao-site <ten> --cau-hinh <file>`: tạo bản cài mới, cài linhx_core + linhx_worker, bật module theo cấu hình | - |
| N5 | N4 | Tạo hai bản cài linhx và ifagent trên VM linhx-engine-1, mỗi bản một DB | - |
| N6 | N5 | Sao lưu DB hằng ngày mỗi bản cài + nhật ký truy cập dữ liệu khách | - |
| A1 | N2, N3 | DocType LX Don Vi, LX To Chuc, LX Nguoi; khoá gộp trùng theo điện thoại, email, Zalo; chuyển từ PROTO 03 m04 | - |
| A2 | A1 | LX Quan He, LX Co Hoi; giao người phụ trách, báo việc chờ | - |
| A3 | A1 | LX Dong Y theo mục đích (liên hệ, chuyển chéo, marketing), rút đồng ý, nhật ký | - |
| A4 | A1 | Quyền theo Đơn vị: người của đơn vị chỉ thấy dữ liệu đơn vị mình | - |
| A5 | A2, A3, N5 | API chuyển lead giữa hai bản cài có ghi công (nguồn, đơn vị, thời điểm) | - |
| B1 | N2, N3 | LX Goi, LX Gia, LX Quyen Dung; chuyển từ PROTO 03 m02 | - |
| B2 | B1 | LX Don + mã VietQR theo đơn; chuyển từ PROTO 03 m03 | - |
| B3 | B2 | Webhook SePay: đối soát, chống trùng tx_id, chuyển đơn sang da_tra | - |
| B4 | B3 | Đơn báo cáo 'AI nói gì' đã trả tự tạo LX Job, giao link báo cáo, bỏ duyệt tay | - |
| B5 | B3 | Sổ S1a-HKD và báo đỏ khi doanh thu chạm ngưỡng; chuyển từ PROTO 03 m07 | - |
| C1 | N1 | Khuôn Next.js Trang BU từ demo ifAgent, đọc nội dung từ API bản cài | - |
| C2 | C1, A3 | Form Trang BU ghi Người + Cơ hội + Đồng ý vào bản cài | - |
| C3 | C2 | ifagent.net bản mới trên khuôn, chạy trên IP VM (chưa đổi DNS) | - |
| D1 | C1 | Tool T1 Khám (LAB113) thành freebie trên Trang BU | - |
| D2 | D1, A3 | Kết quả đầy đủ T1 đổi lấy email/Zalo, ghi Người + Đồng ý + tầng phễu | - |
| D3 | A2, B3 | Bảng phễu 6 tầng bản 1 (biết, mồi, liên hệ, cơ hội/đơn, khách, quay lại) đếm từ crm + pay | - |
| E1 | A2, B2 | Bàn /#/engine thêm: việc chờ anh, lead mới, đơn mới | - |
| E2 | N3 | Token và phút mỗi LX Job hiện trên bàn | - |
| T1 | C3, D2, A5, E1 | Playwright: một lead đi trọn (T1 → hồ sơ + đồng ý → cơ hội → giao người → thấy trên bàn), 390 và 1280 | - |
| T2 | B4 | Playwright: một đơn báo cáo trả QR (webhook giả lập SePay) rồi tự giao | - |

## features-dot1b.json · chưa khoá · đạt 0/5

**Đích:** Bổ sung đợt 1: bảng thợ, trang bán báo cáo QR cho CSMO, Trang BU thứ hai chỉ bằng cấu hình, CTS sẵn sàng chuyển pay + đơn sang engine (chế độ bóng)

Trạng thái: Linh duyệt hướng 8/11; chờ nghiệm thu rồi khoá

| Mã | Cần trước | Mô tả | Đạt |
|---|---|---|---|
| W1 | E2 | Bảng thợ trên /#/engine: phiếu đang chạy, phút, token, tỉ lệ phiếu sửa theo tuần, số lần chạm trần | - |
| Q1 | B2 | Trang bán báo cáo 'AI nói gì về thương hiệu' trên template đã có của 0.1: nhập thương hiệu, chọn gói, nút trả QR gọi B2 | - |
| C4 | C3 | Trang BU thứ hai (unikon) dựng chỉ bằng file cấu hình trên khuôn C1, không sửa code khuôn | - |
| R1 | B3 | Adapter CTS: endpoint engine nhận đúng payload tạo đơn và webhook SePay hiện nay của Chiêm Tinh Số, trả cùng dạng | - |
| R2 | R1 | Chế độ bóng: bản sao webhook SePay của CTS đẩy sang engine, engine ghi đơn bóng và báo lệch; cờ tắt mặc định, không giao hàng | - |

Liên quan: [[loi-engine]] [[lo-trinh]] [[hop-nhat]]
