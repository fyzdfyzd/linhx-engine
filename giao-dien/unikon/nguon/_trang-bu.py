"""Nội dung trang con Unikon. Chạy: python3 nguon/_trang-bu.py && python3 nguon/_bai-tru.py && python3 tao-trang.py
Không bịa giá, số, case, tên khách. Chỗ chưa có dữ liệu dùng ghi_chu."""
import json, pathlib
D = pathlib.Path(__file__).parent
P = []
def add(**k): P.append(k)

FAQ_GIA = ("Giá tính thế nào?", "Mỗi loại asset có một giá sàn. Báo giá cộng theo số asset, số biến thể và độ khó của hướng khách chọn. Gửi brief để nhận báo giá cụ thể.")
FAQ_TRANG_NHAN = ("Khách của tôi có biết Unikon đứng sau không?", "Không, nếu bạn không muốn. Deck và file giao không mang logo Unikon. Tên nhãn hàng của khách được ẩn trong mọi tài liệu của chúng tôi.")
FAQ_NGUOI_THAT = ("Có dùng gương mặt hay giọng người nổi tiếng được không?", "Chỉ khi có hợp đồng với chính người đó. Mặc định, nhân vật AI của Unikon là người hư cấu.")

add(path="/dich-vu/", kenh="trang-dich-vu", loai="service",
 title="Dịch vụ AI production cho agency theo loại asset · Unikon",
 desc="Unikon sản xuất asset sáng tạo bằng AI cho agency: ảnh và key visual, video AI, nhân vật và giọng AI. Mỗi asset có người duyệt, giao trắng nhãn.",
 vet=[("Dịch vụ", "/dich-vu/")], h1="Dịch vụ AI production, chọn theo loại asset",
 mo="Agency mang ý tưởng và quan hệ với khách, Unikon làm phần sản xuất bằng AI. Bảng dưới giúp bạn biết nên ghi gì vào brief.",
 than="""## Chọn theo thứ bạn cần giao cho khách
| Bạn cần | Loại asset | Hợp khi |
|---|---|---|
| Hình để pitch, rồi nhiều biến thể cho kênh | [Ảnh AI và key visual](/dich-vu/anh-ai/) | Chiến dịch nhiều kênh, nhiều cỡ, nhiều tệp khách |
| Chuyển động, cảnh khó quay | [Video AI](/dich-vu/video-ai/) | Video ngắn mạng xã hội, khung hình động cho màn hình |
| Gương mặt, giọng nói cho nhãn hàng | [Nhân vật và giọng AI](/dich-vu/nhan-vat-giong-ai/) | Đại sứ ảo, giọng đọc quảng cáo, nhạc nền |

## Điểm chung của mọi job
- Người duyệt từng asset trước khi giao: bàn tay, chữ, khuôn mặt, logo, màu thương hiệu.
- File giao không có logo Unikon. Tên nhãn hàng của khách được ẩn trong tài liệu của chúng tôi.
- Báo giá theo giá sàn từng loại asset, xem [cách tính giá](/bao-gia/).
- Nhãn chạy đều hằng tháng có thể chuyển sang [Brand kit hằng tháng](/brand-kit/).

## Bắt đầu từ đâu
Phần lớn agency bắt đầu bằng [pitch mẫu 48 giờ](/pitch-48-gio/): ba hướng ý tưởng có hình, trong deck trắng nhãn. Trúng pitch thì sản xuất tiếp theo job.""",
 hoi_dap=[FAQ_TRANG_NHAN, FAQ_GIA])

