"""Xuất 2 bản theo nhạc 96 BPM: python dung_nhac.py hybrid | flow"""
import os, subprocess, sys, warnings
import numpy as np, cv2
from PIL import Image
warnings.filterwarnings("ignore")
import dung_N2 as d, nhac
from nhac import BEAT, LECH, T_CHOT, DUR

GIONG = d.GIONG; D = d.D; FPS = 24
d.T_LOGO = [BEAT, 2 * BEAT, 3 * BEAT]
d.T_KY, d.T_DONG2, d.T_MEO, d.T_THOI = 2.43 + LECH, 3.87 + LECH, T_CHOT, 6.60 + LECH
d.T_CHU, d.T_DUNG, d.T_DAT, d.DUR, d.BEAT = 4 * BEAT, 9 * BEAT, 10.5 * BEAT, DUR, BEAT

def xuat(ra, khung, hieu):
    p = os.path.join(D, "kiem", "_am2.wav"); nhac.tron(GIONG, p, hieu)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920", "-r", str(FPS),
                           "-i", "-", "-i", p, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "192k", "-shortest", ra], stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        ff.stdin.write(khung(i / FPS).tobytes())
    ff.stdin.close(); ff.wait(); print("xong", ra)

def tieng():
    x = np.arange(int(.09 * nhac.SR)) / nhac.SR
    pop = np.sin(2 * np.pi * (500 + 2500 * x) * x) * np.exp(-x * 40)
    return [(t, pop, .14) for t in d.T_LOGO]

if sys.argv[1] == "hybrid":
    d.NHIP = [(0.0, 0.0)] + [(t + LECH, v) for t, v in d.NHIP[1:]]
    d.NHIP[-1] = (DUR, 5.10)
    d.NHIP = [(a if a != 6.12 + LECH else d.T_DAT, b) for a, b in d.NHIP]
    ds = d.nap_clip()
    xuat(os.path.join(D, "N2-hybrid-nhac.mp4"), lambda t: d.khung(ds, t), tieng())
else:
    # phương án Flow: clip nguyên khung, code chỉ chọn khung, đẩy máy, phụ đề
    c = cv2.VideoCapture(os.path.join(D, "flow", "N2-flow.mp4")); ds = []
    while True:
        ok, f = c.read()
        if not ok: break
        ds.append(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))
    # giây cảnh -> giây clip, né đoạn há miệng 1,0-2,3 s
    NHIP = [(0, .1), (d.T_KY - .02, .5), (d.T_KY, 2.5), (9 * BEAT, 3.4), (T_CHOT - .02, 3.45), (T_CHOT, 4.1), (DUR, 7.3)]
    def v(t):
        t = int(t * FPS / 2) * 2 / FPS
        for (a, x), (b, y) in zip(NHIP, NHIP[1:]):
            if a <= t <= b:
                return x + (y - x) * (t - a) / (b - a)
        return NHIP[-1][1]
    def khung(t):
        im = Image.fromarray(ds[min(len(ds) - 1, round(v(t) * 24))]).resize((1080, 1920), Image.BICUBIC).convert("RGBA")
        k = 0 if t < T_CHOT else 1 - np.exp(-(t - T_CHOT) * 16)
        e = d.ease((t - d.T_KY) / (9 * BEAT - d.T_KY))
        z = 1 + .03 * e + .07 * k
        cy = 960 - 10 * e - 300 * k
        w, h = 1080 / z, 1920 / z
        x0, y0 = (1080 - w) / 2, min(max(cy - h / 2, 0), 1920 - h)
        im = im.transform((1080, 1920), Image.AFFINE, (w / 1080, 0, x0, 0, h / 1920, y0), Image.BICUBIC)
        d.phu_de(im, t)
        return im.convert("RGB")
    xuat(os.path.join(D, "N2-flow-nhac.mp4"), khung, [])
