---
tieu_de: Hệ thống nhóm Nền dùng chung
loai: unit
trang_thai: cho-linh
cap_nhat: 2026-11-07
nguon: [nguon/2026-11-08-BANG-HE-THONG.json, https://claude.ai/artifact/Wyeq3HaoB6pfgoeC11P2qY]
sinh_tu_dong: scripts/wiki_tu_bang.py (sửa ở bảng rồi chạy lại, đừng sửa tay)
---
# Hệ thống nhóm Nền dùng chung

7 dòng. Danh mục đủ: [[danh-muc-he-thong]].

## h20 · Kit thu tiền QR + hoá đơn

Dạng: Quy trình nội bộ · Trạng thái: Đang chạy · Quyết: chưa · Ưu tiên: 0 · Cấp: loi · Claude đoán, chờ Linh

- **Là gì:** SePay, VietQR, đơn, hoá đơn cho mọi bên
- **Khách:** Khách mua mọi site + kế toán
- **Nỗi đau:** Chuyển khoản tay phải chờ xác nhận, kế toán đối soát mệt
- **Việc khách cần (JTBD):** Khi trả tiền, tôi muốn quét QR là xong và nhận hàng ngay, để khỏi chờ
- **Khách tin khi / mất khách khi:** Khách chỉ quan tâm: quét xong có hàng ngay không. Một đơn trả tiền không ra hàng (CTS 4/11) giết niềm tin hơn mọi tính năng.
- **Mặt tiền:** Tạo đơn → hiện QR → SePay báo → giao hàng
- **Module cần:** Thanh toán QR
- **Đề xuất:** Lên ngay thành app linhx_vn: mọi site bán đều cần.
- **Phản biện:** Mỗi BU một pháp nhân, một tài khoản SePay; module phải nhiều tài khoản.
- **Gộp vào:** Module Thanh toán QR.
- **Dùng chung:** Mỗi pháp nhân một tài khoản SePay, dùng chung một module.
- **Nguồn:** LAB060, chiemtinhso

## h21 · Generator

Dạng: Quy trình nội bộ · Trạng thái: Có bản thử · Quyết: chưa · Ưu tiên: 0 · Cấp: workflow · Claude đoán, chờ Linh

- **Là gì:** Brief → demo tương tác nhanh
- **Khách:** Sale BU
- **Nỗi đau:** Làm demo cho khách mất nhiều ngày, mất khách
- **Việc khách cần (JTBD):** Khi khách hỏi, tôi muốn có demo trong vài giờ, để chốt khi khách còn nóng
- **Khách tin khi / mất khách khi:** Khách không cần demo nhanh. Họ cần demo giống vấn đề của họ. Demo chung chung nhanh vẫn thua.
- **Mặt tiền:** Dán brief → chọn khuôn → sinh demo → gửi khách
- **Module cần:** Sinh nội dung AI; Sự kiện / minigame
- **Đề xuất:** Thành khuôn tạo site demo từ brief trên engine.
- **Phản biện:** Đừng sinh code mỗi lần; sinh cấu hình trên khuôn có sẵn.
- **Gộp vào:** Gộp với Campaign generator Unikon.
- **Dùng chung:** Unikon làm proposal, ifAgent làm demo sự kiện, URAH làm site khách.
- **Nguồn:** PROTO\09_GENERATOR

## h22 · Report engine

Dạng: Quy trình nội bộ · Trạng thái: Đang chạy · Quyết: chưa · Ưu tiên: 0 · Cấp: workflow · Claude đoán, chờ Linh

- **Là gì:** Báo cáo PDF tự động theo mẫu
- **Khách:** Khách mua báo cáo, NGO, brand
- **Nỗi đau:** Báo cáo làm tay lâu và đắt
- **Việc khách cần (JTBD):** Khi cần báo cáo, tôi muốn nhận bản đẹp đúng số, để dùng ngay
- **Khách tin khi / mất khách khi:** Khách đọc báo cáo để quyết một việc. Báo cáo không nói phải làm gì thì đẹp mấy cũng xếp xó.
- **Mặt tiền:** Chọn mẫu → nạp dữ liệu → xuất PDF
- **Module cần:** Báo cáo tự động
- **Đề xuất:** Module Báo cáo tự động dùng chung.
- **Phản biện:** CTS đang chạy FastAPI; tách lõi báo cáo khỏi chiêm tinh trước.
- **Gộp vào:** Module Báo cáo tự động.
- **Dùng chung:** TUVA báo cáo NGO, Listening báo cáo ngành, Agent Force báo cáo chẩn đoán.
- **Nguồn:** LAB046, report-core

## h23 · Hệ kênh lấy lead

Dạng: Quy trình nội bộ · Trạng thái: Ý tưởng · Quyết: chưa · Ưu tiên: 0 · Cấp: loi · Claude đoán, chờ Linh

- **Là gì:** Showcase, form, onboard, theo dõi lead mọi BU
- **Khách:** Sale mọi BU
- **Nỗi đau:** Lead về rồi nguội vì không ai nhận
- **Việc khách cần (JTBD):** Khi có lead, tôi muốn được giao ngay kèm thông tin, để gọi trong ngày
- **Khách tin khi / mất khách khi:** Lead nguội vì không ai gọi trong 1 giờ. Hệ thống không thay được người gọi.
- **Mặt tiền:** Lead về → gắn BU → giao người → theo dõi
- **Module cần:** CRM / lead; Nội dung / SEO
- **Đề xuất:** Đây là CRM + mồi lead chung, làm ngay sau Thanh toán.
- **Phản biện:** Lead về Google Sheet vẫn đủ cho tới khi có 3 BU dùng.
- **Gộp vào:** Module CRM / lead.
- **Dùng chung:** Một phễu lead cho mọi BU, gắn nhãn BU, chuyển lead chéo (ví dụ TUVA ↔ Listening).
- **Ghi chú:** 6/11: đây là Own Channel OS dùng chung (site, content hub, mạng xã hội, Zalo OA, bản tin, sự kiện → một CRM + đo phễu). BU chạy thật đầu tiên là ifAgent (h08), Linh 11:24: nói 'ifAgent' là hiểu own channel OS. BU khác (TUVA, Unikon, Saké, cungai) cắm vào sau.
Linh 6/11 12:44: mở rộng thành BU OS cho mọi BU B2B, 13 việc: giới thiệu, SEO/GEO, chiếm từ mới (vd ifAgent Event chiếm 'event technology'), cập nhật hoạt động, social, freebie, quét lead; vận hành: quản lý lead, hồ sơ năng lực/credential, quét nhu cầu + đề bài, viết proposal, tìm idea cho brief, Agent Shell vận hành BU. Mỗi BU = một hồ sơ cấu hình. OPC OS = bản B2C bán thẳng cùng máy (đầu ra là đơn). Chi tiết: https://claude.ai/artifact/4ZVAqsor1zbiKGnuRBVhom. Quy hoạch, chưa làm.
- **Nguồn:** Kế hoạch 0.1 ngày 3/11

## h24 · Khâu kiểm chất lượng

Dạng: Quy trình nội bộ · Trạng thái: Có bản thử · Quyết: chưa · Ưu tiên: 0 · Cấp: workflow · Claude đoán, chờ Linh

- **Là gì:** Kiểm thương hiệu, số liệu, luật quảng cáo, pháp chế
- **Khách:** Người duyệt nội dung
- **Nỗi đau:** Lọt sai thương hiệu, sai số, sai luật quảng cáo
- **Việc khách cần (JTBD):** Khi sắp đăng/gửi khách, tôi muốn máy soát trước, để không bị phạt hay mất uy tín
- **Khách tin khi / mất khách khi:** Khách không thấy cổng kiểm, chỉ thấy lỗi. Kiểm luật xong vẫn phải đọc bằng mắt khách.
- **Mặt tiền:** Gửi bài → kiểm brand, số, luật → đạt/sửa
- **Module cần:** Sinh nội dung AI
- **Đề xuất:** Một bước kiểm trong quy trình xuất bản, không phải site.
- **Gộp vào:** Gộp Sinh nội dung AI.
- **Dùng chung:** Unikon bán brand check cho khách; TUVA kiểm thông điệp nhạy cảm giới.
- **Nguồn:** LAB036, LAB107

## h25 · 15 website LINHX-WEB

Dạng: Hệ thống web · Trạng thái: Có site · Quyết: chưa · Ưu tiên: 0 · Cấp: chưa · Claude đoán, chờ Linh

- **Là gì:** Khung web chung cho mọi thương hiệu
- **Khách:** Khách tìm các thương hiệu
- **Nỗi đau:** Site cũ chậm, lỗi thời, không lên Google
- **Việc khách cần (JTBD):** Khi tìm dịch vụ, tôi muốn site nhanh rõ có ví dụ thật, để tin và liên hệ
- **Khách tin khi / mất khách khi:** Khách vào site để biết: làm được gì cho tôi, giá bao nhiêu, ai đã dùng. Thiếu một trong ba là đi.
- **Mặt tiền:** Mặt tiền chung cho 15 thương hiệu
- **Kênh:** Web
- **Module cần:** Nội dung / SEO
- **Đề xuất:** Giữ Astro làm mặt tiền; Frappe làm phần sau.
- **Phản biện:** Chuyển 15 site sang Frappe Website là lùi về SEO; không nên.
- **Gộp vào:** Khuôn Trang giới thiệu.
- **Nguồn:** GV001 (Astro)

## h26 · Sổ tài chính + dòng tiền

Dạng: Quy trình nội bộ · Trạng thái: Đang chạy tay · Quyết: chưa · Ưu tiên: 0 · Cấp: workflow · Claude đoán, chờ Linh

- **Là gì:** Phải thu, nợ, lương theo BU
- **Khách:** Linh, Hoa kế toán
- **Nỗi đau:** Không biết tiền về đâu, nợ bao nhiêu
- **Việc khách cần (JTBD):** Khi đầu tuần, tôi muốn thấy dòng tiền 4 tuần tới, để quyết chi
- **Mặt tiền:** Nhập thu chi → xem dòng tiền tuần
- **Module cần:** Báo cáo tự động
- **Đề xuất:** Để sau: Frappe có sẵn kế toán (ERPNext) nếu cần.
- **Phản biện:** Kế toán thật cần kế toán viên; đừng tự dựng.
- **Gộp vào:** Lõi điều hành.
- **Nguồn:** Sheet Hoa, C BOARD

Liên quan: [[dich-cuoi]] [[kien-truc]] [[hop-nhat]]