add(path="/dich-vu/anh-ai/", kenh="trang-anh-ai", loai="service",
 title="Ảnh AI và key visual cho chiến dịch của agency · Unikon",
 desc="Key visual cho pitch và hàng loạt biến thể theo kênh, làm bằng AI, giữ đúng màu, logo, bao bì nhãn hàng. Có người duyệt từng ảnh, giao trắng nhãn.",
 vet=[("Dịch vụ", "/dich-vu/"), ("Ảnh AI và key visual", "/dich-vu/anh-ai/")], h1="Ảnh AI và key visual cho chiến dịch",
 mo="Từ một hướng hình đã chốt ở pitch, chúng tôi làm key visual và các biến thể theo kênh, theo tệp khách, theo cỡ hiển thị.",
 than="""## Làm được gì
- Key visual cho pitch và cho chiến dịch chạy thật.
- Biến thể theo kênh: bài đăng, story, banner, màn hình ngoài trời.
- Sản phẩm của nhãn đặt vào bối cảnh mới mà không dựng studio.
- Nhiều phiên bản cho nhiều tệp khách trong cùng một chiến dịch.

## Agency cần gửi gì
1. Brief và hướng hình khách đã chọn.
2. Logo, bao bì, màu, phông của nhãn hàng (file gốc nếu có).
3. Danh sách cỡ và kênh cần giao.
4. Những điều nhãn hàng cấm (màu đối thủ, cử chỉ, bối cảnh nhạy cảm).

## Người duyệt soát gì trước khi giao
- Bàn tay, ngón tay, khuôn mặt không méo.
- Chữ trong hình đúng chính tả hoặc để trống cho thiết kế chèn sau.
- Logo, bao bì đúng tỉ lệ và màu.
- Không có biểu tượng, gương mặt người thật lọt vào khung.""",
 hoi_dap=[("Ảnh AI có in khổ lớn được không?", "Ghi cỡ in vào brief. Chúng tôi báo trước trong báo giá cỡ nào làm được và cần bước nâng độ phân giải nào."), FAQ_GIA])

add(path="/dich-vu/video-ai/", kenh="trang-video-ai", loai="service",
 title="Video AI cho agency: video ngắn, khung hình động · Unikon",
 desc="Video ngắn cho mạng xã hội, khung hình động, cảnh khó quay bằng máy thật, làm bằng AI từ hướng hình đã duyệt. Người duyệt từng bản, giao trắng nhãn.",
 vet=[("Dịch vụ", "/dich-vu/"), ("Video AI", "/dich-vu/video-ai/")], h1="Video AI cho chiến dịch của agency",
 mo="Video AI hợp nhất khi đi tiếp từ hình đã duyệt ở bước pitch: khách đã thấy chất hình, video giữ đúng chất đó.",
 than="""## Hợp với
- Video ngắn cho mạng xã hội, nhiều phiên bản theo kênh.
- Khung hình động cho màn hình tại điểm bán, sự kiện.
- Cảnh khó hoặc tốn kém khi quay thật: không gian giả tưởng, sản phẩm phóng to, bối cảnh nước ngoài.

## Chưa hợp với
- Phim cần diễn viên thật nói lời thoại dài.
- Cảnh cần gương mặt người nổi tiếng khi chưa có hợp đồng.

## Cách làm
1. Chốt hướng hình và kịch bản khung với agency.
2. Làm bản nháp chuyển động để duyệt nhịp.
3. Làm bản hoàn chỉnh, ghép giọng và nhạc nếu có.
4. Người duyệt soát từng khung trước khi giao.""",
 ghi_chu="Độ dài tối đa và định dạng giao của video AI chờ Unikon chốt. Ghi yêu cầu vào brief, chúng tôi trả lời trong báo giá.",
 hoi_dap=[FAQ_NGUOI_THAT, FAQ_GIA])

