# DANH SÁCH MỤC NGHI VẤN OCR (`can_kiem = true`) — CẦN CLAUDE SOI 6 ẢNH AGENDA GỐC

Nguồn đối chiếu: `C:\linhx\rc6-cuc-bo\e2e\agenda\ocr-agenda.txt` & `LUU-Y-OCR.md` (6 ảnh `agenda1.jpg` .. `agenda6.jpg`).
Đã chạy kiểm chéo 2 lượt bằng `apps/lab/scripts/xay-agenda-tu-ocr.js`: sửa `"Al"` → `"AI"` mọi chỗ, giữ nguyên dấu tiếng Việt, tên riêng và chức danh gốc.

## 1. Phòng của 3 Track chiều 19/11 (`can_kiem = true`)

| Mã Track | Tên Track | Phòng đang gán | Ảnh gốc cần soi | Ghi chú nghi vấn |
|---|---|---|---|---|
| `01` | TRACK OLIVE · FROM SEARCH TO DELEGATION | **Phòng Hồ Tây 2** | `agenda2..4.jpg` | Kiểm phòng Track Olive = Phòng Hồ Tây 2 trên ảnh agenda2.jpg |
| `02` | TRACK LAVENDER · FROM VISIBILITY TO RECOMMENDATION | **Phòng Trúc Bạch** | `agenda2..4.jpg` | Kiểm phòng Track Lavender = Phòng Trúc Bạch trên ảnh agenda3.jpg |
| `04` | TRACK IRIS · FROM AUTOMATION TO SHARED AGENCY | **Phòng Hồ Tây 1** | `agenda2..4.jpg` | Kiểm phòng Track Iris = Phòng Hồ Tây 1 trên ảnh agenda4.jpg |

## 2. Các phiên chương trình có điểm nghi vấn OCR (`can_kiem = true`)

| Mã phiên | Ảnh gốc | Khung giờ (+07) | Phòng | Nội dung phiên / Diễn giả | Điểm cần Claude soi ảnh |
|---|---|---|---|---|---|
| `ag1-07` | `agenda1.jpg` | 10:15–10:45 19/11 | Hồ Tây Grand Ballroom | **Keynote — One Growth System** — Mr. Nguyễn Đức Sơn, Founder & Chairman, Interloka Brand Agency | OCR ghi "Mr. Nguyễn Đức Son [nghi: Sơn]" — cần soi dấu tên Sơn trên agenda1.jpg |
| `ag2-01` | `agenda2.jpg` | 13:30–13:55 19/11 | Phòng Hồ Tây 2 | **Keynote — TĂNG TRƯỞNG THƯƠNG HIỆU KHI AI THAM GIA QUYỀN LỰA CHỌN: Bảo vệ bản sắc và xây dựng hệ sinh thái trải nghiệm kết nối** — Mr. Bùi Quý Phong, Phó Chủ tịch CSMO Việt Nam | Kiểm phòng Track Olive = Phòng Hồ Tây 2 trên agenda2.jpg |
| `ag2-08` | `agenda2.jpg` | 16:15–17:30 19/11 | Phòng Hồ Tây 2 | **Panel Discussion — Delegated Commerce Governance: Khi AI được trao quyền mua hàng, ai thiết lập luật chơi?** — Ms Đặng Thuý Hà; Mr. Đào Trung Thành; Mr. Đinh Trần Tuấn Linh; Mr. Đào Hoàng Thanh; Mr. Phạm Vũ Tùng, CMO, CNG Group; Moderator: Mr. Bùi Quý Phong | OCR ghi "CNC Group" cho Mr. Phạm Vũ Tùng ở dòng Panel (dùng "CNG Group" theo Keynote); cần soi ảnh agenda2.jpg |
| `ag3-01` | `agenda3.jpg` | 13:30–13:55 19/11 | Phòng Trúc Bạch | **Keynote — THE MACHINE READABLE BRAND: Thương hiệu của bạn, AI có hiểu không?** — Mr. Tuấn Nguyễn, CEO, NetSpace | Kiểm phòng Track Lavender = Phòng Trúc Bạch trên agenda3.jpg |
| `ag3-06` | `agenda3.jpg` | 15:25–15:50 19/11 | Phòng Trúc Bạch | **Keynote — Ứng dụng GAI và triển khai các giải pháp GEO thực tiễn nhằm tối ưu hóa hiển thị trên các công cụ tìm kiếm bằng AI** — Mr. Nguyễn Trọng Thành, Giám đốc Sản phẩm Admicro, Giám đốc Dự án Luvi GEO, VCCorp | OCR ghi "Ứng dụng CAI [nghi: AI] và triển khai các giải pháp CEO [nghi: GEO]" và "Luvi GEO" — đã đối chiếu GAI/GEO |
| `ag3-08` | `agenda3.jpg` | 16:50–17:30 19/11 | Phòng Trúc Bạch | **Panel Discussion — RA MẮT SẢN PHẨM TRONG THỜI ĐẠI AI: LÀM SAO ĐỂ KHÁCH HÀNG CHỌN MUA? Bài học từ Trung Quốc về tạo nhu cầu, đầu tư truyền thông và quyết định mở rộng chiến dịch.** — Ms. Yan Yi, Founder & CMO, bbk! Communications Group; Ms. Jiang Na, Vice President, Huan.TV; Moderator: Ms. Phan Đặng Trà My, Phó Tổng Giám đốc VCCorp, Phó Chủ tịch CSMO Việt Nam | OCR nghi vấn tên đơn vị "bbk! Communications Group" và danh xưng/tên "Ms. Jiang Na" — đã đối chiếu Doc |
| `ag4-01` | `agenda4.jpg` | 13:30–13:55 19/11 | Phòng Hồ Tây 1 | **Keynote — Khi AI "đọc vị" khách hàng: Những hiệu ứng tâm lý cũ trong cuộc chơi mới** — Ms. Đào Cẩm Thuỷ, Giảng viên Đại học Kinh tế, Đại học Quốc gia Hà Nội, Tác giả cuốn "Marketing Now & Future" | Kiểm phòng Track Iris = Phòng Hồ Tây 1 trên agenda4.jpg |
| `ag4-06` | `agenda4.jpg` | 15:25–15:50 19/11 | Phòng Hồ Tây 1 | **Keynote — Tăng trưởng thương hiệu trong xu hướng tích hợp hệ thống marketing** — Mr. Jonathan Beh, Group President, Chicilon | OCR ghi "Chicilon [nghi]" (có thể Chicilon Media) — cần soi ảnh agenda4.jpg |
| `ag4-07` | `agenda4.jpg` | 15:50–16:50 19/11 | Phòng Hồ Tây 1 | **Keynote — Tái định nghĩa công thức tăng trưởng Khách hàng trong kỷ nguyên AI** — Mr. Hạnh Lê, Co-founder & CPO, PMAX | Mốc giờ OCR nhảy từ 3:50PM sang 4:50PM (có thể thiếu mốc 4:15PM giữa Keynote Hạnh Lê và Panel) — cần soi ảnh agenda4.jpg |
| `ag4-08` | `agenda4.jpg` | 16:50–17:30 19/11 | Phòng Hồ Tây 1 | **Panel Discussion — AI ngày càng làm được nhiều việc hơn. Vai trò của con người trong hệ thống và mối quan hệ giữa người và máy sẽ như thế nào?** — Ms Thương Lê, Phó Tổng Giám đốc, SOI.Pro; Ms Trần Vũ Quỳnh Như; Mr. Lê Công Thành; Mr. Nguyễn Việt Đức; Mr. Jonathan Beh; Moderator: Mr. Nguyễn Đình Thành, Phó Tổng Giám đốc NetSpace, CEO & Co-Founder Elite PR School | Kiểm giờ bắt đầu Panel Track Iris (4:15PM hay 4:50PM) trên agenda4.jpg |
| `ag5-08` | `agenda5.jpg` | 11:00–12:00 20/11 | Hồ Tây Grand Ballroom | **Panel Discussion — Bền vững trong thời đại Agentic AI** — Dr. Hoàng Việt Hà; Mr. Trần Nguyên Vũ; Mr. Phan Tất Thứ; Mr. Lê Hồng Quang; Mr. Lu Wenlong, Executive Director of the International Communication Committee, China Advertising Association; Moderator: Ms Nguyễn Quỳnh Trang | OCR nghi vấn chính tả tên diễn giả quốc tế "Mr. Lu Wenlong" — cần soi ảnh agenda5.jpg |
| `ag6-01` | `agenda6.jpg` | 13:30–13:35 20/11 | Hồ Tây Grand Ballroom | **Giới thiệu chương trình** — Host: Mr Vũ Quý Tâm, CEO CSMO miền Nam | OCR ghi trùng mốc 1:30PM cho cả Giới thiệu chương trình và Keynote kế tiếp — cần soi ảnh agenda6.jpg |

