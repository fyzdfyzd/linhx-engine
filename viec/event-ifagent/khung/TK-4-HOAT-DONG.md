# TK-4 · Khung A cho video booth, AR, game đông người, vòng quay, tường clip (Hứa Chử)
Thiết kế · Chân Cơ · 14/11/2026 · commit `1a63a1d`, nhánh `claude/project-thread-9c61ql`

## 1. Video booth (khuôn TK-2, 390 và kiosk 1080×1920)
- HTML: `docs/thiet-ke/event-web/man-khach/video-*.html`, sinh bằng `sinh-man-video.py` (dùng CSS của `sinh-man-khach.py`).
- Ảnh: `NOP/thiet-ke/man-khach/video-*-1a63a1d.png` (23 tấm).
- **Màu nhấn Xanh điện #0088FF, chữ trên nút màu trắng** (thay màu ngọc ở bản dựng 17c71bc0). Ngọc chỉ dùng cho dấu ✓ bước đã xong.
- Chữ đúng theo `hua-chu/CHU-TREN-MAN-VIDEO-BOOTH.md`, gồm 2 chỗ sửa của Quách Gia: chip viết hoa chữ đầu; câu hết lượt "Hôm nay máy này đã dùng hết lượt quay. Hẹn bạn ngày mai nhé."

| Tệp | Cỡ | Ghi chú |
|---|---|---|
| video-1-chon-kieu | 390, 1080 | 390: thẻ ngang (ảnh 96 px bên trái, tên và mô tả bên phải). Kiosk: 3 cột, chữ đè đáy ảnh. Nút **Quay với kiểu này** |
| video-2-quay | 390, 1080 | khung 3:4, viền gợi ý dáng, số đếm 3 · **Đổi kiểu** + **Quay** |
| video-2a-dang-quay | 390, 1080 | nhãn đỏ "Đang quay" góc trái khung · thanh "3/10 giây" màu nhấn · nút **Dừng** (chỉ kiểu Lời chúc) |
| video-2b-xem-lai | 390, 1080 | nút phát giữa khung · **Quay lại** + **Lưu clip** · câu đồng ý dưới nút |
| video-2c-dang-luu | 390, 1080 | ảnh mờ · "Đang gửi clip" + % |
| video-3-nhan-clip | 390, 1080 | khung clip có dải dưới (tên sự kiện trái, "Chạy bằng IF Agent" phải). Kiosk: QR 280 px bên phải + **Quay lượt mới**. 390: **Lưu clip về máy** + **Quay lượt mới**, dòng hạn, link Xoá clip này |
| video-4-trang-xem | 390 | trang mở từ QR: Lưu clip về máy, dòng hạn, Xoá clip này (chỉ máy đã quay), Báo clip không phù hợp |
| video-4b/4c/4d | 390 | Đã xoá · Đã báo · Không tìm thấy clip |
| video-5a/5b/5c | 390, 1080 | thẻ "Chưa xong" + **Thử lại** + link Đổi kiểu |
| video-5d-cau-bao-khac | 390 | 4 câu báo khác (hết lượt, clip quá dài, trình duyệt không quay được, sự kiện chưa mở) dùng cùng thẻ |

Chân trang điện thoại có link "Làm video booth này cho công ty bạn →" như luật 6 của TK-2 (chữ mới, chờ Sản phẩm). Ảnh thẻ kiểu là ảnh tạm; ảnh thật lấy từ hàng gen mục B.

## 2. AR, game đông người, vòng quay, tường clip (nền Đêm, màu nhấn Xanh)
- HTML: `docs/thiet-ke/event-web/a/80-*.html` đến `87-*.html`, sinh bằng `sinh-khung-hoat-dong.py`.
- Ảnh: `NOP/thiet-ke/hoat-dong/*-1a63a1d.png` (30 tấm). Màn lớn đều vừa đúng 1920×1080, 390 không cuộn ngang.
- Chữ lấy từ `_che-do/*/mau.json` và câu lỗi máy chủ (`game/phong.js`, `vong-quay/index.js`). Mã phòng 5 ký tự theo máy chủ.