add(path="/dich-vu/nhan-vat-giong-ai/", kenh="trang-nhan-vat", loai="service",
 title="Nhân vật AI và giọng AI cho nhãn hàng · Unikon",
 desc="Đại sứ ảo, giọng đọc, nhạc nền làm bằng AI cho chiến dịch của agency. Nhân vật là người hư cấu; người thật chỉ khi có hợp đồng. Giao trắng nhãn.",
 vet=[("Dịch vụ", "/dich-vu/"), ("Nhân vật và giọng AI", "/dich-vu/nhan-vat-giong-ai/")], h1="Nhân vật AI và giọng AI cho nhãn hàng",
 mo="Một gương mặt và một giọng nói riêng cho nhãn hàng, dùng được trên ảnh, video và nội dung mạng xã hội trong suốt chiến dịch.",
 than="""## Làm được gì
- Đại sứ ảo của nhãn hàng: ngoại hình, phong cách, tính cách theo brief.
- Bộ ảnh và video của nhân vật cho nhiều kênh.
- Giọng đọc quảng cáo, nhạc nền cho video.

## Luật với người thật
Nhân vật AI của Unikon mặc định là người hư cấu. Mô phỏng gương mặt hay giọng của người thật, kể cả KOL đang hợp tác với nhãn, chỉ làm khi có hợp đồng với chính người đó.

## Giữ nhân vật nhất quán
Nhân vật dùng lâu dài nên nằm trong [Brand kit hằng tháng](/brand-kit/): ngoại hình, trang phục, giọng, những điều nhân vật không làm, để mọi job sau giữ đúng một người.""",
 hoi_dap=[FAQ_NGUOI_THAT, ("Nhân vật thuộc về ai?", "Quyền với nhân vật ghi trong hợp đồng của từng job. Bạn nêu nhu cầu trong brief để chúng tôi đưa vào báo giá.")])

add(path="/pitch-48-gio/", kenh="trang-pitch-48",
 title="Pitch mẫu 48 giờ: ba hướng ý tưởng, deck trắng nhãn · Unikon",
 desc="Gửi brief pitch, sau 48 giờ agency nhận ba hướng ý tưởng có hình làm bằng AI trong deck trắng nhãn, kèm báo giá sản xuất theo giá sàn.",
 vet=[("Pitch 48 giờ", "/pitch-48-gio/")], h1="Pitch mẫu 48 giờ cho agency",
 mo="Khách của bạn chọn dễ hơn khi thấy hình thật. Pitch mẫu 48 giờ đưa ba hướng ý tưởng có hình AI vào deck mang logo agency, để bạn đem đi pitch.",
 than="""## Bạn nhận gì
| Thứ | Gồm |
|---|---|
| Ba hướng ý tưởng | Mỗi hướng một câu ý tưởng và hình mẫu làm bằng AI |
| Deck trắng nhãn | Mang logo agency, không có logo Unikon, bạn sửa lời pitch tuỳ ý |
| Báo giá | Giá sản xuất cho từng hướng, theo giá sàn từng loại asset |

## Brief cần có
- Tên agency và người liên hệ.
- Khách hàng cuối, hoặc chỉ ngành hàng nếu bạn muốn ẩn tên.
- Hạn pitch.
- Loại asset dự kiến: ảnh, video, nhân vật, giọng.
- Ngân sách sản xuất dự kiến, nếu đã có.

## Xem trước một pitch mẫu
Pitch mẫu đặt trên [demo.unikon.vn](https://demo.unikon.vn/?kenh=trang-pitch-48) để bạn thấy deck trông thế nào trước khi gửi brief.

## Sau pitch
Trúng thì sản xuất theo job, hoặc chuyển sang [Brand kit hằng tháng](/brand-kit/) khi nhãn chạy nội dung đều.""",
 ghi_chu="Điều kiện tính 48 giờ (ngày làm việc hay giờ liền, brief cần đủ những gì) và phí pitch mẫu, nếu có, chờ Unikon chốt.",
 hoi_dap=[("Hạn pitch của tôi chỉ còn hai ngày thì sao?", "Gửi brief ngay và ghi rõ hạn. Chúng tôi báo lại có kịp hay không trước khi bắt tay làm."), FAQ_TRANG_NHAN])

