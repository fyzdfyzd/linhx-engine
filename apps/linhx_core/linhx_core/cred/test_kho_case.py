"""Kiểm thử đơn vị cho kho_case, api_cred và controller LXCase."""
from __future__ import annotations

import sys
import types
import pytest

from linhx_core.cred import kho_case


def test_case_cong_khai_loc_chinh_xac_va_khong_sua_dau_vao():
    ds_goc = [
        {
            "name": "CS-01",
            "tieu_de": "Tự động hoá chốt đơn Dược",
            "khach_hang": "Dược Tâm An",
            "chi_so": "+42% tỷ lệ chuyển đổi",
            "mo_ta": "Sau 14 ngày pilot",
            "da_duyet": True,
            "ghi_chu_noi_bo": "Mật nội bộ không được lộ",
        },
        {
            "name": "CS-02",
            "tieu_de": "Case chưa duyệt False",
            "chi_so": "+80%",
            "mo_ta": "Bí mật",
            "da_duyet": False,
        },
        {
            "name": "CS-03",
            "tieu_de": "Case chưa duyệt 0",
            "chi_so": "+50%",
            "mo_ta": "Bí mật 0",
            "da_duyet": 0,
        },
        {
            "name": "CS-04",
            "tieu_de": "Case đã duyệt nhưng thiếu chỉ số",
            "chi_so": "   ",
            "mo_ta": "Không có số",
            "da_duyet": 1,
        },
        {
            "name": "CS-05",
            "tieu_de": "Case duyệt bằng 1",
            "chi_so": "Giảm 60% thời gian xử lý",
            "mo_ta": "Hoàn thành",
            "da_duyet": 1,
        },
    ]
    kq = kho_case.case_cong_khai(ds_goc)
    assert [c["name"] for c in kq] == ["CS-01", "CS-05"]
    assert "ghi_chu_noi_bo" not in kq[0]
    assert ds_goc[0]["ghi_chu_noi_bo"] == "Mật nội bộ không được lộ"


def test_noi_dung_trang_bu_ghep_case_va_chong_trung():
    site_cfg = {
        "ten": "ifagent",
        "ban_cai": "ifagent",
        "noi_dung": {
            "tieu_de": "ifAgent — Trang BU",
            "mo_ta": "Mô tả",
            "muc": [{"ten": "Mục 1", "mo_ta": "Mô tả 1"}],
        },
    }
    ds_case = [
        {
            "name": "CS-10",
            "tieu_de": "Chuỗi Nha Khoa Toàn Tâm",
            "chi_so": "Giảm 68% thời gian phản hồi Lead",
            "mo_ta": "Triển khai Agent Force trong 2 tuần",
            "da_duyet": True,
        },
        {
            "name": "CS-11",
            "tieu_de": "Case Ẩn",
            "chi_so": "99%",
            "mo_ta": "Không hiện",
            "da_duyet": False,
        },
    ]
    nd = kho_case.noi_dung_trang_bu(site_cfg, ds_case)
    assert nd["tieu_de"] == "ifAgent — Trang BU"
    assert len(nd["muc"]) == 2
    assert "Chuỗi Nha Khoa Toàn Tâm" in nd["muc"][1]["ten"]
    assert "Giảm 68% thời gian phản hồi Lead" in nd["muc"][1]["ten"]
    assert nd["muc"][1]["mo_ta"] == "Triển khai Agent Force trong 2 tuần"
    assert len(site_cfg["noi_dung"]["muc"]) == 1


def test_api_cred_danh_sach_case_va_noi_dung_ifagent(monkeypatch):
    fake_frappe = types.ModuleType("frappe")
    fake_frappe.response = {}

    def _whitelist(allow_guest=False):
        def _wrap(fn):
            fn._allow_guest = allow_guest
            return fn
        return _wrap

    fake_frappe.whitelist = _whitelist
    fake_frappe.get_all = lambda *a, **kw: [
        {
            "name": "CS-DB-1",
            "tieu_de": "Bệnh viện Quốc tế",
            "khach_hang": "BV Quốc tế",
            "chi_so": "Tăng 3.2x lịch hẹn thành công",
            "mo_ta": "Tự động đặt lịch tư vấn",
            "da_duyet": 1,
        },
        {
            "name": "CS-DB-2",
            "tieu_de": "Case Nháp DB",
            "khach_hang": "Nội bộ",
            "chi_so": "10x",
            "mo_ta": "Chưa duyệt",
            "da_duyet": 0,
        },
    ]

    monkeypatch.setitem(sys.modules, "frappe", fake_frappe)
    sys.modules.pop("linhx_core.cred.api_cred", None)
    import importlib
    api_cred = importlib.import_module("linhx_core.cred.api_cred")

    ds = api_cred.danh_sach_case()
    assert [c["name"] for c in ds] == ["CS-DB-1"]
    assert getattr(api_cred.danh_sach_case, "_allow_guest", False) is True

    nd = api_cred.noi_dung_ifagent()
    assert getattr(api_cred.noi_dung_ifagent, "_allow_guest", False) is True
    chu_muc = " | ".join(m["ten"] for m in nd["muc"])
    assert "Bệnh viện Quốc tế" in chu_muc
    assert "Tăng 3.2x lịch hẹn thành công" in chu_muc
    assert "Case Nháp DB" not in chu_muc
    assert fake_frappe.response.get("noi_dung") == nd


def test_kiem_case_bat_buoc_tieu_de_va_chi_so_khi_duyet():
    with pytest.raises(ValueError, match="tieu_de"):
        kho_case.kiem_case({"tieu_de": "   ", "chi_so": "+10%", "da_duyet": False})

    with pytest.raises(ValueError, match="chi_so"):
        kho_case.kiem_case({"tieu_de": "Case A", "chi_so": "", "da_duyet": True})

    hop_le = kho_case.kiem_case({"tieu_de": " Case A ", "chi_so": " +35% ", "da_duyet": 1})
    assert hop_le["tieu_de"] == "Case A"
    assert hop_le["chi_so"] == "+35%"
    assert hop_le["da_duyet"] is True
