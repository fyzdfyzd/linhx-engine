"""Nội dung các trang con TUVA. Chạy: python3 nguon/_trang-bu.py rồi python3 tao-trang.py
Không bịa: không giá, không số, không tên khách/đối tác (case UN Women, WWF, British Council chưa được phép nêu tên)."""
import json, pathlib
D = pathlib.Path(__file__).parent
P = []
def add(**k): P.append(k)

LIEN_HE_CHO = "Thông tin liên hệ công khai (email, điện thoại, địa chỉ) đang chờ TUVA xác nhận. Trong lúc chờ, bạn để lại thông tin ở form, chúng tôi liên hệ lại."

add(path="/giai-phap/", kenh="trang-dich-vu", loai="service",
 title="Dịch vụ truyền thông và AI cho NGO · TUVA",
 desc="Ba việc TUVA làm cùng NGO và dự án phát triển: AI cho tổ chức (Decent AI), truyền thông dự án theo lĩnh vực, lắng nghe dữ liệu mạng xã hội.",
 vet=[("Dịch vụ", "/giai-phap/")], h1="Dịch vụ của TUVA cho tổ chức phát triển",
 mo="Ba nhóm việc, chọn theo điều dự án của bạn cần. Nhiều dự án ghép hai nhóm với nhau, ví dụ lắng nghe dữ liệu trước rồi mới làm chiến dịch.",
 than="""## Chọn theo việc
| Bạn cần | Nên chọn | Bạn nhận được |
|---|---|---|
| Đội ngũ dùng AI an toàn, đúng việc | [AI cho tổ chức phát triển](/giai-phap/ai-cho-ngo/) | Tập huấn theo vai trò, bộ quy tắc AI, quy trình duyệt, câu lệnh mẫu |
| Thông điệp dự án tới đúng nhóm công chúng | [Truyền thông dự án và chiến dịch](/giai-phap/truyen-thong-du-an/) | Chiến lược, nội dung đa kênh, sự kiện, tập huấn truyền thông cho đối tác |
| Biết công chúng đang nói gì về vấn đề | [Lắng nghe dữ liệu mạng xã hội](/giai-phap/lang-nghe-du-lieu/) | Báo cáo dữ liệu, thông điệp gợi ý, chỉ số theo dõi |

## Cả ba đều viết được vào đề xuất tài trợ
Mỗi nhóm việc có sẵn cách viết cho concept note, dòng ngân sách và chỉ số logframe. Xem [cách TUVA viết hạng mục cho đề xuất tài trợ](/de-xuat-tai-tro/).

## Chưa chắc bắt đầu từ đâu
[Tự chấm mức sẵn sàng AI của tổ chức](/tu-cham-ai/) trong ba phút, hoặc gửi thông tin dự án để chúng tôi gợi ý.""")