add(path="/bao-gia/", kenh="trang-bao-gia",
 title="Cách tính giá AI production theo giá sàn · Unikon",
 desc="Unikon báo giá theo giá sàn từng loại asset, cộng theo số asset, số biến thể và độ khó. Thu theo hoá đơn từng job hoặc phí Brand kit hằng tháng.",
 vet=[("Cách tính giá", "/bao-gia/")], h1="Cách Unikon tính giá cho agency",
 mo="Mỗi loại asset có một giá sàn. Báo giá cộng từ đó theo số asset, số biến thể và độ khó, để agency biết rõ phần sản xuất trước khi cộng phí của mình.",
 ghi_chu="Giá sàn từng loại asset và phí Brand kit đang chờ Unikon chốt, nên trang chưa ghi số. Gửi brief để nhận báo giá cụ thể.",
 than="""## Giá sàn theo loại asset
| Loại asset | Giá sàn |
|---|---|
| Ảnh AI, key visual | Chờ chốt, báo theo brief |
| Video AI | Chờ chốt, báo theo brief |
| Nhân vật và giọng AI | Chờ chốt, báo theo brief |

## Giá thay đổi theo
- Số asset và số biến thể.
- Độ khó: sản phẩm cần giữ chi tiết bao bì, nhiều nhân vật trong một khung, chữ trong hình.
- Số vòng sửa sau khi khách duyệt hướng.

## Hai cách thu
- **Theo job**: một báo giá, một hoá đơn cho mỗi chiến dịch.
- **Brand kit hằng tháng**: phí tháng cố định, job phát sinh vẫn có hoá đơn riêng. Xem [Brand kit](/brand-kit/).""",
 hoi_dap=[FAQ_GIA, ("Agency có được cộng phí trên báo giá của Unikon không?", "Có. Báo giá gửi cho agency, agency tự định giá với khách hàng của mình.")])

add(path="/brand-kit/", kenh="trang-brand-kit",
 title="Brand kit hằng tháng cho nhãn chạy nội dung AI đều · Unikon",
 desc="Brand kit hằng tháng: Unikon giữ bộ quy tắc hình ảnh AI của nhãn hàng (màu, chất hình, nhân vật, điều cấm) để mọi job sau ra nhanh và cùng một chất.",
 vet=[("Brand kit hằng tháng", "/brand-kit/")], h1="Brand kit hằng tháng",
 mo="Khi một nhãn hàng chạy nội dung AI đều đặn, mỗi job bắt đầu lại từ đầu sẽ chậm và lệch chất. Brand kit giữ những gì đã đúng để dùng lại.",
 ghi_chu="Phạm vi chi tiết và phí tháng của Brand kit đang chờ Unikon chốt. Nội dung dưới đây là khung để trao đổi.",
 than="""## Brand kit giữ gì
- Màu, phông, logo, bao bì của nhãn hàng ở dạng dùng được cho AI.
- Chất hình đã duyệt: ánh sáng, góc máy, bối cảnh.
- Nhân vật AI của nhãn, nếu có: ngoại hình, trang phục, giọng.
- Danh sách điều cấm của nhãn hàng.

## Agency được gì
- Job sau vào việc nhanh hơn vì không phải dựng lại từ đầu.
- Asset giữa các tháng giống nhau về chất.
- Một đầu mối ở Unikon biết rõ nhãn hàng.

## Thu tiền
Phí tháng cho Brand kit. Job sản xuất phát sinh trong tháng có hoá đơn riêng theo [cách tính giá](/bao-gia/).""",
 hoi_dap=[("Khi nào nên chuyển từ job sang Brand kit?", "Khi nhãn hàng cần nội dung AI đều đặn qua nhiều tháng. Một job lẻ thì không cần."), ("Ngừng Brand kit thì sao?", "Điều kiện ngừng và bàn giao ghi trong hợp đồng Brand kit, chờ Unikon chốt mẫu.")])

