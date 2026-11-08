"""brand.json (chuẩn LAB043) -> tokens.css cho trang web.
Dùng: python token.py <brand.json> <ra/tokens.css>"""
import json, sys

def hexes(lst):
    return {x["ten"]: x["hex"] for x in lst}

def main(src, dst):
    b = json.load(open(src, encoding="utf-8"))
    m = b["mau"]
    chinh, phu = m["chinh"], hexes(m.get("phu", []))
    fonts = b.get("chu", {}).get("font_cho_phep", ["system-ui"])
    nhan = hexes(m.get("nhan", []))
    grad = m.get("gradient", {}).get("css", "none")
    chu_xanh = phu.get("Xanh Lá Sâu", chinh[1]["hex"] if len(chinh) > 1 else chinh[0]["hex"])
    nhan_vals = list(nhan.values()) + [chinh[0]["hex"]] * 2
    nen_nhat = next((v for k, v in phu.items() if "Nhạt" in k and v.upper() != "#F0F0F0"), "#F5F5F5")
    css = f"""/* sinh từ {b['brand_id']}/brand.json — không sửa tay, sửa brand.json rồi chạy lại */
:root {{
  --brand: {chinh[0]['hex']};
  --brand-dam: {chinh[1]['hex'] if len(chinh) > 1 else chinh[0]['hex']};
  --chu: {chinh[2]['hex'] if len(chinh) > 2 else '#222'};
  --nen: {phu.get('Trắng', '#FFFFFF')};
  --nen-nhat: {nen_nhat};
  --vien: {phu.get('Xám Nhạt', '#E5E5E5')};
  --chu-xanh: {chu_xanh};
  --nhan-1: {nhan_vals[0]};
  --nhan-2: {nhan_vals[1]};
  --grad: {grad};
  --font: '{fonts[0]}', system-ui, sans-serif;
  --r: 14px;
  --la: 30% 8px;  /* khung hình lá: bo chéo trên trái + dưới phải */
  --c-nhan: 13px;
  --s1: 4px; --s2: 8px; --s3: 16px; --s4: 24px; --s5: 40px; --s6: 64px; --s7: 104px;
  --c-1: clamp(16px, 0.4vw + 15px, 18px);
  --c-2: clamp(20px, 1.4vw + 14px, 26px);
  --c-3: clamp(30px, 3.6vw + 14px, 60px);
}}
"""
    open(dst, "w", encoding="utf-8").write(css)
    print("ghi", dst)

if __name__ == "__main__":
    main(*sys.argv[1:3])
