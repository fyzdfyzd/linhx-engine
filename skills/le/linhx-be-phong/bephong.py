"""Bệ phóng nhiều OPC: lập kế hoạch launch một OPC trên module chung và so KPI giữa các OPC.

Lệnh:
  python bephong.py ke-hoach opc-mau/lich-van-tet.json   # việc còn lại + cổng chờ Linh
  python bephong.py bang opc-mau                          # bản đồ nhiệt KPI giữa các OPC
"""
import json, sys
from pathlib import Path

GOC = Path(__file__).parent
TY_GIA = 26000  # đồng mỗi USD, để quy token ra tiền


def doc(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def ke_hoach(opc, be):
    xong = set(opc["da_xong"]) | set(opc["dung_module"])
    con, cho_linh, dung_chung = [], [], []
    for k in be["khau"]:
        if k["ma"] in opc["dung_module"]:
            dung_chung.append(k)
        elif k["ma"] not in xong:
            (cho_linh if k.get("cong_nguoi") else con).append(k)
    tu_lam = sum(1 for k in con if k["tu_dong"] in ("A3", "A2"))
    return {
        "opc": opc["ma"],
        "san_sang": round(100 * len(xong) / len(be["khau"])),
        "dung_lai": [k["ma"] for k in dung_chung],
        "viec_con": [(k["ma"], k["tu_dong"], k["ten"]) for k in con],
        "cong_cho_linh": [(k["ma"], k["ten"]) for k in cho_linh],
        "ai_tu_lam": f"{tu_lam}/{len(con)}",
    }


def chi_so(opc):
    k = opc["kpi"]
    lai = k["doanh_thu"] - k["chi_phi"] - k["token_usd"] * TY_GIA
    return {
        "chuyen_doi_%": round(100 * k["don"] / max(k["luot_xem"], 1), 2),
        "chi_phi_moi_don": round((k["chi_phi"] + k["token_usd"] * TY_GIA) / max(k["don"], 1)),
        "lai": round(lai),
    }


def bang(ds):
    """So từng chỉ số giữa các OPC: tốt nhất xanh, kém nhất đỏ, còn lại vàng."""
    rows = {o["ma"]: chi_so(o) for o in ds}
    cao_la_tot = {"chuyen_doi_%": True, "chi_phi_moi_don": False, "lai": True}
    mau = {m: {} for m in rows}
    for cs, tot in cao_la_tot.items():
        xep = sorted(rows, key=lambda m: rows[m][cs], reverse=tot)
        for i, m in enumerate(xep):
            mau[m][cs] = "XANH" if i == 0 else ("DO" if i == len(xep) - 1 else "VANG")
    return rows, mau


def main(argv):
    be = doc(GOC / "be-phong.json")
    if argv[:1] == ["ke-hoach"]:
        kh = ke_hoach(doc(argv[1]), be)
        print(f"# {kh['opc']} · sẵn sàng {kh['san_sang']}% · AI tự làm {kh['ai_tu_lam']} việc còn lại")
        print("Dùng lại từ bệ:", ", ".join(kh["dung_lai"]))
        for ma, muc, ten in kh["viec_con"]:
            print(f"- [ ] {ma} ({muc}) {ten}")
        for ma, ten in kh["cong_cho_linh"]:
            print(f"- [ ] {ma} CỔNG LINH: {ten}")
    elif argv[:1] == ["bang"]:
        ds = [doc(p) for p in sorted(Path(argv[1]).glob("*.json"))]
        rows, mau = bang(ds)
        print("| OPC | chuyển đổi % | chi phí/đơn | lãi |\n|---|---|---|---|")
        for m, r in rows.items():
            print(f"| {m} | " + " | ".join(f"{v} {mau[m][c]}" for c, v in r.items()) + " |")
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