add(path="/an-toan-thuong-hieu/", kenh="trang-an-toan", form="form-bo-kiem",
 title="An toàn thương hiệu cho asset AI, tải bộ kiểm · Unikon",
 desc="Cách Unikon kiểm asset AI trước khi giao cho agency: người duyệt, luật với người thật, trắng nhãn. Tải Bộ kiểm an toàn thương hiệu cho asset AI.",
 vet=[("An toàn thương hiệu", "/an-toan-thuong-hieu/")], h1="An toàn thương hiệu cho asset AI",
 mo="Agency chịu trách nhiệm trước khách về từng hình. Đây là những gì chúng tôi soát trước khi asset rời tay, và bộ kiểm để đội của bạn tự soát.",
 than="""## Bốn lớp kiểm của Unikon
1. **Hình**: bàn tay, khuôn mặt, chữ trong hình, chi tiết sản phẩm.
2. **Thương hiệu**: logo, màu, bao bì đúng tỉ lệ; không lẫn màu hay biểu tượng của đối thủ.
3. **Người thật**: không gương mặt, giọng người thật khi chưa có hợp đồng.
4. **Trắng nhãn**: file giao không có logo Unikon, tên khách được ẩn trong tài liệu của chúng tôi.

## Bộ kiểm an toàn thương hiệu cho asset AI
Danh sách điểm cần soát trước khi đưa asset AI cho khách duyệt, dùng được cho cả asset không do Unikon làm. Để lại email ở form dưới, chúng tôi gửi bộ kiểm cho bạn.""",
 ghi_chu="Bản PDF của bộ kiểm đang hoàn thiện. Email để lại ở đây vào danh sách chờ, chúng tôi gửi ngay khi có.",
 hoi_dap=[FAQ_NGUOI_THAT, ("Asset AI có vướng bản quyền không?", "Chúng tôi không đưa hình, logo, nhân vật của bên thứ ba vào asset khi chưa có quyền. Điều khoản quyền với asset ghi trong hợp đồng từng job.")])

add(path="/cho-agency/", kenh="trang-cho-agency",
 title="Làm việc cùng agency: AM, producer, người quyết · Unikon",
 desc="Unikon là đơn vị AI production cho agency: account manager gửi brief, producer theo lịch, người quyết xem báo giá theo giá sàn. Agency giữ khách.",
 vet=[("Cho agency", "/cho-agency/")], h1="Unikon làm việc cùng agency thế nào",
 mo="Agency giữ khách hàng, ý tưởng lớn và lời pitch. Unikon đứng sau làm phần sản xuất bằng AI, giao dưới tên agency.",
 than="""## Mỗi vai trò cần gì từ chúng tôi
| Vai trò | Cần | Unikon đưa |
|---|---|---|
| Account manager | Có hình để pitch kịp hạn | Pitch mẫu 48 giờ, deck trắng nhãn |
| Producer | Lịch sản xuất rõ, ít vòng sửa | Báo giá chốt số asset, người duyệt trước khi giao |
| Creative director | Hình đúng ý tưởng, không bị AI làm hỏng | Ba hướng để chọn, Brand kit giữ chất hình |
| Người quyết ngân sách | Biết phần sản xuất tốn bao nhiêu | Giá sàn từng loại asset, hoá đơn theo job |

## Cách làm cùng nhau
1. Agency gửi brief và hạn pitch.
2. Unikon gửi ba hướng, deck trắng nhãn, báo giá.
3. Agency pitch. Trúng thì ký job.
4. Sản xuất, duyệt, giao file mang tên agency.

## Tên agency và tên khách
Không xuất hiện trong case, bài đăng, hồ sơ năng lực của Unikon khi chưa có văn bản cho phép của cả agency và khách.""",
 hoi_dap=[FAQ_TRANG_NHAN, ("Agency nhỏ có làm được không?", "Được. Gửi brief như bình thường, báo giá theo giá sàn không phụ thuộc cỡ agency.")])

