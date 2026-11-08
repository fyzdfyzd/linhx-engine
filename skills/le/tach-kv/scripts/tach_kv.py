#!/usr/bin/env python3
"""tach_kv.py: phân rã một key visual (KV) phẳng thành các lớp PNG trong suốt + JSON vị trí + PSD + SVG.

Hai lệnh:
  doc  ANH  THU_MUC      OCR tìm hộp chữ, vẽ ảnh đánh số để Claude soạn phan-ra.json
  tach PHAN_RA.json THU_MUC   tách lớp theo bản phân rã, xuất layers/, nen.png, kv.json, kv.psd, kv.svg, xem.html

Cách tách theo loại (trường "tach"):
  mau_don  chữ/logo một màu: unmix alpha theo màu chữ C và nền B đã xoá  a = <I-B, C-B>/|C-B|^2
  da_mau   logo nhiều màu: a theo khoảng cách tới nền, màu gỡ nền F = B + (I-B)/a
  cat      ảnh, QR: cắt cứng theo hộp hoặc đa giác
Nền: xoá mọi phần tử có "xoa_khoi_nen" (mặc định đúng, trừ loại anh) bằng inpaint 2 lượt.
"""
import json, os, sys
import cv2
import numpy as np
from PIL import Image


def ocr(path):
    from rapidocr_onnxruntime import RapidOCR
    r, _ = RapidOCR()(path)
    out = []
    for b, t, c in r or []:
        xs = [p[0] for p in b]; ys = [p[1] for p in b]
        out.append({"hop": [int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))], "ocr": t, "tin_cay": round(float(c), 2)})
    return sorted(out, key=lambda d: (d["hop"][1], d["hop"][0]))


def lenh_doc(anh, ra):
    os.makedirs(ra, exist_ok=True)
    I = cv2.imread(anh)
    dong = ocr(anh)
    json.dump(dong, open(os.path.join(ra, "ocr.json"), "w"), ensure_ascii=False, indent=1)
    v = I.copy()
    for i, d in enumerate(dong):
        x0, y0, x1, y1 = d["hop"]
        cv2.rectangle(v, (x0, y0), (x1, y1), (0, 0, 255), 3)
        cv2.putText(v, str(i), (x0, max(20, y0 - 6)), 0, 1.2, (0, 0, 255), 3)
    cv2.imwrite(os.path.join(ra, "ocr-xem.jpg"), v, [cv2.IMWRITE_JPEG_QUALITY, 80])
    print(f"{len(dong)} dòng chữ -> {ra}/ocr.json, {ra}/ocr-xem.jpg")


def mat_na_vung(p, H, W):
    m = np.zeros((H, W), np.uint8)
    if "da_giac" in p:
        cv2.fillPoly(m, [np.array(p["da_giac"], np.int32)], 255)
    else:
        x0, y0, x1, y1 = p["hop"]
        m[max(0, y0):min(H, y1), max(0, x0):min(W, x1)] = 255
    return m


def lap_day(I, m, ty_le=0.5, sg=4, vong=80):
    """Lấp vùng m kiểu bóc vỏ hành: mỗi vòng lấp một viền mỏng bằng trung bình Gauss của điểm đã biết.
    Hợp nền gradient; không kéo màu từ xa như tích chập cỡ lớn, không để vệt như inpaint Telea."""
    H, W = m.shape
    s = cv2.resize(I, None, fx=ty_le, fy=ty_le, interpolation=cv2.INTER_AREA).astype(np.float32)
    ms = cv2.resize(m, (s.shape[1], s.shape[0]), interpolation=cv2.INTER_NEAREST)
    w = (ms == 0).astype(np.float32)
    con = ms > 0
    for k in range(vong):
        if not con.any():
            break
        num = cv2.GaussianBlur(s * w[..., None], (0, 0), sg); den = cv2.GaussianBlur(w, (0, 0), sg)
        ok = con & (den > 0.2)
        s[ok] = num[ok] / den[ok, None]; w[ok] = 1; con &= ~ok
    if con.any():
        s[con] = s[~con].mean(0)
    s = np.where((ms > 0)[..., None], cv2.GaussianBlur(s, (0, 0), 2), s)
    up = cv2.resize(s, (W, H), interpolation=cv2.INTER_CUBIC)
    return np.where(m[..., None] > 0, np.clip(up, 0, 255), I).astype(np.uint8)