add(path="/giai-phap/ai-cho-ngo/", kenh="trang-ai-cho-ngo", loai="service",
 title="AI cho NGO: tập huấn, quy tắc và quy trình · TUVA",
 desc="Chương trình Decent AI của TUVA giúp NGO ở Việt Nam dùng AI an toàn: tập huấn theo vai trò, bộ quy tắc AI, quy trình duyệt nội dung, câu lệnh mẫu.",
 vet=[("Dịch vụ", "/giai-phap/"), ("AI cho NGO", "/giai-phap/ai-cho-ngo/")], h1="AI cho NGO, dùng an toàn từ tuần đầu tiên",
 mo="Nhiều cán bộ dự án đã tự dùng AI để viết báo cáo hay dịch tài liệu. Việc của tổ chức là biến thói quen lẻ tẻ đó thành cách làm chung, an toàn với dữ liệu người thụ hưởng và đúng yêu cầu của nhà tài trợ.",
 than="""## Chương trình gồm những gì
### Tập huấn theo vai trò
Lãnh đạo học cách đặt quy tắc và quản rủi ro. Cán bộ chương trình học dùng AI để tóm tắt, viết, dịch, chuẩn bị đề xuất. Người làm truyền thông học lên ý tưởng và kiểm chứng. Người làm MEL học phân tích phản hồi cộng đồng đã ẩn danh. Bài tập làm trên tài liệu của chính dự án, đã bỏ thông tin cá nhân.

### Bộ quy tắc AI và quy trình duyệt
Một bộ quy tắc ngắn, sửa theo tên và quy trình của tổ chức: dữ liệu nào không đưa vào AI, công cụ nào được dùng, ai duyệt nội dung nào, ghi nhãn ra sao. [Xem bộ quy tắc AI an toàn](/bo-quy-tac-ai/).

### Câu lệnh mẫu cho việc của NGO
Bộ câu lệnh cho những việc lặp lại: tóm tắt báo cáo, viết bản tin dự án, soạn khung concept note, dịch tài liệu chuyên ngành, phân nhóm phản hồi khảo sát.

## Decent AI nghĩa là gì
Chúng tôi gọi cách làm này là [Decent AI](/decent-ai/): AI tử tế, có quy tắc, có người chịu trách nhiệm, bảo vệ người yếu thế, và để con người giữ quyền quyết định.

## Đưa vào đề xuất tài trợ
Hợp phần năng lực AI có thể thành một đầu ra riêng trong logframe, với chỉ số như số nhân viên được tập huấn, tỉ lệ làm theo quy tắc, số quy trình có AI hỗ trợ. [Xem cách viết](/de-xuat-tai-tro/).""",
 hoi_dap=[["Tổ chức nhỏ, chưa ai biết dùng AI thì bắt đầu từ đâu?", "Bắt đầu từ bộ quy tắc và một buổi tập huấn ngắn cho cả tổ chức. Làm bài tự chấm mức sẵn sàng AI trên trang này để biết nên ưu tiên việc gì trước."],
          ["Có phải mua phần mềm đắt tiền không?", "Không bắt buộc. Phần lớn việc dùng được với công cụ phổ biến, miễn là dùng bằng tài khoản của tổ chức và theo đúng quy tắc dữ liệu."],
          ["Tập huấn bằng tiếng Việt hay tiếng Anh?", "Tiếng Việt là chính. Tài liệu và câu lệnh mẫu có thể song ngữ cho tổ chức làm việc với nhà tài trợ nước ngoài."]])

add(path="/giai-phap/truyen-thong-du-an/", kenh="trang-truyen-thong", loai="service",
 title="Truyền thông dự án và chiến dịch cho NGO · TUVA",
 desc="TUVA làm chiến lược, thông điệp, nội dung đa kênh, sự kiện và tập huấn truyền thông cho dự án phát triển, theo từng lĩnh vực và nhóm công chúng.",
 vet=[("Dịch vụ", "/giai-phap/"), ("Truyền thông dự án", "/giai-phap/truyen-thong-du-an/")], h1="Truyền thông dự án và chiến dịch theo lĩnh vực",
 mo="Tên TUVA lấy từ chiếc tù và, thứ được thổi lên để gọi cả làng. Việc của chúng tôi là giúp câu chuyện của dự án phát triển đến được với nhiều người hơn, thay vì quanh quẩn trong một vòng nhỏ.",
 than="""## Chúng tôi làm gì
- **Chiến lược và thông điệp**: ai cần nghe, họ đang nghĩ gì, nói gì để họ đổi cách nghĩ hoặc cách làm.
- **Nội dung đa kênh**: bài mạng xã hội, video, đồ hoạ, ấn phẩm, sách, báo cáo dạng dễ đọc.
- **Sự kiện và triển lãm**: hội thảo, triển lãm tương tác, ra mắt báo cáo.
- **Tập huấn truyền thông** cho cán bộ dự án và đối tác địa phương.

## Theo lĩnh vực
Mỗi lĩnh vực có công chúng và độ nhạy riêng. Xem [các lĩnh vực TUVA đã làm truyền thông](/linh-vuc/).

## Nguyên tắc
- Không bi thảm hoá người thụ hưởng, không dùng ảnh khi chưa có đồng ý.
- Số liệu nào cũng có nguồn.
- Nội dung có AI hỗ trợ được người phụ trách duyệt và ghi nhãn.""")

