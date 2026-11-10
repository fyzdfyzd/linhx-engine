#!/usr/bin/env python3
"""Cổng kiểm độc lập cho vòng lặp agent tự làm sản phẩm (LAB098).

Thợ (agy/claude) chỉ được đổi 2 trường của mỗi feature: "passes" và "bang_chung".
Cổng này chạy NGOÀI tay thợ:
  khoa <features.json>   chụp mốc (băm mọi thứ trừ passes/bang_chung) vào <file>.khoa
  kiem <features.json>   so với mốc, chạy lại lenh_kiem của từng feature thợ báo đạt,
                         hạ passes về false nếu trượt, ghi KIEM-<file>.json, exit 1 nếu có vi phạm
Biến môi trường CONG_KIEM_DOI=<file danh sách file đã sửa> (Linh 9/11, chấm nhanh): chỉ chạy lại
lenh_kiem của feature có vung khớp một file đã sửa (cộng CONG_KIEM_THEM="ID,ID"); feature đạt khác
vẫn kiểm băm + bằng chứng nhưng không chạy lại lệnh. Không đặt biến thì chạy toàn bộ như cũ.
"""
import fnmatch, hashlib, json, os, subprocess, sys, pathlib

DUOC_DOI = {"passes", "bang_chung"}

def doc(p):
    return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))

def phan_khoa(f):
    return {k: v for k, v in f.items() if k not in DUOC_DOI}

def bam(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

def khoa(path):
    # A (Linh 10/11): đề sai vùng/tiêu chí/phụ thuộc thì không khoá (canh/kiem_de.py, 0 token)
    if not os.environ.get("BO_KIEM_DE"):
        sys.path.insert(0, str(pathlib.Path(__file__).parent))
        import kiem_de
        loi, _ = kiem_de.kiem(path)
        if loi:
            print("\n".join(["kiem_de chặn khoá:"] + [" - " + x for x in loi]))
            return 1
    data = doc(path)
    moc = {"meta": bam({k: v for k, v in data.items() if k != "features"}),
           "features": {f["id"]: bam(phan_khoa(f)) for f in data["features"]}}
    pathlib.Path(str(path) + ".khoa").write_text(json.dumps(moc, indent=1), encoding="utf-8")
    print(f"đã khoá {len(moc['features'])} feature")

def kiem(path, timeout=600):
    path = pathlib.Path(path)
    data, moc = doc(path), doc(str(path) + ".khoa")
    goc = path.parent
    vi_pham, ket = [], []
    doi_tep = os.environ.get("CONG_KIEM_DOI")
    doi = None
    if doi_tep and pathlib.Path(doi_tep).exists():
        doi = [l.strip().replace("\\", "/") for l in pathlib.Path(doi_tep).read_text(encoding="utf-8-sig", errors="ignore").splitlines() if l.strip()]
    them = {x.strip() for x in os.environ.get("CONG_KIEM_THEM", "").split(",") if x.strip()}
    def lien_quan(f):
        if doi is None or f["id"] in them:
            return True
        return any(fnmatch.fnmatch(t, v) or t.startswith(v.rstrip("*").rstrip("/") + "/") for v in f.get("vung", []) for t in doi)
    if bam({k: v for k, v in data.items() if k != "features"}) != moc["meta"]:
        vi_pham.append("sửa phần đầu file (mục tiêu/phạm vi)")
    ids = {f["id"] for f in data["features"]}
    for fid in set(moc["features"]) - ids:
        vi_pham.append(f"{fid}: bị xoá")
    for fid in ids - set(moc["features"]):
        vi_pham.append(f"{fid}: thêm ngoài PRD")
    for f in data["features"]:
        fid = f["id"]
        if fid in moc["features"] and bam(phan_khoa(f)) != moc["features"][fid]:
            vi_pham.append(f"{fid}: sửa mô tả/tiêu chí/lệnh kiểm")
            f["passes"] = False
            continue
        if not f.get("passes"):
            ket.append({"id": fid, "trang_thai": "chua"})
            continue
        bc = f.get("bang_chung")
        if not bc or not (goc / bc).exists():
            vi_pham.append(f"{fid}: báo đạt nhưng thiếu file bằng chứng")
            f["passes"] = False
            ket.append({"id": fid, "trang_thai": "ha_ve_chua"})
            continue
        if not lien_quan(f):
            ket.append({"id": fid, "trang_thai": "dat_khong_chay_lai"})
            continue
        try:
            r = subprocess.run(f["lenh_kiem"], shell=True, cwd=goc, capture_output=True,
                               text=True, timeout=timeout)
            ok = r.returncode == 0
            if not ok:
                print(f"--- {fid} trượt: {f['lenh_kiem']}")
                print((r.stdout + r.stderr)[-1500:])
        except subprocess.TimeoutExpired:
            ok = False
        if not ok:
            vi_pham.append(f"{fid}: báo đạt nhưng lệnh kiểm trượt")
            f["passes"] = False
        ket.append({"id": fid, "trang_thai": "dat" if ok else "ha_ve_chua"})
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    dat = sum(1 for k in ket if k["trang_thai"] in ("dat", "dat_khong_chay_lai"))
    bc = {"dat": dat, "tong": len(data["features"]), "vi_pham": vi_pham, "chi_tiet": ket}
    (goc / f"KIEM-{path.stem}.json").write_text(json.dumps(bc, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"đạt thật {dat}/{len(data['features'])}, vi phạm {len(vi_pham)}")
    for v in vi_pham:
        print(" -", v)
    return 1 if vi_pham else 0

if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("khoa", "kiem"):
        sys.exit(__doc__)
    sys.exit(khoa(sys.argv[2]) or 0 if sys.argv[1] == "khoa" else kiem(sys.argv[2]))
