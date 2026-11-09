# Soát giọng và dấu hiệu văn AI · gói own media IF Agent Event

Ngày soát: 9/11/2026. Người soát: Claude. Phạm vi: `bai-tru-cong-nghe-su-kien.md`, `lich-3-pha-csmo.md`, `bai-mxh.md`, `thu-follow-up.md`.
Cách soát: đọc lại từng bài, rồi quét bằng script Python trên cả bốn file cho các mẫu chữ bên dưới. Phần ghi chú cho người duyệt và cột mô tả trong lịch cũng được quét.

Kết luận: **sạch** sau lượt sửa. Bản cuối không còn mẫu nào trong danh sách chặn. Còn hai điểm giữ lại có chủ ý, ghi ở mục cuối.

## 1. Kết quả quét theo từng dấu hiệu

| Dấu hiệu | Cách quét | Lượt đầu | Bản cuối |
|---|---|---|---|
| "Không phải X mà là Y", "không chỉ... mà còn" | tìm "không phải", "không chỉ", "mà là", "mà còn" | 2 chỗ dạng đối lập "là tin trả lời, không phải broadcast" (bai-mxh ZL-S1, lịch dòng 20/11) | 0. Các chỗ "không phải cài ứng dụng" còn lại mang nghĩa đen là không cần cài |
| Chuỗi phủ định "không X, không Y, không Z" | tìm ba vế "không" liền nhau | 0 | 0 |
| Tự hỏi tự đáp ("Kết quả? ...") | tìm dấu "?" trong thân bài, trừ tiêu đề h2 và câu hỏi FAQ | 1 câu hỏi tu từ ở CTA bài trụ ("Bạn đang chuẩn bị ... chạy với logo của mình?") | 0. Dấu hỏi chỉ còn ở tiêu đề h2 dạng câu hỏi (theo yêu cầu GEO) và sáu câu FAQ |
| Hai chấm bật mí | đọc mọi dấu ":" giữa câu | 1 chỗ ở LI-S2 ("học được một điều ...: [điền]") | 0. Dấu ":" còn lại chỉ dẫn vào danh sách, nhãn trường (Link, Cần ảnh, Tiêu đề) hoặc câu FAQ chép nguyên văn từ trang chủ |
| Gạch ngang dài (— và –) | quét ký tự | 0 (khi viết đã dùng "đến", "và" thay gạch nối khoảng ngày) | 0 |
| Mỗi câu một dòng | đọc bố cục từng bài | 0. Bài viết thành đoạn 2 đến 4 câu | 0 |
| Câu mồi "Bạn nghĩ sao?", "Còn bạn?", "Comment bên dưới" | tìm cụm | 0 | 0 |
| Emoji làm gạch đầu dòng | quét dải ký tự emoji | 0 | 0 |
| Từ sáo rỗng | tìm: toàn diện, nâng tầm, đột phá, bứt phá, cách mạng, kỷ nguyên, hành trình, hệ sinh thái, liền mạch, tối ưu, mở khoá, trao quyền, khám phá, tóm lại, thời đại, hàng đầu, số 1, duy nhất, vượt trội, ấn tượng, đẳng cấp, tuyệt vời | 1 chữ "duy nhất" (lịch, mục luật: "Ngoại lệ duy nhất là 19 và 20/11") | 0 |
| Câu kết kiểu châm ngôn | đọc câu cuối từng bài | 1 câu ở FB-T2 ("vì sự cố ở sự kiện thì không có lần thứ hai") | 0 |
| Liệt kê ba vế đối xứng | đọc các đoạn "Nếu... Nếu... Nếu", "Cần... thì" | LI-T1 có ba câu "Nếu" giống khuôn; EM-T1 chép lại đúng khuôn ba câu "Cần... thì" của đoạn mở bài trụ | Đã phá khuôn ở LI-T1 và viết lại đoạn EM-T1. Đoạn mở bài trụ giữ ba vế, xem mục 3 |
| Swap test (thay "IF Agent" bằng đối thủ mà câu vẫn đúng) | đọc câu nhận định | Vài câu chung chung ở LI-T2, LI-T3 | Mỗi bài đã có ít nhất một chi tiết riêng của IF Agent: ô đồng ý để trống, báo cáo 24 giờ với bốn chỉ số, mốc dựng theo gói, CSMO tại Ascott Tây Hồ |

