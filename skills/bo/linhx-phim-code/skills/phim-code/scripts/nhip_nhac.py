#!/usr/bin/env python3
"""Biến bài nhạc thành số để hình bám nhạc (Claude không nghe được). Chỉ cần ffmpeg + numpy.

python3 nhip_nhac.py nhac.mp3 [--fps 24] [--bpm 120] [--ra nhip.json] [--js]

Ra nhip.json: bpm, beats (giây, lưới đều), onsets (giây, các cú đánh/âm tiết), rms và low (0..1, mỗi khung hình;
low là dải < 150 Hz, tiếng trống bass). --js ghi thêm nhip.js dạng `window.NHIP = {...}` để nhúng vào trang.
Ước BPM có thể ra nửa hoặc gấp đôi nhịp thật: nghe thử, sai thì truyền --bpm.
"""
import argparse, json, subprocess, sys
import numpy as np

ap = argparse.ArgumentParser(); ap.add_argument("nhac"); ap.add_argument("--fps", type=float, default=24)
ap.add_argument("--bpm", type=float); ap.add_argument("--ra", default="nhip.json"); ap.add_argument("--js", action="store_true")
a = ap.parse_args()
SR = 22050
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", a.nhac, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
x = np.frombuffer(raw, dtype=np.float32)
if not len(x): sys.exit("không đọc được tiếng")
dur = len(x) / SR

# phổ ngắn: cửa sổ 2048, bước 512
N, HOP = 2048, 512
nf = 1 + (len(x) - N) // HOP if len(x) >= N else 1
x = np.pad(x, (0, max(0, N + (nf - 1) * HOP - len(x))))
idx = np.arange(N)[None, :] + HOP * np.arange(nf)[:, None]
S = np.abs(np.fft.rfft(x[idx] * np.hanning(N), axis=1))
fr = SR / HOP
T0 = N / 2 / SR  # giờ của khung = tâm cửa sổ
logS = np.log1p(10 * S)
flux = np.maximum(0, np.diff(logS, axis=0)).sum(1); flux = np.concatenate([[0], flux])
flux = (flux - flux.mean()) / (flux.std() + 1e-9)

# onset: đỉnh cục bộ vượt ngưỡng động, cách nhau >= 80 ms
k = int(0.08 * fr) or 1
thr = np.convolve(flux, np.ones(int(fr) or 1) / (int(fr) or 1), "same") + 0.5
on = [i for i in range(1, len(flux) - 1) if flux[i] > thr[i] and flux[i] == flux[max(0, i - k):i + k + 1].max()]
onsets = [round(i / fr + T0, 3) for i in on]

# tempo: tự tương quan đường onset, 70–180 BPM
if a.bpm: bpm = a.bpm
else:
    ac = np.correlate(flux, flux, "full")[len(flux) - 1:]
    lags = np.arange(int(fr * 60 / 180), int(fr * 60 / 70) + 1)
    j = int(lags[np.argmax(ac[lags])])
    d = (ac[j - 1] - ac[j + 1]) / (2 * (ac[j - 1] - 2 * ac[j] + ac[j + 1]) + 1e-12)  # nội suy parabol
    bpm = 60 * fr / (j + float(np.clip(d, -0.5, 0.5)))
per = 60 / bpm
# pha: chọn điểm bắt đầu cho tổng flux trên lưới lớn nhất
pha = max(np.arange(0, per, 0.01), key=lambda p: flux[np.clip(((np.arange(p, dur, per) - T0) * fr).round().astype(int), 0, len(flux) - 1)].sum())
beats = [round(t, 3) for t in np.arange(pha, dur, per)]

# rms và low mỗi khung hình
freqs = np.fft.rfftfreq(N, 1 / SR)
low = S[:, freqs < 150].sum(1); rms = np.sqrt((S ** 2).mean(1))
tf = np.arange(0, dur, 1 / a.fps); fi = np.clip((tf * fr).astype(int), 0, nf - 1)
norm = lambda v: np.round(v / (np.percentile(v, 98) + 1e-9), 3).clip(0, 1).tolist()
kq = {"bpm": round(float(bpm), 2), "giay": round(dur, 3), "fps": a.fps, "beats": beats, "onsets": onsets,
      "rms": norm(rms[fi]), "low": norm(low[fi])}
json.dump(kq, open(a.ra, "w"), separators=(",", ":"))
if a.js: open(a.ra.rsplit(".", 1)[0] + ".js", "w").write("window.NHIP=" + json.dumps(kq, separators=(",", ":")) + ";\n")
print(f"{a.ra}: {kq['bpm']} BPM, {len(beats)} phách, {len(onsets)} cú đánh, {dur:.1f}s")
