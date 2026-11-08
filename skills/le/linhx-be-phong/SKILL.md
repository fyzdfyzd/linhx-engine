---
name: linhx-be-phong
description: Lập kế hoạch launch một OPC mới trên bệ phóng chung của LINHX (15 khâu, module dùng lại từ các lab) và so KPI giữa các OPC. Dùng khi Linh nói "launch OPC mới", "bệ phóng", "so các OPC".
---

# Bệ phóng nhiều OPC (v0.1)

Khung 15 khâu học cách làm của 100 Tasks (Setup, Launch, Scale) nhưng viết lại cho công ty một người chạy bằng agent. Bỏ hết việc tuyển người, nhà xưởng, chuỗi cung ứng. Nội dung gốc của 100 Tasks không chép vào đây.

## Khi Linh muốn launch một OPC
1. Tạo `opc/<ten>.json` theo mẫu `opc-mau/`: `da_xong` (khâu đã làm), `dung_module` (khâu lấy lại từ bệ), `kpi`.
2. Chạy `python bephong.py ke-hoach opc/<ten>.json`. Kết quả: % sẵn sàng, việc AI tự làm, cổng chờ Linh.
3. Việc mức A3/A2: giao agent (agy hoặc Claude) theo lab nguồn ghi ở `be-phong.json`. Việc A1/A0 và các CỔNG LINH: gom vào một phiếu duyệt mỗi tuần, không hỏi lẻ.
4. Mỗi tuần: cập nhật `kpi` rồi chạy `python bephong.py bang opc/` để xem bản đồ nhiệt. OPC đỏ cả 3 chỉ số qua 2 tuần thì đưa ra cổng K15.

## Luật
- Không agent nào tự tiêu tiền, tự ký, tự mở tài khoản thanh toán, tự trả lời khiếu nại tiền. Các việc đó là cổng người.
- Mọi OPC dùng chung một kho KPI (K10) và một sổ cách làm tốt (K14). Cái gì OPC học được phải ghi về sổ chung.
- Kênh người ảo phải ghi rõ là AI theo luật nền tảng.
- Số trong `opc-mau/` là số giả để chạy thử, không phải số thật.
