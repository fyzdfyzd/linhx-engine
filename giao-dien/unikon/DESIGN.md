---
name: Unikon · unikon.vn
version: 1.0 (khoá 9/11/2026, phương án A "Bảng pitch 48 giờ", Claude khoá theo khuyến nghị, chờ Linh duyệt)
nguon: LAB043 brands/unikon (brand.json v0.1, LUAT-ONBRAND.md, guideline 2026 trang 36 "Website, LinkedIn")
colors:
  dem-tim: "#160B2A"        # nền tối chủ đạo
  dem-tim-nhat: "#21143A"   # thẻ trên nền tối
  vien-toi: "#35264F"
  trang: "#FFFFFF"
  xam-chu-phu-nen-toi: "#BBBDBF"
  suong-tim: "#FAF7F4"      # nền sáng, trang con, khối xen
  muc-tim: "#160B2A"        # chữ trên nền sáng
  xam-wordmark: "#58595B"   # chữ phụ nền sáng
  vien-sang: "#E9E2EC"
  hong-phan: "#FDE8EF"      # nền ghi chú
  magenta: "#E6155F"        # mảng, gạch đầu dòng; không làm nền chữ trắng nhỏ
  magenta-dam: "#C8124F"    # nút chính chữ trắng, nhấn trên nền sáng
  magenta-sang: "#FF5C8F"   # link, pill trên nền tối
  tim: "#5113A4"
  man: "#A02487"            # hover nút chính
  cam: "#F7941D"            # chỉ trong gradient, ≤ 10%
  # phụ, không thuộc brand.json: trạng thái lỗi form và chữ gợi ý
  loi-sang: "#FF8A80"
  loi-dam: "#B3261E"
  goi-y: "#8A8590"
  gradient: "linear-gradient(135deg, #F7941D 0%, #E6155F 50%, #5113A4 100%)"
typography:
  tieu-de: { fontFamily: "Montserrat", fontWeight: 700, fontSize: "clamp(36px, 4.4vw, 56px)", lineHeight: 1.08 }
  h2: { fontFamily: "Montserrat", fontWeight: 700, fontSize: "clamp(28px, 3.4vw, 44px)", lineHeight: 1.12 }
  than: { fontFamily: "Be Vietnam Pro", fontSize: "17px", lineHeight: 1.6 }
  nhan: { fontFamily: "Montserrat", fontWeight: 700, fontSize: "14px", letterSpacing: ".1em", textTransform: "uppercase", chiDung: "pill" }
rounded: { s: "8px", m: "16px", l: "24px", vien-thuoc: "999px" }
spacing: { s1: "8px", s2: "16px", s3: "24px", s4: "40px", s5: "64px", s6: "112px" }
components:
  nut-chinh: { background: "{colors.magenta-dam}", textColor: "#FFFFFF", height: "52px", rounded: "999px" }
  nut-phu: { background: "transparent", border: "2px currentColor", height: "52px", rounded: "999px" }
  o-nhap: { background: "nền khối", border: "1px vien", minHeight: "48px", fontSize: "16px" }
  the: { background: "dem-tim-nhat hoặc trắng", border: "1px vien", rounded: "{rounded.l}" }
---

# Unikon · giao diện đã khoá

## Tinh thần
Theo guideline 3.5: hero nền Đêm tím, chữ trái khoảng 55%, một khối cầu gradient tràn mép phải, nút chính magenta đậm chữ trắng, nút phụ viền 2px. Câu chuyện màn đầu là **một pitch đang chạy**: bảng ba hướng ý tưởng có hình AI, đồng hồ hạn pitch, ô "Logo agency của bạn", dấu "Đã qua người duyệt". Trang con là tài liệu dài nên đảo sang nền Sương tím, chữ Mực tím.

## Nhịp trang chủ
Tối (hero) → tối (pitch 48 giờ + ba câu) → sáng (dịch vụ) → tối (an toàn thương hiệu + form bộ kiểm) → sáng (sau pitch: job / Brand kit) → tối (form brief + gọi lại) → sáng (hỏi đáp) → chân tối.

## Nên
- Mỗi màn đầu trả lời ba câu agency hỏi: kịp pitch không, có lộ tên không, giá tính thế nào.
- Số chưa chốt nằm trong `public/cau-hinh.json`; null thì trang giữ chữ an toàn.
- Hình minh hoạ ghi "Minh hoạ", nhân vật AI ghi là người hư cấu.
- Chạm ≥ 44px, chữ thân ≥ 16px, ô đồng ý không tick sẵn.
- Logo nền tối dùng `logo-ngang-mau-nen-toi.svg`, nền sáng dùng `logo-sang.svg`.

## Không nên
- Màu ngoài token trên; màu web và deck cũ (#E93E72, #F60863, #FF00DF...).
- Chữ nhỏ trên gradient hoặc trên khối cầu; chữ gradient; kính mờ trang trí.
- Đánh số 01/02/03 khi không phải trình tự; lưới thẻ giống hệt nhau.
- Logo Unikon trên ảnh minh hoạ deck giao cho agency; logo khách, tên khách, giải thưởng khi chưa được phép.
- Raleway, Avenir, Inter, Poppins.

## Brand ID mới (11/11/2026)
Màu, logo, hoạ tiết theo D:\linhx\BRAND\UNIKON (guideline v1, điểm chờ chốt đi theo ★ A). Bảng lệch: D:\linhx\BRAND\UNIKON\ADAPT-WEB.md.
Mã màu brand: #160B2A #E6155F #5113A4 #F7941D #58595B #FAF7F4 #FBA916 #EF2951 #A02487 #255FB0 #21143A #35264F #E9E2EC #C8124F
