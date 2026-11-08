"""A2: LX Quan He, LX Co Hoi; giao người phụ trách, báo việc chờ. Cơ hội mới có người phụ trách trong 1 giờ (trường han_giao).

Hợp đồng (HOP-DONG.md):
- DocType JSON module crm: LX Quan He (tu Link LX Nguoi, den Link LX Nguoi hoặc LX To Chuc, loai), LX Co Hoi (nguoi Link LX Nguoi,
  phu_trach Link User, han_giao Datetime, trang_thai Select có "moi", "dang_lam", "thang", "thua")
- linhx_core/crm/co_hoi.py thuần Python (thời gian là chuỗi "YYYY-MM-DD HH:MM:SS"):
    han_giao(tao_luc) -> str                        tao_luc + 1 giờ
    giao(co_hoi, ds_phu_trach, ds_co_hoi_mo) -> str  chọn người đang giữ ít cơ hội mở nhất (bằng nhau: theo thứ tự ds_phu_trach)
    viec_cho(ds_co_hoi, luc) -> list[dict]           cơ hội chưa có phu_trach, xếp han_giao tăng dần; mỗi phần tử thêm "qua_han": bool
- lx_co_hoi.py (controller) gọi co_hoi: khi thêm mới đặt han_giao và tự giao nếu có danh sách phụ trách
"""
from _chung import CORE, khong_import_frappe_dau_file, nap_module, ten_truong, tim_doctype


def _ch():
    return nap_module("linhx_core.crm.co_hoi", CORE)


def test_doctype():
    for ten in ["LX Quan He", "LX Co Hoi"]:
        _, d = tim_doctype(ten)
        assert d, f"thiếu DocType {ten}"
        assert str(d.get("module", "")).lower() == "crm"
    _, d = tim_doctype("LX Co Hoi")
    tr = ten_truong(d)
    assert tr.get("nguoi", {}).get("options") == "LX Nguoi"
    assert tr.get("phu_trach", {}).get("fieldtype") == "Link" and tr["phu_trach"].get("options") == "User"
    assert tr.get("han_giao", {}).get("fieldtype") == "Datetime", "LX Co Hoi thiếu han_giao (Datetime)"
    tt = tr.get("trang_thai", {})
    assert tt.get("fieldtype") == "Select" and {"moi", "dang_lam", "thang", "thua"} <= set(str(tt.get("options", "")).split("\n"))


def test_han_giao_mot_gio():
    ch = _ch()
    assert ch.han_giao("2026-11-09 23:30:00") == "2026-11-10 00:30:00"
    assert ch.han_giao("2026-11-09 08:00:00") == "2026-11-09 09:00:00"


def test_giao_nguoi_it_viec_nhat():
    ch = _ch()
    mo = [{"phu_trach": "a@x"}, {"phu_trach": "a@x"}, {"phu_trach": "b@x"}]
    assert ch.giao({"name": "CH1"}, ["a@x", "b@x", "c@x"], mo) == "c@x"
    assert ch.giao({"name": "CH2"}, ["a@x", "b@x"], mo) == "b@x"
    assert ch.giao({"name": "CH3"}, ["b@x", "a@x"], []) == "b@x", "bằng nhau thì theo thứ tự danh sách"


def test_viec_cho_va_qua_han():
    ch = _ch()
    ds = [
        {"name": "CH1", "phu_trach": None, "han_giao": "2026-11-09 10:00:00"},
        {"name": "CH2", "phu_trach": "a@x", "han_giao": "2026-11-09 08:00:00"},
        {"name": "CH3", "phu_trach": "", "han_giao": "2026-11-09 08:30:00"},
    ]
    vc = ch.viec_cho(ds, "2026-11-09 09:00:00")
    assert [x["name"] for x in vc] == ["CH3", "CH1"]
    assert vc[0]["qua_han"] is True and vc[1]["qua_han"] is False


def test_thuan_python_va_controller():
    p = CORE / "linhx_core" / "crm" / "co_hoi.py"
    khong_import_frappe_dau_file(p)
    pd, _ = tim_doctype("LX Co Hoi")
    ctl = pd.with_suffix(".py")
    assert ctl.exists() and "co_hoi" in ctl.read_text(encoding="utf-8"), "lx_co_hoi.py phải gọi co_hoi (han_giao, giao)"
