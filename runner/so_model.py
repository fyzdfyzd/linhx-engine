"""So model agy theo kết quả thật trong hang-doi/xong/*/KET-QUA.md.

Dùng: python runner/so_model.py <thư mục hang-doi/xong> [--tien-to neon-]
In mỗi model: số phiếu, số xong, trung vị phút, trung vị token vào/ra.
Dùng để đo lại bảng runner/model-theo-loai.json sau mỗi đợt phiếu thật.
"""
import argparse
import re
import statistics
from collections import defaultdict
from pathlib import Path

_MAU = {
    "model": re.compile(r"^model: (\S+)", re.M),
    "trang_thai": re.compile(r"^trang_thai: (\w+)", re.M),
    "phut": re.compile(r"^phut: ([\d.]+)", re.M),
    "token": re.compile(r"^token: vao=(\d+) ra=(\d+)", re.M),
}


def doc_mot(tep: Path) -> dict | None:
    nd = tep.read_text(encoding="utf-8", errors="ignore")[:3000]
    m = _MAU["model"].search(nd)
    if not m:
        return None
    tt = _MAU["trang_thai"].search(nd)
    ph = _MAU["phut"].search(nd)
    tk = _MAU["token"].search(nd)
    return {
        "model": m.group(1),
        "xong": bool(tt and tt.group(1) == "xong"),
        "phut": float(ph.group(1)) if ph else None,
        "vao": int(tk.group(1)) if tk else 0,
        "ra": int(tk.group(2)) if tk else 0,
    }


def tong_hop(thu_muc: Path, tien_to: str = "") -> dict:
    nhom: dict = defaultdict(list)
    for tep in sorted(thu_muc.glob(f"{tien_to}*/KET-QUA.md")):
        dong = doc_mot(tep)
        if dong:
            nhom[dong["model"]].append(dong)
    kq = {}
    for model, ds in nhom.items():
        phut = [d["phut"] for d in ds if d["phut"]]
        vao = [d["vao"] for d in ds if d["vao"]]
        ra = [d["ra"] for d in ds if d["ra"]]
        kq[model] = {
            "phieu": len(ds),
            "xong": sum(d["xong"] for d in ds),
            "phut_tv": round(statistics.median(phut), 1) if phut else None,
            "vao_tv": int(statistics.median(vao)) if vao else 0,
            "ra_tv": int(statistics.median(ra)) if ra else 0,
        }
    return kq


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("thu_muc", type=Path)
    ap.add_argument("--tien-to", default="")
    a = ap.parse_args()
    for model, s in sorted(tong_hop(a.thu_muc, a.tien_to).items(), key=lambda x: -x[1]["phieu"]):
        print(f"{model}\tphieu={s['phieu']}\txong={s['xong']}\tphut_tv={s['phut_tv']}\tvao_tv={s['vao_tv']}\tra_tv={s['ra_tv']}")


if __name__ == "__main__":
    main()
