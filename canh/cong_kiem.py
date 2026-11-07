#!/usr/bin/env python3
"""Cổng kiểm độc lập cho vòng lặp agent tự làm sản phẩm (LAB098).

Thợ (agy/claude) chỉ được đổi 2 trường của mỗi feature: "passes" và "bang_chung".
Cổng này chạy NGOÀI tay thợ:
  khoa <features.json>   chụp mốc (băm mọi thứ trừ passes/bang_chung) vào <file>.khoa
  kiem <features.json>   so với mốc, chạy lại lenh_kiem của từng feature thợ báo đạt,
                         hạ passes về false nếu trượt, ghi KIEM-<file>.json, exit 1 nếu có vi phạm
"""
import hashlib, json, subprocess, sys, pathlib

DUOC_DOI = {"passes", "bang_chung"}

def doc(p):
    return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))

def phan_khoa(f):
    return {k: v for k, v in f.items() if k not in DUOC_DOI}

def bam(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

def khoa(path):
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
    dat = sum(1 for k in ket if k["trang_thai"] == "dat")
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
