#!/usr/bin/env python3
"""Kiểm file MP4 đã render, chỉ cần ffmpeg/ffprobe. Thoát 1 nếu có LỖI.

python3 kiem_video.py phim.mp4 [--kho 16:9|9:16|1:1] [--giay 30-45] [--srt phu-de.srt] [--json ra.json]

Đo: khổ, cỡ, fps, độ dài; tiếng: độ to tích hợp (LUFS), đỉnh thật (dBTP), im lặng đầu phim;
hình: khung đen, đứng hình > 3 giây, khung đầu trơn (ảnh bìa trống); phụ đề dài hơn phim.
"""
import json, re, subprocess, sys, argparse

ap = argparse.ArgumentParser()
ap.add_argument("video"); ap.add_argument("--kho"); ap.add_argument("--giay"); ap.add_argument("--srt"); ap.add_argument("--json")
a = ap.parse_args()
loi, canh = [], []

def chay(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, errors="replace")

pr = json.loads(chay(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", a.video]).stdout or "{}")
v = next((s for s in pr.get("streams", []) if s["codec_type"] == "video"), None)
au = next((s for s in pr.get("streams", []) if s["codec_type"] == "audio"), None)
if not v:
    print("LỖI: không có luồng hình"); sys.exit(1)
w, h = int(v["width"]), int(v["height"])
num, den = map(int, v.get("avg_frame_rate", "0/1").split("/")); fps = num / den if den else 0
dur = float(pr["format"].get("duration", 0))
tt = {"rong": w, "cao": h, "fps": round(fps, 2), "giay": round(dur, 2), "co_tieng": bool(au)}

if a.kho:
    x, y = map(int, a.kho.split(":"))
    if abs(w / h - x / y) > 0.01: loi.append(f"khổ {w}x{h} không phải {a.kho}")
if min(w, h) < 1080: canh.append(f"cạnh ngắn {min(w, h)}px < 1080 (bản nháp thì bỏ qua)")
if v.get("pix_fmt") not in ("yuv420p", "yuvj420p"): canh.append(f"pix_fmt {v.get('pix_fmt')}: nên yuv420p để điện thoại phát được")
if a.giay:
    lo, hi = map(float, a.giay.split("-"))
    if not lo <= dur <= hi: loi.append(f"dài {dur:.1f}s, ngoài khoảng {a.giay}s")

if au:
    e = chay(["ffmpeg", "-nostats", "-i", a.video, "-map", "0:a:0", "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
    tail = e[e.rfind("Summary:"):]
    I = re.search(r"I:\s+(-?[\d.]+) LUFS", tail); P = re.search(r"Peak:\s+(-?[\d.inf]+) dBFS", tail)
    lufs = float(I.group(1)) if I else None
    peak = float(P.group(1)) if P and P.group(1) not in ("-inf", "inf") else None
    tt.update(lufs=lufs, dinh_dbtp=peak)
    if lufs is not None:
        if lufs < -20 or lufs > -10: loi.append(f"độ to {lufs} LUFS, cần khoảng -14 (chấp nhận -18..-12)")
        elif not -18 <= lufs <= -12: canh.append(f"độ to {lufs} LUFS, nên -14")
    if peak is not None:
        if peak > 0: loi.append(f"đỉnh thật {peak} dBTP > 0: vỡ tiếng")
        elif peak > -1: canh.append(f"đỉnh thật {peak} dBTP > -1: nén AAC có thể vỡ")
    s = chay(["ffmpeg", "-nostats", "-i", a.video, "-map", "0:a:0", "-af", "silencedetect=n=-45dB:d=0.3", "-f", "null", "-"]).stderr
    m = re.search(r"silence_start: (-?[\d.]+)\s.*?silence_end: ([\d.]+)", s, re.S)
    if m and float(m.group(1)) <= 0.05 and float(m.group(2)) > 1.0:
        canh.append(f"{float(m.group(2)):.1f} giây đầu im lặng")
else:
    canh.append("không có tiếng (phim dưới 13 giây xem không tiếng thì được, ghi lý do)")

vf = "blackdetect=d=0.4:pix_th=0.08,freezedetect=n=0.002:d=3"
e = chay(["ffmpeg", "-nostats", "-i", a.video, "-map", "0:v:0", "-vf", vf, "-f", "null", "-"]).stderr
den_ = [(float(x), float(y)) for x, y in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", e)]
for x, y in den_:
    if x < 0.05: canh.append(f"mở bằng khung đen {y:.1f}s: ảnh bìa sẽ đen")
    elif y < dur - 0.6: canh.append(f"khung đen giữa phim {x:.1f}-{y:.1f}s")
for x in re.findall(r"freeze_start: ([\d.]+)", e):
    canh.append(f"đứng hình từ {float(x):.1f}s quá 3 giây")
tt.update(khung_den=den_)

e = chay(["ffmpeg", "-nostats", "-i", a.video, "-vf", "select=eq(n\\,0),signalstats,metadata=print", "-frames:v", "1", "-f", "null", "-"]).stderr
mn, mx = re.search(r"YMIN=(\d+)", e), re.search(r"YMAX=(\d+)", e)
if mn and mx and int(mx.group(1)) - int(mn.group(1)) < 12: canh.append("khung đầu một màu trơn: ảnh bìa trống")

if a.srt:
    ts = re.findall(r"--> (\d+):(\d+):(\d+)[,.](\d+)", open(a.srt, encoding="utf-8").read())
    if ts:
        hh, mm, ss, ms = map(int, ts[-1]); cuoi = hh * 3600 + mm * 60 + ss + ms / 1000
        if cuoi > dur + 0.2: loi.append(f"phụ đề kết thúc {cuoi:.1f}s, phim chỉ {dur:.1f}s")

bc = {"video": a.video, "thong_tin": tt, "loi": loi, "canh": canh}
if a.json: json.dump(bc, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"# Kiểm video: {a.video}\n{w}x{h} {fps:.2f}fps {dur:.1f}s tiếng={'có' if au else 'không'}"
      + (f" {tt.get('lufs')} LUFS, đỉnh {tt.get('dinh_dbtp')} dBTP" if au else ""))
print(f"\nLỖI ({len(loi)})"); [print("-", x) for x in loi] or print("- không")
print(f"\nCẢNH BÁO ({len(canh)})"); [print("-", x) for x in canh] or print("- không")
sys.exit(1 if loi else 0)
