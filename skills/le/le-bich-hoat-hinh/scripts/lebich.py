"""Lê Bích bụng phệ từ bộ rời GỐC (PSD Le_Bich.psd), dựng bằng Pillow, không cần trình duyệt.

Không vẽ lại nét nào: mỗi bộ phận là PNG gốc (base64 trong assets/rig-data.js), đặt đúng toạ độ
trong khung 462x1348, tay xoay quanh vai, đầu nghiêng quanh cổ, bụng nhún quanh mông, đổi mắt/miệng.

Dùng trong code:
    from lebich import nhan_vat, chu, bong_thoai, font, MAT, MIENG
    im = nhan_vat(mat="cuoi", mieng="ha", tay_trai=60, tay_phai=-100, dau=5, bung=1.04, rong=400)
Chạy thử:  python3 lebich.py thu ra.png   (bảng 6 biểu cảm)
"""
import base64, io, json, os, sys
from PIL import Image, ImageDraw, ImageFont

GOC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

# mắt/miệng: tên dễ nhớ → lớp PSD
MAT = {"cham": "Eye__e", "hoang": "Eye__Layer_10", "tron": "Eye__Layer_11",
       "ngan": "Eye__Layer_12", "cuoi": "Eye__Layer_13", "buon": "Eye__Layer_15"}
MIENG = {"cuoi": "Mouth__m", "ngai": "Mouth__", "chu": "Mouth__3",
         "thang": "Mouth__Layer_9", "ha": "Mouth__Layer_14", "le": "Mouth__Layer_16"}
# khớp xoay, toạ độ gốc PSD
KHOP = {"tay_trai": (205, 984), "tay_phai": (322, 982), "dau": (248, 1095), "bung": (246, 1240)}
CAT = (40, 690, 440, 1310)  # khung cắt 400x620 quanh nhân vật
DEM = 200  # lề trong suốt quanh khung gốc, để tay giơ ra ngoài không bị cắt

_rig = None
def _nap():
    global _rig
    if _rig is None:
        s = open(os.path.join(GOC, "rig-data.js"), encoding="utf-8").read()
        d = json.loads(s[s.index("{"): s.rindex("}") + 1])
        d["img"] = {k: Image.open(io.BytesIO(base64.b64decode(v))).convert("RGBA")
                    for k, v in d["png_base64"].items()}
        _rig = d
    return _rig

def _lop(*ten):
    """Dán các bộ phận lên một tấm trong suốt 462x1348 đúng toạ độ gốc."""
    r = _nap(); W, H = r["khung"]; t = Image.new("RGBA", (W + 2 * DEM, H + 2 * DEM), (0, 0, 0, 0))
    for k in ten:
        x0, y0, _, _ = r["bbox"][k]; t.alpha_composite(r["img"][k], (x0 + DEM, y0 + DEM))
    return t

def _xoay(t, do, khop):
    # do > 0: xoay chiều kim đồng hồ (giống CSS rotate)
    return t if not do else t.rotate(-do, resample=Image.BICUBIC, center=(khop[0] + DEM, khop[1] + DEM))