## 3. Các diễn giả có tên / đơn vị nghi vấn OCR (`can_kiem = true`)

| Mã DG | Họ tên đang hiển thị | Bản OCR gốc (nếu khác) | Chức danh & Đơn vị | Điểm cần Claude soi ảnh |
|---|---|---|---|---|
| `03` | **Mr. Nguyễn Đức Sơn** | Nguyễn Đức Son | Founder & Chairman, Interloka Brand Agency | OCR agenda1.jpg ghi "Nguyễn Đức Son [nghi: Sơn]"; giữ "Nguyễn Đức Sơn" khớp hồ sơ BTC, cần soi ảnh xác nhận |
| `09` | **Mr. Phạm Vũ Tùng** | *(như trên)* | CMO, CNG Group | OCR agenda2.jpg dòng Panel ghi "CNC Group", dòng Keynote ghi "CNG Group" (dùng CNG Group) |
| `10` | **Mr. Thuận Đoàn** | *(như trên)* | Phó Viện trưởng Viện Chiến lược Thương hiệu và Cạnh tranh | OCR agenda6.jpg ghi "Mr. Thuận Đoàn" (hồ sơ cũ ghi "Đoàn Thuận") |
| `24` | **Mr. Nguyễn Trọng Thành** | *(như trên)* | Giám đốc Sản phẩm Admicro, Giám đốc Dự án Luvi GEO, VCCorp | OCR agenda3.jpg ghi "Luvi GEO" và tiêu đề phiên "CAI / CEO" — đã đối chiếu GAI/GEO |
| `25` | **Ms. Yan Yi** | *(như trên)* | Founder & CMO, bbk! Communications Group | OCR agenda3.jpg ghi "bbk! Communications Group" — cần soi ảnh |
| `26` | **Ms. Jiang Na** | *(như trên)* | Vice President, Huan.TV | OCR agenda3.jpg ghi "Mr. Jiang Na" — đã đối chiếu Ms. Jiang Na |
| `32` | **Mr. Jonathan Beh** | *(như trên)* | Group President, Chicilon | OCR agenda4.jpg ghi "Chicilon [nghi]" — cần soi ảnh xác nhận tên công ty |
| `39` | **Mr. Lu Wenlong** | *(như trên)* | Executive Director of the International Communication Committee, China Advertising Association | OCR agenda5.jpg ghi "Mr. Lu Wenlong" — cần soi ảnh xác nhận tên tiếng Anh |
