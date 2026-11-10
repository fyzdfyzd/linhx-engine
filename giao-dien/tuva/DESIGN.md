---
name: TUVA Communication · tuva.work
version: 1.0 (khoá 9/11/2026, phương án B "Tự chấm ngay màn đầu", Claude khuyến nghị, chờ Linh xác nhận)
nguon_brand: LAB043-DESIGN-ONBRAND/brands/tuva (brand.json, LUAT-ONBRAND.md, guideline 3.5 Website)
colors:
  nau: "#2A1E1A"        # Nâu đen: đầu trang, màn đầu, khối đề xuất, chân trang, chữ chính
  cam: "#F9A61B"        # Cam hổ phách: nút chính, tiêu đề trên nền nâu, xoắn ốc, vạch nhấn
  trang: "#FFFFFF"
  be: "#E4DCD5"         # Be ấm: khối dịch vụ chính, vùng form
  kem: "#FEF6E8"        # Kem sóng: thẻ tự chấm, khối bộ quy tắc
  nau-xam: "#584E4C"    # chữ phụ trên nền sáng
  xam-sang: "#EFEFEF"   # chữ trên nền nâu
  ho-phach: "#8A5300"   # liên kết, chữ nhấn nhỏ trên nền sáng (cam chỉ 2.0:1 trên trắng)
  cam-do: "#FD6703"     # chỉ cho viền lỗi và vòng focus, ≤ 10% diện tích
  xam-be: "#C9C3BD"     # đường kẻ, viền ô nhập
  # màu nằm trong file logo SVG gốc (không dùng trong CSS): "#2A1F1B" "#F0EFEF"
typography:
  tieu-de: { fontFamily: "Montserrat", fontWeight: 700, transform: uppercase, fontSize: "clamp(32px, 4.2vw, 54px)", lineHeight: 1.12 }
  h2: { fontFamily: "Montserrat", fontWeight: 700, transform: uppercase, fontSize: "clamp(26px, 2.8vw, 36px)" }
  than: { fontFamily: "Be Vietnam Pro", fontSize: "17px", lineHeight: 1.6 }
  nhan: { fontFamily: "Montserrat", fontWeight: 700, fontSize: "14px", transform: uppercase, letterSpacing: ".06em" }
rounded: { tat-ca: "0" }   # brand: khối phẳng, không bo; chỉ ảnh mới được bo 24px
spacing: { s1: "8px", s2: "16px", s3: "24px", s4: "40px", s5: "64px", s6: "104px" }
components:
  nut-chinh: { background: "{colors.cam}", textColor: "{colors.nau}", height: "52px", uppercase: true }
  nut-phu-tren-nau: { border: "2px {colors.xam-sang}", textColor: "{colors.xam-sang}" }
  nut-phu-tren-sang: { border: "2px {colors.nau}", textColor: "{colors.nau}" }
  o-nhap: { border: "2px {colors.xam-be}", focus: "{colors.cam}", minHeight: "50px", fontSize: "16px" }
  hoa-tiet: "img/xoan-cam.svg (xoắn ốc tù và, một mảng lớn tràn mép ở màn đầu); img/song-xoan-cam.svg (sóng xoắn, dải đáy khối đề xuất)"
---

# TUVA · giao diện đã khoá

## Tinh thần
Tiếng tù và gọi từ xa: nền nâu đen ấm, cam hổ phách là tiếng gọi. Màn đầu cho thấy **thứ thật chạy được**: công cụ tự chấm mức sẵn sàng AI của tổ chức, trả lời ngay trên trang. Phễu của TUVA bắt đầu từ mồi (tự chấm, bộ quy tắc AI) rồi mới tới gặp và đề xuất tài trợ, nên màn đầu mời làm ngay một việc nhỏ, có ích.

## Nên
- Mọi hoạ tiết là **xoắn ốc** (sóng, vỏ ốc, tù và). Một mảng xoắn lớn mỗi màn, tràn mép, không đè chữ.
- Tiêu đề Montserrat Bold IN HOA, căn trái. Chữ thân Be Vietnam Pro.
- Khối phẳng, góc vuông, không bóng. Nhấn bằng vạch cam 2–8px.
- Ba câu người mua hỏi đầu tiên (an toàn dữ liệu, đưa được vào đề xuất không, đã làm lĩnh vực nào) trả lời ngay dưới nút.
- Số, tên khách, liên hệ chưa chốt nằm trong `cau-hinh.json`; trang giữ chữ an toàn.

## Không nên
- Vòng đồng tâm, lưới chấm, lưới hình học (luật Linh 19/10).
- Màu Nhà Nhiều Cột hay Listening Vietnam; gradient, đổ bóng, kính mờ, emoji.
- Chữ cam cỡ nhỏ trên nền trắng.
- Tên, logo đối tác (UN Women, WWF, British Council...) khi chưa có đồng ý bằng văn bản; ảnh có logo đối tác.
- Lưới thẻ giống hệt nhau, nhãn nhỏ IN HOA trên mọi tiêu đề.