def mat_na_net(I, p, d0, vung):
    """Mặt nạ nét chữ/logo một màu bằng top-hat (chữ sáng) hoặc black-hat (chữ tối): không ăn vào nền gradient."""
    if p["tach"] != "mau_don":
        return vung
    x0, y0, x1, y1 = p["hop"]
    g = cv2.cvtColor(I[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY)
    if p.get("mau"):
        h = p["mau"].lstrip("#"); sang = sum(int(h[i:i + 2], 16) for i in (0, 2, 4)) / 3 > np.median(g)
    else:
        dd = d0[y0:y1, x0:x1]; sang = g[dd > np.percentile(dd, 90)].mean() > np.median(g)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (61, 61))
    gs = cv2.resize(g, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    t = cv2.morphologyEx(gs, cv2.MORPH_TOPHAT if sang else cv2.MORPH_BLACKHAT, k)
    t = cv2.resize(t, (x1 - x0, y1 - y0), interpolation=cv2.INTER_LINEAR)
    n = np.zeros_like(vung)
    n[y0:y1, x0:x1] = (t > 12).astype(np.uint8) * 255
    if p.get("mau"):  # chữ đè lên ảnh/khối sáng: bắt thêm điểm gần đúng màu chữ
        h = p["mau"].lstrip("#"); C = np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], np.float32)
        gan = np.linalg.norm(I[y0:y1, x0:x1].astype(np.float32) - C, axis=2) < 40
        n[y0:y1, x0:x1] |= gan.astype(np.uint8) * 255
    L = p.get("lan", 21)  # độ loang quanh nét (bóng, glow)
    return cv2.dilate(n, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (L, L))) & vung


def lenh_tach(phan_ra, ra):
    cfg = json.load(open(phan_ra))
    goc = cfg["anh_goc"]
    if not os.path.isabs(goc):
        goc = os.path.join(os.path.dirname(os.path.abspath(phan_ra)), goc)
    I = cv2.imread(goc)
    H, W = I.shape[:2]
    os.makedirs(os.path.join(ra, "layers"), exist_ok=True)
    pt = cfg["phan_tu"]
    for p in pt:
        p.setdefault("tach", "cat" if p["loai"] in ("anh", "qr", "khoi") else "mau_don")
        p.setdefault("xoa_khoi_nen", p["loai"] != "anh")
        pad = p.get("dem", 6)
        if "hop" in p:
            x0, y0, x1, y1 = p["hop"]
            p["hop"] = [max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad)]

    # Lượt 1: xoá thô cả hộp để có nền ước lượng B0
    m_hop = np.zeros((H, W), np.uint8)
    for p in pt:
        if p["xoa_khoi_nen"]:
            m_hop |= mat_na_vung(p, H, W)
    B0 = lap_day(I, m_hop)
    d0 = np.linalg.norm(I.astype(np.float32) - B0.astype(np.float32), axis=2)

    # Lượt 2: chỉ xoá nét (khác nền > ngưỡng), giữ chi tiết nền quanh nét
    m_net = np.zeros((H, W), np.uint8)
    for p in pt:
        if not p["xoa_khoi_nen"]:
            continue
        vung = mat_na_vung(p, H, W)
        if p["tach"] == "cat":
            m_net |= vung
        else:
            m_net |= mat_na_net(I, p, d0, vung)
    B = lap_day(I, m_net)
    cv2.imwrite(os.path.join(ra, "nen.png"), B)

    If, Bf = I.astype(np.float32), B.astype(np.float32)
    ket = {"anh_goc": os.path.basename(goc), "kich_thuoc": [W, H], "nen": "nen.png", "phan_tu": []}
    ghep = Bf.copy()
    for z, p in enumerate(sorted(pt, key=lambda q: q.get("z", 0))):
        vung = mat_na_vung(p, H, W).astype(np.float32) / 255
        if p["tach"] == "cat":
            a = cv2.GaussianBlur(vung, (3, 3), 0)
            F = Bf if not p["xoa_khoi_nen"] else If  # ảnh nằm dưới chữ: lấy từ nền đã xoá chữ
        elif p["tach"] == "da_mau":
            d = np.linalg.norm(If - Bf, axis=2)
            a = np.clip((d - 12) / (60 - 12), 0, 1) * vung
            F = np.clip(Bf + (If - Bf) / np.maximum(a, 0.05)[..., None], 0, 255)
        else:  # mau_don
            d = np.linalg.norm(If - Bf, axis=2)
            if p.get("mau"):
                h = p["mau"].lstrip("#"); C = np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], np.float32)
            else:
                sel = (d > np.percentile(d[vung > 0], 90)) & (vung > 0)
                C = np.median(If[sel], 0)
            CB = C[None, None] - Bf
            a = np.clip(((If - Bf) * CB).sum(2) / np.maximum((CB * CB).sum(2), 400), 0, 1) * vung
            a[a < 0.04] = 0
            F = np.broadcast_to(C, If.shape)
            p["mau"] = "#%02x%02x%02x" % (int(C[2]), int(C[1]), int(C[0]))
        ys, xs = np.where(a > 0.01)
        if len(xs) == 0:
            print("bỏ qua (trống):", p["id"]); continue
        x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
        rgba = np.dstack([F[y0:y1, x0:x1, ::-1], a[y0:y1, x0:x1, None] * 255]).astype(np.uint8)
        ten = f"layers/{z:02d}-{p['id']}.png"
        Image.fromarray(rgba, "RGBA").save(os.path.join(ra, ten), optimize=True)
        ghep = ghep * (1 - a[..., None]) + F * a[..., None]
        muc = {k: v for k, v in p.items() if k not in ("hop", "dem")}
        muc.update({"z": z + 1, "file": ten, "x": int(x0), "y": int(y0), "w": int(x1 - x0), "h": int(y1 - y0)})
        ket["phan_tu"].append(muc)

    sai = np.abs(ghep - If).mean()
    ket["kiem_tra_ghep_lai"] = {"sai_so_tb_0_255": round(float(sai), 2)}
    cv2.imwrite(os.path.join(ra, "ghep-lai.jpg"), ghep.astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 85])
    json.dump(ket, open(os.path.join(ra, "kv.json"), "w"), ensure_ascii=False, indent=1)
    xuat_psd(ket, ra); xuat_svg(ket, ra); xuat_html(ket, ra)
    print(f"{len(ket['phan_tu'])} lớp + nền -> {ra}; sai số ghép lại trung bình {sai:.2f}/255")


