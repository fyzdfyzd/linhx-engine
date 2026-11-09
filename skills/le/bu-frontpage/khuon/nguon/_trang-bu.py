"""Nội dung các trang BU (ngoài 5 trang đầu). Chạy: python3 nguon/_trang-bu.py rồi python3 tao-trang.py"""
import json, pathlib
D = pathlib.Path(__file__).parent
P = []
def add(**k): P.append(k)

add(path="/giai-phap/", kenh="trang-giai-phap",
 title="Giải pháp AI tương tác cho sự kiện · IF Agent Event",
 desc="Ba giải pháp IF Agent dựng cho sự kiện: nhân vật AI biết nói tiếng Việt, AI Photobooth, minigame quét QR. So sánh để chọn đúng cái bạn cần.",
 vet=[("Giải pháp", "/giai-phap/")], h1="Ba giải pháp, chọn theo việc bạn cần khách làm",
 mo="Mỗi giải pháp giải một việc khác nhau ở sự kiện. Bảng dưới giúp bạn chọn nhanh; nhiều sự kiện ghép hai thứ với nhau.",
 than="""## Chọn theo việc
| Bạn cần khách | Nên chọn | Vì sao |
|---|---|---|
| Hiểu sản phẩm, hỏi gì cũng có người trả lời | [Nhân vật AI biết nói](/giai-phap/nhan-vat-ai/) | Trả lời bằng giọng nói, trong nội dung bạn duyệt, không mệt |
| Dừng lại, chụp, chia sẻ lên mạng | [AI Photobooth](/giai-phap/photobooth/) | Ảnh mang khung cảnh thương hiệu đi xa sau sự kiện |
| Cả hội trường cùng tham gia, để lại thông tin | [Minigame quét QR](/giai-phap/minigame/) | Chơi trên điện thoại, đua bảng xếp hạng, đổi thông tin lấy quà |

## Theo loại sự kiện
- [Hội chợ, triển lãm](/su-kien/hoi-cho-trien-lam/)
- [Ra mắt sản phẩm, sampling](/su-kien/ra-mat-san-pham/)
- [Hội nghị, summit](/su-kien/hoi-nghi/)

## Điểm chung của cả ba
- Chạy trên kiosk, màn LED hoặc điện thoại của khách, không cần cài ứng dụng.
- Khách chỉ để lại thông tin khi tự tick ô đồng ý.
- Báo cáo số đo trong 24 giờ sau sự kiện và danh sách khách đã đồng ý, xuất Excel.
- Chạy thử trên thiết bị thật trước ngày sự kiện.

## Chưa chắc chọn gì
Xem [các gói dựng sẵn](/goi/) đã ghép sẵn theo loại sự kiện, hoặc gửi brief để chúng tôi đề xuất.""")

