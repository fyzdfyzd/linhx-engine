"""Điểm fan kiểu Mautic: mỗi sự kiện cộng điểm theo luật, điểm cũ giảm dần theo tuần, bậc theo ngưỡng."""
from datetime import datetime

from .db import bay_gio


def tinh_diem(su_kien, luat_diem, bay_gio_):
    giam = luat_diem["giam_moi_tuan"]
    tong = 0.0
    for sk in su_kien:
        tuan = (bay_gio_ - datetime.fromisoformat(sk["luc"])).days / 7
        tong += sk["diem"] * (giam ** max(0, tuan))
    return round(tong, 2)


def bac(diem, luat_diem):
    for ten, nguong in luat_diem["bac"]:
        if diem >= nguong:
            return ten
    return "nguoi_la"


def cap_nhat_tat_ca(con, luat_diem):
    t = bay_gio()
    doi = []
    for f in con.execute("SELECT * FROM fan").fetchall():
        sk = con.execute("SELECT diem, luc FROM su_kien_fan WHERE fan_id=?", (f["id"],)).fetchall()
        d = tinh_diem(sk, luat_diem, t)
        b = bac(d, luat_diem)
        if b != f["bac"]:
            doi.append((f["ten"], f["bac"], b))
        con.execute("UPDATE fan SET diem=?, bac=? WHERE id=?", (d, b, f["id"]))
    return doi
