"""Dựng cảnh N2 kiểu hybrid: clip nhân vật Veo + object, chữ, máy, âm thanh bằng code.
Chạy: python dung_N2.py [t1 t2 ...]  (có đối số thì chỉ xuất khung PNG tại các giây đó vào kiem\\)"""
import math, os, random, subprocess, sys, wave
import cv2
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, r"D:\LINHX\SKILLS\le\le-bich-hoat-hinh\scripts")
from lebich import font

D = os.path.dirname(os.path.abspath(__file__))
SB = os.path.join(D, "..", "storyboard-v4", "N2.png")
CLIP = os.path.join(D, "N2-char.mp4")
GIONG = os.path.join(D, "..", "giong-tam", "N2.wav")
RA = os.path.join(D, "N2-hybrid.mp4")
W, H, FPS, DUR = 1080, 1920, 24, 7.5

# mốc thoại đo bằng silencedetect
T_LOGO = [0.15, 0.85, 1.55]   # "Mấy cái logo các hãng AI"
T_KY = 2.43                   # "nhìn kỹ một hồi"
T_DONG2 = 3.87                # "Cái nào cũng trông như…"
T_MEO = 5.84                  # "mông mèo", chữ chốt
T_THOI = 6.60                 # "thế thôi"

# ---- nhịp nhân vật: giây cảnh -> giây trong clip, né các khung nhoè của Veo
NHIP = [(0.0, 0.0), (2.43, 0.56), (2.46, 0.88), (2.80, 1.25), (5.40, 2.62), (5.68, 2.66), (5.70, 2.88), (5.82, 2.88),
        (T_MEO, 3.25), (6.08, 3.5), (6.12, 3.88), (7.5, 5.10)]
BAC = 2  # vẽ trên 2 khung, nhịp hoạt hình tay
T_DAT = 6.12  # chân chạm đất: code thêm squash

def nhip_clip(t):
    t = int(t * FPS / BAC) * BAC / FPS
    for (a, va), (b, vb) in zip(NHIP, NHIP[1:]):
        if a <= t <= b:
            return va + (vb - va) * (t - a) / (b - a)
    return NHIP[-1][1]

def nap_clip():
    c = cv2.VideoCapture(CLIP); ds = []
    while True:
        ok, f = c.read()
        if not ok:
            break
        g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32)
        ds.append(np.clip((g - 95) / (205 - 95), 0, 1))  # kéo mức: hết nền xám, bóng mờ; nét đen tuyền
    return ds

# ---- tách mèo và logo từ storyboard, bỏ các đường xám nền
def nen_mau(a):
    r, g, b = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
    return (a.max(axis=2).astype(int) - a.min(axis=2)) > 28

def tach():
    sb = np.array(Image.open(SB).convert("RGB"))
    x0, y0, x1, y1 = 750, 330, 1030, 750
    a = sb[y0:y1, x0:x1].copy()
    a[cv2.dilate(nen_mau(a).astype(np.uint8), np.ones((5, 5))) > 0] = 255   # bỏ logo sao
    g = a.mean(axis=2).astype(np.uint8)
    net = g < 110
    net = cv2.dilate(net.astype(np.uint8), np.ones((3, 3)))
    net[0, :] = net[-1, :] = 0; net[:, 0] = net[:, -1] = 0
    ngoai = np.zeros((net.shape[0] + 2, net.shape[1] + 2), np.uint8)
    t = net.copy()
    cv2.floodFill(t, ngoai, (0, 0), 2)
    trong = (t != 2).astype(np.float32)
    trong = cv2.GaussianBlur(trong, (0, 0), 0.8)
    den = np.clip((200.0 - g) / 150.0, 0, 1)
    v = (1 - den) * 255
    meo = Image.fromarray(np.dstack([v, v, v, trong * 255]).astype(np.uint8), "RGBA")

    def logo(hop, mau):
        c = sb[hop[1]:hop[3], hop[0]:hop[2]]
        if mau:
            am = np.clip((c.max(axis=2).astype(float) - c.min(axis=2)) / 60, 0, 1)
            rgb = c
        else:
            am = np.clip((215.0 - c.mean(axis=2)) / 170, 0, 1); rgb = c * 0 + 17
        return Image.fromarray(np.dstack([rgb, am * 255]).astype(np.uint8), "RGBA")
    return meo, [logo((146, 606, 234, 698), False), logo((478, 594, 600, 712), True), logo((826, 590, 955, 716), True)]

