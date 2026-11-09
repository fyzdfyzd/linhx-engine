# Danh mục workforce trao tay (bản 0.1, 9/11, chờ Linh chọn thứ tự)

Mỗi workforce = khuôn `af.py moi` + skill có sẵn trong kho `skills/` + 3–5 workflow + bộ thử từ việc thật. "Sẵn" nghĩa là đã có skill và đơn vị dùng thật trong LINHX. Thời gian dựng tính theo phiếu agy (≤ 40 phút một phiếu), không tính ngày.

| # | Workforce | Đơn vị dùng | Workflow đầu (đã có skill) | Thước đo 14 ngày | Sẵn tới đâu |
|---|---|---|---|---|---|
| 1 | **Nụ Event**: trợ lý bán hàng sự kiện | ifAgent Event | tra hồ sơ, trả lời lead, proposal, báo cáo sau sự kiện (`brand-ifagent`, `proposal-studio`, `bao-cao`) | ≥ 20 việc, ≥ 65% xong, 0 số bịa | **Mẫu đã dựng** (`mau/ifagent-event`); chờ Linh 4 câu D0 + rút thời gian trả lời |
| 2 | **Tòa soạn sáng**: chọn tin, viết, duyệt | CafeBiz (Vân Anh) | 20 tin 7h, chọn 10, viết ra Docs, sổ học góp ý (`cafebiz-radar`, `linhx-viet-bai`, `linhx-bien-tap`) | tỉ lệ bài được dùng, số góp ý lặp lại giảm | Bot Telegram LAB090 đang chạy; thiếu danh sách người được ra lệnh |
| 3 | **Thư ký khách VIP** | xưởng Thơm (chị Quỳnh Hương) | trả mail trong ngày, lên kế hoạch + hẹn giờ, soạn đề xuất artwork (`linhx-thu-ky`, `linhx-viet-giong-viet`, `thiet-ke`) | 100% mail được trả lời kế hoạch trong ngày; 0 bài gửi đi chưa rà 3 vòng | Luật đã có trong memory; LAB083 Nụ cũ dừng từ 1/11 |
| 4 | **Shop báo cáo AI** | Chiêm Tinh Số, LINHX ENGINE | nhận đơn, chạy báo cáo, kiểm chất lượng, gửi link (`linhx-report`, `research-write`) | số đơn xong đúng hạn, tỉ lệ trả lại | Engine đã chạy thợ agy; nối bảng việc vào `af.py` |
| 5 | **Phòng giáo vụ khoá học** | EDU / Sakédemy | soạn giáo trình, slide bài, câu hỏi kiểm tra, trả lời học viên (`linhx-course`, `vong-lap-slide`, `bm1_*`) | số bài giảng duyệt lần đầu | Skill đủ; chờ đề EDU Tech + AstraZeneca (thư mục EDU chưa thấy trên máy cty) |
| 6 | **Xưởng video đầu bếp** | Chef Hùng (Ichef) | phiếu món → kịch bản → dựng → kiểm (`linhx-phim-code`, `sd-*`) | số video xuất bản/tuần | WF21 bước 0 xong; chờ phiếu món + quyền Hùng |
| 7 | **Radar tài trợ + viết hồ sơ** | TUVA | quét tài trợ, chấm hợp, viết hồ sơ (`linhx-radar`, `research-loop`) | số hồ sơ nộp, số hạn không bỏ lỡ | LAB013/018 đã có; cần người TUVA làm người duyệt |
| 8 | **Thương hiệu cá nhân** | LinhX (Expert OS) | chấm Linh trên AI, viết bài theo giọng, lịch đăng (`linhx-brand-check`, `linhx-viet-giong-viet`, `linhx-kenh-ao`) | số bài đăng đúng lịch, điểm có mặt trên AI | WF18 D2 đã duyệt; chờ khoá OpenRouter |
| 9 | **Tình báo bán lẻ hằng tháng** | BTMH | báo cáo bán lẻ tháng, đối thủ, gợi ý (`btmh-monthly-retail-intelligence`, `brand-btmh`) | báo cáo đúng hạn, số có nguồn 100% | Skill có; chưa có người nhận phía BTMH |
| 10 | **Bán Agent Force** | Agent Force (ifagent.net) | onboard khách 20 phút, dựng workforce từ danh mục này, báo cáo 14 ngày (`linhx-be-phong`, `linhx-4d`) | số khách chạy đủ 14 ngày | Dùng chính lõi này; làm sau khi #1 đạt D14 |

## Thứ tự đề xuất
1 (đang làm) → 2 (bot đã chạy, chỉ cần bọc vào lõi để có bảng việc + học) → 4 (đã có thợ) → 3 → 5. Còn lại làm khi có người duyệt ở đơn vị đó.

## Muốn vào danh mục phải có
- Một người thật chịu trách nhiệm và duyệt.
- Ít nhất 3 việc lặp lại mỗi tuần, có "xong" đo được.
- Ít nhất 10 ca thật để làm bộ thử trước khi mở nhóm.
