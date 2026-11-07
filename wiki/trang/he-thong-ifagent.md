---
tieu_de: Hệ thống nhóm ifAgent
loai: unit
trang_thai: cho-linh
cap_nhat: 2026-11-07
nguon: [nguon/2026-11-08-BANG-HE-THONG.json, https://claude.ai/artifact/Wyeq3HaoB6pfgoeC11P2qY]
sinh_tu_dong: scripts/wiki_tu_bang.py (sửa ở bảng rồi chạy lại, đừng sửa tay)
---
# Hệ thống nhóm ifAgent

3 dòng. Danh mục đủ: [[danh-muc-he-thong]].

## h31 · ifagent.net + demo.ifagent.net

Dạng: Hệ thống web · Trạng thái: Đang chạy · Quyết: chưa · Ưu tiên: 0 · Cấp: rieng · Claude đoán, chờ Linh

- **Là gì:** Site, showcase, form lead
- **Khách:** Bên tổ chức sự kiện, brand
- **Nỗi đau:** Sự kiện tương tác AI đắt và dựng lâu
- **Việc khách cần (JTBD):** Khi chuẩn bị sự kiện, tôi muốn chọn gói có sẵn và xem demo, để chốt nhanh trong ngân sách
- **Khách tin khi / mất khách khi:** Bên tổ chức hỏi ba câu: giá, thời gian dựng, case gần nhất. Trang phải trả lời trong 10 giây.
- **Mặt tiền:** ifagent.net + demo.ifagent.net
- **Kênh:** Web
- **Cách bán:** B2B
- **Module cần:** Nội dung / SEO; CRM / lead; Sự kiện / minigame
- **Đề xuất:** Lên ngay: đã có lead thật từ GEO, đang chạy.
- **Phản biện:** Đang chạy trên VM riêng; đừng di chuyển trước CSMO 18/11.
- **Gộp vào:** Khuôn demo dùng cho Unikon.
- **Đề bài:** Các BU khi đủ: https://claude.ai/artifact/4ZVAqsor1zbiKGnuRBVhom
- **Ghi chú:** Linh 6/11 11:20: ifagent.net gốc chuyển về Agent Force (showcase + lead), event xuống event.ifagent.net. Xem h08.
Claude 6/11 12:5x (thread BU): Event dùng event.ifagent.net: trang trả lời giá, thời gian dựng, case trong 10 giây; form về CRM chung. Quy hoạch, chưa làm.
- **Nguồn:** PRJ\IFAGENT

## h32 · Event platform quick deploy

Dạng: Hệ thống web · Trạng thái: Đang chạy · Quyết: chưa · Ưu tiên: 0 · Cấp: solution · Claude đoán, chờ Linh

- **Là gì:** Photobooth, nhân vật, game, theo dõi, gói preset giá rẻ
- **Khách:** Bên tổ chức sự kiện
- **Nỗi đau:** Mỗi sự kiện dựng lại từ đầu, không đo được hiệu quả
- **Việc khách cần (JTBD):** Khi có sự kiện, tôi muốn bật module sẵn và có số đo, để báo cáo cho khách
- **Khách tin khi / mất khách khi:** Khách sự kiện cần số đo để báo cáo sếp. Module đẹp không có số thì không ký lần hai.
- **Mặt tiền:** ifagent.net/event
- **Kênh:** Sự kiện; Web
- **Cách bán:** B2B
- **Module cần:** Sự kiện / minigame; Nhân vật ảo; Báo cáo tự động
- **Đề xuất:** Là module Sự kiện dùng chung cho mọi BU; chuyển sau CSMO.
- **Phản biện:** Code đang ở monorepo Next.js; lên Frappe chỉ phần quản trị + theo dõi.
- **Gộp vào:** Module Sự kiện / minigame.
- **Dùng chung:** Unikon chạy minigame chiến dịch; Sakedemy làm workshop tương tác; TUVA làm sự kiện NGO.
- **Đề bài:** Các BU khi đủ: https://claude.ai/artifact/4ZVAqsor1zbiKGnuRBVhom
- **Ghi chú:** Claude 6/11 12:5x (thread BU): Khi đủ: module sự kiện linhx_event dùng chung (CLB, lớp corp, Unikon, TUVA); preset là phễu, may đo là tiền; báo cáo số đo trong 24 giờ bằng report engine. Chuyển sau CSMO 18/11. Quy hoạch, chưa làm.
- **Nguồn:** PRJ\IFAGENT\apps\event

## h33 · Live character

Dạng: Quy trình nội bộ · Trạng thái: Có bản thử · Quyết: chưa · Ưu tiên: 0 · Cấp: solution · Claude đoán, chờ Linh

- **Là gì:** Nhân vật AI tương tác tại sự kiện
- **Khách:** Khách tại sự kiện, brand
- **Nỗi đau:** Gian hàng nhàm, người đi qua không dừng
- **Việc khách cần (JTBD):** Khi đi qua gian hàng, tôi muốn được trò chuyện với nhân vật vui, để nhớ thương hiệu
- **Khách tin khi / mất khách khi:** Người đi qua gian hàng dừng 7 giây. Nhân vật không gây cười hay ngạc nhiên trong 7 giây thì không ai đứng lại.
- **Mặt tiền:** Chọn nhân vật → nạp kịch bản → chạy
- **Kênh:** Live; Sự kiện
- **Module cần:** Nhân vật ảo; Chat bot / Zalo
- **Đề xuất:** Module Nhân vật ảo dùng chung với Own Media.
- **Phản biện:** Realtime khó chạy trên Frappe; giữ dịch vụ riêng.
- **Gộp vào:** Module Nhân vật ảo.
- **Dùng chung:** Đại sứ ảo cho mọi BU; nhân vật Luna của Chiêm Tinh Số chạy cùng lõi.
- **Đề bài:** Các BU khi đủ: https://claude.ai/artifact/4ZVAqsor1zbiKGnuRBVhom
- **Ghi chú:** Claude 6/11 12:5x (thread BU): Khi đủ: module nhân vật ảo, dịch vụ realtime riêng, dùng chung với nấc tác giả ảo của Expert OS. Quy hoạch, chưa làm.
- **Nguồn:** LIVE CHARACTER, LAB038

Liên quan: [[dich-cuoi]] [[kien-truc]] [[hop-nhat]]