MEO, LOGO = tach()
XM = [190, 540, 890]               # tâm ngang 3 con mèo
YM_DAY = 740                       # đáy mèo
Y_LOGO = 650

def ease(x):
    x = max(0, min(1, x)); return x * x * (3 - 2 * x)

def bat(x, tan=1.5, tat=9.0):
    """Lò xo vọt lố rồi ổn định: 0 -> 1."""
    return 0 if x <= 0 else 1 - math.exp(-tat * x) * math.cos(tan * 2 * math.pi * x)

def dan_xoay(nen, anh, cx, cy, sx, sy, goc=0):
    w, h = max(1, round(anh.width * sx)), max(1, round(anh.height * sy))
    a = anh.resize((w, h), Image.LANCZOS)
    if goc:
        a = a.rotate(goc, expand=True, resample=Image.BICUBIC)
    nen.alpha_composite(a, (round(cx - a.width / 2), round(cy - a.height / 2))) if 0 <= round(cx - a.width / 2) and 0 <= round(cy - a.height / 2) else nen.paste(a, (round(cx - a.width / 2), round(cy - a.height / 2)), a)

def san_khau(t):
    c = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    d = ImageDraw.Draw(c)
    d.line([(0, 1478), (W, 1478)], fill=(185, 185, 185, 255), width=5)
    # chữ "tìm con AI…" gõ dần sau khi đủ logo
    s = "tìm con AI…"
    so = int(max(0, min(len(s), (t - 2.0) * 16)))
    if so:
        d.text((540 - font(92).getlength(s) / 2, 190), s[:so], font=font(92), fill="#111")
    # mèo bật ra đúng chữ chốt, lệch nhau 2 khung
    for i, x in enumerate(XM):
        u = (t - T_MEO - i * 2 / FPS)
        if u <= 0:
            continue
        k = bat(u / 0.55)
        ve = 1 + 0.14 * math.exp(-u * 7) * math.sin(u * 24)          # squash theo bật
        lac = 4 * math.sin((t - T_MEO) * 7 + i) * math.exp(-max(0, t - T_THOI) * 0.4) if u > 0.35 else 0
        sx, sy = max(0.02, k) * (2 - ve), max(0.02, k) * ve
        dan_xoay(c, MEO, x, YM_DAY - MEO.height * sy / 2, sx, sy, lac)
    # logo hiện trước, nằm yên làm mốc; sang mèo thì dính vào mông
    for i, (x, l) in enumerate(zip(XM, LOGO)):
        u = t - T_LOGO[i]
        if u <= 0:
            continue
        k = bat(u / 0.5)
        tho = 1 + 0.015 * math.sin(t * 3 + i * 2)
        co = (1.5 - 0.5 * ease((t - T_MEO) / 0.2)) * tho
        y = Y_LOGO - 130 * (1 - ease((t - T_MEO) / 0.2))
        dan_xoay(c, l, x, y, k * co, k * co)
    return c

def camera(t):
    """Trả zoom, tâm x, tâm y."""
    if t < T_KY:
        return 1.0 + 0.04 * t / T_KY, 540, 760
    if t < 5.1:
        k = ease((t - T_KY) / (5.1 - T_KY))
        return 1.04 + 0.18 * k, 540, 760 - 40 * k           # đẩy dần vào logo giữa, vẫn thấy mặt
    if t < T_MEO:
        return 1.22, 540, 720                              # đọng trước chữ chốt
    k = 1 - math.exp(-(t - T_MEO) * 9) * math.cos((t - T_MEO) * 10)
    return 1.22 + (1.0 - 1.22) * k, 540, 720 + 240 * k     # giật ra toàn cảnh, lắc trớn

