"""Nội dung trang con Sakédemy. Chạy: python3 nguon/_trang-bu.py && python3 nguon/_bai-tru.py && python3 tao-trang.py
Nguồn dữ kiện: hồ sơ đào tạo doanh nghiệp (Canva 02/2026, LAB043 brands/sakedemy/00-goc), landing v1.0 Linh duyệt 20/10 (LAB058).
Không bịa giá, số, khách, lời khen. Chỗ chưa có dữ liệu ghi ở ghi_chu và cau-hinh.json."""
import json, pathlib
D = pathlib.Path(__file__).parent
P = []
def add(**k): P.append(k)

GHI_CT = "Đầu việc dưới đây là ví dụ thường gặp. Giáo trình thật chốt sau buổi trao đổi và bảng khảo sát đầu vào của đội bạn."

add(path="/chuong-trinh/", kenh="trang-chuong-trinh",
 title="Chương trình đào tạo AI theo phòng ban · Sakédemy",
 desc="Năm hướng đào tạo AI ứng dụng theo phòng ban: marketing, kinh doanh, vận hành, ban lãnh đạo, chi nhánh ngân hàng. Mỗi lớp có giáo trình riêng.",
 vet=[("Chương trình", "/chuong-trinh/")], h1="Chương trình đào tạo AI theo phòng ban",
 mo="Sakédemy không dạy một khoá chung cho mọi người. Mỗi đề bài của doanh nghiệp có một giáo trình riêng, ví dụ lấy từ việc thật của đội.",
 than="""## Chọn theo phòng ban
| Phòng ban | Học để làm gì | Xem |
|---|---|---|
| Marketing, truyền thông | Ý tưởng, bài viết theo giọng thương hiệu, ảnh và video ngắn | [Chương trình marketing](/chuong-trinh/marketing-truyen-thong/) |
| Kinh doanh, chăm sóc khách | Email, báo giá, kịch bản trả lời khách nhất quán | [Chương trình kinh doanh](/chuong-trinh/kinh-doanh-cham-soc-khach/) |
| Vận hành, hành chính, nhân sự | Biên bản, văn bản đúng mẫu, báo cáo tuần | [Chương trình vận hành](/chuong-trinh/van-hanh-hanh-chinh/) |
| Ban lãnh đạo | Chọn việc giao cho AI, đặt luật dùng AI | [Chương trình lãnh đạo](/chuong-trinh/ban-lanh-dao/) |
| Chi nhánh ngân hàng | Tờ trình, email khách, báo cáo theo khuôn ngân hàng | [Chương trình ngân hàng](/chuong-trinh/chi-nhanh-ngan-hang/) |

## Phần nền chung của mọi lớp
Theo hồ sơ đào tạo doanh nghiệp của Sakédemy, buổi đầu thường gồm:
- AI là gì, phân biệt AI tạo sinh và AI tự hành.
- Tư duy hợp tác với AI: chuyển từ người tự làm hết sang người giao việc.
- Cấu trúc câu lệnh Vai trò, Bối cảnh, Nhiệm vụ, Định dạng.
- Thực hành trước và sau khi học kỹ thuật viết câu lệnh để thấy khác biệt.

Buổi sau đi vào việc của từng phòng ban: quy tắc viết câu lệnh, một số khung làm việc, kỹ thuật trò chuyện với AI, và sản phẩm cụ thể như văn bản, ảnh, nhạc, video.

## Phòng ban khác
Gửi đề bài ở [form đăng ký tư vấn](/?kenh=trang-chuong-trinh#dang-ky). Sakédemy may giáo trình riêng cho vấn đề thực tế của doanh nghiệp.""")

def ct(slug, ten, mo, viec, ket, anh, faq):
    add(path=f"/chuong-trinh/{slug}/", kenh=f"ct-{slug}", loai="service",
        title=f"Đào tạo AI cho {ten} · Sakédemy"[:70],
        desc=mo[:158],
        vet=[("Chương trình", "/chuong-trinh/"), (ten[0].upper() + ten[1:], f"/chuong-trinh/{slug}/")],
        h1=f"AI ứng dụng cho {ten}", mo=mo, ghi_chu=GHI_CT, anh=anh,
        than="## Đầu việc thường đưa vào lớp\n" + "\n".join(f"- {v}" for v in viec) +
             "\n\n## Học viên mang về\n" + "\n".join(f"- {k}" for k in ket) +
             "\n\n## Cách lớp chạy\nNhận đề bài, khảo sát đầu vào, may giáo trình, dạy và khảo sát lại sau khoá. Xem chi tiết ở [quy trình lớp doanh nghiệp](/lop-doanh-nghiep/).",
        hoi_dap=faq)

