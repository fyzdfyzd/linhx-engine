# K6 · Bản đồ Chiêm Tinh Số → LINHX ENGINE (8/11/2026)

Nguồn: repo `fyzdfyzd/chiemtinhso` nhánh main (FastAPI, 18 module + core 6.522 dòng). Đếm dòng Python mỗi module (gồm test riêng của module).

**Kết luận:** CTS chuyển theo 3 lớp. Lớp 1 (tiền, đơn) chuyển trước vì đợt 1 đã có R1, R2 chạy bóng. Lớp 2 (khách, sản phẩm) sau khi A1–A5 đạt. Lớp 3 (động cơ chiêm tinh) KHÔNG chuyển: giữ thành máy nền riêng, engine gọi qua API. Lý do là calc-service AGPL phải mở mã, và để nó tách khỏi lõi cho sạch.

| Module CTS | Dòng | Về đâu trong engine | Lớp | Ghi chú |
|---|---|---|---|---|
| core/ (registry, flags, events, audit, auth, vietqr…) | 6.522 | Frappe thay registry/flags/auth/audit; `vietqr.py` → linhx_core.pay | 1 | Chỉ chép vietqr; phần còn lại Frappe có sẵn |
| pay (PAY-CORE + SePay) | 2.213 | linhx_core.pay | 1 | R1 adapter, R2 bóng |
| order (checkout, đơn, promo) | 9.419 | linhx_core.pay (đơn) + linhx_core.catalog (promo) | 1 | Module lớn nhất phần tiền, chia 3 đợt phiếu |
| subscription | 1.340 | linhx_core.catalog (quyền dùng có hạn) | 1 | |
| points | 1.475 | linhx_core.catalog (tín dụng) | 2 | Sổ bất biến, giữ logic |
| gift | 1.509 | linhx_core.shop | 2 | Quà 60 ngày, mua 1 tặng 1 |
| affiliate | 1.193 | linhx_core.partner | 2 | Engine chưa có partner ở đợt 1 |
| user | 12.438 | linhx_core.crm + id + consent | 2 | Lớn nhất; chuyển sau cùng như kế hoạch 5/11 |
| product | 2.940 | linhx_core.catalog | 2 | SKU yaml → DocType Gói/Giá |
| form | 2.770 | linhx_core.funnel (form chung) | 2 | |
| notify | 1.975 | linhx_core.chat | 2 | |
| track (Meta CAPI) | 1.174 | linhx_core.ads | 2 | |
| cms | 1.758 | linhx_core.content | 2 | |
| legal | 233 | linhx_core.legal | 2 | |
| ops (health, cảnh báo webhook) | 472 | linhx_core.ops | 1 | Gộp vào bàn điều hành |
| share (thẻ story/post) | 2.170 | giữ trong app sp_chiemtinh | 3 | Riêng sản phẩm |
| report (PDF từ ChartData, cổng 17 luật) | 4.501 | linhx_core.report dùng chung + mẫu riêng CTS | 2 | Template Báo cáo số 0 |
| calc + services/astro-calc | 7.836 | máy nền riêng, không vào Frappe | 3 | AGPL, mở mã trước 20/11 |
| hello, hello-plus | 778 | bỏ | – | Module mẫu |

**Cách chuyển (luật 5/11 giữ nguyên):** CTS đang có khách giữ FastAPI. Engine chạy bóng (R2) tới khi 100 đơn khớp liên tiếp, rồi Linh mới duyệt cắt pay + đơn. Phần khách chuyển cuối. Ước lượng cũ ~300 phiếu cho toàn bộ; lớp 1 khoảng 40–60 phiếu (em đoán, chỉnh sau R1).
