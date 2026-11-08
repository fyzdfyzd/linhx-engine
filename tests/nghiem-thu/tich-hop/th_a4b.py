"""Tích hợp A4B: user thường (vai trò "LX Nhan Vien", User Permission allow LX Don Vi) chỉ thấy LX Don Vi của mình."""
import time
import urllib.parse

from th_chung import ADMIN, MK_THU, Phien, bat_co, chay, ghi, nguoi_dung


def kiem():
    ad = Phien(*ADMIN)
    bat_co(ad, bat_crm=1)
    m = str(int(time.time()))
    x = ad.tao("LX Don Vi", {"ten": "DV-BX-" + m})["name"]
    y = ad.tao("LX Don Vi", {"ten": "DV-BY-" + m})["name"]
    ux = nguoi_dung(ad, f"th-bx-{m}@test.local", ["LX Nhan Vien"])
    ad.tao("User Permission", {"user": ux, "allow": "LX Don Vi", "for_value": x, "apply_to_all_doctypes": 1})
    px = Phien(ux, MK_THU)
    ma, _ = px.goi("GET", "/api/resource/LX%20Don%20Vi/" + urllib.parse.quote(y))
    assert ma == 403, f"user đơn vị X đọc đơn vị Y phải 403, được {ma}"
    ma, ds = px.ds("LX Don Vi", [])
    ten = {d["name"] for d in ds}
    assert ma == 200 and x in ten and y not in ten, f"get_list LX Don Vi của X lộ đơn vị khác hoặc thiếu X: {ten}"
    ghi("A4B ok", x, y)


chay(kiem)
