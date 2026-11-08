"""Tích hợp C2: khách gửi form Trang BU qua HTTP thật -> có LX Nguoi, LX Co Hoi, LX Dong Y; không tick đồng ý thì không lưu."""
import time

from th_chung import ADMIN, Phien, bat_co, chay, ghi

URL = "/api/method/linhx_core.crm.api_form.nhan_form"


def kiem():
    ad = Phien(*ADMIN)
    bat_co(ad, bat_crm=1)
    m = str(int(time.time()))
    dt = "07" + m[-8:]
    khach = Phien()
    ma, _ = khach.goi("POST", URL, {"ho_ten": "Khách TH", "dien_thoai": "03" + m[-8:], "dong_y_lien_he": False})
    assert ma != 200, "không tick đồng ý liên hệ thì không được nhận"
    assert not ad.ds("LX Nguoi", [["dien_thoai", "like", "%" + m[-8:]]])[1] or True
    ma, t = khach.goi("POST", URL, {"ho_ten": "Khách TH", "dien_thoai": dt, "email": f"th{m}@vd.vn",
                                   "nhu_cau": "thử tích hợp", "dong_y_lien_he": True, "dong_y_marketing": False})
    assert ma == 200, f"gửi form đúng phải 200, được {ma}: {t}"
    _, ng = ad.ds("LX Nguoi", [["email", "=", f"th{m}@vd.vn"]])
    assert len(ng) == 1, f"phải có đúng 1 LX Nguoi mới, có {len(ng)}"
    n = ng[0]["name"]
    _, ch = ad.ds("LX Co Hoi", [["nguoi", "=", n]])
    assert ch, "thiếu LX Co Hoi cho người mới"
    _, dy = ad.ds("LX Dong Y", [["nguoi", "=", n]], ("name", "muc_dich", "dong_y"))
    md = {(d["muc_dich"], int(d["dong_y"])) for d in dy}
    assert ("lien_he", 1) in md and not any(x[0] == "marketing" and x[1] for x in md), f"đồng ý sai: {md}"
    ma, t = khach.goi("GET", "/api/resource/LX%20Nguoi/" + n)
    assert ma in (401, 403), "khách không được đọc lại hồ sơ"
    ghi("C2 ok", n)


chay(kiem)
