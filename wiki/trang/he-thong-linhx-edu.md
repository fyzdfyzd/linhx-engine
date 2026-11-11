---
tieu_de: Hệ thống nhóm LINHX EDU
loai: unit
trang_thai: cho-linh
cap_nhat: 2026-11-07
nguon: [nguon/2026-11-08-BANG-HE-THONG.json, https://claude.ai/artifact/Wyeq3HaoB6pfgoeC11P2qY]
sinh_tu_dong: scripts/wiki_tu_bang.py (sửa ở bảng rồi chạy lại, đừng sửa tay)
---
# Hệ thống nhóm LINHX EDU

7 dòng. Danh mục đủ: [[danh-muc-he-thong]].

## h01 · Course OS

Dạng: Quy trình nội bộ · Trạng thái: Có bản thử · Quyết: ngay · Ưu tiên: 1 · Cấp: workflow · Claude đoán, chờ Linh

- **Là gì:** Xưởng khoá học top tier, quản trị được: nạp đề và nhu cầu, nghiên cứu nền, kho quan điểm và template, học liệu đủ bộ, slide chất lượng cao, QC, phiên bản theo khách, xuất final, phản hồi, reflect; bản chào và đề xuất, profile giảng viên, credential tự cập nhật sau mỗi lớp
- **Khách:** Linh và giảng viên LINHX; HR/L&D doanh nghiệp mua khoá; học viên
- **Nỗi đau:** 70 giờ soạn cho 55 giờ quỹ; mỗi khách soạn lại; tư liệu rải Zalo/Drive; HR không thấy hiệu quả sau lớp
- **Việc khách cần (JTBD):** Khi nhận đề lớp mới, tôi muốn có bộ khoá đúng nhu cầu khách trong một ngày, để dạy chất lượng top mà không thức đêm
- **Khách tin khi / mất khách khi:** Đo top tier bằng việc học viên làm được sau 30 ngày, và HR có báo cáo để mua tiếp. Số file sinh ra không phải thước đo.
- **Mặt tiền:** Nạp đề → máy soạn → Linh duyệt → xuất; cổng khách DN duyệt đề cương, tải tài liệu, xem báo cáo hiệu quả
- **Module cần:** Sinh nội dung AI; Thợ agy / hàng việc; Khoá học (LMS); Báo cáo tự động; CRM / lead
- **Đề xuất:** Không viết lại. Bọc 9 module Course OS bản 2 thành workflow agy; Frappe app linhx_course chỉ giữ Khoá, Đề, Phiên bản, Quan điểm, Template, Phản hồi và nút duyệt. Mỗi khoá một kho git EDU/<mã>. 18 mảng, 5 bước. Chi tiết: https://claude.ai/artifact/QKjuCFhZzXGtA8dsej8pTy
- **Phản biện:** "360 course" dễ phình: hiện chỉ 3 đầu ra bán được (giáo trình+slide corp, workbook, e-learning). Không làm server thứ ba. Tài liệu ngân hàng không trộn vào kho chung khi chưa ẩn danh. Không dùng Frappe LMS (AGPL) cho phần soạn.
- **Gộp vào:** Module 01–09 Course OS 2, Máy tạo nội dung/LinhX Write, vòng lặp slide LAB099, deck proposal LAB027 (nang-luc.json), phiếu chẩn đoán AIX, brand LAB043, research-loop LAB085, Report engine, Khâu kiểm chất lượng
- **Dùng chung:** Decent AI (TUVA), đào tạo bàn giao agent (Unikon, ifAgent), Sakedemy mặt tiền bán, Industry sharing, lớp teen, CLB Agentic; kho quan điểm dùng chung với Personal Brand
- **Cách thử:** Chạy bước 1 trên lớp corp thật kế tiếp
- **Giả thuyết:** Bọc Course OS 2 thành workflow agy thì Linh soạn một lớp corp trong ≤4 giờ mà chất lượng giữ top
- **Giai đoạn:** Thử nhỏ
- **Ngưỡng:** ≤4 giờ Linh từ đề tới bộ duyệt; học viên ≥4,5/5; ≥60% còn dùng 1 workflow sau 30 ngày
- **Mục tiêu:** V1 xong khi 6 job chạy thật trên 2 lớp corp liên tiếp: J1 soạn ≤4h công Linh; J2 bản chào ≤2h; J3 báo cáo HR D+30 tự sinh; J4 học viên ≥4,5/5, ≥60% còn dùng sau 30 ngày; J5 reflect ≤15 phút; J6 bàn sáng ≤10 phút
- **Ghi chú:** Linh 6/11: Course OS xác nhận, khoá hình thái. 11:09: giảng viên là trợ giảng của Linh, hiện 6 người → Course OS có vai trợ giảng. Đề xuất (chờ Linh): chu trình video e-learning là mảng 22 của Course OS, cấp LINHX Workflow dùng chung Xưởng video AI URAH (h43) và dịch vụ Việt hoá theo phút (LAB074). 3 nhánh: A record Linh + cắt ậm ừ tự động (LAB059 v0.2) làm trước; B slide + giọng (HyperFrames); C giảng viên AI (LAB017 PA2, pilot L01 đã chạy MSI) để sau. Bài 3–5 phút, dọc cho Zalo. Ngưỡng: 1 bài 5 phút ≤30 phút công Linh, ≥60% xem hết.
- **Hình thái:** ok
- **Nguồn:** PROTO\06_COURSE_OS

## h02 · Quản lý lớp corp

Dạng: Hệ thống web · Trạng thái: Đang chạy tay · Quyết: chưa · Ưu tiên: 0 · Cấp: solution · Claude đoán, chờ Linh

- **Là gì:** Lớp, giáo trình, học viên, hoá đơn cho khoá doanh nghiệp (VCB, MSB, Vinhomes…)
- **Khách:** Phòng L&D ngân hàng, DN
- **Nỗi đau:** Khó tìm giảng viên AI hiểu nghiệp vụ ngành, sợ khoá chung chung
- **Việc khách cần (JTBD):** Khi DN cần nhân viên dùng AI, tôi muốn một khoá đúng nghiệp vụ, để có kết quả báo cáo sếp
- **Khách tin khi / mất khách khi:** HR cần một tờ báo cáo: bao nhiêu người làm được việc sau 30 ngày. Có tờ đó thì bán lại được.
- **Mặt tiền:** sakedemy.com/doanh-nghiep
- **Kênh:** Web; Email
- **Cách bán:** B2B
- **Module cần:** CRM / lead; Khoá học (LMS); Đặt lịch; Báo cáo tự động
- **Đề xuất:** Gộp làm phần vận hành của cùng app linhx_course (Lớp, Học viên, Lịch, Hoá đơn, Báo cáo sau lớp) — Course OS là xưởng soạn, đây là quầy bán. Mặt tiền chuyển sang sakedemy.com/doanh-nghiep vì khách ngân hàng đã biết Sakédemy (deck chào VCB).
- **Phản biện:** Ba cửa EDU (linhx.info, Sakedemy, cungai) là quá nhiều cho một người bán. Corp nên một cửa. Học viên corp không tự đăng nhập: cần quản trị nội bộ + báo cáo cho HR, chưa cần cổng học viên.
- **Gộp vào:** Cùng khuôn Khoá học với cungai, Sakedemy, CLB.
- **Dùng chung:** Unikon, ifAgent bán kèm đào tạo bàn giao agent dùng chung bảng Lớp và báo cáo hiệu quả.
- **Cách thử:** Dùng cho 2 lớp corp kế tiếp, gửi báo cáo D+30
- **Giả thuyết:** Một chỗ quản lớp + báo cáo sau lớp giúp HR mua lại
- **Giai đoạn:** Đang chạy
- **Ngưỡng:** ≥1 khách mua lại hoặc giới thiệu sau báo cáo
- **Ghi chú:** Linh chốt 6/11: khoá chỉ bán trên Sakedemy (cửa chính) và linhx.info (kênh thêm, personal brand). Profile + credential trên linhx.info sinh từ Course OS.
- **Nguồn:** EDU\EDU001–020

## h03 · cungai.vn · content hub + e-learning cộng đồng freemium

Dạng: Zalo Mini App + web · Trạng thái: Có bản thử · Quyết: chưa · Ưu tiên: 0 · Cấp: solution · Claude đoán, chờ Linh

- **Là gì:** Hub học AI freemium, web + Zalo Mini App, membership
- **Khách:** (1) Học viên cũ của Linh, trong đó có CLB 100 người; (2) người đi làm VN tìm khoá AI miễn phí; (3) về sau: tổ chức cần đào tạo AI champion
- **Nỗi đau:** Học xong khoá thì không ai chăm, kiến thức AI cũ đi mỗi tuần. Người mới thì gặp khoá AI tiếng Việt ở khắp nơi, chất lượng lẫn lộn, tin tức chưa kiểm chứng, Luật AI 2026 khó hiểu
- **Việc khách cần (JTBD):** Khi học xong một khoá AI, tôi muốn có một chỗ cập nhật cái mới mỗi tuần, nhận prompt, skill và template dùng được ngay, để không bị tụt lại và không phải tự lọc tin
- **Khách tin khi / mất khách khi:** 1.000+ học viên cũ đã tin Linh là tài sản lớn nhất, rẻ hơn kéo người lạ rất nhiều. Họ không cần thêm tin, họ cần mỗi tuần một việc làm thử được ngay cho nghề mình.
- **Mặt tiền:** Zalo OA + Zalo Mini App là cửa chính (bản tin, freebie, khoá free, cộng đồng, mở khoá premium bằng QR). Web cungai.vn hiện có giữ làm lớp SEO và kho lưu trữ, cùng một nguồn nội dung.
- **Kênh:** Zalo; Zalo Mini App; Web
- **Cách bán:** Thuê bao; Miễn phí lấy lead; Bán lẻ
- **Module cần:** Chat bot / Zalo; CRM / lead; Nội dung / SEO; Crawler / dữ liệu; Sinh nội dung AI; Khoá học (LMS); Thanh toán QR; Cộng đồng
- **Đề xuất:** cungai phục vụ 2 mục đích. (A) Content hub: tin AI và trào lưu Sống cùng AI, AI ở Việt Nam, đạo đức và pháp lý AI, kho freebie gồm prompt, skill và template. (B) E-learning và cộng đồng freemium: khoá miễn phí cùng chủ đề với đối thủ để lấy các từ khoá khoá AI top ở VN, tiền thu ở tầng premium. Thứ tự làm: (1) Chăm CLB 100 người trước: bản tin tuần + freebie cho học viên cũ. (2) Mở freebie cho thành viên mới, đổi bằng email hoặc Zalo. (3) Làm khoá miễn phí lấy từ khoá, chọn đề bằng quét nhu cầu: Udemy (khoá AI bán chạy, số học viên, đánh giá, câu hỏi trong Q&A, chủ đề mới nổi), Gitiho, Unica, Google Trends VN; Máy quét chạy hằng tháng, kết quả nạp vào Course OS làm đề. (4) Bán premium. (5) Vận hành CLB AI để đào tạo AI champion cho các tổ chức (B2B). Nội dung lấy từ Course OS (bài và freebie cắt ra từ các khoá), Máy quét và radar LAB035; kết hợp Spiderum để phân phối.
- **Phản biện:** Làm cả 5 bước cùng lúc là phình ra. Chỉ có bước 1 có khách thật đang đau: 100 học viên CLB. Hai bước 3–4 vào thẳng chỗ Gitiho và Unica đã free sẵn (LAB075), nên khoá miễn phí chỉ là vé vào cửa. Premium bán ở đâu? Linh đã chốt chỉ bán trên Sakedemy và linhx.info, nên cungai không có giỏ hàng, chỉ dẫn sang. Bước 5 (AI champion) thực chất là khoá doanh nghiệp, chạy trên Course OS. Hub tin tức ăn công: máy phải chạy 80%, Linh ≤2 giờ/tuần.
- **Gộp vào:** Course OS (h01) cắt freebie và bài từ khoá; Máy quét (h47); radar LAB035; Máy tạo nội dung (h16); Channel OS (h17); plugin linhx-nuoi-cong-dong LAB041; Zalo Mini App mở khoá LAB075; vn-law-check LAB107 cho mục pháp lý; Spiderum
- **Dùng chung:** Freebie và bài viết là đầu ra của Course OS, nên không soạn riêng. Pipeline nội dung là LINHX Workflow dùng chung với linhx.info. CLB AI champion bán qua Course OS mẫu khoá doanh nghiệp.
- **Cách thử:** Mời học viên 30–40 lớp đã dạy + CLB 100 người vào Zalo OA/Mini App, tặng quyền lợi alumni miễn phí (kho freebie, bản tin tuần, 1 buổi hỏi đáp/tháng). Mời qua nhóm Zalo cũ của từng lớp, mỗi lớp 1 mã QR riêng để đo. Chạy thử 5 lớp trước, đạt thì mời hết.
- **Giả thuyết:** Người đi làm VN đổi email/Zalo lấy bản tin AI kiểm chứng + checklist Luật AI, và một phần bấm sang khoá
- **Giai đoạn:** Khảo sát
- **Ngưỡng:** 5 lớp đầu: ≥30% học viên nhận lời mời, ≥50% mở bản tin, ≥30% dùng ít nhất 1 freebie trong 4 tuần. Đạt thì mời cả 30–40 lớp, rồi mở cho người mới; sau đó ≥5% bấm sang premium
- **Mục tiêu:** v1: ≥300 học viên cũ vào OA, ≥40% hoạt động tuần; ≥1.000 thành viên mới; ≥5% mua premium/Sakedemy; Linh ≤2 giờ/tuần; sau v1: 2 tổ chức đặt AI champion. 8 job J1–J8, 10 module. Chi tiết: https://claude.ai/artifact/KZqSmrNTxJRdZiEWkQGHWA
- **Ghi chú:** Linh 6/11 11:09 CHỐT vai: cungai là lớp user (tài khoản, sổ khách chung của EDU); cộng đồng duy nhất CLB Cùng AI; Sakedemy cung cấp khoá e-learning cho cungai; e-learning (LMS) là lõi dùng chung; cungai học miễn phí + cộng đồng, Sakedemy bán, linhx.info tiếng nói Linh. Domain cungai.vn. Còn chờ: Spiderum, số nhóm Zalo còn giữ.
- **Nguồn:** LAB075, LAB076, Linh 6/11

## h04 · Kho học liệu miễn phí

Dạng: Hệ thống web · Trạng thái: Ý tưởng · Quyết: khong · Ưu tiên: 0 · Cấp: chưa · Claude đoán, chờ Linh

- **Là gì:** Template, prompt, học liệu làm mồi lấy lead
- **Khách:** Nhân viên văn phòng, học viên cũ
- **Nỗi đau:** Không biết bắt đầu từ prompt nào cho việc của mình
- **Việc khách cần (JTBD):** Khi gặp việc lặp lại, tôi muốn mẫu dùng ngay, để đỡ mày mò
- **Khách tin khi / mất khách khi:** Mẫu prompt ai cũng phát. Khách chỉ để lại email nếu mẫu giải đúng việc của họ hôm nay.
- **Mặt tiền:** cungai.vn (kho freebie, module 3 của cungai) + trong Zalo Mini App
- **Kênh:** Web; Zalo
- **Cách bán:** Miễn phí lấy lead
- **Module cần:** Nội dung / SEO; CRM / lead
- **Đề xuất:** Không phải unit riêng: là module 3 Kho freebie của cungai. Bộ prompt, skill, template cắt từ Course OS.
- **Phản biện:** Kho mồi chỉ có giá khi đo được lead; cần LEAD-MAGNET chung mọi BU.
- **Gộp vào:** Gộp vào cungai (h03), module Kho freebie.
- **Cách thử:** Đăng 1 bộ 20 prompt ngân hàng, đo lead
- **Giả thuyết:** Bộ template/prompt miễn phí kéo lead cho khoá corp
- **Giai đoạn:** Ý tưởng
- **Ngưỡng:** ≥50 lead có email trong 7 ngày
- **Ghi chú:** 6/11 11:02 Linh: domain là cungai.vn. Chuyển kho học liệu từ sakedemy.com/tai-nguyen sang cungai.vn.
- **Nguồn:** Định hướng LINHX 3.5

## h05 · CLB Cùng AI (cộng đồng duy nhất)

Dạng: Dự án · Trạng thái: Đang chạy tay · Quyết: chưa · Ưu tiên: 0 · Cấp: chưa · Claude đoán, chờ Linh

- **Là gì:** Đăng ký, thu phí, cộng đồng học viên học tiếp
- **Khách:** Học viên corp đã học xong
- **Nỗi đau:** Học xong không có chỗ hỏi tiếp, quên nhanh
- **Việc khách cần (JTBD):** Khi áp dụng thật gặp khó, tôi muốn nhóm hỏi đáp có người giỏi, để không bỏ cuộc
- **Khách tin khi / mất khách khi:** Học viên không thiếu nhóm Zalo. Họ bỏ vì không có ai trả lời đúng lúc. Ai trả lời, trong bao lâu?
- **Mặt tiền:** sakedemy.com/clb-agentic
- **Kênh:** Zalo; Sự kiện
- **Cách bán:** Thuê bao; Chia doanh thu
- **Module cần:** Khoá học (LMS); Thanh toán QR; CRM / lead
- **Đề xuất:** Gom CLB Agentic, CLB 100 người, CLB AI Edge và nhóm Zalo cungai thành MỘT cộng đồng: CLB Cùng AI, sống trong cungai (Zalo OA + Mini App). Có tầng miễn phí và tầng trả phí.
- **Phản biện:** Sau 2 khoá chưa đạt; đừng dựng hạ tầng trước khi có 20 học viên trả tiền.
- **Gộp vào:** Gộp vào cungai (h03), module Cộng đồng.
- **Dùng chung:** Tầng trả phí của cộng đồng cungai: nhóm Zalo miễn phí → CLB Agentic trên Sakedemy.
- **Cách thử:** Hỏi 30 học viên cũ qua Zalo
- **Giả thuyết:** Học viên corp muốn học tiếp ở CLB trả phí
- **Giai đoạn:** Khảo sát
- **Ngưỡng:** ≥10 người đặt cọc
- **Ghi chú:** Linh 6/11 11:09: chỉ có 1 cộng đồng duy nhất là CLB Cùng AI, gom hết.
- **Nguồn:** Định hướng LINHX 3.2

## h06 · Industry sharing

Dạng: Dự án · Trạng thái: Ý tưởng · Quyết: chưa · Ưu tiên: 0 · Cấp: chưa · Claude đoán, chờ Linh

- **Là gì:** Hội thảo theo ngành: đăng ký, lead cho các BU
- **Khách:** Lãnh đạo DN theo ngành
- **Nỗi đau:** Không biết ngành mình đang dùng AI ra sao, sợ tụt lại
- **Việc khách cần (JTBD):** Khi lập kế hoạch năm, tôi muốn nghe case cùng ngành, để quyết đầu tư AI
- **Khách tin khi / mất khách khi:** Lãnh đạo không đi nghe chia sẻ chung chung. Có case cùng ngành, có số, họ mới đến.
- **Mặt tiền:** linhx.info/sharing (trang sự kiện)
- **Kênh:** Sự kiện; Web
- **Cách bán:** Miễn phí lấy lead; B2B
- **Module cần:** CRM / lead; Sự kiện / minigame
- **Đề xuất:** Chiến dịch, không phải hệ thống: dùng trang sự kiện ifAgent + CRM chung; nội dung case ngành do Course OS (mảng nghiên cứu nền) soạn một lần dùng cho 6 ngành.
- **Phản biện:** Chi phí sự kiện cao; chỉ làm khi có nhà tài trợ.
- **Gộp vào:** Dùng khuôn sự kiện của ifAgent.
- **Dùng chung:** Lead chia cho Sakedemy (đào tạo), Unikon/ifAgent (agent), TUVA (radar).
- **Cách thử:** Chào 5 nhà tài trợ ngành ngân hàng
- **Giả thuyết:** Nhà tài trợ trả chi phí sharing theo ngành để có lead
- **Giai đoạn:** Ý tưởng
- **Ngưỡng:** ≥1 nhà tài trợ ký trước 30/11
- **Nguồn:** EDU013

## h07 · Lớp teen + digital literacy

Dạng: Dự án · Trạng thái: Ý tưởng · Quyết: chưa · Ưu tiên: 0 · Cấp: chưa · Claude đoán, chờ Linh

- **Là gì:** Trang đăng ký thử khói K1, K2 (bán qua Sakedemy)
- **Khách:** Phụ huynh có con 13–17
- **Nỗi đau:** Con dùng AI làm bài hộ, bố mẹ lo nhưng không biết dạy
- **Việc khách cần (JTBD):** Khi thấy con dùng AI, tôi muốn con học dùng đúng cách và an toàn, để yên tâm
- **Khách tin khi / mất khách khi:** Phụ huynh trả tiền khi thấy con thay đổi, không phải khi thấy giáo án. Đầu ra con làm được gì sau 4 buổi?
- **Mặt tiền:** sakedemy.com/teen
- **Kênh:** Web; Zalo
- **Cách bán:** Bán lẻ
- **Module cần:** Khoá học (LMS); Thanh toán QR; CRM / lead
- **Đề xuất:** Hai trang thử khói trên Sakedemy; giáo trình soạn bằng Course OS. Kiểm luật dữ liệu trẻ em trước khi mở form.
- **Phản biện:** Phụ huynh mua cần niềm tin; kiểm luật trẻ em trước khi thu dữ liệu.
- **Gộp vào:** Sakedemy (mặt tiền), Course OS (soạn), Thanh toán QR chung.
- **Cách thử:** Hai trang K1, K2 trên sakedemy.com 09–22/11
- **Giả thuyết:** Phụ huynh trả tiền cho khoá AI đúng cách, không dạy code (H22)
- **Giai đoạn:** Thử nhỏ
- **Ngưỡng:** ≥10 đặt chỗ có cọc
- **Nguồn:** EDU014, kế hoạch tổng mục 3

Liên quan: [[dich-cuoi]] [[kien-truc]] [[hop-nhat]]
