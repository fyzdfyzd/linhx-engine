#!/usr/bin/env python3
"""Tạo bộ dữ liệu khách hàng GIẢ (tên bịa) có lỗi kiểu Việt Nam, kèm đáp án để đo trước/sau.

python tao_du_lieu_ban.py [so_dong] [thu_muc]
→ khach-hang-ban.csv, khach-hang-dap-an.csv
"""
import csv
import os
import random
import sys
import unicodedata

random.seed(33)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(__file__))

HO = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Vũ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương"]
DEM = ["Văn", "Thị", "Đức", "Minh", "Ngọc", "Thu", "Quốc", "Hữu", "Thanh", "Hoài"]
TEN = ["An", "Bình", "Châu", "Dũng", "Giang", "Hà", "Hường", "Khánh", "Linh", "Mai", "Nam", "Phúc", "Quỳnh", "Sơn", "Thảo", "Tú", "Việt", "Yến"]
DIA_CHI = [
    "Phường Phúc Xá, Quận Ba Đình, Thành phố Hà Nội",
    "Phường Hàng Bạc, Quận Hoàn Kiếm, Thành phố Hà Nội",
    "Phường Bến Nghé, Quận 1, Thành phố Hồ Chí Minh",
    "Phường Thảo Điền, Thành phố Thủ Đức, Thành phố Hồ Chí Minh",
    "Phường Hải Châu I, Quận Hải Châu, Thành phố Đà Nẵng",
    "Phường Lê Lợi, Thành phố Quy Nhơn, Tỉnh Bình Định",
    "Phường Vĩnh Ninh, Thành phố Huế, Tỉnh Thừa Thiên Huế",
    "Xã Tân Thông Hội, Huyện Củ Chi, Thành phố Hồ Chí Minh",
]
VIET_TAT = [("Phường ", "P. "), ("Quận ", "Q. "), ("Thành phố ", "TP. "), ("Huyện ", "H. ")]
DAU_CU = {"032": "0162", "033": "0163", "035": "0165", "038": "0168", "083": "0123", "077": "0122", "070": "0120"}
DAU_MOI = ["090", "091", "098", "097", "086", "032", "033", "035", "038", "083", "077", "070", "093", "088"]


def bo_dau(s):
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn").replace("đ", "d").replace("Đ", "D")


def mojibake(s):
    return s.encode("utf-8").decode("cp1252", errors="replace")


rows, truth = [], []
for i in range(N):
    ten = f"{random.choice(HO)} {random.choice(DEM)} {random.choice(TEN)}"
    dau = random.choice(DAU_MOI)
    sdt = dau + "".join(random.choice("0123456789") for _ in range(7))
    em = bo_dau(ten).lower().replace(" ", ".") + f"{i}@example.com"
    d, m, y = random.randint(1, 28), random.randint(1, 12), random.randint(1960, 2004)
    ngay = f"{y:04d}-{m:02d}-{d:02d}"
    cc = "0" + "".join(random.choice("0123456789") for _ in range(11))
    dc = random.choice(DIA_CHI)
    truth.append({"ma": f"KH{i:05d}", "ho_ten": ten, "sdt": sdt, "email": em, "ngay_sinh": ngay, "cccd": cc, "dia_chi_goc": dc})

    t, s, e, g, c, a = ten, sdt, em, f"{d:02d}/{m:02d}/{y}", cc, dc
    r = random.random()
    if r < 0.15: t = t.upper()
    elif r < 0.25: t = "  " + t.lower() + " "
    elif r < 0.32: t = unicodedata.normalize("NFD", t)
    elif r < 0.37: t = mojibake(t)
    elif r < 0.42: t = bo_dau(t)
    r = random.random()
    if r < 0.2 and dau in DAU_CU: s = DAU_CU[dau] + s[3:]
    elif r < 0.35: s = "+84 " + s[1:4] + " " + s[4:7] + " " + s[7:]
    elif r < 0.45: s = s[1:]  # Excel làm mất số 0
    elif r < 0.52: s = s[:4] + "." + s[4:7] + "." + s[7:]
    elif r < 0.55: s = s[:6]  # số cụt: không sửa được
    r = random.random()
    if r < 0.15: e = e.upper()
    elif r < 0.2: e = " " + e + " "
    r = random.random()
    if r < 0.3: g = f"{d}-{m}-{y}"
    elif r < 0.45: g = ngay
    elif r < 0.5: g = f"{d:02d}.{m:02d}.{y}"
    r = random.random()
    if r < 0.2: c = c[1:]  # mất số 0
    elif r < 0.25: c = c[3:]  # CMND 9 số cũ
    r = random.random()
    if r < 0.3:
        for a1, a2 in VIET_TAT: a = a.replace(a1, a2)
    elif r < 0.4: a = bo_dau(a)
    elif r < 0.45: a = ""
    rows.append({"Mã KH": f"KH{i:05d}", "Họ tên": t, "SĐT": s, "Email": e, "Ngày sinh": g, "CCCD": c, "Địa chỉ": a})

# 3% dòng trùng (cùng khách nhập lại, khác định dạng)
for j in random.sample(range(N), N * 3 // 100):
    x = dict(rows[j])
    x["Mã KH"] = x["Mã KH"] + "-B"
    x["Họ tên"] = bo_dau(truth[j]["ho_ten"])
    x["SĐT"] = truth[j]["sdt"]
    rows.append(x)
    truth.append(dict(truth[j], ma=x["Mã KH"]))

os.makedirs(OUT, exist_ok=True)
for name, data in (("khach-hang-ban.csv", rows), ("khach-hang-dap-an.csv", truth)):
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(data[0].keys()))
        w.writeheader()
        w.writerows(data)
print(f"Đã tạo {len(rows)} dòng trong {OUT}")
