---
name: Sakédemy · mặt tiền lớp doanh nghiệp
version: 1.0 (khoá 9/11/2026, phương án A: trung thành landing v1.0 Linh duyệt 20/10)
nguon: LAB058-WEB-DESIGN-FLOW/sakedemy/v1 (index.html, tokens.css, GHI-CHU.md); LAB043 brands/sakedemy (brand.json, LUAT-ONBRAND.md, guideline 2026 tr.34 mục 3.5 Website)
colors:
  la: "#6EB264"        # Xanh Lá Sakédemy: một mảng lớn có gân lá, chữ trên nó là Rêu Đậm
  reu: "#02403B"       # Xanh Rêu Đậm: tiêu đề, nút chính, khối lá lớn
  chu: "#414141"       # Xám Chữ: chữ thân
  nen: "#FFFFFF"
  nhat: "#E9F6D3"      # Lá Nhạt: thẻ, chân trang, dải học cá nhân
  vien: "#F0F0F0"      # Xám Nhạt: đường kẻ
  sau: "#118056"       # Xanh Lá Sâu: chữ xanh nhỏ, nhãn, link
  dam: "#1CA571"       # Xanh Lá Đậm: chỉ ở cuối gradient chữ tiêu đề (chữ lớn)
  non: "#A3D34F"       # Lá Non: nhấn trên nền Rêu Đậm
  ngoc: "#26CABE"      # Xanh Ngọc: cuối gradient thương hiệu
  # sắc độ phụ (giữ từ v1 hoặc cần cho form)
  phu: "#5F6B66"       # chữ phụ, tên khách (v1)
  vien2: "#CFD8D3"     # viền ô nhập (v1)
  chu-toi: "#C8DAD4"   # chữ phụ trên Rêu Đậm (v1)
  loi: "#A3361F"       # báo lỗi form (nâu đỏ, không hồng)
  grad: "linear-gradient(210deg, #A3D34F, #26CABE)"
  grad-chu: "linear-gradient(90deg, #118056, #1CA571)"
typography:
  font: "Be Vietnam Pro (Light 300, Regular 400, Bold 700), OFL, từ LAB043 03-chu"
  h1: { fontWeight: 700, fontSize: "clamp(36px, 4.6vw, 64px)", lineHeight: 1.07 }
  h2: { fontWeight: 700, fontSize: "clamp(28px, 3.4vw, 46px)", lineHeight: 1.12 }
  than: { fontSize: "17px (16px trên điện thoại)", lineHeight: 1.65 }
  nhan: { fontSize: "14px", letterSpacing: ".22em", textTransform: uppercase, color: "{colors.sau}" }
shape:
  la: "border-radius: R 0 R 0 (bo góc trên trái + dưới phải). Ảnh, thẻ, nút, ô nhập, chip, số thứ tự, gạch đầu dòng, khối CTA đều là lá."
spacing: { s1: "8px", s2: "16px", s3: "24px", s4: "40px", s5: "64px", s6: "112px" }
components:
  nut-chinh: { background: "{colors.reu}", textColor: "{colors.nen}", minHeight: "52px", radius: "16px 0 16px 0" }
  nut-phu: { background: "transparent", border: "2px inset {colors.reu}", minHeight: "52px" }
  o-nhap: { border: "1.5px {colors.vien2}", radius: "12px 0 12px 0", minHeight: "52px", fontSize: "16px" }
---

# Sakédemy · giao diện đã khoá

## Tinh thần (theo v1 và guideline 3.5)
Hero nền trắng, tiêu đề trái chiếm khoảng một nửa, cụm từ khoá trong tiêu đề là chữ gradient Xanh Lá Sâu sang Xanh Lá Đậm. Ảnh lớp học thật trong khung lá bên phải, thẻ số trắng hình lá nổi trên ảnh. Một mảng Xanh Lá lớn có gân lá mờ, chữ Rêu Đậm. Một khối Rêu Đậm có lá lớn ở góc, điểm nhấn Lá Non. Chân trang Lá Nhạt chấm mờ, SAKEDEMY.COM ở chân.

## Nên
- Mọi hoạ tiết là lá: gân lá, lá chấm, lá lớn (LAB043 05-icon). Hoạ tiết ở góc hoặc nền mờ dưới 20%, không đè chữ.
- Ảnh là ảnh lớp học thật từ hồ sơ đào tạo doanh nghiệp (LAB043 04-hinh-anh). Ảnh do AI vẽ phải ghi "Minh hoạ".
- Số liệu và tên khách chỉ lấy những gì v1 ghi là thật (62+ VOV, 700+ Phenikaa, 11 mentor; Vinhomes, Taseco, ROX, Onsen Fuji, Viện FSB, ĐH Phenikaa). Số chưa chốt nằm trong `cau-hinh.json`.
- Chạm ≥ 44px, chữ thân ≥ 16px, ô đồng ý không tick sẵn.

## Không nên
- Màu hồng, navy #051D40, neon, gradient phủ cả nền.
- Chữ trắng trên Xanh Lá #6EB264 (2,56:1).
- Hình bo đều bốn góc, khung tròn, viền dày, đổ bóng chữ.
- Robot, não phát sáng, ảnh stock văn phòng phương Tây.
- Bịa giá, phần trăm năng suất, lời khen, tên khách.
