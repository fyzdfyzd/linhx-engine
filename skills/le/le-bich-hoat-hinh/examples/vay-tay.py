"""Mẫu thử đường A: Lê Bích vẫy tay 1 giây, lặp liền. Ra GIF (+ WebP nếu Pillow hỗ trợ, + MP4 nếu có ffmpeg).
Chạy: python3 examples/vay-tay.py thu-muc-ra"""
import math, os, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from PIL import Image, ImageDraw
from lebich import nhan_vat, chu

ra = sys.argv[1] if len(sys.argv) > 1 else "ra"; os.makedirs(ra, exist_ok=True)
fps, giay = 24, 1.0; n = int(fps * giay); khung = []
for i in range(n):
    p = i / n                                   # 0..1, khung cuối nối khung đầu
    song = math.sin(2 * math.pi * p)
    im = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    nv = nhan_vat(mat="cuoi" if song > 0.6 else "cham", mieng="ha",
                  tay_phai=-140 + 25 * song, dau=3 * song, bung=1 + 0.03 * abs(song), rong=440, le=160)
    im.alpha_composite(nv.crop((0, 40, 440, 470)), (36, 0))
    chu(ImageDraw.Draw(im), (256, 470), "Xin chào!", 56, vien=6, can="mm")
    khung.append(im); im.save(f"{ra}/f{i:03d}.png")
khung[0].save(f"{ra}/vay-tay.gif", save_all=True, append_images=khung[1:], duration=int(1000 / fps),
              loop=0, disposal=2, transparency=0)
try:
    khung[0].save(f"{ra}/vay-tay.webp", save_all=True, append_images=khung[1:], duration=int(1000 / fps), loop=0, lossless=True)
except Exception as e:
    print("không xuất được WebP:", e)
try:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", f"{ra}/f%03d.png",
                    "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2,format=yuv420p", "-c:v", "libx264", f"{ra}/vay-tay.mp4"], check=True)
except Exception as e:
    print("không xuất được MP4:", e)
print("xong:", sorted(os.listdir(ra))[-3:])
