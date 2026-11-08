# Gom điểm persona: điểm có trọng số, độ lệch (chia rẽ), chọn top N giữ đa dạng nhóm.
# python cham.py diem.json persona.json ung-vien.json [N=5] [toi_da_moi_nhom=2]
import json, sys, statistics as st
D, P, U = (json.load(open(f, encoding="utf-8")) for f in sys.argv[1:4])
N = int(sys.argv[4]) if len(sys.argv) > 4 else 5
K = int(sys.argv[5]) if len(sys.argv) > 5 else 2
L = D.pop("_loi", {})  # {ung_vien: [[mo_ta, tru, tran]]}, tran = điểm tối đa nếu lỗi nặng
W = {p["id"]: p["w"] for p in P}
nhom = {u["id"]: u["nhom"] for u in U}
bang = []
for u in U:
    d = {p: D[p][u["id"]][0] for p in W}
    tb = sum(W[p] * d[p] for p in W) / sum(W.values())
    lech = st.pstdev(d.values())
    loi = L.get(u["id"], [])
    tb += sum(l[1] for l in loi)
    for l in loi:
        if len(l) > 2 and l[2] is not None: tb = min(tb, l[2])
    tb = max(tb, 1)
    bang.append({"id": u["id"], "nhan": u["nhan"], "diem": round(tb, 2), "lech": round(lech, 2),
                 "thap_nhat": min(d.values()), "chia_re": lech >= 2.0 or min(d.values()) <= 3, "tung_nguoi": d, "loi": loi})
bang.sort(key=lambda x: -x["diem"])
chon, dem = [], {}
for x in bang:
    if len(chon) < N and dem.get(nhom[x["id"]], 0) < K:
        chon.append(x["id"]); dem[nhom[x["id"]]] = dem.get(nhom[x["id"]], 0) + 1
for x in bang:  # thiếu nhóm thì lấp bằng ứng viên điểm cao còn lại
    if len(chon) < N and x["id"] not in chon: chon.append(x["id"])
print(json.dumps({"xep_hang": bang, "top": chon}, ensure_ascii=False, indent=1))
