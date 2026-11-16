# TK-5 · Mail, trang 404, trang lỗi chung, thẻ "Sắp ra mắt", khuôn ảnh OG
Thiết kế · Chân Cơ · 14/11/2026 · commit `659dea8`, nhánh `claude/project-thread-9c61ql`
- Sinh bằng `docs/thiet-ke/event-web/sinh-khung-mail-loi.py`. Ảnh: `NOP/thiet-ke/mail-loi-og/*-659dea8.png` (24 tấm).

## 1. Mail (`mail/*.html`, khung bảng 600 px, chụp ở 680 và 390)
Mỗi mail có 2 bộ màu: **sáng** (nền #EEF1F5, thẻ trắng, chữ Đêm, link #0066CC) và **tối** (nền #05080F, thẻ #131C2E, chữ #F4F6F8, link #2E9FF8). Đầu mail luôn là dải Đêm có logo sáng, nên logo không đổi theo chế độ. Nút Xanh #0088FF chữ trắng, cao 52. Trên điện thoại nút giãn hết ngang. Build dựng bằng bảng và CSS nội dòng, thêm `@media (prefers-color-scheme: dark)` cho bộ tối.

| Tệp | Gửi tới | Tiêu đề · dòng xem trước | Nội dung |
|---|---|---|---|
| m1-bao-team | hộp chung team | **Liên lạc mới · <Công ty> · <nguồn>** · "<Tên> · <Công ty> · mở trong trang quản lý" | nhãn "Liên lạc mới", H1 "<Công ty> vừa để lại liên lạc", bảng Tên · Công ty · Nguồn · Lúc, nút **Mở trong trang quản lý**, dòng "Gọi lại trong 24 giờ như đã hứa với khách." Chân: không có SĐT, email trong mail (đúng chốt của anh Linh) |
| m2-de-xuat-pdf | khách | **Đề xuất sự kiện của bạn · <tên ý tưởng>** | "Chào <Tên>," · câu dẫn · thẻ đề xuất (hình thử, mã, tên ý tưởng, 1 câu) + nút **Xem bản trên web** · ô tệp đính kèm `de-xuat-<ma>.pdf · PDF · 2 trang` · "Muốn làm thật…? Trả lời mail này, hoặc để team IF Agent làm thật. IF Agent sẽ gửi báo giá sau." |
| m3-cam-on | khách để lại liên lạc | **IF Agent đã nhận thông tin của bạn** | "Đã nhận. Team IF Agent sẽ liên hệ trong 24 giờ." (câu đã duyệt §6.2) · 3 demo + nút **Vào phòng demo** |
Chân mail khách: lý do nhận mail, "Xem cách IF Agent giữ dữ liệu" (`/bao-mat`), "Xoá thông tin của tôi".

## 2. Trang lỗi (`a/91`, `a/92`, 390 và 1440)
- **404:** nhãn "404" · H1 "Trang này không có ở đây." (§4.11) · câu "Đường dẫn có thể đã đổi. Bạn về trang chủ hoặc thử ngay cho công ty bạn." · **Về trang chủ** + **Thử cho công ty bạn →**. Có đầu trang, chân trang, một nhát cắt 34°.
- **Lỗi chung:** nhãn "Chưa tải được" · H1 câu chuẩn "Có chút trục trặc. Bạn bấm thử lại nhé." · "Nếu vẫn chưa được, bạn quay lại sau ít phút." · **Thử lại** + **Về trang chủ**. Mất mạng dùng câu chuẩn "Mất kết nối. Kiểm tra mạng rồi thử lại."

## 3. Thẻ "Sắp ra mắt" trong phòng demo (`a/93`, 390 và 1440)
Ba trạng thái trên cùng một thẻ, không rời phòng demo:
1. **Đóng:** ảnh mờ 62%, nhãn "Sắp ra mắt", link "Báo tôi khi demo mở →".
2. **Mở:** ô Email, ô đồng ý **để trống** "Tôi đồng ý nhận một email báo khi demo mở.", nút **Báo tôi khi demo mở**. Lỗi ô: "Email chưa đúng, thử lại nhé."
3. **Đã gửi:** "Đã ghi. IF Agent báo bạn khi demo mở." Máy này nhớ đã gửi.
Liên lạc vào kho lead với `nguonChiTiet = demo-cho-<slug>` (bản đồ §4.3).

## 4. Khuôn ảnh OG 1200×630 (`og/*.html`)
Ảnh từ hàng chờ nằm ở 62% bên phải. Lớp Đêm phủ từ trái sang để chữ luôn đọc được. Nhãn Montserrat 18 px · tiêu đề Be Vietnam Pro 500, 60 px (52 px khi tiêu đề dài, tối đa 3 dòng) · logo sáng + đường dẫn ở đáy · một nhát cắt 34° góc phải dưới.
| Tệp | Dùng cho |
|---|---|
| og-blog, og-blog-tieu-de-dai | bài blog: "Blog · <nhóm>" + tên bài |
| og-demo | trang demo có ảnh: "Demo · <giải pháp>" + tên demo + "Bấm là thử" |
| og-demo-nhan-vat | demo nhân vật: PNG nhân vật trên nền chuyển xanh, đứng sát đáy |
| og-demo-sap-ra-mat | demo sắp ra mắt: thêm nhãn "Sắp ra mắt" |
| og-mac-dinh | trang không có ảnh riêng: chữ 88 px |
Build sinh ảnh bằng cách chụp khuôn HTML này ở 1200×630 (cùng Playwright), không vẽ lại. Ảnh thật lấy từ hàng chờ của Thái Văn Cơ.

## Chờ Sản phẩm
Tiêu đề mail báo team đổi "Lead mới" thành "Liên lạc mới" theo luật không dùng "lead" (bản đồ §6.3 đang ghi `Lead mới`). Các câu Thiết kế viết thêm: câu phụ 404, câu phụ lỗi chung, chữ trong 3 mail ngoài câu đã duyệt, "Đã ghi. IF Agent báo bạn khi demo mở.", "Email chưa đúng, thử lại nhé.", "Sự kiện có AI, bấm là thử" (OG mặc định).

## Lần sửa 1 (659dea8)
- Sản phẩm (SP-DOC-CHU-TK-5): trang lỗi chung bỏ vế "Những gì bạn đã nhập vẫn được giữ."
- Chấm (cham1): mail M2 dùng hình thử của xưởng (img/e1-kiosk.jpg, cùng ảnh ở khung đề xuất và PDF) thay ảnh sự kiện thật. Build lấy đúng hình thử của đề xuất đó.