ct("marketing-truyen-thong", "marketing và truyền thông",
   "Khoá AI ứng dụng cho đội marketing và truyền thông: lên ý tưởng, viết theo giọng thương hiệu, làm ảnh và video ngắn, có bước người duyệt.",
   ["Lên ý tưởng chiến dịch và lịch nội dung từ một bản brief", "Viết bài mạng xã hội, email, thông cáo theo giọng thương hiệu", "Tạo ảnh, nhạc, video ngắn bằng AI cho kênh xã hội", "Quy trình nháp, sửa, duyệt khi nhiều người cùng làm với AI"],
   ["Bộ câu lệnh theo giọng thương hiệu của công ty", "Một quy trình nội dung có bước người duyệt trước khi đăng", "Danh sách việc nên và không nên giao cho AI trong truyền thông"],
   ["/img/anh/anh-giang-vien-rox.jpg", "Lớp AI ứng dụng tại Tập đoàn ROX"],
   [["Đội marketing đã dùng ChatGPT rồi, học thêm gì?", "Lớp đi từ kết quả khảo sát đầu vào. Đội đã dùng thường học sâu hơn về giữ giọng thương hiệu, quy trình nhiều bước và làm ảnh, video."],
    ["Có dạy công cụ trả phí không?", "Giáo trình chọn công cụ theo những gì công ty đang có hoặc sẵn sàng mua. Điều này được hỏi trong buổi trao đổi đầu tiên."]])

ct("kinh-doanh-cham-soc-khach", "kinh doanh và chăm sóc khách",
   "Khoá AI ứng dụng cho đội kinh doanh và chăm sóc khách: soạn email, báo giá, kịch bản trả lời khách nhất quán, luôn có người kiểm trước khi gửi.",
   ["Soạn email chào hàng, email theo dõi khách theo mẫu của công ty", "Soạn nhanh báo giá và đề xuất từ thông tin khách", "Bộ câu trả lời câu hỏi sản phẩm hay gặp", "Tóm tắt cuộc gọi và cập nhật ghi chú khách"],
   ["Bộ câu lệnh cho email, báo giá, trả lời khách", "Quy tắc kiểm trước khi gửi cho khách", "Cách che dữ liệu khách khi làm việc với AI"],
   ["/img/anh/anh-thuc-hanh-taseco.jpg", "Học viên thực hành AI trong lớp tại Taseco"],
   [["AI có trả lời khách thay nhân viên không?", "Lớp dạy AI soạn nháp, nhân viên kiểm và gửi. Việc để AI tự trả lời khách là quyết định riêng của công ty, cần quy trình và công cụ khác."],
    ["Dữ liệu khách có bị đưa lên AI không?", "Lớp có phần riêng về việc che thông tin khách trước khi dùng AI, theo quy định dữ liệu của công ty bạn."]])

ct("van-hanh-hanh-chinh", "vận hành, hành chính, nhân sự",
   "Khoá AI ứng dụng cho vận hành, hành chính, nhân sự: tóm tắt họp, soạn văn bản đúng mẫu, tổng hợp báo cáo tuần từ số liệu thô.",
   ["Biên bản và tóm tắt cuộc họp từ ghi chú hoặc ghi âm", "Soạn công văn, thông báo, quy định nội bộ theo mẫu", "Tổng hợp báo cáo tuần từ bảng số liệu", "Soạn mô tả công việc, câu hỏi phỏng vấn, tài liệu hội nhập"],
   ["Bộ câu lệnh cho văn bản hành chính hay dùng", "Mẫu báo cáo tuần có AI hỗ trợ", "Cách kiểm số liệu AI tổng hợp trước khi gửi lên trên"],
   ["/img/anh/anh-lop-onsen-fuji.jpg", "Lớp đào tạo AI tại Onsen Fuji"],
   [["Nhân viên lớn tuổi, ít dùng máy tính có học được không?", "Bảng khảo sát đầu vào cho biết mức của từng người. Lớp có thể chia nhóm hoặc thêm buổi nền tảng cho người mới."],
    ["Có dạy trên Excel, Google Sheets không?", "Có thể đưa vào giáo trình nếu báo cáo của đội làm trên bảng tính. Ghi rõ nhu cầu này khi đăng ký."]])

