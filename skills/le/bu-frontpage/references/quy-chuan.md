# Quy chuẩn trang + kênh của một BU (rút từ event.ifagent.net, 9/11)

Phạm vi: frontend, giao diện, flow lấy lead, own media, GEO của **một BU**. Không đụng lõi engine: form chỉ cần một máy nhận lead nhỏ, khi lõi xong thì đổi đúng một hàm `guiDi()`.

Bản mẫu chạy được: `vong-1/event-site/` (Linh chọn phương án A). BU mới chép thư mục này, thay chữ và token.

## 1. Đầu vào bắt buộc trước khi dựng
| Thứ | Ai đưa | Thiếu thì |
|---|---|---|
| Ba câu khách hỏi đầu tiên (event: giá, thời gian dựng, case gần nhất) | chủ BU | không dựng |
| Danh mục giải pháp, mỗi cái nói theo đầu ra cho khách | chủ BU | không dựng |
| Gói dựng sẵn (2–3 gói), giá hoặc khoảng giá, thời gian dựng | chủ BU | để chữ an toàn trong `cau-hinh.json`, gắn `data-can-xac-nhan` |
| Case có số, ảnh thật, khách được nêu tên | chủ BU | **không có khối case**, không bịa |
| Brand: logo, màu, chữ | LAB043 | không dựng |
| Người nhận lead + cam kết giờ phản hồi | chủ BU | không mở form |

## 2. Khung trang (theo thứ tự)
1. Hero: một câu nói khách được gì; 2 nút (gửi brief, thử demo); dải 3 dữ kiện trả lời ba câu hỏi; hình là **thứ thật đang chạy** (minh hoạ phải ghi "Minh hoạ").
2. Giải pháp: một cái chính lớn hơn, không lưới thẻ giống hệt nhau.
3. Gói dựng sẵn + "gói nào cũng có" + công cụ ba câu gợi ý gói (mồi lead, điền sẵn form).
4. Cách làm: 4 bước từ brief tới bàn giao, có cam kết sau bàn giao (event: báo cáo 24 giờ).
5. Form brief: bên trái "bạn nhận lại gì" + người liên hệ thật; bên phải form.
6. Hỏi đáp: 5–6 câu, có câu về giá và về dữ liệu khách.

## 3. Form lead (luật cứng)
- Bắt buộc: họ tên, công ty, **một trong hai** điện thoại/email, ô đồng ý **không tick sẵn**.
- Giữ nguồn: `?kenh=`, `ref`, `utm_*` lưu theo phiên, gửi kèm lead. Ghi gói được gợi ý.
- Bẫy bot (ô ẩn), giới hạn 5 lần/10 phút/IP, thân ≤ 20 KB.
- Lưu: mã lead `XX-yymmdd-xxxx`, thời điểm, câu đồng ý nguyên văn, IP. Báo tin Telegram hoặc Sheet qua biến môi trường, không ghi bí mật vào repo.
- Lỗi thì luôn chỉ đường lùi (Zalo người phụ trách).

## 4. Khoá giao diện
- `DESIGN.md` (token + Nên/Không nên) → `DESIGN.khoa` băm DESIGN.md, site.css, index.html → ảnh chuẩn màn đầu 5 cỡ trong `khoa/anh-chuan/`.
- Mọi sửa sau khoá: chạy cổng, lệch thì Linh duyệt rồi mới `--chup-chuan` lại.

## 5. Cổng máy (`node kiem/kiem.cjs <url>`, lỗi nào cũng chặn)
K1 băm khoá khớp · K2 màu ngoài token (cảnh báo) · K3 không tràn ngang ở 1280/1024/768/390/360 · K4 chạm ≥ 44 px · K5 không đoạn chữ < 14 px, chữ thân ≥ 16 px · K6 không ảnh hỏng · K7 form gửi được, lead về có mã · K8 màn đầu khớp ảnh chuẩn.
Sau cổng máy: soát mùi AI (5 cụm mặc định, danh sách dấu hiệu văn AI tiếng Việt), kiểm tay bằng bàn phím, chấm mù 3 người (≤ 1/3 đoán AI làm), rồi Linh duyệt.

## 6. GEO / SEO tối thiểu trên trang
- JSON-LD: `Organization` (contactPoint thật), `Service` + `OfferCatalog` các gói, `FAQPage` trùng nguyên văn câu hỏi đáp trên trang.
- `canonical`, `description` nói đúng việc + nơi, `lang="vi"`.
- Cụm từ BU muốn sở hữu nằm trong h1/h2 và FAQ (event: "công nghệ sự kiện", "sự kiện AI", "photobooth AI").
- Sau khi lên: trang trụ + 10–20 bài theo kho vấn đề khách, mỗi bài trỏ về form với `?kenh=bai-<slug>`; đo AI có nhắc BU khi hỏi cụm từ đó (LAB036).

## 7. Own media nối vào trang
- Mỗi link ra ngoài mang `?kenh=<kênh>-<mã bài>` + `utm_source/medium/campaign`; Zalo không dùng link rút gọn.
- Lịch: ≤ 3 bài/ngày, cùng kênh cách ≥ 2 ngày, bài dài trước, mảnh ngắn sau; mỗi dòng lịch có File, Link đo, Người duyệt, Trạng thái.
- Theo pha sự kiện (trước/trong/sau) khi BU bán cho sự kiện; follow-up lead trong 24 giờ.
- Đo bằng lead theo kênh, không đo bằng lượt mở.

## 8. Triển khai
Node ≥ 18 chạy `server.mjs` sau HTTPS; không đổi DNS trang đang có lead thật trước khi chạy song song đủ; giữ đường dẫn cũ bằng 301.

## Còn mở cho IF Agent Event
Giá và thời gian dựng thật của 3 gói, cam kết 1 ngày làm việc, case có số + ảnh thật, người giữ Facebook/Zalo OA/LinkedIn.