add(path="/giai-phap/lang-nghe-du-lieu/", kenh="trang-lang-nghe", loai="service",
 title="Lắng nghe dữ liệu mạng xã hội cho dự án · TUVA",
 desc="Qua Listening Vietnam, TUVA theo dõi thảo luận trên mạng xã hội về vấn đề dự án theo đuổi, rồi chuyển dữ liệu thành báo cáo và thông điệp.",
 vet=[("Dịch vụ", "/giai-phap/"), ("Lắng nghe dữ liệu", "/giai-phap/lang-nghe-du-lieu/")], h1="Lắng nghe dữ liệu mạng xã hội cho dự án phát triển",
 mo="Trước khi nói, hãy nghe. Lắng nghe mạng xã hội cho biết công chúng đang nói gì, bằng từ ngữ nào, về vấn đề dự án theo đuổi.",
 than="""## Dùng vào việc gì
- **Trước dự án**: hiểu bối cảnh, viết phần phân tích vấn đề cho đề xuất tài trợ.
- **Trong chiến dịch**: biết thông điệp nào được bàn tới, thông điệp nào bị hiểu sai.
- **Đánh giá**: có số liệu thảo luận trước và sau để đưa vào báo cáo cho nhà tài trợ.

## Bạn nhận được
Báo cáo dữ liệu ngắn, dễ đọc, có biểu đồ và ví dụ thảo luận đã ẩn danh, kèm gợi ý thông điệp và chỉ số theo dõi cho logframe.

## Listening Vietnam
Listening Vietnam là sáng kiến lắng nghe dữ liệu mạng xã hội của TUVA, có trang riêng tại [listening.vn](https://listening.vn/?kenh=tuva-lang-nghe&utm_source=tuva.work&utm_medium=referral&utm_campaign=lang-nghe).""")

add(path="/de-xuat-tai-tro/", kenh="trang-de-xuat", loai="service", form=True,
 title="Viết hạng mục truyền thông và AI cho đề xuất tài trợ · TUVA",
 desc="TUVA viết hợp phần truyền thông và năng lực AI cho đề xuất tài trợ của NGO: concept note, dòng ngân sách, đầu ra và chỉ số logframe.",
 vet=[("Đề xuất tài trợ", "/de-xuat-tai-tro/")], h1="Hạng mục truyền thông và AI trong đề xuất tài trợ",
 mo="Phần truyền thông và AI thường được viết vội vào những ngày cuối, nên mỏng và khó được duyệt. Chúng tôi viết phần này cùng cán bộ chương trình, đúng ba chỗ hội đồng xét duyệt sẽ đọc.",
 than="""## Ba chỗ chúng tôi viết
| Phần | TUVA viết gì | Bạn cần đưa |
|---|---|---|
| Concept note | Vì sao cần hợp phần, ai hưởng lợi, rủi ro và cách xử lý | Mục tiêu dự án, khung của nhà tài trợ |
| Ngân sách | Dòng chi theo hạng mục, đơn vị tính, số lượng | Quy định chi phí của nhà tài trợ, đơn giá nội bộ |
| Logframe | Đầu ra, chỉ số đo được, nguồn kiểm chứng | Mục tiêu chung, khung logframe của dự án |

## Thanh toán theo đợt tài trợ
Khi đề xuất được duyệt, hai bên ký hợp đồng đúng phạm vi đã viết. Thanh toán theo các đợt giải ngân của hợp đồng tài trợ, bằng VND hoặc ngoại tệ theo hợp đồng.

## Làm bằng tiếng Anh
Concept note, ngân sách và logframe có thể viết bằng tiếng Anh hoặc song ngữ. Đọc [bản tiếng Anh của trang chủ](/en/).

## Gửi thông tin đề xuất
Điền form dưới đây, càng sớm trước hạn nộp càng có nhiều lựa chọn.""",
 cta=False)