ct("ban-lanh-dao", "ban lãnh đạo",
   "Buổi AI cho ban lãnh đạo doanh nghiệp: hiểu AI tạo sinh và AI tự hành tới đâu, chọn việc giao cho AI trước, đặt luật dùng AI trong công ty.",
   ["AI tạo sinh và AI tự hành: làm được gì, chưa làm được gì", "Chọn ba đến năm việc nên giao cho AI trước trong công ty", "Khung luật dùng AI nội bộ: dữ liệu nào được đưa vào, ai duyệt", "Cách đo đội đã dùng AI vào việc tới đâu sau đào tạo"],
   ["Danh sách việc ưu tiên đưa AI vào", "Khung luật dùng AI để pháp chế và nhân sự hoàn thiện", "Lộ trình đào tạo cho các phòng ban tiếp theo"],
   ["/img/anh/anh-lop-vinhomes-2.jpg", "Buổi Lãnh đạo trong kỷ nguyên AI agent tại Vinhomes"],
   [["Buổi cho lãnh đạo khác lớp nhân viên thế nào?", "Ít thao tác công cụ hơn, nhiều phần ra quyết định hơn: chọn việc, đặt luật, đo kết quả."],
    ["Có làm riêng cho một nhóm nhỏ không?", "Có. Buổi cho lãnh đạo thường là nhóm nhỏ, nội dung chốt sau buổi trao đổi."]])

ct("chi-nhanh-ngan-hang", "chi nhánh ngân hàng",
   "Khoá AI thực chiến cho chi nhánh ngân hàng: tờ trình, email khách, báo cáo tuần theo khuôn của ngân hàng bạn và quy định dữ liệu khách hàng.",
   ["Soạn tờ trình, email khách, biên bản theo khuôn của ngân hàng", "Bộ câu trả lời sản phẩm nhất quán, luôn có bước người kiểm", "Tổng hợp báo cáo tuần từ số liệu thô thành bản tóm tắt cho giám đốc", "Che thông tin khách hàng trước khi dùng AI"],
   ["Bộ câu lệnh theo mẫu biểu của chi nhánh", "Quy tắc dữ liệu khách hàng khi dùng AI", "Cách học tiếp sau lớp"],
   ["/img/anh/anh-lop-vinhomes.jpg", "Lớp đào tạo AI của Sakédemy tại doanh nghiệp"],
   [["Quy định dữ liệu của ngân hàng rất chặt, lớp xử lý thế nào?", "Giáo trình may theo quy định dữ liệu của chính ngân hàng bạn, hỏi ngay trong bảng khảo sát đầu vào. Bài thực hành dùng mẫu đã che thông tin khách."],
    ["Học tại chi nhánh được không?", "Được. Lớp doanh nghiệp thường học tại văn phòng của đối tác."]])