add(path="/du-an/", kenh="trang-du-an",
 title="Dự án AI production cùng agency · Unikon",
 desc="Dự án Unikon làm cùng agency được trình bày trong deck credential trắng nhãn. Tên khách chỉ nêu khi được phép. Gửi yêu cầu để nhận deck.",
 vet=[("Dự án", "/du-an/")], h1="Dự án làm cùng agency",
 mo="Phần lớn việc của Unikon giao dưới tên agency, nên chúng tôi không đăng tên khách lên web khi chưa được phép.",
 ghi_chu="Chưa có case được phép công khai. Trang này giữ khung; case sẽ thêm khi có văn bản đồng ý của agency và khách.",
 than="""## Xem năng lực ở đâu
Unikon gửi deck credential trắng nhãn khi agency yêu cầu: loại chiến dịch, ngành hàng, asset đã làm, không nêu tên khách khi chưa được phép.

## Mỗi case khi được phép sẽ có
- Ngành hàng và loại agency.
- Việc cần làm và hạn.
- Asset đã giao, số lượng và kênh chạy.
- Người xác nhận phía agency.

## Muốn xem ngay
[Gửi brief](/?kenh=trang-du-an#brief) hoặc để lại số ở [trang liên hệ](/lien-he/), ghi "cần deck credential".""",
 hoi_dap=[("Vì sao không có logo khách trên trang?", "Vì phần lớn job giao trắng nhãn qua agency. Logo và tên chỉ đăng khi cả agency và khách cho phép bằng văn bản.")])

add(path="/gioi-thieu/", kenh="trang-gioi-thieu",
 title="Giới thiệu Unikon, đơn vị AI production cho agency",
 desc="Unikon sản xuất asset sáng tạo bằng AI cho agency: ảnh, video, nhân vật và giọng AI. Người thật duyệt từng asset, giao trắng nhãn dưới tên agency.",
 vet=[("Giới thiệu", "/gioi-thieu/")], h1="Unikon là ai",
 mo="Unikon là đơn vị AI production cho agency. Chúng tôi làm phần sản xuất bằng AI để agency giữ khách và ý tưởng lớn.",
 ghi_chu="Thông tin đội ngũ, năm thành lập, địa chỉ và pháp nhân hiển thị đang chờ Unikon chốt.",
 than="""## Chúng tôi tin vào
- Hình thật giúp khách chọn nhanh hơn lời mô tả.
- AI cần người duyệt. Không asset nào rời tay khi chưa có người soát.
- Agency là đối tác của chúng tôi. Unikon không tiếp cận khách của agency.

## Chúng tôi làm
- [Pitch mẫu 48 giờ](/pitch-48-gio/)
- [Ảnh AI và key visual](/dich-vu/anh-ai/), [video AI](/dich-vu/video-ai/), [nhân vật và giọng AI](/dich-vu/nhan-vat-giong-ai/)
- [Brand kit hằng tháng](/brand-kit/)

## Liên hệ
Xem [trang liên hệ](/lien-he/).""")

add(path="/lien-he/", kenh="trang-lien-he", cta=False, form=["form-brief", "form-goi-lai"],
 title="Liên hệ Unikon: gửi brief pitch hoặc để lại số",
 desc="Gửi brief pitch cho Unikon hoặc để lại số để chúng tôi gọi lại. Đơn vị AI production cho agency, giao trắng nhãn, báo giá theo giá sàn.",
 vet=[("Liên hệ", "/lien-he/")], h1="Liên hệ Unikon",
 mo="Có brief thì gửi ở form đầu. Chưa có brief, để lại số ở form thứ hai, chúng tôi gọi lại trong giờ làm việc.",
 ghi_chu="Số điện thoại, Zalo, email và địa chỉ đang chờ Unikon cung cấp. Trong lúc chờ, để lại thông tin, chúng tôi liên hệ.",
 than="""## Hai cách bắt đầu
- **Gửi brief pitch**: nhận ba hướng ý tưởng, deck trắng nhãn, báo giá.
- **Để lại số**: chúng tôi gọi lại hỏi thêm về pitch của bạn.""")