| Tệp | Cỡ | Nội dung |
|---|---|---|
| 80-ar-1-chon | 390 | lời mời của mẫu · khung camera có viền gợi ý · hàng lens tròn (tên lens; ảnh lens chờ gen, lens chưa có ảnh thì ẩn) · nút chụp tròn · Đổi camera |
| 80-ar-2-xem-lai / 80-ar-3-nhan-anh | 390 | Lưu ảnh + Chụp lại + câu đồng ý · Ảnh của bạn đây, Lưu ảnh về máy, dòng hạn, Xoá ảnh này |
| 80-ar-4-may-tinh | 1440 | "Mở trên điện thoại để thử" + QR |
| 81-game-1-vao-phong / 1b-loi | 390 | 5 ô mã phòng · tên hiện trên màn lớn · lỗi tên trùng dưới ô · thẻ lỗi: không tìm thấy phòng, đủ người, đã kết thúc, mất kết nối |
| 81-game-2-sanh-cho / 3-man-lon-cho | 390 / 1920 | Chào <tên>, số người đã vào, đội của bạn · màn lớn: QR 300 px, mã phòng cỡ lớn, tên khách vừa vào |
| 82-dua-cham | 390 / 1920 | nút Chạm tròn màu đội, đếm giờ, số chạm của bạn, thanh so 2 đội · màn lớn: 2 cột năng lượng, số mỗi đội |
| 83-binh-chon | 390 / 1920 | 4 lựa chọn A–D, thanh thời gian, trạng thái Đã chọn · màn lớn: thanh %, lựa chọn dẫn đầu sáng hơn |
| 84-do-vui | 390 / 1920 | câu hỏi + 4 đáp án · Đúng rồi +860, hạng, tổng điểm · Chưa đúng + đáp án · màn lớn câu hỏi + số người đã trả lời · bảng xếp hạng top 10 + 3 người lên sân khấu |
| 85-game-dieu-khien | 390, 1440 | màn người dẫn chương trình: các câu và trạng thái, nút bước tiếp theo, đường mở màn lớn, tên bị bộ lọc giữ lại |
| 86-vong-quay | 390 / 1920 / 1440 | để lại liên lạc + đồng ý → Quay → Bạn trúng + mã VQ- → Máy này đã quay rồi · màn lớn: vòng quay + người vừa trúng (tên rút gọn) · quầy đổi quà: kiểm mã, Đã trao quà, quà còn lại |
| 87-video-tuong | 1920 / 390, 1440 | tường 16 clip 9:16 có thời lượng, một nhãn Dữ liệu mẫu ở đầu · duyệt clip: Hiện · Gỡ |

## Ghi chú cho Build
1. Màu đội Xanh #0088FF và Cam #FF7A1A lấy từ cấu hình mẫu đua chạm; chiến dịch thật đổi theo nhận diện. Ô vòng quay tô theo màu `qua[].mau` của cấu hình. Vành và kim vòng quay là ảnh gen (mục C), khung đang vẽ chỗ đặt.
2. Đường "event.ifagent.net/choi/<mã>/man-lon" ở màn điều khiển là chỗ đặt. Build thay bằng đường thật.
3. Mọi tên khách trên màn lớn đi qua bộ lọc chung. Tên bị giữ hiện ở màn điều khiển, không lên màn lớn.

## Chờ Sản phẩm (chữ Thiết kế viết thêm)
- AR: "Ảnh chỉ nằm trên máy bạn cho tới khi bạn bấm Lưu.", "Mở trên điện thoại để thử", câu đồng ý của AR (chép theo câu video booth).
- Game: "Vào phòng chơi", "Mã phòng hiện trên màn lớn.", "Tên hiện trên màn lớn", "Chạm thật nhanh!", "Đúng rồi", "Chưa đúng", "Còn 3 câu, vẫn kịp leo bảng.", "Điều khiển phòng chơi", "Mời ra khỏi phòng".
- Vòng quay: "Gửi và quay", "Bạn trúng", "Đưa mã này cho quầy đổi quà.", "Máy này đã quay rồi", "Quầy đổi quà", "Đã trao quà".
- Video booth: nút "Quay với kiểu này", link chân trang "Làm video booth này cho công ty bạn →".

## Sửa kèm theo commit này
- Trình tạo 21–23 (theo SP-DOC-CHU-TK-1 mục cuối): logo tối đa 2 MB; tên ô bước 4 là "Lời chào trên màn", "Câu mời chụp", "Chữ trên khung ảnh", "Dòng nhỏ đầu trang"; bỏ nút "+ Thêm giải pháp". Ảnh: `anh/a-2[123]-*-1a63a1d.png`.
- Liên lạc khách 40, 41: nhãn nguồn "Kiosk" đổi thành "Tại sự kiện"; thêm một dòng mẫu từ vòng quay để nhãn hiện trên màn. Ảnh: `them/*-1a63a1d.png`.

## Lần sửa 1 (1a63a1d)
- Sản phẩm S1–S7 (SP-DOC-CHU-TK-4.md): "Quay lần nữa" và câu xem lại; "…bấm Lưu ảnh."; "Trò chơi đông người"; "Đội được chia đều tự động."; "Thử vận may nhận quà"; "Đã quá 1 giờ, bạn gửi lại liên lạc nhé."; thêm dấu chấm ở 2 câu báo màn vào phòng.
- Chấm (cham1): vòng quay 86-1, ô đồng ý **để trống mặc định**; nút **Gửi và quay mờ và không bấm được cho tới khi khách tick**, dòng dưới nút "Đánh dấu đồng ý để quay. Mỗi máy quay một lần." Màu ô quà mẫu theo DS: Giấy #F4F6F8, Xanh #0088FF, #0066CC, #2E9FF8, ô may mắn #1C2638. Chiến dịch thật đổi theo nhận diện qua `qua[].mau`.
- Trình tạo 23: ô lỗi bộ lọc dùng chữ mẫu có địa chỉ web lạ ("xem thêm tại mocgiamgia.shop") cho đúng câu "Có chữ chưa dùng được."

## Lần sửa 2 (66a479d)
Màn 85: câu 4 "Trò chơi đông người trên điện thoại…". Câu hỏi mẫu nằm trong _che-do/game/mau.json nên Build sửa cả ở đó.
