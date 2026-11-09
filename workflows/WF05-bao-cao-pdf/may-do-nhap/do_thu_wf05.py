# Máy đo thử WF05 vòng 2 (bản nháp, chỉ đọc): luật hình + nhúng font + số vẽ trên hình.
import json, re, sys
from pathlib import Path
import pymupdf

d = Path(sys.argv[1])
hinh = json.loads((d / "04-hinh.json").read_text(encoding="utf-8"))["hinh"]
doc = pymupdf.open(d / "bao-cao.pdf")
txt = "\n".join(p.get_text() for p in doc)
txt_n = txt.replace(" ", " ")

loi, canh = [], []
print("== Luật hình (đề xuất vòng 1: ≤7 hạng mục, ≤5 chuỗi, tiêu đề 8–30 tiếng)")
tieu_de = []
for h in hinh:
    hid, nhan, chuoi = h.get("id"), h.get("nhan", []), h.get("chuoi", [])
    td = h.get("tieu_de", "")
    tieu_de.append((hid, td))
    so_tieng = len(td.split())
    if len(nhan) > 7:
        loi.append(f"{hid}: {len(nhan)} hạng mục > 7")
    if len(chuoi) > 5:
        loi.append(f"{hid}: {len(chuoi)} chuỗi > 5")
    if not (8 <= so_tieng <= 30):
        canh.append(f"{hid}: tiêu đề {so_tieng} tiếng")
    for c in chuoi:
        gt = c.get("gia_tri", [])
        if len(c.get("bc", [])) not in (len(gt), 0):
            canh.append(f"{hid}/{c.get('ten')}: {len(gt)} giá trị nhưng {len(c.get('bc', []))} mã BC")
    for k in ("3d", "truc_kep", "truc_phu", "y2"):
        if k in json.dumps(h, ensure_ascii=False).lower():
            canh.append(f"{hid}: có khoá nghi '{k}'")
    if h.get("truc_min") not in (None, 0) and h.get("loai", "").startswith(("cot", "thanh")):
        loi.append(f"{hid}: trục cột/thanh không bắt đầu từ 0")
    # số vẽ trên hình có xuất hiện thành nhãn chữ trong PDF không (nhãn trực tiếp)
    thieu = []
    for c in chuoi:
        for v in c.get("gia_tri", []):
            if v is None:
                continue
            s = f"{v:g}".replace(".", ",")
            if not re.search(r"(?<![\d,])" + re.escape(s) + r"(?![\d])", txt_n):
                thieu.append(s)
    if thieu:
        canh.append(f"{hid}: {len(thieu)} giá trị không thấy thành chữ trong PDF: {thieu[:6]}")
    print(f"  {hid} {h.get('loai')}: {len(nhan)} hạng mục, {len(chuoi)} chuỗi, tiêu đề {so_tieng} tiếng")

print("== Nhúng font")
fs = {}
for p in doc:
    for f in p.get_fonts(full=True):
        fs[f[3]] = f[1]  # basefont -> ext
for name, ext in sorted(fs.items()):
    tag = "nhúng" if ext and ext != "n/a" else "KHÔNG NHÚNG"
    if tag != "nhúng":
        loi.append(f"font {name} không nhúng")
    print(f"  {name}: {ext} ({tag})")

print("== Phép thử tiêu đề: đọc liền các tiêu đề hình (đưa cho người chấm mù)")
for hid, td in tieu_de:
    print(f"  {hid}: {td}")

print(f"== KẾT QUẢ: {len(loi)} lỗi, {len(canh)} cảnh báo")
for x in loi:
    print("  LỖI", x)
for x in canh:
    print("  cảnh báo", x)