add(path="/bo-quy-tac-ai/", kenh="trang-bo-quy-tac", form_tai=True,
 title="Bộ quy tắc AI an toàn cho tổ chức, tải miễn phí · TUVA",
 desc="Bộ quy tắc AI ngắn cho NGO và tổ chức phát triển: dữ liệu không đưa vào AI, ai duyệt, kiểm chứng, ghi nhãn, công cụ được phép. Nhận qua email.",
 vet=[("Bộ quy tắc AI", "/bo-quy-tac-ai/")], h1="Bộ quy tắc AI an toàn cho tổ chức",
 mo="Một bộ quy tắc ngắn để cả tổ chức dùng AI giống nhau. Sửa lại theo tên và quy trình của bạn là dùng được.",
 ghi_chu="Bản PDF đang được hoàn thiện. Để lại email, chúng tôi gửi ngay khi có bản đầu tiên.",
 than="""## Bộ quy tắc gồm
1. **Dữ liệu nào không đưa vào AI**: tên, ảnh, hồ sơ, câu chuyện cá nhân của người thụ hưởng và đối tác.
2. **Công cụ được phép**: danh sách công cụ, dùng bằng tài khoản của tổ chức.
3. **Ai duyệt, duyệt gì**: người chịu trách nhiệm cho từng loại nội dung có AI hỗ trợ.
4. **Kiểm chứng**: kiểm số liệu, trích dẫn do AI đưa ra trước khi dùng.
5. **Ghi nhãn**: câu ghi nhãn cho ảnh và bài viết có AI hỗ trợ.
6. **Khi có sự cố**: báo cho ai, làm gì khi dữ liệu bị đưa nhầm vào công cụ AI.

## Trước khi tải
[Tự chấm mức sẵn sàng AI của tổ chức](/tu-cham-ai/) để biết nên sửa quy tắc nào trước.""",
 cta=False)

add(path="/tu-cham-ai/", kenh="trang-tu-cham", cham=True, form_tai=True,
 title="Tự chấm mức sẵn sàng AI của NGO trong 3 phút · TUVA",
 desc="Mười câu hỏi giúp NGO và tổ chức phát triển biết mình đang ở mức nào khi dùng AI, kèm ba gợi ý nên làm trước. Kết quả hiện ngay.",
 vet=[("Tự chấm mức sẵn sàng AI", "/tu-cham-ai/")], h1="Tự chấm mức sẵn sàng AI của tổ chức",
 mo="Mười câu, mỗi câu ba lựa chọn. Kết quả hiện ngay trên trang, không cần để lại thông tin.",
 than="""## Bốn mức
- **Mức 1 · Bắt đầu**: chưa có quy tắc, nhân viên tự dùng AI.
- **Mức 2 · Thử nghiệm**: đã có người dùng, mỗi người một kiểu.
- **Mức 3 · Có nề nếp**: có quy tắc và người duyệt.
- **Mức 4 · Sẵn sàng mở rộng**: AI đã có chỗ trong chương trình và đề xuất tài trợ.

## Nhận bản đầy đủ
Để lại email, bạn nhận bộ quy tắc AI và gợi ý cho từng câu theo kết quả của mình.""",
 cta=False)

add(path="/linh-vuc/", kenh="trang-linh-vuc",
 title="Lĩnh vực TUVA làm truyền thông và AI · TUVA",
 desc="Các lĩnh vực TUVA đã làm truyền thông cho dự án phát triển ở Việt Nam: bình đẳng giới, di sản và giáo dục, y tế, di cư lao động, người cao tuổi.",
 vet=[("Lĩnh vực", "/linh-vuc/")], h1="Lĩnh vực chúng tôi làm truyền thông",
 mo="Mỗi lĩnh vực có công chúng, từ ngữ và độ nhạy riêng. Đây là những lĩnh vực TUVA đã làm truyền thông cho các dự án phát triển.",
 ghi_chu="Chúng tôi chỉ nêu tên dự án, tổ chức đối tác và số liệu khi đối tác đồng ý công bố. Phần case theo từng lĩnh vực sẽ được bổ sung khi có đồng ý.",
 than="""## Bình đẳng giới
Chiến dịch cho người trẻ, nội dung mạng xã hội, triển lãm tương tác, báo cáo phân tích quảng cáo qua lăng kính giới.

## Di sản, văn hoá, giáo dục
Kể chuyện di sản cho công chúng trẻ, tài liệu truyền thông cho chương trình giáo dục.

## Y tế, sức khoẻ
Thông điệp sức khoẻ cộng đồng, tài liệu dễ hiểu cho người dân.

## Di cư, lao động
Lắng nghe mạng xã hội về di cư, nội dung cho người lao động.

## Người cao tuổi
Truyền thông cho chương trình chăm sóc và hoà nhập người cao tuổi.

## Lĩnh vực của bạn chưa có ở đây
Gửi thông tin dự án, chúng tôi trả lời thẳng là có làm được hay không.""")

