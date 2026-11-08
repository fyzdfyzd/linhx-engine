"""Giả lập ROI đa phễu cho một biz: 1 đồng marketing thu về bao nhiêu.

Chạy:  python roi.py ../bizs/spa-hanoi.json  [--lan 2000] [--ra ../../../output]
Ra:    <ra>/<ten-file>-roi.md  và  <ra>/<ten-file>-roi.xlsx

Mô hình (đơn vị triệu đồng, theo tháng):
- Mỗi phễu: lượt đầu phễu × tỉ lệ từng bước = đơn; phễu chín dần tuyến tính trong `thang_chin`.
- Phễu trả tiền bão hoà: lượt = dau_vao × NS_mặc_định × (NS/NS_mặc_định)^bao_hoa.
- Phễu tích luỹ (newsletter, community): danh sách lớn dần, rơi bỏ mỗi tháng, đơn = danh sách × tỉ lệ mua.
- Đơn × `tang_thuc` (chỉ tính đơn thật sự do phễu tạo ra), trễ `tre_ban_thang`.
- Khách mới tháng m mua lại trong phần còn lại của năm: aov × (1 + (lần_mua − 1) × (H − m) / H).
- Chi phí chạy đủ từ tháng 1 kể cả khi phễu chưa chín: đó là lý do SEO, community lỗ năm đầu.
"""
import argparse
import json
import pathlib

import numpy as np

GOC = pathlib.Path(__file__).resolve().parent.parent


def tam_giac(rng, ba, n):
    lo, mo, hi = ba
    if lo == hi:
        return np.full(n, float(lo))
    return rng.triangular(lo, mo, hi, n)


def tron_pheu(nen, rieng):
    p = dict(nen)
    p.update({k: v for k, v in rieng.items() if not k.startswith("_")})
    return p


def gia_lap_pheu(p, biz, n, seed, ngan_sach=None):
    rng = np.random.default_rng(seed)
    H = biz["so_thang"]
    thang = np.arange(H)
    chin = np.minimum(1.0, (thang + 1) / p["thang_chin"])  # [H]
    vao = tam_giac(rng, p["dau_vao"], n)[:, None]  # [n,1]
    if p["kieu"] == "tra_tien":
        ns_goc = p["_ns_goc"]
        ns = p["ngan_sach"] if ngan_sach is None else ngan_sach
        vao = vao * ns_goc * (ns / ns_goc) ** p["bao_hoa"]
    else:
        ns = 0.0
    ti_le = np.ones((n, 1))
    for i, b in enumerate(p["buoc"]):
        r = tam_giac(rng, b[1:], n)[:, None]
        if i == len(p["buoc"]) - 1:
            r = r * p.get("he_so_buoc_cuoi", 1.0)
        ti_le = ti_le * r
    dong = vao * chin[None, :] * ti_le  # [n,H]: đơn (hoặc người vào danh sách)
    if p["kieu"] == "tich_luy":
        mua = tam_giac(rng, p["mua_moi_thang"], n)[:, None]
        ds = np.zeros((n, H))
        cur = np.zeros(n)
        for m in range(H):
            cur = cur * (1 - p["roi_bo_thang"]) + dong[:, m]
            ds[:, m] = cur
        don = ds * mua
    else:
        don = dong
    don = don * tam_giac(rng, p["tang_thuc"], n)[:, None]
    tre = biz["tre_ban_thang"]
    if tre:
        don = np.concatenate([np.zeros((n, tre)), don[:, : H - tre]], axis=1)
    gia_tri = biz["aov"] * (1 + (biz["so_lan_mua_12t"] - 1) * (H - thang) / H)
    doanh_thu = don * gia_tri[None, :]
    lai_gop = doanh_thu * (biz["bien_gop"] - p.get("hoa_hong", 0.0))
    chi = np.full(H, p["co_dinh"] + ns, dtype=float)
    chi[0] += p["setup"]
    return {"don": don, "doanh_thu": doanh_thu, "lai_gop": lai_gop, "chi": np.broadcast_to(chi, (n, H))}


def phan_vi(x):
    return [float(np.percentile(x, q)) for q in (10, 50, 90)]


def hoan_von(lai, chi):
    """Tháng đầu tiên lãi gộp cộng dồn (P50) >= chi phí cộng dồn; None nếu chưa hoàn trong năm."""
    lg = np.percentile(np.cumsum(lai, axis=1), 50, axis=0)
    c = np.cumsum(chi[0])
    ok = np.nonzero(lg >= c)[0]
    return int(ok[0]) + 1 if len(ok) else None


