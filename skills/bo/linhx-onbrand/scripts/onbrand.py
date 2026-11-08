#!/usr/bin/env python3
"""onbrand.py: chấm một thiết kế có bám brand guideline không.

Lệnh:
  tao-cay  <thu-muc-brands> <brand-id>           tạo cây thư mục chuẩn cho một brand mới
  cham     <brand.json> <file> [--ra ket-qua.json] chấm tự động phần máy đo được (màu, chữ, nội dung)
  gop      <ket-qua.json> <diem-nhin.json>        gộp điểm Claude nhìn (logo, hình/bố cục) vào kết quả
  bao-cao  <ket-qua.json ...> --ra bao-cao.html   báo cáo HTML; nhiều file thì xếp hạng (dùng cho "thi")

File chấm được: .png .jpg .jpeg .webp .pdf .pptx .html .svg
Cần: Python 3, Pillow, numpy. PDF cần pdftoppm/pdffonts/pdftotext (poppler).
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile, zipfile, html as H
from pathlib import Path

CAY = {
    "00-goc": "File guideline gốc (PDF, AI, PPTX...), giữ nguyên tên",
    "01-logo": "Logo từng biến thể (PNG nền trong suốt nếu có, SVG nếu có) + trang vùng an toàn",
    "02-mau": "Trang bảng màu; mã màu nằm trong brand.json",
    "03-chu": "Trang font, file font nếu được phép",
    "04-hinh-anh": "Ảnh mẫu đúng phong cách",
    "05-icon": "Bộ icon, hoạ tiết",
    "06-ung-dung": "Ấn phẩm mẫu: social, booth, merchandise...",
    "07-bai-thi": "Thiết kế cần chấm (của designer hoặc AI), mỗi người một thư mục con",
    "08-ket-qua": "Kết quả chấm JSON + báo cáo HTML",
    "09-khuon": "Khuôn thiết kế HTML đúng ngôn ngữ brand + token.css (skill onbrand-thiet-ke)",
}

# ---------- màu ----------

def hex2rgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def rgb2lab(rgb):
    import numpy as np
    c = np.asarray(rgb, dtype=float) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)

def de2000(a, b):
    """CIEDE2000, a: (N,3) Lab, b: (M,3) Lab -> (N,M)."""
    import numpy as np
    L1, a1, b1 = [a[:, None, i] for i in range(3)]
    L2, a2, b2 = [b[None, :, i] for i in range(3)]
    C1 = np.hypot(a1, b1); C2 = np.hypot(a2, b2); Cm = (C1 + C2) / 2
    G = 0.5 * (1 - np.sqrt(Cm ** 7 / (Cm ** 7 + 25 ** 7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = np.hypot(a1p, b1), np.hypot(a2p, b2)
    h1p = np.degrees(np.arctan2(b1, a1p)) % 360; h2p = np.degrees(np.arctan2(b2, a2p)) % 360
    dL = L2 - L1; dC = C2p - C1p
    dh = h2p - h1p; dh = np.where(dh > 180, dh - 360, dh); dh = np.where(dh < -180, dh + 360, dh)
    dh = np.where(C1p * C2p == 0, 0, dh)
    dH = 2 * np.sqrt(C1p * C2p) * np.sin(np.radians(dh / 2))
    Lm = (L1 + L2) / 2; Cmp = (C1p + C2p) / 2
    hs = h1p + h2p
    hm = np.where(C1p * C2p == 0, hs, np.where(np.abs(h1p - h2p) <= 180, hs / 2, np.where(hs < 360, (hs + 360) / 2, (hs - 360) / 2)))
    T = 1 - 0.17 * np.cos(np.radians(hm - 30)) + 0.24 * np.cos(np.radians(2 * hm)) + 0.32 * np.cos(np.radians(3 * hm + 6)) - 0.20 * np.cos(np.radians(4 * hm - 63))
    SL = 1 + 0.015 * (Lm - 50) ** 2 / np.sqrt(20 + (Lm - 50) ** 2); SC = 1 + 0.045 * Cmp; SH = 1 + 0.015 * Cmp * T
    RT = -2 * np.sqrt(Cmp ** 7 / (Cmp ** 7 + 25 ** 7)) * np.sin(np.radians(60 * np.exp(-((hm - 275) / 25) ** 2)))
    return np.sqrt((dL / SL) ** 2 + (dC / SC) ** 2 + (dH / SH) ** 2 + RT * (dC / SC) * (dH / SH))

def bang_mau(brand):
    m = brand["mau"]; out = []
    for nhom in ("chinh", "phu", "nhan"):
        for c in m.get(nhom, []):
            out.append((c["ten"], c["hex"].upper(), nhom))
    for ten, hx in m.get("mau_khi_in_ra_man_hinh", {}).items():
        if not ten.startswith("_"):
            out.append((ten, hx.upper(), "render"))
    return out

def cham_mau(brand, anh_paths):
    import numpy as np
    from PIL import Image
    bm = bang_mau(brand)
    lab_b = rgb2lab(np.array([hex2rgb(h) for _, h, _ in bm]))
    thr = brand["mau"].get("nguong_delta_e", 8)
    can = brand["mau"].get("toi_thieu_phu_mau_thuong_hieu", 0.85)
    nhan = {c["ten"]: c.get("toi_da_dien_tich", 1) for c in brand["mau"].get("nhan", [])}
    tong_phang = 0; dung = 0; dem_ten = {}; lech = {}
    for p in [q for q in anh_paths if not str(q).endswith(".mask.png")]:
        im = Image.open(p).convert("RGB"); im.thumbnail((900, 900))
        a = np.asarray(im).astype(int)
        mp = Path(p).with_suffix(".mask.png")
        if mp.exists():  # thiet_ke.py để lại mặt nạ: vùng ảnh chụp tô #FF00FF, bỏ khỏi phép đo màu
            mk = np.asarray(Image.open(mp).convert("RGB").resize(im.size)).astype(int)
            anh = (mk[..., 0] > 230) & (mk[..., 1] < 30) & (mk[..., 2] > 230)
        else:
            anh = np.zeros(a.shape[:2], bool)
        # chỉ xét vùng "phẳng" (đồ hoạ): pixel giống hệt 4 hàng xóm. Ảnh chụp tự loại ra.
        c = a[1:-1, 1:-1]
        flat = np.ones(c.shape[:2], bool)
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            nb = a[1 + dy:a.shape[0] - 1 + dy, 1 + dx:a.shape[1] - 1 + dx]
            flat &= (np.abs(c - nb).sum(-1) <= 6)
        flat &= ~anh[1:-1, 1:-1]
        px = c[flat]
        if len(px) == 0:
            continue
        q = (px // 4) * 4 + 2  # gom màu cho nhanh
        # bỏ màu trung tính (trắng, xám, đen): nền trắng không được "cứu" điểm cho đồ hoạ sai màu
        co_mau = q[(q.max(1) - q.min(1)) > 24]
        # ấn phẩm nền sáng chỉ có chữ màu nhỏ: không đủ mảng có màu thì đo cả màu trung tính (nền ngà, be...)
        q = co_mau if len(co_mau) >= 0.02 * len(q) else q[(np.abs(q - 128).max(1) < 120)]
        if len(q) == 0:
            continue
        uniq, cnt = np.unique(q, axis=0, return_counts=True)
        # đồ hoạ dùng ít màu, mỗi màu phủ mảng lớn; ảnh chụp rải hàng nghìn sắc nhỏ: bỏ sắc < 0,2% khung
        giu = cnt >= 0.002 * c.shape[0] * c.shape[1]
        uniq, cnt = uniq[giu], cnt[giu]
        if len(cnt) == 0:
            continue
        d = de2000(rgb2lab(uniq), lab_b)
        imin = d.argmin(1); dmin = d.min(1)
        tong_phang += cnt.sum()
        for u, n, i, dm in zip(uniq, cnt, imin, dmin):
            if dm <= thr:
                dung += n; ten = bm[i][0].replace(" (render)", "")
                dem_ten[ten] = dem_ten.get(ten, 0) + int(n)
            else:
                k = "#%02X%02X%02X" % tuple(u)
                e = lech.setdefault(k, [0, bm[i][0], float(dm)]); e[0] += int(n)
    if tong_phang == 0:
        return {"diem_ty_le": None, "ghi_chu": "không có vùng đồ hoạ có màu để đo (toàn ảnh chụp hoặc chỉ đen trắng?)"}
    phu = dung / tong_phang
    ty = min(1.0, phu / can)
    canh_bao = []
    for ten, maxa in nhan.items():
        s = dem_ten.get(ten, 0) / tong_phang
        if s > maxa:
            ty -= 0.2; canh_bao.append(f"màu nhấn {ten} chiếm {s:.0%} diện tích đồ hoạ, chuẩn tối đa {maxa:.0%}")
    # gom các màu lệch gần nhau thành cụm
    top = sorted(lech.items(), key=lambda kv: -kv[1][0])
    cum = []
    for hx, (n, gan, dm) in top:
        lab = rgb2lab(np.array([hex2rgb(hx)]))
        for cc in cum:
            if de2000(lab, rgb2lab(np.array([hex2rgb(cc["hex"])])))[0, 0] < 6:
                cc["dien_tich"] += n; break
        else:
            cum.append({"hex": hx, "dien_tich": n, "gan_nhat": gan, "delta_e": round(dm, 1)})
    cum = [dict(c, dien_tich=round(c["dien_tich"] / tong_phang, 3)) for c in cum if c["dien_tich"] / tong_phang >= 0.005][:8]
    return {
        "diem_ty_le": round(max(0.0, ty), 3),
        "phu_mau_thuong_hieu": round(phu, 3),
        "can_dat": can,
        "mau_dung": {k: round(v / tong_phang, 3) for k, v in sorted(dem_ten.items(), key=lambda kv: -kv[1])},
        "mau_lech": cum,
        "canh_bao": canh_bao,
    }

# ---------- chữ ----------

def chuan_hoa_font(f):
    f = re.sub(r"^[A-Z]{6}\+", "", f)
    return re.sub(r"[-_ ]?(Regular|Medium|Bold|Light|Italic|Semi ?Bold|Demi|Heavy|Black|MT|PS)+$", "", f, flags=re.I).replace("-", " ").strip()

def lay_font_va_chu(path, tmp):
    ext = path.suffix.lower(); fonts = set(); text = ""
    if ext == ".pdf":
        out = subprocess.run(["pdffonts", str(path)], capture_output=True, text=True).stdout.splitlines()[2:]
        fonts = {l.split()[0] for l in out if l.strip()}
        text = subprocess.run(["pdftotext", str(path), "-"], capture_output=True, text=True).stdout
    elif ext == ".pptx":
        with zipfile.ZipFile(path) as z:
            for n in z.namelist():
                if n.endswith(".xml") and ("slides/slide" in n or "theme" in n or "slideMasters" in n):
                    x = z.read(n).decode("utf8", "ignore")
                    fonts |= {f for f in re.findall(r'typeface="([^"+][^"]*)"', x) if f and not f.startswith("+")}
                    if "slides/slide" in n:
                        text += " ".join(re.findall(r"<a:t>([^<]*)</a:t>", x)) + "\n"
    elif ext in (".html", ".htm", ".svg"):
        x = path.read_text("utf8", "ignore")
        for ff in re.findall(r"font-family\s*[:=]\s*['\"]?([^;\"'>]+)", x):
            fonts.add(ff.split(",")[0].strip(" '\""))
        for ff in re.findall(r"[{;\s]font\s*:[^;{}]*?['\"]([^'\"]+)['\"]", x):
            fonts.add(ff.strip())
        text = re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)[\s\S]*?</\1>", " ", x))
    return {chuan_hoa_font(f) for f in fonts if f}, text

def cham_chu(brand, fonts):
    if not fonts:
        return {"diem_ty_le": None, "ghi_chu": "file ảnh: không đọc được font, Claude nhìn và chấm"}
    k = lambda x: re.sub(r"[^a-z0-9]", "", x.lower())
    ok = [k(f) for f in brand["chu"]["font_cho_phep"]]
    logo = k(brand["chu"].get("font_logo_suy_doan", "").split(" ")[0])
    hop = sorted(f for f in fonts if any(o in k(f) for o in ok))
    la = sorted(f for f in fonts if f not in hop and not (logo and logo in k(f)))
    ty = len(hop) / max(1, len(hop) + len(la))
    return {"diem_ty_le": round(ty, 3), "font_dung": hop, "font_la": la}

def cham_noi_dung(brand, text):
    if not text.strip():
        return {"diem_ty_le": None, "ghi_chu": "không trích được chữ, Claude đọc ảnh và chấm"}
    loi = []
    for w in brand.get("noi_dung", {}).get("tu_cam", []):
        n = len(re.findall(re.escape(w), text, flags=re.I))
        if n: loi.append({"tu": w, "so_lan": n})
    return {"diem_ty_le": round(max(0.0, 1 - 0.25 * len(loi)), 3), "tu_cam_gap": loi}

# ---------- chuyển file thành ảnh ----------

def ra_anh(path, tmp):
    ext = path.suffix.lower()
    if ext in (".png", ".jpg", ".jpeg", ".webp"):
        return [path]
    if ext == ".pdf":
        subprocess.run(["pdftoppm", "-r", "60", "-png", str(path), str(Path(tmp) / "p")], check=True)
        return sorted(Path(tmp).glob("p-*.png"))
    if ext == ".pptx":
        so = shutil.which("soffice") or shutil.which("libreoffice")
        if so:
            subprocess.run([so, "--headless", "--convert-to", "pdf", "--outdir", tmp, str(path)], capture_output=True)
            pdf = Path(tmp) / (path.stem + ".pdf")
            if pdf.exists():
                return ra_anh(pdf, tmp)
    return []

# ---------- lệnh ----------

def lenh_tao_cay(a):
    goc = Path(a.thu_muc) / a.brand_id
    for d, mo_ta in CAY.items():
        (goc / d).mkdir(parents=True, exist_ok=True)
        (goc / d / "_DOC.txt").write_text(mo_ta + "\n", encoding="utf8")
    mau = Path(__file__).resolve().parent.parent / "data" / "brand.mau.json"
    if not (goc / "brand.json").exists() and mau.exists():
        shutil.copy(mau, goc / "brand.json")
    print(goc)

def lenh_cham(a):
    brand = json.loads(Path(a.brand).read_text("utf8"))
    tw = brand["trong_so_diem"]; f = Path(a.file)
    with tempfile.TemporaryDirectory() as tmp:
        anh = ra_anh(f, tmp)
        fonts, text = lay_font_va_chu(f, tmp)
        ban_html = f.with_suffix(".html")
        if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp") and ban_html.exists():
            fonts, text = lay_font_va_chu(ban_html, tmp)  # ảnh do thiet_ke.py dựng: đọc font, chữ từ HTML gốc
        kq_mau = cham_mau(brand, anh) if anh else {"diem_ty_le": None, "ghi_chu": "không ra được ảnh (pptx cần LibreOffice)"}
    kq = {
        "brand": brand["brand_id"], "file": str(f),
        "muc": {
            "mau": dict(kq_mau, toi_da=tw["mau"]),
            "chu": dict(cham_chu(brand, fonts), toi_da=tw["chu"]),
            "noi_dung": dict(cham_noi_dung(brand, text), toi_da=tw["noi_dung"]),
            "logo": {"diem_ty_le": None, "toi_da": tw["logo"], "can_claude_nhin": True},
            "hinh_bo_cuc": {"diem_ty_le": None, "toi_da": tw["hinh_bo_cuc"], "can_claude_nhin": True},
        },
    }
    tinh_tong(kq)
    out = json.dumps(kq, ensure_ascii=False, indent=2)
    if a.ra: Path(a.ra).write_text(out, encoding="utf8")
    print(out)

def tinh_tong(kq):
    da = sum(m["toi_da"] for m in kq["muc"].values() if m.get("diem_ty_le") is not None)
    diem = sum(m["diem_ty_le"] * m["toi_da"] for m in kq["muc"].values() if m.get("diem_ty_le") is not None)
    for m in kq["muc"].values():
        if m.get("diem_ty_le") is not None: m["diem"] = round(m["diem_ty_le"] * m["toi_da"], 1)
    kq["diem_da_cham"] = round(diem, 1); kq["tren_tong"] = da
    kq["diem_100"] = round(100 * diem / da, 1) if da else None
    kq["xep_loai"] = None if kq["diem_100"] is None else ("ĐẠT CHUẨN" if kq["diem_100"] >= 85 else "SỬA NHẸ" if kq["diem_100"] >= 70 else "LỆCH CHUẨN")
    kq["chua_cham"] = [k for k, m in kq["muc"].items() if m.get("diem_ty_le") is None]

def lenh_gop(a):
    kq = json.loads(Path(a.ket_qua).read_text("utf8")); nhin = json.loads(Path(a.diem_nhin).read_text("utf8"))
    for k, v in nhin.items():
        if k in kq["muc"]:
            if v.get("diem_ty_le") is not None and "ghi_chu" not in v:
                kq["muc"][k].pop("ghi_chu", None)  # ghi chú "máy không đọc được" không còn đúng
            kq["muc"][k].update(v); kq["muc"][k].pop("can_claude_nhin", None)
    tinh_tong(kq)
    Path(a.ket_qua).write_text(json.dumps(kq, ensure_ascii=False, indent=2), encoding="utf8")
    print(json.dumps({"diem_100": kq["diem_100"], "xep_loai": kq["xep_loai"], "chua_cham": kq["chua_cham"]}, ensure_ascii=False))

TEN_MUC = {"mau": "Màu", "chu": "Chữ", "logo": "Logo", "hinh_bo_cuc": "Hình ảnh và bố cục", "noi_dung": "Nội dung"}

def the_muc(k, m):
    d = "không tính" if m.get("diem") is None else f'{m["diem"]}/{m["toi_da"]}'
    ct = []
    if k == "mau" and m.get("phu_mau_thuong_hieu") is not None:
        ct.append(f'Màu thương hiệu phủ {m["phu_mau_thuong_hieu"]:.0%} vùng đồ hoạ (cần {m["can_dat"]:.0%}).')
        for c in m.get("mau_lech", []):
            ct.append(f'<span class="sw" style="background:{c["hex"]}"></span>{c["hex"]} chiếm {c["dien_tich"]:.1%}, gần {H.escape(c["gan_nhat"])} nhất (ΔE {c["delta_e"]})')
        ct += [H.escape(x) for x in m.get("canh_bao", [])]
    if k == "chu":
        if m.get("font_la"): ct.append("Font lạ: " + H.escape(", ".join(m["font_la"])))
        if m.get("font_dung"): ct.append("Font đúng: " + H.escape(", ".join(m["font_dung"])))
    if k == "noi_dung":
        for x in m.get("tu_cam_gap", []): ct.append(f'Còn chữ cấm “{H.escape(x["tu"])}” ×{x["so_lan"]}')
    for x in m.get("nhan_xet", []) if isinstance(m.get("nhan_xet"), list) else ([m["nhan_xet"]] if m.get("nhan_xet") else []):
        ct.append(H.escape(x))
    if m.get("ghi_chu"): ct.append(H.escape(m["ghi_chu"]))
    return f'<div class="muc"><div class="mh"><b>{TEN_MUC.get(k, k)}</b><span>{d}</span></div><ul>' + "".join(f"<li>{x}</li>" for x in ct) + "</ul></div>"

def lenh_bao_cao(a):
    ds = [json.loads(Path(p).read_text("utf8")) for p in a.ket_qua]
    ds.sort(key=lambda k: -(k.get("diem_100") or 0))
    bang = ""
    if len(ds) > 1:
        bang = "<h2>Xếp hạng</h2><table><tr><th>#</th><th>Bài</th><th>Điểm</th><th>Xếp loại</th>" + "".join(f"<th>{TEN_MUC[k]}</th>" for k in TEN_MUC) + "</tr>"
        for i, k in enumerate(ds, 1):
            bang += f'<tr><td>{i}</td><td>{H.escape(k.get("ten_bai") or Path(k["file"]).name)}</td><td><b>{k["diem_100"]}</b></td><td>{k["xep_loai"]}</td>' + "".join(f'<td>{k["muc"][m].get("diem", "–")}</td>' for m in TEN_MUC) + "</tr>"
        bang += "</table>"
    the = ""
    for k in ds:
        cls = {"ĐẠT CHUẨN": "ok", "SỬA NHẸ": "warn"}.get(k["xep_loai"], "bad")
        the += f'<section><h3>{H.escape(k.get("ten_bai") or Path(k["file"]).name)} <span class="pill {cls}">{k["diem_100"]} · {k["xep_loai"]}</span></h3>'
        if k["chua_cham"]: the += f'<p class="note">Không chấm hoặc chưa chấm: {", ".join(TEN_MUC[c] for c in k["chua_cham"])} (điểm tính trên {k["tren_tong"]} điểm đã chấm)</p>'
        the += "".join(the_muc(m, k["muc"][m]) for m in TEN_MUC) + "</section>"
    css = """:root{--bg:#fff;--fg:#181718;--mut:#5b6b63;--card:#F6F8ED;--line:#dfe6da;--acc:#106047}
@media (prefers-color-scheme:dark){:root{--bg:#0f1a15;--fg:#eef3ec;--mut:#9fb3a8;--card:#17251e;--line:#24382d;--acc:#6dc854}}
body{background:var(--bg);color:var(--fg);font:15px/1.5 'Avenir Next',Avenir,system-ui,sans-serif;max-width:900px;margin:0 auto;padding:24px 16px}
h1{color:var(--acc);margin:0 0 4px}table{border-collapse:collapse;width:100%;font-size:14px;overflow-x:auto;display:block}
td,th{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left}section{background:var(--card);border-radius:14px;padding:12px 16px;margin:16px 0}
.muc{border-top:1px solid var(--line);padding:6px 0}.mh{display:flex;justify-content:space-between}ul{margin:4px 0 0;padding-left:18px;color:var(--mut)}
.sw{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:6px;vertical-align:-1px;border:1px solid var(--line)}
.pill{font-size:13px;padding:2px 10px;border-radius:99px;margin-left:8px}.ok{background:#00B579;color:#fff}.warn{background:#D9E74C;color:#181718}.bad{background:#FF8533;color:#181718}.note{color:var(--mut);font-size:13px}"""
    brand = ds[0]["brand"] if ds else ""
    doc = f'<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Chấm onbrand</title><style>{css}</style><body><h1>Chấm onbrand: {H.escape(brand)}</h1><p class="note">Màu, chữ, nội dung do script đo; logo, hình ảnh và bố cục do Claude nhìn và chấm theo rubric.</p>{bang}{the}</body></html>'
    Path(a.ra).write_text(doc, encoding="utf8"); print(a.ra)

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="lenh", required=True)
    t = s.add_parser("tao-cay"); t.add_argument("thu_muc"); t.add_argument("brand_id"); t.set_defaults(f=lenh_tao_cay)
    c = s.add_parser("cham"); c.add_argument("brand"); c.add_argument("file"); c.add_argument("--ra"); c.set_defaults(f=lenh_cham)
    g = s.add_parser("gop"); g.add_argument("ket_qua"); g.add_argument("diem_nhin"); g.set_defaults(f=lenh_gop)
    b = s.add_parser("bao-cao"); b.add_argument("ket_qua", nargs="+"); b.add_argument("--ra", required=True); b.set_defaults(f=lenh_bao_cao)
    a = p.parse_args(); a.f(a)

if __name__ == "__main__":
    main()
