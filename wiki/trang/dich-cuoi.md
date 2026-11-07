---
tieu_de: Đích cuối đường LINHX ENGINE
loai: tong-quan
trang_thai: cho-linh
cap_nhat: 2026-11-07
nguon: [nguon/2026-11-08-BANG-HE-THONG.json, https://claude.ai/artifact/Wyeq3HaoB6pfgoeC11P2qY]
sinh_tu_dong: scripts/wiki_tu_bang.py (sửa ở bảng rồi chạy lại, đừng sửa tay)
---
# Đích cuối đường LINHX ENGINE

**Vision:** LINHX ENGINE là bộ máy để mở một sản phẩm hay dịch vụ mới nhanh nhất: cài một bản mới từ code lõi chung, bật module cần dùng, điền cấu hình, chọn template, rồi chạy. Máy làm phần lặp lại, người chỉ bán, dạy, nói và duyệt; mỗi việc làm xong thành tài sản cho đơn vị khác.

_Bảng cập nhật: 6/11/2026 13:5x (giờ quốc tế) · Claude · thêm vision và thứ tự đọc_

## Tóm tắt

- Đích 30/6/2027, giả định đủ người và tiền: 27 đơn vị (EDU, Agent Force, Expert, 6 BU, 14 dự án) chạy trên một engine. Đơn vị chỉ là cấu hình, không ai tự dựng hệ thống riêng.
- Hệ thống: 6 tầng trên Frappe. Mỗi đơn vị một bản cài riêng theo cơ chế WordPress (LINHX nội bộ, từng BU, từng OPC, Content hub), chung code lõi và cổng danh tính linhx_id; lõi gồm 25 module lõi, 3 công thức (Radar, Magnet, Expert), 6 module dọc; dưới là 11 máy nền chạy qua hàng việc; trên là 6 template và các tên miền.
- So với những gì anh đã đặt tên, còn thiếu 14 mảng. Năm mảng chặn vòng quay giữa các nhánh: một người một hồ sơ, đồng ý dữ liệu, gói và quyền dùng, hợp đồng, sổ tiền nhiều pháp nhân.
- Lộ trình 4 chặng theo các mốc đã có (18/11 CSMO, 31/12, 31/3, 30/6). Chưa build: anh chốt giải pháp trước (anh dặn 13:15 ngày 6/11).

## Năm thay đổi

- **Mỗi BU tự lo hệ thống**
  - Thành: Một lõi chung. BU chỉ còn là cửa bán: thương hiệu, ngách, người bán, kho case.
- **Người làm, anh kiểm**
  - Thành: Thợ máy làm, người của từng đơn vị duyệt, anh chỉ duyệt điểm chốt.
- **Lead nằm rời trong đầu từng người**
  - Thành: Một sổ khách, mỗi người một hồ sơ. Lead chuyển chéo giữa các BU có đồng ý và có ghi công.
- **Mỗi job làm một lần rồi thôi**
  - Thành: Mỗi job ra case có số trong 7 ngày. Việc lặp lại lần thứ ba thì đóng thành sản phẩm hoặc gói preset.
- **Sản phẩm mới phải dựng từ đầu**
  - Thành: Sản phẩm mới là một bộ cấu hình trên template sẵn có, lên trong vài chục phiếu.

## Từng đơn vị: nay, khi đủ, đo bằng gì

- **Anh (người điều hành)**
  - Đo: Giờ/tuần của anh và tỉ lệ giờ dành cho việc chỉ anh làm được. Em đề xuất ≤ 40 giờ, ≥ 60% là bán/dạy/nói (em đoán, chờ anh chỉnh).
  - Khi đủ: Một bàn điều hành duy nhất: việc chờ anh, tiền về, lead mới. Anh duyệt ≤ 30 phút/ngày, giờ còn lại dồn cho bán, dạy, nói, viết.
  - Nay: 80–100 giờ/tuần, ôm bán, dạy, duyệt, vận hành mọi BU (anh nói 24/10).
- **LINHX EDU (lớp corp, cungai, Sakedemy)**
  - Đo: Giờ công của anh mỗi lớp ≤ 4 giờ. Điểm học viên ≥ 4,5/5. Tỉ lệ lớp sinh ra lead Agent Force. Số lớp do trợ giảng dạy.
  - Khi đủ: Mọi lớp đi qua Course OS, một lõi nội dung cắt ra nhiều dạng. 6 trợ giảng dạy được bằng bộ có sẵn. Học viên cũ về CLB Cùng AI, cuối lớp có cửa vào Agent Force.
  - Nay: 25 khoá 2024–2026, 13 khách corp năm 2025, ngân hàng lớn nhất. Nguồn khách phụ thuộc Talentpool và Unikon (Định hướng 23/10). Mỗi lớp soạn gần như từ đầu.
- **Agent Force (ifagent.net)**
  - Đo: Số DN có agent chạy thật và trả theo tháng. Kế hoạch 24/10 cam kết 4 DN vào 30/6/2027, 8 DN vào 31/12/2027. Bản 'khi đủ' ghi 30 DN là trần lý thuyết.
  - Khi đủ: Một cửa bán agent cho doanh nghiệp. Agent mẫu theo ngành, khách thứ hai cùng ngành lên trong 7 ngày. Mỗi BU là khách số 0 rồi thành case.
  - Nay: Các dự án agent cũ đã thất bại: VTV3, VOV giao thông, Tasco (Input 24/10). Có ENGINE 0.1 chạy báo cáo 'AI nói gì về thương hiệu', chưa thu tiền.
- **Expert OS (anh và mạng chuyên gia)**
  - Đo: Brand Truth ≥ 75, ≥ 5 lời mời/tháng, giờ của anh ≤ 3 giờ/tuần, số hồ sơ chuyên gia trả tiền.
  - Khi đủ: Vault giọng anh nuôi bài, show, sách. Tool chấm thương hiệu cá nhân làm mồi. Sổ quan hệ nằm chung sổ khách. Sau anh thì cắm thêm chuyên gia trong hệ.
  - Nay: Brand Truth 39,7. Thương hiệu tản ra 4 hướng: AI, sáng tạo/Lê Bích, chiêm tinh, công nghệ và triết học (Định hướng 23/10).
- **Unikon**
  - Đo: Độ phủ phễu ≥ 3 lần, 4 job/tháng, ≥ 30% doanh thu từ gói tháng (Kế hoạch 24/10), BTMH ≤ 30% doanh thu.
  - Khi đủ: Xưởng AI production trắng nhãn cho agency. Máy làm phần sản xuất nên năng lực tăng mà không thêm người. Có trang demo, mồi cho agency, gói Brand kit thu theo tháng.
  - Nay: 2–3 lead/tháng, nhận tối đa 2–3 job, gần như mọi lead đều thành job. Đó là dấu hiệu thiếu phễu: độ phủ chỉ khoảng 1 lần (Top việc 24/10). Own media yếu. Minh Hiền nghỉ từ cuối T01.
- **ifAgent Event**
  - Đo: ≥ 2 job may đo/tháng (mức hoà vốn), ≥ 20% lead từ SEO/GEO (Top việc 24/10).
  - Khi đủ: Gói preset giá rẻ chạy quảng cáo, gói may đo giá cao. Mọi sự kiện có báo cáo số đo trong 24 giờ, lead sự kiện vào sổ khách chung.
  - Nay: Đã tái định vị sang event dùng AI, nền tảng làm lại bằng agent. VEV ra 5–7 lead, có 2 khách tự tìm tới qua GEO. CSMO 18/11 kỳ vọng 30–50 lead (Input + Kế hoạch 24/10).
- **TUVA + Listening Vietnam**
  - Đo: ≥ 4 đề xuất có hạng mục Decent AI, thu Decent AI ≥ 300 triệu năm 2027 (Kế hoạch 24/10), số hồ sơ nộp và đậu mỗi tháng.
  - Khi đủ: Decent AI: đối tác AI an toàn cho NGO. Radar tự săn call và soạn hồ sơ. Listening dùng chung máy quét và máy báo cáo, mỗi báo cáo là một sản phẩm.
  - Nay: Comm cho NGO khoảng 1 job/2 tháng. Viện trợ Mỹ giảm từ 68 xuống 32 tỷ USD. Đã thử radar call, có vẻ hiệu quả (Input + Top việc 24/10).
- **Sakedemy**
  - Đo: Có 1 khoá chạy hằng tháng hoặc đóng (Kế hoạch 24/10). Nợ Sake có lộ trình về 0.
  - Khi đủ: Cửa bán khoá và xuất hoá đơn của EDU. Khoá e-learning bán qua QR, dùng chung LMS và Course OS.
  - Nay: Cả 3 nhánh (khoá sáng tạo, sách, gia công content) về 0. Còn khán giả cũ, đã lâu không hoạt động (Input 24/10).
- **URAH**
  - Đo: Phí nội bộ bù ≥ 70% chi, ≥ 90% giờ gắn mã job. Video AI ≥ 2 job/tháng, không đạt thì đóng nhánh từ 31/3 (Kế hoạch 24/10).
  - Khi đủ: Xưởng người của cả hệ. Mọi giờ sản xuất đều gắn mã job và tính phí nội bộ.
  - Nay: Video production không còn hiệu quả, không có sản phẩm riêng, đang lo hạ tầng và sản xuất cho các bên trong hệ (Input 24/10).
- **OPC (Chiêm Tinh Số và các sản phẩm sau)**
  - Đo: Số phiếu từ ý tới ngày bán (đề xuất ≤ 30 phiếu). Doanh thu/ngày, CAC. Kế hoạch 24/10 đặt OPC khoảng 1.700 triệu năm 2027, ngoài cam kết.
  - Khi đủ: Thanh toán, khách, sổ tiền chạy trên lõi chung. Sản phẩm mới lên từ template Báo cáo hoặc Công cụ.
  - Nay: Chiêm Tinh Số có engine riêng. OPC OS mới ở Mức 1, dữ liệu giả lập.
- **Dự án dựng cho khách (VWAI, Platform 333, CafeBiz...)**
  - Đo: Biên lãi từng job, tỉ lệ job thành agent mẫu hoặc sản phẩm bán lại.
  - Khi đủ: Đi chung template Job dựng: mã job, nghiệm thu, bàn giao, case trong 7 ngày.
  - Nay: Mỗi dự án đi một kiểu, khó tính giờ và khó dùng lại.

## Tổng

-
  - hieu_qua: Số đo chính của engine: thời gian từ ý tới sản phẩm/dịch vụ nhận đơn đầu tiên (đo bằng số phiếu và giờ người). Mỗi bản cài mới phải nhanh hơn bản trước.; Giờ công của anh: từ 80–100 giờ xuống mức em đề xuất ≤ 40 giờ/tuần. Đây là số đo quan trọng nhất, vì anh là nút cổ chai.; Chi phí làm thêm một sản phẩm: từ dựng mới thành điền cấu hình. Đo bằng số phiếu tới ngày bán. Mẫu đo đầu tiên là OPC thứ hai.; Chi phí làm thêm một BU: điền hồ sơ BU OS thay vì dựng site, CRM, quy trình riêng.; Thời gian từ đề bài tới proposal ≤ 1 ngày, báo cáo sự kiện trong 24 giờ, mỗi job ra case trong 7 ngày.
  - kinh_doanh: Cam kết đang có (Kế hoạch 24/10, triệu đồng): lõi LINHX thu lũy kế ≥ 1.000 tới 30/6/2027, cả năm 2027 là 2.550 (sàn 1.300); OPC khoảng 1.700 nằm ngoài cam kết. Engine phải giúp đạt các số này, không đặt số mới.; Doanh thu chéo: lead đi giữa EDU, Agent Force, Expert và các BU qua một sổ khách. Đo bằng % doanh thu đến từ lead của đơn vị khác. Hôm nay gần như 0 vì chưa đo được. Em đoán đích là ≥ 20%.; Tiền lặp lại: gói tháng của Unikon, bảo trì agent, thuê bao OPC (Kế hoạch 24/10, H2/2027). Đo bằng tỉ lệ doanh thu lặp lại trên tổng.; Tài sản chung có giá: mỗi job của BU trả phí tài sản chung và phí workforce 5% (Kế hoạch 24/10, luật 2). Engine biến chi phí R&D thành thứ các BU trả tiền dùng.
  - tac_dong: Tài sản dữ liệu: một sổ khách xuyên mọi đơn vị, kho case có số, 326 nguồn quét, bộ 114.731 bài của Listening. Mỗi tháng chạy thì tài sản này dày thêm, đối thủ khó chép.; Cùng một bộ máy phục vụ ba loại người bán: công ty (Radar), sản phẩm (Magnet), con người (Expert). Vì vậy cùng một khoản đầu tư được dùng nhiều lần.; Ra ngoài: những gì LINHX tự chạy trở thành case thật để bán Agent Force. Bán cái mình đã dùng, không bán slide.; Người: đội nhỏ, mỗi người một vai rõ, việc lặp lại do máy làm. Phần tiền thì vẫn chạy bằng code tất định, AI không đụng vào.

## Mục tiêu của Linh

- Mục tiêu số 1 của engine (anh chốt 13:54 ngày 6/11): deploy một sản phẩm/dịch vụ mới nhanh nhất. Vì vậy tách từ đầu: sản phẩm mới = cài một bản mới từ code lõi + bật plugin + điền cấu hình + chọn template.

## Vì sao

- Hôm nay hệ thống của anh có 4 nguồn lực: các BU, đội agent LINHX, thương hiệu và quan hệ của anh, sản phẩm nhân rộng được (Định hướng 23/10).
- Phần lớn BU đang lỗ và nợ lương. Gốc là mô hình cũ và quản lý vận hành, tài chính yếu (Định hướng 23/10). Sheet Hoa 23/10: nợ 3.009 triệu, trong đó nợ lương 609, BHXH 302.
- Anh đang làm 80–100 giờ/tuần (anh nói 24/10). Nhiều việc ở các BU phải chờ anh, nên anh thành nút cổ chai của cả hệ.
- Mỗi BU tự làm lại cùng một việc: site, tìm lead, đề xuất, giao việc, thu tiền, báo cáo. Lead của bên này không sang được bên kia vì không có sổ khách chung.

## Không làm

- Engine không tự trả được nợ. Tiền vẫn đến từ bán và đòi tiền; kế hoạch 24/10 dành 30 giờ/tuần của anh riêng cho việc này.
- Engine không thay người bán. Hằng, Châu Đỗ, Thu Hiền, Vân Anh vẫn phải bán. Engine chỉ làm họ bán nhanh hơn và không bị rơi lead.
- Engine chưa phải sản phẩm để bán ra ngoài. Chỉ bán phần đã chạy thật trong hệ.

## Phản biện

-
  - ai: Công Báo (cãi ngược)
  - y: Bản 'khi đủ' ghi 30 DN có agent, còn kế hoạch 24/10 chỉ cam kết 4 DN vào 30/6/2027. Nếu đọc nhầm trần lý thuyết thành cam kết thì sẽ build quá tay. Đề xuất: mỗi đơn vị giữ hai cột, 'khi đủ' và 'cam kết'.
-
  - ai: Công Báo (cãi ngược)
  - y: Dựng nền trước khi có tiền là rủi ro kinh điển: Gartner dự báo hơn 40% dự án agentic bị huỷ trước 2027 (nguồn trong Định hướng 23/10). Engine chỉ đáng làm khi mỗi chặng đều phục vụ một khoản tiền đang về, ví dụ CSMO 18/11, đơn báo cáo, lớp corp.
-
  - ai: Dương Tiễn (QC)
  - y: Một site lõi chung nghĩa là một điểm hỏng chung. Cần sao lưu hằng ngày, phân quyền theo đơn vị và nhật ký truy cập ngay từ đầu, vì dữ liệu cá nhân của mọi BU nằm chung một chỗ.
-
  - ai: Dương Tiễn (QC)
  - y: Rủi ro người lớn hơn rủi ro máy: Minh Hiền nghỉ từ T01, Hằng đang quá tải (Kế hoạch 24/10). Máy chạy mà không có người bán thì Unikon và Event vẫn đứng.
-
  - ai: Khương Tử Nha (chốt)
  - y: Hướng đúng. Đo engine bằng giờ của anh và tiền về, không đo bằng số module. Chặng nào không làm giảm giờ anh hoặc tăng tiền về thì dời lại.

## Câu hỏi chờ Linh

- Vision một câu ở trên có đúng điều anh muốn không?
- Số đo chính là thời gian từ ý tới đơn đầu tiên, số đo phụ là giờ/tuần của anh (đề xuất ≤ 40 giờ). Anh đồng ý không?
- Mỗi đơn vị có cần hai cột 'khi đủ' và 'cam kết' không, để khỏi build quá tay?
- Đơn vị nào anh không muốn đưa vào engine?

## Đích 30/6/2027 theo mảng

-
  - ds:
    - **Course OS (lớp corp)**
      - Đích: Mọi lớp corp đi qua Course OS: nhận đề tới bộ đã duyệt ≤ 4 giờ công của anh; Điểm học viên ≥ 4,5/5; ≥ 60% còn dùng một workflow sau 30 ngày; Báo cáo HR sau 30 ngày tự sinh, anh chỉ duyệt; 6 trợ giảng dạy được bằng bộ có sẵn
    - **cungai + CLB Cùng AI**
      - Đích: ≥ 300 học viên cũ vào Zalo OA, ≥ 40% hoạt động mỗi tuần; ≥ 1.000 thành viên mới qua freebie và khoá miễn phí; ≥ 5% mua premium hoặc khoá; 2 tổ chức đặt chương trình AI champion; máy chạy ≥ 80% nội dung, anh ≤ 2 giờ/tuần
    - **Sakedemy**
      - Đích: Một mã số thuế xuất mọi hoá đơn đào tạo EDU; ≥ 3 khoá e-learning đang bán; ≥ 10% người học thử ở cungai sang mua; Nợ Sake có lộ trình về 0; nhánh học đường chỉ mở nếu qua cổng 5 cuộc gọi
    - **Agent Force (ifAgent)**
      - Đích: 30 doanh nghiệp có agent chạy thật, 15 trả theo tháng, tiền lặp lại ≥ 50%; 6 agent mẫu theo ngành, khách thứ hai cùng ngành chạy trong 7 ngày; 6 FDE tự dẫn dự án, anh ≤ 20% giờ triển khai; 200 lead doanh nghiệp/tháng; 15 case có số
    - **BespokeAI và xưởng agent tại chỗ**
      - Đích: (giả thuyết) ≥ 3 hợp đồng trao tay có phí bảo trì tháng; (giả thuyết) ≥ 1 khách thuê hoặc cài xưởng agent tại chỗ
    - **Expert OS (anh và mạng chuyên gia)**
      - Đích: Brand Truth từ 39,7 lên ≥ 75; một chức danh thống nhất; Show 12–16 tập; bản thảo sách 1 đã gửi nhà xuất bản; 4 chủ đề có hồ sơ sống; 5–10 hồ sơ chuyên gia chạy, ≥ 3 khách trả gói tháng; ≥ 5 lời mời/tháng; anh ≤ 3 giờ/tuần
    - **Đội máy của anh (xưởng thợ, bàn điều hành, sổ tay skill)**
      - Đích: (giả thuyết) mọi việc lặp lại đi qua hàng việc, có mã job và người duyệt; (giả thuyết) anh duyệt ≤ 30 phút/ngày trên một bàn; mỗi đêm ≥ 4 thợ chạy song song
  - Nhóm: LINHX (vòng trong)
-
  - ds:
    - **Chung cho 4 BU B2B (BU OS)**
      - Đích: Mỗi BU có site + 1 freebie đang chạy; AI nhắc tên ở ≥ 1/3 câu hỏi của cụm từ mình; ≥ 20% lead đến từ kênh của mình; từ đề bài tới bản nháp proposal ≤ 1 ngày; 100% job ra case trong 7 ngày
    - **Unikon**
      - Đích: ≥ 15 agency từng gửi brief, 4 job/tháng; ≥ 3 brand trả Brand kit theo tháng, ≥ 20% doanh thu; BTMH ≤ 30% doanh thu; QR phygital bán được cho khách thứ hai; mọi job có giá sàn và biên lãi
    - **ifAgent Event**
      - Đích: ≥ 2 job may đo và ≥ 4 sự kiện preset mỗi tháng; 100% sự kiện có báo cáo số đo trong 24 giờ; ≥ 20% lead từ SEO/GEO; ≥ 2 BU khác đã dùng module sự kiện trong việc thật
    - **TUVA**
      - Đích: ≥ 2 đề xuất tài trợ có hạng mục Decent AI được duyệt; ≥ 2 lớp Decent AI; Radar: ≥ 2 hồ sơ nộp/tháng, ≥ 1 hồ sơ đậu; Internship 3 trường, ≥ 15 sinh viên
    - **Listening Vietnam**
      - Đích: 2 báo cáo phát hành (AI ứng dụng, Người cao tuổi), ≥ 1 bên trả tiền
    - **URAH**
      - Đích: Phí nội bộ bù ≥ 70% chi; ≥ 90% giờ sản xuất gắn mã job; Video AI ≥ 2 job/tháng, không đạt thì đóng nhánh từ 31/3/2027
    - **15 site thương hiệu khác**
      - Đích: Giữ tĩnh trên khuôn chung; site nào 6 tháng không ra lead thì đóng
  - Nhóm: BU (vòng giữa)
-
  - ds:
    - **Chiêm Tinh Số**
      - Đích: (giả thuyết) thanh toán và đơn đã chạy trên engine; calc-service mở mã đúng hạn AGPL; (giả thuyết) đơn quà Tết doanh nghiệp chuyển sang Radar; là mẫu số 0 của template Báo cáo
    - **OPC tiếp theo**
      - Đích: (giả thuyết) ≥ 1 OPC thứ hai lên từ template Báo cáo hoặc Công cụ trong ≤ 30 phiếu, đo được thời gian golive
    - **Tung ta tung tăng**
      - Đích: Mùa lễ hội 20/11–10/12 chạy thử Hà Nội; (giả thuyết) tới 6/2027 có thành phố thứ hai, đủ điều kiện đóng template Theo nơi
    - **aicontent.vn**
      - Đích: Chờ anh: giữ tên miền để nộp gói startup, hay mở lại thành công cụ tự phục vụ
    - **VWAI, Platform 333, CafeBiz, trợ lý Zalo chị Hương**
      - Đích: Mỗi job đi qua template Job dựng: mã job, nghiệm thu, bàn giao, case trong 7 ngày; (giả thuyết) ≥ 1 job thành agent mẫu hoặc sản phẩm bán lại
    - **Agent RM ngân hàng (chị Thuỷ)**
      - Đích: Ra mắt ở event cuối tháng 11, rồi thành agent mẫu ngành ngân hàng của Agent Force
    - **Research agent (anh Dũng)**
      - Đích: Trở thành máy Research dùng chung của cả hệ, bán qua AIX
    - **Persona khảo sát giả lập**
      - Đích: Thành sản phẩm khảo sát ảo bán trên template Báo cáo
    - **Sân khấu 3D, Đi Chùa Online**
      - Đích: Giữ thử nhỏ trên module nhân vật ảo; chỉ lớn khi có số
    - **Gold radar**
      - Đích: Đề xuất đổi: báo cáo ngành vàng + agent mẫu bán lẻ vàng (case BTMH), không làm hub thứ ba
    - **AIX viện AI ứng dụng**
      - Đích: Kênh đối tác bán lại Agent Force và khoá học, có ghi công
  - Nhóm: Dự án (vòng ngoài)

## Còn thiếu

- **Một người một hồ sơ**
  - Đạt bằng: linhx_id + site lõi chung
  - Vì sao: Cùng một người là khách CTS, học viên lớp corp VCB và người mời anh đi nói; không nhận ra thì không chuyển chéo được
- **Đồng ý dữ liệu**
  - Đạt bằng: linhx_consent
  - Vì sao: Lead CTS chuyển sang Unikon cần đồng ý mới. Căn cứ nay là Luật Bảo vệ dữ liệu cá nhân 2025 (hiệu lực 1/1/2026), không chỉ NĐ 13; em cần kiểm lại văn bản hướng dẫn
- **Gói và quyền dùng**
  - Đạt bằng: linhx_catalog
  - Vì sao: Freemium cungai, ghế lớp corp, tín dụng tool T1–T5, membership CLB đang mỗi nơi tự ghi
- **Hợp đồng, pháp lý**
  - Đạt bằng: linhx_legal + linhx_qc
  - Vì sao: Pilot 'không đạt không trả' cần điều khoản đo; Unikon và ifAgent là bên có liên quan; case AstraZeneca chưa xin phép; người ảo phải gắn nhãn theo Luật AI
- **Tiền nhiều pháp nhân**
  - Đạt bằng: linhx_finance
  - Vì sao: ifAgent, Unikon, TUVA, Sakedemy, URAH và cá nhân anh; phí nội bộ URAH; không biết job nào lãi khi chưa tính token và giờ người
- **Nhân sự và quyền**
  - Đạt bằng: linhx_people + quyền theo đơn vị
  - Vì sao: 6 trợ giảng, FDE, Ambassador, sinh viên, người vận hành 6 đơn vị; tài liệu ngân hàng chỉ người lớp đó được xem
- **Hỗ trợ sau bán**
  - Đạt bằng: linhx_support
  - Vì sao: BespokeAI thu bảo trì tháng nhưng chưa có chỗ nhận lỗi; CTS cần hoàn tiền
- **QC chung**
  - Đạt bằng: linhx_qc
  - Vì sao: Mỗi đơn vị tự kiểm; Dương Tiễn mới chỉ ở trang
- **Bảo mật dữ liệu khách**
  - Đạt bằng: site riêng khi cần, thợ cách ly theo việc, bí mật ngoài repo
  - Vì sao: Dược, ngân hàng ngại đưa dữ liệu; thợ chạy trên máy cty; tài khoản AI của khách
- **Đối tác, giới thiệu**
  - Đạt bằng: linhx_partner
  - Vì sao: Chị Hương, AIX, Unikon bán lại, Spiderum, KOC đều chưa có chỗ ghi công
- **Lịch, sự kiện offline**
  - Đạt bằng: linhx_booking + linhx_event dùng chung
  - Vì sao: Lớp corp, industry sharing, show ghi hình, lịch nói của anh, coaching tháng
- **Đa ngôn ngữ**
  - Đạt bằng: trường dịch trong content, catalog, report
  - Vì sao: TUVA viết cho nhà tài trợ bằng tiếng Anh; Listening bán cho brand ngoại; Việt hoá theo phút cho FDI (LAB074)
- **Kho tài sản, nhận diện**
  - Đạt bằng: linhx_asset + linhx_brand
  - Vì sao: Học liệu 252 MB rải rác; Brand kit Unikon; slide phải đúng brand
- **Agent sau khi giao**
  - Đạt bằng: linhx_agent
  - Vì sao: 15 khách thuê tháng cần giám sát agent sống, chi phí, lỗi

## Điểm vênh

- Bản 13:00 6/11 đề xuất một site lõi chung. Anh chốt (13:55): tách tất cả từ đầu theo cơ chế WordPress, mỗi đơn vị một bản cài, chung code lõi + cổng danh tính linhx_id. Khớp lại hướng 5/11.
- Gold radar là content hub ngành vàng, trái luật chỉ 2 hub. Đề xuất đổi thành báo cáo ngành vàng + agent mẫu bán lẻ vàng.
- Agent RM ngân hàng, trợ lý chị Hương, research agent đang là dự án rời; nên vào thư viện agent mẫu của Agent Force.
- Live character, tác giả ảo, sân khấu 3D, Luna Mai là bốn chỗ của một module nhân vật ảo.
- CafeBiz toà soạn và show của anh trên CafeBiz là cùng một khách, cần một tài khoản tổ chức.
- linhx_quyen và linhx_kenh có trong bản 5/11 nhưng rớt khỏi bảng 10 lõi: em đưa lại thành linhx_catalog, linhx_chat.
- Giấy phép: Frappe MIT, nhưng Frappe CRM, Helpdesk, LMS là AGPL, ERPNext là GPL. Bán bản cài tại chỗ là phân phối, nên app LINHX tự viết; app AGPL chỉ dùng nguyên bản hoặc bỏ.
- Trong Frappe, một app chứa nhiều module. Không làm 35 app: gom 25 lõi + 3 công thức vào app linhx_core; mỗi module dọc là một app riêng để bán hoặc bật riêng.
- aicontent.vn: doc BU ghi không làm B2C, phần dự án ghi nếu mở lại. Chờ anh.
- BespokeAI ký bằng pháp nhân nào (Unikon 23/10 hay Agent Force 6/11). Listening VN dưới TUVA hay riêng. Chờ anh.

## Đã hỏi và chốt

- **Tách tất cả đúng chuẩn ngay từ đầu theo cơ chế WordPress: cùng code lõi, mỗi đơn vị một bản cài riêng (DB riêng): LINHX nội bộ, từng BU, từng OPC, Content hub?**
  - Chốt / đề xuất: ĐÃ CHỐT (anh 13:53–13:55 ngày 6/11). BU về bản chất giống WordPress multisite, nhưng giai đoạn này vẫn tách để học. Lúc đầu nhiều bản cài chung một server (Frappe multi-site, mỗi site một DB), lớn thì dời server, không sửa code. Nối nhau bằng cổng danh tính linhx_id (đăng nhập một lần + đồng ý dữ liệu) và API chuyển lead có ghi công. Sau này nếu các BU chia nhau quá nhiều khách thì cân nhắc gộp các BU thành một bản cài nhiều đơn vị.
- **Đêm nay mở Chặng 0 với 5 làn A–E?**
  - Chốt / đề xuất: Có, bắt đầu từ Làn A và B vì mọi thứ khác ghi vào đó.
- **Gom module vào app linhx_core, module dọc là app riêng?**
  - Chốt / đề xuất: Có. Tên module theo bảng trên.
- **Repo mới fyzdfyzd/linhx-engine?**
  - Chốt / đề xuất: Có. Anh tạo repo trống, em chuyển code 0.1 sang.

## Thứ tự đọc

- **1 · Vision và tác động (mục này)**
  - Đọc: Câu vision, 5 thay đổi, bảng từng đơn vị, phần tổng, phản biện
  - Cần trả lời: Đây có đúng cái đích anh muốn và đúng cách đo không?
- **2 · Cuối đường từng mảng**
  - Đọc: Mục 1 bên dưới
  - Cần trả lời: Số nào là cam kết, số nào chỉ là trần lý thuyết?
- **3 · Còn thiếu mảng gì, điểm vênh**
  - Đọc: Hai mục 'Còn thiếu' và 'Điểm vênh'
  - Cần trả lời: Mảng thiếu nào là thật, mảng nào bỏ được?
- **4 · Hệ thống cần xây**
  - Đọc: Mục 2, 2a–2d: 6 tầng, module, máy nền, template, 9 PROTO dùng lại
  - Cần trả lời: Một site lõi chung, app linhx_core, template theo hình dáng: anh đồng ý không?
- **5 · Lộ trình**
  - Đọc: Mục 3 và 4 (việc build, chỉ đọc sau khi chốt bước 1–4)
  - Cần trả lời: Chặng 0 có phục vụ một khoản tiền đang về không?

Liên quan: [[tong-quan]] [[kien-truc]] [[lo-trinh]] [[hop-nhat]]