def chay(biz_path, lan=2000, seed=7):
    nen = json.loads((GOC / "data" / "pheu.json").read_text(encoding="utf-8"))["pheu"]
    biz = json.loads(pathlib.Path(biz_path).read_text(encoding="utf-8"))
    H = biz["so_thang"]
    # Hệ số chung của biz (offer, giá, độ khớp thị trường): rút một lần cho mỗi lần giả lập và dùng cho MỌI phễu,
    # vì offer dở thì phễu nào cũng dở. Không có hệ số này giả lập sẽ quá tự tin.
    g = tam_giac(np.random.default_rng(seed - 1), biz.get("he_so_biz", [0.4, 1.0, 1.4]), lan)[:, None]
    sims = {}
    for i, (pid, rieng) in enumerate(biz["pheu"].items()):
        if not rieng.get("bat", False):
            continue
        p = tron_pheu(nen[pid], rieng)
        p["_ns_goc"] = nen[pid].get("ngan_sach", 1)
        s = gia_lap_pheu(p, biz, lan, seed + i)
        s2 = gia_lap_pheu(p, biz, lan, seed + i, ngan_sach=p["ngan_sach"] * 1.1) if p["kieu"] == "tra_tien" else None
        sims[pid] = (p, s, s2)
    # Trần năng lực phục vụ: khách mới vượt trần là tiền marketing đổ đi (giường spa, giờ giảng viên).
    def ap_tran(ss):
        tong_don = sum(x["don"] for x in ss) * g
        tran = biz.get("tran_khach_moi_thang")
        k = g * (np.minimum(1.0, tran / np.maximum(tong_don, 1e-9)) if tran else 1.0)
        return [{**x, "don": x["don"] * k, "doanh_thu": x["doanh_thu"] * k, "lai_gop": x["lai_gop"] * k} for x in ss]
    goc = dict(zip(sims, ap_tran([v[1] for v in sims.values()])))
    kq, tong = {}, None
    for pid, (p, _, s2) in sims.items():
        s = goc[pid]
        chi = s["chi"].sum(1)
        dt, lg, don = s["doanh_thu"].sum(1), s["lai_gop"].sum(1), s["don"].sum(1)
        r = {
            "ten": p["ten"], "chi": float(chi[0]),
            "don": phan_vi(don), "doanh_thu": phan_vi(dt), "lai_gop": phan_vi(lg),
            "dt_moi_dong": phan_vi(dt / chi), "lg_moi_dong": phan_vi(lg / chi),
            "cac": phan_vi(chi / np.maximum(don, 1e-9)),
            "hoan_von": hoan_von(s["lai_gop"], s["chi"]),
            "don_thang_chin": float(np.percentile(s["don"][:, -1], 50)),
        }
        if s2 is not None:  # ROI biên: thêm 10% ngân sách phễu này (các phễu khác giữ nguyên, có tính trần)
            moi = ap_tran([s2 if q == pid else sims[q][1] for q in sims])
            d_lg = sum(x["lai_gop"].sum(1) for x in moi) - sum(x["lai_gop"].sum(1) for x in goc.values())
            d_chi = s2["chi"].sum(1) - chi
            r["mroi"] = float(np.percentile(d_lg / d_chi, 50))
        kq[pid] = r
        tong = s if tong is None else {k: tong[k] + s[k] for k in s}
    chung = sum(v for _, v in biz.get("chi_phi_planning", []))
    van_hanh = sum(v for _, v in biz.get("van_hanh_chung_thang", [])) * H
    chi_tong = tong["chi"].sum(1) + chung + van_hanh
    dt, lg = tong["doanh_thu"].sum(1), tong["lai_gop"].sum(1)
    chi_thang = tong["chi"][0].copy() + van_hanh / H
    chi_thang[0] += chung
    tong_kq = {
        "chi": float(chi_tong[0]), "planning": chung, "van_hanh": van_hanh,
        "doanh_thu": phan_vi(dt), "lai_gop": phan_vi(lg),
        "dt_moi_dong": phan_vi(dt / chi_tong), "lg_moi_dong": phan_vi(lg / chi_tong),
        "loi_nhuan_sau_mkt": phan_vi(lg - chi_tong),
        "xac_suat_lo": float((lg < chi_tong).mean()),
        "hoan_von": hoan_von(tong["lai_gop"], np.broadcast_to(chi_thang, tong["chi"].shape)),
        "thang": {
            "chi": chi_thang.tolist(),
            "dt_p50": np.percentile(tong["doanh_thu"], 50, axis=0).tolist(),
            "lg_p50": np.percentile(tong["lai_gop"], 50, axis=0).tolist(),
        },
    }
    return biz, kq, tong_kq


def f(x, d=1):
    return f"{x:,.{d}f}".replace(",", " ")


def ba(x, d=1):
    return f"{f(x[0], d)} · **{f(x[1], d)}** · {f(x[2], d)}"