add(path="/goi/", kenh="trang-goi",
 title="Gói dựng sẵn và cách tính giá · IF Agent Event",
 desc="Ba gói Gian hàng, Activation, Hội nghị: có gì, dựng mất bao lâu, giá phụ thuộc vào đâu. Gói may đo theo brief khi cần khác hẳn.",
 vet=[("Gói và giá", "/goi/")], h1="Gói dựng sẵn và cách tính giá",
 mo="Gói dựng sẵn đã có kịch bản, khung ảnh, luật chơi; chúng tôi thay logo, màu, quà của bạn nên dựng nhanh và giá rõ. Cần khác hẳn thì may đo theo brief.",
 ghi_chu="Giá và thời gian dựng của từng gói đang chờ IF Agent chốt. Trước khi có, mọi báo giá gửi trong 1 ngày làm việc sau khi nhận brief.",
 than="""## So sánh ba gói
| | Gian hàng | Activation | Hội nghị |
|---|---|---|---|
| Hợp với | Hội chợ, triển lãm, gian hàng TTTM | Ra mắt sản phẩm, sampling, roadshow | Hội nghị, summit, lễ trao giải |
| Giải pháp | AI Photobooth hoặc Minigame QR | Nhân vật AI và Photobooth hoặc Minigame | Nhân vật AI dẫn dắt, Minigame toàn hội trường, check-in QR |
| Thiết bị | 1 kiosk hoặc màn LED có sẵn | Kiosk nhân vật và điểm chụp | Màn LED sân khấu, kiosk sảnh |
| Người đứng máy | 1 | 1 đến 2 | 2 trở lên |
| Thời gian dựng | khoảng 5 ngày làm việc | khoảng 10 ngày làm việc | khoảng 15 ngày làm việc |
| Giá | báo trong 1 ngày | báo trong 1 ngày | báo trong 1 ngày |

## Gói nào cũng có
- Báo cáo số đo trong 24 giờ sau sự kiện.
- Danh sách khách đã đồng ý nhận tin, xuất Excel.
- Chạy thử trên thiết bị thật trước ngày sự kiện.
- Kịch bản, khung ảnh, luật chơi đổi theo thương hiệu.

## Giá phụ thuộc vào đâu
1. Số ngày chạy và số điểm đặt máy.
2. Độ riêng: dùng nhân vật, khung cảnh có sẵn hay dựng mới.
3. Thiết bị: dùng màn và kiosk của bạn hay của IF Agent.
4. Số người đứng máy và địa điểm (nội thành Hà Nội, TP.HCM hay tỉnh khác).
5. Quà và tích hợp gửi tin (Zalo, email, SMS).

## May đo
Khi bạn cần nhân vật mới hoàn toàn, trò chơi riêng, hoặc nối dữ liệu về hệ thống của bạn, chúng tôi làm đề xuất riêng kèm demo. Gửi brief càng sớm càng có nhiều lựa chọn.""")

add(path="/du-an/", kenh="trang-du-an",
 title="Dự án đã và sắp chạy · IF Agent Event",
 desc="Các sự kiện IF Agent chạy công nghệ tương tác. Mỗi dự án ghi rõ việc, giải pháp và số đo khi khách đồng ý công bố.",
 vet=[("Dự án", "/du-an/")], h1="Dự án",
 mo="Chúng tôi chỉ đăng một dự án khi có số đo thật và khách đồng ý công bố. Mỗi dự án ghi ba thứ: việc của sự kiện, giải pháp đã chạy, con số sau 24 giờ.",
 ghi_chu="Trang đang chờ số đo và ảnh thật. Phần dưới là khung, IF Agent điền khi có.",
 than="""## Sắp chạy
### CSMO Summit 2026
Hội nghị giám đốc marketing và bán hàng, 19–20/11/2026 tại Ascott Tây Hồ, Hà Nội, hơn 70 diễn giả và hơn 1.500 khách. IF Agent chạy công nghệ tương tác tại sự kiện. Số đo sẽ đăng trong 24 giờ sau khi sự kiện kết thúc.

## Khung mỗi dự án
| Mục | Ghi gì |
|---|---|
| Sự kiện | Tên, ngày, địa điểm, số khách |
| Việc cần làm | Mục tiêu của bên tổ chức, một câu |
| Giải pháp | Nhân vật AI, Photobooth, Minigame, ghép thế nào |
| Số đo | Lượt tương tác, lượt để lại liên hệ, giờ đông khách |
| Người xác nhận | Tên, chức vụ bên tổ chức, nếu đồng ý nêu tên |""")