add(path="/lop-doanh-nghiep/", kenh="trang-lop-dn", loai="service",
 title="Lớp đào tạo AI cho doanh nghiệp: quy trình bốn bước · Sakédemy",
 desc="Quy trình lớp AI doanh nghiệp của Sakédemy: nhận đề bài, khảo sát đầu vào, may giáo trình, dạy và khảo sát lại sau khoá. Học tại văn phòng hoặc online.",
 vet=[("Lớp doanh nghiệp", "/lop-doanh-nghiep/")], h1="Lớp AI doanh nghiệp: đo trước, may đo, học, đo lại",
 mo="Mỗi lớp doanh nghiệp đi qua bốn bước. Theo hồ sơ đào tạo của Sakédemy, lớp nội bộ mẫu gồm 2 buổi, mỗi buổi 2 đến 3 giờ, học tại văn phòng đối tác.",
 anh=["/img/anh/anh-giang-vien-taseco.jpg", "Giảng viên Sakédemy trong lớp tại Taseco"],
 than="""## Bốn bước
1. **Nhận đề bài.** Trao đổi với bên đặt lớp để nắm nhu cầu đào tạo, phòng ban, số người và thời gian học.
2. **Khảo sát đầu vào.** Gửi bảng khảo sát để đo học viên hiểu và đang dùng AI tới đâu, làm căn cứ xây giáo trình.
3. **May giáo trình.** Xây khung bài giảng từ đề bài và kết quả khảo sát, ví dụ lấy sát việc của doanh nghiệp.
4. **Dạy và đo đầu ra.** Giảng dạy, hỗ trợ học viên trong và sau khoá, khảo sát lại khi kết thúc.

## Hình thức
| | Tại văn phòng | Online | Kết hợp |
|---|---|---|---|
| Hợp với | Đội ngồi chung một nơi | Đội ở nhiều chi nhánh | Buổi nền tảng chung, thực hành theo nhóm |
| Thực hành | Giảng viên và trợ giảng đi từng bàn | Chia phòng nhỏ theo nhóm | Theo từng buổi |

## Đội giảng dạy
Giảng viên Đinh Trần Tuấn Linh, trợ giảng Phạm Vân Anh và Hoàng Ngọc Minh (theo hồ sơ đào tạo doanh nghiệp). Xem [trang giảng viên](/giang-vien/).

## Hoá đơn và thanh toán
Sakédemy xuất hoá đơn đào tạo cho doanh nghiệp. Thông tin pháp nhân, thuế suất và cách thanh toán ghi trong báo giá.""",
 hoi_dap=[["Một lớp tối đa bao nhiêu người?", "Tuỳ hình thức và mức thực hành. Đội đông thường chia thành nhiều lớp theo phòng ban, chốt sau bảng khảo sát đầu vào."],
          ["Bao lâu từ lúc đăng ký đến buổi học đầu?", "Tuỳ lịch của doanh nghiệp và thời gian khảo sát. Sakédemy báo lịch cụ thể trong báo giá."],
          ["Có chứng nhận cho học viên không?", "Hỏi trong buổi trao đổi; nội dung này ghi trong báo giá nếu doanh nghiệp cần."]])

add(path="/giang-vien/", kenh="trang-giang-vien",
 title="Giảng viên và trợ giảng · Sakédemy",
 desc="Đội giảng dạy lớp AI doanh nghiệp của Sakédemy: giảng viên Đinh Trần Tuấn Linh, trợ giảng Phạm Vân Anh và Hoàng Ngọc Minh.",
 vet=[("Giảng viên", "/giang-vien/")], h1="Giảng viên và trợ giảng",
 mo="Trang này chỉ nêu người có tên trong hồ sơ đào tạo doanh nghiệp của Sakédemy. Hồ sơ giảng viên khác sẽ thêm khi có thông tin xác nhận.",
 ghi_chu="Đang chờ ảnh chân dung, tiểu sử trợ giảng và danh sách mentor CLB AI Edge được phép nêu tên.",
 than="""## Đinh Trần Tuấn Linh, giảng viên
Chuyên gia AI ứng dụng với hơn 18 năm kinh nghiệm. Giám đốc công nghệ của UNIKON, sáng lập TUVA, URAH Network và Sakédemy. Ứng dụng AI vào marketing, truyền thông, xuất bản và đào tạo.

Các khoá đã tham gia giảng dạy, theo hồ sơ:
- AI Marketing Mastery 2024 cho người làm truyền thông tại agency và brand.
- MICAI, tối ưu quản trị vận hành doanh nghiệp với AI, tại Viện Quản trị và Công nghệ FSB.
- Khoá đào tạo nội bộ cho tập đoàn và ngân hàng.

## Phạm Vân Anh, trợ giảng
Trợ giảng lớp đào tạo nội bộ, theo sát học viên trong giờ thực hành.

## Hoàng Ngọc Minh, trợ giảng
Trợ giảng lớp đào tạo nội bộ, theo sát học viên trong giờ thực hành.""")