def viet_md(biz, kq, t):
    H = biz["so_thang"]
    L = [f"# ROI đa phễu: {biz['ten']}", "",
         f"Loại: {biz['loai']}. Giá trị đơn {biz['aov']} tr, biên gộp {int(biz['bien_gop']*100)}%, "
         f"mua {biz['so_lan_mua_12t']} lần/năm, trễ bán {biz['tre_ban_thang']} tháng. Giả lập {H} tháng, "
         "số in là P10 · **P50** · P90 (xấu · hay gặp · tốt). Đơn vị triệu đồng. Mọi đầu vào là giả định, chưa có số thật.", "",
         "## Kết luận cho owner", "",
         f"- Tổng chi marketing {H} tháng: **{f(t['chi'],0)} tr** (gồm planning {f(t['planning'],0)} tr, vận hành chung {f(t['van_hanh'],0)} tr).",
         f"- **1 đồng bỏ vào thu về {ba(t['dt_moi_dong'],2)} đồng doanh thu**, tức {ba(t['lg_moi_dong'],2)} đồng lãi gộp.",
         f"- Lãi sau khi trừ marketing: {ba(t['loi_nhuan_sau_mkt'],0)} tr. Xác suất lỗ cả năm: **{int(round(t['xac_suat_lo']*100))}%**.",
         f"- Hoàn vốn marketing (P50): {'tháng ' + str(t['hoan_von']) if t['hoan_von'] else 'chưa hoàn trong năm'}.", "",
         "## Theo từng phễu", "",
         "| Phễu | Chi năm | Đơn | Doanh thu/1đ | Lãi gộp/1đ | CAC (tr/khách) | Hoàn vốn | ROI biên +10% NS |",
         "|---|---:|---|---|---|---|---|---:|"]
    for pid, r in sorted(kq.items(), key=lambda kv: -kv[1]["lg_moi_dong"][1]):
        hv = f"tháng {r['hoan_von']}" if r["hoan_von"] else "chưa"
        mr = f(r["mroi"], 2) if "mroi" in r else ""
        L.append(f"| {r['ten']} | {f(r['chi'],0)} | {ba(r['don'],0)} | {ba(r['dt_moi_dong'],2)} | {ba(r['lg_moi_dong'],2)} | {ba(r['cac'],2)} | {hv} | {mr} |")
    L += ["", "Đọc bảng: lãi gộp/1đ dưới 1 là phễu chưa tự nuôi được mình trong năm (SEO, community thường thế ở năm đầu, "
          "giá trị nằm ở năm 2). ROI biên dưới 1 nghĩa là đổ thêm tiền vào phễu trả tiền đó là lỗ trên phần tiền thêm, dù ROI trung bình còn đẹp.", "",
          "## Dòng tiền theo tháng (P50)", "", "| Tháng | Chi | Doanh thu | Lãi gộp | Lãi gộp cộng dồn − chi cộng dồn |", "|---:|---:|---:|---:|---:|"]
    cd = 0.0
    for m in range(H):
        c, d, g = t["thang"]["chi"][m], t["thang"]["dt_p50"][m], t["thang"]["lg_p50"][m]
        cd += g - c
        L.append(f"| {m+1} | {f(c,0)} | {f(d,0)} | {f(g,0)} | {f(cd,0)} |")
    L += ["", "## Chi phí planning (một lần)", "", "| Hạng mục | tr |", "|---|---:|"]
    L += [f"| {a} | {b} |" for a, b in biz.get("chi_phi_planning", [])]
    L += ["", "Vận hành chung mỗi tháng: " + "; ".join(f"{a} {b} tr" for a, b in biz.get("van_hanh_chung_thang", [])) + "."]
    tat = [f"{pid} ({v.get('_ly_do', 'tắt')})" for pid, v in biz["pheu"].items() if not v.get("bat")]
    if tat:
        L += ["", "Phễu tắt: " + "; ".join(tat) + "."]
    return "\n".join(L) + "\n"


