#!/usr/bin/env python3
"""ke_hoach.py · agy tự lập kế hoạch và tự chạy theo phiếu (LAB106).

  python ke_hoach.py moi <thu-muc> --loai chien-luoc --ten "<tên dự án>"
  python ke_hoach.py kiem <thu-muc>            kiểm kế hoạch hợp lệ
  python ke_hoach.py tiep <thu-muc>            in phiếu kế tiếp sẵn sàng, đánh dấu "dang"
  python ke_hoach.py xong <thu-muc> <ma> --dat | --truot "lý do"
  python ke_hoach.py duyet <thu-muc> <cong> --nguoi Linh|Claude   mở cổng D2/D4
  python ke_hoach.py bao-cao <thu-muc>         viết BAO-CAO-QUAN-TRI.md (≤1 trang cho Claude/Linh)
Chỉ dùng thư viện chuẩn. Kế hoạch nằm ở <thu-muc>/ke-hoach.json.
"""
import argparse, datetime as dt, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRAN_PHUT, TRAN_VONG = 40, 3
TRANG_THAI = ("cho", "dang", "xong", "truot", "dung")
DO_DUOC = re.compile(r"\d|kiem\.py|có file|có mục|DAT")


def nap(d):
    return json.loads((Path(d) / "ke-hoach.json").read_text(encoding="utf-8"))


