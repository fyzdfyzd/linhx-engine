---
name: IF Agent Event
version: 1.0 (khoá 9/11/2026, Linh chọn phương án A)
colors:
  nen: "#0D1117"
  the: "#161B22"
  the2: "#1C2128"
  vien: "#21262D"
  vien2: "#30363D"
  chu: "#FFFFFF"
  phu: "#8B949E"
  phu2: "#C9D1D9"
  xanh: "#0088FF"
  ngoc: "#00D4AA"
  loi: "#FF7B72"
  # sắc độ phụ: chỉ dùng cho màn kiosk minh hoạ, nền khối xen, placeholder
  kiosk-tren: "#121A26"
  kiosk-duoi: "#0E141D"
  kiosk-vien: "#0A0E14"
  kiosk-chan: "#1A2230"
  bong-khach: "#262C36"
  bong-ai: "#0E2A3F"
  bong-ai-vien: "#0B4A7A"
  khoi-xen: "#0F141B"
  the-noi: "#10243A"
  goi-y: "#6E7681"
  gradient: "linear-gradient(135deg, #0088FF 0%, #00D4AA 100%)"
typography:
  tieu-de: { fontFamily: "Be Vietnam Pro", fontWeight: 700, fontSize: "clamp(34px, 4.6vw, 58px)", lineHeight: 1.12 }
  h2: { fontFamily: "Be Vietnam Pro", fontWeight: 700, fontSize: "clamp(28px, 3.2vw, 40px)", lineHeight: 1.2 }
  than: { fontFamily: "Inter", fontSize: "17px", lineHeight: 1.6 }
  nhan: { fontFamily: "JetBrains Mono", fontSize: "13px" }
rounded: { s: "8px", m: "12px", l: "24px" }
spacing: { s1: "8px", s2: "16px", s3: "24px", s4: "40px", s5: "64px", s6: "104px" }
components:
  nut-chinh: { background: "{colors.gradient}", textColor: "{colors.nen}", height: "48px", rounded: "{rounded.m}" }
  nut-phu: { background: "transparent", border: "1px {colors.vien2}", height: "48px" }
  o-nhap: { background: "{colors.nen}", border: "1px {colors.vien2}", minHeight: "48px", fontSize: "16px" }
  the: { background: "{colors.the}", border: "1px {colors.vien}", rounded: "{rounded.l}" }
---

# IF Agent Event · giao diện đã khoá

## Tinh thần
Nền tối của brand, màn đầu cho thấy **thứ thật đang chạy** (kiosk nhân vật AI nói chuyện với khách), không dựa vào quầng sáng. Gradient xanh–ngọc chỉ ở nút chính, viền gói nổi bật và sóng giọng nói.

## Nên
- Mỗi màn đầu trả lời ba câu bên tổ chức hỏi: giá, thời gian dựng, case gần nhất.
- Mọi số chưa chốt nằm trong `cau-hinh.json`, trang giữ chữ an toàn khi chưa có.
- Ảnh minh hoạ phải ghi "Minh hoạ" ngay dưới.
- Chạm ≥ 44px, chữ thân ≥ 16px, ô đồng ý không tick sẵn.

## Không nên
- Thêm màu, phông, bo góc ngoài token trên.
- Nhãn nhỏ IN HOA trên tiêu đề, đánh số 01/02/03 khi không phải trình tự, lưới thẻ giống hệt nhau, chữ gradient, kính mờ trang trí.
- Bịa con số, logo khách, lời khen.
