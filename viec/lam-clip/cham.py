"""Chấm máy một clip Lam. Chỉ cần ffmpeg/ffprobe trong PATH, không cần thư viện.

Dùng:
  python cham.py kiosk <clip.webm> <cho.webm> <thu_muc_ra>
  python cham.py dt    <clip.mp4>  <lam-cho-720.mp4> <thu_muc_ra>

Ra: <thu_muc_ra>/<ma>-cham.json và <ma>-tam.jpg (8 khung + khung chuẩn, để Claude soi).
Đạt khi: đúng khổ, 5–6,5 giây, (kiosk) có alpha, SSIM khung đầu và khung cuối so khung cuối
của clip chuẩn >= 0,90.
"""
import json, os, re, subprocess, sys, tempfile

def chay(lenh):
    return subprocess.run(lenh, capture_output=True, text=True)

def thong_tin(p):
    r = chay(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", p])
    j = json.loads(r.stdout)
    v = [s for s in j["streams"] if s["codec_type"] == "video"][0]
    tags = {k.lower(): str(x) for k, x in (v.get("tags") or {}).items()}
    return {
        "rong": v["width"], "cao": v["height"],
        "giay": round(float(j["format"]["duration"]), 2),
        "codec": v["codec_name"],
        "alpha": v.get("pix_fmt", "").startswith("yuva") or tags.get("alpha_mode") == "1",
    }

def vao(p, alpha):
    # VP9 alpha chỉ giải đúng bằng libvpx-vp9
    return (["-c:v", "libvpx-vp9"] if alpha and p.lower().endswith(".webm") else []) + ["-i", p]

def khung(p, alpha, cuoi, ra, rong, cao):
    vt = ["-sseof", "-0.15"] if cuoi else ["-ss", "0"]
    # ghép lên nền xám để so được cả clip trong suốt
    f = (f"color=c=0x808080:s={rong}x{cao}[n];[0:v]scale={rong}:{cao},format=rgba[c];"
         f"[n][c]overlay=shortest=1,format=rgb24")
    r = chay(["ffmpeg", "-v", "error", "-y", *vt, *vao(p, alpha), "-filter_complex", f,
              "-frames:v", "1", ra])
    if r.returncode or not os.path.exists(ra):
        raise RuntimeError(f"khong lay duoc khung {p}: {r.stderr[-300:]}")

def ssim(a, b):
    r = chay(["ffmpeg", "-v", "info", "-i", a, "-i", b, "-lavfi", "ssim", "-f", "null", "-"])
    m = re.search(r"All:([0-9.]+)", r.stderr)
    return round(float(m.group(1)), 4) if m else 0.0

def tam(p, alpha, chuan_png, ra, giay):
    # 8 khung đều + khung chuẩn, mỗi ô cao 480
    fps = 8 / max(giay, 0.5)
    tmp = ra + ".8.png"
    chay(["ffmpeg", "-v", "error", "-y", *vao(p, alpha), "-filter_complex",
          f"color=c=0x808080:s=1080x1920[n];[0:v]scale=1080:1920,format=rgba[c];"
          f"[n][c]overlay=shortest=1,fps={fps:.4f},scale=-2:480,tile=8x1",
          "-frames:v", "1", tmp])
    chay(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-i", chuan_png, "-filter_complex",
          "[1:v]scale=-2:480[c];[c][0:v]hstack=inputs=2", "-q:v", "4", ra])
    if os.path.exists(tmp):
        os.remove(tmp)

def main():
    loai, clip, chuan, ra = sys.argv[1:5]
    os.makedirs(ra, exist_ok=True)
    ma = os.path.splitext(os.path.basename(clip))[0]
    tt, tc = thong_tin(clip), thong_tin(chuan)
    rong, cao = tc["rong"], tc["cao"]
    loi = []
    if (tt["rong"], tt["cao"]) != (rong, cao):
        loi.append(f"kho {tt['rong']}x{tt['cao']} != {rong}x{cao}")
    if not 5.0 <= tt["giay"] <= 6.5:
        loi.append(f"do dai {tt['giay']}s ngoai 5-6.5s")
    if loai == "kiosk" and not tt["alpha"]:
        loi.append("khong co alpha")
    with tempfile.TemporaryDirectory() as d:
        c = os.path.join(d, "chuan.png"); khung(chuan, tc["alpha"], True, c, rong, cao)
        a = os.path.join(d, "dau.png"); khung(clip, tt["alpha"], False, a, rong, cao)
        b = os.path.join(d, "cuoi.png"); khung(clip, tt["alpha"], True, b, rong, cao)
        s_dau, s_cuoi = ssim(a, c), ssim(b, c)
        tam(clip, tt["alpha"], c, os.path.join(ra, f"{ma}-tam.jpg"), tt["giay"])
    if s_dau < 0.90: loi.append(f"SSIM dau {s_dau} < 0.90")
    if s_cuoi < 0.90: loi.append(f"SSIM cuoi {s_cuoi} < 0.90")
    kq = {"ma": ma, **tt, "ssim_dau": s_dau, "ssim_cuoi": s_cuoi,
          "dat_may": not loi, "loi": loi}
    with open(os.path.join(ra, f"{ma}-cham.json"), "w", encoding="utf-8") as f:
        json.dump(kq, f, ensure_ascii=False, indent=1)
    print(json.dumps(kq, ensure_ascii=False))
    sys.exit(0 if not loi else 1)

if __name__ == "__main__":
    main()