## 2. Soát sự thật (khối chặn)

| Vấn đề | Chỗ | Đã sửa |
|---|---|---|
| Nói quá điều trang chủ cam kết: "nhân vật sẽ không tự nói về giá hay khuyến mãi" | bài trụ, mục ba loại tương tác | Bỏ, giữ đúng câu của trang chủ "Câu trả lời chỉ nằm trong nội dung bạn đã duyệt" |
| Tự nhận "những câu khách hỏi IF Agent nhiều nhất" khi không có số | bài trụ, đoạn thứ hai | Bỏ câu |
| Bịa quy trình chạy thử ("rút dây mạng ra để xem thiết bị dự phòng có nhận ngay không") | FB-T2 | Viết lại theo đúng trang chủ: chạy thử trên thiết bị thật, đi hết các bước khách sẽ làm |
| Bịa kinh nghiệm "phần lớn sự cố chúng tôi từng xử lý", "ba dòng hay bị bỏ sót nhất" | LI-T2 | Đổi thành nhận định chung và lời mời đọc kỹ, không tự nhận số liệu |
| Bịa giờ cụ thể "Sáu giờ sáng" | FB-S1 | Thay bằng [ĐIỀN TẠI CHỖ: giờ thật] |
| Tự nhận "hai câu được hỏi nhiều nhất ở CSMO" trước khi sự kiện diễn ra | FB-H2 | Đổi thành "hai câu người tổ chức hay hỏi IF Agent trong buổi gặp đầu tiên" |
| EM-T1 và LI-T1 hứa "xem bài đầy đủ" nhưng link trỏ về form | EM-T1, LI-T1 | Bỏ lời hứa; ghi chú đổi link sang `/cong-nghe-su-kien` khi trang đó lên |
| Ghi "đã chạy" trước sự kiện | toàn bộ pha trước | Đã kiểm: pha trước chỉ dùng "sắp chạy". "Đã chạy xong" chỉ xuất hiện ở ZL-H1, đăng ngày 23/11 |
| Dùng dữ liệu khách của bên tổ chức để gửi thư | EM-H1 | Ghi rõ chỉ gửi cho người để lại liên hệ trực tiếp với IF Agent; không dùng danh sách khách CSMO |
| Tên khách, lời khen, giá | cả bốn file | Không có. Không nêu tên khách hàng nào ngoài sự kiện CSMO Summit 2026. Không có giá; dải ngân sách trong form không được viết thành giá |

## 3. Giữ lại có chủ ý

1. Đoạn mở bài trụ có ba câu song song "Cần... thì chọn...". Giữ vì đây là đoạn để AI trích, và IF Agent đúng là có ba giải pháp; mỗi câu gắn một mục tiêu khác nhau. Các bài khác đã tránh lặp khuôn này.
2. Câu FAQ "Sau sự kiện tôi nhận được gì?" có dạng "Trong 24 giờ: báo cáo số đo...". Giữ nguyên văn vì JSON-LD FAQPage trên trang chủ dùng đúng câu này, sửa ở đây sẽ làm lệch hai nơi.

## 4. Giọng

- Xưng hô: bài trụ gọi "bạn" theo trang chủ. Bài mạng xã hội và Zalo gọi "anh chị". Thư follow-up gọi "anh/chị" để người gửi sửa theo từng khách. Tin Zalo của chị Hằng xưng "em" vì gửi từ Zalo cá nhân.
- LinkedIn: câu đủ ý, có lý do cho từng lựa chọn, không dùng từ cảm thán.
- Facebook: câu ngắn hơn, có "nhé", "đội mình", kể việc đang làm.
- Zalo OA: một đoạn, một link đầy đủ, không rút gọn.
- Tên giải pháp giữ cố định ở mọi bài: nhân vật AI biết nói (tiếng Việt), AI Photobooth, minigame quét QR.

## 5. Việc người duyệt còn phải làm
- Chấm mù và đọc to theo QUY-CHUAN-BU mục 5 chưa làm; phần này máy không thay được.
- Các chỗ [CHỜ SỐ], [CHỜ XÁC NHẬN], [ĐIỀN TẠI CHỖ] phải điền hoặc xoá cả câu trước khi đăng. Sau khi điền, soát lại riêng câu vừa điền theo bảng ở mục 1.
