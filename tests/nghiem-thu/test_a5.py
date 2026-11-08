"""A5: API chuyển lead giữa hai bản cài có ghi công (nguồn, đơn vị, thời điểm).
Lead từ ifagent sang linhx giữ trường ghi_cong. Thiếu đồng ý chuyển chéo thì từ chối.

Hợp đồng (HOP-DONG.md):
- linhx_core/crm/chuyen_lead.py thuần Python:
    goi_di(nguoi: dict, so_dong_y: list, site_nguon: str, don_vi: str, luc: str) -> dict
        gọi dong_y.kiem_chuyen_cheo (TuChoi khi không đồng ý); trả {"nguoi": {ho_ten, dien_thoai, email, zalo},
        "ghi_cong": {"nguon": site_nguon, "don_vi": don_vi, "luc": luc}}; không mang trường nội bộ (name, owner, ghi_chu...)
    nhan(goi: dict, ds_nguoi: list) -> (ds_moi, nguoi)   thiếu ghi_cong.nguon/don_vi/luc -> ValueError;
        gộp trùng bằng gop_trung.gop; người nhận được có "ghi_cong" như gói gửi (không ghi đè ghi_cong cũ nếu đã có)
- linhx_core/crm/api_lead.py: @frappe.whitelist() `nhan_lead` (KHÔNG allow_guest; xác thực bằng API key user riêng
  cho bản cài nguồn) và `gui_lead(nguoi, site_dich)` đọc URL + key bản cài đích từ site_config, không viết trong code.
- Bằng chứng trên VM linhx-engine-1 (hai bản cài N5): bang-chung/A5/chuyen.json
    {"luc", "tu": "ifagent", "toi": "linhx", "nguoi_moi": "<name bên linhx>", "ghi_cong": {"nguon", "don_vi", "luc"},
     "khi_rut_dong_y": {"status": 403 hoặc 417}}
"""
import pytest

from _chung import CORE, bang_chung_json, khong_import_frappe_dau_file, nap_module

LUC = "2026-11-09 08:00:00"


def _m():
    dy = nap_module("linhx_core.crm.dong_y", CORE)
    cl = nap_module("linhx_core.crm.chuyen_lead", CORE)  # nạp sau để dùng chung lớp TuChoi
    return cl, dy


def test_goi_di_giu_ghi_cong_va_bo_truong_noi_bo():
    cl, dy = _m()
    so = dy.ghi([], "N1", "chuyen_cheo", True, LUC, "form")
    g = cl.goi_di({"name": "N1", "owner": "a@x", "ghi_chu": "nội bộ", "ho_ten": "Lan", "dien_thoai": "0912345678"},
                  so, "ifagent", "BU-IFAGENT", LUC)
    assert g["ghi_cong"] == {"nguon": "ifagent", "don_vi": "BU-IFAGENT", "luc": LUC}
    assert g["nguoi"]["ho_ten"] == "Lan"
    assert not ({"name", "owner", "ghi_chu"} & set(g["nguoi"])), "không gửi trường nội bộ sang bản cài khác"


def test_thieu_dong_y_thi_tu_choi():
    cl, dy = _m()
    so = dy.ghi([], "N1", "chuyen_cheo", True, LUC, "form")
    so = dy.ghi(so, "N1", "chuyen_cheo", False, "2026-11-09 09:00:00", "rut")
    with pytest.raises(dy.TuChoi):
        cl.goi_di({"name": "N1", "ho_ten": "Lan"}, so, "ifagent", "BU", LUC)
    with pytest.raises(dy.TuChoi):
        cl.goi_di({"name": "N2", "ho_ten": "Minh"}, so, "ifagent", "BU", LUC)


def test_nhan_gop_trung_giu_ghi_cong():
    cl, _ = _m()
    goi = {"nguoi": {"ho_ten": "Lan", "dien_thoai": "+84912345678"}, "ghi_cong": {"nguon": "ifagent", "don_vi": "BU", "luc": LUC}}
    ds, n = cl.nhan(goi, [])
    assert len(ds) == 1 and n["ghi_cong"]["nguon"] == "ifagent"
    goi2 = {"nguoi": {"ho_ten": "Lan N", "dien_thoai": "0912 345 678", "email": "lan@vd.vn"},
            "ghi_cong": {"nguon": "unikon", "don_vi": "BU2", "luc": "2026-11-10 08:00:00"}}
    ds, n = cl.nhan(goi2, ds)
    assert len(ds) == 1, "cùng số điện thoại phải gộp"
    assert n["ghi_cong"]["nguon"] == "ifagent", "giữ ghi công lần đầu"
    with pytest.raises(ValueError):
        cl.nhan({"nguoi": {"ho_ten": "X"}, "ghi_cong": {"nguon": "ifagent"}}, [])


def test_api_khong_mo_cho_khach():
    p = CORE / "linhx_core" / "crm" / "api_lead.py"
    chu = p.read_text(encoding="utf-8")
    assert "def nhan_lead(" in chu and "def gui_lead(" in chu
    import re
    m = re.search(r"@frappe\.whitelist\(([^)]*)\)\s*\ndef nhan_lead", chu)
    assert m and "allow_guest" not in m.group(1), "nhan_lead không được allow_guest"
    khong_import_frappe_dau_file(CORE / "linhx_core" / "crm" / "chuyen_lead.py")


def test_bang_chung_vm():
    d = bang_chung_json("A5", "chuyen.json")
    assert d.get("tu") == "ifagent" and d.get("toi") == "linhx" and d.get("nguoi_moi")
    gc = d.get("ghi_cong") or {}
    assert gc.get("nguon") and gc.get("don_vi") and gc.get("luc")
    assert (d.get("khi_rut_dong_y") or {}).get("status") in (403, 417)