FAQ_ALL = [
 ("AI production cho agency là làm gì?", "Là sản xuất asset sáng tạo bằng AI cho chiến dịch của agency: ảnh, video, nhân vật và giọng AI. Agency giữ khách và ý tưởng lớn, Unikon làm phần sản xuất, có người duyệt từng asset và giao dưới tên agency."),
 FAQ_TRANG_NHAN,
 ("Pitch mẫu 48 giờ gồm những gì?", "Ba hướng ý tưởng, mỗi hướng có câu ý tưởng và hình mẫu làm bằng AI, gói trong một deck trắng nhãn mang logo agency. Kèm báo giá sản xuất theo giá sàn từng loại asset."),
 FAQ_GIA,
 ("Thu tiền thế nào?", "Hoá đơn theo từng job. Nhãn chạy đều hằng tháng thì có thêm phí Brand kit hằng tháng."),
 ("Asset AI có an toàn để chạy cho nhãn hàng lớn không?", "Mỗi asset được người duyệt trước khi giao: bàn tay, chữ, khuôn mặt, logo, màu thương hiệu. Không dùng gương mặt hay giọng người thật khi chưa có hợp đồng."),
 FAQ_NGUOI_THAT,
 ("Brief của agency được giữ thế nào?", "Brief chỉ dùng để làm pitch và sản xuất cho bạn. Tên agency và tên khách chỉ xuất hiện trong case khi cả hai bên cho phép bằng văn bản."),
 ("Có xem được việc Unikon đã làm không?", "Có, qua deck credential trắng nhãn gửi theo yêu cầu. Tên khách chỉ nêu khi được phép."),
 ("Bộ kiểm an toàn thương hiệu là gì?", "Danh sách điểm cần soát trước khi đưa asset AI cho khách duyệt. Để lại email ở trang an toàn thương hiệu, chúng tôi gửi cho bạn."),
]
add(path="/hoi-dap/", kenh="trang-hoi-dap",
 title="Hỏi đáp về AI production cho agency · Unikon",
 desc="Mười câu agency hay hỏi Unikon: pitch mẫu 48 giờ, trắng nhãn, giá sàn, thu tiền, an toàn thương hiệu, người thật trong asset AI, dữ liệu brief.",
 vet=[("Hỏi đáp", "/hoi-dap/")], h1="Hỏi đáp về AI production cho agency",
 mo="Câu hỏi agency hay gửi trước khi giao brief đầu tiên. Không thấy câu của bạn thì ghi vào brief.",
 than="", hoi_dap=FAQ_ALL)

add(path="/cam-nang/", kenh="trang-cam-nang",
 title="Cẩm nang AI production cho agency · Unikon",
 desc="Bài viết của Unikon cho account manager, producer và creative director: làm pitch có hình AI, giữ an toàn thương hiệu, chọn đơn vị AI production.",
 vet=[("Cẩm nang", "/cam-nang/")], h1="Cẩm nang cho agency làm việc với AI",
 mo="Bài viết ngắn, dùng được ngay cho pitch tuần này.",
 than="""## Bài trụ
- [AI production cho agency: chọn đơn vị, gửi brief, giữ an toàn thương hiệu](/ai-production-cho-agency/)

## Sắp có
- Viết brief cho pitch có hình AI trong năm phút.
- Mười điểm soát trước khi đưa asset AI cho khách duyệt.
- Khi nào một nhãn hàng nên có Brand kit cho nội dung AI.""")