add(path="/gioi-thieu/", kenh="trang-gioi-thieu",
 title="Giới thiệu TUVA Communication, Reaching out · TUVA",
 desc="TUVA Communication là đơn vị truyền thông đồng hành cùng các dự án xã hội ở Việt Nam, nay là đối tác AI và truyền thông cho NGO.",
 vet=[("Giới thiệu", "/gioi-thieu/")], h1="TUVA Communication",
 mo="Ăn cơm nhà, vác tù và hàng tổng. TUVA lấy tên từ câu thành ngữ dành cho những người chuyên lo việc chung, và từ chiếc tù và làm bằng vỏ ốc, thổi lên để gọi cả làng.",
 ghi_chu="Thông tin pháp nhân, năm thành lập và đội ngũ đầy đủ đang chờ TUVA xác nhận.",
 than="""## Vì sao có TUVA
Tin giải trí, tin giật gân phủ sóng rất dễ. Thông điệp về phát triển xã hội thì thường quanh quẩn trong một vòng nhỏ. TUVA muốn những câu chuyện đó đến được với nhiều người hơn. Đó cũng là nghĩa của dòng chữ REACHING OUT trên logo.

## Bây giờ chúng tôi làm gì
Truyền thông dự án, lắng nghe dữ liệu mạng xã hội qua Listening Vietnam, và giúp các tổ chức phát triển dùng AI một cách tử tế qua chương trình Decent AI.

## Người bạn sẽ làm việc cùng
Thu Hiền và Thu Hà phụ trách trao đổi dự án với các tổ chức.

## Giá trị
Tự do, bình đẳng, bao dung.""")

add(path="/lien-he/", kenh="trang-lien-he", form=True,
 title="Liên hệ TUVA, trao đổi một dự án hoặc đề xuất · TUVA",
 desc="Gửi thông tin dự án hoặc đề xuất tài trợ cho TUVA: tổ chức, lĩnh vực, nhà tài trợ, hạn nộp. Chúng tôi liên hệ lại trong 1 ngày làm việc.",
 vet=[("Liên hệ", "/lien-he/")], h1="Trao đổi một dự án hoặc đề xuất",
 mo="Điền những gì bạn đang có, chỗ nào chưa rõ cứ để trống. Thu Hiền hoặc Thu Hà sẽ liên hệ lại.",
 ghi_chu=LIEN_HE_CHO, than="", cta=False)