def luu(d, kh):
    kh["cap_nhat"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    (Path(d) / "ke-hoach.json").write_text(json.dumps(kh, ensure_ascii=False, indent=2), encoding="utf-8")


def moi(a):
    mau = json.loads((HERE / "mau-ke-hoach.json").read_text(encoding="utf-8"))
    if a.loai not in mau:
        sys.exit(f"không có mẫu loại '{a.loai}', có: {', '.join(mau)}")
    d = Path(a.thu_muc)
    d.mkdir(parents=True, exist_ok=True)
    if (d / "ke-hoach.json").exists():
        sys.exit("đã có ke-hoach.json, không ghi đè")
    phieu = []
    for p in mau[a.loai]:
        p = dict(p)
        p.setdefault("tho", "agy")
        p.setdefault("tran_phut", TRAN_PHUT)
        p.setdefault("phu_thuoc", [])
        p.update(trang_thai="cho", vong=0, nhat_ky=[])
        phieu.append(p)
    kh = {"du_an": a.ten, "loai": a.loai, "che_do": a.che_do, "cong_da_mo": [], "phieu": phieu}
    luu(d, kh)
    print(f"đã tạo {d/'ke-hoach.json'} với {len(phieu)} phiếu")


def loi_ke_hoach(kh):
    loi, ma = [], {p["ma"] for p in kh["phieu"]}
    for p in kh["phieu"]:
        for k in ("ma", "viec", "tho", "nguoi_cham", "dau_ra", "tieu_chi", "lenh_kiem"):
            if not p.get(k):
                loi.append(f"{p.get('ma','?')}: thiếu {k}")
        if p.get("tran_phut", 0) > TRAN_PHUT:
            loi.append(f"{p['ma']}: {p['tran_phut']} phút > {TRAN_PHUT}, chia nhỏ")
        if p.get("tho") == p.get("nguoi_cham"):
            loi.append(f"{p['ma']}: người chấm trùng thợ")
        if p.get("tho", "").lower().startswith("claude"):
            loi.append(f"{p['ma']}: giao Claude làm thợ (bộ này chạy trên agy)")
        for t in p.get("tieu_chi", []):
            if not DO_DUOC.search(t):
                loi.append(f"{p['ma']}: tiêu chí không đo được: '{t}'")
        for q in p.get("phu_thuoc", []):
            if q not in ma:
                loi.append(f"{p['ma']}: phụ thuộc {q} không có")
        if p.get("trang_thai") not in TRANG_THAI:
            loi.append(f"{p['ma']}: trạng thái lạ {p.get('trang_thai')}")
    # vòng lặp phụ thuộc
    ke = {p["ma"]: p.get("phu_thuoc", []) for p in kh["phieu"]}
    tham, dang = set(), set()

    def dfs(m):
        if m in dang:
            return True
        if m in tham:
            return False
        dang.add(m)
        vong = any(dfs(q) for q in ke.get(m, []) if q in ke)
        dang.discard(m); tham.add(m)
        return vong
    if any(dfs(m) for m in ke):
        loi.append("phụ thuộc có vòng lặp")
    return loi


def kiem(a):
    loi = loi_ke_hoach(nap(a.thu_muc))
    print("DAT" if not loi else "CHUA_DAT")
    for l in loi:
        print(" -", l)
    return 0 if not loi else 1


def san_sang(kh):
    xong = {p["ma"] for p in kh["phieu"] if p["trang_thai"] == "xong"}
    for p in kh["phieu"]:
        if p["trang_thai"] != "cho" or not set(p.get("phu_thuoc") or []) <= xong:
            continue
        cong = p.get("can_cong")
        if cong and cong not in kh["cong_da_mo"]:
            continue
        return p
    return None


def tiep(a):
    kh = nap(a.thu_muc)
    if loi_ke_hoach(kh):
        sys.exit("kế hoạch chưa hợp lệ, chạy `kiem` trước")
    o = getattr(a, "o", 1) or 1
    dang = [p for p in kh["phieu"] if p["trang_thai"] == "dang"]
    cua_o = [p for p in dang if p.get("o", 1) == o]
    if cua_o:
        print(f"ĐANG CHẠY {cua_o[0]['ma']} (ô {o}): làm xong rồi gọi `xong`")
        return 2
    if len(dang) >= int(kh.get("song_song", 1)) or o > int(kh.get("song_song", 1)):
        print(f"ĐANG CHẠY {', '.join(p['ma'] for p in dang)}: đủ {kh.get('song_song', 1)} ô song song")
        return 2
    p = san_sang(kh)
    if not p:
        cho_cong = sorted({q["can_cong"] for q in kh["phieu"] if q["trang_thai"] == "cho" and q.get("can_cong") and q["can_cong"] not in kh["cong_da_mo"]})
        if cho_cong:
            print(f"CHỜ DUYỆT cổng {', '.join(cho_cong)}. Chạy `bao-cao` rồi báo người duyệt ({nguoi_duyet(kh)}).")
            return 3
        if all(q["trang_thai"] == "xong" for q in kh["phieu"]):
            print("XONG HẾT. Chạy `bao-cao`.")
            return 0
        print("KẸT: còn phiếu dừng hoặc trượt quá 3 vòng. Chạy `bao-cao`.")
        return 4
    p["trang_thai"] = "dang"
    p["o"] = o
    p["nhat_ky"].append(f"{dt.datetime.now():%m-%d %H:%M} bắt đầu vòng {p['vong']+1} (ô {o})")
    luu(a.thu_muc, kh)
    print(f"PHIẾU {p['ma']} · trần {p['tran_phut']} phút · vòng {p['vong']+1}/{TRAN_VONG}")
    print(f"Việc: {p['viec']}")
    if p.get("doc"):
        print("Đọc trước: " + ", ".join(p["doc"]))
    print("Đầu ra: " + ", ".join(p["dau_ra"]))
    print("Tiêu chí:\n  - " + "\n  - ".join(p["tieu_chi"]))
    print(f"Lệnh kiểm: {p['lenh_kiem']}")
    print(f"Người chấm: {p['nguoi_cham']} (phiên MỚI, không phải phiên làm)")
    if p.get("chi_va"):
        print("CHỈ VÁ: không ghi lại cả file, chỉ sửa mục được nêu.")
    return 0


def xong(a):
    kh = nap(a.thu_muc)
    p = next((q for q in kh["phieu"] if q["ma"] == a.ma), None)
    if not p:
        sys.exit(f"không có phiếu {a.ma}")
    gio = f"{dt.datetime.now():%m-%d %H:%M}"
    if a.dat:
        p["trang_thai"] = "xong"
        p["nhat_ky"].append(f"{gio} DAT")
    else:
        p["vong"] += 1
        p["nhat_ky"].append(f"{gio} TRUOT: {a.truot}")
        p["trang_thai"] = "dung" if p["vong"] >= TRAN_VONG else "cho"
    luu(a.thu_muc, kh)
    print(f"{a.ma} → {p['trang_thai']}")


def nguoi_duyet(kh):
    return "Claude rồi Linh" if kh.get("che_do") == "claude-quan-tri" else "Linh"


def duyet(a):
    kh = nap(a.thu_muc)
    if kh.get("che_do") != "claude-quan-tri" and a.nguoi.lower().startswith("claude"):
        sys.exit("chế độ agy-doc-lap: cổng do Linh duyệt")
    if a.cong not in kh["cong_da_mo"]:
        kh["cong_da_mo"].append(a.cong)
    kh.setdefault("lich_su_cong", []).append(f"{dt.datetime.now():%m-%d %H:%M} {a.cong} mở bởi {a.nguoi}")
    luu(a.thu_muc, kh)
    print(f"đã mở cổng {a.cong}")


def bao_cao(a):
    kh = nap(a.thu_muc)
    dem = {t: sum(p["trang_thai"] == t for p in kh["phieu"]) for t in TRANG_THAI}
    dong = [f"# Báo cáo quản trị · {kh['du_an']}", "",
            f"Cập nhật {dt.datetime.now():%d/%m %H:%M} · loại {kh['loai']} · chế độ {kh['che_do']}", "",
            f"Phiếu: {dem['xong']}/{len(kh['phieu'])} xong · {dem['dang']} đang · {dem['cho']} chờ · {dem['dung']} dừng", ""]
    can = []
    for p in kh["phieu"]:
        if p["trang_thai"] == "dung":
            can.append(f"- {p['ma']} dừng sau {p['vong']} vòng: {p['nhat_ky'][-1]}")
    xong_ma = {p["ma"] for p in kh["phieu"] if p["trang_thai"] == "xong"}
    cho_cong = sorted({p["can_cong"] for p in kh["phieu"] if p.get("can_cong") and p["can_cong"] not in kh["cong_da_mo"]
                       and p["trang_thai"] == "cho" and set(p["phu_thuoc"]) <= xong_ma})
    for c in cho_cong:
        can.append(f"- Cổng {c} chờ {nguoi_duyet(kh)} duyệt")
    dong += ["## Cần quyết", *(can or ["- Không"]), "", "## Vừa xong"]
    for p in [p for p in kh["phieu"] if p["trang_thai"] == "xong"][-5:]:
        dong.append(f"- {p['ma']} {p['viec'][:70]} → {', '.join(p['dau_ra'])}")
    dong += ["", "## Tiếp theo"]
    nx = san_sang(kh)
    dong.append(f"- {nx['ma']} {nx['viec'][:80]}" if nx else "- (chờ cổng hoặc đã xong)")
    (Path(a.thu_muc) / "BAO-CAO-QUAN-TRI.md").write_text("\n".join(dong) + "\n", encoding="utf-8")
    print("\n".join(dong))


def main(argv=None):
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="lenh", required=True)
    s = sp.add_parser("moi"); s.add_argument("thu_muc"); s.add_argument("--loai", required=True); s.add_argument("--ten", required=True)
    s.add_argument("--che-do", dest="che_do", choices=["claude-quan-tri", "agy-doc-lap"], default="claude-quan-tri"); s.set_defaults(f=moi)
    for n, f in (("kiem", kiem), ("tiep", tiep), ("bao-cao", bao_cao)):
        s = sp.add_parser(n); s.add_argument("thu_muc"); s.set_defaults(f=f)
    s = sp.add_parser("xong"); s.add_argument("thu_muc"); s.add_argument("ma")
    g = s.add_mutually_exclusive_group(required=True); g.add_argument("--dat", action="store_true"); g.add_argument("--truot")
    s.set_defaults(f=xong)
    s = sp.add_parser("duyet"); s.add_argument("thu_muc"); s.add_argument("cong"); s.add_argument("--nguoi", required=True); s.set_defaults(f=duyet)
    a = ap.parse_args(argv)
    return a.f(a) or 0


if __name__ == "__main__":
    sys.exit(main())