add(path="/hoc-thu/", kenh="trang-hoc-thu",
 title="Bài học thử AI ứng dụng miễn phí · Sakédemy",
 desc="Học thử một bài AI ứng dụng miễn phí trên điện thoại. Để lại email, Sakédemy gửi đường vào bài học và gợi ý khoá cá nhân hợp với việc của bạn.",
 vet=[("Học thử", "/hoc-thu/")], h1="Học thử một bài AI ứng dụng",
 mo="Bài học thử dành cho người học một mình, muốn xem cách Sakédemy dạy trước khi chọn khoá. Học trên điện thoại, không cần cài gì.",
 ghi_chu="Đường vào bài học thử (cungai) chưa chốt. Khi có, điền link_hoc_thu trong cau-hinh.json để form mở thẳng bài học.",
 than="""## Sau bài học thử
1. Bạn nhận email có đường vào bài học.
2. Học xong, bạn chọn [khoá cá nhân](/khoa-ca-nhan/) hợp với việc của mình, hoặc dừng ở đó.
3. Nếu công ty bạn muốn cả đội cùng học, chuyển sang [lớp doanh nghiệp](/lop-doanh-nghiep/).""",
 form_hoc_thu=True, cta=False)

add(path="/khoa-ca-nhan/", kenh="trang-khoa-ca-nhan",
 title="Khoá AI ứng dụng cho người học cá nhân · Sakédemy",
 desc="Người học một mình bắt đầu bằng bài học thử, chọn khoá cá nhân theo việc, học xong học tiếp hoặc giới thiệu lớp cho công ty.",
 vet=[("Khoá cá nhân", "/khoa-ca-nhan/")], h1="Học AI ứng dụng một mình",
 mo="Trang chủ Sakédemy dành cho doanh nghiệp đặt lớp. Nếu bạn học một mình, đường đi gồm ba bước dưới đây.",
 ghi_chu="Danh mục khoá cá nhân, giá và cách thanh toán QR chưa chốt; trang sẽ liệt kê khi có (link_khoa_ca_nhan trong cau-hinh.json).",
 than="""## Ba bước
1. **Học thử một bài** miễn phí trên điện thoại. [Nhận bài học thử](/hoc-thu/).
2. **Chọn khoá theo việc**, thanh toán bằng mã QR.
3. **Học xong**, học khoá kế tiếp hoặc giới thiệu lớp doanh nghiệp cho công ty của bạn.

## Công ty bạn cần cả đội cùng học
Xem [lớp doanh nghiệp](/lop-doanh-nghiep/) hoặc [đăng ký tư vấn](/?kenh=trang-khoa-ca-nhan#dang-ky).""")

add(path="/hoi-dap/", kenh="trang-hoi-dap",
 title="Hỏi đáp về khoá AI ứng dụng cho doanh nghiệp · Sakédemy",
 desc="Giá, hoá đơn, hình thức học, dữ liệu công ty, hỗ trợ sau khoá: câu trả lời ngắn cho doanh nghiệp trước khi đặt lớp AI ứng dụng.",
 vet=[("Hỏi đáp", "/hoi-dap/")], h1="Câu hỏi trước khi đặt lớp",
 mo="Những câu doanh nghiệp hay hỏi trước khi đặt lớp AI ứng dụng cho nhân viên.", than="",
 hoi_dap=[
  ["Một lớp doanh nghiệp giá bao nhiêu?", "Giá phụ thuộc số học viên, số buổi, hình thức tại văn phòng hay online và mức may đo giáo trình. Sakédemy gửi báo giá sau buổi trao đổi đầu tiên và bản khảo sát đầu vào."],
  ["Sakédemy có xuất hoá đơn cho doanh nghiệp không?", "Có. Sakédemy xuất hoá đơn đào tạo cho doanh nghiệp. Thông tin pháp nhân và thuế suất ghi trong báo giá."],
  ["Học tại văn phòng hay online?", "Cả hai. Lớp thường học tại văn phòng của doanh nghiệp; đội ở nhiều nơi thì học online hoặc kết hợp."],
  ["Một khoá kéo dài bao lâu?", "Lớp nội bộ mẫu trong hồ sơ của Sakédemy gồm 2 buổi, mỗi buổi 2 đến 3 giờ. Số buổi thật chốt theo đề bài."],
  ["Nhân viên có phải đưa dữ liệu công ty vào AI khi học không?", "Không bắt buộc. Bài thực hành dùng mẫu biểu đã che thông tin nhạy cảm, và lớp có phần riêng về việc gì được đưa vào AI, việc gì không."],
  ["Học xong có ai hỗ trợ tiếp không?", "Có. Sakédemy hỗ trợ học viên trong và sau khoá, kèm một lần khảo sát sau khoá để đo đội đã dùng AI vào việc tới đâu."],
  ["Đội chúng tôi chưa ai dùng AI, có học được không?", "Được. Bảng khảo sát đầu vào cho biết mức của từng người, giáo trình bắt đầu từ phần nền tảng nếu cần."],
  ["Có dạy riêng cho ban lãnh đạo không?", "Có. Buổi cho lãnh đạo tập trung vào chọn việc giao cho AI và đặt luật dùng AI trong công ty."],
  ["Tôi học một mình thì bắt đầu từ đâu?", "Bắt đầu bằng bài học thử miễn phí. Để lại email, Sakédemy gửi đường vào bài học thử và gợi ý khoá cá nhân hợp với việc của bạn."],
  ["Làm sao biết khoá AI ứng dụng nào uy tín?", "Hỏi bên dạy ba điều: có khảo sát đầu vào không, ví dụ trong lớp lấy từ việc của ai, và đo kết quả sau khoá thế nào. Xem bài chọn khoá AI ứng dụng trong cẩm nang."]])

