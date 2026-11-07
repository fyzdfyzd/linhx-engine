---
tieu_de: Lộ trình LINHX ENGINE
loai: tong-quan
trang_thai: cho-linh
cap_nhat: 2026-11-07
nguon: [nguon/2026-11-08-BANG-HE-THONG.json, https://claude.ai/artifact/Wyeq3HaoB6pfgoeC11P2qY]
sinh_tu_dong: scripts/wiki_tu_bang.py (sửa ở bảng rồi chạy lại, đừng sửa tay)
---
# Lộ trình LINHX ENGINE

## Các chặng

- **Chặng 0 · Xương sống**
  - Cổng đạt: Một lead đi trọn: tải T1 → hồ sơ + đồng ý → cơ hội → giao người → thấy trên bàn; một đơn báo cáo trả QR tự giao.
  - Đến: đêm 6/11 → 18/11 (CSMO)
  - Làm: App linhx_core trên ENGINE 0.1: Đơn vị, Tổ chức, Người, Quan hệ, Cơ hội, Đồng ý, gộp trùng; Tiền: SePay + VietQR cho báo cáo (việc 1 của 0.1), Gói và Giá; Template Trang BU từ khuôn demo ifAgent, form về CRM; ifagent.net bản mới; Freebie T1 Khám nối phễu; bảng phễu 6 tầng bản 1; Bàn điều hành bản 1: việc chờ anh, thợ, job, token; CSMO 18/11: báo cáo + QR chạy trên engine; CTS mở mã calc-service trước 20/11
  - Phiếu: ~35 phiếu
- **Chặng 1 · Bán được**
  - Cổng đạt: 2 pilot ký và đạt chỉ số sau 14 ngày; lớp corp chạy Course OS ≤ 4 giờ công; cungai qua ngưỡng thử 5 lớp.
  - Đến: → 31/12/2026
  - Làm: Agent Force chặng 1: deck và credential tự cập nhật, bảng gói, mẫu hợp đồng pilot, tool T2, 4 case; Course OS v1: bọc 9 module thành workflow, thử trên lớp corp kế tiếp; cungai: Zalo OA + Mini App, bản tin tuần, kho freebie, thử 5 lớp cũ; Expert nấc 0–1: hồ sơ giọng, vault, viết, show → clip; Template Báo cáo: CTS chuyển pay + order; Listening VN báo cáo 1; linhx_event sau CSMO; Tung ta tung tăng chạy mùa lễ hội; agent RM ngân hàng ra mắt cuối T11
  - Phiếu: ~150 phiếu
- **Chặng 2 · Đóng gói, cắm thêm BU**
  - Cổng đạt: Khách thứ hai cùng ngành chạy trong 10 ngày do FDE dẫn; một BU mới lên chỉ bằng cấu hình.
  - Đến: → 31/3/2027
  - Làm: BU OS cho Unikon, TUVA, Event: chỉ điền hồ sơ cấu hình; 3 agent mẫu, Agent Shell bản 1, khoá FDE đợt 1; linhx_finance, people, partner, legal đủ dùng; phí nội bộ URAH; Sakedemy + LMS bán 3 khoá; Expert thêm 2 người trong hệ; Template Công cụ: T3–T5; quyết aicontent.vn
  - Phiếu: ~200 phiếu
- **Chặng 3 · Nhân rộng**
  - Cổng đạt: 15 khách thuê tháng, tiền lặp ≥ 50%, anh ≤ 20% giờ triển khai; các đích ở mục 1.
  - Đến: → 30/6/2027
  - Làm: 6 agent mẫu, 6 FDE, xưởng agent tại chỗ cho khách; Expert bán gói; danh bạ chuyên gia; Listening VN 2 báo cáo; TUVA radar có tỉ lệ đậu; Hỗ trợ sau bán, đồng ý dữ liệu đủ, bản tiếng Anh; CTS chuyển hết (đợt riêng ~300 phiếu, chạy song song bản cũ)
  - Phiếu: ~200 phiếu

## Chặng 0 chia làn

- VM linhx-engine-1 đang chạy (0.1)
- Thợ máy cty đã đăng ký lịch (dang-ky-lich.ps1)
- agy cloud đã đăng nhập nếu muốn chạy hơn 1 thợ
- Có repo để đẩy code (hiện code nằm trong chiemtinhso, thư mục linhx-engine)

- **Làn 0 · Claude (trước khi thợ chạy)**
  - Phiếu: 1 phiên
  - Việc: Phiếu đầu (máy cty): chép code PROTO 03 OPC OS + 01 Máy tạo nội dung từ D:\LINHX\PROTO lên repo; Viết features-dot1.json (mỗi feature ≤ 40 phút, ghi phụ thuộc) + bộ nghiệm thu, anh duyệt rồi khoá; Chia phiếu theo 5 làn dưới, mở hàng việc
- **Làn A · Sổ khách**
  - Phiếu: ~8
  - Việc: DocType Đơn vị, Tổ chức, Người, Quan hệ, Cơ hội; Đồng ý theo mục đích; khoá gộp trùng (điện thoại, email, Zalo); Quyền theo Đơn vị; Chuyển từ 03 OPC OS module 04 (khách + đồng ý), không viết mới
- **Làn B · Tiền**
  - Phiếu: ~6
  - Việc: Webhook SePay + VietQR cho đơn báo cáo, bỏ duyệt tay đơn đã trả; DocType Gói, Giá, Quyền dùng; Chuyển từ 03 OPC OS module 02, 03, 07 (gói giá, thanh toán, sổ S1a-HKD)
- **Làn C · Trang BU**
  - Phiếu: ~6
  - Việc: Khuôn Next.js Trang BU từ demo ifAgent, form về CRM; Dựng ifagent.net bản mới trên khuôn (chạy trên IP, chưa đổi DNS)
- **Làn D · Mồi và phễu**
  - Phiếu: ~5
  - Việc: Đưa T1 Khám (LAB113) thành freebie, kết quả đổi bằng Zalo/email; Bảng phễu 6 tầng bản 1
- **Làn E · Bàn điều hành**
  - Phiếu: ~4
  - Việc: Mở rộng /#/engine: việc chờ anh, lead mới, thợ, token mỗi job

## Khuôn launch một sản phẩm (cổng C1 trở đi)

- **C1 Chốt đề**
  - Đạt bằng: Linh duyệt 1 trang đề; mọi tình huống có mã TH; sau khoá, ý mới sang đợt sau
  - Làm: Chọn 1 trong 7 khuôn site, viết job khách, kho tình huống, sơ đồ trang, mặt tiền. Khoá features.json.
  - Chữa lỗi: thiết kế ẩu
- **C2 Chốt hình**
  - Đạt bằng: Linh duyệt ảnh chụp màn hình mẫu TRƯỚC khi viết code; đổi hình chỉ ở phiên bản sau
  - Làm: Chọn hệ thiết kế từ thư viện có sẵn, DESIGN.md + brand.json, bộ ảnh tài sản khoá phong cách, dựng màn hình mẫu 390 và 1280.
  - Chữa lỗi: đồ hoạ đổi giữa đường
- **C3 Dựng trên khuôn**
  - Đạt bằng: cong_kiem xanh; không phiếu nào chờ gộp quá 1 vòng
  - Làm: site-<tên> chỉ chứa cấu hình + động cơ riêng; module lấy từ linhx_*; mỗi phiếu khai file đụng, hai thợ không đụng chung file; gộp ngay khi đạt, không giữ nhánh dài.
  - Chữa lỗi: tốn thời gian gộp code
- **C4 Test hành trình**
  - Đạt bằng: mọi hành trình xanh trên staging; ảnh lệch quá ngưỡng là trượt
  - Làm: Bộ Playwright chung sinh từ kho tình huống: mua đủ mọi SKU, giải mã QR, mở PDF, đọc thư thật, chụp 390/1280 so ảnh chuẩn.
  - Chữa lỗi: thiếu test đầu cuối, lỗi hiển thị
- **C5 QC sản phẩm**
  - Đạt bằng: không lỗi CHẶN; điểm QC đạt ngưỡng; Linh xem 1 vòng trên điện thoại
  - Làm: Đọc như khách: persona giả lập chạy thử, cổng brand + pháp chế, phiếu QC theo khuôn (nội dung, giá, chính sách, email), 5 người thật alpha có sheet lỗi.
  - Chữa lỗi: QC sản phẩm yếu
- **C6 Lên và giữ**
  - Đạt bằng: kiểm khói xanh trên tên miền thật; bài học ghi vào HOC-HOI và khuôn
  - Làm: Deploy bằng một lệnh, staging giống production, kiểm khói sau deploy, có lệnh lùi bản; lỗi mới thành luật trong khuôn.
  - Chữa lỗi: 

Liên quan: [[dich-cuoi]] [[kien-truc]] [[hop-nhat]] [[danh-muc-de-bai]]