EV = [
("/su-kien/hoi-cho-trien-lam/", "Hội chợ, triển lãm", "Công nghệ tương tác cho gian hàng hội chợ, triển lãm",
 "Giữa hàng trăm gian hàng, AI Photobooth và minigame kéo khách dừng lại, nhân vật AI giới thiệu sản phẩm, mỗi lượt chơi thành một liên hệ đã đồng ý.",
"""## Việc khó của gian hàng
- Khách đi qua nhanh, nhân viên không kịp giới thiệu từng người.
- Phát tờ rơi không biết ai quan tâm thật.
- Sau hội chợ không còn gì để chăm sóc tiếp.

## Ghép đề xuất
| Mục tiêu | Ghép |
|---|---|
| Đông người dừng lại | AI Photobooth với khung cảnh sản phẩm |
| Thu thông tin | Vòng quay quà sau khi khách để lại liên hệ |
| Giới thiệu sản phẩm kỹ thuật | Nhân vật AI trả lời câu hỏi thay nhân viên |

Gói phù hợp: [Gian hàng](/goi/). Thêm nhân vật AI thì lên [Activation](/goi/).

## Chuẩn bị
- Ổ điện và vị trí đặt kiosk trong mặt bằng gian hàng.
- Logo, màu, quà tặng, câu hỏi thường gặp về sản phẩm.
- Ngày dựng gian hàng để chạy thử trên mạng thật."""),
("/su-kien/ra-mat-san-pham/", "Ra mắt sản phẩm, sampling", "Công nghệ tương tác cho ra mắt sản phẩm và sampling",
 "Nhân vật AI làm đại sứ giới thiệu sản phẩm mới, photobooth đưa khách vào khung cảnh chiến dịch, quà và mã giảm giá gửi thẳng vào Zalo khách.",
"""## Việc khó của buổi ra mắt
- Thông điệp sản phẩm dài, khách chỉ đứng vài phút.
- Muốn khách nhớ sản phẩm và chia sẻ lên mạng.
- Cần biết ai muốn mua thử để chăm sóc ngay sau đó.

## Ghép đề xuất
| Mục tiêu | Ghép |
|---|---|
| Khách hiểu sản phẩm | Nhân vật AI nói theo kịch bản đã duyệt |
| Lan toả trên mạng | AI Photobooth khung cảnh chiến dịch |
| Chốt mua thử | Mã giảm giá gửi Zalo khi khách tự đồng ý |

Gói phù hợp: [Activation](/goi/).

## Chuẩn bị
- Tài liệu sản phẩm và các câu không được nói (về giá, so sánh đối thủ, công dụng).
- Chính sách quà và mã giảm giá.
- Hình chiến dịch để dựng khung cảnh photobooth."""),
("/su-kien/hoi-nghi/", "Hội nghị, summit", "Công nghệ tương tác cho hội nghị và summit",
 "Nhân vật AI dẫn dắt ở sân khấu hoặc sảnh, minigame cả hội trường chơi trên điện thoại, check-in và khảo sát qua QR, báo cáo cho ban tổ chức trong 24 giờ.",
"""## Việc khó của hội nghị
- Khách ngồi nghe lâu, khó giữ sự chú ý giữa các phiên.
- Nhà tài trợ cần chứng minh gian hàng có người ghé.
- Ban tổ chức cần số liệu tham dự nhanh sau sự kiện.

## Ghép đề xuất
| Mục tiêu | Ghép |
|---|---|
| Khuấy không khí giữa phiên | Minigame toàn hội trường, bảng xếp hạng màn LED |
| Đón khách, hướng dẫn | Nhân vật AI ở sảnh |
| Số liệu cho nhà tài trợ | Check-in QR theo gian, báo cáo 24 giờ |

Gói phù hợp: [Hội nghị](/goi/).

## Chuẩn bị
- Lịch phiên và khung giờ được chen minigame.
- Danh sách nhà tài trợ, gian hàng cần đặt mã check-in.
- Thông số màn LED và hệ thống âm thanh của địa điểm."""),
]
for path, ten, h1, mo, than in EV:
    add(path=path, kenh="trang-" + path.strip("/").split("/")[-1], loai="service",
        title=f"{ten} · IF Agent Event", desc=mo[:155],
        vet=[("Giải pháp", "/giai-phap/"), (ten, path)], h1=h1, mo=mo, than=than)

