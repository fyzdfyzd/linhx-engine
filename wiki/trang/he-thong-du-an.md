---
tieu_de: Hệ thống nhóm Dự án
loai: unit
trang_thai: cho-linh
cap_nhat: 2026-11-07
nguon: [nguon/2026-11-08-BANG-HE-THONG.json, https://claude.ai/artifact/Wyeq3HaoB6pfgoeC11P2qY]
sinh_tu_dong: scripts/wiki_tu_bang.py (sửa ở bảng rồi chạy lại, đừng sửa tay)
---
# Hệ thống nhóm Dự án

15 dòng. Danh mục đủ: [[danh-muc-he-thong]].

## h45 · Chiêm Tinh Số (OPC001)

Dạng: Hệ thống web · Trạng thái: Đang chạy · Quyết: chưa · Ưu tiên: 0 · Cấp: solution · Claude đoán, chờ Linh

- **Là gì:** chiemtinh.vn, đang có khách, bán report qua QR
- **Khách:** Người tò mò về bản thân, người muốn tặng quà
- **Nỗi đau:** Xem tử vi/chiêm tinh trên mạng chung chung, khó tin
- **Việc khách cần (JTBD):** Khi muốn hiểu mình hay tặng quà, tôi muốn báo cáo riêng đẹp, mua 2 bước, để đọc ngay
- **Khách tin khi / mất khách khi:** Khách tin khi đọc thấy mình trong đó. Báo cáo ghép đoạn có lời viết cho trẻ em (1/11) là mất khách ngay.
- **Mặt tiền:** chiemtinh.vn
- **Kênh:** Web; Zalo; Messenger
- **Cách bán:** Bán lẻ; Quà tặng; Thuê bao
- **Module cần:** Tài khoản khách; Thanh toán QR; Báo cáo tự động; Affiliate / giới thiệu; Chat bot / Zalo
- **Đề xuất:** Giữ FastAPI, đang có khách; lấy làm mẫu suy ngược module Bán.
- **Phản biện:** Chuyển lên Frappe lúc này rủi ro mất đơn; mở mã calc-service trước 20/11.
- **Gộp vào:** Mẫu cho khuôn Bán sản phẩm số.
- **Dùng chung:** Khuôn bán báo cáo số dùng lại cho Listening, Sakedemy (e-book), quà Tết B2B.
- **Nguồn:** fyzdfyzd/chiemtinhso

## h46 · OPC tiếp theo

Dạng: Hệ thống web · Trạng thái: Có bản thử · Quyết: chưa · Ưu tiên: 0 · Cấp: chưa · Claude đoán, chờ Linh

- **Là gì:** Khuôn OPC: nhân bản sản phẩm số thắng
- **Khách:** Khách của từng ngách
- **Nỗi đau:** Chưa rõ: tìm từ radar
- **Việc khách cần (JTBD):** Khi … tôi muốn … để … (chưa có, phải tìm trước khi dựng)
- **Khách tin khi / mất khách khi:** Chưa có khách, chưa có nỗi đau. Đừng dựng khuôn trước khi biết ai sẽ mua.
- **Mặt tiền:** tên miền riêng mỗi OPC
- **Kênh:** Web; Zalo
- **Cách bán:** Bán lẻ
- **Module cần:** Thanh toán QR; Báo cáo tự động; Tài khoản khách
- **Đề xuất:** OPC mới dựng thẳng trên engine, khuôn Bán sản phẩm số.
- **Phản biện:** Chưa có OPC thứ hai thắng; đừng dựng khuôn trước sản phẩm.
- **Gộp vào:** Khuôn Bán sản phẩm số.
- **Cách thử:** Thử khói OPC002 01/12
- **Giả thuyết:** Có sản phẩm số thứ hai bán được trên khuôn CTS
- **Giai đoạn:** Ý tưởng
- **Ngưỡng:** ≥20 đơn trong 14 ngày
- **Nguồn:** PROTO\03_OPC_OS

## h47 · Máy quét

Dạng: Quy trình nội bộ · Trạng thái: Đang chạy · Quyết: chưa · Ưu tiên: 0 · Cấp: workflow · Claude đoán, chờ Linh

- **Là gì:** Crawler, Medium, CafeBiz, vault, extension
- **Khách:** Linh, các BU, toà soạn
- **Nỗi đau:** Đọc tay hàng trăm nguồn mỗi ngày
- **Việc khách cần (JTBD):** Khi cần tin hay bài, tôi muốn có sẵn kho đã lọc, để chỉ chọn
- **Khách tin khi / mất khách khi:** Người dùng là các BU. Kho đầy mà không ai đọc thì chỉ là chi phí lưu trữ.
- **Mặt tiền:** Đặt nguồn → quét đêm → kho → digest
- **Module cần:** Crawler / dữ liệu
- **Đề xuất:** Giữ riêng; engine đọc kết quả qua API.
- **Phản biện:** Chạy ở máy cty, cần Chrome đăng nhập; không đưa lên server.
- **Gộp vào:** Module Crawler (chỉ đầu ra).
- **Dùng chung:** Nguồn dữ liệu cho Radar TUVA, Listening, CafeBiz, nghiên cứu khoá học.
- **Nguồn:** fyzdfyzd/mayquet

## h48 · BespokeAI

Dạng: Dự án · Trạng thái: Có bản thử · Quyết: chưa · Ưu tiên: 0 · Cấp: chưa · Claude đoán, chờ Linh

- **Là gì:** Cùng chị Hương: QR, minigame, CX gom chat
- **Khách:** Brand lớn của chị Hương
- **Nỗi đau:** Agency không hiểu chiến lược, AI vendor không hiểu brand
- **Việc khách cần (JTBD):** Khi muốn AI cho marketing, tôi muốn người hiểu brand làm trọn gói, để ra kết quả thấy được
- **Khách tin khi / mất khách khi:** Khách chị Hương mua vì tin chị. Sản phẩm phải làm chị yên tâm gửi tên mình vào.
- **Mặt tiền:** trang Bespoke (tên miền riêng hoặc unikon.vn/bespoke)
- **Kênh:** Web; Zalo
- **Cách bán:** B2B; Chia doanh thu
- **Module cần:** Sự kiện / minigame; Chat bot / Zalo; CRM / lead
- **Đề xuất:** Là tập khách dùng 3 gói (QR, minigame, CX) trên engine.
- **Phản biện:** Sản phẩm chưa cụ thể, tiêu chuẩn chị Hương rất cao; chốt một gói trước.
- **Gộp vào:** Dùng QR phygital + Sự kiện.
- **Cách thử:** Chốt 1 gói với chị Hương, chào 3 khách
- **Giả thuyết:** Khách của chị Hương mua 1 gói chuẩn
- **Giai đoạn:** Khảo sát
- **Ngưỡng:** ≥1 khách trả gói Check-up
- **Ghi chú:** Linh 6/11 11:20: BespokeAI là một hình thái của Agent Force: chìa khoá trao tay cho DN. Dùng chung chu trình 7 bước + công cụ của h08, khác ở chỗ làm hết rồi giao.
- **Nguồn:** P6_PRJ-BESPOKE

## h49 · Agent cho RM ngân hàng

Dạng: Dự án · Trạng thái: Ý tưởng · Quyết: chưa · Ưu tiên: 0 · Cấp: chưa · Claude đoán, chờ Linh

- **Là gì:** Cùng chị Thuỷ, ra mắt event cuối T11
- **Khách:** RM, quản lý chi nhánh ngân hàng
- **Nỗi đau:** Chỉ tiêu cao, thời gian chăm khách ít
- **Việc khách cần (JTBD):** Khi chuẩn bị gặp khách, tôi muốn trợ lý soạn sẵn hồ sơ và gợi ý, để chốt nhiều hơn
- **Khách tin khi / mất khách khi:** RM không có thời gian học. Trợ lý phải ở trong luồng việc sẵn có, chạy ngay ngày đầu.
- **Mặt tiền:** trang giới thiệu cho event Talentpool
- **Kênh:** Web; Zalo
- **Cách bán:** B2B
- **Module cần:** Chat bot / Zalo; CRM / lead
- **Đề xuất:** Là cấu hình Agent Shell cho ngân hàng, cần cho event cuối T11.
- **Phản biện:** Hạn gấp; làm demo, đừng đợi engine.
- **Gộp vào:** Dùng Agent Shell.
- **Cách thử:** Demo tại event Talentpool cuối T11
- **Giả thuyết:** Manager ngân hàng muốn agent cho RM
- **Giai đoạn:** Thử nhỏ
- **Ngưỡng:** ≥5 đăng ký coaching/pilot
- **Nguồn:** Input Linh dự án 2

## h50 · Research agent

Dạng: Dự án · Trạng thái: Có bản thử · Quyết: chưa · Ưu tiên: 0 · Cấp: chưa · Claude đoán, chờ Linh

- **Là gì:** Cùng anh Dũng, research loop + viết bài
- **Khách:** Nhà nghiên cứu, anh Dũng
- **Nỗi đau:** Đọc tài liệu và viết mất nhiều tháng
- **Việc khách cần (JTBD):** Khi có đề tài, tôi muốn máy gom và nháp, để tập trung phân tích
- **Mặt tiền:** listening.vn/research
- **Cách bán:** B2B
- **Module cần:** Crawler / dữ liệu; Sinh nội dung AI
- **Đề xuất:** Dùng chung Crawler + Sinh nội dung; mặt tiền là trang con.
- **Gộp vào:** Gộp Listening Vietnam.
- **Nguồn:** P7_PRJ-RESEARCH, LAB085

## h51 · CafeBiz toà soạn

Dạng: Dự án · Trạng thái: Có bản thử · Quyết: chưa · Ưu tiên: 0 · Cấp: chưa · Claude đoán, chờ Linh

- **Là gì:** Bot Telegram 20 tin, bài tương tác
- **Khách:** Toà soạn CafeBiz
- **Nỗi đau:** Chọn tin mỗi sáng mất nhiều giờ
- **Việc khách cần (JTBD):** Khi 7h sáng, tôi muốn 20 tin đã chọn sẵn, để viết ngay
- **Khách tin khi / mất khách khi:** Biên tập viên chọn tin bằng cảm giác bạn đọc. Máy chọn 20 tin mà sai gu thì họ vẫn đọc lại từ đầu.
- **Mặt tiền:** trang dịch vụ trên urah.vn
- **Kênh:** Email
- **Cách bán:** B2B
- **Module cần:** Crawler / dữ liệu; Sinh nội dung AI
- **Đề xuất:** Khách của Máy quét + Sinh nội dung; chạy ngoài engine.
- **Gộp vào:** Máy quét.
- **Nguồn:** LAB090, LAB091

## h52 · Tung ta tung tăng

Dạng: Dự án · Trạng thái: Có bản thử · Quyết: chưa · Ưu tiên: 0 · Cấp: chưa · Claude đoán, chờ Linh

- **Là gì:** Du lịch ngách, lễ hội 20/11–10/12
- **Khách:** Khách du lịch lễ hội
- **Nỗi đau:** Không biết đi đâu, xem gì trong lễ hội
- **Việc khách cần (JTBD):** Khi tới lễ hội, tôi muốn gợi ý đường đi hay, để không bỏ lỡ
- **Khách tin khi / mất khách khi:** Khách lễ hội cần biết bây giờ đi đâu. Nền tảng chạy suốt năm không có khách ngoài mùa.
- **Mặt tiền:** site lễ hội đang có
- **Kênh:** Web; Mobile
- **Module cần:** Nội dung / SEO; Sự kiện / minigame
- **Đề xuất:** Chỉ nghiệm thu; không đưa lên engine.
- **Phản biện:** Mùa lễ hội ngắn; dựng nền lâu dài không đáng.
- **Gộp vào:** Không.
- **Nguồn:** P4_PRJ-TTTT, LAB052

## h53 · VWAI

Dạng: Dự án · Trạng thái: Đang chạy · Quyết: chưa · Ưu tiên: 0 · Cấp: chưa · Claude đoán, chờ Linh

- **Là gì:** Demo + tư vấn cho TS. Alex-Thái
- **Khách:** Brand Bia 333
- **Nỗi đau:** Chiến dịch cần tương tác người dùng
- **Việc khách cần (JTBD):** Khi chạy chiến dịch, tôi muốn trò chơi kéo người tham gia, để có data
- **Mặt tiền:** trang case trên unikon.vn
- **Cách bán:** B2B
- **Module cần:** Sự kiện / minigame
- **Đề xuất:** Là khách; dùng khuôn demo chung.
- **Gộp vào:** Khuôn demo ifAgent.
- **Nguồn:** P8_PRJ-VWAI

## h54 · Trợ lý Zalo chị Hương

Dạng: Dự án · Trạng thái: Có bản thử · Quyết: chưa · Ưu tiên: 0 · Cấp: chưa · Claude đoán, chờ Linh

- **Là gì:** Chat 1-1 OA Unikon
- **Khách:** Chị Hương
- **Nỗi đau:** Trả lời tin nhắn khách tốn thời gian
- **Việc khách cần (JTBD):** Khi khách nhắn OA, tôi muốn trợ lý trả lời đúng ý, để tôi chỉ duyệt
- **Mặt tiền:** trang case trên unikon.vn
- **Kênh:** Zalo
- **Cách bán:** B2B
- **Module cần:** Chat bot / Zalo
- **Đề xuất:** Dùng module Chat bot / Zalo.
- **Gộp vào:** Gộp Chat bot.
- **Nguồn:** LAB083

## h55 · Platform 333

Dạng: Dự án · Trạng thái: Có bản thử · Quyết: chưa · Ưu tiên: 0 · Cấp: chưa · Claude đoán, chờ Linh

- **Là gì:** Web app chiến dịch Bia 333
- **Khách:** TS. Alex-Thái
- **Nỗi đau:** Cần demo AI nhanh cho khách tư vấn
- **Việc khách cần (JTBD):** Khi có buổi tư vấn, tôi muốn demo chạy được, để thuyết phục
- **Mặt tiền:** trang case trên linhx.info
- **Kênh:** Web
- **Cách bán:** B2B
- **Module cần:** Sự kiện / minigame
- **Đề xuất:** Là khách; dùng khuôn Sự kiện.
- **Gộp vào:** Gộp Sự kiện.
- **Nguồn:** D:\LINHX\platform-333

## h56 · Persona khảo sát giả lập

Dạng: Quy trình nội bộ · Trạng thái: Có bản thử · Quyết: chưa · Ưu tiên: 0 · Cấp: workflow · Claude đoán, chờ Linh

- **Là gì:** Khảo sát ảo người Việt
- **Khách:** Người làm thông điệp
- **Nỗi đau:** Khảo sát thật lâu và đắt
- **Việc khách cần (JTBD):** Khi cần thử thông điệp, tôi muốn phản hồi giả lập nhanh, để chọn bản tốt trước khi chi tiền
- **Khách tin khi / mất khách khi:** Persona giả lập nói điều mình muốn nghe. Dùng để loại ý tồi, không dùng để xác nhận ý hay.
- **Mặt tiền:** Nhập câu hỏi → chạy persona → đọc kết quả
- **Module cần:** Sinh nội dung AI
- **Đề xuất:** Để sau; công cụ nghiên cứu nội bộ.
- **Gộp vào:** Gộp Sinh nội dung AI.
- **Nguồn:** LAB048, persona-engine

## h57 · Sân khấu 3D + Đi Chùa Online

Dạng: Dự án · Trạng thái: Có bản thử · Quyết: chưa · Ưu tiên: 0 · Cấp: chưa · Claude đoán, chờ Linh

- **Là gì:** Người ảo, live không người
- **Khách:** Người xem live
- **Nỗi đau:** Chưa rõ
- **Việc khách cần (JTBD):** (băng)
- **Kênh:** Live
- **Module cần:** Nhân vật ảo
- **Đề xuất:** Băng.
- **Phản biện:** Rủi ro luật TikTok và tôn giáo.
- **Gộp vào:** Module Nhân vật ảo.
- **Cách thử:** —
- **Giả thuyết:** Live không người kiếm quà đủ tiền
- **Giai đoạn:** No-go
- **Ngưỡng:** Băng vì rủi ro luật TikTok + tôn giáo
- **Nguồn:** LAB038, LAB103

## h58 · Gold radar

Dạng: Dự án · Trạng thái: Băng · Quyết: chưa · Ưu tiên: 0 · Cấp: chưa · Claude đoán, chờ Linh

- **Là gì:** Content hub ngành vàng
- **Khách:** Người mua vàng
- **Nỗi đau:** Chưa rõ
- **Việc khách cần (JTBD):** (băng)
- **Kênh:** Web
- **Module cần:** Crawler / dữ liệu; Nội dung / SEO
- **Đề xuất:** Băng tới khi BTMH ký.
- **Gộp vào:** Không.
- **Cách thử:** —
- **Giả thuyết:** Content hub vàng có khách
- **Giai đoạn:** No-go
- **Ngưỡng:** Băng tới khi BTMH ký QR
- **Nguồn:** PRT012

## h59 · AIX viện AI ứng dụng

Dạng: Dự án · Trạng thái: Tạm hoãn · Quyết: chưa · Ưu tiên: 0 · Cấp: chưa · Claude đoán, chờ Linh

- **Là gì:** Cùng anh Dũng, anh Phong
- **Khách:** —
- **Nỗi đau:** —
- **Việc khách cần (JTBD):** (tạm hoãn)
- **Đề xuất:** Không lên engine.
- **Phản biện:** Đang tạm hoãn.
- **Gộp vào:** Không.
- **Nguồn:** P5_PRJ-AIX

Liên quan: [[dich-cuoi]] [[kien-truc]] [[hop-nhat]]