add(path="/chinh-sach-du-lieu/", kenh="trang-chinh-sach", cta=False,
 title="Chính sách dữ liệu · Unikon",
 desc="Unikon thu gì khi bạn gửi brief, để lại số hay đăng ký nhận bộ kiểm, dùng vào việc gì, giữ bao lâu và cách bạn yêu cầu xoá. Bản nháp chờ pháp chế.",
 vet=[("Chính sách dữ liệu", "/chinh-sach-du-lieu/")], h1="Chính sách dữ liệu",
 ghi_chu="Bản nháp theo Nghị định 13/2023/NĐ-CP, chờ pháp chế Unikon duyệt. Tên pháp nhân và đầu mối nhận yêu cầu sẽ cập nhật khi chốt.",
 than="""## Chúng tôi thu gì
- Form brief: họ tên, agency, vai trò, điện thoại hoặc email, hạn pitch, khách hàng cuối (có thể ẩn), loại asset, ngân sách, nội dung brief.
- Form gọi lại: họ tên, số điện thoại.
- Form bộ kiểm: họ tên, email, agency.
- Kèm theo: thời điểm gửi, câu đồng ý bạn đã tick, địa chỉ IP, nguồn truy cập (đường dẫn có `kenh` hoặc `utm`).

## Dùng vào việc gì
- Liên hệ về brief, gọi lại, gửi bộ kiểm.
- Không bán, không chia sẻ cho bên thứ ba ngoài đơn vị hỗ trợ vận hành đã ký cam kết bảo mật.

## Giữ bao lâu và xoá
Thời hạn lưu chờ pháp chế chốt. Bạn có thể yêu cầu xem, sửa hoặc xoá dữ liệu bằng cách để lại thông tin ở [trang liên hệ](/lien-he/) và ghi "yêu cầu dữ liệu".

## Ô đồng ý
Ô đồng ý trên mọi form không bao giờ được tick sẵn. Chúng tôi lưu nguyên văn câu bạn đồng ý cùng thời điểm.""")

add(path="/cam-on/", kenh="trang-cam-on", cta=False, cam_on=True, noindex=True,
 title="Cảm ơn bạn · Unikon",
 desc="Unikon đã nhận thông tin của bạn. Mã ghi bên dưới, dùng khi trao đổi với chúng tôi. Bước tiếp theo và cách chuẩn bị cho pitch của bạn.",
 vet=[("Cảm ơn", "/cam-on/")], h1="Đã nhận, cảm ơn bạn",
 mo="Thông tin của bạn đã vào hệ thống. Giữ mã bên dưới để tiện trao đổi.",
 than="""## Bước tiếp theo
- Với brief pitch: chúng tôi liên hệ lại để xác nhận hạn pitch và những gì còn thiếu.
- Với yêu cầu gọi lại: chúng tôi gọi trong giờ làm việc.

## Trong lúc chờ
- Xem [pitch mẫu 48 giờ](https://demo.unikon.vn/?kenh=trang-cam-on) để biết deck trông thế nào.
- Đọc [cách tính giá](/bao-gia/) và [an toàn thương hiệu](/an-toan-thuong-hieu/).""")

add(path="/404.html", kenh="trang-404", cta=False,
 title="Không tìm thấy trang · Unikon",
 desc="Trang bạn tìm không có hoặc đã đổi địa chỉ. Quay về trang chủ Unikon hoặc gửi brief pitch.",
 vet=[("Không tìm thấy", "/404.html")], h1="Không tìm thấy trang này",
 mo="Địa chỉ có thể đã đổi. Bạn thử một trong các trang dưới.",
 than="""- [Trang chủ](/)
- [Pitch mẫu 48 giờ](/pitch-48-gio/)
- [Dịch vụ](/dich-vu/)
- [Liên hệ](/lien-he/)""")

for i, p in enumerate(P):
    (D / f"{i + 1:02d}-{p['path'].strip('/').replace('/', '-').replace('.html', '')}.json").write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(P), "trang")