FAQ = [
 ["Chi phí làm việc với TUVA tính thế nào?", "Chi phí tính theo từng hạng mục trong đề xuất tài trợ, theo đơn giá và quy định của nhà tài trợ. Chúng tôi lập khung ngân sách cùng bạn trước hạn nộp, thanh toán theo các đợt giải ngân của hợp đồng tài trợ."],
 ["Decent AI là gì?", "Decent AI là cách TUVA gọi việc dùng AI tử tế trong tổ chức phát triển: có quy tắc, có người chịu trách nhiệm, bảo vệ dữ liệu người thụ hưởng, ghi nhãn nội dung có AI hỗ trợ, giúp đội ngũ làm việc tốt hơn và để con người giữ quyền quyết định."],
 ["Dữ liệu của người thụ hưởng có bị đưa vào công cụ AI không?", "Không. Tên, ảnh, hồ sơ và câu chuyện cá nhân của người thụ hưởng không đưa vào công cụ AI công cộng. Bộ quy tắc AI của TUVA ghi rõ dữ liệu nào được dùng, dữ liệu nào phải ẩn danh, và ai duyệt."],
 ["TUVA có làm việc và viết đề xuất bằng tiếng Anh không?", "Có. Concept note, ngân sách và logframe có thể viết bằng tiếng Anh hoặc song ngữ theo yêu cầu của nhà tài trợ."],
 ["Hạn nộp đề xuất đã gần thì còn kịp không?", "Bạn cứ gửi kèm hạn nộp. Chúng tôi trả lời ngay là kịp làm phần nào: chỉ viết hạng mục truyền thông và AI, hay cùng làm cả concept note."],
 ["Listening Vietnam là gì?", "Listening Vietnam là sáng kiến lắng nghe dữ liệu mạng xã hội của TUVA: theo dõi người dùng mạng đang nói gì về một vấn đề xã hội, rồi biến dữ liệu đó thành báo cáo và thông điệp cho dự án."],
 ["TUVA có nêu tên các tổ chức đã làm cùng không?", "Chỉ khi tổ chức đó đồng ý công bố. Khi trao đổi riêng về một dự án, chúng tôi chia sẻ kinh nghiệm theo lĩnh vực."],
 ["Bộ quy tắc AI có mất phí không?", "Không. Bạn để lại email để nhận bộ quy tắc và các bản cập nhật."],
 ["Tổ chức nhỏ có làm việc với TUVA được không?", "Được. Nhiều việc như tập huấn hay bộ quy tắc AI phù hợp cả với tổ chức vài người."],
 ["TUVA có làm việc ngoài Hà Nội không?", "Có. Tập huấn và trao đổi có thể làm trực tuyến hoặc tại địa phương nơi dự án triển khai."]]
add(path="/hoi-dap/", kenh="trang-hoi-dap",
 title="Câu hỏi hay gặp về AI và truyền thông cho NGO · TUVA",
 desc="Chi phí, dữ liệu người thụ hưởng, Decent AI, làm bằng tiếng Anh, hạn nộp đề xuất gần: câu trả lời cho những câu NGO hay hỏi TUVA.",
 vet=[("Hỏi đáp", "/hoi-dap/")], h1="Câu hỏi hay gặp",
 mo="Những câu cán bộ chương trình và lãnh đạo NGO hay hỏi chúng tôi trong lần trao đổi đầu tiên.", than="", hoi_dap=FAQ)

add(path="/cam-nang/", kenh="trang-cam-nang",
 title="Cẩm nang AI và truyền thông cho NGO · TUVA",
 desc="Bài viết của TUVA về AI cho NGO, Decent AI, truyền thông dự án và cách viết hạng mục truyền thông, AI vào đề xuất tài trợ.",
 vet=[("Cẩm nang", "/cam-nang/")], h1="Cẩm nang",
 mo="Bài viết ngắn cho cán bộ chương trình, người làm truyền thông và lãnh đạo tổ chức phát triển.",
 than="""## Bài trụ
- [AI cho NGO ở Việt Nam: bắt đầu từ đâu, tránh điều gì](/cam-nang/ai-cho-ngo/)
- [Decent AI: AI tử tế cho tổ chức phát triển](/decent-ai/)

## Công cụ
- [Tự chấm mức sẵn sàng AI của tổ chức](/tu-cham-ai/)
- [Bộ quy tắc AI an toàn cho tổ chức](/bo-quy-tac-ai/)
- [Viết hạng mục truyền thông và AI cho đề xuất tài trợ](/de-xuat-tai-tro/)""")