add(path="/agency/", kenh="trang-agency",
 title="Cho agency event · IF Agent Event",
 desc="Agency giữ khách hàng, IF Agent làm công nghệ tương tác và hỗ trợ pitch: demo mang logo khách của bạn, báo giá nhanh, đứng máy tại sự kiện.",
 vet=[("Cho agency", "/agency/")], h1="Cho agency: bạn giữ khách, chúng tôi lo công nghệ",
 mo="Agency gửi brief của khách hàng, IF Agent làm demo mang logo khách để bạn đi pitch, rồi dựng và đứng máy tại sự kiện dưới tên của bạn nếu cần.",
 than="""## Agency nhận được gì
- Demo chạy được với logo và màu của khách hàng, gửi kèm đề xuất.
- Báo giá trong 1 ngày làm việc để kịp đưa vào proposal.
- Tài liệu giải thích giải pháp không mang tên IF Agent nếu bạn muốn.
- Đội đứng máy mặc đồng phục của agency hoặc của sự kiện.

## Cách làm cùng nhau
1. Bạn gửi brief của khách và hạn pitch.
2. Chúng tôi gửi ý tưởng, demo, báo giá cho bạn.
3. Bạn pitch; trúng thì hai bên ký hợp đồng.
4. Dựng, chạy thử, vận hành; báo cáo 24 giờ gửi bạn trước để bạn chuyển khách.

## Quyền với dữ liệu
Dữ liệu người chơi thuộc thương hiệu tổ chức sự kiện. IF Agent xử lý theo hợp đồng và xoá theo thời hạn đã thống nhất.""",
 hoi_dap=[["Agency có được dùng demo cho nhiều khách không?", "Mỗi demo làm riêng cho một khách. Bạn cần cho khách khác thì gửi brief mới, chúng tôi đổi logo và kịch bản."],
          ["Có hoa hồng cho agency không?", "Trao đổi trực tiếp với bộ phận phát triển kinh doanh theo từng dự án."]])

add(path="/gioi-thieu/", kenh="trang-gioi-thieu",
 title="Giới thiệu IF Agent Event",
 desc="IF Agent dựng công nghệ AI tương tác cho sự kiện tại Việt Nam: nhân vật AI biết nói tiếng Việt, AI Photobooth, minigame QR, kèm số đo sau sự kiện.",
 vet=[("Giới thiệu", "/gioi-thieu/")], h1="IF Agent Event",
 mo="IF Agent dựng công nghệ AI tương tác cho sự kiện tại Việt Nam. Chúng tôi làm cho khách dừng lại, nói chuyện, chơi, và để lại thông tin một cách tự nguyện.",
 ghi_chu="Phần đội ngũ và pháp nhân chờ IF Agent cung cấp.",
 than="""## Chúng tôi tin ba điều
1. Khách dừng lại vì được tham gia, không vì được phát tờ rơi.
2. Dữ liệu khách chỉ có giá trị khi khách tự đồng ý.
3. Bên tổ chức cần số đo ngay sau sự kiện để báo cáo, không phải một tuần sau.

## Liên hệ phát triển kinh doanh
**Hằng Nguyễn**, Phát triển kinh doanh. Zalo [0904 106 143](https://zalo.me/0904106143), email [hangnt@ifagent.vn](mailto:hangnt@ifagent.vn).

## Hệ sinh thái
- [ifagent.net](https://ifagent.net): IF Agent.
- [demo.ifagent.net](https://demo.ifagent.net): thử nhân vật AI, photobooth, minigame.""")

add(path="/lien-he/", kenh="trang-lien-he", cta=False, form=True,
 title="Liên hệ và gửi brief · IF Agent Event",
 desc="Gửi brief sự kiện cho IF Agent, nhận ý tưởng, demo và báo giá trong 1 ngày làm việc. Hoặc nhắn Zalo 0904 106 143.",
 vet=[("Liên hệ", "/lien-he/")], h1="Gửi brief hoặc nói chuyện ngay",
 mo="Điền form bên dưới, chỗ nào chưa rõ cứ để trống. Cần gấp thì nhắn Zalo [0904 106 143](https://zalo.me/0904106143) hoặc email [hangnt@ifagent.vn](mailto:hangnt@ifagent.vn).",
 than="")