add(path="/cam-nang/", kenh="trang-cam-nang",
 title="Cẩm nang AI ứng dụng cho doanh nghiệp · Sakédemy",
 desc="Bài viết trả lời câu hỏi doanh nghiệp hay đặt ra trước khi mua khoá AI ứng dụng cho nhân viên: chọn khoá, đo kết quả, luật dùng AI.",
 vet=[("Cẩm nang", "/cam-nang/")], h1="Cẩm nang AI ứng dụng cho doanh nghiệp",
 mo="Mỗi bài trả lời một câu hỏi doanh nghiệp hay đặt ra trước khi mua khoá, và dẫn về trang khoá liên quan.",
 than="""## Bài mới
- [Khoá AI ứng dụng uy tín: năm câu hỏi trước khi đặt lớp cho nhân viên](/khoa-ai-ung-dung-uy-tin/)

## Bài sắp có
- Đo nhân viên đã dùng AI vào việc tới đâu sau đào tạo
- Luật dùng AI nội bộ: bắt đầu từ ba câu hỏi
- Đào tạo AI cho phòng marketing: học gì trước""")

add(path="/gioi-thieu/", kenh="trang-gioi-thieu",
 title="Giới thiệu Sakédemy · Khi sáng tạo gặp công nghệ",
 desc="Sakédemy thành lập năm 2016 với các lớp viết, vẽ và sáng tạo; từ 2024 mở rộng sang e-learning và đào tạo AI ứng dụng cho doanh nghiệp.",
 vet=[("Giới thiệu", "/gioi-thieu/")], h1="Sakédemy, khi sáng tạo gặp công nghệ",
 mo="Sakédemy đào tạo AI ứng dụng cho doanh nghiệp và người đi làm, với các lớp may đo theo việc thật của từng đội.",
 ghi_chu="Tên pháp nhân, mã số thuế, địa chỉ đang chờ xác nhận.",
 anh=["/img/anh/anh-hoi-truong-phenikaa.jpg", "Talkshow tại ĐH Phenikaa"],
 than="""## Chặng đường
| Năm | Việc |
|---|---|
| 2016 đến 2018 | Thành lập, các lớp đầu tiên về viết, vẽ và nuôi dưỡng sự trân trọng nghệ thuật |
| 2019 | Mở rộng sang lớp thể hiện nghệ thuật và viết kịch bản |
| 2024 | Mở rộng sang e-learning, hợp tác với Spiderum và Eduforlife trong các khoá tích hợp AI |

## Năng lực
- 62+ số "Sống Cùng AI" đã lên sóng VOV.
- 700+ sinh viên dự talkshow tại ĐH Phenikaa.
- 11 mentor đồng hành trong CLB AI Edge.

## Đã đào tạo cho
Vinhomes, Taseco, Tập đoàn ROX, Onsen Fuji, Viện FSB, ĐH Phenikaa.

## Chúng tôi tin
Học cùng AI, không học bằng AI. Người học giữ phần nghĩ và quyết định; AI làm nhanh phần việc lặp lại.""")

add(path="/lien-he/", kenh="trang-lien-he",
 title="Liên hệ Sakédemy · Đăng ký tư vấn lớp doanh nghiệp",
 desc="Đăng ký tư vấn lớp đào tạo AI ứng dụng cho doanh nghiệp. Để lại thông tin, Sakédemy liên hệ để hẹn buổi trao đổi về đề bài của đội bạn.",
 vet=[("Liên hệ", "/lien-he/")], h1="Liên hệ Sakédemy",
 mo="Để lại thông tin ở form dưới, chúng tôi liên hệ để hẹn buổi trao đổi.",
 ghi_chu="Số điện thoại, Zalo, email và địa chỉ đang cập nhật.",
 than="", form=True, cta=False)