def nhan_vat(mat="cham", mieng="cuoi", tay_trai=0, tay_phai=0, dau=0, bung=1.0,
             cong_so=False, rong=400, dx=0, dy=0, le=0):
    """Trả ảnh RGBA. Khung cắt gốc 400x620 (đơn vị PSD) nới thêm `le` mỗi phía (le<=200, dùng khi tay giơ cao/dang rộng);
    ảnh ra rộng `rong`, cao theo đúng tỉ lệ khung. bung: 1.0 bình thường, >1 phình (nhún)."""
    r = _nap(); W, H = r["khung"]; W, H = W + 2 * DEM, H + 2 * DEM
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    c.alpha_composite(_lop("Le_Bich__leg_R", "Le_Bich__leg_L"))
    c.alpha_composite(_xoay(_lop("Le_Bich__hand_L"), tay_trai, KHOP["tay_trai"]))
    than = _lop("Le_Bich_cong_so__Body" if cong_so else "Le_Bich__body")
    if bung != 1.0:  # nhún bụng: giãn ngang theo bung, co dọc nghịch đảo, neo ở mông
        bx, by = KHOP["bung"][0] + DEM, KHOP["bung"][1] + DEM
        nw, nh = round(W * bung), round(H / bung)
        than2 = than.resize((nw, nh), Image.BICUBIC)
        than = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        than.paste(than2, (round(bx - bx * bung), round(by - by / bung)), than2)
    c.alpha_composite(than)
    c.alpha_composite(_xoay(_lop("Le_Bich__hand_R"), tay_phai, KHOP["tay_phai"]))
    c.alpha_composite(_xoay(_lop("Le_Bich__head", "Hair_tach_tu_CHARACTERS", "Rau__Rau_basic",
                                 MAT[mat], MIENG[mieng]), dau, KHOP["dau"]))
    x0, y0, x1, y1 = (v + DEM for v in CAT)
    c = c.crop((x0 - le - dx, y0 - le - dy, x1 + le - dx, y1 + le - dy))
    return c.resize((rong, round(rong * (620 + 2 * le) / (400 + 2 * le))), Image.LANCZOS)

_font = {}
def font(co=40):
    """Patrick Hand đủ dấu tiếng Việt (gộp latin + latin-ext + vietnamese), giấy phép OFL."""
    if co not in _font:
        b = base64.b64decode(open(os.path.join(GOC, "font-patrick-hand-vn.b64.txt")).read())
        _font[co] = ImageFont.truetype(io.BytesIO(b), co)
    return _font[co]

def chu(ve, xy, noi_dung, co=40, mau="#111", vien=0, can="la"):
    """Viết chữ; vien > 0 thì có viền trắng dày (kiểu chữ sticker)."""
    ve.text(xy, noi_dung, font=font(co), fill=mau, anchor=can,
            stroke_width=vien, stroke_fill="white")

def bong_thoai(ve, hop, noi_dung, duoi=None, co=34, net=4):
    """Bóng thoại elip trắng viền đen, chữ căn giữa; duoi=(x,y) là chỗ miệng nhân vật."""
    x0, y0, x1, y1 = hop; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if duoi:
        ve.polygon([(cx - 18, cy), duoi, (cx + 18, cy)], fill="white", outline="#111", width=net)
    ve.ellipse(hop, fill="white", outline="#111", width=net)
    ve.multiline_text((cx, cy), noi_dung, font=font(co), fill="#111", anchor="mm", align="center", spacing=4)

if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "thu":
        bang = Image.new("RGB", (1470, 430), "#c9c9c9"); ve = ImageDraw.Draw(bang)
        mau = [("cham", "cuoi", 0, 0, 0, 1.0), ("cuoi", "ha", 60, -100, 0, 1.0), ("hoang", "thang", 0, -30, -5, 1.0),
               ("tron", "chu", 20, 20, 4, 1.0), ("ngan", "cuoi", 0, -35, 0, 1.0), ("buon", "le", 10, 10, 6, 1.0),
               ("cuoi", "ha", 0, -150, 0, 1.06)]
        for i, (m, mi, a, b, d, bu) in enumerate(mau):
            nv = nhan_vat(m, mi, a, b, d, bung=bu, rong=200); x = 10 + i * 208
            bang.paste(nv, (x, 50), nv); chu(ve, (x + 100, 370), f"{m} / {mi}" + (" / nhún" if bu != 1 else ""), 26, can="mt")
        chu(ve, (735, 12), "Lê Bích bụng phệ · bộ rời gốc · kiểm tra dấu: ầ ữ ợ đ", 30, can="mt")
        bang.save(sys.argv[2]); print("đã lưu", sys.argv[2])
    else:
        print(__doc__)
