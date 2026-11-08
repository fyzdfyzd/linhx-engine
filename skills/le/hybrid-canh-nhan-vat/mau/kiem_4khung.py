"""Trích 4 khung 0 / 2,5 / 5 / 7,5 giây, ghép cạnh ảnh đầu vào để duyệt nhân vật.
Dùng: python kiem_4khung.py <clip.mp4> <ra.png>"""
import subprocess, sys, tempfile, os
from PIL import Image

clip, ra = sys.argv[1], sys.argv[2]
goc = os.path.join(os.path.dirname(os.path.abspath(__file__)), "N2-char-in.png")
moc = [0, 2.5, 5, 7.5]
cao = 960
anh = [Image.open(goc).convert("RGB")]
with tempfile.TemporaryDirectory() as t:
    for i, s in enumerate(moc):
        p = os.path.join(t, f"{i}.png")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(s), "-i", clip, "-frames:v", "1", p], check=True)
        anh.append(Image.open(p).convert("RGB").copy())
rong = round(cao * 1080 / 1920)
bang = Image.new("RGB", ((rong + 10) * len(anh), cao), "#888")
for i, a in enumerate(anh):
    bang.paste(a.resize((rong, cao), Image.LANCZOS), (i * (rong + 10), 0))
bang.save(ra)