def viet_xlsx(biz, kq, t, path):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill

    wb = Workbook()
    ws = wb.active
    ws.title = "May tinh nhanh"
    vang = PatternFill("solid", fgColor="FFF2CC")
    dam = Font(bold=True)
    ws["A1"] = f"Máy tính nhanh ROI: {biz['ten']} (triệu đồng/tháng). Ô vàng là số owner sửa; sau 4-8 tuần thay 'Đơn/tháng' bằng số đếm thật trong sổ khách."
    ws["A1"].font = dam
    for c, (k, v) in enumerate([("Giá trị đơn (tr)", biz["aov"]), ("Biên lãi gộp", biz["bien_gop"]), ("Số lần mua/năm", biz["so_lan_mua_12t"])]):
        ws.cell(row=3 + c, column=1, value=k)
        ws.cell(row=3 + c, column=2, value=v).fill = vang
    hd = ["Phễu", "Chi/tháng khi chạy (tr)", "Đơn/tháng khi chín (P50)", "Hoa hồng", "Doanh thu 12 tháng từ khách mới của tháng", "Lãi gộp tương ứng", "Doanh thu / 1đ", "Lãi gộp / 1đ", "CAC (tr/khách)"]
    for c, h in enumerate(hd, 1):
        ws.cell(row=7, column=c, value=h).font = dam
    nen = json.loads((GOC / "data" / "pheu.json").read_text(encoding="utf-8"))["pheu"]
    r = 8
    for pid, v in kq.items():
        p = tron_pheu(nen[pid], biz["pheu"][pid])
        ws.cell(row=r, column=1, value=v["ten"])
        ws.cell(row=r, column=2, value=round(p["co_dinh"] + p.get("ngan_sach", 0), 2)).fill = vang
        ws.cell(row=r, column=3, value=round(v["don_thang_chin"], 2)).fill = vang
        ws.cell(row=r, column=4, value=p.get("hoa_hong", 0)).fill = vang
        ws.cell(row=r, column=5, value=f"=C{r}*$B$3*$B$5")
        ws.cell(row=r, column=6, value=f"=E{r}*($B$4-D{r})")
        ws.cell(row=r, column=7, value=f"=IFERROR(E{r}/B{r},0)")
        ws.cell(row=r, column=8, value=f"=IFERROR(F{r}/B{r},0)")
        ws.cell(row=r, column=9, value=f"=IFERROR(B{r}/C{r},0)")
        r += 1
    vh = sum(v for _, v in biz.get("van_hanh_chung_thang", []))
    ws.cell(row=r, column=1, value="Vận hành chung (token, công cụ, người duyệt)")
    ws.cell(row=r, column=2, value=vh).fill = vang
    r += 1
    ws.cell(row=r, column=1, value="TỔNG").font = dam
    for col in "BCEF":
        ws[f"{col}{r}"] = f"=SUM({col}8:{col}{r-1})"
    ws[f"G{r}"] = f"=IFERROR(E{r}/B{r},0)"
    ws[f"H{r}"] = f"=IFERROR(F{r}/B{r},0)"
    ws.cell(row=r + 2, column=1, value="Đây là tháng đã chín (ổn định), chưa tính tháng đầu lỗ và chi phí planning một lần. Bức tranh 12 tháng ở sheet 'Gia lap 12 thang'.")
    ws.column_dimensions["A"].width = 52
    for col in "BCDEFGHI":
        ws.column_dimensions[col].width = 16

    w2 = wb.create_sheet("Gia lap 12 thang")
    w2.append(["Phễu", "Chi năm", "Lãi gộp/1đ P10", "P50", "P90", "Doanh thu/1đ P50", "Đơn P50", "CAC P50", "Hoàn vốn (tháng)", "ROI biên +10% NS"])
    for v in kq.values():
        w2.append([v["ten"], round(v["chi"], 1), *[round(x, 2) for x in v["lg_moi_dong"]], round(v["dt_moi_dong"][1], 2),
                   round(v["don"][1], 1), round(v["cac"][1], 2), v["hoan_von"] or "chưa", round(v["mroi"], 2) if "mroi" in v else ""])
    w2.append([])
    w2.append(["TỔNG (gồm planning + vận hành)", round(t["chi"], 1), *[round(x, 2) for x in t["lg_moi_dong"]], round(t["dt_moi_dong"][1], 2), "", "", t["hoan_von"] or "chưa", ""])
    w2.append(["Xác suất lỗ cả năm", round(t["xac_suat_lo"], 3)])
    w2.column_dimensions["A"].width = 52
    w3 = wb.create_sheet("Planning")
    w3.append(["Hạng mục planning (một lần)", "tr"])
    for a, b in biz.get("chi_phi_planning", []):
        w3.append([a, b])
    w3.append(["Tổng", f"=SUM(B2:B{len(biz.get('chi_phi_planning', []))+1})"])
    w3.column_dimensions["A"].width = 80
    wb.save(path)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("biz")
    ap.add_argument("--lan", type=int, default=2000)
    ap.add_argument("--ra", default=str(GOC / "out"))
    a = ap.parse_args()
    biz, kq, t = chay(a.biz, a.lan)
    ra = pathlib.Path(a.ra)
    ra.mkdir(parents=True, exist_ok=True)
    ten = pathlib.Path(a.biz).stem
    (ra / f"{ten}-roi.md").write_text(viet_md(biz, kq, t), encoding="utf-8")
    viet_xlsx(biz, kq, t, ra / f"{ten}-roi.xlsx")
    print(f"{ten}: 1đ → {t['dt_moi_dong'][1]:.2f}đ doanh thu, {t['lg_moi_dong'][1]:.2f}đ lãi gộp (P50); lỗ {t['xac_suat_lo']:.0%}; hoàn vốn {t['hoan_von']}")