def xuat_psd(ket, ra):
    try:
        from psd_tools import PSDImage
        from psd_tools.api.layers import PixelLayer
    except ImportError:
        print("thiếu psd-tools, bỏ PSD"); return
    W, H = ket["kich_thuoc"]
    psd = PSDImage.new("RGB", (W, H))
    nen = Image.open(os.path.join(ra, ket["nen"])).convert("RGBA")
    psd.append(PixelLayer.frompil(nen, psd, "nen", 0, 0))
    for p in ket["phan_tu"]:
        im = Image.open(os.path.join(ra, p["file"])).convert("RGBA")
        psd.append(PixelLayer.frompil(im, psd, p["id"], p["y"], p["x"]))
    psd.save(os.path.join(ra, "kv.psd"))


def xuat_svg(ket, ra):
    W, H = ket["kich_thuoc"]
    d = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
         f'<image id="nen" href="{ket["nen"]}" x="0" y="0" width="{W}" height="{H}"/>']
    for p in ket["phan_tu"]:
        t = f'<title>{p.get("noi_dung", "")}</title>' if p.get("noi_dung") else ""
        d.append(f'<g id="{p["id"]}" data-loai="{p["loai"]}">{t}<image href="{p["file"]}" x="{p["x"]}" y="{p["y"]}" width="{p["w"]}" height="{p["h"]}"/></g>')
    d.append("</svg>")
    open(os.path.join(ra, "kv.svg"), "w").write("\n".join(d))


def xuat_html(ket, ra):
    W, H = ket["kich_thuoc"]
    lop = "".join(f'<img data-id="{p["id"]}" src="{p["file"]}" style="left:{p["x"]/W*100:.3f}%;top:{p["y"]/H*100:.3f}%;width:{p["w"]/W*100:.3f}%">' for p in ket["phan_tu"])
    chon = "".join(f'<label><input type="checkbox" checked data-id="{p["id"]}"> {p["id"]} <i>{p["loai"]}</i></label>' for p in ket["phan_tu"])
    html = f"""<!doctype html><meta charset="utf-8"><title>Phân rã KV</title>
<style>body{{font:14px system-ui;margin:16px;background:#ddd}}#kv{{position:relative;max-width:1200px;background:#fff url(data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2220%22 height=%2220%22%3E%3Crect width=%2210%22 height=%2210%22 fill=%22%23ccc%22/%3E%3Crect x=%2210%22 y=%2210%22 width=%2210%22 height=%2210%22 fill=%22%23ccc%22/%3E%3C/svg%3E)}}
#kv img{{position:absolute}}#nen{{position:static!important;width:100%;display:block}}label{{display:inline-block;margin:4px 10px 4px 0}}i{{color:#666}}</style>
<p><label><input type="checkbox" checked id="bnen"> nền</label>{chon}</p><div id="kv"><img id="nen" src="{ket['nen']}">{lop}</div>
<script>document.querySelectorAll('input[data-id]').forEach(c=>c.onchange=()=>document.querySelector('#kv img[data-id="'+c.dataset.id+'"]').style.display=c.checked?'':'none');
bnen.onchange=()=>nen.style.visibility=bnen.checked?'':'hidden'</script>"""
    open(os.path.join(ra, "xem.html"), "w").write(html)


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] not in ("doc", "tach"):
        print(__doc__); sys.exit(1)
    (lenh_doc if sys.argv[1] == "doc" else lenh_tach)(sys.argv[2], sys.argv[3])
