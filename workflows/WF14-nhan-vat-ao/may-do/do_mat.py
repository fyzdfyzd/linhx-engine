# Đo giữ mặt: cosine ArcFace giữa mặt lớn nhất mỗi ảnh và bộ mốc (ảnh đã duyệt).
# python do_mat.py --moc moc1.png moc2.png --anh a.png b.png [--nguong 0.45] [--json out.json]
# Điểm mỗi ảnh = cosine cao nhất với các mốc. Báo điểm tệ nhất lô. Không thấy mặt -> "khong_thay" (không tính là đạt).
import argparse, json, sys
import cv2, numpy as np
from insightface.app import FaceAnalysis
p = argparse.ArgumentParser()
p.add_argument("--moc", nargs="+", required=True); p.add_argument("--anh", nargs="+", required=True)
p.add_argument("--nguong", type=float, default=0.45); p.add_argument("--json")
p.add_argument("--model", default="buffalo_l")
a = p.parse_args()
app = FaceAnalysis(name=a.model, providers=["CPUExecutionProvider"]); app.prepare(ctx_id=-1, det_size=(640, 640))
def emb(f):
    img = cv2.imread(f)
    if img is None: return None, "khong_doc_duoc"
    fs = app.get(img)
    if not fs: return None, "khong_thay"
    f0 = max(fs, key=lambda x: (x.bbox[2]-x.bbox[0])*(x.bbox[3]-x.bbox[1]))
    return f0.normed_embedding, f"det={f0.det_score:.2f}"
moc = [(f, *emb(f)) for f in a.moc]
moc_ok = [(f, e) for f, e, _ in moc if e is not None]
if not moc_ok: sys.exit("Không thấy mặt ở ảnh mốc nào")
kq = []
for f in a.anh:
    e, note = emb(f)
    if e is None: kq.append({"anh": f, "diem": None, "trang_thai": note}); continue
    d = max(float(np.dot(e, m)) for _, m in moc_ok)
    kq.append({"anh": f, "diem": round(d, 3), "trang_thai": "dat" if d >= a.nguong else "co_xem", "ghi": note})
for r in kq: print(f"{r['diem'] if r['diem'] is not None else '  -  ':>6}  {r['trang_thai']:<11} {r['anh']}")
diem = [r["diem"] for r in kq if r["diem"] is not None]
print(f"tệ nhất {min(diem) if diem else None} · không thấy mặt {sum(r['diem'] is None for r in kq)} · ngưỡng {a.nguong}")
if a.json: json.dump({"nguong": a.nguong, "model": a.model, "kq": kq}, open(a.json, "w"), ensure_ascii=False, indent=1)
sys.exit(0 if diem and min(diem) >= a.nguong and all(r["diem"] is not None for r in kq) else 1)