def nhan_vat(c, ds, t):
    g = ds[min(len(ds) - 1, round(nhip_clip(t) * 24))]
    sc = 0.58 * W / g.shape[1]
    nw, nh = round(g.shape[1] * sc), round(g.shape[0] * sc)
    sx, sy = 1.0, 1.0
    u = t - T_DAT
    if 0 <= u < 0.25:                                     # squash lúc tiếp đất, neo ở chân
        k = math.sin(u / 0.25 * math.pi); sx, sy = 1 + 0.09 * k, 1 - 0.09 * k
    m = cv2.resize(g, (round(nw * sx), round(nh * sy)), interpolation=cv2.INTER_AREA)
    x0 = round(W / 2 - m.shape[1] / 2)
    y0 = round(1478 - (1128 + 8) * sc * sy)
    if T_MEO <= t < T_DAT:                                # hạ cú nhảy cho đầu không đè mèo
        y0 += 190
    nen = np.array(c.convert("RGB")).astype(np.float32)
    y1, x1 = min(H, y0 + m.shape[0]), min(W, x0 + m.shape[1])
    yb, xb = max(0, y0), max(0, x0)
    nen[yb:y1, xb:x1] *= m[yb - y0:y1 - y0, xb - x0:x1 - x0, None]  # nhân: nền trắng của clip trong suốt
    return Image.fromarray(nen.astype(np.uint8), "RGB").convert("RGBA")

def phu_de(c, t):
    d = ImageDraw.Draw(c); f = font(62)
    d.rectangle((0, 1560, W, H), fill="white")
    dong1 = "Mấy cái logo các hãng AI, nhìn kỹ một hồi,"
    dong2 = "Cái nào cũng trông như… mông mèo, thế thôi."
    co = 62
    while max(f.getlength(dong1), f.getlength(dong2)) > 980:
        co -= 2; f = font(co)
    d.text(((W - f.getlength(dong1)) / 2, 1610), dong1, font=f, fill="#111")
    if t >= T_DONG2:
        hien = dong2 if t >= T_THOI else ("Cái nào cũng trông như… mông mèo," if t >= T_MEO else "Cái nào cũng trông như…")
        d.text(((W - f.getlength(dong2)) / 2, 1610 + co * 1.25), hien, font=f, fill="#111")

def khung(ds, t):
    c = nhan_vat(san_khau(t), ds, t)
    z, cx, cy = camera(t)
    z = max(1.0, z)
    w, h = W / z, H / z
    x0, y0 = min(max(cx - w / 2, 0), W - w), min(max(cy - h / 2, 0), H - h)
    c = c.transform((W, H), Image.AFFINE, (w / W, 0, x0, 0, h / H, y0), Image.BICUBIC)
    phu_de(c, t)
    return c.convert("RGB")

# ---- âm thanh: giọng + hiệu ứng tổng hợp
def am_thanh(p):
    sr = 44100; n = int(DUR * sr); buf = np.zeros(n)
    w = wave.open(GIONG); ch, sw, r0 = w.getnchannels(), w.getsampwidth(), w.getframerate()
    v = np.frombuffer(w.readframes(w.getnframes()), {2: np.int16, 4: np.int32}[sw]).astype(float) / (2 ** (8 * sw - 1))
    v = v.reshape(-1, ch).mean(axis=1)
    v = np.interp(np.arange(0, len(v), r0 / sr), np.arange(len(v)), v)
    buf[:min(n, len(v))] += v[:n]
    def them(t, dur, fn, amp):
        s = int(t * sr); x = np.arange(int(dur * sr)) / sr; e = min(n, s + len(x))
        buf[s:e] += amp * fn(x)[:e - s]
    for t0 in T_LOGO:
        them(t0, 0.09, lambda x: np.sin(2 * np.pi * (500 + 2500 * x) * x) * np.exp(-x * 40), 0.16)   # pốp logo
    them(T_MEO, 0.35, lambda x: np.sin(2 * np.pi * (70 + 600 * np.exp(-x * 18)) * x) * np.exp(-x * 9), 0.3)  # bật mèo
    them(T_DAT, 0.2, lambda x: np.sin(2 * np.pi * 85 * x) * np.exp(-x * 20), 0.35)                 # tiếp đất
    buf = np.clip(buf, -1, 1)
    o = wave.open(p, "w"); o.setnchannels(1); o.setsampwidth(2); o.setframerate(sr)
    o.writeframes((buf * 32000).astype(np.int16).tobytes()); o.close()

if __name__ == "__main__":
    ds = nap_clip()
    if len(sys.argv) > 1:
        for s in sys.argv[1:]:
            khung(ds, float(s)).save(os.path.join(D, "kiem", f"N2-{s}.png"))
        sys.exit()
    p = os.path.join(D, "kiem", "_am.wav"); am_thanh(p)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-i", p, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "192k", "-shortest", RA],
                          stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        ff.stdin.write(khung(ds, i / FPS).tobytes())
    ff.stdin.close(); ff.wait(); print("xong", RA)