add(path="/chinh-sach-du-lieu/", kenh="trang-chinh-sach",
 title="Chính sách dữ liệu cá nhân · Sakédemy",
 desc="Sakédemy thu gì khi bạn đăng ký tư vấn, gọi lại hoặc học thử, dùng để làm gì, lưu bao lâu, và cách bạn yêu cầu sửa hoặc xoá dữ liệu.",
 vet=[("Chính sách dữ liệu", "/chinh-sach-du-lieu/")], h1="Chính sách dữ liệu cá nhân",
 mo="Bản nháp theo Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân.",
 ghi_chu="Bản nháp, chờ pháp chế duyệt và chờ tên pháp nhân, địa chỉ, kênh liên hệ chính thức.",
 than="""## Chúng tôi thu gì
- Form đăng ký tư vấn: họ tên, công ty, vai trò, điện thoại hoặc email, số học viên, phòng ban, hình thức, thời gian và nhu cầu bạn ghi.
- Form gọi lại: họ tên và số điện thoại.
- Form học thử: email.
- Kèm theo mỗi lần gửi: thời điểm, câu đồng ý bạn đã tick, địa chỉ IP, trang và nguồn bạn đến (ví dụ đường dẫn có `kenh`).

## Dùng để làm gì
- Liên hệ tư vấn, gọi lại, gửi bài học thử theo đúng việc bạn đã đồng ý.
- Đo kênh nào đưa người đăng ký tới, để cải thiện nội dung.

## Không làm gì
- Không bán hay cho thuê dữ liệu của bạn.
- Không gửi tin quảng cáo ngoài phạm vi bạn đồng ý.

## Lưu bao lâu
[Chờ pháp chế chốt thời hạn lưu.]

## Quyền của bạn
Bạn có quyền xem, sửa, rút lại đồng ý và yêu cầu xoá dữ liệu. Kênh tiếp nhận yêu cầu đang cập nhật; trong lúc chờ, bạn gửi yêu cầu qua [form liên hệ](/lien-he/).""", cta=False)

add(path="/cam-on/", kenh="trang-cam-on", cta=False, cam_on=True, noindex=True,
 title="Đã nhận đăng ký · Sakédemy",
 desc="Sakédemy đã nhận đăng ký tư vấn lớp doanh nghiệp của bạn và sẽ liên hệ để hẹn buổi trao đổi về đề bài của đội.",
 vet=[("Đã nhận đăng ký", "/cam-on/")], h1="Đã nhận đăng ký của bạn",
 mo="Sakédemy sẽ liên hệ qua điện thoại hoặc email bạn để lại để hẹn buổi trao đổi.",
 than="""## Tiếp theo
1. Chúng tôi đọc nhu cầu của đội và gọi lại để hỏi thêm nếu cần.
2. Bạn nhận bảng khảo sát đầu vào để gửi cho học viên.
3. Sakédemy gửi đề cương theo phòng ban, báo giá và lịch học đề xuất.

## Trong lúc chờ
- [Đọc năm câu hỏi trước khi đặt lớp AI cho nhân viên](/khoa-ai-ung-dung-uy-tin/)
- [Xem chương trình theo phòng ban](/chuong-trinh/)""")

add(path="/404.html", kenh="trang-404", cta=False,
 title="Không có trang này · Sakédemy",
 desc="Trang bạn tìm không có trên sakedemy.com. Về trang chủ, xem chương trình hoặc đăng ký tư vấn lớp doanh nghiệp.",
 h1="Không có trang này",
 mo="Đường dẫn có thể đã đổi. Bạn về [trang chủ](/), xem [chương trình theo phòng ban](/chuong-trinh/), hoặc [đăng ký tư vấn](/?kenh=trang-404#dang-ky).",
 than="")

for i, t in enumerate(P, 1):
    (D / f"{i:02d}-{t['path'].strip('/').replace('/', '-').replace('.html','') or 'goc'}.json").write_text(json.dumps(t, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(P), "trang")
