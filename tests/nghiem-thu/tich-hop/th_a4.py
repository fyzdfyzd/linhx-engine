"""Tích hợp A4: quyền theo Đơn vị bằng HTTP thật với hai user thường (vai trò "LX Nhan Vien", User Permission allow LX Don Vi)."""
import time

from th_chung import ADMIN, MK_THU, Phien, bat_co, chay, ghi, nguoi_dung


def kiem():
    ad = Phien(*ADMIN)
    bat_co(ad, bat_crm=1)
    m = str(int(time.time()))
    x = ad.tao("LX Don Vi", {"ten": "DV-X-" + m})["name"]
    y = ad.tao("LX Don Vi", {"ten": "DV-Y-" + m})["name"]
    nx = ad.tao("LX Nguoi", {"ho_ten": "Người X", "dien_thoai": "09" + m[-8:], "don_vi": x})["name"]
    ny = ad.tao("LX Nguoi", {"ho_ten": "Người Y", "dien_thoai": "08" + m[-8:], "don_vi": y})["name"]
    ux = nguoi_dung(ad, f"th-x-{m}@test.local", ["LX Nhan Vien"])
    nguoi_dung(ad, f"th-y-{m}@test.local", ["LX Nhan Vien"])
    ad.tao("User Permission", {"user": ux, "allow": "LX Don Vi", "for_value": x, "apply_to_all_doctypes": 1})
    px = Phien(ux, MK_THU)
    ma, _ = px.goi("GET", f"/api/resource/LX%20Nguoi/{nx}")
    assert ma == 200, f"user đơn vị X đọc người của X phải 200, được {ma}"
    ma, _ = px.goi("GET", f"/api/resource/LX%20Nguoi/{ny}")
    assert ma == 403, f"user đơn vị X đọc người của Y phải 403, được {ma}"
    ma, ds = px.ds("LX Nguoi", [["name", "in", [nx, ny]]])
    ten = {d["name"] for d in ds}
    assert ma == 200 and nx in ten and ny not in ten, f"get_list của X lộ người Y hoặc thiếu người X: {ten}"
    # sửa bản ghi của Y mà gửi don_vi = X: phải 403 và bản ghi giữ nguyên đơn vị Y
    ma, _ = px.goi("PUT", f"/api/resource/LX%20Nguoi/{ny}", {"don_vi": x, "ho_ten": "Đổi trộm"})
    assert ma == 403, f"user X sửa người của Y (gửi don_vi X) phải 403, được {ma}"
    _, t = ad.goi("GET", f"/api/resource/LX%20Nguoi/{ny}")
    assert (t.get("data") or {}).get("don_vi") == y, "bản ghi của Y bị đổi đơn vị"
    # tạo cơ hội don_vi X trỏ tới người của Y: phải bị chặn
    ma, _ = px.goi("POST", "/api/resource/LX%20Co%20Hoi", {"nguoi": ny, "don_vi": x})
    assert ma == 403, f"user X tạo cơ hội cho người của Y phải 403 (PermissionError), được {ma}"
    ghi("A4 ok", x, y)


chay(kiem)