add(path="/chinh-sach-du-lieu/", kenh="trang-chinh-sach",
 title="Chính sách dữ liệu cá nhân · TUVA Communication",
 desc="TUVA thu thông tin gì qua các form trên tuva.work, dùng để làm gì, lưu bao lâu và bạn yêu cầu sửa, xoá như thế nào.",
 vet=[("Chính sách dữ liệu", "/chinh-sach-du-lieu/")], h1="Chính sách dữ liệu cá nhân",
 ghi_chu="Bản nháp, chờ TUVA và pháp chế duyệt theo Nghị định 13/2023/NĐ-CP. Tên pháp nhân và đầu mối liên hệ sẽ được điền khi có xác nhận.",
 than="""## Chúng tôi thu gì
Họ tên, tổ chức, vai trò, điện thoại, email, thông tin dự án bạn tự điền ở form; kết quả tự chấm nếu bạn gửi kèm; trang bạn đến từ đâu (mã kênh, utm).

## Dùng để làm gì
Liên hệ về dự án hoặc đề xuất bạn gửi, gọi lại theo yêu cầu, gửi bộ quy tắc AI và cập nhật liên quan.

## Bằng chứng đồng ý
Mỗi lần gửi, hệ thống lưu câu đồng ý bạn đã tick, thời điểm và địa chỉ IP. Ô đồng ý không bao giờ được tick sẵn.

## Lưu bao lâu, ai xem
Chỉ người phụ trách trao đổi dự án của TUVA xem. Thời hạn lưu sẽ ghi rõ trong bản chính thức.

## Quyền của bạn
Bạn có thể yêu cầu xem, sửa hoặc xoá thông tin của mình bằng cách để lại yêu cầu qua form liên hệ.""", cta=False)

add(path="/cam-on/", kenh="trang-cam-on", cta=False, cam_on=True, noindex=True,
 title="Đã nhận thông tin dự án · TUVA",
 desc="TUVA đã nhận thông tin dự án của bạn và sẽ liên hệ trong 1 ngày làm việc qua điện thoại hoặc email bạn để lại.",
 vet=[("Đã nhận", "/cam-on/")], h1="Đã nhận thông tin dự án của bạn",
 mo="Chúng tôi sẽ liên hệ trong 1 ngày làm việc qua điện thoại hoặc email bạn để lại.",
 than="""## Tiếp theo
1. Thu Hiền hoặc Thu Hà đọc thông tin và liên hệ để hẹn một buổi trao đổi.
2. Bạn nhận gợi ý hạng mục truyền thông và AI, khung ngân sách, chỉ số gợi ý cho logframe.
3. Hai bên thống nhất phần TUVA viết cùng bạn trước hạn nộp.

## Trong lúc chờ
- [Tự chấm mức sẵn sàng AI của tổ chức](/tu-cham-ai/?kenh=cam-on)
- [Tải bộ quy tắc AI an toàn](/bo-quy-tac-ai/?kenh=cam-on)
- [Đọc về Decent AI](/decent-ai/)""")

add(path="/en/thank-you/", lang="en", kenh="en-thank-you", cta=False, cam_on=True, noindex=True,
 title="Thank you · TUVA Communication",
 desc="TUVA has received your project details and will get back to you within one working day by phone or email.",
 vet=[("Thank you", "/en/thank-you/")], h1="Thank you, we have your project details",
 mo="We will get back to you within one working day by phone or email.",
 than="""## What happens next
1. Thu Hiền or Thu Hà reads your details and contacts you to set up a conversation.
2. You receive suggested communication and AI line items, a budget frame and indicators for the logframe.
3. We agree on what TUVA drafts with you before the deadline.

## Meanwhile
- [Get the AI rules for your organisation](/en/#ai-rules)""")

add(path="/404.html", kenh="trang-404", cta=False,
 title="Không có trang này · TUVA",
 desc="Trang bạn tìm không có trên tuva.work. Đường dẫn có thể đã đổi sau khi trang web được làm mới.",
 h1="Không có trang này",
 mo="Đường dẫn có thể đã đổi. Bạn về [trang chủ](/), [tự chấm mức sẵn sàng AI](/tu-cham-ai/), hoặc [trao đổi một dự án](/?kenh=trang-404#brief).",
 than="")

for i, t in enumerate(P):
    (D / f"{i + 1:02d}-{t['path'].strip('/').replace('/', '-') or 'goc'}.json").write_text(json.dumps(t, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(P), "trang")