FAQ = [
 ["Dựng một nhân vật AI mất bao lâu?", "Tuỳ độ riêng của kịch bản, giọng và ngoại hình. Khi nhận brief, chúng tôi báo thời gian cụ thể cùng demo."],
 ["Giá một gói khoảng bao nhiêu?", "Tuỳ gói, số ngày chạy và số thiết bị. Gửi brief, bạn nhận báo giá kèm demo trong 1 ngày làm việc."],
 ["Sau sự kiện tôi nhận được gì?", "Trong 24 giờ: báo cáo số đo (lượt tương tác, lượt để lại liên hệ, giờ đông khách, ảnh được chia sẻ) và danh sách khách đã đồng ý nhận tin, xuất Excel."],
 ["Sự kiện ở hội trường sóng yếu thì sao?", "Chúng tôi khảo sát mạng tại địa điểm và mang thiết bị mạng dự phòng. Minigame QR chạy trên mạng di động của khách."],
 ["Dữ liệu khách tham dự thuộc về ai?", "Thuộc về thương hiệu tổ chức. Khách chỉ để lại thông tin khi tự đồng ý, ô đồng ý không bao giờ được tick sẵn. Ảnh và dữ liệu được xoá theo thời hạn hai bên thống nhất."],
 ["Agency có thể dùng dưới tên mình không?", "Có. Agency giữ quan hệ với khách hàng, IF Agent đứng sau làm công nghệ và hỗ trợ pitch."],
 ["Có cần cài ứng dụng không?", "Không. Khách quét mã QR và dùng trên trình duyệt điện thoại, hoặc dùng kiosk và màn LED tại chỗ."],
 ["Nhân vật AI có trả lời sai về sản phẩm không?", "Nhân vật chỉ trả lời trong nội dung bạn duyệt; câu hỏi ngoài phạm vi được chuyển sang mời gặp nhân viên. Chúng tôi chạy thử với câu hỏi khó trước sự kiện."],
 ["IF Agent làm sự kiện ở tỉnh được không?", "Được. Chi phí đi lại và lưu trú của đội đứng máy tính vào báo giá."],
 ["Đặt cọc thế nào?", "Gói dựng sẵn đặt cọc trước khi bắt đầu dựng; dự án may đo theo hợp đồng. Chi tiết ghi trong báo giá."],
]
add(path="/hoi-dap/", kenh="trang-hoi-dap",
 title="Hỏi đáp về công nghệ sự kiện · IF Agent Event",
 desc="Giá, thời gian dựng, mạng tại hội trường, dữ liệu khách, cách làm với agency: câu trả lời ngắn cho người tổ chức sự kiện.",
 vet=[("Hỏi đáp", "/hoi-dap/")], h1="Câu hỏi hay gặp",
 mo="Những câu bên tổ chức sự kiện và agency hỏi nhiều nhất trước khi gửi brief.", than="", hoi_dap=FAQ)

add(path="/cam-nang/", kenh="trang-cam-nang",
 title="Cẩm nang công nghệ sự kiện · IF Agent Event",
 desc="Bài viết cho người tổ chức sự kiện: chọn giải pháp tương tác AI, tính ngân sách, đo hiệu quả, xử lý dữ liệu khách đúng luật.",
 vet=[("Cẩm nang", "/cam-nang/")], h1="Cẩm nang công nghệ sự kiện",
 mo="Bài viết ngắn, thẳng vào việc, cho người tổ chức sự kiện và agency đang cân nhắc công nghệ tương tác.",
 than="""## Bài trụ
- [Công nghệ sự kiện: chọn giải pháp tương tác AI cho gian hàng, activation và hội nghị](/cong-nghe-su-kien/)

## Sắp đăng
- Đo hiệu quả gian hàng hội chợ bằng con số nào.
- Thu thông tin khách tại sự kiện đúng Nghị định 13/2023.
- Checklist kỹ thuật một tuần trước ngày sự kiện.
- Photobooth AI và photobooth thường khác nhau ở đâu.
- Chuẩn bị kịch bản cho nhân vật AI đại sứ thương hiệu.""")

add(path="/cam-on/", kenh="trang-cam-on", cta=False, cam_on=True, noindex=True,
 title="Đã nhận brief · IF Agent Event", desc="IF Agent đã nhận brief của bạn và sẽ liên hệ trong 1 ngày làm việc qua điện thoại, Zalo hoặc email.",
 vet=[("Đã nhận brief", "/cam-on/")], h1="Đã nhận brief của bạn",
 mo="Chúng tôi sẽ liên hệ trong 1 ngày làm việc qua điện thoại, Zalo hoặc email bạn để lại.",
 than="""## Tiếp theo
1. Bộ phận phát triển kinh doanh đọc brief và gọi lại để hỏi thêm nếu cần.
2. Bạn nhận một đến ba ý tưởng, demo với logo của bạn, báo giá và thời gian dựng.
3. Hai bên chốt, chúng tôi bắt đầu dựng và hẹn ngày chạy thử.

## Trong lúc chờ
- [Thử demo trên điện thoại](https://demo.ifagent.net/?kenh=cam-on)
- [Đọc cẩm nang công nghệ sự kiện](/cong-nghe-su-kien/)
- Gấp thì nhắn Zalo [0904 106 143](https://zalo.me/0904106143).""")

add(path="/mau-bao-cao/", kenh="trang-mau-bao-cao",
 title="Mẫu báo cáo số đo 24 giờ · IF Agent Event",
 desc="Sau mỗi sự kiện, bên tổ chức nhận báo cáo trong 24 giờ. Đây là các chỉ số có trong báo cáo, cách đo, và danh sách khách đã đồng ý đi kèm.",
 vet=[("Gói và giá", "/goi/"), ("Mẫu báo cáo 24 giờ", "/mau-bao-cao/")], h1="Báo cáo số đo trong 24 giờ sau sự kiện",
 mo="Trong 24 giờ sau khi sự kiện kết thúc, bạn nhận một báo cáo ngắn để gửi sếp hoặc khách hàng, và danh sách khách đã đồng ý nhận tin. Trang này cho bạn thấy trước báo cáo gồm những gì.",
 than="""## Trang 1: tóm tắt
| Chỉ số | Đo thế nào |
|---|---|
| Lượt tương tác | Mỗi cuộc trò chuyện với nhân vật AI, mỗi lượt chụp, mỗi lượt chơi tính một lần |
| Người tham gia | Đếm theo thiết bị hoặc số điện thoại, không đếm trùng |
| Lượt để lại liên hệ | Khách tự điền và tick ô đồng ý |
| Tỉ lệ để lại liên hệ | Lượt để lại liên hệ chia người tham gia |
| Giờ đông khách | Số lượt theo từng khung 30 phút |
| Ảnh được chia sẻ | Lượt tải ảnh photobooth và lượt bấm chia sẻ |

## Trang 2: theo giải pháp
- Nhân vật AI: số cuộc trò chuyện, độ dài trung bình, 10 câu khách hỏi nhiều nhất, câu hỏi ngoài kịch bản.
- AI Photobooth: lượt chụp, khung cảnh được chọn, lượt tải ảnh.
- Minigame: lượt chơi, điểm cao nhất, câu hỏi khó nhất, quà đã phát.

## Trang 3: việc nên làm tiếp
Ba gợi ý chăm sóc khách sau sự kiện dựa trên câu hỏi và lựa chọn của khách tại gian hàng.

## Đi kèm
- Danh sách khách đã đồng ý, xuất Excel: họ tên, điện thoại hoặc email, thời điểm đồng ý, câu trả lời khảo sát nếu có.
- Ảnh và dữ liệu thô lưu theo thời hạn trong hợp đồng, sau đó xoá.

Báo cáo không có con số nào chúng tôi không đo được. Chỉ số nào sự kiện không dùng thì bỏ khỏi báo cáo.""")

for i, p in enumerate(P):
    (D / f"{i + 6:02d}-{p['path'].strip('/').replace('/', '-')}.json").write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(P), "trang")
